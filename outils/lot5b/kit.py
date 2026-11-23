# Lot 5b : écrans de Create en HD (3x), dans la langue des écrans Create déjà passés en HD (filtres, horaire, gardien de stock) :
# plaque d'ardoise à planches, cadre d'airain exposé de 9 texels riveté, creux et cases gravés, filets gravés rivetés aux bouts.
import random
from PIL import Image, ImageDraw

S = 3
def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
EXP = dict(trait=hx('6a2c1c'), base=hx('da955b'), clair=hx('ebb681'), mi=hx('ae5e33'), sombre=hx('a1532d'))
ARD = dict(base=hx('363a44'), joint=hx('2f333c'), joint_clair=hx('3d4250'), creux=hx('2a2e37'), ombre=hx('1b1e24'), ombre2=hx('23262d'),
           clair=hx('4b5160'), noir=hx('15171b'))

class Planche:
    """Une planche HD de la taille de l'originale x3 ; on y peint des éléments placés en pixels d'interface."""
    def __init__(self, w=256, h=256, base=None):
        self.im = base.copy() if base else Image.new('RGBA', (w * S, h * S)); self.d = ImageDraw.Draw(self.im)
    def r(self, x0, y0, x1, y1, c):            # rectangle en texels HD, bornes incluses
        if x1 >= x0 and y1 >= y0: self.d.rectangle([x0, y0, x1, y1], fill=c)
    def efface(self, x, y, w, h): self.r(x * S, y * S, (x + w) * S - 1, (y + h) * S - 1, (0, 0, 0, 0))

    # ---- ardoise à planches (joints horizontaux interrompus, gravés : sombre puis clair dessous)
    def ardoise(self, X0, Y0, X1, Y1, graine=1):
        self.r(X0, Y0, X1, Y1, ARD['base']); rnd = random.Random(graine); y = Y0 + rnd.randint(12, 22)
        while y < Y1 - 6:
            x = X0
            while x < X1:
                L = rnd.randint(40, 180); g = rnd.randint(10, 40)
                self.r(x, y, min(X1, x + L), y, ARD['joint']); self.r(x, y + 1, min(X1, x + L), y + 1, ARD['joint_clair'])
                x += L + g
            y += rnd.randint(16, 30)

    def rivet(self, cx, cy):                      # rivet de 5 texels : bord sombre, dôme éclairé en haut à gauche
        T = EXP
        for dx, dy in ((0, -2), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)):
            c = T['clair'] if dx + dy < 0 else T['base'] if dx + dy == 0 else T['mi']
            if abs(dx) + abs(dy) == 2: c = T['trait']
            self.im.putpixel((cx + dx, cy + dy), c)

    def plaque(self, x, y, w, h, graine=1, rivets=True):
        """Plaque complète : cadre exposé de 9 texels (trait, base, clair x2, base, mi x2, sombre, trait), ardoise dedans."""
        X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
        bandes = [EXP['trait'], EXP['base'], EXP['clair'], EXP['clair'], EXP['base'], EXP['mi'], EXP['mi'], EXP['sombre'], EXP['trait']]
        for k, c in enumerate(bandes): self.r(X0 + k, Y0 + k, X1 - k, Y1 - k, c)
        self.ardoise(X0 + 9, Y0 + 9, X1 - 9, Y1 - 9, graine)
        if rivets:
            for X in range(X0 + 27, X1 - 20, 60): self.rivet(X, Y0 + 4); self.rivet(X, Y1 - 4)
            for Y in range(Y0 + 27, Y1 - 20, 60): self.rivet(X0 + 4, Y); self.rivet(X1 - 4, Y)
            for (X, Y) in ((X0 + 4, Y0 + 4), (X1 - 4, Y0 + 4), (X0 + 4, Y1 - 4), (X1 - 4, Y1 - 4)): self.rivet(X, Y)

    def creux(self, x, y, w, h, fond=None):
        """Creux gravé (case, champ, zone) : trait, bord d'airain enfoncé (sombre en haut à gauche, clair en bas à droite),
        ombre portée intérieure, fond d'ardoise sombre. Mêmes texels que les cases des filtres HD."""
        X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
        self.r(X0, Y0, X1, Y1, EXP['trait'])
        self.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['clair']); self.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['sombre'])
        self.r(X0 + 2, Y0 + 2, X1 - 1, Y1 - 1, EXP['base']); self.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['mi'])
        self.r(X0 + 3, Y0 + 3, X1 - 3, Y1 - 3, ARD['ombre']); self.r(X0 + 5, Y0 + 5, X1 - 3, Y1 - 3, ARD['ombre2'])
        self.r(X0 + 6, Y0 + 6, X1 - 3, Y1 - 3, fond or ARD['creux'])

    def filet(self, x0, x1, y, rivets=True):
        """Filet gravé horizontal (sombre, clair dessous), rivets aux deux bouts."""
        # le filet commence après le cadre (9 texels) et une marge, comme sur les filtres HD
        X0, X1, Y = x0 * S + 15, x1 * S - 16, y * S + 1
        self.r(X0 + 3, Y, X1 - 3, Y, ARD['ombre']); self.r(X0 + 3, Y + 1, X1 - 3, Y + 1, ARD['clair'])
        if rivets: self.rivet(X0, Y); self.rivet(X1, Y)

    def filet_creux(self, x0, x1, y):
        """Filet dans un creux sombre (sans rivets) : ligne gravée un ton plus sombre que le fond."""
        X0, X1, Y = x0 * S, x1 * S - 1, y * S + 1
        self.r(X0, Y, X1, Y, ARD['ombre']); self.r(X0, Y + 1, X1, Y + 1, hx('353944'))

    def tige(self, x, y0, y1, noeuds=()):
        """Tige d'airain verticale de 1 pixel d'interface (3 texels : clair, base, sombre), nœuds rivetés."""
        X, Y0, Y1 = x * S, y0 * S, y1 * S - 1
        self.r(X - 1, Y0, X + 3, Y1, EXP['trait']); self.r(X, Y0, X, Y1, EXP['clair']); self.r(X + 1, Y0, X + 1, Y1, EXP['base']); self.r(X + 2, Y0, X + 2, Y1, EXP['mi'])
        for y in noeuds:
            # nœud : bague d'airain de 5 px d'interface de haut, rivet au milieu
            Y = y * S + 1; self.r(X - 5, Y - 7, X + 7, Y + 7, EXP['trait']); self.r(X - 4, Y - 6, X + 6, Y + 6, EXP['base'])
            self.r(X - 4, Y - 6, X + 6, Y - 5, EXP['clair']); self.r(X - 4, Y - 6, X - 3, Y + 6, EXP['clair'])
            self.r(X - 4, Y + 5, X + 6, Y + 6, EXP['mi']); self.r(X + 5, Y - 6, X + 6, Y + 6, EXP['mi']); self.rivet(X + 1, Y)

    def colle(self, im, x, y): self.im.alpha_composite(im, (x * S, y * S))

OR = dict(trait=hx('704425'), hl=hx('fce9b7'), clair=hx('f3d694'), base=hx('e1ba6e'), mid=hx('c99b52'), mi=hx('b48242'), sombre=hx('a8763c'))
def bande_or(n=9):
    """Coupe d'une baguette d'airain neuf, de l'extérieur (lumière) vers l'intérieur : n texels."""
    b = [OR['trait'], OR['hl'], OR['clair'], OR['base'], OR['base'], OR['mid'], OR['mi'], OR['sombre'], OR['trait']]
    return b if n == 9 else b[:n - 1] + [OR['trait']]
def plaque_or(p, X0, Y0, X1, Y1):
    """Plaque d'airain neuf en relief (texels HD inclus) : trait, arête claire en haut, corps, pied ombré."""
    p.r(X0, Y0, X1, Y1, OR['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, OR['sombre']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, OR['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, OR['base']); p.r(X0 + 2, Y1 - 3, X1 - 2, Y1 - 2, OR['mid'])

# ---------------- habillage (retour de Liam : « trop simples ») ----------------
import math
def _grave(self, m, X0=0, Y0=0):
    """Gravure dans l'ardoise d'après un masque (texels HD) : creux sombre, arête d'ombre en haut à gauche, arête claire en bas à droite."""
    w, h = m.size; px = m.load()
    for y in range(h):
        for x in range(w):
            if not px[x, y]: continue
            haut = y == 0 or not px[x, y - 1]; gauche = x == 0 or not px[x - 1, y]
            bas = y == h - 1 or not px[x, y + 1]; droite = x == w - 1 or not px[x + 1, y]
            c = ARD['noir'] if (haut or gauche) else hx('454a57') if (bas or droite) else ARD['ombre2']
            self.im.putpixel((X0 + x, Y0 + y), c)
Planche.grave = _grave
def masque_engrenage(r, dents=8, moyeu=0.35, rayons=4, prof=0.22):
    """Masque d'engrenage (rayon r texels) : couronne dentée, rayons, moyeu percé."""
    from PIL import Image as I, ImageDraw as D
    n = 2 * r + 3; K = 4; m = I.new('L', (n * K, n * K)); d = D.Draw(m); c = n * K / 2
    pts = []
    for k in range(dents * 4):
        a = 2 * math.pi * k / (dents * 4); rr = r if (k % 4) in (1, 2) else r * (1 - prof)
        pts.append((c + rr * K * math.cos(a), c + rr * K * math.sin(a)))
    d.polygon(pts, fill=255)
    d.ellipse([c - r * 0.62 * K, c - r * 0.62 * K, c + r * 0.62 * K, c + r * 0.62 * K], fill=0)
    for k in range(rayons):
        a = 2 * math.pi * k / rayons + 0.4
        d.line([(c, c), (c + r * 0.7 * K * math.cos(a), c + r * 0.7 * K * math.sin(a))], fill=255, width=int(max(2, r * 0.16) * K))
    d.ellipse([c - r * moyeu * K, c - r * moyeu * K, c + r * moyeu * K, c + r * moyeu * K], fill=255)
    d.ellipse([c - r * 0.12 * K, c - r * 0.12 * K, c + r * 0.12 * K, c + r * 0.12 * K], fill=0)
    return m.resize((n, n), I.BOX).point(lambda v: 255 if v >= 128 else 0)
def _engrenage(self, cx, cy, r, dents=8):
    m = masque_engrenage(r, dents); self.grave(m, cx * S - m.width // 2, cy * S - m.height // 2)
Planche.engrenage = _engrenage

def _case_riche(self, x, y, w=18, h=18, ep=4):
    """Case principale : creux gravé dans un cadre d'airain exposé en relief, rivets aux quatre coins (comme la sortie du fourneau).
    ep : débord du cadre autour de la case (4 texels ; 3 pour un cadre centré au texel près dans un plateau serré)."""
    X0, Y0, X1, Y1 = x * S - ep, y * S - ep, (x + w) * S - 1 + ep, (y + h) * S - 1 + ep
    self.r(X0, Y0, X1, Y1, EXP['trait']); self.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); self.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    self.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base'])
    self.creux(x, y, w, h)
    if ep >= 4:                                          # rivets d'angle seulement si le cadre est assez large pour eux
        for (X, Y) in ((X0 + 2, Y0 + 2), (X1 - 2, Y0 + 2), (X0 + 2, Y1 - 2), (X1 - 2, Y1 - 2)):
            self.r(X - 1, Y - 1, X + 1, Y + 1, EXP['trait']); self.im.putpixel((X, Y), EXP['clair'])
Planche.case_riche = _case_riche

def _champ(self, x, y, w, h, molette=False):
    """Champ : creux gravé, une bague d'airain à chaque bout ; ⇕ d'airain au bout droit si la valeur se règle à la molette."""
    self.creux(x, y, w, h)
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    for X in (X0 + 3, X1 - 5):
        self.r(X, Y0 + 3, X + 2, Y1 - 3, EXP['trait']); self.r(X + 1, Y0 + 4, X + 1, Y1 - 4, EXP['base']); self.im.putpixel((X + 1, Y0 + 4), EXP['clair'])
    if molette:
        cx = X1 - 13; cy = (Y0 + Y1) // 2
        for k in range(4):       # deux chevrons, haut et bas
            self.r(cx - k, cy - 6 + k, cx + k, cy - 6 + k, EXP['base']); self.r(cx - k, cy + 6 - k, cx + k, cy + 6 - k, EXP['mi'])
        self.r(cx - 3, cy - 6 + 3, cx + 3, cy - 6 + 3, EXP['clair'])
Planche.champ = _champ

def _bandeau(self, x, y, w, h=11):
    """Bandeau du titre, sous le cadre : bande d'ardoise sombre entre deux rails d'airain, embouts rivetés (le texte s'y pose)."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    self.r(X0, Y0, X1, Y1, hx('2e323b'))
    for (Y, c1, c2) in ((Y0, EXP['trait'], EXP['clair']), (Y1 - 2, EXP['mi'], EXP['trait'])):
        self.r(X0, Y, X1, Y, c1); self.r(X0, Y + 1, X1, Y + 1, c2); self.r(X0, Y + 2, X1, Y + 2, EXP['trait'] if Y == Y0 else c2)
    self.r(X0, Y0 + 3, X1, Y0 + 4, ARD['ombre'])
    for X in (X0, X1 - 8):
        self.r(X, Y0, X + 8, Y1, EXP['trait']); self.r(X + 1, Y0 + 1, X + 7, Y1 - 1, EXP['base'])
        self.r(X + 1, Y0 + 1, X + 7, Y0 + 2, EXP['clair']); self.r(X + 1, Y1 - 2, X + 7, Y1 - 1, EXP['mi']); self.rivet(X + 4, (Y0 + Y1) // 2)
Planche.bandeau = _bandeau

def _socle(self, x, y, w, h, texels=None):
    """Plateau du bas (là où Create pose ses boutons) : un cran plus bas que la plaque, bord gravé, rivets aux coins.
    texels=(X0, Y0, X1, Y1) : bornes exactes en texels, pour centrer le plateau au demi-pixel sur une case."""
    X0, Y0, X1, Y1 = texels or (x * S, y * S, (x + w) * S - 1, (y + h) * S - 1)
    self.r(X0, Y0, X1, Y1, ARD['ombre']); self.r(X0 + 1, Y0 + 1, X1, Y1, hx('3f4450')); self.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, hx('30343d'))
    self.r(X0 + 1, Y0 + 1, X1 - 1, Y0 + 2, ARD['ombre2'])
    for (X, Y) in ((X0 + 5, Y0 + 6), (X1 - 5, Y0 + 6), (X0 + 5, Y1 - 5), (X1 - 5, Y1 - 5)): self.rivet(X, Y)
Planche.socle = _socle

def _lampe(self, x, y, couleur, r=8):
    """Voyant : bague d'airain, verre coloré bombé, reflet en haut à gauche (centre en pixels d'interface)."""
    C = {'vert': (hx('e8ffd0'), hx('9be27a'), hx('4a9a3c'), hx('2a5e22')), 'ambre': (hx('fff4c8'), hx('ffc860'), hx('e08a10'), hx('8a4a08')),
         'rouge': (hx('ffd0c4'), hx('ff6a50'), hx('c42a22'), hx('6a1210'))}[couleur]
    X, Y = x * S, y * S
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d > r + 0.3: continue
            if d > r - 1: c = EXP['trait']
            elif d > r - 3: c = EXP['clair'] if dx + dy < 0 else EXP['mi']
            elif d > r - 4: c = C[3]
            else:
                t = (dx + dy) / (2 * (r - 4))
                c = C[0] if (abs(dx + 3) + abs(dy + 3) <= 1) else C[1] if t < -0.3 else C[2] if t < 0.4 else C[3]
            self.im.putpixel((X + dx, Y + dy), c)
Planche.lampe = _lampe

def _tuyau(self, x, y0, y1, brides=()):
    """Tuyau d'airain vertical (2 px d'interface), brides rivetées."""
    X, Y0, Y1 = x * S - 2, y0 * S, y1 * S - 1
    for k, c in enumerate([EXP['trait'], EXP['clair'], EXP['clair'], EXP['base'], EXP['base'], EXP['mi'], EXP['sombre'], EXP['trait']]):
        self.r(X + k, Y0, X + k, Y1, c)
    for y in brides:
        Y = y * S
        self.r(X - 3, Y - 3, X + 10, Y + 3, EXP['trait']); self.r(X - 2, Y - 2, X + 9, Y + 2, EXP['base']); self.r(X - 2, Y - 2, X + 9, Y - 2, EXP['clair'])
        self.r(X - 2, Y + 2, X + 9, Y + 2, EXP['mi'])
    # embouts : le tuyau entre dans une bride pleine à chaque bout (il ne s'arrête plus net)
    for Y in (Y0, Y1 - 5):
        self.r(X - 3, Y, X + 10, Y + 5, EXP['trait']); self.r(X - 2, Y + 1, X + 9, Y + 4, EXP['base'])
        self.r(X - 2, Y + 1, X + 9, Y + 1, EXP['clair']); self.r(X - 2, Y + 4, X + 9, Y + 4, EXP['mi']); self.rivet(X + 3, Y + 2)
Planche.tuyau = _tuyau
def _voyant_monte(self, x, y, couleur):
    """Voyant monté sur le tuyau : collier carré riveté (plus large que le tuyau), le verre posé dessus."""
    X, Y = x * S, y * S
    self.r(X - 11, Y - 11, X + 11, Y + 11, EXP['trait']); self.r(X - 10, Y - 10, X + 10, Y + 10, EXP['mi'])
    self.r(X - 10, Y - 10, X + 9, Y + 9, EXP['clair']); self.r(X - 9, Y - 9, X + 9, Y + 9, EXP['base'])
    for (a, b) in ((-7, -7), (7, -7), (-7, 7), (7, 7)): self.im.putpixel((X + a, Y + b), EXP['trait']); self.im.putpixel((X + a - 1, Y + b - 1), EXP['clair'])
    self.lampe(x, y, couleur, r=7)
Planche.voyant_monte = _voyant_monte

def _chevron(self, x, y):
    """Petit chevron d'airain pointé vers le bas (sens de la liaison), posé sur un filet."""
    X, Y = x * S, y * S
    for k in range(5):
        self.r(X - 6 + k, Y + k, X + 6 - k, Y + k, EXP['trait'])
        if k < 4: self.r(X - 5 + k, Y + k, X + 5 - k, Y + k, EXP['base'] if k else EXP['clair'])
Planche.chevron = _chevron

# ---------------- piste B : « carter de machine » (cadre épais boulonné, plaque nominative, grilles d'aération) ----------------
def _boulon(self, cx, cy):
    """Tête de boulon hexagonale (7 texels), rondelle sombre, pan éclairé en haut à gauche."""
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if abs(dx) + abs(dy) > 4 or (abs(dx) == 3 and abs(dy) == 3): continue
            bord = abs(dx) + abs(dy) == 4 or abs(dx) == 3 or abs(dy) == 3
            c = EXP['trait'] if bord else EXP['clair'] if dx + dy < 0 else EXP['base'] if dx + dy == 0 else EXP['mi']
            self.im.putpixel((cx + dx, cy + dy), c)
    self.im.putpixel((cx, cy), EXP['sombre'])
Planche.boulon = _boulon
def _carter(self, x, y, w, h, graine=1):
    """Cadre de carter : 15 texels (5 px) d'airain exposé, une gorge gravée au milieu, boulons aux coins et tous les 20 px."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    bandes = [EXP['trait'], EXP['clair'], EXP['clair'], EXP['base'], EXP['base'], EXP['base'], EXP['trait'], EXP['clair'],
              EXP['base'], EXP['base'], EXP['mi'], EXP['mi'], EXP['sombre'], ARD['ombre'], EXP['trait']]
    for k, c in enumerate(bandes): self.r(X0 + k, Y0 + k, X1 - k, Y1 - k, c)
    # ombre et lumière des bords : le bas et la droite plus sombres
    for k in range(1, 13):
        self.r(X0 + k, Y1 - k, X1 - k, Y1 - k, EXP['mi'] if k < 6 else EXP['sombre']); self.r(X1 - k, Y0 + k, X1 - k, Y1 - k, EXP['mi'] if k < 6 else EXP['sombre'])
    self.r(X0 + 6, Y1 - 6, X1 - 6, Y1 - 6, EXP['trait']); self.r(X1 - 6, Y0 + 6, X1 - 6, Y1 - 6, EXP['trait'])
    self.ardoise(X0 + 15, Y0 + 15, X1 - 15, Y1 - 15, graine)
    for X in range(X0 + 30, X1 - 25, 60): self.boulon(X, Y0 + 3 + 0); self.boulon(X, Y1 - 3)
    for Y in range(Y0 + 30, Y1 - 25, 60): self.boulon(X0 + 3, Y); self.boulon(X1 - 3, Y)
    for (X, Y) in ((X0 + 7, Y0 + 7), (X1 - 7, Y0 + 7), (X0 + 7, Y1 - 7), (X1 - 7, Y1 - 7)): self.boulon(X, Y)
Planche.carter = _carter
def _plaque_nom(self, x, y, w, h=11):
    """Plaque nominative en relief (le titre s'y pose) : airain exposé poli, deux vis aux bouts, filet gravé autour du texte."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    self.r(X0, Y0, X1, Y1, EXP['trait']); self.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); self.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    self.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, hx('7a3a22')); self.r(X0 + 3, Y0 + 3, X1 - 3, Y1 - 3, hx('5a2a1a'))
    self.r(X0 + 3, Y1 - 3, X1 - 3, Y1 - 3, hx('8a4a2a'))
    for X in (X0 + 6, X1 - 6): self.boulon(X, (Y0 + Y1) // 2)
Planche.plaque_nom = _plaque_nom
def _grille(self, x, y, w, h):
    """Grille d'aération gravée : fentes horizontales régulières dans l'ardoise."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    for Y in range(Y0, Y1 - 2, 5):
        self.r(X0, Y, X1, Y + 1, ARD['noir']); self.r(X0, Y + 2, X1, Y + 2, hx('454a57'))
Planche.grille = _grille
