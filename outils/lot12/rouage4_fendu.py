# Rouage brisé, passe 4 : le rouage est fendu en deux morceaux — un quart s'est détaché et a glissé,
# un vide franc et déchiqueté les sépare (on voit la cassure des deux côtés).
import math
from px import *
from passe3 import OR
from PIL import Image
def rouage_brise():
    cx, cy = 6.5, 6.5
    pts = set()
    for y in range(-2, 18):
        for x in range(-2, 18):
            if math.hypot(x - cx, y - cy) <= 4.4: pts.add((x, y))
    for k in range(8):
        t = math.radians(k * 45 + 22.5)
        tx, ty = cx + 5.6 * math.cos(t), cy + 5.6 * math.sin(t)
        x0, y0 = int(round(tx - 0.5)), int(round(ty - 0.5))
        for (x, y) in ((x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x0 + 1, y0 + 1)): pts.add((x, y))
    # fissure en zigzag qui traverse tout le rouage, du haut à droite vers le bas à gauche, en passant par le moyeu
    def cote(x, y):
        z = (x + y) % 4; zig = (0, 1, 2, 1)[z]
        v = (x - cx) - (y - cy) * 0.35 + zig - 1
        if abs(v) < 0.9: return None                                 # le vide de la fissure
        return 'eclat' if v > 0 else 'corps'
    morceau = lambda x, y: cote(x, y) if math.hypot(x - cx, y - cy) > 1.4 else None
    im = neuf(); px = im.load()
    def teinte(x, y, l, d, bord):
        c = OR[6] if l > 0.6 else OR[5] if l > 0.1 else OR[4] if l > -0.4 else OR[3] if l > -0.75 else OR[2]
        if d > 4.7: c = OR[4] if l > 0 else OR[2]
        if 1.4 < d <= 2.4: c = OR[2]
        if bord: c = OR[7]                                          # métal frais sur la tranche cassée
        return c
    for (x, y) in pts:
        m = morceau(x, y)
        if m is None: continue
        dx, dy = x - cx, y - cy; d = math.hypot(dx, dy); l = (-dx - dy) / max(d, 0.1)
        bord = any(morceau(x + i, y + j) is None and (x + i, y + j) in pts and math.hypot(x + i - cx, y + j - cy) > 1.4 for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        X, Y = (x + 2, y + 1) if m == 'eclat' else (x, y)             # la moitié droite s'est écartée
        if 0 <= X < 16 and 0 <= Y < 16:
            px[X, Y] = teinte(x, y, l, d, bord and d > 2.4)
            if m == 'eclat' and not bord and (x + y) % 5 == 0: px[X, Y] = OR[3]   # l'éclat, un peu dans l'ombre
    return contour(im, OR[0])
if __name__ == '__main__':
    W = Image.new('RGBA', (360, 220), (139, 139, 139, 255))
    W.alpha_composite(rouage_brise().resize((176, 176), Image.NEAREST), (10, 10)); W.alpha_composite(rouage_brise().resize((48, 48), Image.NEAREST), (220, 70))
    W.save('/tmp/nv/r4.png')
