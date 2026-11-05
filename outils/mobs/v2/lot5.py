"""Lot 5 (revue) : Chaudière instable v3 (creeper), Rampeuses v3 (araignées), Creuset v2 (cube de magma),
Coffre blindé (shulker, chevauchement couvercle/socle corrigé), Ventilateur (breeze), Gardien des enfers v2 (wither),
Squelette de fonte v2 (wither skeleton), Forgerons v2 (piglin, piglin zombifié)."""
import math, sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import *
import lot2, lot3

JAUNE = lot2.JAUNE; ROUGE_ALERTE = (220, 40, 30)
FONTE = R((14, 12, 12), (26, 23, 22), (40, 36, 34), (58, 52, 48), (80, 72, 66), (106, 96, 88))
ACIER_BLEU = R((20, 26, 34), (32, 42, 54), (48, 62, 78), (70, 88, 106), (98, 118, 136), (134, 152, 168))
LAVE = [(255, 246, 180), (255, 196, 70), (240, 120, 24), (170, 54, 10), (90, 20, 6)]
ELECTRIQUE = [(230, 250, 255), (140, 220, 255), (60, 150, 230), (20, 70, 140)]

# =========================================================================== CHAUDIÈRE INSTABLE v3
def creeper():
    """Lisible de loin : un dôme de cuivre poli, LE visage du creeper en grille de foyer rougeoyante, une ceinture de danger."""
    t = Toile(64, 32, graine=301)
    TETE, CORPS, PATTE = faces(0, 0, 8, 8, 8), faces(16, 16, 8, 12, 4), faces(0, 16, 4, 6, 4)
    for n, f in TETE.items(): t.matiere(f, CUIVRE, 0.5, nom=n, bruit=0.035, biseau=0.14)
    f = TETE["front"]
    VISAGE = ["........", "........", ".##..##.", ".##..##.", "...##...", "..####..", "..####..", "..#..#.."]
    for j, l in enumerate(VISAGE):
        for i, c in enumerate(l):
            if c == "#":
                bord = any(not (0 <= j + dj < 8 and 0 <= i + di < 8 and VISAGE[j + dj][i + di] == "#") for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                t.pt(f, i, j, LAVE[2] if bord else LAVE[1])
    t.pt(f, 2, 2, LAVE[0]); t.pt(f, 5, 2, LAVE[0]); t.pt(f, 3, 5, LAVE[0]); t.pt(f, 4, 5, LAVE[0])
    t.hligne(f, 0, ramp(LAITON, 0.62)); t.rivets(f, [(0, 0), (7, 0)], LAITON)
    for n in ("right", "left", "back"):
        f = TETE[n]; t.hligne(f, 0, ramp(LAITON, 0.62)); t.couture(f, 4, CUIVRE); t.rivets(f, [(1, 2), (6, 2)], LAITON)
    t.jauge(TETE["right"], 2, 5, LAITON, aiguille=ROUGE_ALERTE)
    f = TETE["back"]; t.grille(f, 2, 5, 4, 2, FER, pas=1)                                   # évent
    f = TETE["up"]                                                                           # volant de soupape
    for (x, y) in ((3, 2), (4, 2), (2, 3), (5, 3), (2, 4), (5, 4), (3, 5), (4, 5)): t.pt(f, x, y, ramp(LAITON, 0.7))
    t.pt(f, 3, 3, ramp(FER, 0.2)); t.pt(f, 4, 4, ramp(FER, 0.2)); t.pt(f, 4, 3, ramp(LAITON, 0.9)); t.pt(f, 3, 4, ramp(LAITON, 0.5))
    for n, f in CORPS.items(): t.matiere(f, CUIVRE, 0.46, nom=n, bruit=0.035, stries=0)
    for n in COTES:
        f = CORPS[n]
        t.hligne(f, 0, ramp(LAITON, 0.6)); t.hligne(f, 1, ramp(LAITON, 0.4)); t.hligne(f, 11, ramp(LAITON, 0.35))
        for i in range(f[2]): t.pt(f, i, 7, ramp(JAUNE, 0.6) if (i // 2) % 2 == 0 else NOIR)         # ceinture de danger
        t.hligne(f, 6, ramp(CUIVRE, 0.2)); t.hligne(f, 8, ramp(CUIVRE, 0.7))
        for x in range(0, f[2], 3): t.rivet(f, x, 10, LAITON)
    f = CORPS["front"]; t.jauge(f, 2, 2, LAITON, aiguille=ROUGE_ALERTE)
    t.pt(f, 5, 3, LAVE[1]); t.pt(f, 6, 4, LAVE[2]); t.pt(f, 5, 5, LAVE[2])                 # une seule fissure, nette
    f = CORPS["back"]; t.rect(f, 2, 2, 4, 3, FER, 0.35); t.grille(f, 2, 3, 4, 1, FER)
    for n, f in PATTE.items():
        t.matiere(f, FER, 0.38, nom=n)
        if n in COTES: t.rect(f, 0, 4, 4, 2, LAITON, 0.5, relief=0.14); t.hligne(f, 0, ramp(FER, 0.6))
    return t.im

# =========================================================================== RAMPEUSES v3
def araignee(pal, accent, graine, reparation=False):
    im, yeux = lot2.rampeuse(pal, accent, graine, reparation)
    t = Toile(64, 32, graine=graine + 7); t.im = im; t.px = im.load()
    PATTE = faces(18, 0, 16, 2, 2); ABDO = faces(0, 12, 10, 8, 12)
    # pattes : fémur de fonte riveté, genou de laiton, tibia chromé, griffe sombre
    for n, f in PATTE.items():
        w, h = f[2], f[3]
        if n in ("right", "left"):
            t.matiere(f, LAITON, 0.5, nom=n, biseau=0.1); continue
        for x in range(w):
            for y in range(h):
                if x < 6: c = ramp(pal, 0.42 + (0.1 if y == 0 else -0.06))
                elif x < 8: c = ramp(LAITON, 0.7 if y == 0 else 0.42)
                elif x < 14: c = ramp(NICKEL, 0.78 if y == 0 else 0.5)
                else: c = ramp(FER, 0.12 if x == 15 else 0.28)
                if n == "down": c = mix(c, (0, 0, 0), 0.25)
                t.pt(f, x, y, c)
        t.pt(f, 2, 0, ramp(LAITON, 0.9)); t.pt(f, 4, 0, ramp(LAITON, 0.9))
        t.pt(f, 10, 0, ramp(NICKEL, 0.95)); t.pt(f, 11, 1, ramp(NICKEL, 0.3))
    # abdomen : flancs à persiennes, ventre à grille
    for n in ("right", "left"):
        f = ABDO[n]
        for x in range(2, f[2] - 2, 2): t.vligne(f, x, ramp(pal, 0.2), 2, 4)
    f = ABDO["down"]; t.grille(f, 2, 2, 6, 8, pal, pas=2)
    return t.im, yeux

# =========================================================================== CREUSET v2 (cube de magma)
def magma():
    """Anneaux de fonte fissurée empilés ; les coutures rougeoient, le cœur est en fusion."""
    t = Toile(64, 32, graine=331)
    # tranches (u, v) dans l'ordre du modèle ; faces latérales sur une ligne à v + 8
    TR = [(0, 0), (0, 1), (24, 10), (24, 19), (0, 4), (0, 5), (0, 6), (0, 7)]
    for i, (u, v) in reversed(list(enumerate(TR))):
        y = v + 8
        for x in range(32):
            k = x % 8
            if i == 0: c = ramp(LAITON, 0.55 if k not in (0, 7) else 0.35)          # bord de creuset
            elif i == 7: c = ramp(FONTE, 0.25)
            else:
                c = ramp(FONTE, 0.42 + 0.08 * math.sin(x * 1.3 + i))
                if (x * 7 + i * 5) % 11 == 0: c = LAVE[2]                            # fissures
                if (x * 3 + i * 7) % 17 == 0: c = LAVE[1]
            t.px[u + x, y] = c + (255,)
        if i in (2, 3):                                                               # yeux sur la face avant
            for xe in (2, 5): t.px[u + 8 + xe, y] = LAVE[0] + (255,)
    # dessus : couvercle de fonte, croix rougeoyante ; dessous
    f = (8, 0, 8, 8)
    t.matiere(f, FONTE, 0.45, nom="up", bruit=0.05)
    for k in range(8): t.pt(f, k, 3, LAVE[2] if k % 3 else LAVE[1]); t.pt(f, 3, k, LAVE[2] if k % 3 else LAVE[1])
    t.pt(f, 3, 3, LAVE[0]); t.rivets(f, [(0, 0), (7, 0), (0, 7), (7, 7)], LAITON)
    t.matiere((16, 7, 8, 8), FONTE, 0.2, nom="down")
    # cœur (4 x 4 x 4 en 0,16) : métal en fusion
    for n, f in faces(0, 16, 4, 4, 4).items():
        for y in range(4):
            for x in range(4):
                t.pt(f, x, y, LAVE[0] if (x in (1, 2) and y in (1, 2)) else LAVE[1] if (x + y) % 2 else LAVE[2])
    return t.im

# =========================================================================== COFFRE BLINDÉ (shulker)
def shulker():
    """Couvercle (16x12x16) et socle (16x8x16) se chevauchent sur 4 px quand ils sont fermés : les 4 dernières lignes du
    couvercle restent transparentes (sauf des dents), le socle montre à cet endroit sa ceinture de laiton."""
    t = Toile(64, 64, graine=341)
    COUV, SOCLE, TETE = faces(0, 0, 16, 12, 16), faces(0, 28, 16, 8, 16), faces(0, 52, 6, 6, 6)
    for n, f in COUV.items():
        t.matiere(f, ACIER_BLEU, 0.48, nom=n, bruit=0.03, biseau=0.1)
    f = COUV["up"]                                                         # blindage : plaques et hublot
    for (x, y, w, h) in ((1, 1, 6, 6), (9, 1, 6, 6), (1, 9, 6, 6), (9, 9, 6, 6)): t.rect(f, x, y, w, h, ACIER_BLEU, 0.52, relief=0.14)
    for (x, y) in ((1, 1), (6, 1), (9, 1), (14, 1), (1, 14), (6, 14), (9, 14), (14, 14)): t.rivet(f, x, y, NICKEL)
    for y in range(5, 11):
        for x in range(5, 11):
            d = math.hypot(x + .5 - 8, y + .5 - 8)
            if d < 3.2: t.pt(f, x, y, ramp(LAITON, 0.62 if d > 2.2 else 0.0) if d > 2.2 else (30, 40, 58))
    t.pt(f, 7, 7, (120, 150, 190)); t.pt(f, 6, 7, (80, 104, 140))
    t.matiere(COUV["down"], FONTE, 0.25, nom="down")
    for n in COTES:
        f = COUV[n]
        for x in range(16):
            for y in range(8, 12): t.vide(f, x, y)                         # zone de chevauchement : transparente
            if x % 4 in (1, 2): t.pt(f, x, 8, ramp(ACIER_BLEU, 0.3)); t.pt(f, x, 9, ramp(ACIER_BLEU, 0.22))   # dents
        t.hligne(f, 0, ramp(NICKEL, 0.8)); t.couture(f, 4, ACIER_BLEU, 0, 16)
        for x in (1, 5, 10, 14): t.rivet(f, x, 2, NICKEL); t.rivet(f, x, 6, NICKEL)
        t.hligne(f, 7, ramp(LAITON, 0.45))
    f = COUV["front"]; t.rect(f, 6, 1, 4, 5, LAITON, 0.5, relief=0.16); t.pt(f, 7, 3, NOIR); t.pt(f, 8, 3, NOIR); t.pt(f, 7, 4, NOIR)   # serrure
    for n, f in SOCLE.items(): t.matiere(f, FONTE, 0.4, nom=n, bruit=0.04)
    for n in COTES:
        f = SOCLE[n]
        t.rect(f, 0, 0, 16, 4, LAITON, 0.5, relief=0.14)                    # ceinture visible sous le couvercle
        for x in (2, 6, 9, 13): t.rivet(f, x, 1, LAITON)
        for x in range(16): t.pt(f, x, 6, ramp(JAUNE, 0.6) if (x // 2) % 2 == 0 else NOIR)
        t.hligne(f, 7, ramp(FONTE, 0.15))
    f = SOCLE["up"]                                                        # intérieur : mécanisme
    t.matiere(f, FONTE, 0.18, nom="up"); t.rect(f, 4, 4, 8, 8, FER, 0.3, relief=0.1)
    for (x, y) in ((7, 5), (8, 5), (5, 7), (10, 8), (7, 10), (8, 10), (5, 8), (10, 7)): t.pt(f, x, y, ramp(LAITON, 0.5))
    for n, f in TETE.items(): t.matiere(f, FONTE, 0.35, nom=n)            # la tête : une optique au bout d'une tige
    f = TETE["front"]; t.rect(f, 1, 1, 4, 4, LAITON, 0.45, relief=0.16); t.pt(f, 2, 2, (255, 60, 40)); t.pt(f, 3, 2, (200, 30, 20)); t.pt(f, 2, 3, (200, 30, 20)); t.pt(f, 3, 3, (120, 14, 10))
    return t.im

# =========================================================================== VENTILATEUR (breeze, 32x32)
def breeze():
    t = Toile(32, 32, graine=351)
    TETE, TIGE, COL = faces(0, 0, 8, 8, 8), faces(0, 17, 2, 8, 2), faces(4, 24, 10, 3, 4)
    for n, f in TETE.items(): t.matiere(f, NICKEL, 0.62, nom=n, bruit=0.03, biseau=0.12)
    f = TETE["front"]                                                       # hélice à quatre pales dans son carénage
    PALES = ["..####..", ".#.##.#.", "#..##..#", "########", "########", "#..##..#", ".#.##.#.", "..####.."]
    for y in range(8):
        for x in range(8):
            if PALES[y][x] == "#":
                bord = x in (0, 7) or y in (0, 7) or PALES[y][x] == "#" and (x in (1, 6) and y in (1, 6))
                t.pt(f, x, y, ramp(NICKEL, 0.35) if bord else ramp(LAITON, 0.75 if x < 4 and y < 4 else 0.55))
            else:
                t.pt(f, x, y, (30, 36, 48))
    for (x, y) in ((3, 3), (4, 4)): t.pt(f, x, y, ramp(LAITON, 0.95))
    t.pt(f, 4, 3, (120, 230, 255)); t.pt(f, 3, 4, (120, 230, 255))
    for n in ("right", "left", "back"):
        f = TETE[n]
        for y in range(2, 7, 2): t.hligne(f, y, (70, 78, 90), 2, 4)         # ouïes
        t.rivets(f, [(0, 0), (7, 0)], LAITON)
    f = TETE["up"]; t.grille(f, 1, 1, 6, 6, NICKEL, sombre=(44, 52, 64)); t.pt(f, 3, 3, ramp(LAITON, 0.7))
    for n, f in COL.items():                                                # col de laiton
        t.matiere(f, LAITON, 0.5, nom=n, biseau=0.16)
        if n in COTES:
            for x in range(0, f[2], 3): t.rivet(f, x, 1, LAITON)
    for n, f in TIGE.items():                                               # pistons chromés à bagues
        t.matiere(f, NICKEL, 0.66, nom=n, biseau=0.08)
        if n in COTES:
            t.hligne(f, 0, ramp(LAITON, 0.6)); t.hligne(f, 4, ramp(LAITON, 0.45)); t.hligne(f, 7, ramp(FER, 0.3))
    return t.im

# =========================================================================== GARDIEN DES ENFERS v2 (wither, 64x64)
def wither(invuln=False):
    t = Toile(64, 64, graine=361 if not invuln else 367)
    met = FONTE if not invuln else ACIER_BLEU
    feu = LAVE if not invuln else ELECTRIQUE
    TETE_C, TETE_S = faces(0, 0, 8, 8, 8), faces(32, 0, 6, 6, 6)
    EPAULES, ECHINE, QUEUE, COTES_ = faces(0, 16, 20, 3, 3), faces(0, 22, 3, 10, 3), faces(12, 22, 3, 6, 3), faces(24, 22, 11, 2, 2)
    def crane(F, w):
        for n, f in F.items(): t.matiere(f, met, 0.44, nom=n, bruit=0.04)
        f = F["front"]
        t.hligne(f, 0, ramp(LAITON, 0.5))
        e = 1 if w == 6 else 1
        for x0 in (e, w - e - 2):                                           # orbites-foyers
            t.pt(f, x0, 2, feu[1]); t.pt(f, x0 + 1, 2, feu[0]); t.pt(f, x0, 3, feu[2]); t.pt(f, x0 + 1, 3, feu[1])
        t.hligne(f, w - 2, ramp(LAITON, 0.42), 1, w - 2)                    # mâchoire de laiton
        for x in range(1, w - 1, 2): t.pt(f, x, w - 1, ramp(met, 0.12))     # dents
        t.pt(f, w // 2 - 1, w - 3, ramp(met, 0.1)); t.pt(f, w // 2, w - 3, ramp(met, 0.1))   # nez
        for n in ("right", "left"):
            ff = F[n]; t.rivet(ff, 1, 1, LAITON); t.rivet(ff, w - 2, 1, LAITON); t.hligne(ff, w // 2, ramp(met, 0.2))
        ff = F["up"]; t.vcouture(ff, w // 2 - 1, met, 0, w); t.rivet(ff, 1, 1, LAITON); t.rivet(ff, w - 2, w - 2, LAITON)
        ff = F["back"]; t.grille(ff, 1, w - 3, w - 2, 2, met, pas=2); t.lueur(ff, w // 2 - 1, 2, 2, 2, feu, fort=False)
    crane(TETE_C, 8); crane(TETE_S, 6)
    for n, f in EPAULES.items():                                            # poutre d'épaules
        t.matiere(f, met, 0.42, nom=n, biseau=0.12)
        if n in COTES and f[2] > 3:
            for x in (0, 1, f[2] - 2, f[2] - 1): t.vligne(f, x, ramp(LAITON, 0.5))
            for x in range(3, f[2] - 3, 4): t.rivet(f, x, 1, NICKEL)
    for n, f in ECHINE.items():                                             # vertèbres alternées fonte / laiton
        for y in range(f[3]):
            for x in range(f[2]): t.pt(f, x, y, ramp(LAITON if y % 3 == 0 else met, 0.5 if y % 3 == 0 else 0.4 + 0.05 * (x == 0)))
    for n, f in QUEUE.items():
        t.matiere(f, met, 0.35, nom=n)
        if n in COTES: t.hligne(f, 2, ramp(LAITON, 0.45)); t.pt(f, 1, f[3] - 1, feu[2])
    for n, f in COTES_.items():                                             # côtes : tuyaux
        t.matiere(f, met, 0.46, nom=n, biseau=0.15)
        if n in ("front", "back", "up", "down"):
            for x in range(0, f[2], 4): t.vligne(f, x, ramp(LAITON, 0.45))
    return t.im

# =========================================================================== SQUELETTE DE FONTE v2
def wither_squelette():
    """Moins de braises semées au hasard (le « quelque chose qui dérange ») : une fonte propre et sombre, des creux noirs,
    le feu concentré dans la cage thoracique et les yeux, des articulations de bronze."""
    import squelettes as S
    p = S.pal(((22, 20, 22), (38, 35, 38), (58, 54, 58), (86, 80, 84)),
              laiton={"b": (96, 56, 26), "B": (146, 92, 44), "Y": (196, 136, 70)},
              yeux=((255, 220, 110), (255, 140, 40)), creux=(10, 9, 10), cavite=(30, 14, 10), rouage=((120, 50, 14), (230, 120, 30)))
    def foyer(px, rnd):
        # la cage thoracique : quelques braises seulement, dans les cavités du torse
        for (x, y) in ((22, 23), (25, 23), (22, 25), (25, 25), (23, 21), (24, 21)):
            if px[x, y][3]: px[x, y] = (230, 110, 28, 255) if (x + y) % 2 else (255, 170, 60, 255)
        for _ in range(10):
            x, y = rnd.randrange(16, 40), rnd.randrange(20, 32)
            if px[x, y][3] and px[x, y][0] < 40: px[x, y] = (110, 40, 14, 255)
    return S.peindre(p, graine=133, retouche=foyer)

# =========================================================================== FORGERONS v2 (piglins)
def forgeron(calcine=False):
    import lot3 as L
    im = L.piglin(L.BRONZE if not calcine else L.SUIE, CUIVRE if not calcine else FER, L.OR if not calcine else LAITON,
                  111 if not calcine else 117, calcine=calcine, yeux=AMBRE if not calcine else BRAISE)
    t = Toile(graine=151 if not calcine else 157); t.im = im; t.px = im.load()
    f = L.TETE["front"]                                                     # lunettes de forge relevées sur le front
    for x in (1, 6):
        t.rect(f, x, 0, 3, 2, LAITON, 0.55, relief=0.18)
        t.pt(f, x + 1, 0, (150, 220, 230) if not calcine else (60, 60, 64)); t.pt(f, x + 1, 1, (90, 160, 180) if not calcine else (40, 40, 44))
    t.hligne(f, 0, ramp(CUIR, 0.35), 4, 2)
    for n in ("right", "left"): t.hligne(L.TETE[n], 0, ramp(CUIR, 0.35)); t.hligne(L.TETE[n], 1, ramp(CUIR, 0.25))
    if calcine: t.pt(f, 7, 0, NOIR); t.pt(f, 8, 1, NOIR)                     # verre brisé
    f = L.CORPS["front"]                                                    # tablier : marteau pendu, poche, chaîne d'or
    if not calcine:
        t.vligne(f, 6, ramp(FER, 0.45), 5, 4); t.rect(f, 5, 4, 3, 1, FER, 0.55, relief=0); t.pt(f, 6, 9, ramp(CUIR, 0.2))
        t.rect(f, 1, 7, 3, 3, CUIR, 0.3, relief=0.12); t.pt(f, 2, 7, ramp(L.OR, 0.7))
    else:
        for (x, y) in ((2, 4), (3, 6), (6, 9)): t.pt(f, x, y, BRAISE[1])
    for n in ("front", "back"):                                              # sangles croisées
        g = L.CORPS[n]
        for k in range(8): t.pt(g, k, k + 1 if n == "front" else 8 - k, ramp(CUIR, 0.28))
    for o in (L.BRAS_D, L.BRAS_G):                                           # brassards d'or martelé
        for n in COTES:
            g = o[n]; t.hligne(g, 6, ramp(L.OR if not calcine else LAITON, 0.75)); t.rivet(g, 1, 7, L.OR if not calcine else LAITON)
    for o in (L.JAMBE_D, L.JAMBE_G):
        for n in COTES: t.pt(o[n], 1, 9, ramp(L.OR if not calcine else LAITON, 0.8))
    return t.im

def produits():
    sp, spy = araignee(FER, CUIVRE, 101)
    cs, csy = araignee(lot2.BLEU_ENTRETIEN, JAUNE, 103, reparation=True)
    return {"creeper/creeper.png": creeper(), "spider/spider.png": sp, "spider_eyes.png": spy, "spider/cave_spider.png": cs,
            "slime/magmacube.png": magma(), "shulker/shulker.png": shulker(), "breeze/breeze.png": breeze(),
            "wither/wither.png": wither(), "wither/wither_invulnerable.png": wither(True),
            "skeleton/wither_skeleton.png": wither_squelette(), "piglin/piglin.png": forgeron(), "piglin/zombified_piglin.png": forgeron(True)}

if __name__ == "__main__":
    import os
    out = sys.argv[1]
    for chemin, im in produits().items():
        p = os.path.join(out, chemin); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
    print("ok")
