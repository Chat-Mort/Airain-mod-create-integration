"""Panorama de l'écran d'accueil : une cité de l'Empire au crépuscule, peinte en pixel art, vue à 360°.
Chaque pixel des 6 faces est calculé depuis sa direction de vue : les raccords tombent juste."""
import math, random
from PIL import Image
R = random.Random(1789)
B = 256                      # résolution « pixel art » d'une face (agrandie ×4 en 1024)
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def pal(stops, t, pas=None):
    if pas: t = round(t * pas) / pas                       # dégradé en paliers, façon pixel art
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1: return lerp(c0, c1, (t - t0) / (t1 - t0) if t1 > t0 else 0)
    return stops[-1][1]
CIEL = [(0.0, (232, 150, 70)), (0.06, (214, 112, 64)), (0.16, (150, 72, 78)), (0.32, (60, 52, 78)), (0.55, (26, 38, 56)), (1.0, (12, 16, 26))]
SOL = (18, 14, 12)
SILHOUETTE = (24, 18, 16); SILH2 = (40, 28, 22)
FENETRE = [(255, 196, 92), (240, 160, 70), (255, 220, 140)]
# ---------------------------------------------------------------- la ligne des toits, faite de bâtiments tirés au hasard
def ville():
    segs, az = [], 0.0
    while az < 360:
        w = R.uniform(2.0, 6.0); h = R.uniform(1.2, 6.5)
        kind = R.choices(["toit", "cheminee", "reservoir", "pignon"], [5, 2, 1, 2])[0]
        segs.append((az, az + w, h, kind, R.random())); az += w
    return segs
SEGS = ville()
def proches():            # les toits proches, au premier plan (sous l'horizon)
    segs, az = [], 0.0
    while az < 360:
        w = R.uniform(8.0, 16.0); top = R.uniform(-22.0, -9.0)
        segs.append((az, az + w, top, R.random(), R.random() < 0.35)); az += w + R.uniform(0.6, 1.8)
    return segs
PROCHES = proches()
TOUR = (0.0, 2.6, 17.0)                              # la tour d'horloge, droit devant (az 0°)
ROUES = [(42.0, -9.0, 26.0, 10, 0.1), (238.0, -12.0, 34.0, 12, 0.25), (148.0, -4.0, 15.0, 8, 0.0)]   # az, élévation du centre, rayon, dents, phase
BALLONS = [(70.0, 22.0, 1.0), (300.0, 17.0, 0.8), (190.0, 27.0, 0.6)]
def dans_roue(az, el, cx, cy, r, n, ph):
    dx = ((az - cx + 180) % 360) - 180; dy = el - cy
    d = math.hypot(dx, dy); a = math.atan2(dy, dx)
    dent = math.cos(n * a + ph * 6.28) > 0.3
    if d < r * 0.30: return 0
    if d < r * 0.30 + 1.0: return 2                 # moyeu
    if d <= r * 0.82 or (d <= r and dent):
        rayon = any(abs(((a * 180 / math.pi) - k * (360 / 6) + 720) % 60 - 30) > 27 for k in range(1))
        if r * 0.36 < d < r * 0.66 and abs(math.sin(3 * a)) > 0.45: return 0          # ajours entre les rayons
        return 3 if (r * 0.78 < d <= r * 0.82) else 1
    return 0
def couleur(az, el):
    az %= 360
    # ciel
    t = max(0.0, min(1.0, el / 90.0)) ** 0.6
    c = pal(CIEL, t, pas=22)
    # soleil couchant derrière la cité, et son halo
    ds = math.hypot(((az - 200 + 180) % 360) - 180, el - 2.5)
    if ds < 4.2 and el > -0.5: c = (255, 226, 150) if ds < 3.4 else (250, 190, 110)
    elif ds < 16 and el > -1: c = lerp(c, (240, 170, 90), (1 - ds / 16) * 0.35)
    # étoiles
    if el > 38 and R.random() < 0.0 : pass
    h = (int(az * 7.3) * 92821 + int(el * 7.3) * 68917) % 997
    if el > 34 and h < 3: c = (220, 222, 230)
    # nuages en bandes
    for (a0, a1, e0, ep) in ((20, 95, 19, 2.2), (120, 170, 26, 1.6), (205, 290, 15, 2.6), (310, 355, 23, 1.8)):
        if a0 <= az <= a1 and abs(el - e0 - 1.2 * math.sin(az / 9)) < ep * (1 - abs((az - (a0 + a1) / 2) / ((a1 - a0) / 2)) ** 3):
            c = lerp(c, (196, 112, 96) if el - e0 < 0 else (120, 70, 86), 0.55)
    # dirigeables
    for (ax, ae, s) in BALLONS:
        dx = ((az - ax + 180) % 360) - 180; dy = el - ae
        if (dx / (5.0 * s)) ** 2 + (dy / (1.7 * s)) ** 2 < 1: c = (52, 40, 40) if dy > -0.4 * s else (36, 28, 30)
        if abs(dy) < 0.35 * s and abs(dx) < 5.0 * s and (dx / (5.0 * s)) ** 2 + (dy / (1.7 * s)) ** 2 < 1: c = (150, 96, 48)   # bande de laiton
        if -2.6 * s < dy < -1.9 * s and abs(dx) < 1.4 * s: c = (40, 30, 30)                   # nacelle
        if -1.9 * s < dy < -1.7 * s and abs(abs(dx) - 1.0 * s) < 0.2 * s: c = (40, 30, 30)
    # grandes roues dentées enfouies à l'horizon
    for (cx, cy, r, n, ph) in ROUES:
        k = dans_roue(az, el, cx, cy, r, n, ph)
        if k: c = {1: (46, 32, 24), 2: (70, 48, 30), 3: (128, 82, 44)}[k]
    if el < 0:
        c = SOL
        if el > -6 and (h % 331) < 3: c = FENETRE[h % 3]                                    # lumières lointaines
        if -2.2 < el < -1.6 and int(az * 3) % 2 == 0: c = (60, 44, 30)                       # voie ferrée
    if el < 0:
        # rue entre les toits proches : réverbères
        if el < -6 and (h % 97) < 2: c = (255, 205, 120)
        # les toits proches : façades sombres, fenêtres en grille, faîte de cuivre vert-de-gris, cheminées qui fument
        for (a0, a1, top, v, chem) in PROCHES:
            if a0 <= az < a1:
                if el < top:
                    c = (22, 16, 14) if v < 0.5 else (30, 21, 17)
                    gx, gy = (az - a0) % 1.6, (top - el) % 2.4
                    if 0.5 < gx < 1.1 and 0.9 < gy < 1.9 and el < top - 1.2 and ((int((az - a0) / 1.6) * 31 + int((top - el) / 2.4) * 17) % 7) < 2:
                        c = FENETRE[int(az * 3 + el) % 3] if v < 0.8 else (90, 120, 110)
                    if top - 0.9 < el < top: c = (78, 118, 100)
                    if top - 1.2 < el <= top - 0.9: c = (40, 58, 50)
                if chem:
                    xm = a0 + (a1 - a0) * 0.3
                    if abs(az - xm) < 0.9 and top <= el < top + 6: c = (64, 36, 26) if abs(az - xm) < 0.7 else (40, 24, 18)
                    fx = xm + (el - top - 6) * 0.5
                    if top + 6 <= el < top + 16 and abs(az - fx - math.sin(el * 0.6)) < 1.0 + (el - top - 6) * 0.25:
                        c = lerp(c, (200, 182, 172), 0.5)
        # la grande conduite de laiton qui fait le tour de la cité
        if -34.5 < el < -30.5:
            c = (176, 124, 50) if el > -31.6 else ((132, 88, 34) if el > -33.4 else (86, 56, 24))
            if (az % 15) < 1.0: c = (70, 48, 26) if abs(el + 32.5) < 2.0 else (210, 160, 70)          # brides
            if (az % 15) < 1.0 and abs(el + 32.5) >= 2.0: c = (224, 176, 84)
    # la cité
    for (a0, a1, hh, kind, v) in SEGS:
        if a0 <= az < a1:
            top = hh
            if kind == "pignon": top = hh + 1.6 * (1 - abs((az - (a0 + a1) / 2) / ((a1 - a0) / 2)))
            if 0 <= el < top and not any(p0 <= az < p1 and el < pt for (p0, p1, pt, pv, pc) in PROCHES):
                c = SILHOUETTE if v < 0.6 else SILH2
                if (h % 61) < 3 and el < top - 0.6: c = FENETRE[h % 3]
            if kind == "cheminee":
                xm = a0 + (a1 - a0) * 0.7
                if abs(az - xm) < 0.45 and el < hh + 4.5: c = (60, 34, 26) if el > hh else c
                fumee_x = xm + (el - hh - 4.5) * 0.35
                if el > hh + 4.5 and el < hh + 13 and abs(az - fumee_x - 0.8 * math.sin(el)) < 0.7 + (el - hh - 4.5) * 0.18:
                    c = lerp(c, (196, 176, 168), 0.55)
            if kind == "reservoir":
                xm = (a0 + a1) / 2
                if abs(az - xm) < 1.2 and hh + 1.6 < el < hh + 3.4: c = (92, 120, 104)              # cuve de cuivre vert-de-gris
                if abs(abs(az - xm) - 0.9) < 0.2 and hh <= el <= hh + 1.6: c = SILHOUETTE
    # la tour d'horloge (droit devant)
    dx = ((az - TOUR[0] + 180) % 360) - 180
    if 0 <= el < TOUR[2] and abs(dx) < TOUR[1]: c = (30, 22, 20)
    if TOUR[2] <= el < TOUR[2] + 4 and abs(dx) < TOUR[1] * (1 - (el - TOUR[2]) / 4): c = (54, 70, 62)  # toit de tôle verte
    if TOUR[2] + 4 <= el < TOUR[2] + 6.5 and abs(dx) < 0.2: c = (54, 70, 62)                         # paratonnerre
    dcad = math.hypot(dx, el - (TOUR[2] - 3.4))
    if dcad < 1.8: c = (250, 214, 130) if dcad < 1.5 else (150, 100, 46)                           # cadran éclairé
    if dcad < 1.5 and ((abs(dx) < 0.18 and 0 < el - (TOUR[2] - 3.4) < 1.2) or (abs(el - (TOUR[2] - 3.4)) < 0.18 and 0 < dx < 0.9)):
        c = (60, 40, 24)                                                                                 # aiguilles
    if 0 <= el < TOUR[2] - 6 and abs(dx) < TOUR[1] - 0.6 and (int(el * 2) % 3 == 0) and abs(dx) % 1.2 < 0.5: c = FENETRE[0]
    return c
def face(i):
    im = Image.new("RGB", (B, B)); px = im.load()
    for y in range(B):
        for x in range(B):
            u = (x + 0.5) / B * 2 - 1; v = (y + 0.5) / B * 2 - 1
            d = {0: (u, -v, 1), 1: (1, -v, -u), 2: (-u, -v, -1), 3: (-1, -v, u), 4: (u, 1, v), 5: (u, -1, -v)}[i]
            az = math.degrees(math.atan2(d[0], d[2])); el = math.degrees(math.atan2(d[1], math.hypot(d[0], d[2])))
            px[x, y] = couleur(az, el)
    return im.resize((1024, 1024), Image.NEAREST)
if __name__ == "__main__":
    import os
    os.makedirs("panorama", exist_ok=True)
    faces = [face(i) for i in range(6)]
    for i, f in enumerate(faces): f.save("panorama/panorama_%d.png" % i)
    # planche : les 4 faces latérales côte à côte
    pl = Image.new("RGB", (4 * 512, 512))
    for i in range(4): pl.paste(faces[i].resize((512, 512), Image.NEAREST), (i * 512, 0))
    pl.save("apercu_panorama.png")
