"""Lot 1 : Chauffeur (zombie), Prospecteur (husk), Scaphandrier perdu (drowned + couche extérieure),
couches du Veilleur des glaces (stray_overlay) et du Drainier (bogged_overlay)."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import *

TETE, CHAP = faces(0, 0, 8, 8, 8), faces(32, 0, 8, 8, 8)
CORPS = faces(16, 16, 8, 12, 4)
BRAS_D, JAMBE_D = faces(40, 16, 4, 12, 4), faces(0, 16, 4, 12, 4)
BRAS_G, JAMBE_G = faces(32, 48, 4, 12, 4), faces(16, 48, 4, 12, 4)
TOUT = list(TETE)

def gauche(t):
    """Membres gauches (utilisés par le Scaphandrier) = miroir des droits ; droite/gauche échangées."""
    for src, dst in ((BRAS_D, BRAS_G), (JAMBE_D, JAMBE_G)):
        for n in ("front", "back", "up", "down"): t.miroir(src[n], dst[n])
        t.miroir(src["right"], dst["left"]); t.miroir(src["left"], dst["right"])

# =========================================================================== CHAUFFEUR
def chauffeur():
    t = Toile(graine=11)
    # --- tête : casque de fonte, lunettes de soudeur, grille de bouche
    for n, f in TETE.items(): t.matiere(f, FER, 0.42, nom=n, taches=(SUIE, 6, 0.3))
    f = TETE["front"]
    t.rect(f, 0, 0, 8, 2, FER, 0.62); t.rivets(f, [(1, 1), (6, 1)], LAITON)
    for x0 in (0, 4):                                   # montures de laiton
        t.rect(f, x0, 2, 4, 4, LAITON, 0.45, relief=0.18)
    for x0 in (1, 5):                                   # verres ambrés
        t.pt(f, x0, 3, AMBRE[0]); t.pt(f, x0+1, 3, AMBRE[1]); t.pt(f, x0, 4, AMBRE[1]); t.pt(f, x0+1, 4, AMBRE[2])
    t.grille(f, 1, 6, 6, 1, FER); t.hligne(f, 7, ramp(FER, 0.2))
    for n in ("right", "left"):                         # sangle des lunettes
        f = TETE[n]; t.rect(f, 0, 3, 8, 2, CUIR, 0.4, relief=0.1); t.pt(f, 3 if n == "right" else 4, 3, ramp(LAITON, 0.8))
        t.rect(f, 2, 0, 4, 2, FER, 0.6); t.rivet(f, 1, 6, FER)
    f = TETE["back"]; t.rect(f, 0, 3, 8, 2, CUIR, 0.35, relief=0.1); t.grille(f, 1, 5, 6, 2, FER)
    f = TETE["up"]; t.couture(f, 3, FER); t.vcouture(f, 3, FER); t.rivets(f, [(1, 1), (6, 1), (1, 6), (6, 6)], LAITON)
    # --- corps : bretelles de cuir, porte de foyer incandescente, manomètre, tablier
    for n, f in CORPS.items(): t.matiere(f, FER, 0.4, nom=n, taches=(SUIE, 8, 0.25))
    f = CORPS["front"]
    t.rect(f, 0, 7, 8, 5, CUIR, 0.45); t.hligne(f, 7, ramp(LAITON, 0.6))               # tablier
    for x in (0, 7): t.rect(f, x, 0, 1, 7, CUIR, 0.5, relief=0.06)                   # bretelles
    t.rect(f, 1, 2, 5, 5, LAITON, 0.5, relief=0.2)                                    # cadre du foyer
    t.lueur(f, 2, 3, 3, 3, BRAISE); t.hligne(f, 4, ramp(LAITON, 0.3), 2, 3)          # grille de la porte
    t.jauge(f, 5, 0, LAITON)
    t.rivets(f, [(6, 4), (6, 6)], FER)
    f = CORPS["back"]
    for x in (2, 5):                                                                   # cheminées d'échappement
        t.rect(f, x, 0, 1, 10, LAITON, 0.4, relief=0.1); t.pt(f, x, 0, (30, 26, 24))
    t.rect(f, 0, 7, 8, 1, CUIR, 0.4, relief=0); t.grille(f, 3, 3, 2, 3, FER, pas=1)
    t.rivets(f, [(0, 1), (7, 1), (0, 10), (7, 10)], FER)
    for n in ("right", "left"):
        f = CORPS[n]; t.rect(f, 0, 7, 4, 5, CUIR, 0.4); t.rivets(f, [(1, 2), (2, 4)], FER)
    f = CORPS["up"]; t.rect(f, 0, 0, 8, 4, FER, 0.55); t.plein(f, 3, 1, 2, 2, ramp(LAITON, 0.5))
    # --- bras : épaulière rivetée, coude de laiton, gant de cuir
    for n, f in BRAS_D.items():
        t.matiere(f, FER, 0.42, nom=n, taches=(SUIE, 3, 0.25))
        if n in COTES:
            t.rect(f, 0, 0, 4, 3, FER, 0.62); t.rivet(f, 1, 1, LAITON)
            t.rect(f, 0, 5, 4, 2, LAITON, 0.45, relief=0.12)
            t.rect(f, 0, 9, 4, 3, CUIR, 0.35, relief=0.08)
    t.plein(BRAS_D["down"], 0, 0, 4, 4, ramp(CUIR, 0.25))
    # --- jambes : pantalon de suie, genouillère, bottes à coque de laiton
    for n, f in JAMBE_D.items():
        t.matiere(f, SUIE, 0.55, nom=n)
        if n in COTES:
            t.rect(f, 0, 5, 4, 2, FER, 0.55); t.rect(f, 0, 9, 4, 3, CUIR, 0.3, relief=0.1)
            if n == "front": t.rect(f, 0, 10, 4, 2, LAITON, 0.5, relief=0.12)
    t.plein(JAMBE_D["down"], 0, 0, 4, 4, ramp(CUIR, 0.15))
    gauche(t)
    return t.im

# =========================================================================== PROSPECTEUR
CAPUCHE = R((44, 30, 18), (66, 46, 28), (90, 64, 40), (114, 84, 54), (138, 106, 70), (164, 132, 92))
def prospecteur():
    t = Toile(graine=23)
    # --- tête : fer-blanc décapé par le sable, foulard sur la bouche, monocle-lunette
    for n, f in TETE.items(): t.matiere(f, NICKEL, 0.5, nom=n, taches=(ROUILLE, 4, 0.5))
    f = TETE["front"]
    t.rect(f, 1, 2, 3, 3, LAITON, 0.5, relief=0.2); t.pt(f, 2, 3, AMBRE[0])            # monocle
    t.pt(f, 5, 3, AMBRE[1]); t.pt(f, 6, 3, AMBRE[2]); t.hligne(f, 2, ramp(FERBLANC, 0.2), 4, 4)
    t.rect(f, 0, 5, 8, 3, TOILE, 0.45, relief=0.08); t.hligne(f, 6, ramp(TOILE, 0.25), 1, 6)   # foulard
    for n in ("right", "left", "back"):
        f = TETE[n]; t.rect(f, 0, 5, 8, 3, TOILE, 0.42, relief=0.06)
    t.pt(TETE["left"], 1, 6, ramp(TOILE, 0.2)); t.pt(TETE["left"], 1, 7, ramp(TOILE, 0.3))     # nœud
    # capuche de toile (couche chapeau) : dessus, côtés, dos ; ouverture devant
    for n, f in CHAP.items():
        if n == "down": continue
        t.matiere(f, CAPUCHE, 0.45, nom=n, bruit=0.06, biseau=0.06)
    f = CHAP["front"]
    for j in range(1, 8):
        for i in range(1, 7): t.vide(f, i, j)
    t.hligne(f, 0, ramp(CAPUCHE, 0.7))
    for n in ("right", "left"):
        f = CHAP[n]
        for j in range(5, 8):
            for i in range(8):
                if t.rnd.random() < 0.5 + (j-5)*0.2: t.vide(f, i, j)
    f = CHAP["back"]; t.hligne(f, 3, ramp(CAPUCHE, 0.2))
    # --- corps : cache-poussière, bandoulière de fioles, ceinture
    for n, f in CORPS.items(): t.matiere(f, KAKI, 0.5, nom=n, bruit=0.06)
    f = CORPS["front"]
    t.vligne(f, 3, ramp(KAKI, 0.2), 0, 9); t.vligne(f, 4, ramp(KAKI, 0.25), 0, 9)       # pans du manteau
    for k in range(9):                                                                 # bandoulière en diagonale
        x = 7 - k if k < 8 else 0
        t.pt(f, x, k+1, ramp(CUIR, 0.45)); t.pt(f, x, k+2, ramp(CUIR, 0.25))
    for (x, y, c) in ((6, 2, TEAL[1]), (4, 4, AMBRE[1]), (2, 6, (150, 220, 120))):       # fioles d'échantillons
        t.pt(f, x, y, c); t.pt(f, x, y-1, ramp(LAITON, 0.7))
    t.rect(f, 0, 9, 8, 1, CUIR, 0.4, relief=0); t.pt(f, 3, 9, ramp(LAITON, 0.8)); t.pt(f, 4, 9, ramp(LAITON, 0.6))
    f = CORPS["back"]
    t.rect(f, 1, 1, 6, 6, TOILE, 0.4); t.couture(f, 3, TOILE, 1, 6)                    # sac à dos roulé
    t.rect(f, 2, 7, 4, 1, CUIR, 0.4, relief=0); t.rect(f, 0, 9, 8, 1, CUIR, 0.4, relief=0)
    for n in ("right", "left"): t.rect(CORPS[n], 0, 9, 4, 1, CUIR, 0.4, relief=0)
    # --- bras : manches de toile bandées, mains de fer-blanc
    for n, f in BRAS_D.items():
        t.matiere(f, KAKI, 0.5, nom=n)
        if n in COTES:
            for y in (3, 6): t.hligne(f, y, ramp(TOILE, 0.6))
            t.rect(f, 0, 9, 4, 3, FERBLANC, 0.5, relief=0.1)
    # --- jambes : pantalon kaki, molletières, bottes
    for n, f in JAMBE_D.items():
        t.matiere(f, KAKI, 0.38, nom=n)
        if n in COTES:
            for y in (6, 8): t.hligne(f, y, ramp(TOILE, 0.55))
            t.rect(f, 0, 10, 4, 2, CUIR, 0.35, relief=0.08)
    gauche(t)
    return t.im

# =========================================================================== SCAPHANDRIER
def scaphandrier():
    t = Toile(graine=37)
    # --- tête : casque de cuivre, hublot grillagé, petits hublots latéraux, valve
    for n, f in TETE.items(): t.matiere(f, CUIVRE, 0.45, nom=n, taches=(VDG, 7, 0.5))
    f = TETE["front"]
    t.rect(f, 1, 1, 6, 6, LAITON, 0.5, relief=0.2)
    for j in range(2, 6):
        for i in range(2, 6): t.pt(f, i, j, TEAL[2] if (i+j) % 3 else TEAL[1])
    t.pt(f, 3, 3, TEAL[0]); t.hligne(f, 3, ramp(LAITON, 0.35), 2, 4); t.vligne(f, 3, ramp(LAITON, 0.35), 2, 4)
    t.rivets(f, [(1, 1), (6, 1), (1, 6), (6, 6)], NICKEL)
    for n in ("right", "left"):
        f = TETE[n]; t.rect(f, 2, 2, 4, 4, LAITON, 0.5, relief=0.2); t.plein(f, 3, 3, 2, 2, TEAL[2]); t.pt(f, 3, 3, TEAL[1])
    f = TETE["back"]; t.rect(f, 3, 3, 2, 3, LAITON, 0.55); t.pt(f, 3, 3, ramp(NICKEL, 0.8))
    f = TETE["up"]; t.rect(f, 3, 3, 2, 2, LAITON, 0.7)
    for n in COTES: t.hligne(TETE[n], 7, ramp(LAITON, 0.45))                           # collerette
    # --- corps : scaphandre de toile, corselet de cuivre boulonné, ceinture de plomb
    for n, f in CORPS.items(): t.matiere(f, TOILE_MOUILLEE, 0.55, nom=n, bruit=0.07)
    for n in ("front", "back"):
        f = CORPS[n]; t.rect(f, 0, 0, 8, 4, CUIVRE, 0.5, relief=0.16); t.rivets(f, [(1, 1), (6, 1), (1, 3), (6, 3)], LAITON)
        t.rect(f, 0, 8, 8, 2, FER, 0.45); t.pt(f, 3, 8, ramp(LAITON, 0.8)); t.pt(f, 4, 8, ramp(LAITON, 0.6))
    for n in ("right", "left"):
        f = CORPS[n]; t.rect(f, 0, 0, 4, 4, CUIVRE, 0.45); t.rect(f, 0, 8, 4, 2, FER, 0.45)
    t.rect(CORPS["up"], 0, 0, 8, 4, CUIVRE, 0.6); t.plein(CORPS["up"], 3, 1, 2, 2, ramp(LAITON, 0.4))
    t.vligne(CORPS["back"], 4, ramp(FER, 0.3), 4, 4)                                  # tuyau d'air
    # --- bras : toile, manchettes de cuivre, gants de caoutchouc
    for n, f in BRAS_D.items():
        t.matiere(f, TOILE_MOUILLEE, 0.55, nom=n, bruit=0.07)
        if n in COTES:
            t.rect(f, 0, 0, 4, 2, CUIVRE, 0.5); t.rect(f, 0, 8, 4, 1, CUIVRE, 0.55, relief=0); t.rect(f, 0, 9, 4, 3, SUIE, 0.45, relief=0.08)
    # --- jambes : toile, bottes lestées de plomb à sangles de laiton
    for n, f in JAMBE_D.items():
        t.matiere(f, TOILE_MOUILLEE, 0.5, nom=n, bruit=0.07)
        if n in COTES:
            t.rect(f, 0, 8, 4, 4, FER, 0.4, relief=0.14); t.hligne(f, 9, ramp(LAITON, 0.55))
    gauche(t)
    return t.im

def scaphandrier_algues():
    """Couche extérieure : algues pendantes, bernacles, plaques de vert-de-gris ; le reste transparent."""
    t = Toile(graine=41)
    for pieces in (CORPS, BRAS_D, JAMBE_D):
        for n, f in pieces.items():
            if n in ("up", "down"): continue
            for _ in range(max(1, f[2] // 3)):                    # filaments d'algue qui pendent
                x = t.rnd.randrange(f[2]); y0 = t.rnd.randrange(max(1, f[3] // 2)); long = t.rnd.randint(2, f[3] - y0)
                for j in range(y0, min(f[3], y0 + long)):
                    t.pt(f, x, j, ramp(ALGUE, 0.35 + 0.4 * (j - y0) / long))
            for _ in range(2):                                # bernacles
                t.pt(f, t.rnd.randrange(f[2]), t.rnd.randrange(f[3]), (196, 196, 184))
    for n in ("right", "left", "back"):                       # quelques brins sur le casque, pas sur le hublot
        f = TETE[n]; x = t.rnd.randrange(8)
        for j in range(t.rnd.randint(4, 7), 8): t.pt(f, x, j, ramp(ALGUE, 0.5))
    f = TETE["up"]
    for _ in range(5): t.pt(f, t.rnd.randrange(8), t.rnd.randrange(8), ramp(ALGUE, t.rnd.uniform(0.3, 0.7)))
    gauche(t)
    return t.im

# =========================================================================== COUCHES DES SQUELETTES (64x32)
S_TETE, S_CORPS, S_BRAS, S_JAMBE = faces(0, 0, 8, 8, 8), faces(16, 16, 8, 12, 4), faces(40, 16, 2, 12, 2), faces(0, 16, 2, 12, 2)

def veilleur_cape():
    """Cape de toile givrée sur le dos et les épaules, croûte de glace sur le crâne, stalactites."""
    t = Toile(64, 32, graine=53)
    CAPE = R((40, 54, 72), (58, 76, 98), (80, 100, 124), (108, 128, 150), (140, 160, 180), (180, 196, 212))
    f = S_TETE["up"]; t.matiere(f, GIVRE, 0.45, nom="up", bruit=0.12, biseau=0)
    for n in COTES:
        f = S_TETE[n]
        for i in range(8):
            for j in range(t.rnd.randint(1, 3)): t.pt(f, i, j, ramp(GIVRE, 0.5 - j*0.12 + t.rnd.uniform(-0.08, 0.08)))
    # cape : dos complet jusqu'à une lisière déchirée, côtés partiels, devant = épaules
    for n, f in S_CORPS.items():
        if n == "down": continue
        if n == "up":
            t.matiere(f, CAPE, 0.5, nom="up", bruit=0.06); continue
        bas = {"back": 11, "right": 9, "left": 9, "front": 2}[n]
        for i in range(f[2]):
            fin = bas - (t.rnd.randint(0, 2) if n != "front" else 0)
            for j in range(fin):
                t.pt(f, i, j, ramp(CAPE, 0.5 + t.rnd.uniform(-0.06, 0.06) + (0.15 if j == 0 else 0)))
            t.pt(f, i, fin, ramp(GIVRE, 0.6))                                     # lisière gelée
            if t.rnd.random() < 0.35 and fin + 1 < f[3]: t.pt(f, i, fin + 1, ramp(GIVRE, 0.85))   # stalactite
        if n == "back":
            t.couture(f, 4, CAPE, 0, 8)
            for k in range(6): t.pt(f, t.rnd.randrange(8), t.rnd.randrange(9), ramp(GIVRE, 0.8))
    for n, f in S_BRAS.items():                                                    # épaules
        if n == "down": continue
        for i in range(f[2]):
            for j in range(3 if n != "up" else f[3]): t.pt(f, i, j, ramp(CAPE, 0.55))
            if n != "up": t.pt(f, i, 3, ramp(GIVRE, 0.7))
    for n in COTES:                                                                # givre aux pieds
        f = S_JAMBE[n]; t.pt(f, 0, 11, ramp(GIVRE, 0.7)); t.pt(f, 1, 10, ramp(GIVRE, 0.9))
    return t.im

def drainier_mousse():
    """Mousse, tuyau de drainage rouillé dans le dos, coulures d'algue, petits champignons sur le crâne."""
    t = Toile(64, 32, graine=59)
    f = S_TETE["up"]; t.matiere(f, MOUSSE, 0.5, nom="up", bruit=0.12, biseau=0)
    for (x, y, c) in ((2, 2, (170, 40, 30)), (5, 5, (196, 150, 90)), (6, 2, (170, 40, 30))):
        t.pt(f, x, y, c); t.pt(f, x, y+1, (220, 210, 180))
    for n in COTES:
        f = S_TETE[n]
        for i in range(8):
            for j in range(t.rnd.randint(0, 2)): t.pt(f, i, j, ramp(MOUSSE, 0.45))
    f = S_CORPS["back"]
    t.rect(f, 3, 0, 2, 12, ROUILLE, 0.45, relief=0.12)
    for y in (2, 8): t.rect(f, 2, y, 4, 1, LAITON, 0.45, relief=0)
    for pieces in (S_CORPS, S_BRAS, S_JAMBE):
        for n, f in pieces.items():
            if n in ("up", "down"): continue
            for _ in range(max(2, f[2] * f[3] // 12)):
                x, y = t.rnd.randrange(f[2]), t.rnd.randrange(f[3])
                if t.get(f, x, y)[3]: continue
                t.pt(f, x, y, ramp(MOUSSE, t.rnd.uniform(0.3, 0.7)))
            x = t.rnd.randrange(f[2])                                              # coulure
            for j in range(t.rnd.randint(1, 3), min(f[3], 9)): t.pt(f, x, j, ramp(ALGUE, 0.3 + j * 0.04))
    return t.im

PRODUITS = {"zombie/zombie.png": chauffeur, "zombie/husk.png": prospecteur, "zombie/drowned.png": scaphandrier,
            "zombie/drowned_outer_layer.png": scaphandrier_algues,
            "skeleton/stray_overlay.png": veilleur_cape, "skeleton/bogged_overlay.png": drainier_mousse}

if __name__ == "__main__":
    import os
    out = sys.argv[1]
    for chemin, fn in PRODUITS.items():
        p = os.path.join(out, chemin); os.makedirs(os.path.dirname(p), exist_ok=True); fn().save(p)
    print("ok")
