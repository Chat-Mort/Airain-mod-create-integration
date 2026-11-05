"""Balise de défense : textures 32 x 32 (2 pixels par unité de modèle) et forme."""
import json, math, os, random
from PIL import Image
OUT = os.path.dirname(os.path.abspath(__file__))
random.seed(11)
def neuf(): return Image.new("RGBA", (32, 32), (0, 0, 0, 0))
def mix(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))
def var(c, a=5): d = random.randint(-a, a); return tuple(max(0, min(255, v+d)) for v in c)
def put(p, x, y, c): p[x, y] = tuple(c[:3]) + (255,)

L_OMBRE, L_BAS, L_MOY, L_HAUT, L_ECLAT = (96, 60, 22), (150, 100, 36), (200, 146, 58), (232, 184, 92), (255, 228, 156)
F_OMBRE, F_BAS, F_MOY, F_HAUT = (22, 21, 26), (38, 36, 44), (54, 52, 60), (82, 80, 90)
C_OMBRE, C_MOY, C_HAUT = (104, 46, 28), (170, 86, 52), (224, 136, 92)
R_OMBRE, R_BAS, R_MOY, R_HAUT, R_COEUR = (96, 8, 8), (160, 20, 16), (220, 44, 28), (255, 104, 64), (255, 214, 176)
CREME = (236, 228, 204)

def plaque(p, x0, y0, w, h, base, haut, bas, strie=True, a=4):
    """Plaque biseautée : bord clair en haut à gauche, sombre en bas à droite, métal brossé."""
    for y in range(h):
        teinte = var(base, a) if not strie else mix(base, haut if y % 3 == 0 else base, 0.25)
        for x in range(w):
            c = var(teinte, 2)
            if x == 0 or y == 0: c = haut
            if x == w-1 or y == h-1: c = bas
            put(p, x0+x, y0+y, c)

def rivet(p, x, y, base=L_MOY):
    put(p, x, y, L_ECLAT); put(p, x+1, y, base); put(p, x, y+1, base); put(p, x+1, y+1, L_OMBRE)

def disque(p, cx, cy, fn):
    for y in range(32):
        for x in range(32):
            r = math.hypot(x+0.5-cx, y+0.5-cy); a = math.degrees(math.atan2(y+0.5-cy, x+0.5-cx)) % 360
            c = fn(r, a)
            if c: put(p, x, y, c)

# ---------------- socle (fonte) : côté (0,0)-(28,4), dessus (0,4)-(28,32)
s = neuf(); p = s.load()
plaque(p, 0, 0, 28, 4, F_MOY, F_HAUT, F_OMBRE, strie=False)
for x in range(0, 28, 7): put(p, x+3, 2, F_OMBRE)                              # fentes de fonderie
plaque(p, 0, 4, 28, 28, F_BAS, F_HAUT, F_OMBRE, strie=False, a=3)
for i in range(3, 25):                                                          # rainure intérieure
    put(p, i, 7, F_OMBRE); put(p, i, 28, F_HAUT); put(p, 3, 4+i-0, F_OMBRE) if i < 25 else None
for i in range(7, 29): put(p, 3, i, F_OMBRE); put(p, 24, i, F_HAUT)
for (bx, by) in ((1, 5), (25, 5), (1, 29), (25, 29)):                          # boulons hexagonaux
    put(p, bx, by, (170, 160, 140)); put(p, bx+1, by, (130, 122, 108)); put(p, bx, by+1, (130, 122, 108)); put(p, bx+1, by+1, (70, 66, 60))
s.save(f"{OUT}/balise_socle.png")

# ---------------- corps : une texture par face, côté (0,0)-(20,12) ; dessus à part (0,0)-(20,20)
def fond_corps():
    t = neuf(); p = t.load()
    plaque(p, 0, 0, 20, 12, L_MOY, L_HAUT, L_OMBRE)
    for (x, y) in ((1, 1), (17, 1), (1, 9), (17, 9)): rivet(p, x, y)
    return t, p

# nord : manomètre
t, p = fond_corps()
def mano(r, a):
    if r >= 4.8: return None
    if r >= 3.9: return L_ECLAT if 200 < a < 320 else L_OMBRE if 20 < a < 160 else L_MOY          # lunette
    if r < 1.0: return (40, 34, 30)                                                                # axe
    ecart = abs(((a - 305) + 180) % 360 - 180)
    if r < 3.4 and ecart < 18 / max(r, 1): return (200, 26, 18)                                    # aiguille
    if r > 2.9 and (a > 150 or a < 30) and int(a) % 45 < 10: return (80, 70, 60)                   # graduations
    return CREME
disque(p, 10, 6, mano)
put(p, 8, 4, (255, 255, 255))                                                   # reflet du verre
t.save(f"{OUT}/balise_corps_nord.png")

# sud : engrenage
t, p = fond_corps()
for x in range(4, 16):
    for y in range(1, 11): put(p, x, y, var(L_BAS, 3))                          # renfoncement
def roue(r, a):
    dent = (a % 40) < 16
    if r < 1.2: return L_OMBRE
    if r < 2.2: return C_HAUT
    if r < 3.6: return C_MOY if int(a) % 90 < 22 else C_OMBRE                  # rayons
    if r < 4.2: return C_MOY if a > 180 else C_HAUT
    if r < 5.3 and dent: return C_MOY if a > 180 else C_HAUT
    return None
disque(p, 10, 6, roue)
t.save(f"{OUT}/balise_corps_sud.png")

# est : vanne (volant rouge sur un départ de tuyau)
t, p = fond_corps()
for y in range(3, 10):
    for x in range(8, 13): put(p, x, y, C_MOY if 9 <= x <= 11 else C_OMBRE)   # tuyau
def volant(r, a):
    if r < 1.0: return (60, 50, 44)
    if r < 3.2 and int(a + 22) % 90 < 16: return (150, 24, 18)                  # rayons
    if 3.2 <= r < 4.4: return (210, 40, 30) if a > 200 else (150, 24, 18)
    return None
disque(p, 10.5, 6, volant)
t.save(f"{OUT}/balise_corps_est.png")

# ouest : plaque à l'emblème de l'Empire (roue couronnée)
t, p = fond_corps()
for x in range(5, 15):
    for y in range(1, 11): put(p, x, y, (48, 34, 20) if (x in (5, 14) or y in (1, 10)) else (70, 50, 30))
def embleme(r, a):
    if r < 0.8: return (70, 50, 30)
    if r < 2.0: return L_HAUT
    if r < 2.8 and (a % 60) < 30: return L_MOY
    return None
disque(p, 10, 7, embleme)
for (x, y) in ((8, 3), (10, 2), (12, 3), (9, 4), (10, 4), (11, 4), (8, 4), (12, 4)): put(p, x, y, L_ECLAT)   # couronne
t.save(f"{OUT}/balise_corps_ouest.png")

# dessus du corps
t = neuf(); p = t.load()
plaque(p, 0, 0, 20, 20, L_MOY, L_HAUT, L_OMBRE)
for (x, y) in ((1, 1), (17, 1), (1, 17), (17, 17)): rivet(p, x, y)
disque(p, 10, 10, lambda r, a: (40, 28, 16) if r < 2.6 else (L_OMBRE if a < 180 else L_ECLAT) if r < 3.6 else None)
for i in range(4, 16): put(p, i, 4, L_BAS); put(p, i, 15, L_HAUT); put(p, 4, i, L_BAS); put(p, 15, i, L_HAUT)
t.save(f"{OUT}/balise_corps_dessus.png")

# ---------------- lampe : côté (0,0)-(12,10), dessus (0,10)-(12,22) ; chapeau côté (12,0)-(20,1), dessus (12,1)-(20,9) ; tige côté (20,0)-(24,6), dessus (20,6)-(24,10)
t = neuf(); p = t.load()
for y in range(10):
    for x in range(12):
        if y in (0, 9): c = L_HAUT if y == 0 else L_OMBRE
        elif y in (1, 8): c = L_MOY if y == 1 else L_BAS
        elif x in (0, 11): c = L_MOY if x == 0 else L_BAS
        elif x in (4, 7): c = L_BAS if y % 2 else L_MOY                             # barreaux de la cage
        else:
            d = math.hypot((x - 5.5) / 1.3, y - 4.5)
            c = R_COEUR if d < 1.2 else R_HAUT if d < 2.4 else R_MOY if d < 3.6 else R_BAS
        put(p, x, y, c)
put(p, 2, 3, (255, 200, 180)); put(p, 9, 3, (255, 160, 130))                       # reflets
for y in range(10, 22):
    for x in range(12):
        bord = x in (0, 11) or y in (10, 21)
        d = math.hypot(x - 5.5, y - 15.5)
        put(p, x, y, L_BAS if bord else R_COEUR if d < 2 else R_HAUT if d < 3.5 else R_MOY)
for x in range(12, 20): put(p, x, 0, L_HAUT)
plaque(p, 12, 1, 8, 8, L_HAUT, L_ECLAT, L_BAS)
for (x, y) in ((15, 4), (16, 4), (15, 5), (16, 5)): put(p, x, y, L_OMBRE)       # évent du chapeau
for y in range(6):
    put(p, 20, y, C_HAUT); put(p, 21, y, C_MOY); put(p, 22, y, C_MOY); put(p, 23, y, C_OMBRE)
    if y in (1, 4): [put(p, x, y, L_MOY) for x in range(20, 24)]                     # colliers de laiton
for y in range(6, 10):
    for x in range(20, 24): put(p, x, y, C_MOY)
t.save(f"{OUT}/balise_lampe.png")

# ---------------- forme (uv en unités de modèle : pixel / 2)
def h(u): return [v / 2 for v in u]
def cotes(tex, uv, dessus=None, dessous=None, par_face=None):
    f = {}
    for d in ("north", "south", "east", "west"):
        f[d] = {"texture": (par_face or {}).get(d, tex), "uv": h(uv)}
    if dessus: f["up"] = {"texture": dessus[0], "uv": h(dessus[1])}
    if dessous: f["down"] = {"texture": dessous[0], "uv": h(dessous[1])}
    return f
modele = {"parent": "minecraft:block/block",
  "textures": {"particle": "kubejs:block/balise_corps_nord", "socle": "kubejs:block/balise_socle",
               "nord": "kubejs:block/balise_corps_nord", "sud": "kubejs:block/balise_corps_sud",
               "est": "kubejs:block/balise_corps_est", "ouest": "kubejs:block/balise_corps_ouest",
               "dessus": "kubejs:block/balise_corps_dessus", "lampe": "kubejs:block/balise_lampe"},
  "elements": [
    {"from": [1, 0, 1], "to": [15, 2, 15], "faces": cotes("#socle", [0, 0, 28, 4], ("#socle", [0, 4, 28, 32]), ("#socle", [0, 4, 28, 32]))},
    {"from": [3, 2, 3], "to": [13, 8, 13], "faces": cotes(None, [0, 0, 20, 12], ("#dessus", [0, 0, 20, 20]),
        par_face={"north": "#nord", "south": "#sud", "east": "#est", "west": "#ouest"})},
    {"from": [7, 8, 7], "to": [9, 11, 9], "faces": cotes("#lampe", [20, 0, 24, 6], ("#lampe", [20, 6, 24, 10]))},
    {"from": [5, 10.5, 5], "to": [11, 15.5, 11], "faces": cotes("#lampe", [0, 0, 12, 10], ("#lampe", [0, 10, 12, 22]), ("#lampe", [0, 10, 12, 22]))},
    {"from": [6, 15.5, 6], "to": [10, 16, 10], "faces": cotes("#lampe", [12, 0, 20, 1], ("#lampe", [12, 1, 20, 9]))}]}
json.dump(modele, open(f"{OUT}/balise_defense_forme.json", "w"), indent=2)
