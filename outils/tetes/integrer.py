import sys, random; sys.path.insert(0, '.')
from geo import *
from PIL import Image
M = '/home/claude/airain-mod-create-integration/src/main'
random.seed(4)
TUILES = [None, ARG, ARG2, LAV, PALE, VIO, RUN, NOIR, VIO2]
tex = Image.new('RGBA', (64, 96), (0, 0, 0, 0))
nt = Image.open('../mcmeta-assets/assets/minecraft/textures/models/armor/netherite_layer_1.png').convert('RGBA')
tex.paste(nt.crop((0, 0, 32, 16)), (0, 0))
for t, c in enumerate(TUILES):
    if c is None: continue
    u, v = (t % 2) * 32, (t // 2) * 16
    for x in range(32):
        for y in range(16):
            n = random.randint(-6, 6) if c in (RUN, NOIR, VIO2) else random.randint(-3, 3)
            tex.putpixel((u + x, v + y), tuple(max(0, min(255, k + n)) for k in c) + (255,))
tex.save(M + '/resources/assets/airain/textures/models/armor/coiffes_echo.png')

def java(nom, B):
    L = [f'\tstatic void {nom}(CubeListBuilder c) {{']
    for (x, y, z, w, h, d, col) in B:
        col = col[:3]
        t = TUILES.index(col)
        L.append(f'\t\tc.texOffs({(t % 2) * 32}, {(t // 2) * 16}).addBox({x:g}f, {y:g}f, {z:g}f, {w:g}f, {h:g}f, {d:g}f);')
    L.append('\t}')
    return '\n'.join(L)
casque = [b for b in diademe_casque() if b[6] != NETH]
src = '''package fr.chatmort.airain.armure;

import net.minecraft.client.model.geom.builders.CubeListBuilder;

/** Géométrie des coiffes de l'Écho (générée par tetes/integrer.py) : texture coiffes_echo.png, tuiles unies de 32×16. */
final class CoiffesGeo {
	private CoiffesGeo() {}
''' + '\n'.join([java('casque', casque), java('tiare', tiare()), java('nimbe', nimbe()), java('halo', halo())]) + '\n}\n'
open(M + '/java/fr/chatmort/airain/armure/CoiffesGeo.java', 'w').write(src)

# ---- icônes 16×16
I = M + '/resources/assets/airain/textures/item/'
def px(im, pts, c):
    for p in pts: im.putpixel(p, c + (255,))
# casque au diadème : casque de netherite + cercle d'argent + gemme
im = Image.open('../mcmeta-assets/assets/minecraft/textures/item/netherite_helmet.png').convert('RGBA')
px(im, [(3, 7), (12, 7)], ARG2); px(im, [(x, 7) for x in range(4, 12)], ARG)
px(im, [(7, 5), (8, 5), (6, 6), (9, 6)], ARG); px(im, [(7, 6), (8, 6)], LAV); px(im, [(7, 7), (8, 7)], PALE)
px(im, [(4, 6), (11, 6)], VIO)
im.save(I + 'casque_diademe.png')
# tiare runique
im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
px(im, [(x, 10) for x in range(2, 14)], RUN); px(im, [(x, 11) for x in range(3, 13)], NOIR); px(im, [(x, 9) for x in range(2, 14)], ARG2)
px(im, [(1, 9), (1, 10), (14, 9), (14, 10)], NOIR)
px(im, [(x, 8) for x in range(4, 12)], RUN); px(im, [(x, 7) for x in range(5, 11)], RUN); px(im, [(x, 6) for x in range(6, 10)], RUN)
px(im, [(7, 5), (8, 5)], RUN); px(im, [(7, 4), (8, 4)], ARG)
px(im, [(4, 7), (11, 7), (5, 6), (10, 6), (6, 5), (9, 5)], ARG)
px(im, [(7, 6), (8, 6), (7, 7)], LAV); px(im, [(8, 7)], PALE); px(im, [(7, 8), (8, 8)], VIO)
px(im, [(5, 8), (10, 8)], VIO); px(im, [(4, 10), (7, 10), (8, 10), (11, 10)], LAV)
px(im, [(2, 8), (13, 8)], RUN); px(im, [(2, 7), (13, 7)], LAV)
im.save(I + 'casque_runique.png')
# nimbe : halo + couronne à branches fines
im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
px(im, [(x, 0) for x in range(4, 12)] + [(x, 2) for x in range(4, 12)] + [(2, 1), (3, 1), (12, 1), (13, 1), (3, 0), (12, 0), (3, 2), (12, 2)], PALE)
px(im, [(x, 12) for x in range(2, 14)], NOIR); px(im, [(x, 11) for x in range(2, 14)], VIO2)
for x, h in ((2, 2), (4, 3), (6, 2), (9, 2), (11, 3), (13, 2)):
    px(im, [(x, 11 - k) for k in range(1, h)], VIO2); px(im, [(x, 11 - h)], LAV)
px(im, [(7, y) for y in range(6, 11)] + [(8, y) for y in range(6, 11)], VIO2)
px(im, [(6, 7), (9, 7)], VIO2); px(im, [(5, 6), (10, 6)], LAV); px(im, [(7, 5), (8, 5)], PALE)
px(im, [(7, 8), (8, 8), (7, 9)], LAV); px(im, [(8, 9)], PALE); px(im, [(6, 8), (9, 8)], VIO)
im.save(I + 'casque_arcanique.png')
sheet = Image.new('RGBA', (16 * 3 * 12 + 40, 16 * 12 + 20), (32, 33, 38, 255))
for i, n in enumerate(('casque_diademe', 'casque_runique', 'casque_arcanique')):
    ic = Image.open(I + n + '.png').resize((192, 192), 0); sheet.alpha_composite(ic, (10 + i * 202, 10))
sheet.save('icones.png')
print('ok')
