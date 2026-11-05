"""Détails mécaniques peints par-dessus la recoloration, face par face (UV « box »)."""
import random
from peindre import *

def faces(u, v, w, h, d):
    return {"top": (u+d, v, w, d), "bottom": (u+d+w, v, w, d), "right": (u, v+d, d, h),
            "front": (u+d, v+d, w, h), "left": (u+d+w, v+d, d, h), "back": (u+2*d+w, v+d, w, h)}

def cotes(f): return [f[k] for k in ("right", "front", "left", "back")]
def pt(p, x, y, c): p[x, y] = tuple(c[:3]) + (255,)
def rivet(p, x, y): pt(p, x, y, LAITON[5])

def bande(p, rects, ligne, rampe=LAITON, clair=4, sombre=2):
    """Un cerclage d'une ligne de haut, tout autour d'une boîte."""
    for (x0, y0, w, h) in rects:
        for x in range(w): pt(p, x0+x, y0+ligne, rampe[clair] if x % 3 else rampe[sombre])

# ======================= ZOMBIE : ouvrier rouillé
def zombie_v2(base):
    t = zombie(base); p = t.load()
    tete = faces(0, 0, 8, 8, 8)
    x0, y0, _, _ = tete["front"]
    for x in range(8):                                                     # visière sombre et yeux de braise
        pt(p, x0+x, y0+3, FER[0]); pt(p, x0+x, y0+4, FER[1])
    for (x, c) in ((1, (255, 150, 50)), (2, (220, 90, 30)), (5, (220, 90, 30)), (6, (255, 150, 50))): pt(p, x0+x, y0+3, c)
    for x in (2, 3, 4, 5): pt(p, x0+x, y0+6, FER[0] if x % 2 else FER[2])   # grille de bouche
    for (x, y) in ((0, 0), (7, 0), (0, 7), (7, 7)): rivet(p, x0+x, y0+y)
    xt, yt, _, _ = tete["top"]
    for i in range(8): pt(p, xt+i, yt+3, ROUILLE[1]); pt(p, xt+3, yt+i, ROUILLE[1])   # soudures du crâne
    corps = faces(16, 16, 8, 12, 4)
    xf, yf, _, _ = corps["front"]
    for y in range(12):                                                    # bretelles de cuir et boucle de laiton
        pt(p, xf+1, yf+y, (60, 36, 20)); pt(p, xf+6, yf+y, (60, 36, 20))
    pt(p, xf+1, yf+5, LAITON[4]); pt(p, xf+6, yf+5, LAITON[4])
    for x in range(2, 6): pt(p, xf+x, yf+7, TOILE[1])                      # poche du tablier
    bras = faces(40, 16, 4, 12, 4)
    bande(p, cotes(bras), 1); bande(p, cotes(bras), 9)                      # bagues d'épaule et de poignet
    for (x0, y0, w, h) in cotes(bras):
        for x in range(w):
            for y in (10, 11): pt(p, x0+x, y0+y, FER[2] if (x+y) % 2 else FER[3])   # mains de fer
    jambe = faces(0, 16, 4, 12, 4)
    for (x0, y0, w, h) in cotes(jambe):
        for x in range(w):
            for y in (10, 11): pt(p, x0+x, y0+y, FER[1] if y == 11 else FER[3])     # bottes ferrées
    return t

# ======================= SQUELETTE : automate de laiton
def squelette_v2(base):
    t = squelette(base); p = t.load()
    tete = faces(0, 0, 8, 8, 8)
    x0, y0, _, _ = tete["front"]
    for x in range(8): pt(p, x0+x, y0+1, LAITON[1])                         # joint du front
    for (x, y) in ((0, 0), (7, 0)): rivet(p, x0+x, y0+y)
    xt, yt, _, _ = tete["top"]
    for (x, y) in ((1, 1), (6, 1), (1, 6), (6, 6)): rivet(p, xt+x, yt+y)
    corps = faces(16, 16, 8, 12, 4)
    xf, yf, _, _ = corps["front"]
    for (x, y, c) in ((3, 3, (255, 180, 60)), (4, 3, (255, 140, 40)), (3, 4, (230, 110, 30)), (4, 4, (255, 180, 60))):
        if p[xf+x, yf+y][3]: pt(p, xf+x, yf+y, c)                          # cœur de braise dans la poitrine
    for (u, v) in ((40, 16), (0, 16)):                                      # bras et jambes fins (2 x 12 x 2)
        f = faces(u, v, 2, 12, 2)
        for (x0, y0, w, h) in cotes(f):
            for x in range(w):
                if p[x0+x, y0+5][3]: pt(p, x0+x, y0+5, FER[1])             # articulation (coude, genou)
                if p[x0+x, y0+6][3]: pt(p, x0+x, y0+6, LAITON[5] if x == 0 else FER[3])
    return t

# ======================= CREEPER : chaudière instable
def creeper_v2(base):
    van = base.convert("RGBA"); pv = van.load()
    t = creeper(base); p = t.load()
    rnd = random.Random(9)
    def plaques(f, cercles=()):
        for (x0, y0, w, h) in [f[k] for k in f]:
            coulures = {x: rnd.randint(0, h // 2) if rnd.random() < 0.35 else -1 for x in range(w)}
            for y in range(h):
                for x in range(w):
                    c = p[x0+x, y0+y]
                    r, g, b, a = pv[x0+x, y0+y]
                    if c[3] == 0 or (8 <= x0+x <= 15 and 8 <= y0+y <= 15 and r+g+b < 150): continue   # visage conservé
                    lum = 0.45 + 0.35*((r+g+b)/765) - 0.12*(y/h)
                    col = sur_rampe(CUIVRE, lum)
                    if coulures[x] >= 0 and y <= coulures[x]: col = sur_rampe(VERT_DE_GRIS, 0.35 + 0.4*(1 - y/max(1, coulures[x]+1)))
                    if x % 4 == 3: col = CUIVRE[1]
                    if x % 4 == 3 and y % 3 == 1: col = LAITON[5]
                    if y in cercles: col = LAITON[4] if x % 2 else LAITON[3]
                    pt(p, x0+x, y0+y, col)
    plaques(faces(16, 16, 8, 12, 4), cercles=(1, 10))
    plaques(faces(0, 16, 4, 6, 4), cercles=(5,))
    plaques(faces(0, 0, 8, 8, 8))
    return t

# ======================= ARAIGNÉE : araignée mécanique
def araignee_v2(base, metal=FER, accent=LAITON):
    t = araignee(base, metal, accent); p = t.load()
    ab = faces(0, 12, 10, 8, 12)
    xt, yt, w, d = ab["top"]
    for y in range(d):
        pt(p, xt+4, yt+y, accent[3]); pt(p, xt+5, yt+y, accent[2])           # échine de laiton
    for y in (2, 6, 10):
        for x in (1, 8): rivet(p, xt+x, yt+y)
    for (x0, y0, w, h) in cotes(ab):
        for x in range(w): pt(p, x0+x, y0+h-1, metal[0])                       # ventre sombre
    patte = faces(18, 0, 16, 2, 2)
    for k in ("front", "back", "top", "bottom"):
        x0, y0, w, h = patte[k]
        for x in range(w):
            if x % 5 == 2:
                for y in range(h): pt(p, x0+x, y0+y, accent[4] if y == 0 else accent[2])   # articulations
    return t

# ======================= améliorations (v3) : plus de mécanique, lecture plus nette
def cadran(p, x0, y0):
    """Petit manomètre 3 x 3."""
    for (x, y, c) in ((0, 0, LAITON[2]), (1, 0, LAITON[4]), (2, 0, LAITON[2]), (0, 1, LAITON[4]), (1, 1, (236, 228, 204)),
                      (2, 1, (200, 30, 20)), (0, 2, LAITON[2]), (1, 2, LAITON[1]), (2, 2, LAITON[2])):
        pt(p, x0+x, y0+y, c)

def zombie_v3(base):
    t = zombie_v2(base); p = t.load()
    tete = faces(0, 0, 8, 8, 8)
    x0, y0, _, _ = tete["front"]
    for x in range(8):                                                         # masque riveté : plaque claire au front, joue sombre
        pt(p, x0+x, y0+1, ROUILLE[4] if x % 2 else ROUILLE[3])
        pt(p, x0+x, y0+7, FER[2])
    for (x, y) in ((0, 1), (7, 1), (0, 5), (7, 5)): rivet(p, x0+x, y0+y)
    for k in ("right", "left"):                                                # oreillettes : boulons de fixation
        xs, ys, _, _ = tete[k]
        for (x, y) in ((3, 3), (4, 3), (3, 4), (4, 4)): pt(p, xs+x, ys+y, LAITON[3] if (x+y) % 2 else LAITON[1])
    corps = faces(16, 16, 8, 12, 4)
    xb, yb, _, _ = corps["back"]
    for y in range(1, 10):                                                     # petite chaudière dorsale et son tuyau
        for x in range(2, 6): pt(p, xb+x, yb+y, CUIVRE[3] if x == 2 else CUIVRE[2] if x < 5 else CUIVRE[0])
    for x in range(2, 6): pt(p, xb+x, yb+1, LAITON[4]); pt(p, xb+x, yb+9, LAITON[2])
    cadran(p, xb+3, yb+4)
    xf, yf, _, _ = corps["front"]
    cadran(p, xf+3, yf+1)                                                       # jauge de poitrine
    return t

def squelette_v3(base):
    t = squelette_v2(base); p = t.load()
    corps = faces(16, 16, 8, 12, 4)
    xb, yb, _, _ = corps["back"]
    for y in range(12):                                                         # colonne : tuyau de cuivre
        for x in (3, 4):
            if p[xb+x, yb+y][3]: pt(p, xb+x, yb+y, CUIVRE[3] if x == 3 else CUIVRE[1])
    for (u, v) in ((40, 16), (0, 16)):                                          # gaines sombres entre les plaques
        f = faces(u, v, 2, 12, 2)
        for (x0, y0, w, h) in cotes(f):
            for y in (0, 11):
                for x in range(w):
                    if p[x0+x, y0+y][3]: pt(p, x0+x, y0+y, FER[2])
    tete = faces(0, 0, 8, 8, 8)
    xt, yt, _, _ = tete["top"]
    for (x, y) in ((3, 3), (4, 3), (3, 4), (4, 4)): pt(p, xt+x, yt+y, CUIVRE[2])  # bouchon de remplissage sur le crâne
    return t

def creeper_v3(base):
    t = creeper_v2(base); p = t.load()
    tete = faces(0, 0, 8, 8, 8)
    xt, yt, _, _ = tete["top"]
    for y in range(8):                                                           # soupape au sommet : laiton et volant rouge
        for x in range(8):
            if 2 <= x <= 5 and 2 <= y <= 5:
                pt(p, xt+x, yt+y, (200, 40, 28) if x in (2, 5) or y in (2, 5) else LAITON[4])
    pt(p, xt+3, yt+3, (90, 70, 60))
    corps = faces(16, 16, 8, 12, 4)
    xb, yb, _, _ = corps["back"]
    cadran(p, xb+2, yb+4); cadran(p, xb+5, yb+4)
    for x in range(8): pt(p, xb+x, yb+8, FER[2])                                 # trappe de foyer
    for x in range(2, 6): pt(p, xb+x, yb+9, (230, 90, 24) if x % 2 else (170, 40, 14))
    return t

def araignee_v3(base, metal=FER, accent=LAITON):
    t = araignee_v2(base, metal, accent); p = t.load()
    ab = faces(0, 12, 10, 8, 12)
    xb, yb, w, h = ab["back"]
    for y in range(2, 6):                                                        # grille de chaudière à l'arrière
        for x in range(2, 8): pt(p, xb+x, yb+y, (220, 80, 20) if (x+y) % 2 == 0 and y in (3, 4) else metal[0])
    for x in range(2, 8): pt(p, xb+x, yb+1, accent[4])
    tete = faces(32, 4, 8, 8, 8)
    xt, yt, _, _ = tete["top"]
    for (x, y) in ((1, 1), (6, 1), (1, 6), (6, 6)): rivet(p, xt+x, yt+y)
    return t
