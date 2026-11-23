# Lot 4 de la passe qualité : blocs faibles (marquages au sol, émail, verres) et objets liés.
# Toutes les textures restent en 16 px, comme le reste des blocs du pack.
import math, os, sys
from PIL import Image

T = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures'

def hx(s): return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))

# Bruit déterministe par pixel (même graine = même texture à chaque génération)
def bruit(x, y, g=0):
    n = (x * 374761393 + y * 668265263 + g * 2147483647) & 0xffffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

# Bruit doux et périodique sur 16 (raccord parfait d'un bloc à l'autre)
def doux(x, y, g=0, p=4):
    def v(i, j): return bruit(i % (16 // p), j % (16 // p), g)
    fx, fy = x / p, y / p
    i, j = int(math.floor(fx)), int(math.floor(fy)); u, w = fx - i, fy - j
    u = u * u * (3 - 2 * u); w = w * w * (3 - 2 * w)
    a = v(i, j) * (1 - u) + v(i + 1, j) * u
    b = v(i, j + 1) * (1 - u) + v(i + 1, j + 1) * u
    return a * (1 - w) + b * w

def teinte(c, k):
    return tuple(max(0, min(255, round(v * k))) for v in c[:3])

def vers(c, d, t):
    return tuple(round(c[i] + (d[i] - c[i]) * t) for i in range(3))

# ---------- Peinture de sol ----------
# Une couleur, trois nuances : la peinture usée prend la teinte de la poussière (pas de noir).
PEINTURES = {
    'white':  dict(base=hx('e9e4d6'), clair=hx('f6f2e7'), use=hx('c9c2b0')),
    'yellow': dict(base=hx('e2ad22'), clair=hx('f0c544'), use=hx('b88a24')),
    'red':    dict(base=hx('b8342a'), clair=hx('cf4a3b'), use=hx('8f2a24')),
    'black':  dict(base=hx('2b2a28'), clair=hx('383633'), use=hx('46423b')),
}

def peindre(masque, nom, g, ecaille=0.06, passage=None):
    """masque : fonction (x, y) -> True si peint. passage : zone (x, y) -> 0..1 plus usée (piétinement)."""
    P = PEINTURES[nom]; im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); px = im.load()
    for y in range(16):
        for x in range(16):
            if not masque(x, y): continue
            bord = any(not masque(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if 0 <= x + dx < 16 and 0 <= y + dy < 16)
            r = bruit(x, y, g); u = doux(x, y, g + 7) + (passage(x, y) if passage else 0) * 0.5
            # écailles : la peinture manque sur quelques pixels, surtout aux bords et aux endroits piétinés
            if r < ecaille * (0.55 if bord else 0.12) * (1 + u): continue
            c = P['base']
            if u > 0.8: c = vers(c, P['use'], min(0.45, (u - 0.8) * 1.5))
            elif r > 0.93: c = P['clair']
            c = teinte(c, 0.97 + 0.06 * bruit(x, y, g + 3))
            px[x, y] = c + (255,)
    return im

def ligne(nom):
    # Seules la colonne x 7-8 et la rangée y 7-8 servent au modèle (bras et centre de la ligne)
    return peindre(lambda x, y: 7 <= x <= 8 or 7 <= y <= 8, nom, {'white': 11, 'yellow': 12, 'red': 13}[nom])

def fleche(nom):
    def m(x, y):
        if 9 <= y <= 14: return 6 <= x <= 9                 # fût
        if 1 <= y <= 8:  return abs(x - 7.5) <= (y - 0.5)   # pointe
        return False
    return peindre(m, nom, {'white': 21, 'yellow': 22}[nom], passage=lambda x, y: max(0, 1 - abs(y - 10) / 5))

def passage_pieton():
    return peindre(lambda x, y: (1 <= x <= 4 or 11 <= x <= 14) and 1 <= y <= 14, 'white', 31,
                   passage=lambda x, y: max(0, 1 - abs(y - 7.5) / 6))

def hachures(nom):
    # Bandes en diagonale de 4 px, raccord sur 16 dans les deux sens ; le fond est peint lui aussi
    fond = 'white' if nom == 'red' else 'black'
    a = peindre(lambda x, y: ((x + y) // 4) % 2 == 0, nom, 41 if nom == 'red' else 42, ecaille=0)
    b = peindre(lambda x, y: ((x + y) // 4) % 2 == 1, fond, 43 if nom == 'red' else 44, ecaille=0)
    b.alpha_composite(a)
    # le fond reste opaque (le bloc couvre le sol) : on bouche les rares trous avec la teinte usée
    px = b.load()
    for y in range(16):
        for x in range(16):
            if px[x, y][3] == 0:
                px[x, y] = PEINTURES[nom if ((x + y) // 4) % 2 == 0 else fond]['use'] + (255,)
    return b

# ---------- Émail ----------
# L'émail est teinté par le jeu (multiplication) et carrelé tous les 16 px sur les grands tableaux :
# il reste presque blanc et sans motif repérable, avec juste une glaçure légère.
def email(mat):
    im = Image.new('RGBA', (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16):
            if mat:
                v = 236 + round(6 * doux(x, y, 51, 2) + 4 * bruit(x, y, 52))
            else:
                v = 242 + round(7 * doux(x, y, 53, 8) + 3 * doux(x, y, 54, 4))
                if bruit(x, y, 55) > 0.985: v -= 6               # rares piqûres de cuisson
            px[x, y] = (v, v, max(0, v - 3), 255)
    return im

# ---------- Verre d'airain ----------
# Verre soufflé à peine ambré : nuages de teinte, deux reflets en diagonale qui se raccordent, sans bulles (elles passaient pour de la poussière).
def verre_airain():
    im = Image.new('RGBA', (16, 16)); px = im.load()
    base = hx('a9a690'); clair = hx('eef0e2'); chaud = hx('c2b27c')
    for y in range(16):
        for x in range(16):
            n = doux(x, y, 61, 8)
            c = vers(base, chaud, max(0, n - 0.4) * 1.1); a = 78 + round(24 * n)
            d = (x + y) % 16
            k = {2: 0.25, 3: 0.55, 4: 0.6, 5: 0.3, 11: 0.3}.get(d)
            if k:                                                 # reflets en biseau (raccord sur 16)
                c = vers(c, clair, k); a += round(48 * k)
            px[x, y] = c + (a,)
    return im

# ---------- Verre d'écho ----------
# Côté Écho : argent et améthyste. Vitre presque claire, voile violet très léger, éclats d'améthyste et d'argent.
AME = dict(clair=hx('e6d4ff'), base=hx('b48ce6'), sombre=hx('7a52b8'))
ARGENT = hx('e8ecf2')
def verre_echo():
    im = Image.new('RGBA', (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16):
            n = doux(x, y, 71, 8)
            px[x, y] = vers(hx('cbbde8'), hx('e4dcf4'), n) + (round(18 + 22 * n),)
    for x0, y0, L in ((3, 8, 4), (11, 14, 4)):                   # éclats en diagonale
        for k in range(L):
            px[x0 + k, y0 - k] = (AME['clair'] if k == L - 1 else ARGENT if k % 2 else AME['base']) + (230,)
    for x, y in ((3, 10), (12, 3), (13, 4)):
        px[x, y] = AME['base'] + (200,)
    return im

def verre_echo_bord():
    # Le pourtour givré : pierre de lune pâle, veinée d'améthyste (remplace le givre cyan)
    im = Image.new('RGBA', (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16):
            n = doux(x, y, 81, 4) * 0.7 + bruit(x, y, 82) * 0.3
            c = vers(hx('b9b6c9'), hx('dcd9e6'), n)
            v = abs(doux(x, y, 83, 4) * 0.6 + doux(x, y, 84, 2) * 0.4 - 0.5)                      # veines : le long des lignes de niveau
            if v < 0.04: c = vers(c, AME['base'], 0.45)
            elif v < 0.08: c = vers(c, AME['clair'], 0.4)
            px[x, y] = c + (255,)
    return im

# ---------- Objets ----------
def rouleau(nom):
    # Rouleau de ruban de marquage : un cylindre court vu de trois quarts (dessus + tranche), le bout posé à plat
    P = PEINTURES[nom]; im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); px = im.load()
    trait = teinte(P['use'], 0.55) if nom != 'white' else hx('857f6e')
    carton = hx('a88457'); carton_s = hx('6e5232')
    def dans(x, y, cx, cy, rx, ry): return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
    cx, cy, rx, ry, h = 7.5, 5.5, 6.5, 4.2, 4                          # ellipse du dessus, tranche de 4 px
    for y in range(16):
        for x in range(16):
            haut = dans(x, y, cx, cy, rx, ry); tranche = any(dans(x, y - k, cx, cy, rx, ry) for k in range(h + 1))
            if haut:
                if dans(x, y, cx, cy, 2.2, 1.5): continue                  # trou du mandrin
                if dans(x, y, cx, cy, 3.2, 2.2): c = carton                # mandrin
                elif not dans(x, y, cx, cy, rx - 1, ry - 1): c = trait     # arête
                else:
                    c = P['clair'] if y < cy - 1 else P['base']
                    if dans(x, y, cx, cy, 4.9, 3.3) and not dans(x, y, cx, cy, 4.3, 2.8): c = teinte(c, 0.93)   # spire
                px[x, y] = c + (255,)
            elif tranche:
                bord = not any(dans(x, y - k, cx, cy, rx - 1, ry - 1) for k in range(h + 1)) or not tranche
                c = P['base'] if x < cx - 2 else P['use']
                if bord or not any(dans(x, y - k, cx, cy, rx, ry) for k in range(h)): c = trait
                px[x, y] = c + (255,)
    # le trou laisse voir le fond du mandrin
    for y in range(16):
        for x in range(16):
            if dans(x, y, cx, cy, 2.2, 1.5) and dans(x, y - 1, cx, cy, 2.2, 1.5): px[x, y] = carton_s + (255,)
    for x in range(12, 16):                                             # bout de ruban posé à plat
        for y, c in ((12, P['clair']), (13, P['base']), (14, trait)):
            if px[x, y][3] == 0 or x >= 13: px[x, y] = c + (255,)
    return im

AIRAIN = dict(fce=hx('fce9b7'), clair=hx('f3d694'), haut=hx('e1ba6e'), base=hx('c99b52'), bas=hx('b07e40'), trait=hx('704425'), noir=hx('57331d'))
EMAUX = {1: (hx('fff6d0'), hx('e8c46e'), hx('8a5a20')), 3: (hx('d4ecff'), hx('8cbef0'), hx('4a78b0')), 4: (hx('ff9a88'), hx('d64030'), hx('8e1a16'))}

def renfort(n):
    # Ferrure d'airain neuf : plaque à pans coupés, n cabochons (pas de rivets : ils se confondaient avec le niveau) d'émail (or, or, bleu, rouge comme en jeu)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); px = im.load()
    x0, x1, y0, y1 = 1, 15, 5, 10                                     # 15 px de large : centre exact en x 8
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x in (x0, x1)) and (y in (y0, y1)): continue             # pans coupés
            if x in (x0, x1) or y in (y0, y1) or (x in (x0 + 1, x1 - 1) and y in (y0, y1)): c = AIRAIN['trait']
            elif y == y0 + 1 or x == x0 + 1: c = AIRAIN['clair']
            elif y == y1 - 1 or x == x1 - 1: c = AIRAIN['bas']
            else: c = AIRAIN['haut'] if y == y0 + 2 else AIRAIN['base']
            px[x, y] = c + (255,)
    cl, ba, so = EMAUX[1 if n < 3 else n]
    pas = 2
    debut = (x0 + x1) // 2 - (n - 1)                              # cabochons centrés au pixel près
    for k in range(n):                                                  # cabochons de 1x2, reflet en haut
        x = debut + k * pas
        px[x, 7] = cl + (255,); px[x, 8] = so + (255,)
    # ombre portée sous la plaque, pour le volume dans la case
    return im

SORTIES = {
    # 'block/white_floor_line': lambda: ligne('white'),
    # 'block/yellow_floor_line': lambda: ligne('yellow'),
    # 'block/red_floor_line': lambda: ligne('red'),
    # 'block/white_floor_arrow': lambda: fleche('white'),
    # 'block/yellow_floor_arrow': lambda: fleche('yellow'),
    # 'block/white_floor_crossing': passage_pieton,
    # 'block/red_hazard_stripes': lambda: hachures('red'),
    # 'block/yellow_hazard_stripes': lambda: hachures('yellow'),
    'block/enamel': lambda: email(False),
    'block/enamel_matte': lambda: email(True),
    'block/airain_glass': verre_airain,
    'block/echo_glass': verre_echo,
    'block/echo_glass_edge': verre_echo_bord,
    'item/white_floor_line': lambda: rouleau('white'),
    'item/yellow_floor_line': lambda: rouleau('yellow'),
    'item/red_floor_line': lambda: rouleau('red'),
    'item/rack_reinforcement_1': lambda: renfort(1),
    'item/rack_reinforcement_2': lambda: renfort(2),
    'item/rack_reinforcement_3': lambda: renfort(3),
    'item/rack_reinforcement_4': lambda: renfort(4),
}

if __name__ == '__main__':
    dest = sys.argv[2] if len(sys.argv) > 2 else '/tmp/l4/apres'
    for k, f in SORTIES.items():
        os.makedirs(os.path.join(dest, os.path.dirname(k)), exist_ok=True)
        f().save(os.path.join(dest, k + '.png'))
    print(len(SORTIES), 'textures ->', dest)
