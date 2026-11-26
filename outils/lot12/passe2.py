# Lot 12, passe 2 : câble (spires de métal, pas de quadrillage) et rouage brisé (dents carrées comme les rouages de Create)
import math
from px import *
from patine import RAMPE, REFLET
from PIL import Image
R = RAMPE
SOMBRE = dict(o=hx('2a1410'), d=hx('4a2a1c'), s=hx('6a3e26'))
def cable():
    """Tambour à deux joues de fer sombre ; le câble d'airain est enroulé en spires : chaque spire = une ligne claire au-dessus d'une ligne d'ombre."""
    im = neuf(); px = im.load()
    for y in range(3, 14):                                           # joues
        for x in (1, 2, 3, 12, 13, 14):
            px[x, y] = SOMBRE['s'] if x in (1, 12) else SOMBRE['d']
    for x in (2, 13): px[x, 2] = SOMBRE['s']; px[x, 14] = SOMBRE['d']
    for y in range(4, 13):                                           # spires
        for x in range(4, 12):
            spire = (y - 4) % 2
            base = R[7] if spire == 0 else R[3]
            if x == 4: base = R[5] if spire == 0 else R[2]
            if x == 11: base = R[5] if spire == 0 else R[2]
            px[x, y] = base
        if (y - 4) % 2 == 0: px[6, y] = R[9]; px[7, y] = R[8]         # reflet sur chaque spire
    for (x, y) in ((8, 6), (9, 10)): px[x, y] = REFLET[0]            # reflets de patine
    for (x, y, c) in ((12, 12, R[6]), (13, 13, R[5]), (14, 14, R[4])): px[x, y] = c   # bout libre
    return contour(im, SOMBRE['o'])

def rouage_brise():
    """Rouage d'airain : couronne pleine, huit dents carrées de 2 x 2 posées sur la grille, moyeu percé ;
    le quart en bas à droite est arraché (dents comprises), la cassure en métal frais, un éclat à côté."""
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
    casse = lambda x, y: x >= 8 and y >= 8 and math.hypot(x - cx, y - cy) > 3.2 + ((x * 3 + y) % 2) * 0.8
    for (x, y) in pts:
        if not (0 <= x < 16 and 0 <= y < 16) or casse(x, y): continue
        dx, dy = x - cx, y - cy; d = math.hypot(dx, dy)
        l = (-dx - dy) / max(d, 0.1)
        px[x, y] = R[7] if l > 0.55 else R[6] if l > 0.1 else R[5] if l > -0.4 else R[4] if l > -0.75 else R[3]
        if d > 5.2: px[x, y] = R[5] if l > 0 else R[3]                 # dents un ton plus bas
        if 1.6 < d <= 2.6: px[x, y] = R[2]
        if d <= 1.6: px[x, y] = (0, 0, 0, 0)
    for (x, y) in list(pts):                                           # métal frais le long de la cassure
        if 0 <= x < 16 and 0 <= y < 16 and px[x, y][3] and any(casse(x + i, y + j) and (x + i, y + j) in pts for i, j in ((1, 0), (0, 1), (1, 1))):
            px[x, y] = R[9] if (x + y) % 3 else REFLET[0]
    for (x, y, c) in ((13, 13, R[6]), (14, 13, R[4]), (13, 14, R[3]), (14, 14, R[3])): px[x, y] = c   # éclat
    return contour(im, R[0])
