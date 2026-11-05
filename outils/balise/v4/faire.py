"""Balise de défense : textures 64 x 64 (4 pixels par unité de modèle) et forme du bloc."""
import json, math, os, random
from PIL import Image
OUT = os.path.dirname(os.path.abspath(__file__))
random.seed(5)
K = 4

def neuf(): return Image.new("RGBA", (64, 64), (0, 0, 0, 0))
def mix(a, b, t): t = max(0, min(1, t)); return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))
def clair(c, f): return tuple(max(0, min(255, int(v*f))) for v in c)
def put(p, x, y, c): p[x, y] = tuple(int(v) for v in c[:3]) + (255,)
def lum(a): return 0.5 + 0.5*math.cos(math.radians(a - 225))      # lumière venant d'en haut à gauche (écran)

LAI = [(84, 52, 20), (138, 92, 34), (190, 138, 56), (224, 176, 86), (248, 214, 140), (255, 240, 196)]
FON = [(18, 17, 22), (32, 31, 38), (46, 45, 53), (62, 61, 70), (92, 90, 100)]
CUI = [(92, 40, 24), (150, 72, 44), (196, 110, 70), (232, 156, 112)]
ROU = [(80, 6, 6), (140, 16, 12), (206, 36, 24), (250, 90, 52), (255, 170, 120), (255, 236, 210)]
CREME = (238, 230, 208)

def metal(p, x0, y0, w, h, pal, brosse=True, biseau=True):
    for y in range(h):
        strie = random.uniform(-0.06, 0.06) if brosse else 0
        for x in range(w):
            t = 0.5 + strie + random.uniform(-0.03, 0.03)
            c = mix(pal[2], pal[3], t)
            if biseau:
                if x == 0 or y == 0: c = pal[4]
                elif x == 1 or y == 1: c = pal[3]
                if x == w-1 or y == h-1: c = pal[0]
                elif x == w-2 or y == h-2: c = pal[1]
            put(p, x0+x, y0+y, c)

def rivet(p, cx, cy, pal=LAI):
    for y in range(-2, 3):
        for x in range(-2, 3):
            r = math.hypot(x, y)
            if r > 2.2: continue
            c = pal[5] if (x, y) in ((-1, -1), (0, -1), (-1, 0)) else pal[3] if r < 1.2 else pal[1] if x + y > 0 else pal[2]
            put(p, cx+x, cy+y, c)

def disque(p, cx, cy, rmax, fn):
    for y in range(int(cy-rmax-1), int(cy+rmax+2)):
        for x in range(int(cx-rmax-1), int(cx+rmax+2)):
            dx, dy = x+0.5-cx, y+0.5-cy; r = math.hypot(dx, dy)
            if r > rmax: continue
            c = fn(r, math.degrees(math.atan2(dy, dx)) % 360)
            if c is not None: put(p, x, y, c)

def renfoncement(p, x0, y0, w, h, pal):
    for y in range(h):
        for x in range(w):
            c = pal[1]
            if x == 0 or y == 0: c = pal[0]
            if x == w-1 or y == h-1: c = pal[3]
            put(p, x0+x, y0+y, c)

# ===================== socle : côté (0,0) 56x8, dessus (0,8) 56x56
t = neuf(); p = t.load()
metal(p, 0, 0, 56, 8, FON, brosse=False)
for i in range(5):
    bx = 6 + i*11
    for (x, y, c) in ((0, 0, FON[4]), (1, 0, FON[3]), (0, 1, FON[3]), (1, 1, FON[1])): put(p, bx+x, 3+y, mix(c, (150, 140, 120), 0.4))
metal(p, 0, 8, 56, 56, FON, brosse=False)
for i in range(6, 50):
    put(p, i, 14, FON[0]); put(p, i, 15, FON[3]); put(p, i, 57, FON[0]); put(p, i, 58, FON[3])
    put(p, 6, 8+i-0 if i < 50 else 8, FON[0])
for j in range(14, 59): put(p, 6, j, FON[0]); put(p, 7, j, FON[3]); put(p, 49, j, FON[0]); put(p, 50, j, FON[3])
for (cx, cy) in ((3, 11), (52, 11), (3, 60), (52, 60)):
    disque(p, cx+0.5, cy+0.5, 2.6, lambda r, a: mix((120, 112, 98), (190, 180, 160), lum(a)) if r > 1.2 else (90, 84, 74))
t.save(f"{OUT}/balise_socle.png")

# ===================== corps : faces 40x24
def fond():
    t = neuf(); p = t.load(); metal(p, 0, 0, 40, 24, LAI)
    for (x, y) in ((3, 3), (36, 3), (3, 20), (36, 20)): rivet(p, x, y)
    return t, p

# --- nord : manomètre
t, p = fond()
def mano(r, a):
    if r > 9.6: return mix(LAI[0], LAI[1], 0.5)                                            # ombre portée
    if r > 7.9: return mix(LAI[1], LAI[5], lum(a))                                         # lunette
    if r > 7.2: return LAI[0]
    if r < 1.3: return (36, 30, 26) if r > 0.6 else (120, 110, 100)                        # axe
    aig = abs(((a - 300) + 180) % 360 - 180)
    if r < 6.2 and aig < max(6, 22 / r): return (180, 20, 14) if r > 1 else (36, 30, 26)  # aiguille
    arc = (a - 135) % 360                                                                  # cadran sur 270° depuis le bas gauche
    if arc < 270 and 5.6 < r < 7.0:
        if arc > 220: return (200, 50, 36)                                                 # zone rouge
        if int(arc) % 30 < 5: return (50, 44, 40)                                          # graduations
    return mix(CREME, (255, 252, 240), 1 - lum(a)*0.6) if r < 7.2 else None
disque(p, 20, 12, 10.2, mano)
for (x, y) in ((15, 7), (16, 7), (15, 8)): put(p, x, y, (255, 255, 255))                 # reflet du verre
t.save(f"{OUT}/balise_corps_nord.png")

# --- sud : engrenage dans un logement
t, p = fond()
renfoncement(p, 8, 1, 24, 22, LAI)
def roue(r, a):
    dent = (a % 36) < 15
    if r > 9.6 or (r > 7.6 and not dent): return None
    l = lum(a)
    if r > 6.2: return mix(CUI[1], CUI[3], l)                                              # dents et jante
    if r > 5.2: return CUI[0]
    if r < 1.4: return (40, 28, 22)
    if r < 3.0: return mix(CUI[1], CUI[3], l)                                              # moyeu
    return mix(CUI[1], CUI[2], l) if (a % 72) < 16 else LAI[0]                             # rayons
disque(p, 20, 12, 9.8, roue)
t.save(f"{OUT}/balise_corps_sud.png")

# --- est : vanne (volant rouge sur un départ de tuyau)
t, p = fond()
for y in range(12, 24):
    for x in range(16, 25):
        put(p, x, y, CUI[3] if x == 17 else CUI[2] if x < 21 else CUI[1] if x < 24 else CUI[0])
for x in range(14, 27):
    for y in (19, 20): put(p, x, y, LAI[3] if y == 19 else LAI[1])                         # bride
def volant(r, a):
    if r > 8.4: return None
    l = lum(a)
    if r > 6.4: return mix((120, 16, 12), (236, 70, 50), l)
    if r < 1.8: return (70, 64, 60) if r > 0.8 else (160, 150, 140)
    if (a + 45) % 90 < 14: return mix((120, 16, 12), (210, 50, 36), l)                     # rayons
    return None
disque(p, 20.5, 11, 8.4, volant)
t.save(f"{OUT}/balise_corps_est.png")

# --- ouest : plaque à l'emblème (roue couronnée)
t, p = fond()
SOMBRE = [(30, 20, 12), (52, 36, 22), (70, 50, 30), (100, 74, 44)]
renfoncement(p, 9, 1, 22, 22, SOMBRE)
def embleme(r, a):
    dent = (a % 45) < 20
    if r > 6.2 or (r > 4.9 and not dent): return None
    if r < 1.6: return SOMBRE[1]
    return mix(LAI[2], LAI[5], lum(a)) if r > 2.6 else LAI[1]
disque(p, 20, 14.5, 6.2, embleme)
COURONNE = ["X...X...X", "XX.XXX.XX", "XXXXXXXXX", ".XXXXXXX."]
for yy, ligne in enumerate(COURONNE):
    for xx, ch in enumerate(ligne):
        if ch == "X": put(p, 16+xx, 3+yy, LAI[4] if yy < 2 else LAI[3])
t.save(f"{OUT}/balise_corps_ouest.png")

# --- dessus du corps 40x40
t = neuf(); p = t.load(); metal(p, 0, 0, 40, 40, LAI)
for (x, y) in ((3, 3), (36, 3), (3, 36), (36, 36)): rivet(p, x, y)
for i in range(8, 32):
    put(p, i, 8, LAI[1]); put(p, i, 31, LAI[4]); put(p, 8, i, LAI[1]); put(p, 31, i, LAI[4])
disque(p, 20, 20, 7.6, lambda r, a: (34, 24, 14) if r < 5 else mix(LAI[0], LAI[4], 1-lum(a)) if r < 6.2 else mix(LAI[1], LAI[5], lum(a)))
t.save(f"{OUT}/balise_corps_dessus.png")

# ===================== lampe : côté (0,0) 24x20 ; dessus (0,20) 24x24 ; chapeau côté (24,0) 16x2, dessus (24,2) 16x16 ;
#                      tige côté (40,0) 8x12, dessus (40,12) 8x8
t = neuf(); p = t.load()
for y in range(20):
    for x in range(24):
        if y < 3 or y > 16:                                                                # bagues haute et basse
            c = [LAI[4], LAI[3], LAI[1]][y] if y < 3 else [LAI[3], LAI[2], LAI[0]][y-17]
        elif x < 2 or x > 21: c = LAI[3] if x in (0, 22) else LAI[1]                       # montants
        elif x in (8, 15): c = LAI[1] if y % 3 else LAI[3]                                 # barreaux
        else:
            d = math.hypot((x - 11.5)/1.6, (y - 9.5)/1.1)
            c = ROU[5] if d < 1.4 else ROU[4] if d < 2.6 else ROU[3] if d < 4 else ROU[2] if d < 5.6 else ROU[1]
        put(p, x, y, c)
for (x, y) in ((3, 4), (4, 4), (3, 5), (17, 4)): put(p, x, y, (255, 214, 196))            # reflets
for y in range(20, 44):
    for x in range(24):
        d = math.hypot(x - 11.5, y - 31.5)
        bord = x < 2 or x > 21 or y < 22 or y > 41
        put(p, x, y, (LAI[3] if (x < 1 or y < 21) else LAI[1]) if bord else ROU[5] if d < 3 else ROU[4] if d < 5.5 else ROU[3] if d < 8 else ROU[2])
for x in range(24, 40): put(p, x, 0, LAI[4]); put(p, x, 1, LAI[2])
metal(p, 24, 2, 16, 16, LAI, brosse=False)
disque(p, 32, 10, 5, lambda r, a: mix(LAI[2], LAI[5], lum(a)) if r > 2.2 else LAI[0])    # dôme et évent
for y in range(12):
    for x in range(8):
        c = CUI[3] if x == 1 else CUI[2] if x < 4 else CUI[1] if x < 7 else CUI[0]
        if y in (2, 3, 9, 10): c = LAI[4] if x < 3 else LAI[2] if x < 6 else LAI[0]          # colliers
        put(p, 40+x, y, c)
for y in range(12, 20):
    for x in range(40, 48): put(p, x, y, CUI[2])
t.save(f"{OUT}/balise_lampe.png")

# ===================== forme (uv = pixels / 4)
def h(u): return [v / K for v in u]
def cotes(uv, tex=None, par_face=None, dessus=None, dessous=None):
    f = {d: {"texture": (par_face or {}).get(d, tex), "uv": h(uv)} for d in ("north", "south", "east", "west")}
    if dessus: f["up"] = {"texture": dessus[0], "uv": h(dessus[1])}
    if dessous: f["down"] = {"texture": dessous[0], "uv": h(dessous[1])}
    return f
modele = {"parent": "minecraft:block/block",
  "textures": {"particle": "kubejs:block/balise_corps_nord", "socle": "kubejs:block/balise_socle",
               "nord": "kubejs:block/balise_corps_nord", "sud": "kubejs:block/balise_corps_sud",
               "est": "kubejs:block/balise_corps_est", "ouest": "kubejs:block/balise_corps_ouest",
               "dessus": "kubejs:block/balise_corps_dessus", "lampe": "kubejs:block/balise_lampe"},
  "elements": [
    {"from": [1, 0, 1], "to": [15, 2, 15], "faces": cotes([0, 0, 56, 8], "#socle", dessus=("#socle", [0, 8, 56, 64]), dessous=("#socle", [0, 8, 56, 64]))},
    {"from": [3, 2, 3], "to": [13, 8, 13], "faces": cotes([0, 0, 40, 24], par_face={"north": "#nord", "south": "#sud", "east": "#est", "west": "#ouest"},
                                                         dessus=("#dessus", [0, 0, 40, 40]))},
    {"from": [7, 8, 7], "to": [9, 11, 9], "faces": cotes([40, 0, 48, 12], "#lampe", dessus=("#lampe", [40, 12, 48, 20]))},
    {"from": [5, 10.5, 5], "to": [11, 15.5, 11], "faces": cotes([0, 0, 24, 20], "#lampe", dessus=("#lampe", [0, 20, 24, 44]), dessous=("#lampe", [0, 20, 24, 44]))},
    {"from": [6, 15.5, 6], "to": [10, 16, 10], "faces": cotes([24, 0, 40, 2], "#lampe", dessus=("#lampe", [24, 2, 40, 18]))}]}
json.dump(modele, open(f"{OUT}/balise_defense_forme.json", "w"), indent=2)
