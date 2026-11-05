"""Géométrie des modules de gardien -> ModulesGeo.java + textures (niveau 1 laiton, niveau 2 netherite)."""
import math, random
from PIL import Image
MOD = '/home/claude/airain-mod-create-integration/src/main'
# matières : couleur niveau 1, couleur niveau 2, lumineuse
MAT = [((150,108,40),(46,40,50),0), ((205,160,70),(76,66,80),0), ((240,205,120),(255,214,110),0), ((70,72,78),(40,36,44),0),
       ((48,50,56),(26,22,28),0), ((190,110,75),(92,80,96),0), ((150,80,50),(58,50,62),0), ((176,120,70),(70,60,74),0),
       ((196,140,80),(104,92,110),0), ((100,102,112),(76,66,80),0), ((78,80,88),(58,50,62),0), ((120,122,128),(210,170,90),0),
       ((220,60,40),(220,60,40),0), ((150,200,215),(150,200,215),0), ((210,240,250),(210,240,250),0),
       ((255,196,90),(255,196,90),1), ((255,170,60),(255,170,60),1), ((255,120,50),(255,120,50),1), ((140,230,255),(140,230,255),1)]
LUM = {i for i, m in enumerate(MAT) if m[2]}
P = {}
def b(part, x, y, z, w, h, d, m):
    P.setdefault(part + ('_lum' if m in LUM else ''), []).append((x, y, z, w, h, d, m))
def cyl(part, axe, c1, c2, r, a0, a1, m, pas=0.5):
    """Cylindre en tranches : axe 'y' (c1=x, c2=z), 'z' (c1=x, c2=y)."""
    n = int(round(2 * r / pas))
    for i in range(n):
        u0 = -r + i * pas; uc = u0 + pas / 2
        hw = math.sqrt(max(0, r * r - uc * uc))
        if hw < 0.15: continue
        if axe == 'y': b(part, c1 + u0, a0, c2 - hw, pas, a1 - a0, 2 * hw, m)
        else: b(part, c1 + u0, c2 - hw, a0, pas, 2 * hw, a1 - a0, m)

# ---------------- tête-lanterne (repère de la tête : boîte -4..4, -12..-2, -5.5..2.5)
T = 'lanterne'
b(T, -4.25, -12, -5.5, 0.2, 10, 8, 15); b(T, 4.05, -12, -5.5, 0.2, 10, 8, 15)
b(T, -4, -12, 2.55, 8, 10, 0.2, 16);   b(T, -4, -12.25, -5.5, 8, 0.2, 8, 15)
for x in (-4.5, 3.7):
    for z in (-5.9, 2.3): b(T, x, -12.5, z, 0.8, 10.8, 0.8, 0)
for y, m in ((-12.5, 1), (-2.5, 0)):
    for z in (-5.9, 2.3): b(T, -4.5, y, z, 9, 0.8, 0.8, m)
    for x in (-4.5, 3.7): b(T, x, y, -5.9, 0.8, 0.8, 9, m)
for x in (-4.45, 4.15):
    b(T, x, -12, -1.75, 0.3, 10, 0.5, 1); b(T, x, -7.25, -5.5, 0.3, 0.5, 8, 1)
b(T, -0.25, -12, 2.6, 0.5, 10, 0.3, 1); b(T, -4, -7.25, 2.6, 8, 0.5, 0.3, 1)
b(T, -0.25, -12.45, -5.5, 0.5, 0.3, 8, 1); b(T, -4, -12.45, -1.75, 8, 0.3, 0.5, 1)
b(T, -2, -13.6, -3.5, 4, 1.1, 4, 1); b(T, -1, -14.4, -2.5, 2, 0.8, 2, 2)
b(T, -3, -7, -5.56, 2, 2, 0.05, 17); b(T, 1, -7, -5.56, 2, 2, 0.05, 17)          # yeux

# ---------------- longue-vue (tête) : lunette réglable sur l'œil droit
T = 'lunette'
b(T, -4.6, -9.6, -5.9, 9.2, 0.8, 0.4, 0); b(T, -4.6, -9.6, 2.5, 9.2, 0.8, 0.4, 0)   # sangle
b(T, -4.6, -9.6, -5.5, 0.4, 0.8, 8, 0);  b(T, 4.2, -9.6, -5.5, 0.4, 0.8, 8, 0)
b(T, -4.5, -9.2, -6.6, 0.5, 3.4, 0.6, 2)                                            # bras du pivot
cyl(T, 'z', -2, -6, 2.0, -8.4, -5.6, 1)
cyl(T, 'z', -2, -6, 2.3, -7.9, -7.4, 2)                                             # bague moletée
cyl(T, 'z', -2, -6, 1.4, -10.4, -8.4, 0)
cyl(T, 'z', -2, -6, 1.6, -10.6, -10.3, 2)
cyl(T, 'z', -2, -6, 1.0, -10.65, -10.55, 13, pas=0.5)

# ---------------- canon d'épaule (corps : boîte -9..9, -2..10, -6..5 ; bras droit -13..-9)
T = 'canon'
b(T, -13.6, -4.6, -3.6, 5.2, 1.4, 7.2, 3); b(T, -12.5, -6.6, -1.5, 3, 2, 2.6, 0)
F = 'canon_fut'
for k in range(8):
    z0 = -9 + k * 1.5
    cyl(F, 'z', -11, -7.8, 1.6, z0, z0 + 1.5, 7 if k % 2 else 8)
cyl(F, 'z', -11, -7.8, 2.0, -9.6, -8.1, 2); cyl(F, 'z', -11, -7.8, 0.9, -9.7, -9.6, 4)
cyl(F, 'z', -11, -7.8, 2.1, 3, 4.4, 0); cyl(F, 'z', -11, -7.8, 0.8, 4.4, 5.4, 2)

# ---------------- bobine Tesla (corps, entre les épaules)
T = 'tesla'
b(T, -3, -3, 4, 6, 1.5, 3, 3)
for k in range(9): cyl(T, 'y', 0, 6.5, 1.6, -12 + k, -11 + k, 5 if k % 2 else 6)
cyl(T, 'y', 0, 6.5, 2.6, -14.5, -12, 1); cyl(T, 'y', 0, 6.5, 1.2, -15.5, -14.5, 2)
E = 'tesla_eclairs'
for (x, y, z) in ((1.6, -15.6, 6.8), (2.4, -16.3, 7.1), (3.0, -17.1, 7.6), (3.9, -17.6, 7.4), (-1.5, -15.4, 6.2), (-2.4, -16.0, 5.8),
                  (-3.1, -16.9, 5.6), (-3.6, -17.8, 6.0), (0.3, -16.2, 8.3), (0.8, -17.1, 9.0), (0.4, -18.0, 9.7)):
    b(E, x, y, z, 0.5, 0.5, 0.5, 18)

# ---------------- blindage riveté (corps + bras)
T = 'blindage'
b(T, -7, -1, -7, 14, 0.6, 1, 0); b(T, -7, 5.4, -7, 14, 0.6, 1, 0)
b(T, -7, -1, -7, 0.6, 7, 1, 0); b(T, 6.4, -1, -7, 0.6, 7, 1, 0)
for k in range(5): b(T, -6.4, -0.4 + k * 1.16, -6.9, 12.8, 1.16, 0.9, 9 if k % 2 else 10)
for x in (-6.75, -3.3, -0.25, 2.8, 6.25):
    for y in (-0.95, 5.45): b(T, x, y, -7.2, 0.5, 0.5, 0.25, 11)
b(T, -5, 6, -6.8, 10, 2.5, 0.8, 10); b(T, -5, 6, -6.9, 10, 0.5, 0.9, 0)
for c, x0 in (('brasD', -13.6), ('brasG', 8.4)):
    P_ = 'blindage_' + c
    b(P_, x0, -3.2, -3.6, 5.2, 2.2, 7.2, 1); b(P_, x0 - 0.1, -3.3, -0.4, 5.4, 2.4, 0.8, 2)
    xb = x0 + 0.2
    b(P_, xb, 12, -3.4, 4.8, 6, 6.8, 9)
    b(P_, xb - 0.1, 12, -3.5, 5, 0.6, 7, 0); b(P_, xb - 0.1, 17.4, -3.5, 5, 0.6, 7, 0)
    for z in (-2.2, 1.7): b(P_, xb + 1.9, 14.6, z - 1.35, 0.5, 0.5, 0.2, 11) if False else None

# ---------------- chaudière de secours (corps, dans le dos)
T = 'chaudiere'
for (y0, y1, m) in ((-1, -0.4, 0), (-0.4, 3.5, 5), (3.5, 4.1, 0), (4.1, 8.4, 5), (8.4, 9, 0)): cyl(T, 'y', 0, 9.3, 3.5, y0, y1, m)
cyl(T, 'y', 0, 9.3, 3.6, -1.6, -1, 1)
cyl(T, 'y', 2, 9.8, 0.9, -7, -1.6, 4); cyl(T, 'y', 2, 9.8, 1.2, -7.6, -7, 3)
b(T, -5.5, -1, 5, 1, 1, 4.5, 2); b(T, 4.5, -1, 5, 1, 1, 4.5, 2)
b(T, -1, 3, 12.75, 2, 2, 0.4, 12); b(T, -1.3, 2.7, 12.7, 2.6, 2.6, 0.3, 2)
b(T, 2.2, 0.8, 12.6, 1.6, 1.6, 0.4, 2)

# ---------------- Java
L = ['package fr.chatmort.airain.gardien;', '', 'import java.util.Map;', '',
     '/** Généré par modules/geo_modules.py : boîtes des modules de gardien (pixels, repère de la partie porteuse). */',
     'final class ModulesGeo {', '\tprivate ModulesGeo() {}', '\t/** Matières lumineuses (rendues en pleine lumière). */',
     '\tstatic final int[] LUMINEUSES = {' + ', '.join(map(str, sorted(LUM))) + '};', '\t/** x, y, z, largeur, hauteur, profondeur, matière */',
     '\tstatic final Map<String, float[][]> PARTIES = Map.ofEntries(']
ent = []
f = lambda v: ('%g' % round(v, 3)) + 'f'
for k, bx in sorted(P.items()):
    ent.append('\t\tMap.entry("%s", new float[][] {\n%s})' % (k, ',\n'.join('\t\t\t{' + ', '.join(f(v) for v in q[:6]) + ', %d}' % q[6] for q in bx)))
L.append(',\n'.join(ent)); L.append('\t);'); L.append('}')
open(MOD + '/java/fr/chatmort/airain/gardien/ModulesGeo.java', 'w').write('\n'.join(L) + '\n')
print({k: len(v) for k, v in P.items()})
# ---------------- textures 256x256, tuiles de 32x32
for niv in (1, 2):
    im = Image.new('RGBA', (256, 256), (0, 0, 0, 0)); rnd = random.Random(7)
    for i, m in enumerate(MAT):
        c = m[niv - 1]; u, v = (i % 8) * 32, (i // 8) * 32
        for x in range(32):
            for y in range(32):
                n = rnd.randint(-7, 7) if not m[2] else rnd.randint(-4, 4)
                im.putpixel((u + x, v + y), tuple(max(0, min(255, q + n)) for q in c) + (255,))
    im.save(MOD + '/resources/assets/airain/textures/entity/gardien_modules%s.png' % ('' if niv == 1 else '_2'))
