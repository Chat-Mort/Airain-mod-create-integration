"""Panorama sobre : un mur de roues dentées en bronze sur fond presque noir, à 360°."""
import math, random, os
from PIL import Image
R = random.Random(412)
B = 256
def vec(az, el):
    a, e = math.radians(az), math.radians(el)
    return (math.cos(e) * math.sin(a), math.sin(e), math.cos(e) * math.cos(a))
ROUES = []
for i in range(26):
    az = i * (360 / 26) + R.uniform(-6, 6); el = R.choice((-38, -20, -4, 12, 28, 44)) + R.uniform(-6, 6)
    plan = R.choices((0, 1, 2), (4, 3, 2))[0]
    r = {0: R.uniform(20, 32), 1: R.uniform(13, 22), 2: R.uniform(8, 15)}[plan]
    ROUES.append((plan, az, el, r, R.choice((10, 12, 14, 16)), R.random(), R.choice((5, 6, 8))))
ROUES.sort()
TEINTES = {0: [(22, 15, 10), (30, 20, 13), (44, 30, 18)], 1: [(34, 23, 14), (46, 31, 18), (78, 52, 26)], 2: [(52, 35, 20), (70, 47, 24), (150, 104, 46)]}
def couleur(d):
    x, y, z = d
    el = math.degrees(math.asin(max(-1, min(1, y))))
    c = (13 + int(5 * (1 - abs(el) / 90)), 10 + int(3 * (1 - abs(el) / 90)), 8)          # fond presque noir, un peu plus chaud au centre
    for (plan, az, e, r, n, ph, rayons) in ROUES:
        cx = vec(az, e)
        dot = max(-1, min(1, x * cx[0] + y * cx[1] + z * cx[2]))
        dd = math.degrees(math.acos(dot))
        if dd > r + 1: continue
        # repère local autour du centre de la roue (est, nord) pour l'angle autour du moyeu
        est = (math.cos(math.radians(az)), 0, -math.sin(math.radians(az)))
        nord = (cx[1] * est[2] - cx[2] * est[1], cx[2] * est[0] - cx[0] * est[2], cx[0] * est[1] - cx[1] * est[0])
        u = x * est[0] + y * est[1] + z * est[2]; v = x * nord[0] + y * nord[1] + z * nord[2]
        a = math.atan2(v, u)
        dent = math.cos(n * a + ph * 6.283) > 0.25
        if not (dd < r * 0.82 or (dd < r and dent)): continue
        if dd < r * 0.10: continue                                                         # axe : on voit au travers
        if r * 0.30 < dd < r * 0.66 and math.cos(rayons * (a + ph)) < -0.15: continue        # ajours entre les rayons
        sombre, moyen, clair = TEINTES[plan]
        col = moyen
        if dd > r * 0.66 or dd < r * 0.30: col = moyen
        if r * 0.10 <= dd < r * 0.16: col = clair                                          # bague du moyeu
        haut = math.sin(a) > 0.55                                                          # lumière venant d'en haut
        if r * 0.78 < dd < r * 0.82 or (dent and r * 0.82 <= dd < r and haut): col = clair if haut else sombre
        if dd > r * 0.95 and not haut: col = sombre
        c = col
    return c
def face(i):
    im = Image.new("RGB", (B, B)); px = im.load()
    for y in range(B):
        for x in range(B):
            u = (x + 0.5) / B * 2 - 1; v = (y + 0.5) / B * 2 - 1
            d = {0: (u, -v, 1), 1: (1, -v, -u), 2: (-u, -v, -1), 3: (-1, -v, u), 4: (u, 1, v), 5: (u, -1, -v)}[i]
            n = math.sqrt(sum(t * t for t in d)); px[x, y] = couleur(tuple(t / n for t in d))
    return im.resize((1024, 1024), Image.NEAREST)
if __name__ == "__main__":
    os.makedirs("panorama", exist_ok=True)
    for i in range(6): face(i).save("panorama/panorama_%d.png" % i)
