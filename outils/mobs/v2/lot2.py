"""Lot 2 : Chaudière instable (creeper), Rampeuse mécanique (spider + yeux), Rampeuse de réparation (cave spider),
Égaré du Vide (enderman + yeux), Puce du vide (endermite), Ver de forage (silverfish)."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import *

ROUGE_ALERTE = (220, 40, 30)
JAUNE = R((80, 60, 10), (140, 108, 20), (196, 156, 30), (232, 196, 52), (248, 222, 100), (255, 240, 170))
BLEU_ENTRETIEN = R((14, 30, 46), (22, 48, 72), (34, 70, 102), (52, 96, 132), (78, 126, 162), (120, 164, 196))
OBSID = R((6, 4, 10), (12, 8, 20), (20, 14, 32), (32, 22, 48), (48, 34, 70), (72, 54, 100))
VIOLET = [(250, 220, 255), (214, 130, 255), (150, 60, 220), (80, 24, 130)]
ROUGE_OEIL = [(255, 120, 90), (255, 30, 20), (170, 10, 8), (90, 4, 4)]

# =========================================================================== CHAUDIÈRE INSTABLE
def chaudiere():
    t = Toile(64, 32, graine=71)
    TETE, CORPS, PATTE = faces(0, 0, 8, 8, 8), faces(16, 16, 8, 12, 4), faces(0, 16, 4, 6, 4)
    # tête : dôme de chaudière ; le visage du creeper devient la grille du foyer
    for n, f in TETE.items(): t.matiere(f, CUIVRE, 0.42, nom=n, taches=(VDG, 4, 0.45))
    f = TETE["front"]
    t.rect(f, 0, 0, 8, 8, FER, 0.3, relief=0.12)
    for (x, y) in ((1, 2), (2, 2), (1, 3), (2, 3), (5, 2), (6, 2), (5, 3), (6, 3)):         # « yeux » : évents
        t.pt(f, x, y, BRAISE[1] if y == 2 else BRAISE[2])
    for (x, y) in ((3, 4), (4, 4), (2, 5), (3, 5), (4, 5), (5, 5), (2, 6), (5, 6)):         # « bouche » : grille
        t.pt(f, x, y, BRAISE[0] if (x, y) in ((3, 5), (4, 5)) else BRAISE[2])
    t.rivets(f, [(0, 0), (7, 0), (0, 7), (7, 7)], LAITON)
    for n in ("right", "left", "back"):
        f = TETE[n]; t.couture(f, 3, CUIVRE); t.rivets(f, [(1, 1), (6, 1), (1, 6), (6, 6)], LAITON)
    f = TETE["back"]; t.jauge(f, 2, 4, LAITON, aiguille=ROUGE_ALERTE)
    f = TETE["up"]; t.rect(f, 2, 2, 4, 4, LAITON, 0.5); t.plein(f, 3, 3, 2, 2, ramp(FER, 0.2))   # soupape
    t.pt(f, 3, 3, (220, 220, 220))
    # corps : cylindre riveté, bande d'avertissement, fissures incandescentes, manomètre dans le rouge
    for n, f in CORPS.items(): t.matiere(f, CUIVRE, 0.45, nom=n, stries=4, taches=(VDG, 5, 0.45))
    for n in COTES:
        f = CORPS[n]
        for y in (0, 11): t.hligne(f, y, ramp(LAITON, 0.45))
        for i in range(f[2]):                                                              # bande jaune et noire
            for j in (5, 6): t.pt(f, i, j, ramp(JAUNE, 0.6) if (i + j) % 4 < 2 else NOIR)
        for x in range(0, f[2], 2): t.rivet(f, x, 1, LAITON); t.rivet(f, x, 10, LAITON)
    f = CORPS["front"]
    t.jauge(f, 1, 2, LAITON, aiguille=ROUGE_ALERTE); t.pt(f, 3, 2, ROUGE_ALERTE)
    for (x, y) in ((5, 2), (6, 3), (5, 4), (6, 8), (5, 9), (4, 8)): t.pt(f, x, y, BRAISE[1])   # fissures
    t.pt(f, 6, 2, BRAISE[0])
    f = CORPS["back"]; t.rect(f, 2, 1, 4, 3, FER, 0.4); t.grille(f, 2, 2, 4, 1, FER)
    for (x, y) in ((1, 8), (2, 9), (6, 8)): t.pt(f, x, y, BRAISE[2])
    # pattes : pieds de fonte, sabots de laiton
    for n, f in PATTE.items():
        t.matiere(f, FER, 0.4, nom=n)
        if n in COTES: t.rect(f, 0, 4, 4, 2, LAITON, 0.45, relief=0.12); t.rivet(f, 1, 1, LAITON)
    return t.im

# =========================================================================== RAMPEUSES
def rampeuse(pal, accent, graine, reparation=False):
    t = Toile(64, 32, graine=graine)
    TETE, COU, ABDO, PATTE = faces(32, 4, 8, 8, 8), faces(0, 0, 6, 6, 6), faces(0, 12, 10, 8, 12), faces(18, 0, 16, 2, 2)
    # tête : caisson à huit optiques (la lumière vient de la texture des yeux)
    for n, f in TETE.items(): t.matiere(f, pal, 0.4, nom=n)
    f = TETE["front"]
    t.rect(f, 0, 0, 8, 8, pal, 0.3, relief=0.16)
    for (x, y) in OPTIQUES: t.pt(f, x, y, ramp(LAITON, 0.45))
    t.grille(f, 2, 6, 4, 1, pal)
    t.rivets(f, [(0, 0), (7, 0)], LAITON)
    for n in ("right", "left"): f = TETE[n]; t.rect(f, 1, 2, 6, 4, accent, 0.5, relief=0.14); t.rivet(f, 2, 3, pal)
    f = TETE["up"]; t.couture(f, 4, pal); t.rect(f, 3, 1, 2, 2, LAITON, 0.6)
    # cou : rotule
    for n, f in COU.items(): t.matiere(f, FER, 0.45, nom=n)
    for n in COTES: t.hligne(COU[n], 2, ramp(LAITON, 0.55)); t.hligne(COU[n], 3, ramp(LAITON, 0.35))
    # abdomen : châssis à panneaux, échine de laiton, réservoir
    for n, f in ABDO.items(): t.matiere(f, pal, 0.42, nom=n)
    f = ABDO["up"]                        # dos (10 x 12)
    t.rect(f, 1, 1, 8, 10, pal, 0.5, relief=0.14); t.vcouture(f, 4, pal, 1, 10)
    t.rect(f, 3, 2, 4, 3, accent, 0.5, relief=0.14)
    if reparation:
        t.plein(f, 1, 7, 8, 1, ramp(JAUNE, 0.6)); t.plein(f, 1, 8, 8, 1, NOIR)
        for x in range(1, 9, 2): t.pt(f, x, 8, ramp(JAUNE, 0.6))
        t.jauge(f, 6, 5, LAITON)
    else:
        t.jauge(f, 6, 7, LAITON); t.grille(f, 2, 7, 3, 3, pal, pas=1)
    t.rivets(f, [(1, 1), (8, 1), (1, 10), (8, 10)], LAITON)
    for n in COTES:
        f = ABDO[n]; t.couture(f, 3, pal); t.rivets(f, [(1, 1), (f[2]-2, 1), (1, 6), (f[2]-2, 6)], LAITON)
    f = ABDO["back"]; t.rect(f, 3, 2, 4, 4, FER, 0.35); t.lueur(f, 4, 3, 2, 2, BRAISE if not reparation else TEAL)
    # pattes : tiges de piston, articulation, pointe
    for n, f in PATTE.items():
        t.matiere(f, FER, 0.5, nom=n, biseau=0.08)
        if n in ("front", "back", "up", "down"):
            w = f[2]
            for x in (5, 6): t.vligne(f, x, ramp(LAITON, 0.5 if x == 5 else 0.3))
            for x in range(8, w): t.vligne(f, x, ramp(NICKEL, 0.65 if n != "down" else 0.4))   # tige chromée
            t.vligne(f, w-1, ramp(FER, 0.15))
    if reparation:                                                       # chalumeau sur une patte
        f = PATTE["front"]; t.pt(f, 14, 0, TEAL[1]); t.pt(f, 15, 0, TEAL[0])
    # texture des yeux (émissive)
    yeux = Image.new("RGBA", (64, 32), (0, 0, 0, 0)); py = yeux.load()
    fx, fy = TETE["front"][0], TETE["front"][1]
    for k, (x, y) in enumerate(OPTIQUES):
        py[fx+x, fy+y] = ((ROUGE_OEIL if not reparation else [(220, 255, 250), (110, 240, 225), (40, 170, 170)])[0 if k < 2 else 1]) + (255,)
    return t.im, yeux

OPTIQUES = [(2, 3), (5, 3), (1, 2), (6, 2), (3, 2), (4, 2), (1, 4), (6, 4)]

# =========================================================================== ÉGARÉ DU VIDE
def egare():
    t = Toile(64, 32, graine=83)
    TETE, MACHOIRE, CORPS, MEMBRE = faces(0, 0, 8, 8, 8), faces(0, 16, 8, 8, 8), faces(32, 16, 8, 12, 4), faces(56, 0, 2, 30, 2)
    def fissures(f, n):
        for _ in range(max(1, f[2]*f[3] // 45)):
            x, y = t.rnd.randrange(f[2]), t.rnd.randrange(f[3])
            for k in range(t.rnd.randint(2, 4)):
                t.pt(f, x, y, VIOLET[2] if k else VIOLET[1]); x += t.rnd.choice((-1, 0, 1)); y += 1
    for pieces in (TETE, CORPS, MEMBRE):
        for n, f in pieces.items():
            t.matiere(f, OBSID, 0.45, nom=n, bruit=0.08, biseau=0.06); fissures(f, n)
    f = TETE["front"]                                   # masque : plaque lisse, fente des yeux
    t.rect(f, 1, 1, 6, 6, OBSID, 0.62, relief=0.1)
    t.hligne(f, 4, ramp(OBSID, 0.1), 0, 8)
    f = CORPS["front"]                                  # cœur de cristal
    t.rect(f, 2, 2, 4, 4, OBSID, 0.25, relief=0.08); t.plein(f, 3, 3, 2, 2, VIOLET[1]); t.pt(f, 3, 3, VIOLET[0])
    # mâchoire / coiffe (couche réduite) : transparente sauf le menton fendu
    for n, f in MACHOIRE.items():
        if n in COTES:
            for i in range(8):
                for j in range(5, 8): t.pt(f, i, j, ramp(OBSID, 0.3 + 0.05 * j))
    t.pt(MACHOIRE["front"], 3, 6, VIOLET[2]); t.pt(MACHOIRE["front"], 4, 6, VIOLET[2])
    yeux = Image.new("RGBA", (64, 32), (0, 0, 0, 0)); py = yeux.load()
    for x, c in ((8, 1), (9, 0), (10, 1), (13, 1), (14, 0), (15, 1)): py[x, 12] = VIOLET[c] + (255,)
    for x in (9, 14): py[x, 11] = VIOLET[2] + (255,)
    return t.im, yeux

# =========================================================================== PUCE DU VIDE
def puce():
    t = Toile(64, 32, graine=89)
    for k, ((u, v), (w, h, d)) in enumerate(zip(((0, 0), (0, 5), (0, 14), (0, 18)), ((4, 3, 2), (6, 4, 5), (3, 3, 1), (1, 2, 1)))):
        for n, f in faces(u, v, w, h, d).items():
            t.matiere(f, OBSID, 0.5, nom=n, bruit=0.06, biseau=0.15)
            if n in ("up", "right", "left"):
                t.hligne(f, 0, ramp(OBSID, 0.85))
                if f[2] > 2: t.pt(f, f[2] // 2, f[3] // 2, VIOLET[1])
    f = faces(0, 0, 4, 3, 2)["front"]; t.pt(f, 0, 1, VIOLET[0]); t.pt(f, 3, 1, VIOLET[0])
    return t.im

# =========================================================================== VER DE FORAGE
def ver():
    t = Toile(64, 32, graine=97)
    TAILLES = [(3, 2, 2), (4, 3, 2), (6, 4, 3), (3, 3, 3), (2, 2, 3), (2, 1, 2), (1, 1, 2)]
    UV = [(0, 0), (0, 4), (0, 9), (0, 16), (0, 22), (11, 0), (13, 4)]
    for k, ((u, v), (w, h, d)) in enumerate(zip(UV, TAILLES)):
        for n, f in faces(u, v, w, h, d).items():
            if k == 0:                                   # tête : foret hélicoïdal
                t.matiere(f, NICKEL, 0.6, nom=n, biseau=0.1)
                for i in range(f[2]):
                    for j in range(f[3]):
                        if (i + j) % 2 == 0: t.pt(f, i, j, ramp(NICKEL, 0.3))
            else:
                t.matiere(f, FER, 0.45, nom=n, biseau=0.14)
                if n in COTES or n == "up": t.hligne(f, 0, ramp(LAITON, 0.5))
    # écailles / plaques de blindage (couches externes)
    for (u, v), (w, h, d) in (((20, 0), (10, 8, 3)), ((20, 11), (6, 4, 3)), ((20, 18), (6, 5, 2))):
        for n, f in faces(u, v, w, h, d).items():
            t.matiere(f, FER, 0.55, nom=n, biseau=0.14)
            if n == "up":
                t.vcouture(f, f[2] // 2, FER)
                t.rivets(f, [(0, 0), (f[2]-1, 0)], LAITON)
            if n in COTES: t.hligne(f, f[3]-1, ramp(LAITON, 0.4))
    return t.im

def produits():
    sp, spy = rampeuse(FER, CUIVRE, 101)
    cs, csy = rampeuse(BLEU_ENTRETIEN, JAUNE, 103, reparation=True)
    en, eny = egare()
    return {"creeper/creeper.png": chaudiere(), "spider/spider.png": sp, "spider_eyes.png": spy, "spider/cave_spider.png": cs,
"enderman/enderman.png": en, "enderman/enderman_eyes.png": eny,
            "endermite.png": puce(), "silverfish.png": ver()}

if __name__ == "__main__":
    import os
    out = sys.argv[1]
    for chemin, im in produits().items():
        p = os.path.join(out, chemin); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
    print("ok")
