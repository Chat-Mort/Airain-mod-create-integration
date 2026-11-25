# Relais cinétique d'airain, allure retenue : cage d'arêtes noir netherite, rivets d'airain aux huit coins,
# cœur d'obsidienne à fentes violettes, œil de l'Ender devant, arbre en retrait derrière.
import math
from PIL import Image
import rtex
from rtex import OB, VIO, OEIL_V, OEIL_R, hx, A, neuf
NE = [hx('6b6468'), hx('4d474b'), hx('3a3538'), hx('2a2629'), hx('1a1719')]   # netherite : reflet -> ombre

def arete():
    """Barre de netherite : reflet en haut à gauche, ombre en bas à droite."""
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16):
            p[x, y] = NE[1] if (x + y) % 9 else NE[2]
            if x == 0 or y == 0: p[x, y] = NE[0]
            if x == 1 or y == 1: p[x, y] = NE[1]
    return im

def coin():
    """Coin de la cage : rivet d'airain sur netherite (chaque face de coin fait 2 x 2 texels, en haut à gauche)."""
    im = arete(); p = im.load()
    p[0, 0] = A['r']; p[1, 0] = A['c']; p[0, 1] = A['c']; p[1, 1] = A['s']
    return im

def coeur(fente=True, seed=3):
    """Face du cœur : obsidienne, fente violette (texels 2 à 13 visibles entre les arêtes)."""
    im = rtex.obsidienne(seed); p = im.load()
    if fente:
        for y in range(4, 12): p[7, y] = VIO[2]; p[8, y] = VIO[1]
        p[7, 4] = p[8, 4] = VIO[3]; p[7, 11] = p[8, 11] = VIO[3]
    return im

def oeil(pal):
    im = rtex.obsidienne(5); p = im.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 4.4 < d <= 5.6: p[x, y] = NE[0] if x + y < 15 else NE[3]          # lunette de netherite
            elif d <= 4.4:
                if pal is None: p[x, y] = OB[2] if d > 2 else OB[3]; continue    # œil fermé
                p[x, y] = pal[3] if d > 3.8 else pal[1] if d > 2.6 else pal[2]
                if x in (7, 8) and abs(y - 7.5) < 3: p[x, y] = pal[4]
    if pal: p[5, 5] = pal[0]; p[6, 5] = pal[0]
    return im

def dos():
    """Face arrière : obsidienne, collier de netherite autour du passage de l'arbre."""
    im = rtex.obsidienne(7); p = im.load()
    for y in range(16):
        for x in range(16):
            dd = max(abs(x - 7.5), abs(y - 7.5))
            if 2.5 < dd <= 4: p[x, y] = NE[1] if x + y < 15 else NE[3]
            elif dd <= 2.5: p[x, y] = hx('0a080c')
    return im

def dessus():
    im = rtex.obsidienne(9); p = im.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 2.5 < d < 3.6: p[x, y] = VIO[1] if x + y < 15 else VIO[2]
            elif d <= 2.5: p[x, y] = VIO[0] if d < 1.2 else VIO[1]
    return im

TEX = dict(arete=arete(), coin=coin(), coeur=coeur(), oeil=oeil(OEIL_V), oeil_r=oeil(OEIL_R), oeil_off=oeil(None), dos=dos(), dessus=dessus())
