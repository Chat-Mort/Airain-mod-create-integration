"""Lot 3, version détaillée : chaque machine reçoit ses détails face par face."""
import random
from lot3 import *

def rect(p, x0, y0, w, h, c):
    for y in range(h):
        for x in range(w): pt(p, x0+x, y0+y, c)
def cadre(p, x0, y0, w, h, clair, sombre):
    for x in range(w): pt(p, x0+x, y0, clair); pt(p, x0+x, y0+h-1, sombre)
    for y in range(h): pt(p, x0, y0+y, clair); pt(p, x0+w-1, y0+y, sombre)
BRAISE, BRAISE2, BRAISE3 = (255, 196, 80), (255, 130, 30), (190, 50, 14)

# ---------------- FOURNAISE VOLANTE (blaze)
def fournaise_v3(base):
    t = fournaise(base); p = t.load()
    tete = faces(0, 0, 8, 8, 8)
    x0, y0, _, _ = tete["front"]
    rect(p, x0, y0, 8, 8, LAITON[2]); cadre(p, x0, y0, 8, 8, LAITON[4], LAITON[0])
    for x in (2, 5): pt(p, x0+x, y0+2, BRAISE); pt(p, x0+x+1, y0+2, BRAISE2)             # fentes des yeux
    rect(p, x0+1, y0+4, 6, 3, FER[0]); cadre(p, x0+1, y0+4, 6, 3, LAITON[1], LAITON[1])     # porte du foyer
    for x in (2, 4): pt(p, x0+x, y0+5, BRAISE2)
    pt(p, x0+3, y0+5, BRAISE); pt(p, x0+5, y0+5, BRAISE3)
    for k in ("right", "left"):                                                             # ouïes d'aération
        xs, ys, _, _ = tete[k]
        rect(p, xs, ys, 8, 8, LAITON[2]); cadre(p, xs, ys, 8, 8, LAITON[4], LAITON[0])
        for y in (2, 4, 6):
            for x in range(2, 6): pt(p, xs+x, ys+y, FER[0])
        rivet(p, xs+1, ys+1); rivet(p, xs+6, ys+1)
    xb, yb, _, _ = tete["back"]
    rect(p, xb, yb, 8, 8, LAITON[2]); cadre(p, xb, yb, 8, 8, LAITON[4], LAITON[0]); cadran(p, xb+2, yb+2); cadran(p, xb+5, yb+4)
    xt, yt, _, _ = tete["top"]
    rect(p, xt, yt, 8, 8, LAITON[3]); cadre(p, xt, yt, 8, 8, LAITON[5], LAITON[1])
    rect(p, xt+2, yt+2, 4, 4, FER[0]); pt(p, xt+3, yt+3, BRAISE); pt(p, xt+4, yt+4, BRAISE2)    # cheminée
    tige = faces(0, 16, 2, 8, 2)
    for (x0, y0, w, h) in cotes(tige):
        for y in range(h):
            for x in range(w): pt(p, x0+x, y0+y, CUIVRE[3] if x == 0 else CUIVRE[1])
        for x in range(w): pt(p, x0+x, y0, LAITON[4]); pt(p, x0+x, y0+3, FER[2]); pt(p, x0+x, y0+h-1, BRAISE2)
    xb, yb, w, d = tige["bottom"]
    rect(p, xb, yb, w, d, BRAISE)
    return t

# ---------------- COFFRE-SENTINELLE (shulker)
def coffre_v3(base):
    t = coffre_sentinelle(base); p = t.load()
    def plaque(x0, y0, w, h, bandes=True):
        for y in range(h):
            for x in range(w): pt(p, x0+x, y0+y, sur_rampe(LAITON, 0.5 + 0.12*((y % 4) == 0) - 0.05*(x % 2)))
        cadre(p, x0, y0, w, h, LAITON[4], LAITON[0])
        if bandes:
            for y in range(h):
                for x in (0, 1, w-2, w-1): pt(p, x0+x, y0+y, FER[2] if x in (1, w-2) else FER[3])
            for y in range(1, h-1, 3): rivet(p, x0+1, y0+y); rivet(p, x0+w-2, y0+y)
    couvercle = faces(0, 0, 16, 12, 16)
    for k in ("right", "front", "left", "back"): plaque(*couvercle[k])
    x0, y0, _, _ = couvercle["front"]
    rect(p, x0+6, y0+5, 4, 5, FER[1]); cadre(p, x0+6, y0+5, 4, 5, LAITON[5], FER[0])       # serrure
    pt(p, x0+7, y0+7, (10, 8, 8)); pt(p, x0+8, y0+7, (10, 8, 8)); pt(p, x0+7, y0+8, (10, 8, 8))
    xt, yt, w, d = couvercle["top"]
    plaque(xt, yt, w, d, bandes=False)
    for i in range(w): pt(p, xt+i, yt+7, FER[2]); pt(p, xt+i, yt+8, FER[3]); pt(p, xt+7, yt+i, FER[2]); pt(p, xt+8, yt+i, FER[3])
    rect(p, xt+6, yt+6, 4, 4, LAITON[5]); rect(p, xt+7, yt+7, 2, 2, FER[0])                 # évent central
    socle = faces(0, 28, 16, 8, 16)
    for k in ("right", "front", "left", "back"):
        x0, y0, w, h = socle[k]
        plaque(x0, y0, w, h)
        for x in range(w): pt(p, x0+x, y0+h-2, FER[1]); pt(p, x0+x, y0+h-1, FER[0])
    tete = faces(0, 52, 6, 6, 6)
    for k in tete:
        x0, y0, w, h = tete[k]; rect(p, x0, y0, w, h, FER[2]); cadre(p, x0, y0, w, h, FER[3], FER[0])
    x0, y0, _, _ = tete["front"]
    cadre(p, x0+1, y0+1, 4, 4, LAITON[4], LAITON[1])
    pt(p, x0+2, y0+2, BRAISE); pt(p, x0+3, y0+2, BRAISE2); pt(p, x0+2, y0+3, BRAISE2); pt(p, x0+3, y0+3, BRAISE3)   # œil-lentille
    return t

# ---------------- SENTINELLE DU VIDE (enderman)
def sentinelle_v3(base):
    t = sentinelle(base); p = t.load()
    VIO, VIO2 = (204, 110, 255), (140, 60, 200)
    tete = faces(0, 0, 8, 8, 8)
    x0, y0, _, _ = tete["front"]
    for x in range(8): pt(p, x0+x, y0+1, LAITON[1])                                          # bord de casque
    for (x, y) in ((0, 0), (7, 0), (0, 7), (7, 7)): rivet(p, x0+x, y0+y)
    xt, yt, _, _ = tete["top"]
    for i in range(8): pt(p, xt+i, yt+4, LAITON[1]); pt(p, xt+4, yt+i, LAITON[1])
    corps = faces(32, 16, 8, 12, 4)
    xf, yf, _, _ = corps["front"]
    cadre(p, xf+2, yf+3, 4, 4, LAITON[4], LAITON[0])                                         # cœur du vide
    pt(p, xf+3, yf+4, VIO); pt(p, xf+4, yf+4, VIO2); pt(p, xf+3, yf+5, VIO2); pt(p, xf+4, yf+5, VIO)
    xb, yb, _, _ = corps["back"]
    for y in range(12): pt(p, xb+3, yb+y, CUIVRE[2]); pt(p, xb+4, yb+y, CUIVRE[0])           # colonne en tuyau
    membre = faces(56, 0, 2, 30, 2)
    for (x0, y0, w, h) in cotes(membre):
        for y in (13, 14, 28):
            for x in range(w): pt(p, x0+x, y0+y, LAITON[4] if y != 14 else FER[0])            # genoux / coudes, pieds
        pt(p, x0, y0+13, LAITON[5])
    return t

# ---------------- GELÉE D'HUILE (slime)
def gelee_v3(base):
    t = gelee(base); p = t.load(); rnd = random.Random(21)
    ext = faces(0, 0, 8, 8, 8)
    for k in ext:
        x0, y0, w, h = ext[k]
        for _ in range(3):                                                                    # bulles et reflets
            x, y = rnd.randint(1, w-2), rnd.randint(1, h-2)
            c = p[x0+x, y0+y]; pt(p, x0+x, y0+y, (240, 200, 120)); p[x0+x, y0+y] = (240, 200, 120, c[3])
    coeur = faces(0, 16, 6, 6, 6)
    for k in coeur:
        x0, y0, w, h = coeur[k]
        rect(p, x0, y0, w, h, FER[1]); cadre(p, x0, y0, w, h, LAITON[3], LAITON[0])            # cœur : un rouage noyé
        pt(p, x0+2, y0+2, LAITON[4]); pt(p, x0+3, y0+3, LAITON[2]); pt(p, x0+2, y0+3, FER[0]); pt(p, x0+3, y0+2, FER[0])
    for (u, v) in ((32, 0), (32, 4)):                                                         # yeux : boulons de laiton
        f = faces(u, v, 2, 2, 2)
        for k in f:
            x0, y0, w, h = f[k]; rect(p, x0, y0, w, h, LAITON[3]); pt(p, x0, y0, LAITON[5])
    return t

# ---------------- CREUSET (cube de magma)
def creuset_v3(base):
    t = creuset(base); p = t.load(); rnd = random.Random(31)
    for y in range(t.height):
        for x in range(t.width):
            c = p[x, y]
            if c[3] and lum(c) < 0.35 and x % 4 == 1 and y % 4 == 1: pt(p, x, y, LAITON[3])  # rivets alignés sur la fonte
    for x in range(0, 32):                                                                    # cerclage de laiton du bord supérieur
        if p[x, 0][3]: pt(p, x, 0, LAITON[3])
    return t

# ---------------- GARDIENS DES MARÉES
def gardien_v3(base, ancien=False):
    t = gardien(base, ancien); p = t.load()
    plaque = BRONZE if ancien else CUIVRE
    tete = faces(0, 0, 12, 12, 16)
    x0, y0, _, _ = tete["front"]
    for (x, y) in [(x, y) for x in range(12) for y in range(12)]:
        dx, dy = x - 5.5, y - 5.5; r = (dx*dx + dy*dy) ** 0.5
        if 3.2 < r < 4.6: pt(p, x0+x, y0+y, LAITON[4] if dx + dy < 0 else LAITON[1])          # hublot autour de l'œil
        elif r <= 3.2: pt(p, x0+x, y0+y, (30, 60, 70) if r > 1.6 else (60, 110, 120))
    for (x, y) in ((1, 1), (10, 1), (1, 10), (10, 10)): rivet(p, x0+x, y0+y)
    for (u, v) in ((16, 40),):                                                                # plaques haut et bas : trappe à volant
        f = faces(u, v, 12, 2, 12)
        xt, yt, w, d = f["top"]
        for (x, y) in [(x, y) for x in range(12) for y in range(12)]:
            dx, dy = x - 5.5, y - 5.5; r = (dx*dx + dy*dy) ** 0.5
            if 2.5 < r < 4: pt(p, xt+x, yt+y, (200, 40, 28) if abs(dx) > 1 and abs(dy) > 1 else (150, 24, 18))
            elif r < 1.5: pt(p, xt+x, yt+y, FER[3])
    nag = faces(25, 19, 1, 9, 9)                                                               # nageoire -> hélice de laiton
    for k in ("right", "left"):
        x0, y0, w, h = nag[k]
        for y in range(h):
            for x in range(w):
                pale = abs(x - 4) <= 1 or abs(y - 4) <= 1
                pt(p, x0+x, y0+y, (LAITON[4] if (x+y) % 3 else LAITON[2]) if pale else FER[1])
        pt(p, x0+4, y0+4, FER[3])
    return t

# ---------------- TURBINE (breeze) : recoloration + cerclages et rivets répartis
def turbine_v3(base):
    t = turbine(base); p = t.load()
    for y in range(t.height):
        for x in range(t.width):
            c = p[x, y]
            if not c[3]: continue
            if y % 4 == 0 and lum(c) > 0.4: pt(p, x, y, LAITON[3])
            if (x + y*3) % 9 == 0 and lum(c) > 0.5: pt(p, x, y, LAITON[5])
    return t

# ---------------- SCARABÉES (silverfish, endermite)
SEG_SILVER = [((3, 2, 2), (0, 0)), ((4, 3, 2), (0, 4)), ((6, 4, 3), (0, 9)), ((3, 3, 3), (0, 16)), ((2, 2, 3), (0, 22)), ((2, 1, 2), (11, 0)), ((1, 1, 2), (13, 4))]
SEG_ENDERMITE = [((4, 3, 2), (0, 0)), ((6, 4, 5), (0, 5)), ((3, 3, 1), (0, 14)), ((1, 2, 1), (0, 18))]
def scarabee_v3(base, segments, oeil=None):
    t = Image.new("RGBA", base.size, (0, 0, 0, 0)); p = t.load(); src = base.convert("RGBA").load()
    for y in range(base.height):
        for x in range(base.width):
            if src[x, y][3]: pt(p, x, y, FER[2])
    for i, ((w, h, d), (u, v)) in enumerate(segments):
        f = faces(u, v, w, h, d)
        pal = LAITON if i % 2 else FER
        for k in f:
            x0, y0, fw, fh = f[k]
            for y in range(fh):
                for x in range(fw): pt(p, x0+x, y0+y, sur_rampe(pal, 0.75 - 0.35*(y/max(1, fh-1)) if pal is LAITON else 0.55 - 0.3*(y/max(1, fh-1))))
        xt, yt, fw, fd = f["top"]
        if fw >= 3 and fd >= 2: pt(p, xt+fw//2, yt+fd//2, LAITON[5] if pal is FER else FER[0])     # rivet ou trou de vis
    if oeil:
        x0, y0, fw, fh = faces(*segments[0][1], *segments[0][0])["front"]
        pt(p, x0, y0+1, oeil); pt(p, x0+fw-1, y0+1, oeil)
    for (u, v, w, h, d) in ((20, 0, 10, 8, 3), (20, 11, 6, 4, 3), (20, 18, 6, 5, 2)) if segments is SEG_SILVER else ():
        f = faces(u, v, w, h, d)                                                                 # carapaces dorsales du silverfish
        for k in f:
            x0, y0, fw, fh = f[k]
            for y in range(fh):
                for x in range(fw): pt(p, x0+x, y0+y, LAITON[3] if (x % 3) else LAITON[1])
    return t

# ---------------- ÂME DE L'ÉCHO (phantom)
def ame_v3(base):
    t = ame_echo(base); p = t.load(); rnd = random.Random(17)
    for y in range(t.height):
        for x in range(t.width):
            c = p[x, y]
            if not c[3]: continue
            if rnd.random() < 0.08: pt(p, x, y, (210, 160, 255))                                   # étincelles d'Écho
            elif (x + 2*y) % 7 == 0 and lum(c) > 0.3: pt(p, x, y, (160, 100, 220))                 # veines
    return t
