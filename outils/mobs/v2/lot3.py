"""Lot 3 : le Nether. Forgeron de l'abîme / Garde de la forge / Forgeron calciné (piglins), Bélier-locomotive / Épave (hoglins),
Lanterne de forge (blaze), Dirigeable fantôme (ghast), Creuset vivant (magma cube), Gardien des enfers (wither)."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import *
V = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/entity/"

OR = R((90, 56, 8), (140, 96, 16), (190, 140, 30), (226, 182, 52), (246, 214, 96), (255, 240, 170))
BRONZE = R((40, 26, 16), (66, 44, 26), (96, 66, 38), (126, 90, 52), (156, 116, 70), (186, 146, 96))
ACIER_NOIR = R((10, 10, 12), (20, 20, 24), (32, 32, 38), (48, 48, 56), (70, 70, 80), (100, 100, 112))
VERT_LOCO = R((10, 30, 22), (16, 46, 32), (24, 64, 44), (36, 84, 58), (54, 108, 74), (84, 136, 100))
ROUGE_LOCO = R((50, 8, 8), (84, 14, 12), (120, 24, 18), (152, 36, 26), (182, 60, 44), (210, 100, 80))
FUMEE = R((40, 40, 44), (64, 64, 68), (92, 92, 96), (122, 122, 126), (156, 156, 160), (196, 196, 200))
SPECTRE = R((120, 128, 140), (156, 164, 176), (190, 198, 208), (214, 220, 228), (232, 236, 242), (248, 250, 252))

# =========================================================================== PIGLINS (64x64, tête de 10 de large)
TETE = faces(0, 0, 10, 8, 8); GROIN = faces(31, 1, 4, 4, 1)
OREILLE_D, OREILLE_G = faces(39, 6, 1, 5, 4), faces(51, 6, 1, 5, 4)
DEFENSE_A, DEFENSE_B = faces(2, 0, 1, 2, 1), faces(2, 4, 1, 2, 1)
CORPS = faces(16, 16, 8, 12, 4)
BRAS_D, BRAS_G, JAMBE_D, JAMBE_G = faces(40, 16, 4, 12, 4), faces(32, 48, 4, 12, 4), faces(0, 16, 4, 12, 4), faces(16, 48, 4, 12, 4)

def gauche(t):
    for src, dst in ((BRAS_D, BRAS_G), (JAMBE_D, JAMBE_G)):
        for n in ("front", "back", "up", "down"): t.miroir(src[n], dst[n])
        t.miroir(src["right"], dst["left"]); t.miroir(src["left"], dst["right"])

def piglin(peau, armure, garni, graine, yeux=AMBRE, garde=False, calcine=False):
    t = Toile(graine=graine)
    usure = (SUIE, 14, 0.25) if calcine else None
    # tête : masque de forge ; groin = embout de soufflet, oreilles = ailettes, défenses = goupilles
    for n, f in TETE.items(): t.matiere(f, peau, 0.45, nom=n, taches=usure)
    f = TETE["front"]
    if garde:
        t.rect(f, 0, 0, 10, 8, armure, 0.45, relief=0.16)
        t.grille(f, 1, 5, 8, 2, armure, pas=2)
    else:
        t.rect(f, 0, 0, 10, 2, armure, 0.55, relief=0.12)
    t.hligne(f, 2, ramp(peau, 0.15))
    for x in (2, 6):                                   # optiques
        t.rect(f, x, 3, 2, 2, garni, 0.5, relief=0.2); t.pt(f, x, 3, yeux[0]); t.pt(f, x+1, 4, yeux[2]); t.pt(f, x+1, 3, yeux[1]); t.pt(f, x, 4, yeux[1])
    t.rivets(f, [(0, 1), (9, 1)], garni)
    for n in ("right", "left"):
        f = TETE[n]; t.rect(f, 0, 0, 8, 2, armure, 0.5); t.rect(f, 2, 3, 3, 3, garni, 0.45, relief=0.16); t.pt(f, 3, 4, ramp(FER, 0.2))
    f = TETE["back"]; t.rect(f, 0, 0, 10, 2, armure, 0.45); t.grille(f, 2, 4, 6, 2, peau)
    f = TETE["up"]; t.rect(f, 1, 1, 8, 6, armure, 0.55, relief=0.12); t.vcouture(f, 4, armure, 1, 6)
    for n, f in GROIN.items():                         # embout de soufflet
        t.matiere(f, garni, 0.5, nom=n, biseau=0.15)
    f = GROIN["front"]; t.rect(f, 0, 0, 4, 4, garni, 0.55, relief=0.2); t.pt(f, 1, 2, NOIR); t.pt(f, 2, 2, NOIR)
    for o in (OREILLE_D, OREILLE_G):                   # ailettes de refroidissement
        for n, f in o.items():
            t.matiere(f, CUIVRE if not calcine else SUIE, 0.5, nom=n, biseau=0.1)
            for j in range(0, f[3], 2): t.hligne(f, j, ramp(CUIVRE if not calcine else SUIE, 0.25))
    for d in (DEFENSE_A, DEFENSE_B):
        for n, f in d.items(): t.matiere(f, OR if not calcine else LAITON, 0.7, nom=n, biseau=0.15)
    # corps
    for n, f in CORPS.items(): t.matiere(f, peau, 0.42, nom=n, taches=usure)
    if garde:                                          # cuirasse noire à filets d'or
        for n in ("front", "back"):
            f = CORPS[n]; t.rect(f, 0, 0, 8, 8, armure, 0.45, relief=0.16)
            t.hligne(f, 0, ramp(garni, 0.6)); t.vligne(f, 0, ramp(garni, 0.5), 0, 8); t.vligne(f, 7, ramp(garni, 0.4), 0, 8)
            t.rivets(f, [(2, 2), (5, 2), (2, 5), (5, 5)], garni)
        t.rect(CORPS["front"], 3, 3, 2, 2, garni, 0.6, relief=0.2)
    else:                                              # tablier de forgeron, chaîne d'or
        f = CORPS["front"]; t.rect(f, 1, 2, 6, 10, CUIR, 0.45, relief=0.08)
        for k in range(6): t.pt(f, 1 + k, 1 + (1 if k in (2, 3) else 0), ramp(garni, 0.65 if k % 2 else 0.45))
        t.pt(f, 3, 5, ramp(garni, 0.8)); t.pt(f, 4, 5, ramp(garni, 0.6))
        t.rect(CORPS["back"], 0, 7, 8, 1, CUIR, 0.4, relief=0); t.vligne(CORPS["back"], 3, ramp(CUIR, 0.4), 0, 7)
        t.vligne(CORPS["back"], 4, ramp(CUIR, 0.3), 0, 7)
    for n in ("front", "back", "right", "left"):
        t.rect(CORPS[n], 0, 8, CORPS[n][2], 1, CUIR, 0.35, relief=0)
    t.pt(CORPS["front"], 3, 8, ramp(garni, 0.8)); t.pt(CORPS["front"], 4, 8, ramp(garni, 0.6))
    if calcine:                                        # plaques arrachées : rouages et braises visibles
        for (x, y, w, h) in ((4, 2, 3, 3), (1, 9, 2, 2)):
            t.plein(CORPS["front"], x, y, w, h, ramp(SUIE, 0.1)); t.pt(CORPS["front"], x+1, y+1, BRAISE[1])
        t.lueur(CORPS["back"], 2, 2, 3, 3, BRAISE, fort=False)
    # bras : brassards dorés, gants de forge
    for n, f in BRAS_D.items():
        t.matiere(f, peau, 0.45, nom=n, taches=usure)
        if n in COTES:
            if garde: t.rect(f, 0, 0, 4, 4, armure, 0.5, relief=0.14); t.hligne(f, 3, ramp(garni, 0.55))
            t.rect(f, 0, 7, 4, 2, garni, 0.5, relief=0.14)
            t.rect(f, 0, 9, 4, 3, CUIR if not calcine else SUIE, 0.35, relief=0.08)
    # jambes : culotte de cuir, bottes de fer
    for n, f in JAMBE_D.items():
        t.matiere(f, CUIR if not calcine else SUIE, 0.42, nom=n)
        if n in COTES:
            if garde: t.rect(f, 0, 2, 4, 4, armure, 0.5, relief=0.14)
            t.rect(f, 0, 8, 4, 4, ACIER_NOIR if garde else FER, 0.45, relief=0.14); t.hligne(f, 8, ramp(garni, 0.55))
    gauche(t)
    return t.im

# =========================================================================== HOGLINS (128x64)
H_TETE = faces(61, 1, 14, 6, 19); H_OREILLES = (faces(1, 1, 6, 1, 4), faces(1, 6, 6, 1, 4))
H_CORNES = (faces(10, 13, 2, 11, 2), faces(1, 13, 2, 11, 2)); H_CORPS = faces(1, 1, 16, 14, 26)
H_CRINIERE = faces(90, 33, 0, 10, 19)
H_PATTES = (faces(66, 42, 6, 14, 6), faces(41, 42, 6, 14, 6), faces(21, 45, 5, 11, 5), faces(0, 45, 5, 11, 5))

def belier(epave=False, graine=131):
    t = Toile(128, 64, graine=graine)
    peint = ROUILLE if epave else VERT_LOCO
    taches = (ROUILLE, 40, 0.4) if not epave else (SUIE, 50, 0.2)
    # tête : avant de locomotive (chasse-pierres, phare, plaque)
    for n, f in H_TETE.items(): t.matiere(f, ACIER_NOIR, 0.5, nom=n, taches=(ROUILLE, 6, 0.4))
    f = H_TETE["front"]                     # 14 x 6
    t.rect(f, 0, 0, 14, 3, peint, 0.5, relief=0.14)
    t.rect(f, 5, 0, 4, 3, LAITON, 0.5, relief=0.2)
    if epave: t.plein(f, 6, 1, 2, 1, NOIR)
    else: t.pt(f, 6, 1, AMBRE[0]); t.pt(f, 7, 1, AMBRE[1])
    for x in range(14):                     # chasse-pierres
        for y in (3, 4, 5): t.pt(f, x, y, ramp(ROUGE_LOCO if not epave else ROUILLE, 0.45 - 0.1*(y-3)) if (x + y) % 2 else NOIR)
    f = H_TETE["up"]                        # 14 x 19 : plaque de boîte à fumée
    t.rect(f, 1, 1, 12, 17, peint, 0.5, relief=0.12)
    for y in (4, 10, 16): t.couture(f, y, peint, 1, 12)
    t.rivets(f, [(1, 1), (12, 1), (1, 17), (12, 17)], LAITON)
    for n in ("right", "left"):
        f = H_TETE[n]; t.rect(f, 0, 0, 19, 3, peint, 0.48); t.hligne(f, 3, ramp(ROUGE_LOCO, 0.5))
    for o in H_OREILLES:
        for n, f in o.items(): t.matiere(f, LAITON, 0.5, nom=n, biseau=0.1)
    for c in H_CORNES:                     # sifflets à vapeur
        for n, f in c.items():
            t.matiere(f, LAITON if not epave else ROUILLE, 0.55, nom=n, biseau=0.1)
            if n in COTES:
                for y in (2, 6, 9): t.hligne(f, y, ramp(LAITON, 0.25))
    # corps : chaudière cerclée de laiton, dôme de vapeur, châssis rouge
    for n, f in H_CORPS.items(): t.matiere(f, peint, 0.48, nom=n, taches=taches)
    f = H_CORPS["up"]                       # 16 x 26 (dos)
    for y in range(2, 26, 6): t.rect(f, 0, y, 16, 1, LAITON, 0.55, relief=0)
    t.rect(f, 5, 8, 6, 5, LAITON, 0.5, relief=0.2); t.plein(f, 7, 10, 2, 1, ramp(LAITON, 0.85))   # dôme
    t.rect(f, 6, 17, 4, 4, ACIER_NOIR, 0.4, relief=0.12); t.plein(f, 7, 18, 2, 2, NOIR)            # cheminée
    for n in ("right", "left"):             # 26 x 14
        f = H_CORPS[n]
        for x in range(2, 26, 6): t.rect(f, x, 0, 1, 10, LAITON, 0.5, relief=0)
        t.rect(f, 0, 10, 26, 4, ROUGE_LOCO if not epave else ROUILLE, 0.45, relief=0.12)
        t.rivets(f, [(x, 11) for x in range(1, 26, 3)], LAITON)
        if not epave: t.rect(f, 10, 3, 6, 4, LAITON, 0.55, relief=0.2)                   # plaque de l'Empire
        else:
            for (x, y) in ((8, 4), (9, 5), (15, 3), (20, 6)): t.plein(f, x, y, 2, 2, NOIR)  # trous
    for n in ("front", "back"):
        f = H_CORPS[n]; t.rect(f, 2, 2, 12, 8, ACIER_NOIR, 0.45, relief=0.14); t.rect(f, 0, 10, 16, 4, ROUGE_LOCO if not epave else ROUILLE, 0.45)
        t.rect(f, 6, 4, 4, 4, LAITON, 0.5, relief=0.2); t.plein(f, 7, 5, 2, 2, ramp(LAITON, 0.2))
    # crinière : panache de fumée (dégradé)
    for n, f in H_CRINIERE.items():
        if f[2] == 0: continue
        for j in range(f[3]):
            for i in range(f[2]):
                if t.rnd.random() < 0.25 + 0.06 * j: continue
                t.pt(f, i, j, ramp(FUMEE, 0.75 - 0.05 * j + t.rnd.uniform(-0.08, 0.08)))
    # pattes : cylindres et roues rouges à rayons
    for p in H_PATTES:
        for n, f in p.items():
            t.matiere(f, ACIER_NOIR, 0.45, nom=n)
            if n in ("right", "left"):
                w, h = f[2], f[3]; cx, cy = w // 2, h - w // 2 - 1
                for j in range(h):
                    for i in range(w):
                        d = abs(i - cx) + abs(j - cy)
                        if d <= w // 2:
                            c = ROUGE_LOCO if not epave else ROUILLE
                            t.pt(f, i, j, ramp(c, 0.55) if d == w // 2 else (ramp(LAITON, 0.6) if d == 0 else ramp(c, 0.3 if (i + j) % 2 else 0.45)))
            if n in ("front", "back"): t.hligne(f, 2, ramp(LAITON, 0.5))
    return t.im

# =========================================================================== LANTERNE DE FORGE (blaze, 64x32)
def lanterne():
    t = Toile(64, 32, graine=151)
    TETE, TIGE = faces(0, 0, 8, 8, 8), faces(0, 16, 2, 8, 2)
    for n, f in TETE.items():
        if n in COTES:                      # vitres ambrées, flamme au centre, armature de laiton
            for j in range(8):
                for i in range(8):
                    d = abs(i - 3.5) + abs(j - 4.5)
                    t.pt(f, i, j, BRAISE[0] if d < 1.6 else BRAISE[1] if d < 3 else BRAISE[2] if d < 4.5 else (150, 60, 16))
            t.vligne(f, 0, ramp(LAITON, 0.6)); t.vligne(f, 7, ramp(LAITON, 0.35)); t.hligne(f, 0, ramp(LAITON, 0.7)); t.hligne(f, 7, ramp(LAITON, 0.3))
            t.vligne(f, 3, ramp(LAITON, 0.4), 1, 6); t.vligne(f, 4, ramp(LAITON, 0.25), 1, 6)
        else:
            t.matiere(f, LAITON, 0.5, nom=n, biseau=0.12)
            if n == "up": t.rect(f, 2, 2, 4, 4, LAITON, 0.65, relief=0.2); t.plein(f, 3, 3, 2, 2, ramp(FER, 0.15))
    f = TETE["front"]                       # deux taches de suie : les yeux
    for (x, y) in ((1, 3), (2, 3), (5, 3), (6, 3)): t.pt(f, x, y, (40, 22, 12))
    for n, f in TIGE.items():               # tuyaux de fonte, bagues de laiton, bout incandescent
        t.matiere(f, FER, 0.5, nom=n, biseau=0.1)
        if n in COTES:
            for y in (1, 4): t.hligne(f, y, ramp(LAITON, 0.55))
            t.hligne(f, 7, BRAISE[1]); t.hligne(f, 6, BRAISE[2])
    t.plein(TIGE["down"], 0, 0, 2, 2, BRAISE[0])
    return t.im

# =========================================================================== DIRIGEABLE FANTÔME (ghast, 64x32)
def dirigeable(tir=False):
    t = Toile(64, 32, graine=163)
    CORPS, TENT = faces(0, 0, 16, 16, 16), faces(0, 0, 2, 15, 2)
    for n, f in CORPS.items():
        t.matiere(f, SPECTRE, 0.5, nom=n, bruit=0.04, biseau=0.08)
        if n in COTES or n == "up":
            for x in range(0, 16, 4): t.vligne(f, x, ramp(SPECTRE, 0.25))            # fuseaux de l'enveloppe
            for k in range(-16, 16, 8):                                                # filet de cordage
                for i in range(16):
                    for y in (i + k, 15 - i + k):
                        if 0 <= y < 16 and (n != "front" or not (3 <= y <= 12)): t.pt(f, i, y, ramp(CORDE, 0.55))
    f = CORPS["down"]                         # nacelle de bois sous le ballon
    t.matiere(f, CUIR, 0.5, nom="down", stries=3)
    t.rect(f, 2, 2, 12, 12, CUIR, 0.6, relief=0.12)
    for x in (4, 8, 11): t.plein(f, x, 7, 2, 2, AMBRE[2] if not tir else AMBRE[0])
    f = CORPS["front"]                        # visage : hublots et trappe de canon
    t.rect(f, 1, 3, 14, 10, SPECTRE, 0.55, relief=0.06)
    for x in (3, 9):
        t.rect(f, x, 4, 4, 4, LAITON, 0.5, relief=0.2)
        if tir:
            t.plein(f, x+1, 5, 2, 2, BRAISE[1]); t.pt(f, x+1, 5, BRAISE[0])
        else:
            t.plein(f, x+1, 5, 2, 2, ramp(LAITON, 0.25)); t.hligne(f, 6, ramp(LAITON, 0.7), x+1, 2)   # volets fermés
    t.rect(f, 5, 9, 6, 3, FER, 0.45, relief=0.14)
    if tir: t.lueur(f, 6, 10, 4, 1, BRAISE, fort=False); t.plein(f, 7, 10, 2, 1, BRAISE[0])
    else: t.hligne(f, 10, ramp(FER, 0.2), 6, 4)
    t.rivets(f, [(5, 9), (10, 9)], LAITON)
    # amarres : cordes, lest de laiton au bout
    for n, f in TENT.items():
        if n in COTES:
            for j in range(f[3]):
                for i in range(2): t.pt(f, i, j, ramp(CORDE, 0.45 + (0.15 if (i + j) % 2 else 0)))
            for j in range(12, 15):
                for i in range(2): t.pt(f, i, j, ramp(LAITON, 0.5 + (0.15 if i == 0 else -0.05)))
    return t.im

# =========================================================================== REMAPPAGE (creuset, gardien des enfers)
def remap(chemin, regles, graine):
    """Garde le dessin vanilla : chaque pixel est reporté sur une nouvelle palette selon sa luminance et sa teinte."""
    im = Image.open(V + chemin).convert("RGBA"); px = im.load(); rnd = random.Random(graine)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a: continue
            lum = (0.3*r + 0.59*g + 0.11*b) / 255
            px[x, y] = regles(r, g, b, lum, rnd) + (a,)
    return im

def creuset():
    def r(r_, g, b, lum, rnd):
        if r_ > 150 and r_ > g * 1.3:        # lave : métal en fusion
            return BRAISE[0] if lum > 0.7 else BRAISE[1] if lum > 0.5 else BRAISE[2]
        return ramp(ACIER_NOIR, lum * 1.6 + rnd.uniform(-0.03, 0.03)) if lum < 0.35 else ramp(LAITON, lum)
    return remap("slime/magmacube.png", r, 171)

def gardien_enfers(invuln=False):
    def r(r_, g, b, lum, rnd):
        if invuln:
            return ramp(R((20, 30, 60), (40, 70, 130), (70, 120, 200), (120, 170, 240), (180, 210, 255), (230, 240, 255)), lum * 1.4)
        if lum > 0.55: return ramp(OR, lum)               # os clairs → ornements dorés
        return ramp(ACIER_NOIR, lum * 3.4 + rnd.uniform(-0.03, 0.03))
    im = remap("wither/wither_invulnerable.png" if invuln else "wither/wither.png", r, 181)
    if not invuln:                                        # yeux incandescents des trois têtes
        px = im.load()
        for (x, y) in ((9, 12), (10, 12), (13, 12), (14, 12), (38, 8), (39, 8), (42, 8), (43, 8)):
            if px[x, y][3]: px[x, y] = BRAISE[1] + (255,)
    return im

def produits():
    return {"piglin/piglin.png": piglin(BRONZE, CUIVRE, OR, 111),
            "piglin/piglin_brute.png": piglin(ACIER_NOIR, ACIER_NOIR, OR, 113, garde=True, yeux=BRAISE),
            "piglin/zombified_piglin.png": piglin(SUIE, FER, LAITON, 117, calcine=True, yeux=BRAISE),
            "hoglin/hoglin.png": belier(), "hoglin/zoglin.png": belier(epave=True, graine=133),
            "blaze.png": lanterne(), "ghast/ghast.png": dirigeable(), "ghast/ghast_shooting.png": dirigeable(tir=True),
            "slime/magmacube.png": creuset(), "wither/wither.png": gardien_enfers(), "wither/wither_invulnerable.png": gardien_enfers(True)}

if __name__ == "__main__":
    import os
    out = sys.argv[1]
    for chemin, im in produits().items():
        p = os.path.join(out, chemin); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
    print("ok")
