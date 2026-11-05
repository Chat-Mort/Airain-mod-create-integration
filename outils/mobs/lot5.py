"""Lot 5, les boss : le Gardien des portes (dragon), le Triple Moteur (wither), le Gardien des profondeurs (warden)."""
import random
from lot4 import *

ECHO = rampe((40, 12, 60), (80, 30, 120), (130, 60, 190), (180, 100, 240), (220, 160, 255), (245, 220, 255))

def dragon(base):
    """Écailles noires -> plaques de fonte jointées et rivetées ; crêtes grises -> laiton ; ailes -> tôle de cuivre sur longerons."""
    def regle(x, y, h, s, v):
        if s > 0.4 and 270 <= h <= 330: return None                                   # yeux violets
        aile = x < 64 and y >= 88
        if v > 0.45:                                                                   # crêtes, griffes, longerons
            return sur_rampe(LAITON, 0.25 + v*0.7)
        if aile:
            c = sur_rampe(CUIVRE, 0.08 + v*1.4)
            if (x % 12 == 0) or (y % 12 == 0): c = CUIVRE[0]                           # coutures de la tôle
            if x % 12 == 6 and y % 12 == 6: c = LAITON[4]
            return c
        decal = 4 if (y // 8) % 2 else 0                                               # plaques posées en quinconce
        c = sur_rampe(FER, 0.12 + v*2.2 + 0.08*(((x + decal)//8 + y//8) % 3 == 0))
        if (x + decal) % 8 == 0 or y % 8 == 0: c = FER[0]
        if y % 8 == 1: c = sur_rampe(FER, 0.5)                                         # arête éclairée de chaque plaque
        if (x + decal) % 8 == 4 and y % 8 == 3: c = LAITON[4]                          # rivets
        return c
    return recolorer(base, regle)

def wither(base, chaud=False):
    rnd = random.Random(55)
    def regle(x, y, h, s, v):
        if v > 0.6 and s < 0.3: return sur_rampe(LAITON, v)                            # dents, côtes -> laiton
        if chaud: return sur_rampe(rampe((60, 20, 8), (120, 40, 12), (190, 80, 20), (240, 140, 40), (255, 200, 90), (255, 240, 180)), v*1.4)
        return sur_rampe(FONTE_N, v*1.6)
    t = recolorer(base, regle); p = t.load()
    if not chaud:
        for _ in range(26):                                                            # fissures incandescentes : courts traits
            x, y = rnd.randrange(64), rnd.randrange(64); dx = rnd.choice((-1, 1))
            for i in range(3):
                xx, yy = x + i*dx, y + i
                if 0 <= xx < 64 and yy < 64 and p[xx, yy][3] and lum(p[xx, yy]) < 0.3:
                    pt(p, xx, yy, (255, 120, 30) if i == 1 else (200, 60, 16))
    for (u, v_, w) in ((0, 0, 8), (32, 0, 6)):                                         # casques : bandeau de laiton riveté
        f = faces(u, v_, w, w, w)
        for k in ("right", "front", "left", "back"):
            x0, y0, fw, fh = f[k]
            for x in range(fw): pt(p, x0+x, y0+1, LAITON[3] if x % 2 else LAITON[1])
            pt(p, x0, y0+1, LAITON[5]); pt(p, x0+fw-1, y0+1, LAITON[5])
        xt, yt, fw, fd = f["top"]
        for i in range(fw): pt(p, xt+i, yt+fd//2, LAITON[2])
        rect(p, xt+fw//2-1, yt+fd//2-1, 2, 2, LAITON[4])
    for y in range(22, 26):                                                            # côtes : barres de laiton
        for x in range(0, 24):
            c = p[x, y]
            if c[3] and lum(c) > 0.15: pt(p, x, y, LAITON[3] if (y % 2) else LAITON[1])
    for (u, v_, w) in ((0, 0, 8), (32, 0, 6)):                                         # yeux des trois têtes : braises
        f = faces(u, v_, w, w, w); x0, y0, fw, fh = f["front"]
        for x in range(fw):
            c = p[x0+x, y0+fh//2 - 1]
            if c[3] and lum(c) < 0.25: pt(p, x0+x, y0+fh//2 - 1, (255, 140, 30))
    return t

def warden(base):
    """Le sculk devient de l'Écho : chair sombre -> fonte, bleu-vert -> violet, côtes -> tuyaux de laiton."""
    def regle(x, y, h, s, v):
        if s < 0.35 and v > 0.55: return sur_rampe(LAITON, v)                          # côtes et cornes -> laiton
        if 160 <= h <= 200 and s > 0.35: return sur_rampe(ECHO, v*1.1)                 # bioluminescence -> Écho
        return sur_rampe(FER, 0.1 + v*2.2)
    return recolorer(base, regle)

def couche_echo(base):
    def regle(x, y, h, s, v): return sur_rampe(ECHO, 0.3 + v*0.7)
    return recolorer(base, regle)
