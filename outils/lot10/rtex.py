# Relais cinétique d'airain : textures 16 x 16 (obsidienne, filets d'airain, œil de l'Ender)
import sys, math
sys.path.insert(0, '/home/claude/travail/lot9')
import importlib.util as _u
_s = _u.spec_from_file_location("ptex", "/home/claude/travail/lot9/tex.py"); _m = _u.module_from_spec(_s); _s.loader.exec_module(_m)
A, S, neuf, cadre, rivet, hx = _m.A, _m.S, _m.neuf, _m.cadre, _m.rivet, _m.hx
# A, S, neuf, cadre, rivet, hx
from PIL import Image
OB = [hx('5a3f8a'), hx('3b2a5a'), hx('2a1e44'), hx('1d1530'), hx('0f0b19')]     # obsidienne : reflet -> fond
VIO = [hx('f0c8ff'), hx('c77dff'), hx('9b4fd6'), hx('6a2fa0')]                     # lueur violette
OEIL_V = [hx('d8ffe8'), hx('7fe0b0'), hx('2fa57a'), hx('17664a'), hx('0b2e22')]      # œil de l'Ender

def obsidienne(seed=3):
    """Obsidienne régulière (rien de répété en grand) : fond sombre, quelques éclats violets."""
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16):
            v = ((x * 374761393 + y * 668265263 + seed * 2147483647) ^ ((x * 31 + y * 17 + seed) * 1274126177)) % 23
            p[x, y] = OB[4] if v < 9 else OB[3] if v < 17 else OB[2] if v < 21 else OB[1]
    for (x, y) in ((4, 5), (11, 3), (9, 11), (3, 12), (13, 9)):
        p[x, y] = OB[0]
    return im

def flanc(fentes=True):
    """Face de côté : obsidienne dans un cadre d'airain, fente de lueur violette."""
    im = obsidienne(); p = im.load()
    if fentes:
        for y in range(4, 12):
            p[7, y] = VIO[2]; p[8, y] = VIO[1]
        p[7, 4] = p[8, 4] = VIO[3]; p[7, 11] = p[8, 11] = VIO[3]
    cadre(im); rivet(im, 2, 2); rivet(im, 12, 2); rivet(im, 2, 12); rivet(im, 12, 12)
    return im

def oeil(actif=True, pal=None):
    """Face avant : œil de l'Ender dans une lunette d'airain sur obsidienne (pal : couleurs de l'iris)."""
    OEIL = pal or OEIL_V
    im = obsidienne(5); p = im.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 5.2 < d <= 6.4: p[x, y] = A['c'] if x + y < 15 else A['s']
            elif 4.4 < d <= 5.2: p[x, y] = A['t']
            elif d <= 4.4:
                if not actif: p[x, y] = OB[2] if d > 2 else OB[3]; continue
                p[x, y] = OEIL[3] if d > 3.8 else OEIL[1] if d > 2.6 else OEIL[2]
                if x in (7, 8) and abs(y - 7.5) < 3: p[x, y] = OEIL[4]     # pupille fendue
    if actif: p[5, 5] = OEIL[0]; p[6, 5] = OEIL[0]
    cadre(im)
    return im

def arbre():
    """Face de l'arbre : collier d'airain, trou carré."""
    im = obsidienne(7); p = im.load()
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5))
            if 3 < d <= 5: p[x, y] = A['b'] if x + y < 15 else A['s']
            elif d <= 3: p[x, y] = S['o']
    cadre(im)
    return im

def dessus():
    im = obsidienne(9); p = im.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 2.5 < d < 3.6: p[x, y] = VIO[1] if x + y < 15 else VIO[2]
            elif d <= 2.5: p[x, y] = VIO[0] if d < 1.2 else VIO[1]
    cadre(im); rivet(im, 2, 2); rivet(im, 12, 2); rivet(im, 2, 12); rivet(im, 12, 12)
    return im

OEIL_R = [hx('ffe6ff'), hx('d89cff'), hx('a45ee0'), hx('6a2fa0'), hx('240c3c')]   # récepteur : iris violet
TEX = dict(oeil_r=oeil(True, OEIL_R), flanc=flanc(), oeil=oeil(True), oeil_off=oeil(False), arbre=arbre(), dessus=dessus(), obs=obsidienne())
