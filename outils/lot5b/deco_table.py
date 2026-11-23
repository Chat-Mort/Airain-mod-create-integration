# Table de décoration de Sophisticated Storage, dans le style des écrans vanilla HD du pack (cadre d'or riveté de 9 texels,
# ardoise à joints, cases au filet d'or, sortie sertie, flèche d'or, engrenage gravé) — coordonnées relevées sur la planche
# d'origine et dans DecorationTableMenu / DecorationTableScreen (Sophisticated Storage 1.21.x).
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
import kit
from kit import *
O = '/tmp/src5/sophst/src/main/resources/assets/sophisticatedstorage/textures/gui/'

class en_or:
    """Le kit dessine en airain exposé ; les écrans vanilla HD sont en or : on échange la palette le temps du dessin."""
    def __enter__(self):
        self.sv = dict(EXP); EXP.update(trait=OR['trait'], base=OR['base'], clair=OR['clair'], mi=OR['mi'], sombre=OR['sombre'])
    def __exit__(self, *a): EXP.clear(); EXP.update(self.sv)

def cadre_union(p, rects, graine=3):
    """Cadre de 9 texels autour de l'union de rectangles (px d'interface) : mêmes bandes que les plaques vanilla HD,
    angles rentrants compris (distance de Tchebychev au bord), ardoise à joints dedans."""
    H, W = p.im.height, p.im.width; m = np.zeros((H, W), bool)
    for (x, y, w, h) in rects: m[y * S:(y + h) * S, x * S:(x + w) * S] = True
    d = ndimage.distance_transform_cdt(np.pad(m, 1), metric='chessboard')[1:-1, 1:-1]
    fond = Planche(); fond.ardoise(0, 0, W - 1, H - 1, graine)
    bandes = [OR['trait'], OR['base'], OR['clair'], OR['clair'], OR['base'], OR['mi'], OR['mi'], OR['sombre'], OR['trait']]
    px = p.im.load(); fp = fond.im.load()
    for Y, X in zip(*np.nonzero(m)):
        k = d[Y, X] - 1
        px[X, Y] = bandes[k] if k < 9 else fp[X, Y]

def table_decoration():
    p = Planche()
    cadre_union(p, [(0, 0, 250, 138), (37, 130, 176, 91)])
    with en_or():
        # rivets du cadre, au milieu de la bande (comme les plaques vanilla HD) : coins et tous les 20 px environ
        for (X, Y) in ((4, 4), (250 * S - 5, 4), (4, 138 * S - 5), (250 * S - 5, 138 * S - 5), (37 * S + 4, 221 * S - 5), (213 * S - 5, 221 * S - 5)):
            p.rivet(X, Y)
        for X in range(60, 250 * S - 40, 60): p.rivet(X, 4)
        for Y in range(60, 138 * S - 30, 60): p.rivet(4, Y); p.rivet(250 * S - 5, Y)
        for X in range(37 * S + 60, 213 * S - 30, 60): p.rivet(X, 221 * S - 5)
        for (X0, X1) in ((24, 37 * S - 20), (213 * S + 20, 250 * S - 24)):         # bas du panneau du haut, de part et d'autre
            p.rivet((X0 + X1) // 2, 138 * S - 5)
        # cases (le gris de l'original est l'intérieur 16 x 16 ; la case fait 18 x 18)
        for (x, y) in ((7, 16), (7, 46), (7, 76), (7, 106), (55, 46), (55, 76), (55, 106), (99, 16), (117, 16), (135, 16), (99, 106)):
            p.creux(x, y, 18, 18)
        for r in range(3):
            for c in range(9): p.creux(44 + 18 * c, 138 + 18 * r, 18, 18)
        for c in range(9): p.creux(44 + 18 * c, 196, 18, 18)
        p.r(44 * S, 194 * S, 206 * S - 1, 194 * S + 1, OR['trait']); p.r(44 * S + 1, 194 * S, 206 * S - 2, 194 * S, OR['base'])   # filet au-dessus de la barre
        # sortie : grande case sertie (131,102 26 x 26)
        p.case_riche(131, 102, 26, 26, ep=4)
        # aperçu du coffre décoré (161,16 82 x 112) : creux profond, rivets d'angle
        p.creux(161, 16, 82, 112, fond=hx('1b1e24'))
        for (X, Y) in ((161 * S + 9, 16 * S + 9), (243 * S - 10, 16 * S + 9), (161 * S + 9, 128 * S - 10), (243 * S - 10, 128 * S - 10)):
            p.r(X - 1, Y - 1, X + 1, Y + 1, OR['trait']); p.im.putpixel((X, Y), OR['clair'])
        # flèche d'or de la case du coffre vers la sortie (centrée sur 115)
        fl = Image.new('L', (11 * S, 11 * S)); dd = ImageDraw.Draw(fl)
        dd.polygon([(0, 12), (17, 12), (17, 4), (32, 16), (17, 28), (17, 20), (0, 20)], fill=255)
        for yy in range(fl.height):
            for xx in range(fl.width):
                if fl.getpixel((xx, yy)):
                    bord = any(not (0 <= xx + a < fl.width and 0 <= yy + b < fl.height) or not fl.getpixel((xx + a, yy + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    p.im.putpixel((119 * S + xx, 110 * S - 1 + yy), OR['trait'] if bord else OR['clair'] if yy < 15 else OR['mi'])
    # engrenages gravés dans la place libre du haut (comme l'établi HD)
    p.engrenage(78, 25, 22, 10); p.engrenage(92, 30, 13, 7)
    return p.im

if __name__ == '__main__':
    table_decoration().save('/tmp/nv/deco.png')
