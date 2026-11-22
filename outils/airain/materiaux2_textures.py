# Maquettes des nouveaux matériaux : marbre redessiné (blanc et noir), nouvelles ardoises, piliers raccordés.
# Toutes les textures sont raccordables (bruit périodique sur 16 px).
import math, random, os
from PIL import Image
T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
OUT = '/home/claude/travail/materiaux2/tex/'; os.makedirs(OUT, exist_ok=True)
def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def bruit(seed, x, y):
    """Nuage périodique (16 px) : somme d'ondes à fréquences entières, phases tirées au sort."""
    r = random.Random(seed); v = 0; tot = 0
    for (fx, fy, a) in ((1, 0, 1), (0, 1, 1), (1, 1, .8), (1, -1, .8), (2, 1, .5), (1, 2, .5), (2, -1, .4), (3, 2, .25), (2, 3, .25)):
        ph = r.random() * 6.283
        v += a * math.sin(2 * math.pi * (fx * x + fy * y) / 16 + ph); tot += a
    return v / tot           # environ -1..1

MARBRE = {'blanc': (hx('d6d0c4'), hx('e7e2d7'), hx('f3efe7'), hx('b9b1a3')),     # sombre, base, clair, veine
          'noir': (hx('141317'), hx('1e1c22'), hx('2b2830'), hx('4a4552'))}
OR = (hx('8a6420'), hx('c79a3e'), hx('ecc874'))

def veine(r, p, col, n, force):
    """Veine courte et fine (4 à 7 px), qui serpente un peu ; s'efface aux bouts."""
    x, y = r.randrange(16), r.randrange(16); dx, dy = r.choice([(1, 0), (1, 1), (0, 1), (1, -1)])
    for k in range(n):
        t = force * (1 - abs(k - n / 2) / (n / 2 + 1))
        p[x % 16, y % 16] = mix(p[x % 16, y % 16], col, t)
        if r.random() < .45: x += dy if r.random() < .5 else 0; y += dx if r.random() < .5 else 0
        x += dx; y += dy

def marbre(nom, v):
    """Raccord sans couture entre toutes les variantes : un fond commun (bruit périodique sur 16 px, le même pour les 6)
    sur les bords, et une nuance propre à chaque variante seulement au cœur du bloc (fondue en sinus vers les bords).
    Deux variantes voisines ont donc exactement les mêmes pixels de bord."""
    S, B, C, V = MARBRE[nom]
    k = .6                                               # nuance douce, la même pour les deux teintes
    im = Image.new('RGB', (16, 16)); p = im.load()
    for y in range(16):
        for x in range(16):
            # fenêtre en sinus : presque nulle sur les bords (écart entre variantes < 1 niveau de couleur), pleine au cœur
            f = math.sin(math.pi * (x + .5) / 16) * math.sin(math.pi * (y + .5) / 16)
            n = .35 * bruit(0 if nom == 'blanc' else 100, x, y) + f * .7 * bruit(v * 7 + 11 + (0 if nom == 'blanc' else 100), x, y)
            p[x, y] = mix(B, C if n > 0 else S, min(1, abs(n) * k))
    return im

def biseau(p, x0, y0, x1, y1, cl, so, f=.45):
    for x in range(x0, x1 + 1): p[x, y0] = mix(p[x, y0], cl, f); p[x, y1] = mix(p[x, y1], so, f)
    for y in range(y0, y1 + 1): p[x0, y] = mix(p[x0, y], cl, f); p[x1, y] = mix(p[x1, y], so, f)

def poli(nom):
    """Marbre poli : la même pierre, en 4 dalles de 8 ; chaque dalle a son biseau (clair en haut/gauche, sombre en bas/droite),
    comme l'ardoise de Liam, donc les joints tombent pile entre les pixels 7 et 8, au centre du bloc."""
    im = marbre(nom, 3); p = im.load(); S, B, C, V = MARBRE[nom]
    fonce = mix(S, (0, 0, 0), .12 if nom == 'blanc' else .5)
    for ox in (0, 8):
        for oy in (0, 8): biseau(p, ox, oy, ox + 7, oy + 7, C, fonce, .7)
    return im

# ---------------------------------------------------------------- piliers : bande d'or seulement aux bouts d'une colonne
def pilier(nom, haut, bas):
    src = Image.open(T + nom + '_marble_pillar.png').convert('RGB'); im = src.copy(); p = im.load(); s = src.load()
    corps = [s[x, 6] for x in range(16)]                  # une ligne du fût, sans or
    lignes = []
    if not haut: lignes += [0, 1]
    if not bas: lignes += [14, 15]
    for y in lignes:
        for x in range(16): p[x, y] = corps[x]
    return im

# ---------------------------------------------------------------- ardoises
ARD = Image.open(T + 'slate.png').convert('RGB')           # l'ardoise de Liam : sa teinte, ses biseaux
_a = ARD.load(); _int = sorted((_a[x, y] for x in range(1, 15) for y in range(1, 15)), key=sum)
A = {'creux': _int[0], 'plein': _int[-1], 'clair': _a[1, 0], 'fonce': _a[8, 15], 'joint': mix(_a[8, 15], (0, 0, 0), .25)}
def grain(seed=0):
    """Fond d'ardoise sans les arêtes de la texture d'origine (qui, décalées, faisaient des lignes hors du centre)."""
    im = Image.new('RGB', (16, 16)); p = im.load()
    for y in range(16):
        for x in range(16): p[x, y] = mix(A['creux'], A['plein'], .5 + .5 * bruit(300 + seed, x, y))
    return im
def tuile(p, x0, y0, x1, y1, f=.75):
    """Biseau d'une pierre, à la manière de l'ardoise de Liam : colonne gauche claire et colonne droite sombre sur toute
    la hauteur, ligne du haut claire et ligne du bas sombre entre les deux."""
    for y in range(y0, y1 + 1):
        p[x0 % 16, y % 16] = mix(p[x0 % 16, y % 16], A['clair'], f); p[x1 % 16, y % 16] = mix(p[x1 % 16, y % 16], A['fonce'], f)
    for x in range(x0 + 1, x1):
        p[x % 16, y0 % 16] = mix(p[x % 16, y0 % 16], A['clair'], f); p[x % 16, y1 % 16] = mix(p[x % 16, y1 % 16], A['fonce'], f)

def briques_ardoise():
    im = grain(1); p = im.load()
    for r in range(4):
        d = 0 if r % 2 == 0 else 4
        for k in range(-1, 2): tuile(p, k * 8 + d, r * 4, k * 8 + d + 7, r * 4 + 3)
    return im

def petites_dalles():
    im = grain(2); p = im.load()
    for ox in range(0, 16, 4):
        for oy in range(0, 16, 4): tuile(p, ox, oy, ox + 3, oy + 3, .5)
    return im

def ardoise_taillee():
    """Deux pierres taillées pleine largeur, joint au centre exact du bloc."""
    im = grain(3); p = im.load()
    tuile(p, 0, 0, 15, 7); tuile(p, 0, 8, 15, 15)
    return im

def chevrons():
    """Chevrons : moitié gauche en lames obliques, moitié droite en miroir, raccord au centre (entre 7 et 8)."""
    im = grain(4); p = im.load(); g = im.copy().load()
    for y in range(16):
        for x in range(8):
            u = (x + y) % 4                         # lames de 4 en oblique
            c = g[x, y]
            if u == 0: c = mix(c, A['clair'], .55)
            elif u == 3: c = mix(c, A['fonce'], .75)
            p[x, y] = c
            # moitié droite : miroir exact
            u2 = u; c2 = g[15 - x, y]
            if u2 == 0: c2 = mix(c2, A['clair'], .55)
            elif u2 == 3: c2 = mix(c2, A['fonce'], .75)
            p[15 - x, y] = c2
    for y in range(16): p[7, y] = mix(p[7, y], A['fonce'], .6); p[8, y] = mix(p[8, y], A['clair'], .4)
    for y in range(16): p[0, y] = mix(p[0, y], A['clair'], .4); p[15, y] = mix(p[15, y], A['fonce'], .6)
    return im

def ardoise_ciselee():
    """Dalle à cadre en creux et rouage gravé, centré sur le bloc (centre 7,5 ; 7,5)."""
    im = grain(5); p = im.load()
    tuile(p, 0, 0, 15, 15, .8)
    # cadre en creux : inversé (sombre en haut/gauche, clair en bas/droite)
    for x in range(2, 14): p[x, 2] = mix(p[x, 2], A['fonce'], .6); p[x, 13] = mix(p[x, 13], A['clair'], .5)
    for y in range(3, 13): p[2, y] = mix(p[2, y], A['fonce'], .6); p[13, y] = mix(p[13, y], A['clair'], .5)
    def rouage(x, y):
        d = math.hypot(x - 7.5, y - 7.5); a = math.atan2(y - 7.5, x - 7.5)
        return 1.6 < d < 4.4 + 1.1 * (math.cos(a * 8) > .3)
    # rouage en relief : contour gravé, face légèrement éclairée
    for y in range(16):
        for x in range(16):
            if not rouage(x, y): continue
            bord = any(not rouage(x + i, y + j) for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            p[x, y] = mix(p[x, y], A['joint'], .6) if bord else mix(p[x, y], A['clair'], .18)
    return im

def pilier_ardoise(haut=True, bas=True):
    """Fût cannelé : 4 cannelures de 4 px (clair à gauche, creux à droite), bague aux bouts d'une colonne."""
    im = grain(6); p = im.load()
    for y in range(16):
        for x in range(16):
            k = x % 4
            p[x, y] = mix(p[x, y], A['clair'] if k == 0 else A['fonce'], (.45, 0, .2, .7)[k])
    for (on, y0) in ((haut, 0), (bas, 14)):
        if on:
            for x in range(16): p[x, y0] = A['clair']; p[x, y0 + 1] = A['fonce']
    return im

def ardoise_pilier_bout():
    """Dessus/dessous du pilier d'ardoise : dalle biseautée avec un cercle de fût."""
    im = grain(7); p = im.load(); tuile(p, 0, 0, 15, 15)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 5.2 < d < 6.3: p[x, y] = mix(p[x, y], A['fonce'], .6)
    return im

TEX = {}
for n in ('blanc', 'noir'):
    for v in range(6): TEX[f'marbre_{n}_{v}'] = marbre(n, v)
    TEX[f'marbre_{n}_poli'] = poli(n)
    for h in (True, False):
        for b in (True, False): TEX[f'pilier_{n}_{int(h)}{int(b)}'] = pilier({'blanc': 'white', 'noir': 'black'}[n], h, b)
TEX.update({'ardoise_briques': briques_ardoise(), 'ardoise_dalles': petites_dalles(), 'ardoise_taillee': ardoise_taillee(),
            'ardoise_chevrons': chevrons(), 'ardoise_ciselee': ardoise_ciselee(), 'ardoise_pilier': pilier_ardoise(), 'ardoise_pilier_bout': ardoise_pilier_bout()})
for k, im in TEX.items(): im.save(OUT + k + '.png')
print(len(TEX))
