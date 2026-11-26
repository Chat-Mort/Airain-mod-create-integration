# Lot 12, passe 3 : patine rouge appuyée seulement sur plaque, lingot et pépite ; fil, câble et rouage en airain doré
import math, random
from px import *
from PIL import Image
from patine import lum, C, ORIG
# airain doré (sans patine) : sombre -> clair
OR = [hx(c) for c in ('3a2414', '704425', '8f5a2e', 'a8763c', 'c99b52', 'e1ba6e', 'f3d694', 'fff0c4')]
# airain à patine rouge : ombres franchement rouge impérial, clairs dorés
PAT = [hx(c) for c in ('3c0a10', '5e0f16', '8b0018', 'af2a22', 'c45a34', 'd99248', 'e8b860', 'f3d48a', 'fbe8b4', 'fff6dc')]
ROUGE = [hx('e06a5a'), hx('c04343'), hx('af1d25')]

def recolorer(src, rampe, haut=None, reflets=False):
    im = src.convert('RGBA'); px = im.load(); n, m = im.size
    teintes = sorted({px[x, y][:3] for y in range(m) for x in range(n) if px[x, y][3] > 0}, key=lum)
    l0, l1 = lum(teintes[0]), lum(teintes[-1]); h = len(rampe) - 1 if haut is None else haut
    table = {t: rampe[round((lum(t) - l0) / max(1, l1 - l0) * h)] for t in teintes}
    out = Image.new('RGBA', im.size); po = out.load()
    for y in range(m):
        for x in range(n):
            if px[x, y][3] > 0: po[x, y] = table[px[x, y][:3]]
    if reflets:
        clairs = set(rampe[-3:]); moyens = set(rampe[3:6])
        base = out.copy(); pb = base.load()
        for y in range(m):
            for x in range(n):
                c = pb[x, y]
                if not c[3] or c not in moyens: continue
                v = [pb[x + i, y + j] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + i < n and 0 <= y + j < m]
                # reflet rouge franc le long du reflet clair, et sur les arêtes d'ombre
                if any(w in clairs for w in v): po[x, y] = ROUGE[0] if (x + y) % 2 else ROUGE[1]
    return out

def plaque_A(): return recolorer(Image.open(C + 'golden_sheet.png'), PAT, 7, True)
def plaque_B(): return recolorer(Image.open(C + 'brass_sheet.png'), PAT, 7, True)
def lingot(): return recolorer(Image.open(ORIG + 'airain_ingot.png'), PAT, 7, True)
def pepite(): return recolorer(Image.open(ORIG + 'airain_nugget.png'), PAT, 7, True)
def fil(): return recolorer(Image.open(ORIG + 'airain_wire.png'), OR, 6)

def cable():
    """Forme de la passe 1 (tambour à joues), le câble en lignes verticales : chaque brin enroulé vu de face."""
    g = ["................",
         "................",
         "..ooo......ooo..",
         ".oddso....oddso.",
         ".odsdooooooddso.",
         ".odsd123432dsdo.",
         ".odsd123432dsdo.",
         ".odsd123432dsdo.",
         ".odsd123432dsdo.",
         ".odsd123432dsdo.",
         ".odsd012321dsdo.",
         ".odsdooooooddso.",
         ".oddso....oddsoo",
         "..ooo......oo5ao",
         ".............oo.",
         "................"]
    pal = dict(o=OR[0], d=OR[1], s=OR[2], a=OR[5])
    pal.update({'0': OR[2], '1': OR[3], '2': OR[4], '3': OR[5], '4': OR[7], '5': OR[6]})
    im = depuis(g, pal); px = im.load()
    for y in range(5, 11):                                              # séparation des brins : un texel plus sombre une ligne sur deux
        if y % 2: px[6, y] = OR[4]; px[9, y] = OR[5]
    return im

def rouage_brise():
    """Dents carrées (passe 2) ; la cassure est irrégulière : bord déchiqueté, deux dents à moitié arrachées, éclats, métal frais discret."""
    im = neuf(); px = im.load()
    cx, cy = 7.5, 7.5
    pts = set()
    for y in range(16):
        for x in range(16):
            if math.hypot(x - cx, y - cy) <= 4.9: pts.add((x, y))
    for k in range(8):
        t = math.radians(k * 45)
        tx, ty = cx + 6.0 * math.cos(t), cy + 6.0 * math.sin(t)
        x0, y0 = int(round(tx - 0.5)), int(round(ty - 0.5))
        for (x, y) in ((x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x0 + 1, y0 + 1)): pts.add((x, y))
    # bord de cassure déchiqueté, fait à la main (bas droite)
    arrache = {(9, 13), (10, 13), (10, 12), (11, 12), (11, 11), (12, 11), (12, 10), (13, 10), (13, 9), (14, 9), (14, 8), (13, 13), (12, 13),
               (12, 12), (13, 12), (13, 11), (14, 10), (11, 13), (10, 14), (9, 14), (8, 14), (14, 11), (15, 8), (15, 7), (14, 7)}
    for (x, y) in pts:
        if not (0 <= x < 16 and 0 <= y < 16) or (x, y) in arrache: continue
        dx, dy = x - cx, y - cy; d = math.hypot(dx, dy)
        l = (-dx - dy) / max(d, 0.1)
        px[x, y] = OR[6] if l > 0.6 else OR[5] if l > 0.1 else OR[4] if l > -0.4 else OR[3] if l > -0.75 else OR[2]
        if d > 5.2: px[x, y] = OR[4] if l > 0 else OR[2]
        if 1.6 < d <= 2.6: px[x, y] = OR[2]
        if d <= 1.6: px[x, y] = (0, 0, 0, 0)
    for (x, y) in ((10, 11), (12, 9), (9, 12)): px[x, y] = OR[7]          # métal frais, discret
    for (x, y) in ((11, 10),): px[x, y] = OR[2]                           # fissure qui part vers le moyeu
    px[10, 10] = OR[3]
    for (x, y, c) in ((14, 13, 4), (15, 13, 3), (14, 14, 3), (12, 15, 4)): px[x, y] = OR[c]   # éclats
    return contour(im, OR[0])
