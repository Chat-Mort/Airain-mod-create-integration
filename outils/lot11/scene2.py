import sys
sys.path.insert(0, '/home/claude/travail/lot9')
import numpy as np
from PIL import Image
from proj import rendre, boite as _b, T
U = {k: (0, 0, 16, 16) for k in ('north', 'south', 'east', 'west', 'up', 'down')}
def boite(f, t, tex): return _b(f, t, tex, uvs=U)
def fil(col):
    im = np.zeros((16, 16, 4), np.uint8)
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)): im[y, x] = col
    return im
TX = {'sol': T('herringbone_slate'), 'blanc': T('white_marble_0'), 'noir': T('black_marble_0'), 'airain': T('airain_block'),
      'fil': fil((243, 214, 148, 255)), 'rouge': fil((192, 67, 67, 255)), 'piquet': T('airain_block')}
GUI = lambda s: {'vue': [38, 35], 'scale': [s] * 3}
def decale(el, w, d):
    for e in el:
        e['from'] = [e['from'][0] - w * 8 + 8, e['from'][1], e['from'][2] - d * 8 + 8]
        e['to'] = [e['to'][0] - w * 8 + 8, e['to'][1], e['to'][2] - d * 8 + 8]
    return el
def scene(w, d, poses, fantomes, cadres, rouges, echelle, N=420, boites=()):
    """poses : {(x,z): tex} au niveau 0 ; fantomes : idem en transparence ; cadres / rouges : cases en fil d'airain / rouge."""
    sol = [boite([x * 16, -16, z * 16], [x * 16 + 16, 0, z * 16 + 16], 'sol') for x in range(w) for z in range(d)]
    ps = [boite([x * 16, y * 16, z * 16], [x * 16 + 16, y * 16 + 16, z * 16 + 16], t) for (x, y, z), t in poses.items()]
    g = GUI(echelle)
    base = rendre(decale(sol + ps, w, d), TX, g, N)
    if fantomes:
        fa = rendre(decale([boite([x * 16 + .5, y * 16 + .5, z * 16 + .5], [x * 16 + 15.5, y * 16 + 15.5, z * 16 + 15.5], t) for (x, y, z), t in fantomes.items()], w, d), TX, g, N)
        fa.putalpha(Image.eval(fa.getchannel('A'), lambda k: k * 140 // 255)); base.alpha_composite(fa)
    for cs, t in ((cadres, 'fil'), (rouges, 'rouge')):
        if cs:
            f = rendre(decale([boite([x * 16 + .2, y * 16 + .2, z * 16 + .2], [x * 16 + 15.8, y * 16 + 15.8, z * 16 + 15.8], t) for (x, y, z) in cs], w, d), TX, g, N, lumineux=(t,))
            base.alpha_composite(f)
    for (f0, f1, tx) in boites:      # grandes boîtes de sélection (fil sur le pourtour seulement)
        f = rendre(decale([boite([f0[0] * 16 + .2, f0[1] * 16 + .2, f0[2] * 16 + .2], [f1[0] * 16 - .2, f1[1] * 16 - .2, f1[2] * 16 - .2], tx)], w, d), TX, g, N, lumineux=(tx,))
        base.alpha_composite(f)
    return base
