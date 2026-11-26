# Extraction des 24 motifs des captures de Liam : détection des échantillons (tout ce qui n'est pas l'herbe),
# découpe de la face du dessus, recherche de la taille de grille, moyenne par case, regroupement en 3 teintes
import numpy as np
from PIL import Image
from scipy import ndimage
FICH = ['/mnt/user-data/uploads/d2eb327b-image.png', '/mnt/user-data/uploads/cfcff6db-image.png']
def echantillons(f):
    im = np.array(Image.open(f).convert('RGB')).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    herbe = (g > r + 8) & (g > b + 8)
    bois = ~herbe
    bois = ndimage.binary_opening(bois, iterations=3)
    lab, n = ndimage.label(bois)
    boites = []
    for s in ndimage.find_objects(lab):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if h > 60 and w > 60: boites.append((s[0].start, s[1].start, s[0].stop, s[1].stop))
    boites.sort(key=lambda b: (round(b[0] / 80), b[1]))
    return im, boites
if __name__ == '__main__':
    for f in FICH:
        im, bx = echantillons(f); print(f[-20:], len(bx), bx)

def face(im, b, cote=0.075, bas=0.085):
    y0, x0, y1, x1 = b
    h, w = y1 - y0, x1 - x0
    return im[y0 + 1:int(y1 - h * bas), x0 + 1:int(x1 - w * cote)]
def lum(a): return 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
def grille(fc, n):
    H, W = fc.shape[:2]; L = lum(fc.astype(float))
    m = np.zeros((n, n)); s = 0
    for j in range(n):
        for i in range(n):
            ya, yb = int((j + 0.25) * H / n), int((j + 0.75) * H / n); xa, xb = int((i + 0.25) * W / n), int((i + 0.75) * W / n)
            c = L[ya:yb, xa:xb]; m[j, i] = np.median(c); s += c.var()
    return m, s / (n * n)
def meilleur(fc):
    res = []
    for n in range(5, 14):
        m, v = grille(fc, n)
        # contraste entre cases voisines : grand si la grille tombe juste
        contr = (np.abs(np.diff(m, axis=0)).mean() + np.abs(np.diff(m, axis=1)).mean())
        res.append((contr / (v ** 0.5 + 1), n))
    return sorted(res)[-3:]
