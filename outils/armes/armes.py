import math
from PIL import Image, ImageDraw, ImageFont
N1, N2, N3 = (34,28,38), (52,45,56), (82,72,88)
O1, O2, O3 = (176,138,58), (226,186,96), (255,224,140)
B1, B2, B3 = (196,200,214), (226,229,238), (252,253,255)
K = (14,10,16); ET = (235,248,255); ET2 = (160,215,255); RG, RG2 = (150,28,34), (100,18,24); CUIR = (70,46,30)

def vide(n): return Image.new('RGBA', (n, n), (0,0,0,0))
def px(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height: im.putpixel((int(x), int(y)), c + (255,))

def lame(im, a, b, larg, f):
    """Segment de a à b ; larg(t) demi-largeur ; f(t, s) couleur (t 0..1 le long, s -1..1 en travers)."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    for x in range(im.width):
        for y in range(im.height):
            dx, dy = x + .5 - x0, y + .5 - y0
            t = (dx * ux + dy * uy) / L; s = dx * -uy + dy * ux
            if 0 <= t <= 1:
                w = larg(t)
                if w > 0 and abs(s) <= w: px(im, x, y, f(t, s / w))

def contour(im):
    a = im.copy()
    for x in range(im.width):
        for y in range(im.height):
            if a.getpixel((x, y))[3] == 0 and any(0 <= x+dx < im.width and 0 <= y+dy < im.height and a.getpixel((x+dx, y+dy))[3] > 0
                                                   for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                im.putpixel((x, y), K + (255,))
    return im

def etoile(im, cx, cy):
    for (dx, dy, c) in ((0,0,ET),(1,0,ET2),(-1,0,ET2),(0,1,ET2),(0,-1,ET2)): px(im, cx+dx, cy+dy, c)

# ------------------------------------------------------------------ épée (16)
def epee(imp):
    im = vide(16)
    bl = (lambda t, s: O3 if s < -0.67 else (B3 if s < 0.1 else B2)) if imp else (lambda t, s: O2 if s < -0.67 else (N3 if s < 0.1 else N2))
    lame(im, (5.5, 10.5), (14.5, 1.5), lambda t: 1.5 if t < .85 else 1.5 * (1 - t) / .15 + .3, bl)
    lame(im, (2.5, 9.5), (6.5, 13.5), lambda t: 0.8, lambda t, s: O2 if abs(s) < .5 else O1)          # garde
    lame(im, (1.5, 14.5), (4.5, 11.5), lambda t: 0.7, lambda t, s: (RG if imp and int(t * 6) % 2 else (N1 if not imp else RG2)))
    px(im, 1, 14, O3 if imp else O2)
    if imp: etoile(im, 4.6, 11.4)
    return contour(im)

# ------------------------------------------------------------------ katana (32) : lame fine et courbe, tsuba ronde, tsuka tressée
def katana(imp):
    im = vide(32)
    def courbe(t): return (8 + t * 22, 23 - t * 21 + t * t * 2.5 - 1.2 * t)
    for i in range(160):
        t = i / 160; x, y = courbe(t); w = 1.4 if t < .8 else max(0.3, 1.4 * (1 - t) / .2)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if math.hypot(dx, dy) <= w:
                    edge = dy > 0.3   # tranchant en bas
                    c = (O3 if imp else O2) if (dy <= -1) else ((B3 if imp else N3) if edge else (B2 if imp else N2))
                    if not imp and dy == 0 and int(t * 12) % 3 == 0: c = O1     # hamon d'or
                    if imp and dy == 0 and int(t * 14) % 4 == 0: c = (232, 240, 255)
                    px(im, x + dx, y + dy, c)
    for a in range(0, 360, 10):       # tsuba
        for r in (2.2, 3.0):
            x, y = 7.5 + r * math.cos(math.radians(a)), 23.5 + r * math.sin(math.radians(a))
            px(im, x, y, (N1 if r < 2.5 else (O2 if imp or a % 40 else O1)))
    px(im, 7, 23, N1); px(im, 8, 23, N1); px(im, 7, 24, N1)
    if imp: etoile(im, 7.5, 23.5)
    lame(im, (1.5, 30.5), (6.2, 25.8), lambda t: 1.1, lambda t, s: ((RG if (int(t * 9) + (s > 0)) % 2 else O2) if imp else ((N1 if (int(t * 9) + (s > 0)) % 2 else N3))))
    px(im, 1, 30, O2); px(im, 2, 30, O2); px(im, 1, 29, O2)
    return contour(im)

# ------------------------------------------------------------------ espadon (32) : lame large, gouttière, grande garde
def espadon(imp):
    im = vide(32)
    def bl(t, s):
        if abs(s) < 0.22: return N1 if imp else O1         # gouttière
        if abs(s) > 0.75: return O3 if imp else O2         # filets
        return (B3 if s < 0 else B2) if imp else (N3 if s < 0 else N2)
    lame(im, (9.5, 22.5), (29.5, 2.5), lambda t: 2.6 if t < .86 else 2.6 * (1 - t) / .14 + .3, bl)
    lame(im, (4.5, 18), (13.5, 27), lambda t: 1.1 + .4 * abs(t - .5), lambda t, s: O2 if abs(s) < .5 else O1)   # garde
    for (x, y) in ((4, 17), (3, 16), (13, 28), (14, 29)): px(im, x, y, O2)
    lame(im, (3.5, 28.5), (8.6, 23.4), lambda t: 1.0, lambda t, s: (RG if int(t * 7) % 2 else RG2) if imp else (N1 if int(t * 7) % 2 else CUIR))
    lame(im, (1.5, 30.5), (3.6, 28.4), lambda t: 1.3, lambda t, s: O2)
    if imp: etoile(im, 9, 23)
    return contour(im)

# ------------------------------------------------------------------ twinblade (32) : deux lames, poignée centrale
def twinblade(imp):
    im = vide(32)
    def bl(t, s): return (O3 if imp else O2) if s < -0.45 else ((B3 if s < .2 else B2) if imp else (N3 if s < .2 else N2))
    lame(im, (18.5, 13.5), (30, 2), lambda t: 1.8 * (1 - t) + .4 if t > .6 else 1.8, bl)
    lame(im, (13.5, 18.5), (2, 30), lambda t: 1.8 * (1 - t) + .4 if t > .6 else 1.8, lambda t, s: bl(t, -s))
    lame(im, (12.5, 19.5), (19.5, 12.5), lambda t: 1.1, lambda t, s: (RG if int(t * 8) % 2 else O2) if imp else (N1 if int(t * 8) % 2 else O1))
    for c in ((12, 17), (19, 14)):
        lame(im, (c[0] - 2, c[1] - 2), (c[0] + 2, c[1] + 2), lambda t: .8, lambda t, s: O2)
    if imp: etoile(im, 16, 16)
    return contour(im)

# ------------------------------------------------------------------ pioche (16)
def pioche(imp):
    im = vide(16)
    lame(im, (1.5, 14.5), (10.5, 5.5), lambda t: .8, lambda t, s: (RG if imp and t < .4 and int(t * 12) % 2 else (CUIR if not imp else N2)))
    def tete(t, s):
        if t < .14 or t > .86: return N1 if imp else O2
        return (B3 if s < 0 else B2) if imp else (N3 if s < 0 else N2)
    # tête perpendiculaire au manche, légèrement arquée vers le bas, pointes effilées
    r2 = math.sqrt(.5)
    for i in range(80):
        u = -6 + 12 * i / 80; t = (u + 6) / 12
        bomb = 1.8 * (1 - (u / 6) ** 2)
        x = 10.5 + u * r2 + bomb * r2; y = 5.5 + u * r2 - bomb * r2
        w = 1.3 if abs(u) < 3.5 else 0.8
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if math.hypot(dx, dy) <= w: px(im, x + dx, y + dy, tete(t, -1 if dx - dy < 0 else 1))
    lame(im, (9.4, 4.6), (11.6, 6.8), lambda t: 1.3, lambda t, s: O2)
    if imp: etoile(im, 10, 6)
    return contour(im)

ARMES = [("Épée", epee), ("Katana", katana), ("Espadon", espadon), ("Twinblade", twinblade), ("Pioche", pioche)]
if __name__ == '__main__':
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; f = ImageFont.truetype(FB, 17)
    C = 150
    out = Image.new('RGB', (len(ARMES) * (C + 20) + 150, 2 * (C + 20) + 60), (32,33,38)); d = ImageDraw.Draw(out)
    for i, (n, fn) in enumerate(ARMES):
        for j, imp in enumerate((False, True)):
            im = fn(imp); g = im.resize((C if im.width == 32 else C * 16 // 32 * 2 // 2 * 1, ) * 2, Image.NEAREST) if False else im.resize((C, C) if im.width == 32 else (C // 2 * 1 + 0, C // 2 * 1 + 0), Image.NEAREST)
            if im.width == 16: g = im.resize((96, 96), Image.NEAREST)
            X = 140 + i * (C + 20) + (C - g.width) // 2; Y = 40 + j * (C + 20) + (C - g.height) // 2
            out.paste(g, (X, Y), g)
        d.text((140 + i * (C + 20) + C // 2 - d.textlength(n, font=f) / 2, 10), n, fill=(240,205,120), font=f)
    d.text((10, 40 + C // 2), "Sacré", fill=(240,205,120), font=f); d.text((10, 40 + C + 20 + C // 2), "Impérial", fill=(240,205,120), font=f)
    d.text((10, out.height - 30), "Épée et pioche à la taille vanilla ; katana, espadon et twinblade en grand, comme Simply Swords.", fill=(170,170,170), font=ImageFont.truetype(FB, 14))
    out.save('apercu_armes.png'); print(out.size)
