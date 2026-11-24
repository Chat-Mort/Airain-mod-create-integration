# Scènes de la maquette du cordeau : sol d'ardoise, deux piquets A et B, cases prévues en fil d'airain
import numpy as np
from PIL import Image
from proj import rendre, boite as _boite, T
U = {k: (0, 0, 16, 16) for k in ('north', 'south', 'east', 'west', 'up', 'down')}
def boite(f, t, tex): return _boite(f, t, tex, uvs=U)
def fil():
    im = np.zeros((16, 16, 4), np.uint8)
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)): im[y, x] = (243, 214, 148, 255)
    return im
def voile():
    im = np.zeros((16, 16, 4), np.uint8); im[:, :] = (243, 214, 148, 255); return im
TX = {'sol': T('cut_slate'), 'fil': fil(), 'voile': voile(), 'pierre': T('herringbone_slate'), 'piquet': T('airain_block')}

def scene(cases, a, b, w=7, d=4, posees=(), N=420):
    """cases : positions (x, y, z) prévues ; a, b : piquets ; posees : blocs déjà là."""
    sol = [boite([x * 16, -16, z * 16], [x * 16 + 16, 0, z * 16 + 16], 'sol') for x in range(w) for z in range(d)]
    pq = [boite([p[0] * 16 + 6, p[1] * 16, p[2] * 16 + 6], [p[0] * 16 + 10, p[1] * 16 + 10, p[2] * 16 + 10], 'piquet') for p in (a, b) if p]
    pz = [boite([x * 16, y * 16, z * 16], [x * 16 + 16, y * 16 + 16, z * 16 + 16], 'pierre') for (x, y, z) in posees]
    gui = {'vue': [32, 35], 'scale': [0.115] * 3}
    def decale(el):
        for e in el:
            e['from'] = [e['from'][0] - w * 8 + 8, e['from'][1] - 8 + 8, e['from'][2] - d * 8 + 8]
            e['to'] = [e['to'][0] - w * 8 + 8, e['to'][1] - 8 + 8, e['to'][2] - d * 8 + 8]
        return el
    base = rendre(decale(sol + pq + pz), TX, gui, N)
    fils = [boite([x * 16 + .3, y * 16 + .3, z * 16 + .3], [x * 16 + 15.7, y * 16 + 15.7, z * 16 + 15.7], 'fil') for (x, y, z) in cases]
    vl = [boite([x * 16 + .3, y * 16 + .3, z * 16 + .3], [x * 16 + 15.7, y * 16 + 15.7, z * 16 + 15.7], 'voile') for (x, y, z) in cases]
    v = rendre(decale(vl), TX, gui, N, lumineux=('voile',)); v.putalpha(Image.eval(v.getchannel('A'), lambda k: k * 45 // 255))
    f = rendre(decale(fils), TX, gui, N, lumineux=('fil',))
    base.alpha_composite(v); base.alpha_composite(f)
    return base
