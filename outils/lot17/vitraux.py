# Petits vitraux : verre teinté texturé, plombs dorés ; trois dessins de plombs ; cadre qui se raccorde aux voisins
import sys; sys.path.insert(0, '/home/claude/travail/lot12')
from px import hx
from PIL import Image, ImageDraw, ImageFont
PLOMB = [hx('fff0c4'), hx('e1ba6e'), hx('a8763c'), hx('5a3a1e')]
COUL = {'clear': ('dfe9ee', 110), 'imperial red': ('a81e2a', 205), 'amber': ('e08a1e', 195), 'royal blue': ('22449a', 205), 'emerald': ('23804a', 200), 'violet': ('5e2e92', 205)}
def verre(c, a, x, y):
    """Verre légèrement texturé : bulles et ondulations, reflet en haut à gauche."""
    r, g, b, _ = hx(c); k = ((x * 7 + y * 13) % 11) / 10.0
    f = 1.0 + 0.10 * (k - 0.5) + (0.18 if (x + y) < 6 and (x * 3 + y) % 5 == 0 else 0)
    return (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
def tex(c, a, dessin, n=True, e=True, s=True, w=True):
    im = Image.new('RGBA', (16, 16)); p = im.load()
    for y in range(16):
        for x in range(16):
            p[x, y] = verre(c, a, x, y)
            if dessin == 'diamonds':
                u, v = (x + y) % 8, (x - y) % 8
                if u == 0 or v == 0: p[x, y] = PLOMB[2]
            elif dessin == 'squares':
                if x % 8 == 0 or y % 8 == 0: p[x, y] = PLOMB[2]
            elif dessin == 'border':
                if x in (3, 12) and 3 <= y <= 12 or y in (3, 12) and 3 <= x <= 12: p[x, y] = PLOMB[2]
                if 4 <= x <= 11 and 4 <= y <= 11: p[x, y] = verre(c, a, x, y)
                elif not (3 <= x <= 12 and 3 <= y <= 12): p[x, y] = verre('f0d58a' if c != 'f0d58a' else c, a, x, y)
    # cadre doré seulement sur les côtés non raccordés (2 texels, lumière en haut à gauche)
    for i in range(16):
        if n: p[i, 0] = PLOMB[0]; p[i, 1] = PLOMB[1]
        if s: p[i, 15] = PLOMB[3]; p[i, 14] = PLOMB[2]
        if w: p[0, i] = PLOMB[0]; p[1, i] = PLOMB[1]
        if e: p[15, i] = PLOMB[3]; p[14, i] = PLOMB[2]
    return im
def baie(c, a, dessin, l=3, h=4):
    im = Image.new('RGBA', (16 * l, 16 * h))
    for j in range(h):
        for i in range(l):
            im.paste(tex(c, a, dessin, n=j == 0, s=j == h - 1, w=i == 0, e=i == l - 1), (i * 16, j * 16))
    return im
K = 5
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
mur = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/slate_bricks.png').convert('RGBA').crop((0, 0, 16, 16))
dessins = ['diamonds', 'squares', 'border']
cols = list(COUL)
W = Image.new('RGBA', (len(cols) * 3 * 16 * K // 1 + 40, len(dessins) * (4 * 16 * K + 60) + 20), (139, 139, 139, 255))
# derrière le verre : ciel clair (pour juger la transparence)
d = ImageDraw.Draw(W)
for r, dz in enumerate(dessins):
    y0 = 20 + r * (4 * 16 * K + 60)
    d.text((10, y0 - 18), {'diamonds': 'A  diamond leading', 'squares': 'B  square leading', 'border': 'C  border pane'}[dz], font=F, fill=(255, 255, 255))
    for i, c in enumerate(cols):
        x0 = 10 + i * (3 * 16 * K + 6)
        ciel = Image.new('RGBA', (3 * 16, 4 * 16), (150, 190, 225, 255))
        for yy in range(4 * 16):
            for xx in range(3 * 16):
                if yy > 44: ciel.putpixel((xx, yy), (95, 140, 80, 255))   # horizon d'herbe
        ciel.alpha_composite(baie(*COUL[c], dz))
        W.paste(ciel.resize((3 * 16 * K, 4 * 16 * K), Image.NEAREST), (x0, y0))
        if r == len(dessins) - 1: d.text((x0, y0 + 4 * 16 * K + 4), c, font=F, fill=(255, 255, 255))
W.save('/tmp/mob/stained_glass_small_v1.png'); print(W.size)
