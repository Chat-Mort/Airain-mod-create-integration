# Textures 16 x 16 du projecteur de chantier
from PIL import Image
import numpy as np, math
def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
A = dict(r=hx('fff0c4'), c=hx('f3d694'), b=hx('e1ba6e'), m=hx('b48242'), s=hx('a8763c'), t=hx('704425'))
S = dict(c=hx('3f4350'), b=hx('363a44'), j=hx('2f333c'), s=hx('2a2e37'), o=hx('1b1e24'))
def neuf(): return Image.new('RGBA', (16, 16), (0, 0, 0, 0))

def cadre(im, x0=0, y0=0, x1=15, y1=15):
    """Cadre d'airain de 2 texels, lumière en haut à gauche."""
    p = im.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            e = min(x - x0, y - y0, x1 - x, y1 - y)
            if e == 0: p[x, y] = A['c'] if (x == x0 or y == y0) and not (x == x1 or y == y1) else A['t']
            elif e == 1: p[x, y] = A['b'] if (x - x0 == 1 or y - y0 == 1) and not (x1 - x == 1 or y1 - y == 1) else A['s']
    return im

def rivet(im, x, y):
    p = im.load(); p[x, y] = A['r']; p[x + 1, y] = A['m']; p[x, y + 1] = A['m']; p[x + 1, y + 1] = A['t']

def carter_flanc():
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16): p[x, y] = S['b']
    for y in (5, 8, 11):                                         # ouïes d'aération
        for x in range(4, 12): p[x, y] = S['o']; p[x, y - 1] = S['s']; p[x, y + 1] = S['c']
    cadre(im); rivet(im, 2, 2); rivet(im, 12, 2); rivet(im, 2, 12); rivet(im, 12, 12)
    return im

def carter_dessus():
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16): p[x, y] = A['b'] if (x + y) % 7 else A['m']
    cadre(im)
    for y in range(16):                                          # collier central
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 3.2 < d < 4.6: p[x, y] = A['t'] if x + y > 15 else A['r']
            elif d <= 3.2: p[x, y] = S['s']
    return im

def dessous():
    im = carter_dessus(); p = im.load()
    for y in range(6, 10):
        for x in range(6, 10): p[x, y] = S['o']
    return im

def tete_flanc():
    """Tambour d'ardoise à ailettes, bandes d'airain aux deux bouts."""
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16):
            p[x, y] = S['c'] if x % 3 == 0 else S['b'] if x % 3 == 1 else S['o']
    for y in (0, 1, 14, 15):
        for x in range(16): p[x, y] = A['c'] if y in (0, 14) else A['t']
    return im

def verre(allume, n=16):
    """Lentille ronde (n x n texels, en haut à gauche) : plaque d'airain, lunette sombre, verre dégradé, reflet en haut à gauche.
    Anneaux de Fresnel à partir de 12 texels. Éteinte : verre ambré sombre."""
    im = neuf(); p = im.load(); c0 = (n - 1) / 2; R = n / 2 - 0.6
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - c0, y - c0)
            if x in (0, n - 1) or y in (0, n - 1): p[x, y] = A['c'] if (x == 0 or y == 0) and not (x == n - 1 or y == n - 1) else A['t']
            elif d > R: p[x, y] = A['b'] if (x - c0) + (y - c0) < 0 else A['s']
            elif d > R - 1: p[x, y] = A['t']
            else:
                v = 1 - d / (R - 1)
                if allume: c = (255, int(178 + 72 * v), int(96 + 140 * v), 255)
                else: c = (int(70 + 30 * v), int(44 + 20 * v), int(22 + 10 * v), 255)
                if n >= 12 and int(d) % 2 == 1 and d > 1.5:
                    c = tuple(int(k * 0.9) for k in c[:3]) + (255,)
                p[x, y] = c
    h = max(1, n // 6); hx0 = int(c0 - R * 0.45)                 # reflet
    for k in range(h):
        p[hx0 + k, hx0] = (255, 255, 240, 255) if allume else hx('b08a5a')
        p[hx0, hx0 + k] = (255, 255, 240, 255) if allume else hx('b08a5a')
    return im

def verre_carre(allume):
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16):
            v = 1 - math.hypot(x - 7.5, y - 7.5) / 10
            if allume: c = (255, int(185 + 60 * v), int(105 + 110 * v), 255)
            else: c = hx('5a3a1c') if (x + y) % 4 else hx('3e2814')
            p[x, y] = c
    for k in (5, 10):                                            # grille de protection
        for i in range(16): p[k, i] = A['t']; p[i, k] = A['t']
    cadre(im)
    return im

def bras():
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16): p[x, y] = A['b'] if x < 8 else A['s']
    for y in range(16): p[0, y] = A['c']; p[15, y] = A['t']
    return im

def chapeau():
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16): p[x, y] = A['b'] if (x * 3 + y) % 11 else A['m']
    for k in (4, 7, 10):                                         # ouïes du chapeau
        for i in range(4, 12): p[i, k] = S['o']; p[i, k + 1] = A['c']
    cadre(im); rivet(im, 2, 2); rivet(im, 12, 2); rivet(im, 2, 12); rivet(im, 12, 12)
    return im

TEX = dict(l8=verre(True, 8), l8_off=verre(False, 8), l12=verre(True, 12), l12_off=verre(False, 12), chapeau=chapeau(), flanc=carter_flanc(), dessus=carter_dessus(), dessous=dessous(), tete=tete_flanc(), lentille=verre(True), lentille_off=verre(False),
           carre=verre_carre(True), carre_off=verre_carre(False), bras=bras())
