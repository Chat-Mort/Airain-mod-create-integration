# Lecture des 24 motifs : flou pour effacer le grain du bois, taille de grille choisie par l'accord des pixels
# avec leur case, trois teintes (foncé = A, moyen = B, clair = accent)
import sys; sys.path.insert(0, '.')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from extraire import FICH, echantillons, face, lum
def teintes(vals):
    """k-moyennes à 3 centres sur une liste de luminances."""
    c = np.percentile(vals, [15, 50, 85]).astype(float)
    for _ in range(20):
        lab = np.argmin(np.abs(vals[:, None] - c[None, :]), axis=1)
        for k in range(3):
            if (lab == k).any(): c[k] = vals[lab == k].mean()
    return np.sort(c)
def lire(fc, n):
    img = Image.fromarray(fc.astype('uint8')).filter(ImageFilter.BoxBlur(2))
    L = lum(np.array(img).astype(float)); H, W = L.shape
    m = np.zeros((n, n))
    for j in range(n):
        for i in range(n):
            m[j, i] = np.median(L[int((j + .3) * H / n):int((j + .7) * H / n), int((i + .3) * W / n):int((i + .7) * W / n)])
    c = teintes(m.ravel())
    g = np.argmin(np.abs(m[..., None] - c[None, None, :]), axis=2)     # 0 foncé, 1 moyen, 2 clair
    # accord : part des pixels (zone centrale de chaque case) les plus proches de la teinte de leur case
    ok = tot = 0
    for j in range(n):
        for i in range(n):
            z = L[int((j + .15) * H / n):int((j + .85) * H / n), int((i + .15) * W / n):int((i + .85) * W / n)]
            lab = np.argmin(np.abs(z[..., None] - c[None, None, :]), axis=2)
            ok += (lab == g[j, i]).sum(); tot += lab.size
    return g, ok / tot
def meilleure(fc, tailles=range(6, 13)):
    r = [(lire(fc, n)[1], n) for n in tailles]
    return sorted(r)[::-1]
if __name__ == '__main__':
    k = 0; res = []
    for f in FICH:
        im, bx = echantillons(f)
        for b in bx:
            k += 1; fc = face(im, b); m = meilleure(fc)
            res.append((k, fc, m)); print(k, [(round(s, 3), n) for s, n in m[:3]])
