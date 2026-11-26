# Rouage brisé, passe 5 : forme et cassure de la passe 1 de la maquette 2 (quart arraché entre 5° et 95°, bord irrégulier, éclat),
# dents carrées et couleurs de la passe 2
import math
from px import *
from patine import RAMPE as R, REFLET
from PIL import Image
def rouage_brise():
    im = neuf(); px = im.load()
    cx, cy = 7.0, 7.5                                                   # centre de la passe 1
    pts = set()
    for y in range(16):
        for x in range(16):
            if math.hypot(x - cx, y - cy) <= 4.7: pts.add((x, y))
    for k in range(8):                                                  # dents carrées de 2 x 2 (passe 2)
        t = math.radians(k * 45)
        tx, ty = cx + 6.0 * math.cos(t), cy + 6.0 * math.sin(t)
        x0, y0 = int(round(tx - 0.5)), int(round(ty - 0.5))
        for (x, y) in ((x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x0 + 1, y0 + 1)): pts.add((x, y))
    for (x, y) in pts:
        if not (0 <= x < 16 and 0 <= y < 16): continue
        dx, dy = x - cx, y - cy; d = math.hypot(dx, dy); a = math.degrees(math.atan2(dy, dx))
        if 5 < a < 95 and d > 2.6 - ((x * 7 + y * 3) % 3) * 0.6: continue     # cassure de la passe 1
        l = (-dx - dy) / max(d, 0.1)
        px[x, y] = R[8] if l > 0.6 else R[6] if l > 0 else R[4] if l > -0.6 else R[3]   # couleurs de la passe 2
        if 1.5 < d <= 2.5: px[x, y] = R[2]
        if d <= 1.5: px[x, y] = (0, 0, 0, 0)
    for y in range(16):                                                 # métal frais le long de la cassure (passe 1), teinte de la passe 2
        for x in range(16):
            if not px[x, y][3] or px[x, y] == R[2]: continue
            dx, dy = x - cx, y - cy; a = math.degrees(math.atan2(dy, dx))
            if math.hypot(dx, dy) > 2.5 and (abs(a - 5) < 12 or abs(a - 95) < 12): px[x, y] = R[9] if (x + y) % 3 else REFLET[0]
    for (x, y, c) in ((12, 12, 6), (13, 12, 4), (12, 13, 3), (13, 13, 3), (11, 14, 7)): px[x, y] = R[c]   # éclat (passe 1)
    return contour(im, R[0])
if __name__ == '__main__':
    import objets2, passe2
    W = Image.new('RGBA', (560, 220), (139, 139, 139, 255))
    for i, f in enumerate((objets2.rouage_brise, passe2.rouage_brise, rouage_brise)):
        W.alpha_composite(f().resize((160, 160), Image.NEAREST), (10 + i * 185, 10)); W.alpha_composite(f().resize((48, 48), Image.NEAREST), (66 + i * 185, 172))
    W.save('/tmp/nv/r5.png')
