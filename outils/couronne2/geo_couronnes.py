"""Couronne d'airain (seule, laiton) et casque couronné (netherite, couronne noircie) :
écrit CouronneGeo.java et les deux textures d'armure (128 x 64)."""
import math, random
from PIL import Image
LA, LA2, LA3, OR, FER, RUBIS, VERT, VERRE, CU, OR2 = range(10)
MOD = "/home/claude/airain-mod-create-integration/src/main/"

def voxels(E, HB, bas):
    V = {}
    A0, A1 = -1 - E, 9 + E
    for x in range(A0, A1 + 1):
        for z in range(A0, A1 + 1):
            if x in (A0, A1) or z in (A0, A1):
                V[(x, bas, z)] = LA2
                for y in range(bas + 1, 8 + HB): V[(x, y, z)] = LA3 if (y == 7 + HB and (x + z) % 3 == 0) else LA
            elif E and (x in (A0 + 1, A1 - 1) or z in (A0 + 1, A1 - 1)):
                V[(x, 7 + HB, z)] = LA2
    B0 = 8 + HB
    def pointe(x, z, h, top=LA3):
        for k in range(h): V[(x, B0 + k, z)] = LA if k < h - 1 else top
    M = (A0 + A1) // 2
    for i in range(A0, A1 + 1):
        for (x, z) in ((i, A0), (i, A1), (A0, i), (A1, i)):
            if i in (A0, A1): pointe(x, z, 3)
            elif i in (M - 1, M + 1): pointe(x, z, 2, LA)
            elif i == M: pointe(x, z, 5)
            elif i in (A0 + 2, A1 - 2): pointe(x, z, 1)
    V[(A1 + 1, B0 + 1, M)] = RUBIS; V[(A1 + 1, B0 + 2, M)] = RUBIS
    for (x, z) in ((M, A0 - 1), (M, A1 + 1), (A0 - 1, M)): V[(x, B0 + 1, z)] = VERT
    for zz, s in ((A0 - 1, -1), (A1 + 1, 1)):
        V[(4, 3, zz)] = FER; V[(4, 3, zz + s)] = LA3
        for y in range(4, bas): V[(4, y, zz)] = LA2
    LX = A1 + 1
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            V[(LX, 3 + dy, 2 + dz)] = VERRE if (dy, dz) == (0, 0) else OR
    for k in range(E + 3): V[(LX - k, 3, -k)] = LA2
    return V

def boites(V):
    out, vu = [], set()
    for (x, y, z), m in sorted(V.items()):
        if (x, y, z) in vu: continue
        h = 1
        while V.get((x, y + h, z)) == m and (x, y + h, z) not in vu: h += 1
        for k in range(h): vu.add((x, y + k, z))
        out.append((z - 4 - 0.5, -(y + h - 1) - 1, 4 - x - 1 - 0.5, 1, h, 1, m))
    return out

G = {}
for dy in range(-4, 5):
    for dx in range(-4, 5):
        r = math.hypot(dy, dx); a = math.atan2(dy, dx)
        if 1.3 <= r <= 3.0: G[(dx, dy)] = OR if r > 2.2 else OR2
        elif 3.0 < r <= 4.2 and (a * 10 / math.pi) % 2 < 1: G[(dx, dy)] = LA2
for (dx, dy) in ((0, 2), (0, -2), (2, 0), (-2, 0)): G[(dx, dy)] = OR2
G.pop((0, 0), None)

seule = boites(voxels(0, 0, 5)); casque = boites(voxels(1, 1, 6))
J = ["package fr.chatmort.airain.gardien;", "",
     "/** Généré par couronne2/geo_couronnes.py : boîtes de la couronne (pixels, repère de la tête). */",
     "final class CouronneGeo {", "\tprivate CouronneGeo() {}", "\t/** x, y, z, largeur, hauteur, profondeur, matière */"]
for nom, bx in (("SEULE", seule), ("CASQUE", casque)):
    J.append("\tstatic final float[][] %s = {" % nom)
    J += ["\t\t{%sf, %sf, %sf, %d, %d, %d, %d}," % b for b in bx]
    J.append("\t};")
J += ["\t/** rouage : y, z relatifs au moyeu, matière */", "\tstatic final int[][] ROUAGE = {"]
J += ["\t\t{%d, %d, %d}," % (-dy, -dx, m) for (dx, dy), m in G.items()]
J += ["\t};", "\tstatic final float MOYEU_Y = -3.5f, MOYEU_Z = -1f, MOYEU_X_SEULE = 6f, MOYEU_X_CASQUE = 7f;", "}"]
open(MOD + "java/fr/chatmort/airain/gardien/CouronneGeo.java", "w").write("\n".join(J) + "\n")
print(len(seule), len(casque), len(G))

LAITON = {LA: [(160, 104, 34), (176, 120, 44), (190, 134, 52)], LA2: [(112, 70, 24), (124, 80, 28), (100, 62, 20)],
          LA3: [(226, 186, 98), (240, 206, 122), (214, 170, 84)], OR: [(214, 160, 48), (228, 178, 64), (200, 146, 40)],
          OR2: [(150, 104, 30), (166, 116, 36)], FER: [(64, 66, 72), (78, 80, 86)], RUBIS: [(176, 24, 32), (210, 50, 52), (140, 16, 24)],
          VERT: [(48, 140, 120), (66, 164, 140)], VERRE: [(150, 205, 220), (190, 230, 240)], CU: [(184, 104, 70), (200, 120, 80)]}
NOIR = dict(LAITON)
NOIR.update({LA: [(71, 62, 63), (77, 73, 77), (66, 58, 60)], LA2: [(36, 31, 32), (44, 38, 40), (53, 45, 45)],
             LA3: [(93, 86, 93), (118, 106, 118), (100, 92, 100)], OR: [(77, 73, 77), (93, 86, 93), (71, 62, 63)],
             OR2: [(53, 45, 45), (60, 52, 56)], FER: [(23, 17, 17), (36, 31, 32)]})
def texture(pal, casque_, fichier):
    R = random.Random(3)
    im = Image.new("RGBA", (128, 64))
    for m, p in pal.items():
        ox, oy = (m % 2) * 32, (m // 2) * 12
        for x in range(32):
            for y in range(12):
                c = R.choice(p)
                if m in (LA, LA2, LA3, OR) and (x + y * 3) % 7 == 0: c = tuple(min(255, v + 22) for v in c)
                im.putpixel((ox + x, oy + y), c + (255,))
    if casque_:
        NE = [(49, 41, 42), (68, 58, 63), (77, 73, 76), (60, 52, 56)]; NH = [(92, 84, 88), (110, 100, 104)]
        def face(ox, oy, avant=False, dessus=False):
            for x in range(8):
                for y in range(8):
                    c = R.choice(NE)
                    if (y == 0 and not dessus) or (x in (0, 7) and R.random() < .4): c = R.choice(NH)
                    if avant and 3 <= y <= 6 and 2 <= x <= 5 and not (x in (3, 4) and y <= 5): continue
                    if avant and y == 7 and 2 <= x <= 5: continue
                    im.putpixel((ox + x, oy + y), c + (255,))
        face(72, 0, dessus=True); face(80, 0, dessus=True)
        face(64, 8); face(72, 8, avant=True); face(80, 8); face(88, 8)
    im.save(MOD + "resources/assets/airain/textures/models/armor/" + fichier)
texture(LAITON, False, "couronne_layer_1.png")
texture(NOIR, True, "casque_couronne_layer_1.png")
