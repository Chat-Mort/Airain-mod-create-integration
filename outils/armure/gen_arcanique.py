"""Armure arcanique (Morgana Dalmont) : redingote à pans fendus, capuche, diadème, mantelet noir ; texture 128x128 + ArcaniqueGeo.java + icônes."""
import random, json
from PIL import Image
import gen_armures as GA
MOD = '/home/claude/airain-mod-create-integration/src/main'
TEX = MOD + '/resources/assets/airain/textures/'
NOIR, NOIR2 = (12,8,18), (30,22,40)
F1, F2 = (24,14,34), (36,24,50)
V1, V2, V3 = (58,30,96), (86,48,140), (122,84,190)
LV, LV2 = (186,156,255), (232,218,255)
AR = (176,180,198)                         # le diadème reste d'argent
boite = GA.boite_uv
def viol(x, y): return V2 if (x - y) % 7 == 0 else V1

TUILES = [NOIR, NOIR2, V1, V2, LV, LV2, AR, F2]      # 0..7, 32x16 en x >= 64
def tuile(i): return (64 + (i % 2) * 32, (i // 2) * 16)
PANS = (64, 64)                                       # pans de la redingote (dos et côtés)

def texture():
    im = Image.new('RGBA', (128, 128), (0,0,0,0))
    def capuche(face, x, y, w, h):
        if face == 'dessous': return None
        if face == 'avant':
            if 1 <= x <= w-2 and 2 <= y <= h-1: return None            # le visage reste découvert
            return NOIR if y <= 1 or x in (0, w-1) else viol(x, y)
        if face == 'dessus': return V3 if (x + y) % 4 == 0 else viol(x, y)
        return viol(x, y)
    boite(im, 0, 0, 8, 8, 8, capuche)
    def torse(face, x, y, w, h):
        if face in ('dessus', 'dessous'): return F1
        if face == 'avant':
            if x in (w//2 - 1, w//2): return LV if y % 3 == 1 else NOIR     # fermoirs sur la fente
            if y <= 1 and x in (w//2 - 2, w//2 + 1): return V3              # revers du col
            if x in (0, w-1) or y == h-1: return NOIR
            if y == 9: return NOIR                                          # ceinture
            if (x + y) % 6 == 0 and y < 9: return LV
            return viol(x, y)
        if face == 'arriere': return NOIR if y in (0, 9) else viol(x, y)
        return NOIR2 if y == 9 else viol(x, y)
    boite(im, 16, 16, 8, 12, 4, torse)
    def manches(face, x, y, w, h):
        if face == 'dessus': return NOIR
        if face == 'dessous': return NOIR
        if y >= h-2: return NOIR                                             # poignets noirs
        if y == 6 and x % 2 == 0: return LV
        return viol(x + 1, y)
    boite(im, 40, 16, 4, 12, 4, manches)
    def bottines(face, x, y, w, h):
        if face == 'dessus' or y < 7: return None
        if face == 'dessous' or y == h-1: return NOIR
        if y == 7: return NOIR2
        if face == 'avant' and y == h-2 and x in (1, 2): return LV
        return F2
    boite(im, 0, 16, 4, 12, 4, bottines)
    def ceinture(face, x, y, w, h):
        if face == 'dessus' or y < 9: return None
        if face == 'dessous': return F1
        return NOIR if y == 9 else F2
    boite(im, 16, 48, 8, 12, 4, ceinture)
    def chausses(face, x, y, w, h):
        if face == 'dessus': return None
        if face == 'dessous': return F1
        return F2 if (x + y) % 4 else V1
    boite(im, 0, 48, 4, 12, 4, chausses)
    rnd = random.Random(5)
    for i, c in enumerate(TUILES):
        u, v = tuile(i)
        for x in range(32):
            for y in range(16): im.putpixel((u + x, v + y), GA.bruit(c, 3) if i not in (4, 5, 6) else c + (255,))
    # pans : une boîte 10 x 8 x 6 (dos et côtés), runes brodées, ourlet noir
    def pans(face, x, y, w, h):
        if face in ('dessus', 'dessous'): return None
        if face == 'avant' and 1 < x < w-2: return None                  # fendue devant
        if y == h-1 or y == 0: return NOIR
        if (x + y) % 7 == 0: return LV
        return viol(x, y)
    boite(im, PANS[0], PANS[1], 10, 8, 6, pans)
    im.save(TEX + 'models/armor/arcanique.png')

# --------------------------------------------------------------------- pièces ajoutées (repère des parties)
G = {}
def b(part, x, y, z, w, h, d, t): G.setdefault(part, []).append((x, y, z, w, h, d, t))
N0, N2T, VI1, VI2, LUE, LUE2, ARG, FO = range(8)
# capuche : pointe dans le dos, bord avant épaissi ; diadème visible sous la capuche
b('tete', -1, -10.2, 2.6, 2, 1.4, 2, VI2); b('tete', -0.5, -11, 3.4, 1, 1, 1.4, VI1)
b('tete', -5.2, -9.2, -5.4, 10.4, 0.8, 0.6, N0)
for x0 in (-5.2, 4.6): b('tete', x0, -9.2, -5.4, 0.6, 9.4, 0.6, N0)
b('tete', -4, -7.2, -5.35, 8, 0.6, 0.3, ARG)                                     # cercle du diadème sur le front
b('tete', -1, -8.2, -5.6, 2, 1.6, 0.4, LUE2); b('tete', -1.5, -8.5, -5.5, 3, 2.2, 0.2, ARG)
# col haut, mantelet noir, boucle de ceinture en Écho primordial
b('corps', -4.6, -1.6, -3.3, 3.4, 2.4, 0.6, N0); b('corps', 1.2, -1.6, -3.3, 3.4, 2.4, 0.6, N0)
b('corps', -4.6, -1.6, 2.7, 9.2, 2.4, 0.6, N0)
b('corps', -1, 8.6, -3.45, 2, 1.6, 0.4, LUE2)
for part, x0 in (('bras_d', -4.4), ('bras_g', -1.6)):
    b(part, x0, -3.4, -3.6, 6, 2.6, 7.2, N0)
    b(part, x0 - 0.1, -1.1, -3.7, 6.2, 0.5, 7.4, N2T)
    b(part, x0 + 2.5, -3.6, -3.7, 1, 0.3, 7.4, LUE)
for part in ('pied_d', 'pied_g'): b(part, -2.6, 11, -3.4, 5.2, 1.2, 0.6, N0)

L = ['package fr.chatmort.airain.armure;', '', 'import java.util.Map;', '',
     '/** Généré par armure/gen_arcanique.py : pièces ajoutées de l\'armure arcanique (pixels, repère de la partie). */',
     'final class ArcaniqueGeo {', '\tprivate ArcaniqueGeo() {}',
     '\tstatic final int[][] TUILES = {' + ', '.join('{%d, %d}' % tuile(i) for i in range(len(TUILES))) + '};',
     '\tstatic final int[] PANS = {%d, %d};' % PANS, '\tstatic final Map<String, float[][]> PIECES = Map.of(']
f = lambda v: ('%g' % round(v, 3)) + 'f'
L.append(',\n'.join('\t\t"%s", new float[][] {\n%s}' % (k, ',\n'.join('\t\t\t{' + ', '.join(f(q) for q in e[:6]) + ', %d}' % e[6] for e in v)) for k, v in G.items()))
L += ['\t);', '}']
open(MOD + '/java/fr/chatmort/airain/armure/ArcaniqueGeo.java', 'w').write('\n'.join(L) + '\n')

# --------------------------------------------------------------------- icônes (silhouettes des autres armures)
import sys; sys.path.insert(0, '../armure2'); import icones_armure as IA
def capuche_i():
    def f(x, y, d):
        if 4 <= x <= 11 and y >= 6: return F1 if y > 6 else (186,156,255)          # ombre du visage, diadème
        return IA.ombrer(d, x, y, V3, V2, V1)
    im = IA.piece('casque', f)
    IA.ajouter(im, [(7, 6), (8, 6)], LV2); IA.ajouter(im, [(7, 2), (8, 2), (7, 1)], V2)
    return im
def redingote_i():
    def f(x, y, d):
        if y <= 3 and (x <= 5 or x >= 10): return NOIR if y <= 1 else NOIR2           # mantelet noir
        if x in (7, 8) and y >= 4: return LV if y % 3 == 1 else NOIR                  # fermoirs
        if y == 10: return NOIR
        if y >= 11 and x in (6, 9): return None
        if (x + y) % 6 == 0: return LV
        return IA.ombrer(d, x, y, V3, V2, V1)
    im = IA.piece('plastron', f)
    IA.ajouter(im, [(7, 10), (8, 10)], LV2)
    return im
def chausses_i():
    def f(x, y, d):
        if y == 1: return NOIR
        if y == 2: return LV if x in (7, 8) else NOIR2
        return IA.ombrer(d, x, y, V2, F2, F1)
    return IA.piece('jambieres', f)
def bottines_i():
    def f(x, y, d):
        if y == 4: return NOIR2
        if y == 11: return NOIR
        if y == 10 and x in (0, 1, 8, 9): return LV
        return IA.ombrer(d, x, y, V1, F2, F1)
    return IA.piece('bottes', f)
ICONES = [("casque_arcanique", capuche_i), ("plastron_arcanique", redingote_i), ("jambieres_arcaniques", chausses_i), ("bottes_arcaniques", bottines_i)]

if __name__ == '__main__':
    texture()
    for n, fn in ICONES:
        fn().save(TEX + 'item/' + n + '.png')
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "airain:item/" + n}}, open(MOD + '/resources/assets/airain/models/item/' + n + '.json', 'w'))
    print({k: len(v) for k, v in G.items()})
