# Cordeau de maçon (objet 32 x 32, famille des outils impériaux) : dévidoir rond en airain, manivelle noire,
# cordeau rouge impérial qui sort par un bec et finit sur un crochet d'acier.
from PIL import Image
import math, sys
sys.path.insert(0, '/home/claude/travail/lot8')
from marteau import hx, CONT, AIR_OR, ACIER, MANCHE, OR
ROUGE = [hx('d9645c'), hx('c04343'), hx('af1d25'), hx('8b0018')]
ARD = [hx('4a4f5c'), hx('363a44'), hx('2a2e37'), hx('1b1e24')]

def cordeau():
    im = Image.new('RGBA', (32, 32)); px = im.load()
    cx, cy, R = 13.0, 13.0, 9.6
    for y in range(32):
        for x in range(32):
            dx, dy = x - cx, y - cy; d = math.hypot(dx, dy)
            l = (-dx - dy) / max(d, 1e-6)                                  # éclairage en haut à gauche
            if d > R: continue
            if d > R - 1.1: m = AIR_OR[1] if l > 0.3 else AIR_OR[3] if l > -0.4 else AIR_OR[5]           # jante du carter
            elif d > R - 2.3: m = AIR_OR[2] if l > 0.3 else AIR_OR[3] if l > -0.4 else AIR_OR[4]
            elif d > R - 2.9: m = AIR_OR[5]                                                                # ombre intérieure
            elif d > 2.6:                                                                                  # bobine de cordeau rouge
                k = 0 if l > 0.45 else 1 if l > -0.3 else 2
                if int(d) % 2 == 0: k += 1
                m = ROUGE[min(3, k)]
            elif d > 1.5: m = AIR_OR[4]
            else: m = OR[0]
            px[x, y] = m
    for a in (225, 315, 135):                                                  # vis de carter
        r = math.radians(a); x, y = round(cx + (R - 1.6) * math.cos(r)), round(cy + (R - 1.6) * math.sin(r))
        px[x, y] = AIR_OR[0]
    # manivelle : bras d'airain du moyeu vers le haut à gauche, poignée noire
    for k in range(2, 12):
        x, y = round(cx - k * 0.72), round(cy - k * 0.72)
        px[x, y] = AIR_OR[1]; px[x + 1, y] = AIR_OR[3]; px[x, y + 1] = AIR_OR[4]
    for (x, y) in ((2, 2), (3, 2), (4, 2), (2, 3), (3, 3), (4, 3), (2, 4), (3, 4), (4, 4), (3, 5), (5, 3)):
        px[x, y] = MANCHE[0] if x + y < 6 else MANCHE[1] if x + y < 8 else MANCHE[2]
    px[2, 2] = hx('6a6078')
    # bec de sortie en bas à droite
    for (x, y, c) in ((20, 20, AIR_OR[2]), (21, 20, AIR_OR[3]), (20, 21, AIR_OR[3]), (21, 21, AIR_OR[4]), (22, 21, AIR_OR[5]), (21, 22, AIR_OR[5])):
        px[x, y] = c
    # cordeau rouge : petite courbe jusqu'au crochet
    pts = []
    for i in range(0, 41):
        t = i / 40; x = 22 + t * 6; y = 22 + t * 5 + math.sin(t * math.pi) * 1.4
        pts.append((round(x), round(y)))
    for (x, y) in pts:
        if px[x, y][3] == 0: px[x, y] = ROUGE[1]
    for (x, y) in pts[::7]:
        if px[x, y] == ROUGE[1]: px[x, y] = ROUGE[3]
    # crochet d'acier
    for (x, y, c) in ((28, 27, ACIER[1]), (29, 27, ACIER[0]), (29, 28, ACIER[1]), (29, 29, ACIER[2]), (28, 29, ACIER[2]), (27, 29, ACIER[3]), (27, 28, ACIER[2])):
        px[x, y] = c
    m = [[px[x, y][3] > 0 for x in range(32)] for y in range(32)]
    for y in range(32):
        for x in range(32):
            if not m[y][x] and any(0 <= x + i < 32 and 0 <= y + j < 32 and m[y + j][x + i] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = CONT
    return im

if __name__ == '__main__':
    im = cordeau(); bg = Image.new('RGBA', (32 * 12, 32 * 12), (139, 139, 139, 255)); bg.alpha_composite(im.resize((384, 384), Image.NEAREST)); bg.save('/tmp/nv/cordeau.png')
