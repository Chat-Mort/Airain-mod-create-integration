"""Icônes 32x32 des armes sacrées / impériales, dans l'esprit de Simply Swords : fines, en diagonale, contour sombre, gemmes."""
from PIL import Image, ImageDraw, ImageFont
K = (16, 12, 20)
S = dict(  # sacré : netherite noire, or
    l0=(30,25,36), l1=(52,45,60), l2=(78,70,90), l3=(120,110,134), f1=(150,112,40), f2=(214,170,70), f3=(255,222,130),
    g0=(28,22,32), g1=(60,40,30), g2=(90,62,40), j1=(110,170,220), j2=(200,235,255))
I = dict(  # impérial : nacre blanche, netherite, or, rouge, étoile
    l0=(150,154,172), l1=(200,204,220), l2=(232,235,244), l3=(255,255,255), f1=(170,130,50), f2=(228,188,96), f3=(255,228,150),
    g0=(30,24,34), g1=(130,26,32), g2=(190,48,48), j1=(150,215,255), j2=(240,250,255))
N = dict(n0=(26,21,30), n1=(48,41,54), n2=(74,66,82))

class Icone:
    def __init__(s): s.im = Image.new('RGBA', (32, 32), (0,0,0,0))
    def p(s, x, y, c):
        if 0 <= x < 32 and 0 <= y < 32 and c: s.im.putpixel((x, y), c + (255,))
    def uv(s, f):
        """f(u, v) -> couleur ; u = x - y (le long de la diagonale), v = x + y (en travers)."""
        for x in range(32):
            for y in range(32):
                c = f(x - y, x + y)
                if c: s.p(x, y, c)
    def contour(s):
        a = s.im.copy()
        for x in range(32):
            for y in range(32):
                if a.getpixel((x, y))[3] == 0 and any(0 <= x+dx < 32 and 0 <= y+dy < 32 and a.getpixel((x+dx, y+dy))[3] > 0
                                                       for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                    s.im.putpixel((x, y), K + (255,))
        return s.im

def lame3(P, u, v, c, u0, u1, pointe=4, larg=1):
    """Lame à trois tons : bord haut (v < c) clair, cœur, bord bas sombre ; pointe effilée sur les `pointe` derniers pas."""
    if not (u0 <= u <= u1): return None
    w = larg if u <= u1 - pointe else max(0, larg * (u1 - u) / pointe)
    d = v - c
    if abs(d) > w + 0.01: return None
    if d < -0.5: return P['l3']
    if d > 0.5: return P['l0']
    return P['l2'] if u % 7 else P['l1']

def etoile(ic, x, y, P):
    for (dx, dy, k) in ((0,0,'j2'),(1,0,'j1'),(-1,0,'j1'),(0,1,'j1'),(0,-1,'j1')): ic.p(x+dx, y+dy, P[k])

# ------------------------------------------------------------------------- épée longue
def epee(P):
    ic = Icone()
    def f(u, v):
        c = lame3(P, u, v, 31, -4, 26, 5, 1.5)
        if c:
            if v == 31 and 0 <= u <= 22 and u % 3 == 0: return P['f2']        # filet d'or au cœur
            return c
        if -7 <= u <= -5 and abs(v - 31) <= 6:                               # garde à cornes
            return P['f3'] if u == -5 else P['f2'] if abs(v - 31) < 5 else P['f1']
        if (u in (-4, -3) and abs(v - 31) in (6, 7)) or (u in (-2,) and abs(v - 31) == 7): return P['f2']   # cornes vers la lame
        if -18 <= u <= -8 and abs(v - 31) <= 1: return P['g2'] if (u + (v > 31)) % 3 == 0 else P['g1']    # fusée tressée
        if -21 <= u <= -19 and abs(v - 31) <= 2: return P['f2'] if abs(v - 31) == 2 or u == -19 else P['f1']
        return None
    ic.uv(f); etoile(ic, 12, 19, P)                                            # gemme au centre de la garde
    return ic.contour()

# ------------------------------------------------------------------------- katana : lame fine et courbe, tsuba, tsuka tressée
def katana(P, rouge):
    ic = Icone()
    def f(u, v):
        if -5 <= u <= 27:
            c = 31 - (1 if u > 19 else 0) - (1 if u > 24 else 0)                # presque droit, la pointe remonte
            w = 1 if u <= 22 else (0.5 if u <= 25 else 0)
            d = v - c
            if abs(d) <= w + .01:
                if d < -0.5: return P['f2'] if P is S else P['l3']            # dos
                if d > 0.5: return P['l3'] if P is S else P['l1']             # tranchant
                return P['l2'] if u % 9 else P['f2']                          # hamon
        if -7 <= u <= -6 and abs(v - 31) <= 2: return P['f2'] if u == -6 else P['f1']   # tsuba plate
        if -21 <= u <= -8 and abs(v - 31) <= 1:                               # tsuka
            losange = (u + abs(v - 31)) % 3 == 0                                # tressage en losanges
            if rouge: return P['l3'] if losange else P['g1']
            return P['f2'] if losange else P['g0']
        if -23 <= u <= -22 and abs(v - 31) <= 1: return P['f2']              # kashira
        return None
    ic.uv(f)
    return ic.contour()

# ------------------------------------------------------------------------- espadon : lame large, gouttière, longue garde droite
def espadon(P):
    ic = Icone()
    def f(u, v):
        if -3 <= u <= 27:
            w = 2 if u <= 21 else max(0, 2 * (27 - u) / 6)
            d = v - 31
            if abs(d) <= w + .01:
                if d == 0 and u <= 20: return P['f1'] if P is S else N['n1']   # gouttière
                if d <= -2: return P['f3'] if P is S else P['l3']
                if d < 0: return P['l3'] if P is S else P['l2']
                if d >= 2: return P['l0']
                return P['l1']
        if -5 <= u <= -4 and abs(v - 31) <= 8:                                 # garde
            if abs(v - 31) >= 7: return P['f3']
            return P['f2'] if u == -4 else P['f1']
        if -15 <= u <= -6 and abs(v - 31) <= 1: return P['g2'] if u % 3 == 0 else P['g1']
        if -18 <= u <= -16 and abs(v - 31) <= 2: return P['f2'] if abs(v - 31) < 2 else P['f1']
        return None
    ic.uv(f); etoile(ic, 13, 18, P)
    return ic.contour()

# ------------------------------------------------------------------------- twinblade : manche long, deux lames
def twinblade(P):
    ic = Icone()
    def f(u, v):
        d = v - 31
        for sgn in (1, -1):
            uu = u * sgn
            if 11 <= uu <= 27:
                w = 1.5 if uu <= 22 else max(0, 1.5 * (27 - uu) / 5)
                dd = d * sgn
                if abs(dd) <= w + .01:
                    if dd < -0.5: return P['l3']
                    if dd > 0.5: return P['l0']
                    return P['f2'] if uu in (14, 18) else P['l2']
            if uu == 10 and abs(d) <= 1: return P['f1']                         # bague
            if uu in (8, 9) and abs(d) <= 2: return P['f3'] if uu == 9 else P['f1']  # petite garde
        if -7 <= u <= 7 and abs(d) <= 0.5: return P['g2'] if u % 4 == 0 else (P['g1'] if P is I else N['n2'])
        if -7 <= u <= 7 and abs(d) == 1 and u % 4 == 2: return P['f2']        # bagues
        return None
    ic.uv(f); etoile(ic, 16, 15, P)
    return ic.contour()

# ------------------------------------------------------------------------- pioche : grande tête arquée, gemme, manche serti
def pioche(P):
    ic = Icone()
    V0 = 32                                       # axe du manche (un cran plus bas que les lames)
    def f(u, v):
        t = v - V0
        if abs(t) <= 15:                          # tête : arquée vers le manche aux extrémités, pointes fines
            centre = 15 - round((t / 15) ** 2 * 7)
            ep = 2 if abs(t) <= 4 else (1 if abs(t) <= 9 else 0)
            dans = abs(u - centre) <= ep if ep else (u - centre) in (0, 1)   # pointe : un seul pixel par rang
            if dans:
                if abs(t) >= 13: return P['f3']   # pointes d'or
                if u - centre >= 1: return P['l3'] if P is I else N['n2']
                if u - centre <= -1: return P['l1'] if P is I else N['n0']
                return P['l2'] if P is I else N['n1']
        if -15 <= u <= -13 and abs(t) <= (u + 15) * 0.5: return P['f3'] if u == -15 else P['f2']   # pointe d'or du manche
        if -12 <= u <= 12 and abs(t) <= 1:
            if t == 0 and u % 5 == 0 and u < 10: return P['j1']    # sertis
            return N['n1'] if t != 1 else N['n0']
        return None
    ic.uv(f)
    x, y = (15 + V0) // 2, (V0 - 15) // 2         # gemme au cœur de la tête
    for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1)): ic.p(x + dx, y + dy, P['f2'])
    etoile(ic, x, y, P)
    return ic.contour()

ARMES = [("Épée", epee), ("Katana", lambda P: katana(P, P is I)), ("Espadon", espadon), ("Twinblade", twinblade), ("Pioche", pioche)]
if __name__ == '__main__':
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; f = ImageFont.truetype(FB, 17)
    Z = 5; C = 32 * Z
    out = Image.new('RGB', (110 + len(ARMES) * (C + 20), 2 * (C + 20) + 50), (31, 32, 36)); d = ImageDraw.Draw(out)
    for i, (n, fn) in enumerate(ARMES):
        for j, P in enumerate((S, I)):
            g = fn(P).resize((C, C), Image.NEAREST)
            out.paste(g, (110 + i * (C + 20), 40 + j * (C + 20)), g)
        d.text((110 + i * (C + 20) + C // 2 - d.textlength(n, font=f) / 2, 10), n, fill=(240, 205, 120), font=f)
    d.text((10, 40 + C // 2), "Sacré", fill=(240, 205, 120), font=f); d.text((10, 60 + C + C // 2), "Impérial", fill=(240, 205, 120), font=f)
    out.save('apercu_icones.png'); print(out.size)
