# Lot 12, passe 2 : recoloration en airain « à patine rouge » des formes de référence (luminance -> rampe)
from PIL import Image
from px import hx
C = '/tmp/src5/create/src/main/resources/assets/create/textures/item/'
T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
ORIG = '/home/claude/travail/lot12/origine/'
# rampe sombre -> clair : les ombres tirent vers le rouge impérial de la patine, les clairs restent l'or de l'airain
RAMPE = [hx(c) for c in ('4a1410', '74201a', '9a3420', 'b85a2c', 'cc8236', 'dca447', 'e8bd5c', 'f2d27e', 'f9e6a8', 'fff6d8')]
REFLET = [hx('d9645c'), hx('c04343')]
def lum(c): return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
def recolorer(src, reflets=True, haut=8, bas=0):
    im = src.convert('RGBA'); px = im.load(); n, m = im.size
    teintes = sorted({px[x, y][:3] for y in range(m) for x in range(n) if px[x, y][3] > 0}, key=lum)
    k = len(teintes)
    l0, l1 = lum(teintes[0]), lum(teintes[-1])
    # la luminance d'origine fixe la place sur la rampe (les écarts du dessin sont gardés)
    table = {t: RAMPE[bas + round((lum(t) - l0) / max(1, l1 - l0) * (haut - bas))] for t in teintes}
    out = Image.new('RGBA', im.size); po = out.load()
    for y in range(m):
        for x in range(n):
            if px[x, y][3] > 0: po[x, y] = table[px[x, y][:3]]
    if reflets:
        # reflets de patine : un texel rouge là où un ton moyen touche un ton très clair (bord du reflet principal)
        for y in range(m):
            for x in range(n):
                c = po[x, y]
                if c[3] and c in (RAMPE[4], RAMPE[5]):
                    voisins = [po[x + i, y + j] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + i < n and 0 <= y + j < m]
                    if any(v in (RAMPE[8], RAMPE[9]) for v in voisins) and (x + 2 * y) % 3 == 0: po[x, y] = REFLET[0]
    return out
