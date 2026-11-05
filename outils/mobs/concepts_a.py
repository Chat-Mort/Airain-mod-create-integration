"""Lot A, les monstres de base : un métier, une matière, un signe distinctif chacun."""
import random
from atelier import *

TETE, CORPS = (0, 0, 8, 8, 8), (16, 16, 8, 12, 4)
BRAS, JAMBE = (40, 16, 4, 12, 4), (0, 16, 4, 12, 4)
BRAS_G, JAMBE_G = (32, 48, 4, 12, 4), (16, 48, 4, 12, 4)
SBRAS, SJAMBE = (40, 16, 2, 12, 2), (0, 16, 2, 12, 2)

def F(b): return faces(*b)

# =========================================================== ZOMBIE : le Chauffeur (fonte noircie, foyer au ventre)
def chauffeur():
    t = Toile((64, 64))
    for b in (TETE, CORPS, BRAS, JAMBE): t.boite(*b, metal(SUIE, 0.42, 0.1, graine=2), force=True)
    x, y, _, _ = F(TETE)["front"]
    t.ligne_h(x, y+2, 8, SUIE[0], True)
    for (i, c) in ((1, BRAISE[2]), (2, BRAISE[1]), (5, BRAISE[1]), (6, BRAISE[2])): t.pt(x+i, y+3, c, True)
    for i in range(2, 6):
        t.pt(x+i, y+5, SUIE[0] if i % 2 else FER[3], True); t.pt(x+i, y+6, FER[3] if i % 2 else SUIE[0], True)
    for (i, j) in ((0, 0), (7, 0), (0, 7), (7, 7)): t.rivet(x+i, y+j, force=True)
    x, y, _, _ = F(CORPS)["front"]
    t.rect(x+1, y+2, 6, 7, FER[3], True); t.cadre(x+1, y+2, 6, 7, FER[4], SUIE[0], True)          # porte du foyer
    for j in range(3, 8):
        for i in range(2, 6):
            centre = 1 - (abs(i - 3.5) + abs(j - 5)) / 4
            t.pt(x+i, y+j, BRAISE[max(0, min(4, int(4 - centre*4)))] if j % 2 else SUIE[0], True)
    t.rect(x, y+9, 8, 3, lambda i, j: ramp(CUIR, 0.45 - 0.1*j), True)                            # tablier
    xb, yb, _, _ = F(CORPS)["back"]
    for j in range(12): t.pt(xb+3, yb+j, FER[3], True); t.pt(xb+4, yb+j, FER[1], True)             # tuyau de fumée
    t.pt(xb+3, yb, BRAISE[1], True); t.pt(xb+4, yb, BRAISE[2], True)
    for k in COTES:
        x, y, w, h = F(BRAS)[k]
        t.rect(x, y+7, w, 5, lambda i, j: ramp(CUIR, 0.5 - 0.06*j), True); t.ligne_h(x, y+7, w, LAITON[3], True)   # gantelets
        x, y, w, h = F(JAMBE)[k]
        t.rect(x, y, w, 10, lambda i, j: ramp(SUIE, 0.6 + 0.05*((i+j) % 2)), True)                 # pantalon
        t.rect(x, y+10, w, 2, lambda i, j: FER[2] if j == 0 else FER[0], True)                     # bottes
        if k == "front": t.rect(x, y, w, 6, lambda i, j: ramp(CUIR, 0.42 - 0.04*j), True)           # le tablier descend
    return t.im

# =========================================================== HUSK : le Prospecteur (fer-blanc, lunettes de désert)
def prospecteur():
    t = Toile((64, 64)); rnd = random.Random(5)
    bosse = lambda pal, b: (lambda i, j, w, h, f: ramp(pal, b + (-0.12 if rnd.random() < 0.08 else rnd.uniform(-0.04, 0.04)) + (0.12 if j == 0 else 0) - (0.12 if j == h-1 else 0)))
    for b in (TETE, BRAS): t.boite(*b, bosse(FERBLANC, 0.5), force=True)
    for b in (CORPS, JAMBE): t.boite(*b, lambda i, j, w, h, f: ramp(KAKI, 0.5 + (0.05 if (i+j) % 2 else -0.03) - 0.1*(j == h-1)), force=True)
    tete = F(TETE)
    for k in COTES:
        x, y, w, h = tete[k]
        t.ligne_h(x, y+3, w, CUIR[2], True)                                                        # sangle des lunettes
        t.rect(x, y+6, w, 2, lambda i, j: ramp(KAKI, 0.55 - 0.1*j), True)                           # foulard
    x, y, _, _ = tete["front"]
    for cx in (1, 5):                                                                              # lunettes rondes
        t.cadre(x+cx-1, y+2, 4, 3, LAITON[4], LAITON[1], True)
        t.pt(x+cx, y+3, (250, 200, 90), True); t.pt(x+cx+1, y+3, (210, 140, 50), True)
    x, y, w, h = F(CORPS)["front"]
    t.rect(x, y, w, 2, lambda i, j: ramp(KAKI, 0.62), True)
    for cx in (1, 5):
        t.rect(x+cx, y+5, 2, 2, KAKI[1], True); t.pt(x+cx, y+5, LAITON[4], True)                   # poches
    t.ligne_h(x, y+8, w, CUIR[1], True); t.pt(x+3, y+8, LAITON[4], True); t.pt(x+4, y+8, LAITON[2], True)   # ceinture
    xb, yb, _, _ = F(CORPS)["back"]
    t.rect(xb+1, yb+1, 6, 8, lambda i, j: ramp(KAKI, 0.35 + 0.05*(j == 0)), True)                  # sac de toile
    t.cadre(xb+1, yb+1, 6, 8, KAKI[3], KAKI[0], True); t.ligne_h(xb+1, yb+3, 6, CUIR[2], True)
    t.pt(xb+5, yb+6, FERBLANC[4], True); t.pt(xb+6, yb+6, FERBLANC[2], True)                     # quart en fer-blanc
    for k in COTES:
        x, y, w, h = F(BRAS)[k]; t.rect(x, y, w, 4, lambda i, j: ramp(KAKI, 0.55 - 0.04*j), True)  # manches retroussées
        x, y, w, h = F(JAMBE)[k]; t.rect(x, y+9, w, 3, lambda i, j: ramp(CUIR, 0.5 - 0.15*j), True)
    return t.im

# =========================================================== NOYÉ : le Scaphandrier (casque de plongée à trois hublots)
def scaphandrier():
    t = Toile((64, 64))
    t.boite(*TETE, metal(LAITON, 0.55, 0.05, graine=3), force=True)
    for b in (CORPS, BRAS, JAMBE, BRAS_G, JAMBE_G): t.boite(*b, lambda i, j, w, h, f: ramp(ARDOISE, 0.5 + (0.04 if (i+j) % 2 else 0) - 0.1*(j == h-1)), force=True)
    tete = F(TETE)
    x, y, _, _ = tete["front"]
    t.disque(x+4, y+4, 3.4, lambda r, a: LAITON[5] if r > 2.6 and 150 < a < 300 else LAITON[1] if r > 2.6 else (230, 250, 250) if r < 1.2 and 180 < a < 270 else (24, 62, 72), True)
    for (i, j) in ((0, 0), (7, 0), (0, 7), (7, 7), (3, 0), (4, 7)): t.rivet(x+i, y+j, force=True)
    for k in ("right", "left"):
        x, y, _, _ = tete[k]
        t.disque(x+4, y+4, 2.2, lambda r, a: LAITON[1] if r > 1.4 else (24, 62, 72), True)
    x, y, _, _ = tete["back"]
    t.rect(x+3, y+3, 2, 3, CUIVRE[2], True); t.cadre(x+2, y+2, 4, 5, LAITON[4], LAITON[0], True)      # raccord du tuyau d'air
    x, y, _, _ = tete["up"]
    t.disque(x+4, y+4, 2, lambda r, a: LAITON[5] if r < 1 else LAITON[2], True)
    for k in COTES:
        x, y, w, h = F(CORPS)[k]; t.rect(x, y, w, 2, lambda i, j: LAITON[4] if j == 0 else LAITON[2], True)   # collerette
        for (bras, jambe) in ((BRAS, JAMBE), (BRAS_G, JAMBE_G)):
            x, y, w, h = F(bras)[k]; t.ligne_h(x, y+8, w, LAITON[3], True); t.rect(x, y+9, w, 3, (22, 22, 26), True)   # gants
            x, y, w, h = F(jambe)[k]; t.rect(x, y+8, w, 4, lambda i, j: ramp(FER, 0.45 - 0.08*j), True); t.ligne_h(x, y+8, w, LAITON[2], True)
    xb, yb, _, _ = F(CORPS)["back"]
    for cx in (1, 5):                                                                              # bouteilles de cuivre
        for j in range(1, 11):
            t.pt(xb+cx, yb+j, CUIVRE[4] if j > 1 else LAITON[4], True); t.pt(xb+cx+1, yb+j, CUIVRE[2] if j > 1 else LAITON[2], True)
    return t.im

# =========================================================== SQUELETTES (masque vanilla : on garde les vides des côtes)
def ossature(masque, pal, base=0.55, articulation=NICKEL):
    t = Toile((64, 32), masque); mv = masque.load()
    for b in (TETE, CORPS, SBRAS, SJAMBE): t.boite(*b, metal(pal, base, 0.05, graine=4))
    for y in range(32):                                                                            # creux d'origine -> ombre
        for x in range(64):
            c = mv[x, y]
            if c[3] and (c[0]+c[1]+c[2]) < 230: t.pt(x, y, mix(ramp(pal, 0.12), (0, 0, 0), 0.2))
    for b in (SBRAS, SJAMBE):
        for k in COTES:
            x, y, w, h = F(b)[k]
            for j in (0, 5, 6, 11): t.ligne_h(x, y+j, w, articulation[4] if j != 6 else articulation[1])
    return t

def yeux(t, c1, c2):
    x, y, _, _ = F(TETE)["front"]
    for (i, c) in ((1, c1), (2, c2), (5, c2), (6, c1)): t.pt(x+i, y+4, c, True)

def arbaletrier(v):
    t = ossature(v, PORCELAINE, 0.6)
    yeux(t, (170, 240, 255), (60, 170, 240))
    x, y, _, _ = F(TETE)["front"]; t.ligne_h(x, y+1, 8, OR[3])                                     # filet d'or
    x, y, _, _ = F(TETE)["up"]; t.ligne_h(x, y+4, 8, OR[3]); t.ligne_v(x+4, y, 8, OR[3])
    x, y, _, _ = F(CORPS)["front"]
    for j in range(12): t.pt(x+3, y+j, NICKEL[4]); t.pt(x+4, y+j, NICKEL[2])                         # sternum de nickel
    t.pt(x+3, y+2, OR[4]); t.pt(x+4, y+2, OR[2])
    return t.im

def veilleur(v):
    t = ossature(v, ACIER_BLEU, 0.5); rnd = random.Random(8)
    for y in range(32):
        for x in range(64):
            if t.get(x, y)[3] and rnd.random() < 0.09: t.pt(x, y, PORCELAINE[4])                    # givre
    for b in (TETE, CORPS):
        for k in COTES:
            x, y, w, h = F(b)[k]; t.ligne_h(x, y, w, PORCELAINE[5])
    yeux(t, (210, 245, 255), (120, 210, 255))
    x, y, _, _ = F(CORPS)["front"]                                                                 # lanterne de poitrine
    t.cadre(x+2, y+2, 4, 5, NICKEL[4], NICKEL[0], True); t.rect(x+3, y+3, 2, 3, (190, 236, 255), True)
    return t.im

def manteau_fourrure(v):
    """Manteau doublé de fourrure grise, seulement sur le torse (la tête et les membres restent en acier bleui)."""
    t = Toile((64, 32), v); rnd = random.Random(9)
    FOURRURE = R((60, 54, 50), (84, 76, 70), (110, 100, 92), (136, 126, 116), (160, 150, 140), (186, 178, 168))
    for y in range(16, 32):
        for x in range(16, 40): t.pt(x, y, ramp(FOURRURE, 0.45 + rnd.uniform(-0.18, 0.18) + (0.2 if y in (20, 21) else 0)))
    return t.im

def drainier(v):
    t = ossature(v, VERT_USINE, 0.5, articulation=LAITON); rnd = random.Random(10)
    for y in range(32):
        for x in range(64):
            if t.get(x, y)[3] and rnd.random() < 0.12: t.pt(x, y, ramp(ROUILLE, rnd.uniform(0.3, 0.7)))   # laque écaillée
    yeux(t, (210, 255, 120), (150, 230, 60))
    x, y, _, _ = F(CORPS)["front"]
    t.disque(x+4, y+4, 2.4, lambda r, a: (200, 34, 24) if r > 1.4 else LAITON[4], True)               # vanne rouge
    for k in COTES:                                                                                 # durites noires en spirale
        for b in (SBRAS, SJAMBE):
            x, y, w, h = F(b)[k]
            for j in range(1, 11, 3): t.ligne_h(x, y+j, w, (18, 18, 20))
    return t.im

def durites(v):
    """Le calque de champignons du bogged est retiré : le Drainier n'a que ses vannes et ses durites."""
    return Image.new("RGBA", v.size, (0, 0, 0, 0))

def algues(v):
    """Quelques lanières d'algues sur le scaphandre, jamais sur le casque."""
    t = Toile((64, 64), v); src = v.load(); rnd = random.Random(14)
    for y in range(16, 64):
        for x in range(64):
            if src[x, y][3] and (x % 5 in (1, 2)) and rnd.random() < 0.8: t.pt(x, y, src[x, y])
    return t.im

def fondeur(v):
    t = ossature(v, FER, 0.32, articulation=FER); rnd = random.Random(11)
    for b in (SBRAS, SJAMBE):
        for k in COTES:
            x, y, w, h = F(b)[k]
            for j in (5, 6): t.ligne_h(x, y+j, w, BRAISE[2] if j == 5 else BRAISE[3])                # joints chauffés au rouge
    for b in (TETE, CORPS):                                                                         # coulures de laitier
        for k in COTES:
            x, y, w, h = F(b)[k]
            for i in range(w):
                if rnd.random() < 0.3:
                    for j in range(rnd.randint(1, 4)): t.pt(x+i, y+j, BRAISE[min(4, 1+j)])
    yeux(t, BRAISE[0], BRAISE[1])
    return t.im

# =========================================================== CREEPER : la Chaudière (cuivre, bandes de danger, manomètres)
def chaudiere(v):
    t = Toile((64, 32)); mv = v.load()
    TETE_C, CORPS_C, PATTE = (0, 0, 8, 8, 8), (16, 16, 8, 12, 4), (0, 16, 4, 6, 4)
    def plaques(i, j, w, h, f):
        c = ramp(CUIVRE, 0.55 + 0.05*((i//4) % 2) - 0.1*(j == h-1) + 0.1*(j == 0))
        if i % 4 == 3: c = CUIVRE[1]
        if i % 4 == 3 and j % 3 == 1: c = LAITON[5]
        return c
    for b in (TETE_C, CORPS_C, PATTE): t.boite(*b, plaques, force=True)
    danger = lambda i, j: LAQUE_ROUGE[3] if ((i + j) // 2) % 2 else (238, 232, 222)
    for k in COTES:
        x, y, w, h = F(CORPS_C)[k]; t.rect(x, y+5, w, 2, danger, True)
        x, y, w, h = F(PATTE)[k]; t.rect(x, y, w, 2, danger, True)
    x, y, _, _ = F(TETE_C)["front"]
    for j in range(8):                                                                              # visage : bouche de grille
        for i in range(8):
            c = mv[x+i, y+j]
            if (c[0]+c[1]+c[2]) < 150 and j >= 4: t.pt(x+i, y+j, SUIE[0] if (i+j) % 2 else FER[3], True)
    for cx in (1, 5):                                                                               # yeux : deux manomètres
        t.pt(x+cx, y+2, (238, 230, 206), True); t.pt(x+cx+1, y+2, (200, 30, 20), True)
        t.pt(x+cx, y+3, (238, 230, 206), True); t.pt(x+cx+1, y+3, (238, 230, 206), True)
        t.pt(x+cx-1, y+2, LAITON[2], True); t.pt(x+cx+2, y+3, LAITON[1], True)
    x, y, _, _ = F(TETE_C)["up"]
    t.disque(x+4, y+4, 2.5, lambda r, a: (200, 34, 24) if r > 1.5 else LAITON[4], True)               # soupape
    x, y, _, _ = F(CORPS_C)["back"]
    t.disque(x+4, y+2.5, 1.8, lambda r, a: LAITON[2] if r > 1.2 else (238, 230, 206), True); t.pt(x+4, y+2, (200, 30, 20), True)
    return t.im

# =========================================================== ARAIGNÉES
TETE_A, COU, ABDO, PATTE_A = (32, 4, 8, 8, 8), (0, 0, 6, 6, 6), (0, 12, 10, 8, 12), (18, 0, 16, 2, 2)
def emaille(i, j, w, h, f):
    t = 0.32 + (0.45 if j == 1 and i % 3 else 0) + (0.12 if f == "up" else 0)
    return ramp(EMAIL_NOIR, t)

def araignee_forage(v):
    t = Toile((64, 32)); mv = v.load()
    for b in (TETE_A, COU, ABDO): t.boite(*b, emaille, force=True)
    t.boite(*PATTE_A, lambda i, j, w, h, f: EMAIL_NOIR[1] if i % 5 == 0 else ramp(CHROME, 0.55 + 0.3*(j == 0)), force=True)
    for k in ("right", "left", "back"):
        x, y, w, h = F(ABDO)[k]
        t.rect(x, y+3, w, 2, lambda i, j: (240, 196, 30) if ((i + j) // 2) % 2 else EMAIL_NOIR[0], True)   # bandes de danger
    x, y, _, _ = F(TETE_A)["front"]
    t.disque(x+4, y+5, 2.3, lambda r, a: CHROME[5] if int(a/45 + r*2) % 2 else CHROME[2], True)        # tête-foret
    for yy in range(8):                                                                              # yeux rouges d'origine
        for xx in range(8):
            c = mv[x+xx, y+yy]
            if c[0] > 120 and c[1] < 60: t.pt(x+xx, y+yy, (220, 30, 24), True)
    x, y, w, d = F(ABDO)["up"]
    for j in range(d): t.pt(x+4, y+j, CHROME[3], True); t.pt(x+5, y+j, CHROME[1], True)
    return t.im

def araignee_reparation(v):
    t = Toile((64, 32)); mv = v.load()
    for b in (TETE_A, COU, ABDO): t.boite(*b, metal(VDG, 0.5, 0.06, graine=13), force=True)
    t.boite(*PATTE_A, lambda i, j, w, h, f: LAITON[2] if i % 5 == 0 else ramp(CUIVRE, 0.5 + 0.2*(j == 0)), force=True)
    x, y, w, d = F(ABDO)["up"]                                                                      # dôme de verre et rouages
    for j in range(d):
        for i in range(w):
            dx, dy = (i - 4.5)/4.5, (j - 5.5)/5.5
            if dx*dx + dy*dy < 1:
                c = (176, 226, 228) if dx*dx + dy*dy > 0.7 else (120, 190, 196)
                if (i + j) % 4 == 0 and dx*dx + dy*dy < 0.6: c = LAITON[4]
                if i == 2 and j == 3: c = (240, 255, 255)
                t.pt(x+i, y+j, c, True)
    x, y, _, _ = F(TETE_A)["front"]
    for yy in range(8):
        for xx in range(8):
            c = mv[x+xx, y+yy]
            if c[0] > 120 and c[1] < 60: t.pt(x+xx, y+yy, (220, 30, 24), True)
    return t.im

LOT_A = {
    "zombie/zombie.png": lambda: chauffeur(),
    "zombie/husk.png": lambda: prospecteur(),
    "zombie/drowned.png": lambda: scaphandrier(),
    "skeleton/skeleton.png": lambda: arbaletrier(vanilla("skeleton/skeleton.png")),
    "skeleton/stray.png": lambda: veilleur(vanilla("skeleton/stray.png")),
    "skeleton/stray_overlay.png": lambda: manteau_fourrure(vanilla("skeleton/stray_overlay.png")),
    "zombie/drowned_outer_layer.png": lambda: algues(vanilla("zombie/drowned_outer_layer.png")),
    "skeleton/bogged.png": lambda: drainier(vanilla("skeleton/bogged.png")),
    "skeleton/bogged_overlay.png": lambda: durites(vanilla("skeleton/bogged_overlay.png")),
    "skeleton/wither_skeleton.png": lambda: fondeur(vanilla("skeleton/wither_skeleton.png")),
    "creeper/creeper.png": lambda: chaudiere(vanilla("creeper/creeper.png")),
    "spider/spider.png": lambda: araignee_forage(vanilla("spider/spider.png")),
    "spider/cave_spider.png": lambda: araignee_reparation(vanilla("spider/cave_spider.png")),
}
