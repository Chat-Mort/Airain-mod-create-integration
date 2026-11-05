"""Textures (sacrée : armure classique ; impériale : modèle sur mesure) + icônes + géométrie impériale (ImperialeGeo.java)."""
import random
from PIL import Image
MOD = '/home/claude/airain-mod-create-integration/src/main'
TEX = MOD + '/resources/assets/airain/textures/'
N1, N2, N3 = (34,28,38), (52,45,56), (76,66,80)
O1, O2, O3 = (176,138,58), (226,186,96), (255,220,130)
B1, B2, B3 = (200,204,218), (228,231,240), (250,251,255)
ET, ET2 = (235,248,255), (170,220,255)
CAPE1, CAPE2 = (128,26,32), (96,18,24)
rnd = random.Random(5)
def bruit(c, k=4): return tuple(max(0, min(255, v + rnd.randint(-k, k))) for v in c) + (255,)

def boite_uv(im, u, v, w, h, d, f):
    """Peint une boîte au format UV de Minecraft. f(face, x, y, w, h) -> couleur ou None (transparent).
    Faces : 'dessus', 'dessous', 'droite' (côté x-), 'avant' (z-), 'gauche' (x+), 'arriere' (z+)."""
    zones = {'dessus': (u+d, v, w, d), 'dessous': (u+d+w, v, w, d), 'droite': (u, v+d, d, h),
             'avant': (u+d, v+d, w, h), 'gauche': (u+d+w, v+d, d, h), 'arriere': (u+2*d+w, v+d, w, h)}
    for face, (x0, y0, fw, fh) in zones.items():
        for x in range(fw):
            for y in range(fh):
                c = f(face, x, y, fw, fh)
                if c is not None: im.putpixel((x0 + x, y0 + y), bruit(c) if len(c) == 3 else c)

def nacre(x, y): return B3 if (x - y) % 9 in (0, 1) else ((236,238,246) if (x + y) % 11 == 0 else B2)
def noir(x, y): return N2 if (x * 3 + y) % 5 else N3

# ======================================================================= ARMURE SACRÉE (64x32, deux couches)
def sacree():
    l1 = Image.new('RGBA', (64, 32), (0,0,0,0)); l2 = Image.new('RGBA', (64, 32), (0,0,0,0))
    def corps(face, x, y, w, h):
        if face in ('dessus', 'dessous'): return N1
        if face == 'avant':
            if x in (0, w-1) or y in (0, h-1): return O2
            if x in (w//2 - 1, w//2): return O3 if y % 3 == 0 else O1
            if y == h - 3: return O2
            return noir(x, y)
        if face == 'arriere': return O1 if y in (0, h-1) else noir(x, y)
        return noir(x, y)
    boite_uv(l1, 16, 16, 8, 12, 4, corps)
    def bras(face, x, y, w, h):
        if face in ('dessus', 'dessous'): return O2 if face == 'dessus' else N1
        if y in (0, 3, h-1): return O2
        return N3 if (x + y) % 3 == 0 else N2
    boite_uv(l1, 40, 16, 4, 12, 4, bras)
    def bottes(face, x, y, w, h):
        if face == 'dessus': return None
        if face == 'dessous': return N1
        if y < 7: return None
        if y == 7: return O2
        if y == h-1: return N1
        if face == 'avant' and y == h-2: return O2
        return N2
    boite_uv(l1, 0, 16, 4, 12, 4, bottes)
    def tete(face, x, y, w, h): return noir(x, y)
    boite_uv(l1, 0, 0, 8, 8, 8, tete)
    # couche 2 : jambières (ceinture + jambes)
    def ceinture(face, x, y, w, h):
        if face in ('dessus', 'dessous'): return None if face == 'dessus' else N1
        if y < 8: return None
        return O2 if y == 8 else noir(x, y)
    boite_uv(l2, 16, 16, 8, 12, 4, ceinture)
    def jambes(face, x, y, w, h):
        if face in ('dessus',): return None
        if face == 'dessous': return N1
        if y == 0: return O1
        if face == 'avant' and y in (4, 5) and 0 < x < w-1: return O2
        return noir(x, y)
    boite_uv(l2, 0, 16, 4, 12, 4, jambes)
    l1.save(TEX + 'models/armor/sacree_layer_1.png'); l2.save(TEX + 'models/armor/sacree_layer_2.png')

# ======================================================================= ARMURE IMPÉRIALE (128x128, modèle sur mesure)
# tuiles 32x16 en x>=64 : matières unies des pièces ajoutées
TUILES = [O2, O3, O1, N2, B2, ET, (150,205,220), N1]
def tuile(i): return (64 + (i % 2) * 32, (i // 2) * 16)
CAPE_UV = (64, 64)
def imperiale():
    im = Image.new('RGBA', (128, 128), (0,0,0,0))
    # couche « 1 » en (0,0) : casque, plastron, bras, bottes
    def tete(face, x, y, w, h):
        if face == 'dessus': return B2 if (x + y) % 2 else B3
        if face == 'dessous': return None
        if face == 'avant':
            if y == 4 and 0 < x < w-1: return N1                       # visière
            if y == 1: return O2
        if face in ('droite', 'gauche') and 2 <= y <= 5: return N2      # joues de netherite
        if y == 1: return O2 if x % 2 else O1
        return nacre(x, y)
    boite_uv(im, 0, 0, 8, 8, 8, tete)
    def corps(face, x, y, w, h):
        if face in ('dessus', 'dessous'): return N1
        if face == 'avant':
            if x in (0, w-1): return N2
            if y in (0, h-1): return O2
            if y == h-2: return O1
            return nacre(x, y)
        if face == 'arriere': return O1 if y in (0, h-1) else nacre(x, y)
        return N2 if y % 4 else N3
    boite_uv(im, 16, 16, 8, 12, 4, corps)
    def bras(face, x, y, w, h):
        if face == 'dessus': return O2
        if face == 'dessous': return N1
        if y in (1, 5): return O2
        if y < 5: return N2
        return O1 if y == h-1 else nacre(x + 2, y)
    boite_uv(im, 40, 16, 4, 12, 4, bras)
    def bottes(face, x, y, w, h):
        if face == 'dessus': return None
        if face == 'dessous': return N1
        if y < 7: return None
        if y == 7: return O2
        if y == h-1: return N1
        if face == 'avant' and y == h-2: return O1
        return nacre(x, y)
    boite_uv(im, 0, 16, 4, 12, 4, bottes)
    # couche « 2 » en (0,32) : ceinture et jambières
    def ceinture(face, x, y, w, h):
        if face == 'dessus': return None
        if face == 'dessous': return N1
        if y < 8: return None
        return O2 if y in (8, h-1) else N2
    boite_uv(im, 16, 48, 8, 12, 4, ceinture)
    def jambes(face, x, y, w, h):
        if face == 'dessus': return None
        if face == 'dessous': return N1
        if face in ('droite', 'gauche'): return N2 if y % 4 else N3
        if y in (0, 4): return O2
        return nacre(x, y)
    boite_uv(im, 0, 48, 4, 12, 4, jambes)
    # tuiles
    for i, c in enumerate(TUILES):
        u, v = tuile(i)
        for x in range(32):
            for y in range(16):
                im.putpixel((u + x, v + y), bruit(c, 3) if i not in (5, 6) else c + (255,))
    # cape (boîte 12 x 22 x 1)
    def cape(face, x, y, w, h):
        if face in ('dessus', 'dessous', 'droite', 'gauche'): return O2
        if x in (0, w-1) or y == h-1: return O2
        if y == 0: return O1
        return CAPE1 if (x + y) % 5 else CAPE2
    boite_uv(im, CAPE_UV[0], CAPE_UV[1], 12, 22, 1, cape)
    im.save(TEX + 'models/armor/imperiale.png')

# ======================================================================= géométrie ajoutée (repère des parties du modèle humain)
G = {}
def b(part, x, y, z, w, h, d, t): G.setdefault(part, []).append((x, y, z, w, h, d, t))
OR, ORC, ORS, NOIRT, NAC, ETO, VER, NOIR2 = range(8)
# --- casque : couronne intégrée (bandeau, fleurons blancs à pointe d'or), étoile au sommet, étoile au front, loupe
for (x, z, w, d) in ((-5.2, -5.2, 10.4, 0.6), (-5.2, 4.6, 10.4, 0.6), (-5.2, -4.6, 0.6, 9.2), (4.6, -4.6, 0.6, 9.2)):
    b('tete', x, -9.6, z, w, 1.2, d, OR)
for k in (-4.6, -1.6, 0.6, 3.6):
    for z in (-5.2, 4.6):
        b('tete', k, -11.2, z, 1, 1.6, 0.6, NAC); b('tete', k, -12.2, z, 1, 1, 0.6, ORC)
    for x in (-5.2, 4.6):
        if k in (-1.6, 0.6): b('tete', x, -11.2, k, 0.6, 1.6, 1, NAC); b('tete', x, -12.2, k, 0.6, 1, 1, ORC)
b('tete', -1, -13.6, -5.4, 2, 2, 0.8, ETO); b('tete', -1.5, -11.6, -5.4, 3, 0.6, 0.9, OR)       # grande étoile au sommet de l'avant
b('tete', -1, -7.6, -5.35, 2, 2, 0.4, ETO)                                                       # étoile au front
for (x, y, w, h) in ((-1.6, -8.2, 3.2, 0.6), (-1.6, -5.6, 3.2, 0.6), (-1.6, -7.6, 0.6, 2), (1, -7.6, 0.6, 2)):
    b('tete', x, y, -5.3, w, h, 0.3, OR)
b('tete', -3.5, -4.6, -5.6, 2, 2, 0.4, VER)                                                      # loupe (œil droit)
for (x, y, w, h) in ((-4, -5.1, 3, 0.5), (-4, -2.6, 3, 0.5), (-4, -4.6, 0.5, 2), (-1.5, -4.6, 0.5, 2)):
    b('tete', x, y, -5.5, w, h, 0.4, OR)
b('tete', -5.3, -4.2, -5.2, 0.6, 0.6, 1.6, OR)
# --- plastron : étoile au cœur, sertie d'or
b('corps', -1, 3, -3.35, 2, 2, 0.4, ETO)
for (x, y, w, h) in ((-1.6, 2.4, 3.2, 0.6), (-1.6, 5, 3.2, 0.6), (-1.6, 3, 0.6, 2), (1, 3, 0.6, 2)):
    b('corps', x, y, -3.3, w, h, 0.3, OR)
# --- cape (partie à part, accrochée au dos) et sa barre d'or
b('cape_barre', -6.5, -0.6, 2.4, 13, 1, 1.2, OR)
# --- grandes épaulières (repère des bras : droit -3..1, gauche -1..3 en x)
for part, x0 in (('bras_d', -5.6), ('bras_g', -1.4)):
    b(part, x0, -4.2, -4, 7, 3.4, 8, NAC)
    b(part, x0 - 0.1, -1.2, -4.1, 7.2, 0.6, 8.2, OR)
    b(part, x0 - 0.1, -4.4, -4.1, 7.2, 0.5, 8.2, OR)
    for k in range(3): b(part, x0 + 1 + k * 2.4, -4.6, -0.5, 0.8, 0.4, 1, ORC)
# --- jambières : genouillères d'or ; bottes : coques de pointe
for part in ('jambe_d', 'jambe_g'):
    b(part, -1.5, 4, -2.8, 3, 1.4, 0.4, OR)
    b(part.replace('jambe', 'pied'), -2.6, 10.8, -3.4, 5.2, 1.4, 0.6, OR)   # bottes

L = ['package fr.chatmort.airain.armure;', '', 'import java.util.Map;', '',
     '/** Généré par armure/gen_armures.py : pièces ajoutées de l\'armure impériale (pixels, repère de la partie). */',
     'final class ImperialeGeo {', '\tprivate ImperialeGeo() {}',
     '\t/** Coin haut-gauche des tuiles de matière (32 x 16) dans la texture 128 x 128. */',
     '\tstatic final int[][] TUILES = {' + ', '.join('{%d, %d}' % tuile(i) for i in range(len(TUILES))) + '};',
     '\tstatic final int[] CAPE = {%d, %d};' % CAPE_UV,
     '\t/** x, y, z, largeur, hauteur, profondeur, tuile */', '\tstatic final Map<String, float[][]> PIECES = Map.of(']
f = lambda v: ('%g' % round(v, 3)) + 'f'
L.append(',\n'.join('\t\t"%s", new float[][] {\n%s}' % (k, ',\n'.join('\t\t\t{' + ', '.join(f(q) for q in e[:6]) + ', %d}' % e[6] for e in v)) for k, v in G.items()))
L += ['\t);', '}']
open(MOD + '/java/fr/chatmort/airain/armure/ImperialeGeo.java', 'w').write('\n'.join(L) + '\n')

# ======================================================================= icônes
P = dict(k=(16,12,18), n=N2, N=N3, m=N1, o=O2, O=O3, d=O1, b=B2, B=B3, c=B1, e=ET, r=CAPE1)
ICONES = {
 'plastron_sacre': ["................", "..kkkk....kkkk..", ".kodnnk..knndok.", ".knnnnkkkknnnnk.", ".kkkknoddoknkkk.", "....kndOOdnk....", "....knnddnnk....",
                    "....knNddNnk....", "....knnddnnk....", "....kooOOook....", "....knnddnnk....", "....knNddNnk....", "....koooooook...", ".....kkkkkkk....", "................", "................"],
 'jambieres_sacrees': ["................", "....kkkkkkkk....", "....kooooook....", "....knnnnnnk....", "....knnkknnk....", "....knnkknnk....", "....kOokkoOk....",
                       "....kOokkoOk....", "....knnkknnk....", "....knnkknnk....", "....knnkknnk....", "....kddkkddk....", "....kkkkkkkk....", "................", "................", "................"],
 'bottes_sacrees': ["................", "................", "................", "................", "...kkkk..kkkk...", "...koook.koook..", "...knnk..knnk...",
                    "...knnk..knnk...", "...knnk..knnk...", "..knnnk.knnnk...", ".kooOok.kooOok..", ".kmmmmk.kmmmmk..", ".kkkkkk.kkkkkk..", "................", "................", "................"],
 'casque_imperial': ["......kOk.......", "...kOkkekkOk....", "...kbkkokkbk....", "...kbbbbbbbk....", "..kooooooooook..", "..kbbbbeebbbbk..", "..knbbbeebbbnk..",
                     "..knkkkkkkkknk..", "..knbBbbbbBbnk..", "..knbbbbbbbbnk..", "..kkk......kkk..", "................", "................", "................", "................", "................"],
 'plastron_imperial': ["................", "..kkkkk..kkkkk..", ".kBbbook.koobbBk", ".kooooookoooooo.", ".kkkknboobnkkkk.", "....knbeebnk....", "....knbeebnk....",
                       "....knbbobnk....", "....knBbbbnk....", "....knbbBbnk....", "....kodooddk....", "....knbbbbnk....", "....kooooook....", ".....kkkkkk.....", "................", "................"],
 'jambieres_imperiales': ["................", "....kkkkkkkk....", "....kooooook....", "....knnnnnnk....", "....kbbkkbbk....", "....kbBkkbBk....", "....kookkook....",
                          "....kbbkkbbk....", "....kBbkkBbk....", "....kbbkkbbk....", "....knbkkbnk....", "....kddkkddk....", "....kkkkkkkk....", "................", "................", "................"],
 'bottes_imperiales': ["................", "................", "................", "................", "...kkkk..kkkk...", "...koook.koook..", "...kbBk..kbBk...",
                       "...kbbk..kbbk...", "...kbbk..kbbk...", "..knbbk.knbbk...", ".kdooOk.kdooOk..", ".kmmmmk.kmmmmk..", ".kkkkkk.kkkkkk..", "................", "................", "................"],
}
def icones():
    import json
    for nom, g in ICONES.items():
        im = Image.new('RGBA', (16, 16), (0,0,0,0))
        for y, r in enumerate(g):
            for x, ch in enumerate(r.ljust(16, '.')[:16]):
                if ch != '.': im.putpixel((x, y), P[ch] + (255,))
        im.save(TEX + 'item/' + nom + '.png')
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "airain:item/" + nom}},
                  open(MOD + '/resources/assets/airain/models/item/' + nom + '.json', 'w'))

if __name__ == '__main__':
    import os
    os.makedirs(MOD + '/java/fr/chatmort/airain/armure', exist_ok=True)
    sacree(); imperiale(); icones(); print({k: len(v) for k, v in G.items()})
