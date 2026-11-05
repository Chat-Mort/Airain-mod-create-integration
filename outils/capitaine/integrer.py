import random
from PIL import Image
M = '/home/claude/airain-mod-create-integration/src/main'
src = open('apercu.py').read(); src = src[:src.index('bloc, put, cyl')]
g = {}; exec(src, g)
g['recolor'](g['f_cap']).save(M + '/resources/assets/airain/textures/entity/gardien_capitaine.png')
g['recolor'](g['f_echo']).save(M + '/resources/assets/airain/textures/entity/gardien_echo.png')
GOLD, GOLD2, WH, RED, DARK, LAV, VIO, LAVG, CYAN, GEM = (235,195,75), (185,140,40), (248,246,236), (150,25,32), (20,16,30), (190,165,240), (120,90,180), (205,185,255), (120,235,230), (255,255,255)
T = [GOLD, GOLD2, WH, RED, DARK, LAV, VIO, LAVG, CYAN, GEM]
random.seed(7)
tex = Image.new('RGBA', (256, 128), (0, 0, 0, 0))
for i, c in enumerate(T):
    u, v = (i % 4) * 64, (i // 4) * 32
    for x in range(64):
        for y in range(32):
            n = random.randint(-8, 8) if c in (RED, DARK, GOLD, GOLD2) else random.randint(-3, 3)
            if c == RED and (x + y) % 9 == 0: n -= 30
            tex.putpixel((u + x, v + y), tuple(max(0, min(255, k + n)) for k in c) + (255,))
tex.save(M + '/resources/assets/airain/textures/entity/gardien_elite.png')
P = {}
def box(part, ox, oy, oz, x, y, z, w, h, d, c):
    P.setdefault(part, []).append((x - ox, y - oy, z - oz, w, h, d, T.index(c)))
TETE, CORPS = (0, -7, -2), (0, -7, 0)
def tete(*a): box('cap_tete', *TETE, *a)
# couronne
tete(-4.5, -20, -8, 9, 1, 0.5, GOLD); tete(-4.5, -20, 0.5, 9, 1, 0.5, GOLD)
tete(-4.5, -20, -7.5, 0.5, 1, 8, GOLD2); tete(4, -20, -7.5, 0.5, 1, 8, GOLD2)
for (x, z) in [(-4.5, -8), (-0.5, -8), (3.5, -8), (-4.5, -3.5), (3.5, -3.5), (-4.5, 0), (-0.5, 0), (3.5, 0)]:
    tete(x, -22, z, 1, 2, 0.5 if z in (-8, 0) else 1, GOLD)
box('cap_tete_lum', *TETE, -1, -21.5, -8.5, 2, 1.5, 0.5, GEM)
for i in range(8): tete(-0.5 + i * 0.25, -23 - i * 0.6, -3 + i * 0.6, 1, 1, 1, WH)
for nom, x0 in (('cap_brasD', -14.5), ('cap_brasG', 8.5)):
    box(nom, *CORPS, x0, -11, -4, 6, 1.5, 8, GOLD)
    for i in range(12): box(nom, *CORPS, x0 + i * 0.5, -9.5, -4.5, 0.5, 1.5 + (i % 2), 0.5, WH)
box('cap_corps', *CORPS, -8, -9, 5, 16, 1, 1.5, GOLD2)
box('cap_corps', *CORPS, -8.5, -8, 5.5, 17, 24, 0.5, RED)
# Écho
box('echo_corps', *CORPS, -3.5, -7, -6.5, 7, 7, 0.5, DARK)
box('echo_corps_lum', *CORPS, -2.6, -6.1, -6.7, 5.2, 5.2, 0.2, LAVG)
box('echo_corps_lum', *CORPS, -1.6, -5.1, -6.8, 3.2, 3.2, 0.2, CYAN)
for (x, h) in [(-5, 6), (-2, 8), (1, 7), (4, 5)]:
    box('echo_corps', *CORPS, x, -9 - h + 1.5, 4, 1.5, h - 1.5, 1.5, VIO); box('echo_corps_lum', *CORPS, x, -9 - h, 4, 1.5, 1.5, 1.5, LAVG)
for nom, l in (('echo_brasD', [(-12.5, -2, 5), (-11, 1, 3.5), (-13, 1.5, 2.5)]), ('echo_brasG', [(10.5, -2, 5), (12, 1, 3.5), (9.5, 1.5, 2.5)])):
    for (x, z, h) in l:
        box(nom, *CORPS, x, -9.5 - h + 1, z, 1.5, h - 1, 1.5, LAV); box(nom + '_lum', *CORPS, x, -9.5 - h, z, 1.5, 1, 1.5, LAVG)
L = ['package fr.chatmort.airain.gardien;', '', 'import java.util.LinkedHashMap;', 'import java.util.Map;', '',
     '/** Ornements des gardiens d\'élite (générés par capitaine/integrer.py) : {x, y, z, w, h, d, tuile} dans le repère de la pièce porteuse. */',
     'final class EliteGeo {', '\tprivate EliteGeo() {}', '\tstatic final Map<String, float[][]> PARTIES = new LinkedHashMap<>();', '\tstatic {']
for k, bs in P.items():
    L.append(f'\t\tPARTIES.put("{k}", new float[][] {{' + ', '.join('{' + ', '.join(f'{v:g}f' for v in b) + '}' for b in bs) + '});')
L += ['\t}', '}', '']
open(M + '/java/fr/chatmort/airain/gardien/EliteGeo.java', 'w').write('\n'.join(L))
print({k: len(v) for k, v in P.items()})
