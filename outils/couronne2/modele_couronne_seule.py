"""Couronne d'airain : voxels (repère de la maquette) -> boîtes du modèle (repère de la tête), CouronneGeo.java + texture 64x64."""
import math, random
from PIL import Image
LA, LA2, LA3, OR, FER, RUBIS, VERT, VERRE, CU, OR2 = range(10)
V = {}
# bandeau : 3 rangs autour de la tête (maquette : x avant/arrière 0..8 face en +x, z côtés, y bas->haut)
for x in range(-1, 10):
    for z in range(-1, 10):
        if x in (-1, 9) or z in (-1, 9):
            V[(x, 5, z)] = LA2; V[(x, 6, z)] = LA; V[(x, 7, z)] = LA3 if (x + z) % 3 == 0 else LA
def pointe(x, z, h, top=LA3):
    for k in range(h): V[(x, 8 + k, z)] = LA if k < h - 1 else top
for i in range(-1, 10):
    for (x, z) in ((i, -1), (i, 9), (-1, i), (9, i)):
        if i in (-1, 9): pointe(x, z, 3)
        elif i in (3, 5): pointe(x, z, 2, LA)
        elif i == 4: pointe(x, z, 5)
        elif i in (1, 7): pointe(x, z, 1)
V[(10, 9, 4)] = RUBIS; V[(10, 10, 4)] = RUBIS
for (x, z) in ((4, -2), (4, 10), (-2, 4)): V[(x, 9, z)] = VERT
# moyeux des rouages (fixes) et bras de la loupe
for zz, s in ((-2, -1), (10, 1)):
    V[(4, 3, zz)] = FER; V[(4, 3, zz + s)] = LA3
    for y in (4, 5): V[(4, y, zz - s)] = LA2           # attache au bandeau
for dy in (-1, 0, 1):
    for dz in (-1, 0, 1):
        V[(9, 3 + dy, 2 + dz)] = VERRE if (dy, dz) == (0, 0) else OR
V[(9, 3, 0)] = LA2; V[(8, 3, -1)] = LA2; V[(7, 3, -2)] = LA2
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
      "\tstatic final float MOYEU_Y = -3.5f, MOYEU_Z = -1f, MOYEU_X = 6f;", "}"]
open("/home/claude/airain-mod-create-integration/src/main/java/fr/chatmort/airain/gardien/CouronneGeo.java", "w").write("\n".join(J) + "\n")

# texture : une zone 32 x 12 par matière
PAL = {LA: [(160, 104, 34), (176, 120, 44), (190, 134, 52)], LA2: [(112, 70, 24), (124, 80, 28), (100, 62, 20)],
       LA3: [(226, 186, 98), (240, 206, 122), (214, 170, 84)], OR: [(214, 160, 48), (228, 178, 64), (200, 146, 40)],
       OR2: [(150, 104, 30), (166, 116, 36)], FER: [(64, 66, 72), (78, 80, 86)], RUBIS: [(176, 24, 32), (210, 50, 52), (140, 16, 24)],
       VERT: [(48, 140, 120), (66, 164, 140)], VERRE: [(150, 205, 220), (190, 230, 240)], CU: [(184, 104, 70), (200, 120, 80)]}
R = random.Random(3)
im = Image.new("RGBA", (64, 64))
for m, pal in PAL.items():
    ox, oy = (m % 2) * 32, (m // 2) * 12
    for x in range(32):
        for y in range(12):
            c = R.choice(pal)
            if m in (LA, LA2, LA3, OR) and (x + y * 3) % 7 == 0: c = tuple(min(255, v + 22) for v in c)   # reflets
            im.putpixel((ox + x, oy + y), c + (255,))
im.save("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/models/armor/couronne_layer_1.png")
