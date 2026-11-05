"""Lot 4 : Âme sans repos (phantom + yeux), Graisse vivante (slime), Torpilleur (guardian), Gardien des marées (elder guardian)."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import *

GRIS_NAVAL = R((40, 46, 52), (62, 70, 78), (88, 96, 104), (114, 122, 130), (142, 150, 156), (174, 180, 186))
IVOIRE = R((110, 100, 80), (150, 138, 112), (186, 174, 146), (214, 204, 178), (232, 224, 202), (248, 244, 230))
ROUGE_COQUE = R((50, 10, 10), (86, 18, 14), (120, 28, 20), (150, 40, 28), (176, 62, 46), (200, 96, 80))
SPECTRE_V = R((20, 40, 52), (34, 64, 80), (54, 96, 112), (84, 134, 146), (130, 176, 182), (196, 230, 230))
ECHO = [(240, 210, 255), (190, 120, 250), (130, 60, 200), (70, 24, 120)]
HUILE = R((14, 10, 6), (28, 20, 10), (48, 34, 16), (74, 52, 24), (104, 76, 36), (140, 108, 56))

# =========================================================================== ÂME SANS REPOS (64x64)
def ame():
    t = Toile(64, 64, graine=191)
    TETE, CORPS = faces(0, 0, 7, 3, 5), faces(0, 8, 5, 3, 9)
    QUEUE, POINTE = faces(3, 20, 3, 2, 6), faces(4, 29, 1, 1, 6)
    AILE, BOUT = faces(23, 12, 6, 2, 9), faces(16, 24, 13, 1, 9)
    for p in (TETE, CORPS, QUEUE, POINTE):
        for n, f in p.items(): t.matiere(f, SPECTRE_V, 0.5, nom=n, bruit=0.07, biseau=0.1)
    for n in ("up", "right", "left"):                         # cœur d'écho qui transparaît
        f = CORPS[n]; t.pt(f, f[2] // 2, f[3] // 2, ECHO[1]); t.pt(f, f[2] // 2, f[3] // 2 - 1 if f[3] > 2 else 0, ECHO[2])
    f = TETE["front"]; t.hligne(f, 2, ramp(SPECTRE_V, 0.2))
    t.pt(f, 0, 1, ramp(SPECTRE_V, 0.15)); t.pt(f, 6, 1, ramp(SPECTRE_V, 0.15))
    for n in ("up", "down"):                                  # ailes : voile déchiré, nervures de laiton terni
        for p, ls in ((AILE, 6), (BOUT, 13)):
            f = p[n]
            for j in range(f[3]):
                for i in range(f[2]):
                    if p is BOUT and i > f[2] - 1 - (j % 3) * 2 and t.rnd.random() < 0.7: t.vide(f, i, j); continue
                    t.pt(f, i, j, ramp(SPECTRE_V, 0.55 + 0.1 * ((i + j) % 2) + t.rnd.uniform(-0.05, 0.05)))
            for j in range(0, f[3], 3): t.hligne(f, j, ramp(LAITON, 0.35 if n == "up" else 0.25), 0, f[2] - (2 if p is BOUT else 0))
    for p in (AILE, BOUT):
        for n in COTES: t.matiere(p[n], LAITON, 0.35, nom=n, biseau=0.05)
    yeux = Image.new("RGBA", (64, 64), (0, 0, 0, 0)); py = yeux.load()
    for (x, y), c in zip(((5, 6), (6, 6), (10, 6), (11, 6)), (ECHO[1], ECHO[0], ECHO[0], ECHO[1])): py[x, y] = c + (255,)
    return t.im, yeux

# =========================================================================== GRAISSE VIVANTE (slime, 64x32)
def graisse():
    t = Toile(64, 32, graine=197)
    EXT, INT = faces(0, 0, 8, 8, 8), faces(0, 16, 6, 6, 6)
    OEIL_D, OEIL_G, BOUCHE = faces(32, 0, 2, 2, 2), faces(32, 4, 2, 2, 2), faces(32, 8, 1, 1, 1)
    for n, f in EXT.items():                                   # pellicule d'huile translucide, reflets irisés
        for j in range(f[3]):
            for i in range(f[2]):
                c = ramp(HUILE, 0.45 + t.rnd.uniform(-0.06, 0.06) + (0.15 if j == 0 else 0))
                if (i + 2 * j) % 13 == 0: c = mix(c, (110, 90, 160), 0.3)       # irisation violette
                elif (2 * i + j) % 17 == 0: c = mix(c, (80, 140, 120), 0.3)   # irisation verte
                t.pt(f, i, j, c, a=180)
        t.pt(f, 1, 1, (210, 200, 170), a=200); t.pt(f, 2, 1, (170, 160, 130), a=190)
    for n, f in INT.items():                                   # noyau : rouage de laiton dans la graisse
        t.matiere(f, LAITON, 0.4, nom=n, biseau=0.12)
        for (x, y) in ((0, 0), (5, 0), (0, 5), (5, 5), (2, 0), (3, 5), (0, 3), (5, 2)): t.pt(f, x, y, ramp(HUILE, 0.3))
        t.plein(f, 2, 2, 2, 2, ramp(HUILE, 0.15))
    for o in (OEIL_D, OEIL_G):                                 # yeux : écrous
        for n, f in o.items(): t.matiere(f, NICKEL, 0.6, nom=n, biseau=0.2)
        t.pt(o["front"], 0, 0, ramp(NICKEL, 0.95)); t.pt(o["front"], 1, 1, NOIR)
    for n, f in BOUCHE.items(): t.pt(f, 0, 0, NOIR)
    return t.im

# =========================================================================== TORPILLEURS (guardian, 64x64)
def torpilleur(ancien=False):
    t = Toile(64, 64, graine=211 if not ancien else 223)
    coque = IVOIRE if ancien else GRIS_NAVAL
    filet = OR if ancien else ROUGE_COQUE
    CORPS = faces(0, 0, 12, 12, 16); OEIL = faces(8, 0, 2, 2, 1)
    PIC = faces(0, 0, 2, 9, 2)
    Q1, Q2, Q3, AILERON = faces(40, 0, 4, 4, 8), faces(0, 54, 3, 3, 7), faces(41, 32, 2, 2, 6), faces(25, 19, 1, 9, 9)
    for n, f in CORPS.items():
        t.matiere(f, coque, 0.5, nom=n, taches=(VDG if ancien else ROUILLE, 6, 0.45))
        if n in COTES:
            for y in (3, 7): t.couture(f, y, coque)
            for x in range(1, f[2], 3): t.rivet(f, x, 1, coque if not ancien else OR); t.rivet(f, x, 10, coque)
            t.rect(f, 0, f[3] - 2, f[2], 2, filet, 0.45, relief=0.1)                 # ligne de flottaison
    f = CORPS["front"]                                   # proue : anneau de laiton autour de l'œil, tubes lance-torpilles
    t.rect(f, 3, 2, 6, 6, LAITON if not ancien else OR, 0.5, relief=0.22); t.plein(f, 4, 3, 4, 4, NOIR)
    for x in (1, 9): t.rect(f, x, 8, 2, 2, FER, 0.3, relief=0.1); t.pt(f, x, 8, NOIR)
    f = CORPS["up"]                                      # pont : écoutille, tourelle de veille
    t.rect(f, 3, 4, 6, 6, coque, 0.62, relief=0.16); t.rect(f, 5, 6, 2, 2, LAITON if not ancien else OR, 0.6)
    t.vcouture(f, 5, coque, 0, 3)
    if ancien:                                           # bernacles et coraux sur le vieux gardien
        for p in (CORPS,):
            for n, f in p.items():
                for _ in range(3): t.pt(f, t.rnd.randrange(f[2]), t.rnd.randrange(f[3]), t.rnd.choice([(170, 166, 150), (96, 130, 110)]))
    for n, f in OEIL.items():                            # œil : projecteur
        t.matiere(f, LAITON, 0.5, nom=n, biseau=0.1)
    f = OEIL["front"]; t.pt(f, 0, 0, (255, 240, 200)); t.pt(f, 1, 0, (255, 200, 120)); t.pt(f, 0, 1, (255, 200, 120)); t.pt(f, 1, 1, (220, 120, 60))
    for n, f in PIC.items():                             # pics : antennes et ailerons d'acier, pointe peinte
        if n in COTES:
            for j in range(f[3]):
                for i in range(f[2]): t.pt(f, i, j, ramp(FER, 0.5 + 0.12 * (1 - i) - 0.03 * j) if j > 1 else ramp(filet, 0.55))
    for q in (Q1, Q2, Q3):
        for n, f in q.items():
            t.matiere(f, coque, 0.48, nom=n)
            if n in COTES and f[3] > 2: t.hligne(f, f[3] - 1, ramp(filet, 0.45))
            if n in ("right", "left", "up") and f[2] > 3:
                for x in range(1, f[2], 3): t.rivet(f, x, 0, coque)
    for n in ("right", "left"):                          # hélice de laiton
        f = AILERON[n]
        for j in range(f[3]):
            for i in range(f[2]):
                if abs(i - 4) + abs(j - 4) <= 1: t.pt(f, i, j, ramp(LAITON, 0.7))
                elif (i == 4 or j == 4) and abs(i - 4) + abs(j - 4) <= 4: t.pt(f, i, j, ramp(LAITON if not ancien else OR, 0.5))
                elif abs(i - 4) == abs(j - 4) and abs(i - 4) <= 2: t.pt(f, i, j, ramp(LAITON, 0.35))
    return t.im

def produits():
    a, ay = ame()
    return {"phantom.png": a, "phantom_eyes.png": ay, "slime/slime.png": graisse(),
            "guardian.png": torpilleur(), "guardian_elder.png": torpilleur(ancien=True)}

if __name__ == "__main__":
    import os
    out = sys.argv[1]
    for chemin, im in produits().items():
        p = os.path.join(out, chemin); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
    print("ok")
