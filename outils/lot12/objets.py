# Lot 12 : objets de matière d'airain (16 x 16) — lingot, plaque, pépite, fil, câble
from px import *
from PIL import Image
A = AIR

def ligne(px, x0, y0, x1, y1, col, seulement=None):
    n = max(abs(x1 - x0), abs(y1 - y0))
    for k in range(n + 1):
        x = round(x0 + (x1 - x0) * k / n); y = round(y0 + (y1 - y0) * k / n)
        if 0 <= x < 16 and 0 <= y < 16 and (seulement is None or px[x, y][3]): px[x, y] = col

def lingot():
    """Lingot : barre en perspective aux arêtes nettes ; dessus clair biseauté, long côté moyen, bout sombre, poinçon."""
    im = neuf(); px = im.load()
    poly(im, [(1, 8), (11, 3), (15, 5), (5, 10)], A['c'])            # dessus
    poly(im, [(5, 10), (15, 5), (15, 8), (5, 13)], A['m'])           # long côté avant
    poly(im, [(1, 8), (5, 10), (5, 13), (1, 11)], A['s'])            # bout
    ligne(px, 5, 10, 15, 5, A['h'])                                  # arête avant du dessus : le reflet
    ligne(px, 2, 8, 11, 4, A['b'], True)                             # biseau du fond
    ligne(px, 5, 13, 15, 8, A['s'], True)                            # pied du long côté
    ligne(px, 1, 11, 5, 13, A['d'], True)
    px[8, 7] = A['m']; px[9, 6] = A['m']; px[9, 7] = A['h']          # poinçon de l'Empire
    return contour(im)

def plaque():
    """Plaque : tôle presque de face, légèrement inclinée, tranche visible en bas et à droite, quatre trous de rivet,
    coin bas droit un peu relevé, reflet en bande diagonale."""
    im = neuf(); px = im.load()
    poly(im, [(2, 3), (13, 2), (14, 11), (1, 12)], A['b'])           # face
    poly(im, [(1, 12), (14, 11), (14, 12), (1, 13)], A['s'])         # tranche du bas
    ligne(px, 14, 3, 14, 11, A['m'])                                   # tranche de droite
    for y in range(16):                                              # dégradé vertical
        for x in range(16):
            if px[x, y] == A['b'] and y <= 4: px[x, y] = A['c']
            elif px[x, y] == A['b'] and y >= 10: px[x, y] = A['m']
    for k, col in ((0, A['c']), (1, A['h']), (2, A['h']), (3, A['c'])):   # reflet : bande de 4 texels
        ligne(px, 3 + k, 11, 9 + k, 3, col, True)
    for (x, y) in ((3, 4), (12, 3), (3, 10), (12, 10)):              # trous de rivet
        px[x, y] = A['d']; px[x + 1, y] = A['s'] if px[x + 1, y][3] else px[x + 1, y]
    ligne(px, 2, 3, 13, 2, A['h'], True)                             # arête haute éclairée
    return contour(im)

def pepite():
    g = ["................",
         "................",
         "................",
         "................",
         "................",
         "......ooo.......",
         ".....ohcbo......",
         "....ohccbmo.....",
         "....ocbbmsooo...",
         "....obmmsohcbo..",
         ".....ossdocbmso.",
         "......oooobmsdo.",
         "..........osddo.",
         "...........ooo..",
         "................",
         "................"]
    return depuis(g, A)

def fil():
    """Fil d'airain : bobine de fil fin enroulé en boucles lâches, sans tambour."""
    im = neuf(); px = im.load()
    import math
    for k, (cx, cy, rx, ry) in enumerate(((7.5, 8.5, 6.0, 4.2), (8.0, 8.0, 5.0, 3.4), (7.2, 8.8, 4.2, 2.8))):
        for t in range(0, 360, 4):
            a = math.radians(t); x = round(cx + rx * math.cos(a)); y = round(cy + ry * math.sin(a))
            px[x, y] = A['c'] if math.sin(a) < -0.2 else A['b'] if math.cos(a) < 0.3 else A['s']
    # le bout du fil qui s'échappe
    for (x, y) in ((13, 11), (14, 12), (14, 13), (15, 14)): px[x, y] = A['b']
    return contour(im)

def cable():
    """Câble d'airain : tambour à deux joues sombres, câble épais toronné enroulé, bout libre."""
    g = ["................",
         "................",
         "..ooo......ooo..",
         ".oddso....oddso.",
         ".odsdooooooddso.",
         ".odsdcbcbcbdsdo.",
         ".odsdbmbmbmdsdo.",
         ".odsdcbcbcbdsdo.",
         ".odsdbmbmbmdsdo.",
         ".odsdcbcbcbdsdo.",
         ".odsdmsmsmsdsdo.",
         ".odsdooooooddso.",
         ".oddso....oddsoo",
         "..ooo......oocbo",
         ".............oo.",
         "................"]
    return depuis(g, A)

OBJETS = dict(airain_ingot=lingot, airain_sheet=plaque, airain_nugget=pepite, airain_wire=fil, airain_cable=cable)
if __name__ == '__main__':
    W = Image.new('RGBA', (len(OBJETS) * 2 * 200, 220), (139, 139, 139, 255))
    T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
    for i, (n, f) in enumerate(OBJETS.items()):
        W.alpha_composite(Image.open(T + n + '.png').convert('RGBA').resize((160, 160), Image.NEAREST), (i * 400 + 10, 20))
        W.alpha_composite(f().resize((160, 160), Image.NEAREST), (i * 400 + 200, 20))
    W.save('/tmp/nv/lot12.png')
