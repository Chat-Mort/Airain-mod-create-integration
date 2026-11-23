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
def masque_engrenage(r, dents=8, moyeu=0.35, rayons=4, prof=0.22, plein=False):
    """Masque d'engrenage (rayon r texels) : couronne dentée, rayons, moyeu percé."""
    from PIL import Image as I, ImageDraw as D
    n = 2 * r + 3; K = 4; m = I.new('L', (n * K, n * K)); d = D.Draw(m); c = n * K / 2
    pts = []
    for k in range(dents * 4):
        a = 2 * math.pi * k / (dents * 4); rr = r if (k % 4) in (1, 2) else r * (1 - prof)
        pts.append((c + rr * K * math.cos(a), c + rr * K * math.sin(a)))
    d.polygon(pts, fill=255)
    if not plein: d.ellipse([c - r * 0.62 * K, c - r * 0.62 * K, c + r * 0.62 * K, c + r * 0.62 * K], fill=0)
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

def _lampe(self, x, y, couleur, r=8): self._lampe_texel(x * S, y * S, couleur, r)
def _lampe_texel(self, X, Y, couleur, r=8):
    """Voyant : bague d'airain, verre coloré bombé, reflet en haut à gauche (centre en pixels d'interface)."""
    C = {'vert': (hx('e8ffd0'), hx('9be27a'), hx('4a9a3c'), hx('2a5e22')), 'ambre': (hx('fff4c8'), hx('ffc860'), hx('e08a10'), hx('8a4a08')),
         'rouge': (hx('ffd0c4'), hx('ff6a50'), hx('c42a22'), hx('6a1210'))}[couleur]
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
Planche.lampe = _lampe; Planche._lampe_texel = _lampe_texel

def _tuyau(self, x, y0, y1, brides=()):
    """Tuyau d'airain vertical de 7 texels, centré sur le texel x*S+1 (le centre du pixel d'interface x), embouts à bride."""
    C = x * S + 1; X = C - 3; Y0, Y1 = y0 * S, y1 * S - 1
    for k, c in enumerate([EXP['trait'], EXP['clair'], EXP['clair'], EXP['base'], EXP['mi'], EXP['sombre'], EXP['trait']]):
        self.r(X + k, Y0, X + k, Y1, c)
    for Y in [y * S for y in brides] + [Y0, Y1 - 5]:
        self.r(C - 6, Y, C + 6, Y + 5, EXP['trait']); self.r(C - 5, Y + 1, C + 5, Y + 4, EXP['base'])
        self.r(C - 5, Y + 1, C + 5, Y + 1, EXP['clair']); self.r(C - 5, Y + 4, C + 5, Y + 4, EXP['mi']); self.rivet(C, Y + 2)
Planche.tuyau = _tuyau
def _voyant_monte(self, x, y, couleur):
    """Voyant monté sur le tuyau : collier carré riveté centré sur le tuyau (texel x*S+1), le verre posé dessus."""
    X, Y = x * S + 1, y * S + 1
    self.r(X - 11, Y - 11, X + 11, Y + 11, EXP['trait']); self.r(X - 10, Y - 10, X + 10, Y + 10, EXP['mi'])
    self.r(X - 10, Y - 10, X + 9, Y + 9, EXP['clair']); self.r(X - 9, Y - 9, X + 9, Y + 9, EXP['base'])
    for (a, b) in ((-7, -7), (7, -7), (-7, 7), (7, 7)): self.im.putpixel((X + a, Y + b), EXP['trait']); self.im.putpixel((X + a - 1, Y + b - 1), EXP['clair'])
    self._lampe_texel(X, Y, couleur, 7)
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

def _emplacement(self, x, y, w, h):
    """Emplacement vide (champ non utilisé) : simple filet gravé en creux, coins marqués d'un point d'airain."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    for (a, b, c, d2) in ((X0, Y0, X1, Y0), (X0, Y0, X0, Y1)): self.r(a, b, c, d2, ARD['ombre'])
    for (a, b, c, d2) in ((X0, Y1, X1, Y1), (X1, Y0, X1, Y1)): self.r(a, b, c, d2, hx('454a57'))
    for (X, Y) in ((X0 + 2, Y0 + 2), (X1 - 2, Y0 + 2), (X0 + 2, Y1 - 2), (X1 - 2, Y1 - 2)): self.im.putpixel((X, Y), EXP['mi'])
Planche.emplacement = _emplacement

def _imprimante(self, x0, y0, x1, y1, fente_y0, fente_y1):
    """Étiqueteuse : petit carter d'airain exposé, rivets, fenêtre de la roue à caractères, manivelle sur le dessus,
    deux rouleaux d'entraînement à la fente de sortie (bord droit) d'où sort l'étiquette. Coordonnées en px d'interface."""
    X0, Y0, X1, Y1 = x0 * S, y0 * S, x1 * S - 1, y1 * S - 1
    self.r(X0, Y0, X1, Y1, EXP['trait']); self.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); self.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    self.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); self.r(X0 + 2, Y1 - 4, X1 - 2, Y1 - 2, EXP['mi'])
    for (X, Y) in ((X0 + 4, Y0 + 4), (X1 - 4, Y0 + 4), (X0 + 4, Y1 - 5), (X1 - 4, Y1 - 5)): self.rivet(X, Y)
    # fenêtre de la roue à caractères : creux sombre, trois lettres gravées suggérées par des traits clairs
    wx0, wx1, wy0, wy1 = X0 + 9, X1 - 12, Y0 + 9, Y0 + 21
    self.r(wx0, wy0, wx1, wy1, EXP['trait']); self.r(wx0 + 1, wy0 + 1, wx1 - 1, wy1 - 1, ARD['ombre']); self.r(wx0 + 2, wy0 + 2, wx1 - 1, wy1 - 1, ARD['creux'])
    for k, X in enumerate(range(wx0 + 4, wx1 - 3, 5)):
        self.r(X, wy0 + 4, X + 2, wy0 + 4, hx('f3ead6')); self.r(X + (k % 2), wy0 + 5, X + (k % 2), wy1 - 4, hx('d8ccae'))
    self.r(wx0 + 2, (wy0 + wy1) // 2, wx1 - 1, (wy0 + wy1) // 2, ARD['noir'])            # repère de lecture
    # manivelle sur le dessus : axe, bras, poignée
    cx = (X0 + X1) // 2
    self.r(cx - 2, Y0 - 5, cx + 2, Y0, EXP['trait']); self.r(cx - 1, Y0 - 4, cx + 1, Y0, EXP['base'])
    self.r(cx, Y0 - 6, cx + 12, Y0 - 4, EXP['trait']); self.r(cx + 1, Y0 - 5, cx + 11, Y0 - 5, EXP['clair'])
    self.r(cx + 10, Y0 - 12, cx + 14, Y0 - 5, EXP['trait']); self.r(cx + 11, Y0 - 11, cx + 13, Y0 - 6, hx('5a2a1a'))
    # fente de sortie et rouleaux
    F0, F1 = fente_y0 * S, fente_y1 * S - 1
    self.r(X1 - 3, F0, X1, F1, ARD['noir'])
    for Yc in (F0 - 4, F1 + 4):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                d = (dx * dx + dy * dy) ** 0.5
                if d <= 4.3: self.im.putpixel((X1 - 3 + dx, Yc + dy), EXP['trait'] if d > 3.3 else EXP['clair'] if dx + dy < 0 else EXP['mi'] if d > 1.5 else EXP['sombre'])
Planche.imprimante = _imprimante

def _cadran(self, x, y, r=10):
    """Manomètre : lunette d'airain, cadran ivoire gradué, aiguille, rivet central (centre en px d'interface, rayon en texels)."""
    X, Y = x * S + 1, y * S + 1
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = (dx * dx + dy * dy) ** 0.5
            if d > r + 0.3: continue
            c = EXP['trait'] if d > r - 1 else (EXP['clair'] if dx + dy < 0 else EXP['mi']) if d > r - 3 else EXP['trait'] if d > r - 4 else hx('f3ead6')
            self.im.putpixel((X + dx, Y + dy), c)
    import math as m
    for k in range(9):                                       # graduations sur 270°
        a = m.radians(135 + k * 33.75); rr = r - 5
        self.im.putpixel((X + round(rr * m.cos(a)), Y + round(rr * m.sin(a))), hx('5a2a1a'))
    a = m.radians(135 + 0.62 * 270)
    for t in range(0, r - 4):
        self.im.putpixel((X + round(t * m.cos(a)), Y + round(t * m.sin(a))), hx('c42a22'))
    self.r(X - 1, Y - 1, X + 1, Y + 1, EXP['trait']); self.im.putpixel((X, Y), EXP['clair'])
Planche.cadran = _cadran

def _telescripteur(self, x0, y0, x1, y1, fente_y0, fente_y1):
    """Téléscripteur (ruban qui devient l'étiquette) : socle d'airain mouluré, corps riveté à fente de sortie et rouleaux,
    cloche de verre sur le dessus avec la roue à caractères dedans. Coordonnées en px d'interface (x1, y1 exclus)."""
    X0, Y0, X1, Y1 = x0 * S, y0 * S, x1 * S - 1, y1 * S - 1
    W = X1 - X0
    # socle
    sb = Y1 - 13
    self.r(X0, sb, X1, Y1, EXP['trait']); self.r(X0 + 1, sb + 1, X1 - 1, Y1 - 1, EXP['mi']); self.r(X0 + 1, sb + 1, X1 - 2, sb + 3, EXP['clair'])
    self.r(X0 + 2, sb + 4, X1 - 2, Y1 - 3, EXP['base']); self.r(X0 + 2, Y1 - 3, X1 - 2, Y1 - 2, EXP['sombre'])
    for X in (X0 + 6, X1 - 6): self.rivet(X, sb + 7)
    # corps
    # le corps couvre toute la hauteur de la fente (le ruban sort bien de lui), avec 2 px de marge au-dessus
    cb0, cb1 = X0 + 6, X1 - 4; ct = min(sb - 34, fente_y0 * S - 6)
    self.r(cb0, ct, cb1, sb, EXP['trait']); self.r(cb0 + 1, ct + 1, cb1 - 1, sb - 1, EXP['base'])
    for X in range(cb0 + 1, cb1):                                     # volume : clair à gauche, sombre à droite
        t = (X - cb0) / (cb1 - cb0)
        self.r(X, ct + 1, X, sb - 1, EXP['clair'] if t < 0.2 else EXP['base'] if t < 0.7 else EXP['mi'])
    self.r(cb0 + 1, ct + 1, cb1 - 1, ct + 2, EXP['clair'])
    for (X, Y) in ((cb0 + 4, ct + 5), (cb0 + 4, sb - 5)): self.rivet(X, Y)
    # petite plaque gravée sur le corps
    # compteur rond sur le devant (le ruban ne sort que par le côté)
    Xc, Yc = (cb0 + cb1) // 2, (ct + sb) // 2
    for dy in range(-9, 10):
        for dx in range(-9, 10):
            d = (dx * dx + dy * dy) ** 0.5
            if d <= 9.3: self.im.putpixel((Xc + dx, Yc + dy), EXP['trait'] if d > 8.3 else (EXP['clair'] if dx + dy < 0 else EXP['mi']) if d > 6.3 else EXP['trait'] if d > 5.4 else hx('f3ead6'))
    for k2 in range(-3, 4, 3): self.r(Xc + k2 - 1, Yc - 2, Xc + k2, Yc + 2, hx('3a2a1a'))
    # fente et rouleaux à droite
    F0, F1 = fente_y0 * S, fente_y1 * S - 1
    for Yc in (F0 - 4, F1 + 4):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                d = (dx * dx + dy * dy) ** 0.5
                if d <= 4.3: self.im.putpixel((cb1 - 1 + dx, Yc + dy), EXP['trait'] if d > 3.3 else hx('3a3e48') if d > 1.5 else hx('8a8e98'))
    # cloche de verre : demi-ellipse, verre bleuté translucide, reflet, roue à caractères dedans, bague d'airain au pied
    gx0, gx1, gy1 = cb0 + 4, cb1 - 4, ct; gy0 = max(ct - 44, Y0)          # la cloche ne dépasse pas le haut du morceau
    cx = (gx0 + gx1) / 2; rx = (gx1 - gx0) / 2; ry = gy1 - gy0
    for Y in range(gy0, gy1):
        for X in range(gx0, gx1 + 1):
            u, v = (X - cx) / rx, (gy1 - Y) / ry
            d = u * u + v * v
            if d > 1: continue
            fond = self.im.getpixel((X, Y))
            if d > 0.86: c = hx('c8d8e8')
            elif -0.75 < u < -0.45 and 0.35 < v < 0.8: c = hx('eef6ff')
            else: c = tuple(int(fond[i] * 0.6 + (90, 110, 130)[i] * 0.4) for i in range(3)) + (255,)
            self.im.putpixel((X, Y), c)
    m = masque_engrenage(min(9, (gy1 - gy0 - 8) // 2), 8)
    for yy in range(m.height):
        for xx in range(m.width):
            if m.getpixel((xx, yy)):
                X, Y = int(cx) - m.width // 2 + xx, gy1 - 6 - m.height + yy
                self.im.putpixel((X, Y), EXP['clair'] if yy < m.height // 2 else EXP['base'])
    self.r(gx0 - 2, gy1 - 3, gx1 + 2, gy1, EXP['trait']); self.r(gx0 - 1, gy1 - 2, gx1 + 1, gy1 - 1, EXP['clair'])
Planche.telescripteur = _telescripteur

def _telescripteur2(self, x0, x1, y_cloche, y_corps, y_socle, y_bas, fente_y0, fente_y1):
    """Téléscripteur compact (refait de zéro) : tout tient entre x0 et x1 (px d'interface).
    Cloche de verre (y_cloche -> y_corps), corps riveté (y_corps -> y_socle) qui couvre toute la hauteur du ruban,
    compteur rond en façade, rouleaux sur le bord droit de part et d'autre du ruban, socle mouluré (y_socle -> y_bas)."""
    X0, X1 = x0 * S, x1 * S - 1
    # socle
    Ys0, Ys1 = y_socle * S, y_bas * S - 1
    self.r(X0, Ys0, X1, Ys1, EXP['trait']); self.r(X0 + 1, Ys0 + 1, X1 - 1, Ys1 - 1, EXP['mi']); self.r(X0 + 1, Ys0 + 1, X1 - 2, Ys0 + 2, EXP['clair'])
    self.r(X0 + 2, Ys0 + 3, X1 - 2, Ys1 - 2, EXP['base'])
    for X in (X0 + 5, X1 - 5): self.rivet(X, (Ys0 + Ys1) // 2)
    # corps (plus étroit que le socle)
    C0, C1, Yc0, Yc1 = X0 + 5, X1 - 3, y_corps * S, Ys0
    self.r(C0, Yc0, C1, Yc1, EXP['trait'])
    for X in range(C0 + 1, C1):
        t = (X - C0) / (C1 - C0)
        self.r(X, Yc0 + 1, X, Yc1 - 1, EXP['clair'] if t < 0.18 else EXP['base'] if t < 0.72 else EXP['mi'])
    self.r(C0 + 1, Yc0 + 1, C1 - 1, Yc0 + 1, EXP['hl'] if 'hl' in EXP else EXP['clair'])
    for (X, Y) in ((C0 + 4, Yc0 + 4), (C0 + 4, Yc1 - 4)): self.rivet(X, Y)
    # compteur rond en façade
    Xc, Yc = (C0 + C1) // 2 - 1, (Yc0 + Yc1) // 2
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            d = (dx * dx + dy * dy) ** 0.5
            if d <= 8.3: self.im.putpixel((Xc + dx, Yc + dy), EXP['trait'] if d > 7.3 else (EXP['clair'] if dx + dy < 0 else EXP['mi']) if d > 5.3 else EXP['trait'] if d > 4.4 else hx('f3ead6'))
    for k2 in (-2, 1): self.r(Xc + k2, Yc - 2, Xc + k2, Yc + 2, hx('3a2a1a'))
    # rouleaux sur le bord droit, au-dessus et au-dessous du ruban
    F0, F1 = fente_y0 * S, fente_y1 * S - 1
    for Ycr in (F0 - 3, F1 + 3):
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                d = (dx * dx + dy * dy) ** 0.5
                if d <= 3.3: self.im.putpixel((C1 - 1 + dx, Ycr + dy), EXP['trait'] if d > 2.4 else hx('8a8e98') if dx + dy < 0 else hx('3a3e48'))
    # cloche de verre sur le dessus, bague d'airain au pied, roue à caractères dedans
    G0, G1, Yg0, Yg1 = C0 + 3, C1 - 3, y_cloche * S, Yc0
    cx = (G0 + G1) / 2; rx = (G1 - G0) / 2; ry = Yg1 - Yg0
    for Y in range(Yg0, Yg1):
        for X in range(G0, G1 + 1):
            u, v = (X - cx) / rx, (Yg1 - Y) / ry
            d = u * u + v * v
            if d > 1: continue
            fond = self.im.getpixel((X, Y))
            c = hx('c8d8e8') if d > 0.82 else hx('eef6ff') if (-0.72 < u < -0.42 and 0.3 < v < 0.75) else tuple(int(fond[i] * 0.55 + (90, 110, 130)[i] * 0.45) for i in range(3)) + (255,)
            self.im.putpixel((X, Y), c)
    m = masque_engrenage(max(4, min(8, (Yg1 - Yg0) // 2 - 4)), 8)
    for yy in range(m.height):
        for xx in range(m.width):
            if m.getpixel((xx, yy)): self.im.putpixel((int(cx) - m.width // 2 + xx, Yg1 - 3 - m.height + yy), EXP['clair'] if yy < m.height // 2 else EXP['base'])
    self.r(G0 - 2, Yg1 - 2, G1 + 2, Yg1, EXP['trait']); self.r(G0 - 1, Yg1 - 1, G1 + 1, Yg1 - 1, EXP['clair'])
Planche.telescripteur2 = _telescripteur2

def _etiqueteuse(self, x0, x1, y0, y1, fente_y0, fente_y1):
    """Étiqueteuse dans l'esprit des machines de Create : bobine de papier sur un support en haut, le papier descend dans un
    boîtier en carter d'airain (coins boulonnés, panneau central en creux) ; engrenage sur la façade entraîné par un arbre
    qui sort du côté gauche ; sortie à droite, côté étiquette, entre deux rouleaux sous une lèvre d'airain."""
    X0, X1, Y0, Y1 = x0 * S, x1 * S - 1, y0 * S, y1 * S - 1
    F0, F1 = fente_y0 * S, fente_y1 * S - 1
    # --- boîtier : du haut de la fente - 4 px jusqu'en bas
    B0 = F0 - 6; B1 = Y1
    self.r(X0, B0, X1, B1, EXP['trait'])
    for X in range(X0 + 1, X1):
        t = (X - X0) / (X1 - X0)
        self.r(X, B0 + 1, X, B1 - 1, EXP['clair'] if t < 0.12 else EXP['base'] if t < 0.8 else EXP['mi'])
    self.r(X0 + 1, B0 + 1, X1 - 1, B0 + 2, EXP['clair']); self.r(X0 + 1, B1 - 2, X1 - 1, B1 - 1, EXP['sombre'])
    # panneau central en creux (comme un carter de Create)
    P0, P1, Q0, Q1 = X0 + 6, X1 - 6, B0 + 6, B1 - 6
    self.r(P0, Q0, P1, Q1, EXP['sombre']); self.r(P0 + 1, Q0 + 1, P1, Q1, EXP['clair']); self.r(P0 + 1, Q0 + 1, P1 - 1, Q1 - 1, EXP['base'])
    self.r(P0 + 1, Q0 + 1, P1 - 1, Q0 + 1, EXP['mi']); self.r(P0 + 1, Q0 + 1, P0 + 1, Q1 - 1, EXP['mi'])
    for (X, Y) in ((X0 + 3, B0 + 3), (X1 - 3, B0 + 3), (X0 + 3, B1 - 3), (X1 - 3, B1 - 3)): self.boulon(X, Y)
    # engrenage sur la façade (moyeu d'andésite, couronne d'airain), centré dans le panneau
    m = masque_engrenage(min((P1 - P0) // 2 - 2, (Q1 - Q0) // 2 - 2), 10, moyeu=0.42, rayons=0)
    gx, gy = (P0 + P1) // 2 - m.width // 2, (Q0 + Q1) // 2 - m.height // 2
    for yy in range(m.height):
        for xx in range(m.width):
            if not m.getpixel((xx, yy)): continue
            u, v = xx - m.width / 2, yy - m.height / 2; d = (u * u + v * v) ** 0.5
            bord = any(not (0 <= xx + a < m.width and 0 <= yy + b < m.height) or not m.getpixel((xx + a, yy + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if d < m.width * 0.22: c = hx('9a9a92') if u + v < 0 else hx('6e6e68')            # moyeu d'andésite
            else: c = EXP['trait'] if bord else EXP['clair'] if u + v < -2 else EXP['base'] if u + v < 3 else EXP['mi']
            self.im.putpixel((gx + xx, gy + yy), c)
    # arbre qui entre par le côté gauche (axe d'andésite au centre de l'engrenage)
    ay = (Q0 + Q1) // 2
    self.r(X0 - 6, ay - 2, X0, ay + 2, hx('3a3a36')); self.r(X0 - 6, ay - 1, X0, ay, hx('a8a8a0')); self.r(X0 - 6, ay + 1, X0, ay + 1, hx('7a7a74'))
    # --- bobine de papier sur son support, au-dessus du boîtier
    rc = min((X1 - X0) // 2 - 4, (B0 - Y0) // 2); cx, cy = (X0 + X1) // 2 - 2, Y0 + rc + 1
    for dy in range(-rc, rc + 1):
        for dx in range(-rc, rc + 1):
            d = (dx * dx + dy * dy) ** 0.5
            if d > rc + 0.3: continue
            c = hx('7a6a4a') if d > rc - 1 else hx('fffaf0') if (dx + dy < -rc * 0.6) else hx('f3ead6') if d > rc * 0.4 else hx('5a3a22') if d > rc * 0.22 else hx('2a1a12')
            if rc * 0.4 < d < rc - 1 and int(d) % 3 == 0: c = hx('e2d6ba')               # spires du rouleau
            self.im.putpixel((cx + dx, cy + dy), c)
    # flasques du support et papier qui descend dans le boîtier
    for X in (cx - rc - 3, cx + rc + 1):
        self.r(X, cy - 2, X + 2, B0, EXP['trait']); self.r(X + 1, cy - 1, X + 1, B0, EXP['base'])
    self.r(cx + rc - 3, cy, cx + rc - 1, B0, hx('f3ead6')); self.r(cx + rc - 3, cy, cx + rc - 3, B0, hx('d8ccae'))
    # --- sortie à droite : lèvre d'airain au-dessus, deux rouleaux, le ruban passe entre eux
    self.r(X1 - 4, F0 - 3, X1 + 1, F0 - 1, EXP['trait']); self.r(X1 - 3, F0 - 2, X1, F0 - 2, EXP['clair'])
    for Yr in (F0 + 2, F1 - 2):
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                d = (dx * dx + dy * dy) ** 0.5
                if d <= 3.3: self.im.putpixel((X1 - 1 + dx, Yr + dy), EXP['trait'] if d > 2.4 else hx('9a9a92') if dx + dy < 0 else hx('4a4a46'))
Planche.etiqueteuse = _etiqueteuse

def _etiqueteuse_dessus(self, x0, x1, y0, y1, fente_y0, fente_y1, partie='tout', x1_socle=None):
    """Étiqueteuse vue du dessus (le papier est à plat, comme l'étiquette).
    partie='socle' : plateau d'airain (prolongé jusqu'à x1_socle, il passe sous l'étiquette), dégradé de lumière, ombre portée
    sur l'ardoise seulement ; partie='dessus' : bobine couchée, feuille en papier vieilli, rouleau encreur, rouleau presseur,
    engrenage à centre vide qui entraîne la bobine. Coordonnées en px d'interface. (Retours de Liam du 23 novembre.)"""
    X0, X1, Y0, Y1 = x0 * S, x1 * S - 1, y0 * S, y1 * S - 1
    F0, F1 = fente_y0 * S, fente_y1 * S - 1
    Rb0, Rb1 = X0 + 6, X0 + 6 + 17
    if partie in ('tout', 'socle'):
        XS = (x1_socle or x1) * S - 1
        # ombre portée, seulement sur l'ardoise (jamais sur le papier)
        for (a0, b0, a1, b1) in ((X0 + 3, Y1 + 1, XS + 2, Y1 + 3), (XS + 1, Y0 + 3, XS + 3, Y1 + 3)):
            for Y in range(b0, b1 + 1):
                for X in range(a0, a1 + 1):
                    c = self.im.getpixel((X, Y))
                    if c[0] + c[1] + c[2] < 300: self.im.putpixel((X, Y), ARD['ombre'])
        self.r(X0, Y0, XS, Y1, EXP['trait'])
        # dégradé très léger : plus clair en haut à gauche, plus sombre vers l'ombre (en bas à droite)
        base, sombre = EXP['base'], hx('cc8550')
        for Y in range(Y0 + 2, Y1 - 1):
            for X in range(X0 + 2, XS - 1):
                t = ((X - X0) / max(1, XS - X0) + (Y - Y0) / max(1, Y1 - Y0)) / 2
                self.im.putpixel((X, Y), tuple(int(base[i] + (sombre[i] - base[i]) * t) for i in range(3)) + (255,))
        self.r(X0 + 1, Y0 + 1, XS - 1, Y0 + 1, EXP['clair']); self.r(X0 + 1, Y0 + 1, X0 + 1, Y1 - 1, EXP['clair'])
        self.r(X0 + 1, Y1 - 1, XS - 1, Y1 - 1, EXP['mi']); self.r(XS - 1, Y0 + 1, XS - 1, Y1 - 1, EXP['mi'])
        for (X, Y) in ((X0 + 3, Y0 + 3), (XS - 3, Y0 + 3), (X0 + 3, Y1 - 3), (XS - 3, Y1 - 3)): self.rivet(X, Y)
    if partie in ('tout', 'dessus'):
        import random as _r
        rnd = _r.Random(5); PAP = [hx('f3ead6'), hx('efe4cc'), hx('f6eedc')]
        # feuille à plat, de la bobine au rouleau presseur : même papier vieilli que l'étiquette
        for Y in range(F0, F1 + 1):
            for X in range(Rb1, X1 + 1):
                self.im.putpixel((X, Y), PAP[rnd.randint(0, 2)] if rnd.random() < 0.35 else PAP[0])
        self.r(Rb1, F0, X1, F0, hx('7a6a4a')); self.r(Rb1, F1, X1, F1, hx('7a6a4a')); self.r(Rb1, F1 - 1, X1, F1 - 1, hx('d8ccae'))
        # bobine couchée
        By0, By1 = Y0 + 6, Y1 - 6
        for X in range(Rb0, Rb1 + 1):
            t = (X - Rb0) / (Rb1 - Rb0)
            c = hx('fffaf0') if t < 0.25 else hx('f3ead6') if t < 0.6 else hx('e2d6ba') if t < 0.85 else hx('c9bb9a')
            self.r(X, By0 + 4, X, By1 - 4, c)
        for Y in range(By0 + 7, By1 - 6, 6): self.r(Rb0 + 2, Y, Rb1 - 2, Y, hx('e8dcc0'))
        self.r(Rb0 - 1, By0 + 3, Rb0 - 1, By1 - 3, hx('7a6a4a')); self.r(Rb1 + 1, By0 + 3, Rb1 + 1, By1 - 3, hx('7a6a4a'))
        for Y in (By0, By1 - 3):
            self.r(Rb0 - 2, Y, Rb1 + 2, Y + 3, EXP['trait']); self.r(Rb0 - 1, Y + 1, Rb1 + 1, Y + 2, EXP['sombre']); self.r(Rb0 - 1, Y + 1, Rb1 + 1, Y + 1, EXP['base'])
        # rouleau encreur
        Re0 = (Rb1 + X1 - 8) // 2 - 3; Re1 = Re0 + 6
        for X in range(Re0, Re1 + 1):
            t = (X - Re0) / (Re1 - Re0)
            self.r(X, F0 - 2, X, F1 + 2, hx('5a5e6e') if t < 0.25 else hx('2a2c34') if t < 0.75 else hx('14151a'))
        self.r(Re0 + 1, F0 - 2, Re0 + 1, F1 + 2, hx('8a90a8'))
        for Y in (F0 - 5, F1 + 2):
            self.r(Re0 - 1, Y, Re1 + 1, Y + 3, EXP['trait']); self.r(Re0, Y + 1, Re1, Y + 2, EXP['base'])
        # rouleau presseur
        Rp0, Rp1 = X1 - 8, X1 - 1
        for X in range(Rp0, Rp1 + 1):
            t = (X - Rp0) / (Rp1 - Rp0)
            self.r(X, F0 - 3, X, F1 + 3, hx('c8ccd4') if t < 0.3 else hx('8a8e98') if t < 0.7 else hx('4a4e58'))
        self.r(Rp0 - 1, F0 - 3, Rp0 - 1, F1 + 3, hx('2a2e36')); self.r(Rp1 + 1, F0 - 3, Rp1 + 1, F1 + 3, hx('2a2e36'))
        for Y in (F0 - 7, F1 + 4):
            self.r(Rp0 - 2, Y, Rp1 + 2, Y + 3, EXP['trait']); self.r(Rp0 - 1, Y + 1, Rp1 + 1, Y + 2, EXP['base']); self.r(Rp0 - 1, Y + 1, Rp1 + 1, Y + 1, EXP['clair'])
        # engrenage à centre vide (couronne et rayons, la bobine se voit entre eux), à cheval sur le bord gauche ; pas d'arbre
        m = masque_engrenage(15, 8, moyeu=0.4, rayons=4, prof=0.22)
        gx, gy = X0 - m.width // 2 + 2, (Y0 + Y1) // 2 - m.height // 2
        for yy in range(m.height):
            for xx in range(m.width):
                if not m.getpixel((xx, yy)): continue
                u, v = xx - m.width / 2, yy - m.height / 2; d = (u * u + v * v) ** 0.5
                bord = any(not (0 <= xx + a < m.width and 0 <= yy + b < m.height) or not m.getpixel((xx + a, yy + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                c = EXP['trait'] if bord else (hx('b8b8b0') if u + v < 0 else hx('7a7a74')) if d < 5 else EXP['clair'] if u + v < -2 else EXP['base'] if u + v < 4 else EXP['mi']
                self.im.putpixel((gx + xx, gy + yy), c)
Planche.etiqueteuse_dessus = _etiqueteuse_dessus
