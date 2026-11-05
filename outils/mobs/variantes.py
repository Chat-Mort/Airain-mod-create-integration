"""Variantes : ouvriers ensablés et noyés, automates givrés, moussus et de fonte noire, araignée de cuivre."""
import colorsys, random
from details import *

GIVRE = rampe((40, 52, 64), (70, 88, 104), (104, 124, 140), (146, 166, 182), (190, 208, 222), (232, 242, 250))
BRONZE = rampe((40, 32, 18), (72, 58, 30), (106, 88, 48), (138, 118, 66), (166, 148, 92), (196, 182, 130))
FONTE_N = rampe((10, 10, 12), (20, 19, 22), (32, 30, 34), (46, 44, 48), (64, 60, 64), (86, 80, 82))
SABLE = (214, 190, 140)

def lum(c): return (0.3*c[0] + 0.59*c[1] + 0.11*c[2]) / 255
def est_laiton(c):
    h, s, v = colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
    return 0.06 < h < 0.15 and s > 0.3

def remapper(t, pal, garder=()):
    p = t.load()
    for y in range(t.height):
        for x in range(t.width):
            c = p[x, y]
            if c[3] == 0 or c[:3] in garder: continue
            if est_laiton(c): p[x, y] = sur_rampe(pal, lum(c)*1.15) + (c[3],)
    return t

def yeux(t, positions, couleur):
    p = t.load()
    for (x, y) in positions: p[x, y] = couleur + (255,)
    return t

OEIL_ZOMBIE = ((9, 11), (10, 11), (13, 11), (14, 11))      # rangée de la visière (face avant : y0 = 8, ligne 3)
OEIL_SQUELETTE = ((9, 12), (10, 12), (13, 12), (14, 12))

def membres_gauches(t):
    """Modèles 64 x 64 à membres gauches séparés (noyé) : on recopie bras et jambe droits."""
    for (src, dst) in (((40, 16), (32, 48)), ((0, 16), (16, 48))):
        bloc = t.crop((src[0], src[1], src[0]+16, src[1]+16)); t.paste(bloc, dst)
    return t

def husk_v3(base_zombie):
    t = zombie_v3(base_zombie); p = t.load(); rnd = random.Random(4)
    for y in range(t.height):
        for x in range(t.width):
            c = p[x, y]
            if c[3] == 0 or (x, y) in OEIL_ZOMBIE: continue
            k = 0.28 + (0.25 if rnd.random() < 0.12 else 0)
            p[x, y] = tuple(int(c[i] + (SABLE[i]-c[i])*k) for i in range(3)) + (c[3],)
    return t

def noye_v3(base_zombie):
    t = zombie_v3(base_zombie); p = t.load(); rnd = random.Random(6)
    for y in range(t.height):
        for x in range(t.width):
            c = p[x, y]
            if c[3] == 0: continue
            v = sur_rampe(VERT_DE_GRIS, lum(c)*1.2)
            k = 0.55 if rnd.random() < 0.7 else 0.25
            p[x, y] = tuple(int(c[i] + (v[i]-c[i])*k) for i in range(3)) + (c[3],)
    yeux(t, OEIL_ZOMBIE, (80, 230, 210))
    return membres_gauches(t)

def stray_v3(base):
    t = remapper(squelette_v3(base), GIVRE, garder=((255, 150, 40), (200, 70, 20), (255, 180, 60), (255, 140, 40), (230, 110, 30)))
    yeux(t, OEIL_SQUELETTE, (150, 220, 255)); return t

def stray_habit(base):
    """Le manteau en lambeaux devient une bâche givrée ; la capuche est retirée pour montrer la tête."""
    def regle(x, y, h, s, v): return sur_rampe(GIVRE, v*0.75)
    t = recolorer(base, regle); p = t.load()
    for y in range(16):
        for x in range(64): p[x, y] = (0, 0, 0, 0)
    return t

def bogged_v3(base):
    t = remapper(squelette_v3(base), BRONZE, garder=((255, 150, 40), (200, 70, 20)))
    p = t.load(); rnd = random.Random(2)
    for y in range(t.height):
        for x in range(t.width):
            if p[x, y][3] and rnd.random() < 0.16: p[x, y] = rnd.choice(((58, 92, 40), (78, 112, 52), (44, 70, 34))) + (255,)
    yeux(t, OEIL_SQUELETTE, (170, 230, 90)); return t

def wither_v3(base):
    t = remapper(squelette_v3(base), FONTE_N, garder=((255, 150, 40), (200, 70, 20), (255, 180, 60), (255, 140, 40), (230, 110, 30)))
    p = t.load(); rnd = random.Random(8)
    for y in range(t.height):                                   # fissures incandescentes
        for x in range(t.width):
            if p[x, y][3] and lum(p[x, y]) < 0.2 and rnd.random() < 0.05: p[x, y] = (230, 90, 20, 255)
    yeux(t, OEIL_SQUELETTE, (255, 120, 20)); return t

def araignee_cuivre(base):
    return araignee_v3(base, metal=rampe((30, 14, 8), (60, 28, 16), (98, 48, 28), (140, 70, 42), (176, 98, 62), (206, 130, 90)), accent=VERT_DE_GRIS)
