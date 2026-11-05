"""Géométrie de la tour de défense (balise v7) : boîtes en pixels dans un volume 48 x 128 x 48 (3 x 8 x 3 blocs),
la bâtisse au centre ; écrit BaliseGeo.java (boîtes du rendu, formes de collision par case) et l'atlas de textures."""
import math, random, json
from PIL import Image
c = 24
FONTE, FER, LAITON, CUIVRE, TUF, VERRE, LAMPE, CADRAN, PORTE, OXYDE, TUF2, LAITON_S = range(12)
B = []          # boîtes fixes : (x0,y0,z0,x1,y1,z1,mat)
LAMPES = []     # s'allument en alerte (hublots, cœur du phare)
VITRES = []     # translucides
SIRENE = []     # tournent autour de l'axe en alerte (coordonnées relatives à l'axe)
def b(x0, y0, z0, x1, y1, z1, m, liste=None): (B if liste is None else liste).append((x0, y0, z0, x1, y1, z1, m))
def octo(r, y0, y1, m, liste=None):
    k = r * 0.4142
    b(c - r, y0, c - k, c + r, y1, c + k, m, liste); b(c - k, y0, c - r, c + k, y1, c + r, m, liste)
    d = r * 0.7071 * 0.98
    b(c - d, y0, c - d, c + d, y1, c + d, m, liste)
# socle
b(0, 0, 0, 48, 3, 48, TUF2); b(2, 3, 2, 46, 6, 46, TUF)
for (x, z) in ((3, 3), (44, 3), (3, 44), (44, 44)): b(x, 6, z, x + 1, 7, z + 1, LAITON)
# salle des machines
octo(10, 6, 36, FONTE)
for y in (8, 20, 34): octo(10.6, y, y + 1.5, LAITON)
b(c - 3.5, 6, c - 10.6, c + 3.5, 17.5, c - 9.6, LAITON_S); b(c - 2.5, 6, c - 11, c + 2.5, 16.5, c - 10, PORTE)
b(c + 1, 10.5, c - 11.5, c + 2, 12, c - 11, LAITON)
b(c - 2, 23.5, c - 11, c + 2, 27.5, c - 10, CADRAN)
b(c + 10, 11, c - 2.5, c + 12, 18, c + 2.5, LAITON_S); b(c + 12, 14, c - 0.5, c + 13.5, 15, c + 0.5, LAITON)
b(c + 13.5, 12, c - 0.5, c + 14.5, 17, c + 0.5, LAITON)
for (dx, dz) in ((-10, 0), (0, 10)): pass
# galerie de la sirène
octo(14, 36, 38, LAITON_S)
for k in range(20):
    a = k * math.pi / 10; r = 13.2
    x, z = c + math.cos(a) * r, c + math.sin(a) * r
    b(x - .5, 38, z - .5, x + .5, 41, z + .5, LAITON)
# colonne
octo(7, 38, 84, FONTE)
for y in (50, 62, 74): octo(7.6, y, y + 1.5, CUIVRE)
for y in (55, 67): b(c - 1.2, y, c - 7.4, c + 1.2, y + 3, c - 6.9, LAMPE, LAMPES)
b(c - 2, 41, c - 2, c + 2, 47, c + 2, LAITON_S)             # moyeu de la sirène (fixe)
# la sirène : deux pavillons en tronc de cône, axe horizontal x, centrés sur y = 44 (relatif à l'axe : x, y, z autour de 0)
for s in (1, -1):
    for t in range(14):
        rr = 1.6 + t * 0.36
        x0 = 7 + t
        b(*(sorted((s * x0, s * (x0 + 1)))[0], 44 - rr, -rr), *(sorted((s * x0, s * (x0 + 1)))[1], 44 + rr, rr), LAITON if t < 13 else LAITON_S, liste=SIRENE)
    x0 = 20
    b(*(sorted((s * 20.6, s * 20.9))[0], 44 - 5.4, -5.4), *(sorted((s * 20.6, s * 20.9))[1], 44 + 5.4, 5.4), FONTE, liste=SIRENE)
# le phare
octo(12, 84, 86, LAITON_S)
for k in range(20):
    a = k * math.pi / 10; r = 11.3
    x, z = c + math.cos(a) * r, c + math.sin(a) * r
    b(x - .5, 86, z - .5, x + .5, 89, z + .5, LAITON)
octo(7, 86, 102, VERRE, VITRES)
octo(4.2, 88, 100, LAMPE, LAMPES)
for k in range(8):
    a = k * math.pi / 4 + math.pi / 8; r = 7.05
    x, z = c + math.cos(a) * r, c + math.sin(a) * r
    b(x - .6, 86, z - .6, x + .6, 102, z + .6, LAITON)
octo(8.6, 102, 104, CUIVRE); octo(7, 104, 107, CUIVRE); octo(4.6, 107, 110, CUIVRE); octo(2.2, 110, 112, OXYDE)
b(c - 1, 112, c - 1, c + 1, 121, c + 1, LAITON)
for k in range(8):
    a = k * math.pi / 4; x, z = c + math.cos(a) * 2.6, c + math.sin(a) * 2.6
    b(x - .7, 115.5, z - .7, x + .7, 117.5, z + .7, LAITON)
octo(2, 115.5, 117.5, LAITON)
# jambes : quatre poutres inclinées (rendu à part) ; ici leur trajet en marches pour la collision
JAMBES = [(4, 6, 4), (c - 8.5, 36, c - 8.5)]
def jambe_cases():
    out = []
    for sx in (1, -1):
        for sz in (1, -1):
            for i in range(6):
                t0, t1 = i / 6, (i + 1) / 6
                p = lambda t: (4 + (c - 8.5 - 4) * t, 6 + 30 * t)
                (d0, y0), (d1, y1) = p(t0), p(t1)
                x = c + sx * (c - d0) if False else (d0 if sx > 0 else 48 - d0)
                z = d0 if sz > 0 else 48 - d0
                x1 = d1 if sx > 0 else 48 - d1; z1 = d1 if sz > 0 else 48 - d1
                out.append((min(x, x1) - 1.5, y0, min(z, z1) - 1.5, max(x, x1) + 1.5, y1, max(z, z1) + 1.5))
    return out
# formes de collision : silhouettes simplifiées, découpées par case
FORMES = [(0, 0, 0, 48, 6, 48), (c - 10, 6, c - 10, c + 10, 36, c + 10), (c - 14, 36, c - 14, c + 14, 38, c + 14),
          (c - 7, 38, c - 7, c + 7, 84, c + 7), (c - 12, 84, c - 12, c + 12, 86, c + 12), (c - 7, 86, c - 7, c + 7, 104, c + 7),
          (c - 4.6, 104, c - 4.6, c + 4.6, 112, c + 4.6), (c - 1, 112, c - 1, c + 1, 121, c + 1)] + jambe_cases()
cases = {}
for (x0, y0, z0, x1, y1, z1) in FORMES:
    for cx in range(3):
        for cy in range(8):
            for cz in range(3):
                a = (max(x0, cx * 16), max(y0, cy * 16), max(z0, cz * 16)); bb = (min(x1, cx * 16 + 16), min(y1, cy * 16 + 16), min(z1, cz * 16 + 16))
                if a[0] < bb[0] - 0.01 and a[1] < bb[1] - 0.01 and a[2] < bb[2] - 0.01:
                    cases.setdefault((cx, cy, cz), []).append(tuple(round(v - o, 2) for v, o in zip(a + bb, (cx * 16, cy * 16, cz * 16) * 2)))
print(len(B), "boîtes,", len(cases), "cases occupées")
f = lambda v: ("%.2ff" % v).replace(".00f", "f")
J = ["package fr.chatmort.airain.balise;", "", "/** Généré par balise7/geo.py : boîtes de la tour (pixels, volume 48 x 128 x 48) et formes de collision. */",
     "final class BaliseGeo {", "\tprivate BaliseGeo() {}"]
def tab(nom, L):
    J.append("\tstatic final float[][] %s = {" % nom)
    for t in L: J.append("\t\t{" + ", ".join(f(v) for v in t) + "},")
    J.append("\t};")
tab("FIXES", B); tab("LAMPES", LAMPES); tab("VITRES", VITRES); tab("SIRENE", SIRENE)
J.append("\t/** Cases occupées : {x, y, z, puis des boîtes de 6 valeurs en pixels dans la case}. */")
J.append("\tstatic final float[][] CASES = {")
for (k, L) in sorted(cases.items()):
    J.append("\t\t{" + ", ".join(str(v) + "f" for v in k) + ", " + ", ".join(f(v) for bx in L for v in bx) + "},")
J.append("\t};"); J.append("}")
open("/home/claude/airain-mod-create-integration/src/main/java/fr/chatmort/airain/balise/BaliseGeo.java", "w").write("\n".join(J) + "\n")
json.dump({"B": B, "L": LAMPES, "V": VITRES, "S": SIRENE, "cases": [list(k) for k in cases]}, open("geo.json", "w"))
print(sorted(cases))
