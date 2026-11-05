"""Lot 3 : les machines (gardiens des marées, fournaise, turbine, coffre-sentinelle, scarabées, sentinelle du vide,
gelée d'huile, creuset) et les âmes de l'Écho (phantom)."""
import random
from variantes import *

VIOLET = rampe((22, 10, 34), (44, 20, 66), (74, 36, 104), (110, 60, 146), (150, 96, 190), (200, 150, 230))
HUILE = rampe((30, 18, 6), (64, 38, 12), (104, 64, 20), (146, 96, 34), (190, 134, 54), (230, 180, 90))

def gardien(base, ancien=False):
    """Écailles -> plaques de cuivre (bronze pour l'ancien) ; les motifs sombres d'origine deviennent du vert-de-gris."""
    rnd = random.Random(12)
    plaque = BRONZE if ancien else CUIVRE
    def regle(x, y, h, s, v):
        if 15 <= h <= 45 and s > 0.4: return sur_rampe(LAITON, v)                         # épines -> laiton
        if (not ancien and 120 <= h <= 200) or (ancien and s < 0.35 and v > 0.25):
            if v < (0.42 if not ancien else 0.55): return sur_rampe(VERT_DE_GRIS, v*1.3)    # motifs -> vert-de-gris
            return sur_rampe(plaque, 0.35 + v*0.6)
        return None
    t = recolorer(base, regle); p = t.load()
    for y in range(t.height):
        for x in range(t.width):
            if p[x, y][3] and x % 6 == 2 and y % 6 == 2 and not (8 <= x < 12 and y < 4):
                p[x, y] = LAITON[5] + (255,)
    return t

def fournaise(base):
    def regle(x, y, h, s, v):
        if v < 0.32: return (255, 170, 50) if y < 16 else sur_rampe(FER, v*2)            # yeux et bouche : foyer
        if y >= 16: return sur_rampe(CUIVRE, v*0.7)                                       # tiges -> tuyaux de cuivre
        return sur_rampe(LAITON, v*0.72)
    t = recolorer(base, regle); p = t.load()
    for x in range(0, 32):                                                                # cerclages des tuyaux
        for y in (17, 21):
            if p[x, y][3]: p[x, y] = FER[2] + (255,)
    for x in range(8, 16):                                                                # grille de foyer sur le front
        if p[x, 13][3]: p[x, 13] = (FER[1] if x % 2 else (230, 90, 20)) + (255,)
    return t

def turbine(base):
    def regle(x, y, h, s, v):
        if s > 0.35: return sur_rampe(LAITON, v)
        return sur_rampe(GIVRE, v*0.9)
    return recolorer(base, regle)

def vapeur(base):
    def regle(x, y, h, s, v): return sur_rampe(rampe((150, 150, 156), (190, 190, 196), (230, 230, 236)), v)
    return recolorer(base, regle)

def coffre_sentinelle(base):
    def regle(x, y, h, s, v):
        if y >= 52: return (255, 160, 50) if v < 0.45 else sur_rampe(FER, v*0.8)         # tête : noyau sombre, yeux de braise
        if 250 <= h <= 330: return sur_rampe(LAITON, v*1.05)
        return None
    t = recolorer(base, regle); p = t.load()
    for y in range(0, 52):
        for x in range(64):
            if p[x, y][3] and x % 8 == 0 and y % 4 == 2: p[x, y] = LAITON[5] + (255,)      # rivets
    return t

def scarabee(base, glow=None):
    def regle(x, y, h, s, v):
        if glow and s > 0.4 and v > 0.45: return glow
        return sur_rampe(LAITON if (x // 4) % 2 else FER, v*1.1)
    return recolorer(base, regle)

def sentinelle(base):
    def regle(x, y, h, s, v):
        if s > 0.4: return None                                                          # yeux violets
        c = sur_rampe(FER, v*3.2)
        if x % 8 == 0 or y % 12 == 0: c = LAITON[1]                                      # joints de laiton
        return c
    return recolorer(base, regle)

def gelee(base):
    def regle(x, y, h, s, v):
        if v < 0.25: return (40, 24, 8)
        return sur_rampe(HUILE, v)
    return recolorer(base, regle)

def creuset(base):
    def regle(x, y, h, s, v):
        if v < 0.3: return sur_rampe(FER, v*2.5)
        if h < 18 and v < 0.62: return sur_rampe(ROUILLE, v)
        return None                                                                      # le métal en fusion reste
    return recolorer(base, regle)

def ame_echo(base):
    def regle(x, y, h, s, v): return sur_rampe(VIOLET, v*1.1)
    return recolorer(base, regle)

def yeux_echo(base):
    def regle(x, y, h, s, v): return (230, 140, 255)
    return recolorer(base, regle)
