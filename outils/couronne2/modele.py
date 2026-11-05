"""Couronne d'airain : voxels (repère de la maquette) -> boîtes du modèle (repère de la tête), CouronneGeo.java + texture 64x64."""
import math, random
from PIL import Image
LA, LA2, LA3, OR, FER, RUBIS, VERT, VERRE, CU, OR2 = range(10)
V = {}
E, HB = 1, 1          # couronne élargie d'un pixel et bandeau d'un rang de plus : elle se pose sur le casque de netherite
A0, A1 = -1 - E, 9 + E
for x in range(A0, A1 + 1):
    for z in range(A0, A1 + 1):
        if x in (A0, A1) or z in (A0, A1):
            V[(x, 6, z)] = LA2
            for y in range(7, 8 + HB): V[(x, y, z)] = LA3 if (y == 7 + HB and (x + z) % 3 == 0) else LA
        elif x in (A0 + 1, A1 - 1) or z in (A0 + 1, A1 - 1):
            V[(x, 7 + HB, z)] = LA2                    # rebord intérieur posé sur le casque
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
    for y in (4, 5): V[(4, y, zz)] = LA2               # bras du rouage jusqu'au bandeau
LX = A1 + 1
for dy in (-1, 0, 1):
    for dz in (-1, 0, 1):
        V[(LX, 3 + dy, 2 + dz)] = VERRE if (dy, dz) == (0, 0) else OR
V[(LX, 3, 0)] = LA2; V[(LX - 1, 3, -1)] = LA2; V[(LX - 2, 3, -2)] = LA2; V[(LX - 3, 3, -3)] = LA2
# rouage (relatif au moyeu, plan vertical, épaisseur 1) : couronne pleine + 10 dents
G = {}
for dy in range(-4, 5):
    for dx in range(-4, 5):
        r = math.hypot(dy, dx); a = math.atan2(dy, dx)
        if 1.3 <= r <= 3.0: G[(dx, dy)] = OR if r > 2.2 else OR2
        elif 3.0 < r <= 4.2 and (a * 10 / math.pi) % 2 < 1: G[(dx, dy)] = LA2
for (dx, dy) in ((0, 2), (0, -2), (2, 0), (-2, 0)): G[(dx, dy)] = OR2     # rayons

def modele(x, y, z):          # voxel maquette -> coin min dans le repère de la tête (pixels)
    return (z - 4, -y - 1, 4 - x - 1)

boites = []     # (x0,y0,z0,w,h,d,mat)
vu = set()
for (x, y, z), m in sorted(V.items()):
    if (x, y, z) in vu: continue
    # fusion verticale
    h = 1
    while V.get((x, y + h, z)) == m and (x, y + h, z) not in vu: h += 1
    for k in range(h): vu.add((x, y + k, z))
    mx, my, mz = modele(x, y + h - 1, z)
    boites.append((mx - 0.5, my, mz - 0.5, 1, h, 1, m))
rouage = []
for (dx, dy), m in G.items():
    if (dx, dy) == (0, 0): continue
    rouage.append((dy, dx, m))   # dans le plan y/z du modèle : (dz=dx maquette -> z, dy)
print(len(boites), "boîtes,", len(rouage), "dents/pixels de rouage")
J = ["package fr.chatmort.airain.gardien;", "", "/** Généré par couronne2/modele.py : boîtes de la couronne d'airain (pixels, repère de la tête). */",
     "final class CouronneGeo {", "\tprivate CouronneGeo() {}",
     "\t/** x, y, z, largeur, hauteur, profondeur, matière */",
     "\tstatic final float[][] FIXE = {"]
J += ["\t\t{%sf, %sf, %sf, %d, %d, %d, %d}," % b for b in boites]
J += ["\t};", "\t/** rouage : y, z relatifs au moyeu, matière */", "\tstatic final int[][] ROUAGE = {"]
J += ["\t\t{%d, %d, %d}," % (-dy, -dz, m) for (dy, dz, m) in rouage]
J += ["\t};", "\t/** moyeu des rouages (pixels) : centre en y et z ; x = ±(5.5 + 0.5) */",
      "\tstatic final float MOYEU_Y = -3.5f, MOYEU_Z = -1f, MOYEU_X = %sf;" % (6 + E), "}"]
open("/home/claude/airain-mod-create-integration/src/main/java/fr/chatmort/airain/gardien/CouronneGeo.java", "w").write("\n".join(J) + "\n")

# texture : une zone 32 x 12 par matière
PAL = {LA: [(160, 104, 34), (176, 120, 44), (190, 134, 52)], LA2: [(112, 70, 24), (124, 80, 28), (100, 62, 20)],
       LA3: [(226, 186, 98), (240, 206, 122), (214, 170, 84)], OR: [(214, 160, 48), (228, 178, 64), (200, 146, 40)],
       OR2: [(150, 104, 30), (166, 116, 36)], FER: [(64, 66, 72), (78, 80, 86)], RUBIS: [(176, 24, 32), (210, 50, 52), (140, 16, 24)],
       VERT: [(48, 140, 120), (66, 164, 140)], VERRE: [(150, 205, 220), (190, 230, 240)], CU: [(184, 104, 70), (200, 120, 80)]}
R = random.Random(3)
im = Image.new("RGBA", (128, 64))
for m, pal in PAL.items():
    ox, oy = (m % 2) * 32, (m // 2) * 12
    for x in range(32):
        for y in range(12):
            c = R.choice(pal)
            if m in (LA, LA2, LA3, OR) and (x + y * 3) % 7 == 0: c = tuple(min(255, v + 22) for v in c)   # reflets
            im.putpixel((ox + x, oy + y), c + (255,))
# casque de netherite (UV de tête vanilla en 64,0) : faces pleines, visière ouverte avec nasal et joues
NE = [(49, 41, 42), (68, 58, 63), (77, 73, 76), (60, 52, 56)]
NH = [(92, 84, 88), (110, 100, 104)]
def face(ox, oy, avant=False, dessus=False):
    for x in range(8):
        for y in range(8):
            c = R.choice(NE)
            if y == 0 and not dessus or x in (0, 7) and R.random() < .4: c = R.choice(NH)
            if avant and 3 <= y <= 6 and 2 <= x <= 5 and not (x in (3, 4) and y <= 5): continue   # yeux, bouche
            if avant and y == 7 and 2 <= x <= 5: continue
            im.putpixel((ox + x, oy + y), c + (255,))
face(64 + 8, 0, dessus=True); face(64 + 16, 0, dessus=True)
face(64 + 0, 8); face(64 + 8, 8, avant=True); face(64 + 16, 8); face(64 + 24, 8)
im.save("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/models/armor/couronne_layer_1.png")
