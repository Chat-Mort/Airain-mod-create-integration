# Repérage des zones d'une planche de Create : composantes connexes d'une couleur de remplissage -> rectangles
import sys, numpy as np
from PIL import Image
from scipy import ndimage
O = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/'
def zones(feuille, couleurs, mini=4, cadre=None):
    a = np.array(Image.open(O + feuille + '.png').convert('RGBA'))
    m = np.zeros(a.shape[:2], bool)
    for c in couleurs:
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        m |= (a[..., 0] == r) & (a[..., 1] == g) & (a[..., 2] == b) & (a[..., 3] == 255)
    if cadre: m[:] &= False if False else True; m &= np.pad(np.ones((cadre[3]-cadre[1], cadre[2]-cadre[0]), bool), ((cadre[1], a.shape[0]-cadre[3]), (cadre[0], a.shape[1]-cadre[2])))
    lab, n = ndimage.label(m)
    out = []
    for s in ndimage.find_objects(lab):
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        if (x1 - x0) >= mini and (y1 - y0) >= mini: out.append((x0, y0, x1, y1))
    return sorted(out, key=lambda r: (r[1], r[0]))
if __name__ == '__main__':
    f = sys.argv[1]; cs = sys.argv[2].split(',')
    for r in zones(f, cs): print(r, 'w', r[2]-r[0], 'h', r[3]-r[1])
