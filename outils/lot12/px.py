# Outils de dessin au pixel 16 x 16 (objets) : polygones pleins, dégradés, contour sombre automatique
from PIL import Image, ImageDraw
def hx(s, a=255): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (a,)
# airain (palette du bloc d'airain) : reflet -> ombre
AIR = dict(h=hx('fff4cf'), c=hx('f3d694'), b=hx('e1ba6e'), m=hx('c99b52'), s=hx('a8763c'), d=hx('704425'), o=hx('3a2414'))
def neuf(n=16): return Image.new('RGBA', (n, n), (0, 0, 0, 0))
def poly(im, pts, col):
    d = ImageDraw.Draw(im); d.polygon(pts, fill=col)
def contour(im, col=AIR['o']):
    px = im.load(); n = im.size[0]
    m = [[px[x, y][3] > 0 for x in range(n)] for y in range(im.size[1])]
    for y in range(im.size[1]):
        for x in range(n):
            if not m[y][x] and any(0 <= x + i < n and 0 <= y + j < im.size[1] and m[y + j][x + i] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = col
    return im
def depuis(grille, pal):
    """Dessin en texte : une lettre par pixel, '.' = vide."""
    im = neuf(len(grille[0])); px = im.load()
    for y, l in enumerate(grille):
        for x, ch in enumerate(l):
            if ch != '.': px[x, y] = pal[ch]
    return im
