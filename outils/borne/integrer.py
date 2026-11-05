import json, math, random
from PIL import Image
M = '/home/claude/airain-mod-create-integration/src/main/resources'
A = M + '/assets/airain'
random.seed(7)

class Modele:
    def __init__(s, nom, couleurs):
        s.nom, s.couleurs, s.el = nom, couleurs, []
    def b(s, x0, y0, z0, x1, y1, z1, c, lum=False, rot=None):
        x0, x1 = max(-16, x0), min(32, x1); y0, y1 = max(-16, y0), min(32, y1); z0, z1 = max(-16, z0), min(32, z1)
        if x1 - x0 < 0.01 or y1 - y0 < 0.01 or z1 - z0 < 0.01: return
        t = s.couleurs.index(c); u, v = (t % 4) * 4, (t // 4) * 4
        f = {"texture": "#t", "uv": [u + 0.5, v + 0.5, u + 3.5, v + 3.5]}
        if lum: f["neoforge_data"] = {"block_light": 15, "sky_light": 15}
        e = {"from": [round(x0, 3), round(y0, 3), round(z0, 3)], "to": [round(x1, 3), round(y1, 3), round(z1, 3)],
             "faces": {k: dict(f) for k in ("north", "south", "east", "west", "up", "down")}}
        if rot: e["rotation"] = rot
        if lum: e["shade"] = False
        s.el.append(e)
    def cyl(s, cx, cz, y0, y1, r, c, lum=False):      # cylindre vertical, en bandes d'un pixel le long de z
        z = math.floor(cz - r)
        while z < cz + r:
            zc = z + 0.5 - cz
            if abs(zc) <= r:
                w = math.sqrt(max(0, r * r - zc * zc)); s.b(cx - w, y0, z, cx + w, y1, z + 1, c, lum)
            z += 1
    def anneau_xz(s, cx, cz, y0, y1, r0, r1, c, lum=False):   # anneau horizontal
        z = math.floor(cz - r1)
        while z < cz + r1:
            zc = z + 0.5 - cz
            if abs(zc) <= r1:
                wo = math.sqrt(max(0, r1 * r1 - zc * zc))
                if abs(zc) >= r0: s.b(cx - wo, y0, z, cx + wo, y1, z + 1, c, lum)
                else:
                    wi = math.sqrt(r0 * r0 - zc * zc)
                    s.b(cx - wo, y0, z, cx - wi, y1, z + 1, c, lum); s.b(cx + wi, y0, z, cx + wo, y1, z + 1, c, lum)
            z += 1
    def anneau_xy(s, cx, cy, z0, z1, r0, r1, c, lum=False):   # anneau vertical (face avant)
        y = math.floor(cy - r1)
        while y < cy + r1:
            yc = y + 0.5 - cy
            if abs(yc) <= r1:
                wo = math.sqrt(max(0, r1 * r1 - yc * yc))
                if abs(yc) >= r0: s.b(cx - wo, y, z0, cx + wo, y + 1, z1, c, lum)
                else:
                    wi = math.sqrt(r0 * r0 - yc * yc)
                    s.b(cx - wo, y, z0, cx - wi, y + 1, z1, c, lum); s.b(cx + wi, y, z0, cx + wo, y + 1, z1, c, lum)
            y += 1
    def rouage_yz(s, cy, cz, x0, x1, r, c, dents=8):          # roue dentée dans le plan YZ (flanc)
        y = math.floor(cy - r)
        while y < cy + r:
            yc = y + 0.5 - cy
            if abs(yc) <= r:
                w = math.sqrt(max(0, r * r - yc * yc)); s.b(x0, y, cz - w, x1, y + 1, cz + w, c)
            y += 1
        for k in range(dents):
            a = k * 2 * math.pi / dents; py, pz = cy + math.sin(a) * (r + 0.5), cz + math.cos(a) * (r + 0.5)
            s.b(x0, py - 0.6, pz - 0.6, x1, py + 0.6, pz + 0.6, c)
    def eclat(s, cx, cy, cz, h, c):
        n = int(h * 2)
        for k in range(n):
            t = k / 2; w = 1.2 * (1 - abs(t - h / 2) / (h / 2 + .01))
            if w > 0.2: s.b(cx - w, cy + t, cz - w, cx + w, cy + t + .5, cz + w, c, True)
    def texture(s):
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        for i, c in enumerate(s.couleurs):
            u, v = (i % 4) * 4, (i // 4) * 4
            for x in range(4):
                for y in range(4):
                    n = random.randint(-7, 7) if len(c) == 3 else 0
                    img.putpixel((u + x, v + y), tuple(max(0, min(255, k + n)) for k in c[:3]) + (255,))
        img.save(f'{A}/textures/block/{s.nom}.png')
    def modele(s, tex=None, gui=0.42):
        tex = tex or s.nom
        m = {"parent": "minecraft:block/block", "ambientocclusion": False, "textures": {"t": f"airain:block/{tex}", "particle": f"airain:block/{tex}"},
             "elements": s.el,
             "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, -2, 0], "scale": [gui] * 3},
                         "ground": {"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.2] * 3},
                         "fixed": {"rotation": [0, 0, 0], "translation": [0, -2, 0], "scale": [gui] * 3},
                         "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.2] * 3},
                         "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 0, 0], "scale": [0.2] * 3},
                         "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.2] * 3}}}
        json.dump(m, open(f'{A}/models/block/{s.nom}.json', 'w'), indent=0)
        print(s.nom, len(s.el), 'éléments')

FACINGS = (("north", 0), ("east", 90), ("south", 180), ("west", 270))
def ecrire_borne(m):
    m.texture(); m.modele(gui=0.26)
    json.dump({"parent": f"airain:block/{m.nom}"}, open(f'{A}/models/item/{m.nom}.json', 'w'))
    json.dump({"variants": {f"facing={f}": {"model": f"airain:block/{m.nom}", "y": y} for f, y in FACINGS}}, open(f'{A}/blockstates/{m.nom}.json', 'w'), indent=1)
    json.dump({"type": "minecraft:block", "pools": [{"rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"airain:{m.nom}"}],
               "conditions": [{"condition": "minecraft:survives_explosion"}]}]}, open(f'{M}/data/airain/loot_table/blocks/{m.nom}.json', 'w'), indent=1)

def ecrire_partie(nom, zone, tex):
    json.dump({"textures": {"particle": f"airain:block/{tex}"}, "elements": []}, open(f'{A}/models/block/{nom}_vide.json', 'w'))
    v = {}
    for f, _ in FACINGS:
        for px in range(3):
            for py in range(2):
                for pz in range(4):
                    v[f"facing={f},px={px},py={py},pz={pz}"] = {"model": f"airain:block/{zone if (px, py, pz) == (1, 0, 2) else nom + '_vide'}"}
    json.dump({"variants": v}, open(f'{A}/blockstates/{nom}.json', 'w'))

def ecrire_simple(m, gui=0.42):
    m.texture(); m.modele(gui=gui)
    json.dump({"variants": {"": {"model": f"airain:block/{m.nom}"}}}, open(f'{A}/blockstates/{m.nom}.json', 'w'))

# ======================= Empire
WH, GOLD, GOLD2, RED, IRON, IRON2, BRASS, COPPER, INK, LUM, PAPER = (236,234,224),(232,192,72),(180,135,40),(150,26,32),(80,82,90),(55,56,62),(200,150,60),(190,110,75),(30,26,24),(255,220,120,1),(240,236,220)
E = Modele('borne_imperiale', [WH, GOLD, GOLD2, RED, IRON, IRON2, BRASS, COPPER, INK, LUM])
E.b(1, 0, 3, 15, 2, 13, IRON2)
for (x, z) in ((1, 3), (14, 3), (1, 12), (14, 12)): E.b(x, 2, z, x + 1, 26, z + 1, BRASS)
E.b(1, 26, 3, 15, 28, 13, BRASS)
for c, x in enumerate((4.5, 8, 11.5)):
    E.b(x - 0.5, 2, 7.5, x + 0.5, 26, 8.5, IRON)
    for k in range(6):
        y = 4 + k * 3.5
        E.cyl(x, 8, y, y + 1.6, 2.6, GOLD if (k + c) % 2 else COPPER)
        E.b(x - 0.4, y + 0.3, 5.1, x + 0.4, y + 1.3, 5.5, INK)
E.rouage_yz(14, 8, 15, 16, 3, GOLD2, 8)
E.b(16, 13.5, 7.5, 17, 14.5, 8.5, IRON); E.b(16, 13.5, 8, 17, 18, 9, IRON); E.b(15.5, 17.5, 8, 17.5, 19, 9, RED)
# gauche (ouest) : chaudière, cheminée, manomètre, tuyau
E.cyl(-8, 8, 0, 14, 6, IRON2); E.cyl(-8, 8, 3, 4, 6.4, BRASS); E.cyl(-8, 8, 10, 11, 6.4, BRASS)
E.cyl(-8, 8, 14, 30, 1.6, IRON); E.cyl(-8, 8, 29.5, 31.5, 2.2, BRASS)
E.anneau_xy(-8, 8, 1.4, 2, 0, 2.2, WH); E.anneau_xy(-8, 8, 1.3, 1.9, 1.8, 2.6, GOLD2); E.b(-8.2, 8, 1.2, -7.8, 10, 1.4, RED)
E.b(-2, 9, 7, 1, 11, 9, BRASS)
# droite (est) : lampadaire impérial + étendard
E.b(21, 0, 4, 27, 2, 10, WH); E.b(23, 2, 6, 25, 26, 8, IRON2)
E.b(22, 26.5, 5, 26, 29.5, 9, LUM, True)
for (x, z) in ((21.5, 4.5), (25.5, 4.5), (21.5, 8.5), (25.5, 8.5)): E.b(x, 26, z, x + 1, 30, z + 1, GOLD2)
E.b(21, 30, 4, 27, 31, 10, GOLD); E.b(23.5, 31, 6.5, 24.5, 32, 7.5, GOLD)
E.b(25, 12, 7, 31, 25, 7.6, RED); E.b(25, 12, 6.9, 31, 13, 7.7, GOLD); E.b(25, 24.4, 6.9, 31, 25.4, 7.7, GOLD); E.b(27.5, 16, 6.8, 28.5, 21, 7.8, GOLD)
ecrire_borne(E)

Z = Modele('zone_imperiale', [WH, GOLD, GOLD2, RED, BRASS])
Z.b(-16, 0, -16, 32, 1, 32, WH)
for (a, b_, c_, d) in ((-16, -16, 32, -14), (-16, 30, 32, 32), (-16, -14, -14, 30), (30, -14, 32, 30)): Z.b(a, 1, b_, c_, 1.4, d, RED)
for (a, b_, c_, d) in ((-16, -16, 32, -15), (-16, 31, 32, 32), (-16, -15, -15, 31), (31, -15, 32, 31)): Z.b(a, 1, b_, c_, 1.6, d, GOLD)
Z.anneau_xz(8, 8, 1, 1.4, 9, 11, RED); Z.anneau_xz(8, 8, 1, 1.5, 3, 4.5, GOLD)
Z.b(7, 1, -1, 9, 1.3, 3.5, GOLD); Z.b(7, 1, 12.5, 9, 1.3, 17, GOLD); Z.b(-1, 1, 7, 3.5, 1.3, 9, GOLD); Z.b(12.5, 1, 7, 17, 1.3, 9, GOLD)
for k in range(-14, 30, 3):
    Z.b(k, 1, -13.5, k + 1.5, 2.2, -12, BRASS); Z.b(k, 1, 28, k + 1.5, 2.2, 29.5, BRASS)
for k in range(-11, 28, 3):
    Z.b(-13.5, 1, k, -12, 2.2, k + 1.5, BRASS); Z.b(28, 1, k, 29.5, 2.2, k + 1.5, BRASS)
Z.texture(); Z.modele()

C = Modele('caisse_imperiale', [WH, GOLD, GOLD2, RED])
C.b(1, 0, 1, 15, 14, 15, WH)
for (x, z) in ((1, 1), (14, 1), (1, 14), (14, 14)): C.b(x - 0.2, 0, z - 0.2, x + 1.2, 14, z + 1.2, GOLD)
C.b(0.8, 0, 0.8, 15.2, 1, 15.2, GOLD2); C.b(0.8, 13, 0.8, 15.2, 14.2, 15.2, GOLD2)
C.b(0.9, 6, 0.9, 15.1, 8, 15.1, RED); C.b(7, 14, 7, 9, 14.6, 9, GOLD)
ecrire_simple(C)
P = Modele('parachute', [WH, RED, GOLD2])
P.b(-8, 12, -8, 24, 14, 24, WH); P.b(-4, 14, -4, 20, 16, 20, RED); P.b(0, 16, 0, 16, 17, 16, WH); P.b(4, 17, 4, 12, 17.5, 12, RED)
P.b(-8, 11.5, -8, 24, 12, -7, RED); P.b(-8, 11.5, 23, 24, 12, 24, RED); P.b(-8, 11.5, -7, -7, 12, 23, RED); P.b(23, 11.5, -7, 24, 12, 23, RED)
for (x, z) in ((1, 1), (14.7, 1), (1, 14.7), (14.7, 14.7)): P.b(x, -2, z, x + 0.3, 12, z + 0.3, GOLD2)
ecrire_simple(P)
ecrire_partie('borne_partie_imperiale', 'zone_imperiale', 'borne_imperiale')

# ======================= Écho
NOIR, NOIR2, VIO, LAV, PALE = (24,20,34),(44,36,62),(96,58,156),(186,156,255,1),(232,218,255,1)
O = Modele('borne_arcanique', [NOIR, NOIR2, VIO, LAV, PALE])
O.b(1, 0, 3, 15, 2, 13, NOIR2)
for (x, z) in ((1, 3), (14, 3), (1, 12), (14, 12)): O.b(x, 2, z, x + 1, 26, z + 1, VIO)
O.b(2, 2, 12, 14, 26, 13, NOIR); O.b(1, 26, 3, 15, 28, 13, VIO)
for c, x in enumerate((4.5, 8, 11.5)):
    for k in range(5):
        y = 6 + k * 4
        O.b(x - 1.2, y, 7, x + 1.2, y + 2, 10, PALE if (k + c) % 2 else NOIR2, (k + c) % 2 == 1)
        O.b(x - 0.3, y + 2.6, 8.2, x + 0.3, y + 3.2, 8.8, LAV, True)
O.b(6, 2, 1.5, 10, 4, 3, NOIR)
r = {"angle": -22.5, "axis": "x", "origin": [8, 4.5, 2.5]}
O.b(3, 4, 0.5, 13, 5, 4.5, NOIR2, False, r); O.b(4, 5, 1, 7.8, 5.4, 4, PALE, True, r); O.b(8.2, 5, 1, 12, 5.4, 4, PALE, True, r); O.b(7.8, 5, 1, 8.2, 5.5, 4, VIO, False, r)
for x in (-8, 24):
    O.b(x - 3, 0, 5, x + 3, 2, 11, NOIR); O.b(x - 2, 2, 6, x + 2, 22, 10, NOIR2); O.b(x - 1.5, 22, 6.5, x + 1.5, 25, 9.5, NOIR2)
    O.b(x - 0.5, 6, 5.7, x + 0.5, 18, 6, LAV, True); O.eclat(x, 26.5, 8, 5, LAV)
ecrire_borne(O)

Y = Modele('zone_arcanique', [NOIR, NOIR2, VIO, LAV, PALE])
Y.b(-16, 0, -16, 32, 1, 32, NOIR2)
for (a, b_, c_, d) in ((-16, -16, 32, -15), (-16, 31, 32, 32), (-16, -15, -15, 31), (31, -15, 32, 31)): Y.b(a, 1, b_, c_, 1.4, d, VIO)
Y.anneau_xz(8, 8, 1, 1.3, 16, 17, LAV, True); Y.anneau_xz(8, 8, 1, 1.3, 10, 10.8, LAV, True); Y.anneau_xz(8, 8, 1, 1.3, 3, 3.8, PALE, True)
for k in range(8):
    a = k * math.pi / 4; x, z = 8 + 13.4 * math.cos(a), 8 + 13.4 * math.sin(a); Y.b(x - .6, 1, z - .6, x + .6, 1.3, z + .6, PALE, True)
for (x, z) in ((-13, -13), (29, -13), (-13, 29), (29, 29)):
    Y.b(x - 1.5, 1, z - 1.5, x + 1.5, 2.5, z + 1.5, NOIR); Y.eclat(x, 7, z, 7, LAV); Y.eclat(x, 15.5, z, 2, PALE)
Y.texture(); Y.modele()
K = Modele('caisse_arcanique', [NOIR, NOIR2, VIO, LAV, PALE])
K.b(1, 0, 1, 15, 14, 15, NOIR2)
for (x, z) in ((1, 1), (14, 1), (1, 14), (14, 14)): K.b(x - 0.2, 0, z - 0.2, x + 1.2, 14, z + 1.2, VIO)
K.b(0.8, 0, 0.8, 15.2, 1, 15.2, NOIR); K.b(0.8, 13, 0.8, 15.2, 14.2, 15.2, NOIR)
for (a, b_, c_, d) in ((5, 0.7, 11, 0.9), (5, 15.1, 11, 15.3)): K.b(a, 5, b_, c_, 9, d, LAV, True)
for (a, b_, c_, d) in ((0.7, 5, 0.9, 11), (15.1, 5, 15.3, 11)): K.b(a, 5, b_, c_, 9, d, LAV, True)
K.b(6, 14, 6, 10, 14.5, 10, PALE, True)
ecrire_simple(K)
ecrire_partie('borne_partie_arcanique', 'zone_arcanique', 'borne_arcanique')
