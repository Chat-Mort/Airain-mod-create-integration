"""Lot C, le Nether et les boss."""
import random, math, colorsys
from atelier import *
import lot5

def F(b): return faces(*b)
P_TETE, P_GROIN, P_CORPS = (0, 0, 10, 8, 8), (31, 1, 4, 4, 1), (16, 16, 8, 12, 4)
P_BRAS, P_BRAS_G, P_JAMBE, P_JAMBE_G = (40, 16, 4, 12, 4), (32, 48, 4, 12, 4), (0, 16, 4, 12, 4), (16, 48, 4, 12, 4)
P_OREILLES = ((51, 6, 1, 5, 4), (39, 6, 1, 5, 4))

def piglin_base(peau, cuir, accent):
    t = Toile((64, 64))
    for b in (P_TETE, P_CORPS, P_BRAS, P_BRAS_G) + P_OREILLES: t.boite(*b, metal(peau, 0.5, 0.05, graine=31), force=True)
    for b in (P_JAMBE, P_JAMBE_G): t.boite(*b, lambda i, j, w, h, f: ramp(cuir, 0.45 + 0.05*((i+j) % 2) - 0.15*(j >= 10)), force=True)
    g = t.boite(*P_GROIN, metal(FER, 0.45), force=True)
    x, y, w, h = g["front"]
    for j in range(h):
        for i in range(w): t.pt(x+i, y+j, FER[3] if i in (0, w-1) or j in (0, h-1) else (FER[0] if i % 2 else FER[2]), True)   # respirateur
    x, y, _, _ = F(P_TETE)["front"]
    for (i, c) in ((2, BRAISE[1]), (3, BRAISE[2]), (6, BRAISE[2]), (7, BRAISE[1])): t.pt(x+i, y+3, c, True)
    for (i, j) in ((0, 0), (9, 0), (0, 7), (9, 7)): t.rivet(x+i, y+j, accent, True)
    for k in COTES:
        x, y, w, h = F(P_CORPS)[k]; t.ligne_h(x, y+8, w, cuir[1], True); t.pt(x+w//2, y+8, accent[4], True)   # ceinture
    return t

def forgeron():
    t = piglin_base(LAQUE_ROUGE, CUIR, LAITON)
    x, y, w, h = F(P_CORPS)["front"]
    t.rect(x+1, y+2, 6, 10, lambda i, j: ramp(CUIR, 0.5 - 0.02*j), True)                          # tablier de cuir
    xb, yb, _, _ = F(P_CORPS)["back"]                                                             # soufflet
    for j in range(1, 11):
        for i in range(1, 7):
            pli = j % 2 == 0
            t.pt(xb+i, yb+j, CUIR[1] if pli else CUIR[3], True)
    t.rect(xb+1, yb+1, 6, 1, (120, 84, 50), True); t.rect(xb+1, yb+10, 6, 1, (120, 84, 50), True)
    t.pt(xb+3, yb+11, LAITON[4], True); t.pt(xb+4, yb+11, LAITON[2], True)
    for k in COTES:
        for b in (P_BRAS, P_BRAS_G):
            x, y, w, h = F(b)[k]; t.rect(x, y+8, w, 4, lambda i, j: ramp(CUIR, 0.4 - 0.05*j), True)  # gants de forge
    return t.im

def garde():
    t = piglin_base(EMAIL_NOIR, FER, OR)
    for b in (P_TETE, P_CORPS, P_BRAS, P_BRAS_G):
        for k in COTES:
            x, y, w, h = F(b)[k]; t.ligne_h(x, y, w, OR[3], True); t.ligne_h(x, y+h-1, w, OR[1], True)   # filets d'or
    x, y, w, d = F(P_TETE)["up"]
    for j in range(d): t.pt(x+4, y+j, OR[4], True); t.pt(x+5, y+j, OR[2], True)                   # crête du casque
    x, y, w, h = F(P_CORPS)["front"]
    t.disque(x+4, y+4, 2.2, lambda r, a: OR[4] if r > 1.2 else EMAIL_NOIR[1], True)                  # médaillon
    return t.im

def calcine():
    BRULE = R((14, 10, 8), (28, 20, 14), (46, 32, 22), (66, 46, 30), (88, 62, 40), (110, 80, 52))
    t = piglin_base(BRULE, BRULE, LAITON); rnd = random.Random(33)
    for _ in range(140):                                                                           # craquelures de l'émail
        x, y = rnd.randrange(64), rnd.randrange(64)
        if t.get(x, y)[3]: t.pt(x, y, BRAISE[3] if rnd.random() < 0.25 else BRULE[4])
    x, y, w, h = F(P_CORPS)["front"]
    for (cx, cy, r) in ((3, 4, 2.2), (5.5, 7.5, 1.8)):                                             # rouages à nu
        t.disque(x+cx, y+cy, r, lambda rr, a: LAITON[4] if (rr > r-0.8 and int(a/30) % 2) else LAITON[2] if rr > 0.7 else FER[0], True)
    return t.im

def belier(rouille=False):
    v = vanilla("hoglin/zoglin.png" if rouille else "hoglin/hoglin.png"); src = v.load()
    t = Toile(v.size, v); rnd = random.Random(44)
    tole = ROUILLE if rouille else LAQUE_ROUGE
    for y in range(v.height):
        for x in range(v.width):
            c = src[x, y]
            if not c[3]: continue
            h, s, l = colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255); h *= 360
            if l > 0.85 and s < 0.2: col = (255, 150, 40) if not rouille else (150, 240, 220)          # yeux
            elif s < 0.25 and l > 0.6: col = ramp(LAITON, l)                                       # défenses -> chasse-pierres
            elif l < 0.3: col = ramp(SUIE, l*2)                                                    # crinière -> cheminée, charbon
            elif 80 <= h <= 160: col = ramp(VDG, l)
            else:
                col = ramp(tole, 0.25 + l*0.7)
                if x % 8 == 0 or y % 8 == 0: col = SUIE[1]                                         # joints noirs
                if x % 8 == 4 and y % 8 == 4: col = LAITON[5]
                if rouille and rnd.random() < 0.05: col = SUIE[0]                                  # plaques arrachées
            t.pt(x, y, col)
    return t.im

def gardien_portes():
    """Ender Dragon : corps d'obsidienne, ailes en vitraux violets sertis de laiton."""
    v = vanilla("enderdragon/dragon.png"); src = v.load(); t = Toile(v.size, v); rnd = random.Random(55)
    GERMES = [(rnd.randrange(0, 64), rnd.randrange(88, 200)) for _ in range(46)]
    VERRES = [(110, 40, 170), (150, 60, 210), (80, 30, 140), (180, 90, 230), (60, 40, 150), (130, 30, 120), (200, 120, 240)]
    for y in range(v.height):
        for x in range(v.width):
            c = src[x, y]
            if not c[3]: continue
            h, s, l = colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255); h *= 360
            if s > 0.4 and 270 <= h <= 330: t.pt(x, y, c); continue                                # yeux
            aile = x < 64 and y >= 88
            if aile:
                if l > 0.45: t.pt(x, y, LAITON[4] if (x+y) % 2 else LAITON[2]); continue           # longerons
                d = sorted(((x-gx)**2 + (y-gy)**2, n) for n, (gx, gy) in enumerate(GERMES))
                if d[1][0] - d[0][0] < 9: t.pt(x, y, LAITON[1]); continue                          # plombs du vitrail
                teinte = VERRES[d[0][1] % len(VERRES)]
                t.pt(x, y, mix(teinte, (255, 255, 255), 0.18) if (x + 2*y) % 11 == 0 else teinte); continue
            if l > 0.45: t.pt(x, y, ramp(OBSIDIENNE, 0.75 + 0.2*(y % 2))); continue                # crêtes : arêtes brillantes
            col = ramp(OBSIDIENNE, 0.25 + l*1.8)
            if rnd.random() < 0.04: col = OBSIDIENNE[4]                                            # reflets violets
            if x % 8 == 0 or y % 8 == 0: col = OBSIDIENNE[0]
            t.pt(x, y, col)
    return t.im

LOT_C = {
    "piglin/piglin.png": forgeron,
    "piglin/piglin_brute.png": garde,
    "piglin/zombified_piglin.png": calcine,
    "hoglin/hoglin.png": lambda: belier(False),
    "hoglin/zoglin.png": lambda: belier(True),
    "enderdragon/dragon.png": gardien_portes,
    "wither/wither.png": lambda: lot5.wither(vanilla("wither/wither.png")),
    "wither/wither_invulnerable.png": lambda: lot5.wither(vanilla("wither/wither_invulnerable.png"), True),
    "warden/warden.png": lambda: lot5.warden(vanilla("warden/warden.png")),
    "warden/warden_bioluminescent_layer.png": lambda: lot5.couche_echo(vanilla("warden/warden_bioluminescent_layer.png")),
    "warden/warden_heart.png": lambda: lot5.couche_echo(vanilla("warden/warden_heart.png")),
    "warden/warden_pulsating_spots_1.png": lambda: lot5.couche_echo(vanilla("warden/warden_pulsating_spots_1.png")),
    "warden/warden_pulsating_spots_2.png": lambda: lot5.couche_echo(vanilla("warden/warden_pulsating_spots_2.png")),
}
