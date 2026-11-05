"""Lot 7 : choix finaux — wither « feu des âmes », squelette de fonte acier noirci (tête fidèle à celle d'origine),
shulker « Néant » retravaillé (magie plutôt que mécanique)."""
import math, random, sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import *
import lot6
from lot6 import AME, AMETHYSTE, OBSIDIENNE

def wither_squelette():
    im = lot6.variantes()["wsq_B"]; px = im.load()
    # tête : comme celle d'origine — orbites en trait, nez, rangée de dents ; acier noirci, feu des âmes dans les orbites
    D, M, L, H = (14, 16, 22), (28, 32, 42), (46, 52, 66), (70, 78, 96)
    CREUX = (8, 8, 12)
    VISAGE = ["HHLLLLHH",
              "LMMMMMML",
              "MMMMMMMM",
              "MooMMooM",
              "MkkMMkkM",
              "MMMkkMMM",
              "DkDkDkkD",
              "DDMMMMDD"]
    pal = {"H": H, "L": L, "M": M, "D": D, "k": CREUX, "o": AME[1]}
    for j, l in enumerate(VISAGE):
        for i, c in enumerate(l): px[8 + i, 8 + j] = pal[c] + (255,)
    px[9, 11] = AME[0] + (255,); px[14, 11] = AME[0] + (255,)
    return im

def shulker():
    """Coquille du Néant : obsidienne polie gravée de runes d'améthyste, couvercle à sceau, intérieur ouvert sur le vide étoilé,
    un œil du Néant pour tête. Le bas des flancs du couvercle reste transparent (chevauchement avec le socle)."""
    t = Toile(64, 64, graine=501); rnd = random.Random(7)
    COUV, SOCLE, TETE = faces(0, 0, 16, 12, 16), faces(0, 28, 16, 8, 16), faces(0, 52, 6, 6, 6)
    RUNES = [["#.#", ".#.", "#.#"], ["##.", "#.#", ".##"], [".#.", "###", ".#."], ["#..", "###", "..#"], ["###", "#..", "##."], [".##", "#.#", "##."]]
    for n, f in COUV.items(): t.matiere(f, OBSIDIENNE, 0.42, nom=n, bruit=0.06, biseau=0.12)
    f = COUV["up"]                                                       # sceau : cercle et étoile à huit branches
    for y in range(16):
        for x in range(16):
            dx, dy = x + .5 - 8, y + .5 - 8; d = math.hypot(dx, dy); a = math.atan2(dy, dx)
            if abs(d - 6.2) < 0.55: t.pt(f, x, y, AMETHYSTE[2])
            elif d < 5.6 and abs(math.sin(4 * a)) < 0.16 and d > 1.2: t.pt(f, x, y, AMETHYSTE[1] if d < 3.5 else AMETHYSTE[2])
            elif d < 1.3: t.pt(f, x, y, AMETHYSTE[0])
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)): t.pt(f, x, y, AMETHYSTE[1])
    t.matiere(COUV["down"], OBSIDIENNE, 0.12, nom="down")
    for k, n in enumerate(COTES):
        f = COUV[n]
        for x in range(16):
            for y in range(8, 12): t.vide(f, x, y)
            if x % 5 in (1, 2, 3): t.pt(f, x, 8, ramp(OBSIDIENNE, 0.28)); t.pt(f, x, 9, ramp(OBSIDIENNE, 0.2))   # bord festonné
        t.hligne(f, 0, ramp(OBSIDIENNE, 0.75)); t.hligne(f, 7, ramp(OBSIDIENNE, 0.2))
        for r, x0 in enumerate((2, 7, 12)):                              # trois runes gravées par flanc
            g = RUNES[(k * 3 + r) % len(RUNES)]
            for j in range(3):
                for i in range(3):
                    if g[j][i] == "#": t.pt(f, x0 + i, 2 + j, AMETHYSTE[1] if j == 1 else AMETHYSTE[2])
    for n, f in SOCLE.items(): t.matiere(f, OBSIDIENNE, 0.34, nom=n, bruit=0.06)
    for n in COTES:
        f = SOCLE[n]
        t.hligne(f, 0, ramp(OBSIDIENNE, 0.6)); t.hligne(f, 2, AMETHYSTE[2])          # filet d'améthyste sous le couvercle
        for x in range(1, 16, 4): t.pt(f, x, 5, AMETHYSTE[1]); t.pt(f, x + 1, 5, AMETHYSTE[3])   # éclats de cristal
        t.hligne(f, 7, ramp(OBSIDIENNE, 0.1))
    f = SOCLE["up"]                                                      # intérieur : le vide étoilé
    for y in range(16):
        for x in range(16):
            t.pt(f, x, y, (6 + rnd.randint(0, 6), 4, 14 + rnd.randint(0, 10)))
    for _ in range(14):
        x, y = rnd.randrange(16), rnd.randrange(16); t.pt(f, x, y, rnd.choice([AMETHYSTE[0], AMETHYSTE[1], (200, 240, 255)]))
    for n, f in TETE.items():                                           # l'œil du Néant
        for y in range(6):
            for x in range(6): t.pt(f, x, y, AMETHYSTE[3] if (x + y) % 3 else (60, 20, 100))
    f = TETE["front"]
    for y in range(6):
        for x in range(6):
            d = math.hypot(x + .5 - 3, y + .5 - 3)
            if d < 2.6: t.pt(f, x, y, AMETHYSTE[1] if d > 1.4 else (250, 245, 255))
    t.pt(f, 2, 2, (40, 10, 70)); t.pt(f, 3, 3, (40, 10, 70)); t.pt(f, 2, 3, (40, 10, 70)); t.pt(f, 3, 2, (40, 10, 70))
    return t.im

if __name__ == "__main__":
    import os
    o = sys.argv[1]; os.makedirs(o, exist_ok=True)
    v = lot6.variantes()
    v["wither_C"].save(os.path.join(o, "wither.png")); v["wither_C_inv"].save(os.path.join(o, "wither_invulnerable.png"))
    wither_squelette().save(os.path.join(o, "wither_skeleton.png")); shulker().save(os.path.join(o, "shulker.png"))
    print("ok")

def visages_wither(im, met, feu):
    """Têtes du wither façon crâne d'origine : orbites en trait, nez, rangée de dents."""
    px = im.load()
    D, M, L, H = ramp(met, 0.25), ramp(met, 0.45), ramp(met, 0.62), ramp(met, 0.8)
    pal = {"H": H, "L": L, "M": M, "D": D, "k": (6, 6, 9), "o": feu[1], "O": feu[0]}
    GRAND = ["HHLLLLHH", "LMMMMMML", "MMMMMMMM", "MOoMMoOM", "MkkMMkkM", "MMMkkMMM", "DkDkDkkD", "DDMMMMDD"]
    PETIT = ["HLLLLH", "MMMMMM", "MOMMOM", "MkMMkM", "MMkkMM", "kDkDkD"]
    for (x0, y0, g) in ((8, 8, GRAND), (38, 6, PETIT)):
        for j, l in enumerate(g):
            for i, c in enumerate(l): px[x0 + i, y0 + j] = pal[c] + (255,)
    return im
