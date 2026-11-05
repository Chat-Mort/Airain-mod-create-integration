"""Icônes 16x16 des armures sacrée et impériale : silhouettes façon vanilla, ombrage à trois tons, détails d'or."""
from PIL import Image, ImageDraw, ImageFont
K = (18, 14, 22)
N1, N2, N3, N4 = (34,28,40), (54,47,62), (80,72,90), (108,98,120)
O1, O2, O3 = (168,126,46), (222,180,84), (255,226,140)
B1, B2, B3 = (186,190,206), (224,227,238), (252,253,255)
ET, ET2, RG, RG2, VER = (240,250,255), (150,212,255), (150,30,36), (104,20,26), (150,210,230)

MASQUES = {
 'plastron': ["................",
              ".####......####.",
              "######....######",
              "######....######",
              "################",
              ".##############.",
              "..############..",
              "...##########...",
              "...##########...",
              "...##########...",
              "...##########...",
              "...##########...",
              "...##########...",
              "....########....",
              "................",
              "................"],
 'jambieres': ["................",
               "...##########...",
               "...##########...",
               "...##########...",
               "...####..####...",
               "...####..####...",
               "...####..####...",
               "...####..####...",
               "...####..####...",
               "...####..####...",
               "...####..####...",
               "...####..####...",
               "...####..####...",
               "................",
               "................",
               "................"],
 'bottes': ["................",
            "................",
            "................",
            "................",
            "..####....####..",
            "..####....####..",
            "..####....####..",
            "..####....####..",
            "..####....####..",
            ".#####...#####..",
            "######..######..",
            "######..######..",
            "................",
            "................",
            "................",
            "................"],
 'casque': ["................",
            "................",
            "................",
            "...##########...",
            "..############..",
            "..############..",
            "..############..",
            "..####....####..",
            "..###......###..",
            "..###......###..",
            "................",
            "................",
            "................",
            "................",
            "................",
            "................"],
}

def masque(nom):
    m = MASQUES[nom]
    return lambda x, y: 0 <= x < 16 and 0 <= y < 16 and m[y][x] == '#'

def ombrer(dedans, x, y, clair, moyen, sombre, reflet=None):
    """Bords haut/gauche éclairés, bas/droite dans l'ombre ; reflet diagonal optionnel."""
    if not dedans(x, y - 1) or not dedans(x - 1, y): return clair
    if not dedans(x, y + 1) or not dedans(x + 1, y): return sombre
    if reflet and (x - y) % 7 == 0: return reflet
    return moyen

def piece(nom, detail):
    im = Image.new('RGBA', (16, 16), (0,0,0,0)); d = masque(nom)
    for x in range(16):
        for y in range(16):
            if d(x, y):
                c = detail(x, y, d)
                if c: im.putpixel((x, y), c + (255,))
    for x in range(16):                                   # contour
        for y in range(16):
            if not d(x, y) and im.getpixel((x, y))[3] == 0 and any(d(x+a, y+b) for a, b in ((1,0),(-1,0),(0,1),(0,-1))):
                im.putpixel((x, y), K + (255,))
    return im

def ajouter(im, pts, c):
    for (x, y) in pts: im.putpixel((x, y), c + (255,))
    return im

def etoile(im, x, y):
    return ajouter(ajouter(im, [(x, y)], ET), [(x-1, y), (x+1, y), (x, y-1), (x, y+1)], ET2)

# ------------------------------------------------------------------------- sacrée : netherite, filets d'or
def plastron_sacre():
    def f(x, y, d):
        if y <= 3 and (x <= 5 or x >= 10): return O3 if y == 1 or (y == 2 and x in (0, 15)) else (O2 if y == 2 else O1)   # épaulières d'or
        if x in (7, 8) and y >= 5: return O3 if x == 7 else O2       # bande centrale
        if y == 12: return O2 if x != 12 else O1                     # bord bas
        if y == 9 and 3 <= x <= 12: return O1
        return ombrer(d, x, y, N4, N2, N1)
    return piece('plastron', f)

def jambieres_sacrees():
    def f(x, y, d):
        if y == 1: return O3 if x < 8 else O2                         # ceinture
        if y == 2: return O1
        if y in (7, 8) and x in (4, 5, 10, 11): return O2 if y == 7 else O1   # genouillères
        return ombrer(d, x, y, N4, N2, N1)
    return piece('jambieres', f)

def bottes_sacrees():
    def f(x, y, d):
        if y == 4: return O3 if x in (2, 3, 10, 11) else O2           # revers d'or
        if y == 11: return N1                                         # semelle
        if y == 10 and x in (0, 1, 8, 9): return O2                   # bout ferré
        return ombrer(d, x, y, N4, N2, N1)
    return piece('bottes', f)

# ------------------------------------------------------------------------- impériale : nacre, flancs noirs, or, étoile, cape
def plastron_imperial():
    def f(x, y, d):
        if y <= 3 and (x <= 5 or x >= 10): return O3 if y == 1 else (B3 if y == 2 else O2)   # grandes épaulières
        if y >= 5 and x in (3, 12): return N2 if x == 3 else N1        # flancs de netherite
        if y == 12: return O2
        if y == 4: return O1
        return ombrer(d, x, y, B3, B2, B1, (255,255,255))
    im = piece('plastron', f)
    ajouter(im, [(6, 6), (9, 6), (6, 8), (9, 8), (7, 5), (8, 9)], O2)     # serti d'or
    etoile(im, 7, 7); ajouter(im, [(8, 7)], ET); ajouter(im, [(8, 8), (7, 8)], ET2)
    ajouter(im, [(2, 8), (2, 9), (2, 10), (2, 11), (13, 8), (13, 9), (13, 10), (13, 11)], RG)   # cape, derrière
    ajouter(im, [(2, 12), (13, 12)], RG2)
    return im

def jambieres_imperiales():
    def f(x, y, d):
        if y == 1: return O3 if x < 8 else O2
        if y == 2: return O1
        if x in (3, 12): return N2 if x == 3 else N1                   # flancs noirs
        if y == 7 and x in (5, 10): return O3                          # rivets de genou
        if y == 7 and x in (4, 6, 9, 11): return O2
        return ombrer(d, x, y, B3, B2, B1, (255,255,255))
    return piece('jambieres', f)

def bottes_imperiales():
    def f(x, y, d):
        if y == 4: return O3 if x in (2, 3, 10, 11) else O2
        if y == 11: return N1
        if y == 10 and x in (0, 1, 8, 9): return O2
        if x in (5, 13) and y < 10: return N2                          # flanc noir
        return ombrer(d, x, y, B3, B2, B1, (255,255,255))
    return piece('bottes', f)

def casque_imperial():
    """Même silhouette que le casque couronné : nacre, couronne aux pointes d'or, bandeau d'or, étoile, joues noires."""
    o = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/casque_couronne.png').convert('RGBA')
    po = o.load(); im = Image.new('RGBA', (16, 16), (0,0,0,0)); px = im.load()
    pts = [(x, y) for x in range(16) for y in range(16) if po[x, y][3]]
    haut = min(y for _, y in pts); xs = [x for x, _ in pts]; gx, dx = min(xs), max(xs)
    bande = {y for (x, y) in pts if po[x, y][0] > 120 and po[x, y][1] < 90}
    for (x, y) in pts:
        r, g, b, a = po[x, y]; l = (r + g + b) / 3
        if l < 30: px[x, y] = K + (255,); continue                     # contour et ouverture
        if y in bande: c = O3 if x % 3 == 0 else O2
        elif y < min(bande) and (y == 0 or po[x, y - 1][3] == 0 or sum(po[x, y - 1][:3]) / 3 < 30): c = O3   # pointes d'or
        elif x in (gx + 1, dx - 1) and y > max(bande): c = N2          # joues de netherite
        else: c = B3 if l > 95 else (B2 if l > 70 else B1)
        px[x, y] = c + (255,)
    for y in bande:
        cx = [x for (x, yy) in pts if yy == y and po[x, y][0] > 120 and po[x, y][1] < 90]
        if cx: etoile(im, sum(cx) // len(cx), y)
    return im

ICONES = [("plastron_sacre", plastron_sacre), ("jambieres_sacrees", jambieres_sacrees), ("bottes_sacrees", bottes_sacrees),
          ("casque_imperial", casque_imperial), ("plastron_imperial", plastron_imperial), ("jambieres_imperiales", jambieres_imperiales),
          ("bottes_imperiales", bottes_imperiales)]

if __name__ == '__main__':
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; f = ImageFont.truetype(FB, 15)
    casque_sacre = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/casque_couronne_sacree.png').convert('RGBA')
    lignes = [[("Casque couronné sacré", casque_sacre)] + [(n, fn()) for n, fn in ICONES[:3]], [(n, fn()) for n, fn in ICONES[3:]]]
    Z = 9; C = 16 * Z
    out = Image.new('RGB', (4 * (C + 40) + 130, 2 * (C + 50) + 20), (31, 32, 36)); d = ImageDraw.Draw(out)
    for j, l in enumerate(lignes):
        d.text((10, 20 + j * (C + 50) + C // 2), ("Sacrée", "Impériale")[j], fill=(240, 205, 120), font=f)
        for i, (n, im) in enumerate(l):
            g = im.resize((C, C), Image.NEAREST); X = 120 + i * (C + 40); Y = 15 + j * (C + 50)
            out.paste(g, (X, Y), g)
            t = n.replace('_', ' '); d.text((X + C // 2 - d.textlength(t, font=f) / 2, Y + C + 6), t, fill=(200, 200, 200), font=f)
    out.save('apercu_icones_armures.png'); print(out.size)
