# Icônes de Waystones redessinées au pixel (3x) : aplats francs par facette, ombrage en paliers, contour d'un texel.
# Aucune image agrandie : chaque icône est construite à partir de formes, pour éviter le flou et les mélanges de teintes.
import math
from hd import *
def P(*h): return [hx(x) for x in h]            # rampe : du plus clair au plus sombre, puis le trait
def facettes(W, H, faces, trait):
    """faces : [(polygone en texels, couleur)] dans l'ordre de dessin ; contour d'un texel autour de l'ensemble."""
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); m = masque(W, H)
    for pts, c in faces: d.polygon(pts, fill=c); ImageDraw.Draw(m).polygon(pts, fill=255)
    return entourer(im, m, trait)
def entourer(im, m, trait):
    q = m.load(); p = im.load(); W, H = im.size
    for y in range(H):
        for x in range(W):
            if q[x, y] < 128 and any(0 <= x + a < W and 0 <= y + b < H and q[x + a, y + b] > 127 for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                p[x, y] = trait
    return im
def sphere(d, rampe, trait, lum=(-.55, -.6), reflet=True):
    """Bille en paliers : éclairage d'en haut à gauche quantifié sur la rampe, reflet de deux texels."""
    im = Image.new('RGBA', (d + 2, d + 2)); m = masque(d + 2, d + 2); r = d / 2; c = r + 1
    p = im.load(); q = m.load()
    for y in range(d + 2):
        for x in range(d + 2):
            u, v = (x + .5 - c) / r, (y + .5 - c) / r
            if u * u + v * v > 1: continue
            z = math.sqrt(max(0, 1 - u * u - v * v)); e = -(u * lum[0] + v * lum[1]) * .9 + z * .45
            i = max(0, min(len(rampe) - 1, int((1 - e) * len(rampe) * .62)))
            p[x, y] = rampe[i]; m.putpixel((x, y), 255)
    if reflet:
        hx_, hy_ = int(c - r * .45), int(c - r * .5)
        for (a, b) in ((0, 0), (1, 0), (0, 1)): p[hx_ + a, hy_ + b] = (255, 255, 255, 255)
    return entourer(im, m, trait)

# ---------------- les icônes (taille du dessin en texels ; posées ensuite au centre de leur toile)
def rose_wither():
    W = H = 42; im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); m = masque(W, H)
    vert = P('6a8a3a', '4e6e2a', '36521e'); noir = P('5a3c3c', '3a2626', '241818', '140c0c')
    def f(pts, c): d.polygon(pts, fill=c); ImageDraw.Draw(m).polygon(pts, fill=255)
    f([(20, 18), (23, 18), (23, 41), (20, 41)], vert[1]); f([(20, 18), (21, 18), (21, 41), (20, 41)], vert[0])
    f([(21, 30), (8, 22), (6, 26), (20, 34)], vert[1]); f([(21, 30), (8, 22), (12, 24)], vert[0])
    f([(22, 26), (35, 19), (37, 23), (23, 30)], vert[2]); f([(22, 26), (35, 19), (31, 22)], vert[1])
    f([(12, 4), (31, 4), (34, 12), (27, 19), (16, 19), (9, 12)], noir[2])
    f([(12, 4), (22, 4), (20, 11), (9, 12)], noir[1]); f([(22, 4), (31, 4), (34, 12), (23, 11)], noir[2])
    f([(16, 19), (21, 11), (27, 19)], noir[3]); f([(14, 6), (17, 6), (16, 9)], noir[0])
    return entourer(im, m, hx('0a0606'))
def pierre_partage():
    W = H = 44
    g = P('a8adb6', '8a909a', '6c727c', '50565e'); cy = P('d8ffff', '7ff4f0', '2cc8c4', '128a88')
    im = facettes(W, H, [([(8, 12), (22, 4), (38, 10), (40, 30), (26, 40), (6, 32)], g[2]),
                         ([(8, 12), (22, 4), (24, 18), (10, 22)], g[0]), ([(22, 4), (38, 10), (24, 18)], g[1]),
                         ([(10, 22), (24, 18), (26, 40), (6, 32)], g[2]), ([(24, 18), (38, 10), (40, 30), (26, 40)], g[3])], hx('1c2024'))
    d = ImageDraw.Draw(im)
    for pts in ([(14, 16), (20, 12), (26, 16)], [(18, 24), (24, 28), (30, 22), (34, 26)], [(12, 28), (18, 32)]):
        d.line(pts, fill=cy[2], width=3); d.line(pts, fill=cy[0], width=1)
    return im
def perle_ender():
    im = sphere(36, P('8af0dc', '3cc0aa', '1e8c7c', '146058', '0c3c38'), hx('061c1a'))
    d = ImageDraw.Draw(im); d.ellipse([12, 12, 26, 26], fill=hx('0c3c38')); d.ellipse([15, 15, 23, 23], fill=hx('062624'))
    return im
def oeil_ender():
    im = sphere(36, P('c8f0a0', '8cd07a', '4ea068', '2e7052', '1a4a3a'), hx('0a2018'))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 8, 28, 30], fill=hx('7ae070')); d.ellipse([12, 10, 26, 28], fill=hx('9cf088'))
    d.polygon([(19, 9), (22, 19), (19, 29), (16, 19)], fill=hx('0c2a14'))
    im.putpixel((13, 11), (255, 255, 255, 255)); im.putpixel((14, 11), (255, 255, 255, 255))
    return im
def eclat():
    W, H = 34, 44
    v = P('f0b8ff', 'c060e8', '9a34c8', '6e1c98', '44105e')
    return facettes(W, H, [([(10, 2), (26, 8), (32, 26), (20, 42), (4, 30), (2, 12)], v[2]),
                           ([(10, 2), (26, 8), (16, 20), (2, 12)], v[0]), ([(26, 8), (32, 26), (16, 20)], v[1]),
                           ([(2, 12), (16, 20), (4, 30)], v[2]), ([(16, 20), (32, 26), (20, 42)], v[3]), ([(4, 30), (16, 20), (20, 42)], v[2])], hx('2a0838'))
def cube_iso(haut, gauche, droite, frange=None, motif=None):
    """Bloc vu de trois quarts : trois faces planes, une frange (herbe) qui déborde sur les côtés."""
    W, H = 44, 46; c = 22
    T = [(c, 2), (42, 12), (c, 22), (2, 12)]; L = [(2, 12), (c, 22), (c, 44), (2, 34)]; R = [(c, 22), (42, 12), (42, 34), (c, 44)]
    im = facettes(W, H, [(T, haut), (L, gauche), (R, droite)], hx('141210'))
    d = ImageDraw.Draw(im)
    if frange:
        for x in range(3, 42, 4):
            y = 12 + (x - 2) / 2 if x <= c else 12 + (42 - x) / 2
            d.polygon([(x, y), (x + 4, y + (2 if x < c else -2)), (x + 2, y + 6)], fill=frange)
    if motif:
        for (x, y, col) in motif: d.rectangle([x, y, x + 2, y + 2], fill=col)
    return im
def monde():
    return cube_iso(hx('6cb04a'), hx('8a5c38'), hx('6a4428'), frange=hx('5a9a3c'),
                    motif=[(8, 26, hx('6a4428')), (14, 34, hx('a07048')), (28, 30, hx('543420')), (34, 22, hx('8a5c38')), (16, 8, hx('82c45e')), (28, 12, hx('5a9a3c'))])
def pierre_end():
    return cube_iso(hx('f2f0c0'), hx('d8d49a'), hx('bab678'), motif=[(10, 24, hx('c4c088')), (16, 34, hx('eceab4')), (30, 28, hx('a8a466')), (24, 8, hx('dedca8'))])
def nether():
    return cube_iso(hx('9a3a3a'), hx('7a2a2a'), hx('5a1c1c'), motif=[(8, 24, hx('a84848')), (14, 32, hx('5a1c1c')), (30, 24, hx('8a3434')), (34, 32, hx('461414')), (20, 10, hx('b04a4a'))])
def pioches():
    W = H = 44; im = Image.new('RGBA', (W, H)); m = masque(W, H); d = ImageDraw.Draw(im)
    bois = P('c08a50', '9a6a38', '6e4a24'); fer = P('e6e8ee', 'b8bcc6', '8a909c', '5e6470')
    def ligne(a, b, w, c):
        d.line([a, b], fill=c, width=w); ImageDraw.Draw(m).line([a, b], fill=255, width=w)
    def f(pts, c): d.polygon(pts, fill=c); ImageDraw.Draw(m).polygon(pts, fill=255)
    ligne((8, 40), (34, 14), 5, bois[1]); ligne((8, 39), (33, 14), 2, bois[0])
    ligne((36, 40), (10, 14), 5, bois[2]); ligne((36, 39), (11, 14), 2, bois[1])
    f([(4, 14), (12, 4), (24, 4), (18, 10), (10, 18)], fer[1]); f([(4, 14), (12, 4), (16, 6), (8, 14)], fer[0])   # hache
    f([(22, 6), (30, 2), (40, 6), (44, 18), (36, 10), (30, 8)], fer[1]); f([(30, 2), (40, 6), (36, 8), (30, 5)], fer[0])   # pioche
    f([(28, 8), (34, 6), (36, 12), (32, 14)], fer[3])
    return entourer(im, m, hx('16120e'))
def boussole():
    im = sphere(38, P('f4f6fa', 'd0d4dc', 'a8aeba', '7c8290', '565c68'), hx('1c1e24'), reflet=False)
    d = ImageDraw.Draw(im); d.ellipse([7, 7, 32, 32], fill=hx('f8f4e8')); d.ellipse([8, 8, 31, 31], outline=hx('c8c0a8'))
    for a in range(0, 360, 90):
        x, y = 19.5 + 10 * math.cos(math.radians(a)), 19.5 + 10 * math.sin(math.radians(a)); d.rectangle([x - 1, y - 1, x, y], fill=hx('8a8270'))
    d.polygon([(19, 9), (22, 20), (17, 20)], fill=hx('e03a2a')); d.polygon([(17, 20), (22, 20), (19, 30)], fill=hx('5a5e6a'))
    d.rectangle([18, 19, 20, 21], fill=hx('2a2a30'))
    return im
def livre_plume():
    W, H = 46, 40; im = Image.new('RGBA', (W, H)); m = masque(W, H); d = ImageDraw.Draw(im)
    rouge = P('c0584a', '9a3a30', '742820', '4e1a14'); page = P('fbf7ee', 'e6dfcc', 'c8bea6')
    def f(pts, c): d.polygon(pts, fill=c); ImageDraw.Draw(m).polygon(pts, fill=255)
    f([(2, 18), (24, 10), (44, 18), (22, 30)], rouge[1]); f([(2, 18), (22, 30), (22, 38), (2, 26)], rouge[2]); f([(22, 30), (44, 18), (44, 26), (22, 38)], rouge[3])
    f([(4, 20), (22, 28), (22, 33), (4, 25)], page[1]); f([(22, 28), (42, 20), (42, 25), (22, 33)], page[2])
    f([(2, 18), (24, 10), (26, 12), (5, 19)], rouge[0])
    f([(30, 2), (36, 0), (24, 24), (20, 26)], page[0]); f([(30, 2), (36, 0), (33, 6)], page[1]); d.line([(34, 2), (21, 25)], fill=page[2])
    return entourer(im, m, hx('1e0e0a'))
def crayon():
    W = H = 44; im = Image.new('RGBA', (W, H)); m = masque(W, H); d = ImageDraw.Draw(im)
    def f(pts, c): d.polygon(pts, fill=c); ImageDraw.Draw(m).polygon(pts, fill=255)
    # corps en diagonale (bas-gauche -> haut-droite)
    f([(10, 28), (30, 8), (36, 14), (16, 34)], hx('6ec850')); f([(10, 28), (30, 8), (33, 11), (13, 31)], hx('9ae078'))
    f([(30, 8), (34, 4), (40, 10), (36, 14)], hx('c8ccd6')); f([(34, 4), (37, 1), (43, 7), (40, 10)], hx('e88aa8'))
    f([(10, 28), (16, 34), (4, 40)], hx('e8c890')); f([(6, 36), (8, 38), (3, 41)], hx('3a3a40'))
    return entourer(im, m, hx('14181a'))
def oeil(ouvert=True):
    W, H = 44, 30; im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); m = masque(W, H)
    if ouvert:
        pts = [(2, 15), (12, 5), (22, 3), (32, 5), (42, 15), (32, 25), (22, 27), (12, 25)]
        d.polygon(pts, fill=hx('f4f6f8')); ImageDraw.Draw(m).polygon(pts, fill=255)
        d.ellipse([14, 7, 30, 23], fill=hx('3cb89a')); d.ellipse([17, 10, 27, 20], fill=hx('2a8a74')); d.ellipse([19, 12, 25, 18], fill=hx('0c2420'))
        d.rectangle([18, 10, 19, 11], fill=(255, 255, 255, 255))
        d.line([(12, 5), (22, 3), (32, 5)], fill=hx('8a9aa0'))
        return entourer(im, m, hx('14181a'))
    d.arc([4, -6, 40, 22], 20, 160, fill=hx('3cb89a'), width=4)
    for x in (10, 22, 34): d.line([(x, 20), (x - (x - 22) // 4, 26)], fill=hx('2a8a74'), width=2)
    ImageDraw.Draw(m).arc([4, -6, 40, 22], 20, 160, fill=255, width=4)
    return entourer(im, m, hx('14181a'))
def etoile():
    W = H = 44; c = 22; R, r = 21, 9; faces = []
    pts = [(c + (R if k % 2 == 0 else r) * math.sin(math.pi * k / 5), c + 2 - (R if k % 2 == 0 else r) * math.cos(math.pi * k / 5)) for k in range(10)]
    clair, sombre = hx('ffe27a'), hx('e0a020')
    for k in range(0, 10, 2):
        a, b, g = pts[k], pts[(k + 1) % 10], pts[(k - 1) % 10]
        faces.append(([(c, c + 2), g, a], clair if k in (0, 8) else hx('f8c840'))); faces.append(([(c, c + 2), a, b], hx('f8c840') if k in (0, 8) else sombre))
    return facettes(W, H, faces, hx('5a3a06'))
def cloche():
    W, H = 40, 42; o = P('ffe8a0', 'f0c050', 'd09a30', 'a0701c')
    im = facettes(W, H, [([(14, 6), (26, 6), (30, 30), (36, 34), (4, 34), (10, 30)], o[2]),
                         ([(14, 6), (20, 6), (18, 30), (10, 30)], o[0]), ([(20, 6), (26, 6), (30, 30), (22, 30)], o[1]),
                         ([(4, 34), (36, 34), (36, 37), (4, 37)], o[3]), ([(18, 37), (22, 37), (22, 41), (18, 41)], hx('6a4a1a')),
                         ([(12, 1), (28, 1), (28, 6), (12, 6)], hx('7a5a3a'))], hx('3a2408'))
    return im
def coffre():
    W, H = 44, 38; b = P('d8a050', 'b07a34', '8a5a24', '603c14')
    im = facettes(W, H, [([(2, 4), (42, 4), (42, 16), (2, 16)], b[1]), ([(2, 16), (42, 16), (42, 36), (2, 36)], b[2]),
                         ([(2, 4), (42, 4), (42, 7), (2, 7)], b[0]), ([(2, 15), (42, 15), (42, 18), (2, 18)], b[3]),
                         ([(19, 12), (25, 12), (25, 22), (19, 22)], hx('c8ccd6'))], hx('2a1806'))
    ImageDraw.Draw(im).rectangle([21, 16, 22, 19], fill=hx('3a3e48'))
    return im
def dimension():
    im = sphere(36, P('b48ae8', '8a5ad0', '6438a8', '461e80', '2c0e58'), hx('140628'))
    d = ImageDraw.Draw(im)
    for k in range(3):
        a0 = k * 120; pts = []
        for t in range(12):
            a = math.radians(a0 + t * 18); rr = 4 + t * 1.1; pts.append((19 + rr * math.cos(a), 19 + rr * math.sin(a)))
        d.line(pts, fill=hx('d8c0ff'), width=2)
    return im
def carte():
    W, H = 44, 40; im = Image.new('RGBA', (W, H)); m = masque(W, H); d = ImageDraw.Draw(im)
    pts = [(4, 6), (16, 2), (28, 6), (40, 2), (40, 34), (28, 38), (16, 34), (4, 38)]
    d.polygon(pts, fill=hx('ecdcb0')); ImageDraw.Draw(m).polygon(pts, fill=255)
    d.polygon([(16, 2), (28, 6), (28, 38), (16, 34)], fill=hx('d8c494'))
    d.line([(8, 30), (14, 20), (22, 24), (30, 14), (36, 12)], fill=hx('c0402a'), width=2)
    d.line([(32, 9), (37, 15)], fill=hx('c0402a'), width=2); d.line([(37, 9), (32, 15)], fill=hx('c0402a'), width=2)
    return entourer(im, m, hx('3a2a14'))
