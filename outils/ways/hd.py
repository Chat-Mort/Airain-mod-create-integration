# Boîte à outils des sprites d'interface HD (3x) : palettes du pack, biseaux tirés d'un masque, plaques, chiffres.
# Tout se dessine en texels (1 px d'interface = 3 texels). Lumière en haut à gauche, contour sombre d'un texel.
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
S = 3
def hx(h, a=255): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)
# palettes relevées sur les sprites HD existants (case à cocher, barre d'outils, boutons)
OR = dict(clair=hx('f3d694'), base=hx('e1ba6e'), mi=hx('b48242'), sombre=hx('a8763c'), trait=hx('704425'))
ROUGE = dict(clair=hx('e06060'), base=hx('c04343'), mi=hx('af1d25'), sombre=hx('8a0018'), trait=hx('520019'))
# familles d'interface (décisions GUI) : fours et machines en airain exposé, outils d'atelier en airain patiné
EXPOSE = dict(clair=hx('ebb681'), base=hx('da955b'), mi=hx('ae5e33'), sombre=hx('a1532d'), trait=hx('6a2c1c'))
PATINE = dict(clair=hx('da8367'), base=hx('c85b40'), mi=hx('9c261c'), sombre=hx('931f19'), trait=hx('610f13'))
GRIS = dict(clair=hx('bdb8aa'), base=hx('a29d90'), mi=hx('87826f'), sombre=hx('6c6857'), trait=hx('2f2d27'))
BLANC = dict(clair=hx('ffffff'), base=hx('f4f2ec'), mi=hx('d8d4ca'), sombre=hx('b8b3a6'), trait=hx('3a3630'))
ARD = dict(survol=hx('434855'), clair=hx('4b5160'), base=hx('363a44'), fond=hx('2a2e37'), creux=hx('23262d'), noir=hx('1b1e24'), puits=hx('15171b'), abime=hx('0e0f12'))
ROUGE_VIF = dict(clair=hx('ff8a7a'), base=hx('e8402f'), mi=hx('c42a22'), sombre=hx('8e1a16'), trait=hx('4a0c0a'))
VERT = dict(clair=hx('b9f0a0'), base=hx('6cc456'), mi=hx('4a9a3c'), sombre=hx('336e2a'), trait=hx('15301a'))
CYAN = dict(clair=hx('c8f4ff'), base=hx('7fd8f0'), mi=hx('4aa8cc'), sombre=hx('2e7898'), trait=hx('103444'))

def toile(w, h): return Image.new('RGBA', (w * S, h * S))
def masque(w, h): return Image.new('L', (w, h), 0)
def dedans(m, x, y): return 0 <= x < m.width and 0 <= y < m.height and m.getpixel((x, y)) > 127

def biseau(m, pal, contour=True, epais=1, plat=False):
    """Matière en relief tirée d'un masque (en texels) : arête claire en haut/gauche, sombre en bas/droite, contour d'un texel."""
    w, h = m.size; im = Image.new('RGBA', (w, h)); p = im.load(); q = m.load()
    def ins(x, y): return 0 <= x < w and 0 <= y < h and q[x, y] > 127
    for y in range(h):
        for x in range(w):
            if ins(x, y):
                c = pal['base']
                if not plat:
                    haut = any(not ins(x, y - k) or not ins(x - k, y) for k in range(1, epais + 1))
                    bas = any(not ins(x, y + k) or not ins(x + k, y) for k in range(1, epais + 1))
                    if haut and not bas: c = pal['clair']
                    elif bas and not haut: c = pal['mi']
                    elif haut and bas: c = pal['base']
                p[x, y] = c
            elif contour and any(ins(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))):
                p[x, y] = pal['trait']
    return im

def metal(m, pal, contour=True, facettes=None):
    """Métal en volume : dégradé vertical (clair en haut, sombre en bas) dans le masque, arêtes claires en haut/gauche,
    sombres en bas/droite, contour d'un texel. facettes(x, y) -> +1 (plus clair) / -1 (plus sombre) / 0 pour tailler des faces."""
    w, h = m.size; im = Image.new('RGBA', (w, h)); p = im.load(); q = m.load()
    bb = m.getbbox()
    if not bb: return im
    y0, y1 = bb[1], bb[3]
    rampe = [pal['clair'], pal['base'], pal['base'], pal['mi'], pal['sombre']]
    def ins(x, y): return 0 <= x < w and 0 <= y < h and q[x, y] > 127
    for y in range(h):
        for x in range(w):
            if ins(x, y):
                i = min(4, int((y - y0) / max(1, y1 - y0) * 5))
                if facettes: i -= facettes(x, y)
                if not ins(x, y - 1) or not ins(x - 1, y): i -= 1
                if not ins(x, y + 1) or not ins(x + 1, y): i += 2
                p[x, y] = rampe[max(0, min(4, i))]
            elif contour and any(ins(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))):
                p[x, y] = pal['trait']
    return im
def rivet(im, x, y, pal):
    """Rivet de 3 x 3 texels : point clair en haut à gauche, ombre en bas à droite."""
    for (dx, dy, c) in ((0, 0, 'clair'), (1, 0, 'base'), (0, 1, 'base'), (1, 1, 'mi'), (2, 1, 'trait'), (1, 2, 'trait'), (2, 2, 'trait')):
        im.putpixel((x + dx, y + dy), pal[c])

def rect(m, x0, y0, x1, y1, v=255): ImageDraw.Draw(m).rectangle([x0, y0, x1 - 1, y1 - 1], fill=v)
def poly(m, pts, v=255): ImageDraw.Draw(m).polygon(pts, fill=v)
def ellipse(m, x0, y0, x1, y1, v=255): ImageDraw.Draw(m).ellipse([x0, y0, x1 - 1, y1 - 1], fill=v)
def trait(m, pts, w, v=255): ImageDraw.Draw(m).line(pts, fill=v, width=w, joint='curve')

def plaque(w, h, cadre=OR, fond=ARD['fond'], ep=3, coin=2, rivets=False):
    """Plaque d'ardoise (w x h px d'interface) dans un cadre d'airain biseauté de ep texels."""
    W, H = w * S, h * S
    ext = masque(W, H); rect(ext, 1, 1, W - 1, H - 1)
    # coins chanfreinés
    d = ImageDraw.Draw(ext)
    for (cx, cy, sx, sy) in ((1, 1, 1, 1), (W - 2, 1, -1, 1), (1, H - 2, 1, -1), (W - 2, H - 2, -1, -1)):
        for k in range(coin):
            for j in range(coin - k): ext.putpixel((cx + sx * j, cy + sy * k), 0)
    inner = masque(W, H); rect(inner, 1 + ep, 1 + ep, W - 1 - ep, H - 1 - ep)
    anneau = ImageChops.subtract(ext, inner)
    im = biseau(anneau, cadre)
    # fond : ardoise, ombre portée du cadre en haut/gauche
    f = Image.new('RGBA', (W, H)); fp = f.load()
    for y in range(1 + ep, H - 1 - ep):
        for x in range(1 + ep, W - 1 - ep):
            c = fond
            if y == 1 + ep or x == 1 + ep: c = mix(fond, (0, 0, 0, 255), .35)
            elif y == 2 + ep or x == 2 + ep: c = mix(fond, (0, 0, 0, 255), .15)
            fp[x, y] = c
    f.alpha_composite(im)
    if rivets:
        for (x, y) in ((ep + 4, ep + 4), (W - ep - 6, ep + 4), (ep + 4, H - ep - 6), (W - ep - 6, H - ep - 6)):
            f.putpixel((x, y), cadre['clair']); f.putpixel((x + 1, y + 1), cadre['trait']); f.putpixel((x + 1, y), cadre['base']); f.putpixel((x, y + 1), cadre['mi'])
    return f

def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (a[3] if len(a) > 3 else 255,)
def colle(fond, im, x=0, y=0): fond.alpha_composite(im, (int(x), int(y))); return fond
def centre(fond, im): return colle(fond, im, (fond.width - im.width) // 2, (fond.height - im.height) // 2)

POLICE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def texte_masque(t, taille, w=None, h=None):
    f = ImageFont.truetype(POLICE, taille); bb = f.getbbox(t)
    m = Image.new('L', (bb[2] - bb[0] + 2, bb[3] - bb[1] + 2)); ImageDraw.Draw(m).text((1 - bb[0], 1 - bb[1]), t, font=f, fill=255)
    return m.point(lambda v: 255 if v > 120 else 0)
