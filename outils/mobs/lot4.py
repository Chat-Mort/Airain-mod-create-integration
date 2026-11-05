"""Lot 4, le Nether : les forges de l'Empire se sont rallumées."""
import random
from lot3b import *

TOILE_CLAIRE = rampe((150, 132, 104), (184, 166, 134), (212, 196, 164), (230, 218, 190), (242, 234, 214), (250, 246, 234))
CORDE = rampe((44, 30, 18), (70, 50, 30), (100, 74, 44), (130, 100, 62))

# ---------------- GHAST -> ballon de garde (enveloppe cousue, hublots, trappe de foyer, amarres)
def ballon(base, tir=False):
    t = Image.new("RGBA", base.size, (0, 0, 0, 0)); p = t.load(); src = base.convert("RGBA").load()
    for y in range(32):
        for x in range(64):
            if src[x, y][3] == 0: continue
            if x < 16 and y < 16:                                                    # amarres (tentacules)
                pt(p, x, y, CORDE[2] if (x + y) % 3 else CORDE[1]); continue
            r, g, b, a = src[x, y]
            lumi = (r+g+b)/765
            c = sur_rampe(TOILE_CLAIRE, 0.25 + lumi*0.7)
            if x % 4 == 0: c = TOILE_CLAIRE[0]                                       # coutures des fuseaux
            pt(p, x, y, c)
    corps = faces(0, 0, 16, 16, 16)
    for k in ("right", "front", "left", "back"):
        x0, y0, w, h = corps[k]
        for x in range(w): pt(p, x0+x, y0+11, LAITON[4] if x % 2 else LAITON[2]); pt(p, x0+x, y0+12, CORDE[1])   # sangle de gréement
        for x in range(0, w, 4): rivet(p, x0+x+1, y0+11)
    x0, y0, _, _ = corps["front"]
    for (cx, cy) in ((4, 6), (11, 6)):                                               # hublots
        for (dx, dy) in [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if abs(dx) + abs(dy) <= 3]:
            bord = abs(dx) == 2 or abs(dy) == 2
            col = LAITON[4] if bord else ((255, 70, 40) if tir else (40, 50, 60)) if (dx, dy) != (-1, -1) else ((255, 200, 160) if tir else (150, 170, 180))
            pt(p, x0+cx+dx, y0+cy+dy, col)
    for x in range(5, 11):                                                            # trappe de foyer
        for y in range(13, 16):
            ouverte = tir and 6 <= x <= 9 and y >= 14
            pt(p, x0+x, y0+y, (255, 150, 40) if ouverte and (x+y) % 2 else (210, 60, 20) if ouverte else FER[1] if y > 13 else LAITON[2])
    xt, yt, _, _ = corps["top"]
    for (x, y) in ((7, 7), (8, 7), (7, 8), (8, 8)): pt(p, xt+x, yt+y, LAITON[3])     # soupape de sommet
    return t

# ---------------- HOGLIN -> bélier à vapeur ; ZOGLIN -> bélier rouillé
def belier(base, rouille=False):
    rnd = random.Random(41)
    def regle(x, y, h, s, v):
        if v > 0.85 and s < 0.2: return (255, 150, 40) if not rouille else (120, 230, 200)       # yeux
        if s < 0.25 and v > 0.6: return sur_rampe(LAITON, v)                                      # défenses -> laiton
        if v < 0.3: return sur_rampe(CUIVRE if not rouille else VERT_DE_GRIS, v*2.2)              # crinière -> tuyaux
        if 80 <= h <= 160: return sur_rampe(VERT_DE_GRIS, v)                                      # végétation (zoglin)
        base_ = ROUILLE if rouille else FER
        c = sur_rampe(base_, 0.25 + v*0.75)
        if x % 8 == 0 or y % 8 == 0: c = base_[1]                                                 # joints des plaques
        if x % 8 == 4 and y % 8 == 4: c = LAITON[5]                                               # rivets
        return c
    t = recolorer(base, regle)
    if rouille:
        p = t.load()
        for y in range(t.height):
            for x in range(t.width):
                if p[x, y][3] and rnd.random() < 0.05: pt(p, x, y, VERT_DE_GRIS[2])
    return t

# ---------------- PIGLINS -> forgerons de l'abîme (automates de bronze), brute en fonte, zombifié rouillé
def forgeron(base, variante="piglin"):
    peau = {"piglin": BRONZE, "brute": FONTE_N, "zombie": ROUILLE}[variante]
    def regle(x, y, h, s, v):
        if 40 <= h <= 60 and s > 0.5: return sur_rampe(LAITON, v)                                 # or -> laiton
        if 80 <= h <= 160 and s > 0.25: return sur_rampe(VERT_DE_GRIS, v)                          # pourriture -> vert-de-gris
        if s < 0.18 and v > 0.75: return sur_rampe(LAITON, v*0.9)                                  # os -> rouages de laiton
        if (h < 34 or h > 330) and s > 0.12 and v > 0.58: return sur_rampe(peau, 0.05 + v*0.75)       # peau -> métal
        if (h < 45 or h > 330) and v <= 0.58: return sur_rampe(CORDE if variante != "brute" else FER, v*1.6)   # cuir
        return None
    t = recolorer(base, regle); p = t.load()
    tete = faces(0, 0, 10, 8, 8)
    x0, y0, _, _ = tete["front"]
    for x in range(10): pt(p, x0+x, y0+1, peau[1])                                                 # joint du front
    for (x, y) in ((0, 0), (9, 0), (0, 7), (9, 7)): rivet(p, x0+x, y0+y)
    for x in (2, 3, 6, 7):
        c = p[x0+x, y0+3]
        if lum(c) > 0.55 or lum(c) < 0.15: pt(p, x0+x, y0+3, (255, 150, 40) if x in (2, 7) else (220, 90, 20))   # yeux de braise
    xt, yt, _, _ = tete["top"]
    for i in range(10): pt(p, xt+i, yt+4, peau[1])
    for i in range(8): pt(p, xt+5, yt+i, peau[1])
    for (x, y) in ((1, 1), (8, 1), (1, 6), (8, 6)): rivet(p, xt+x, yt+y)
    for k in ("right", "left", "back"):
        xs, ys, w, h = tete[k]
        for x in range(w): pt(p, xs+x, ys+1, peau[1])
        for (x, y) in ((1, 3), (w-2, 3)): rivet(p, xs+x, ys+y)
        if k != "back":
            for (x, y) in ((3, 4), (4, 4), (3, 5), (4, 5)): pt(p, xs+x, ys+y, LAITON[3] if (x+y) % 2 else LAITON[1])
    bras = faces(40, 16, 4, 12, 4)
    bande(p, cotes(bras), 1); bande(p, cotes(bras), 9)
    groin = faces(31, 1, 4, 4, 1)
    x0, y0, w, h = groin["front"]
    for y in range(h):
        for x in range(w): pt(p, x0+x, y0+y, FER[3] if x in (0, w-1) or y in (0, h-1) else (FER[0] if x % 2 else FER[2]))   # respirateur
    corps = faces(16, 16, 8, 12, 4)
    xb, yb, _, _ = corps["back"]
    for y in range(1, 10):
        for x in range(2, 6): pt(p, xb+x, yb+y, CUIVRE[3] if x == 2 else CUIVRE[2] if x < 5 else CUIVRE[0])   # chaudière dorsale
    cadran(p, xb+3, yb+4)
    if variante == "zombie":
        xf, yf, _, _ = corps["front"]
        for y in (3, 5, 7):
            for x in range(2, 6): pt(p, xf+x, yf+y, LAITON[3] if x % 2 else FER[0])               # mécanisme à nu
    return t
