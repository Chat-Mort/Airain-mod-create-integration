"""Lot 6 : variantes à choisir pour le shulker, le wither et le squelette de fonte."""
import math, sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import *
import lot5
from lot5 import LAVE, ELECTRIQUE, FONTE, ACIER_BLEU, JAUNE
OBSIDIENNE = R((10, 6, 16), (20, 12, 30), (34, 22, 50), (52, 34, 74), (74, 52, 100), (104, 80, 134))
AMETHYSTE = [(250, 220, 255), (214, 140, 255), (150, 70, 220), (80, 30, 130)]
OS = R((96, 88, 70), (130, 120, 98), (164, 154, 128), (196, 186, 158), (220, 212, 186), (240, 234, 212))
AME = [(220, 250, 255), (120, 220, 255), (40, 140, 210), (16, 60, 110)]
BRONZE_C = R((26, 16, 10), (44, 28, 16), (66, 44, 26), (92, 64, 38), (120, 88, 54), (150, 116, 74))

def shulker(met, joint, oeil, accent, graine):
    t = Toile(64, 64, graine=graine)
    COUV, SOCLE, TETE = faces(0, 0, 16, 12, 16), faces(0, 28, 16, 8, 16), faces(0, 52, 6, 6, 6)
    for n, f in COUV.items(): t.matiere(f, met, 0.48, nom=n, bruit=0.035, biseau=0.1)
    f = COUV["up"]
    for (x, y, w, h) in ((1, 1, 6, 6), (9, 1, 6, 6), (1, 9, 6, 6), (9, 9, 6, 6)): t.rect(f, x, y, w, h, met, 0.52, relief=0.14)
    for k in range(16): t.pt(f, 7, k, joint[1] if k % 3 else joint[0]); t.pt(f, 8, k, joint[2]); t.pt(f, k, 7, joint[1] if k % 3 else joint[0]); t.pt(f, k, 8, joint[2])
    t.matiere(COUV["down"], met, 0.15, nom="down")
    for n in COTES:
        f = COUV[n]
        for x in range(16):
            for y in range(8, 12): t.vide(f, x, y)
            if x % 4 in (1, 2): t.pt(f, x, 8, ramp(met, 0.3)); t.pt(f, x, 9, ramp(met, 0.22))
        t.hligne(f, 0, ramp(met, 0.8)); t.hligne(f, 7, ramp(accent, 0.45))
        for x in (3, 4, 11, 12): t.vligne(f, x, joint[2] if x in (3, 12) else joint[1], 2, 4)    # coutures lumineuses
        t.rivets(f, [(1, 2), (14, 2), (1, 5), (14, 5)], accent)
    for n, f in SOCLE.items(): t.matiere(f, met, 0.36, nom=n, bruit=0.04)
    for n in COTES:
        f = SOCLE[n]; t.rect(f, 0, 0, 16, 4, accent, 0.48, relief=0.14)
        for x in (2, 6, 9, 13): t.rivet(f, x, 1, accent)
        t.hligne(f, 6, joint[2]); t.hligne(f, 7, ramp(met, 0.15))
    f = SOCLE["up"]; t.matiere(f, met, 0.15, nom="up")
    for y in range(16):
        for x in range(16):
            if abs(math.hypot(x + .5 - 8, y + .5 - 8) - 4) < 0.7: t.pt(f, x, y, joint[1])
    for n, f in TETE.items(): t.matiere(f, met, 0.4, nom=n)
    f = TETE["front"]; t.rect(f, 1, 1, 4, 4, accent, 0.45, relief=0.16)
    t.pt(f, 2, 2, oeil[0]); t.pt(f, 3, 2, oeil[1]); t.pt(f, 2, 3, oeil[1]); t.pt(f, 3, 3, oeil[2])
    return t.im

def wither(met, feu, accent, graine, laiton=True):
    t = Toile(64, 64, graine=graine)
    TETE_C, TETE_S = faces(0, 0, 8, 8, 8), faces(32, 0, 6, 6, 6)
    EPAULES, ECHINE, QUEUE, COTES_ = faces(0, 16, 20, 3, 3), faces(0, 22, 3, 10, 3), faces(12, 22, 3, 6, 3), faces(24, 22, 11, 2, 2)
    def crane(F, w):
        for n, f in F.items(): t.matiere(f, met, 0.5, nom=n, bruit=0.05)
        f = F["front"]
        for x0 in (1, w - 3):
            t.plein(f, x0, 2, 2, 2, ramp(met, 0.05)); t.pt(f, x0 + (1 if x0 == 1 else 0), 2 if w == 8 else 2, feu[0]); t.pt(f, x0 + (0 if x0 == 1 else 1), 3, feu[1])
        t.pt(f, w // 2 - 1, w - 3, ramp(met, 0.08)); t.pt(f, w // 2, w - 3, ramp(met, 0.08))
        for x in range(1, w - 1): t.pt(f, x, w - 1, ramp(met, 0.12) if x % 2 else ramp(met, 0.75))
        if laiton: t.hligne(f, 0, ramp(accent, 0.5))
        for n in ("right", "left", "up"):
            ff = F[n]; t.usure(ff, met, 4, 0.2)
            if laiton: t.rivet(ff, 1, 1, accent); t.rivet(ff, w - 2, 1, accent)
    crane(TETE_C, 8); crane(TETE_S, 6)
    for n, f in EPAULES.items():
        t.matiere(f, met, 0.46, nom=n, biseau=0.12)
        if laiton and n in COTES and f[2] > 3:
            for x in (0, f[2] - 1): t.vligne(f, x, ramp(accent, 0.5))
    for n, f in ECHINE.items():
        for y in range(f[3]):
            for x in range(f[2]): t.pt(f, x, y, ramp(met, 0.55 if y % 3 else 0.3))
    for n, f in QUEUE.items(): t.matiere(f, met, 0.4, nom=n)
    for n, f in COTES_.items(): t.matiere(f, met, 0.5, nom=n, biseau=0.15)
    return t.im

def squelette(metal, laiton, yeux, cavite, rouage, graine, retouche=None):
    import squelettes as S
    return S.peindre(S.pal(metal, laiton=laiton, yeux=yeux, creux=(10, 9, 10), cavite=cavite, rouage=rouage), graine=graine, retouche=retouche)

def variantes():
    v = {}
    v["shulker_B"] = shulker(OBSIDIENNE, AMETHYSTE, AMETHYSTE, LAITON, 401)
    v["shulker_C"] = shulker(CUIVRE, [(200, 255, 220), (120, 220, 170), (60, 150, 110)], [(200, 255, 200), (90, 220, 120), (40, 140, 70)], LAITON, 403)
    v["wither_A"] = wither(FONTE, LAVE, LAITON, 411, laiton=False)
    v["wither_B"] = wither(OS, LAVE, LAITON, 413)
    v["wither_C"] = wither(R((8, 8, 10), (16, 16, 20), (28, 28, 34), (44, 44, 52), (64, 64, 74), (90, 90, 100)), AME, NICKEL, 415)
    v["wither_C_inv"] = wither(R((40, 60, 90), (60, 86, 120), (86, 116, 150), (116, 146, 180), (150, 178, 206), (190, 214, 236)), AME, NICKEL, 416)
    noir = ((18, 16, 16), (32, 29, 28), (50, 46, 44), (74, 68, 64))
    v["wsq_A"] = squelette(noir, {"b": (40, 36, 34), "B": (60, 54, 50), "Y": (84, 76, 70)}, ((255, 230, 120), (255, 170, 50)), (10, 9, 10), ((40, 36, 34), (60, 54, 50)), 421)
    v["wsq_B"] = squelette(((14, 16, 22), (28, 32, 42), (46, 52, 66), (70, 78, 96)), {"b": (60, 70, 86), "B": (96, 110, 130), "Y": (150, 168, 190)},
                           (AME[1], AME[2]), (16, 40, 70), (AME[3], AME[2]), 423)
    v["wsq_C"] = squelette(((24, 16, 10), (42, 28, 16), (64, 44, 26), (92, 66, 40)), {"b": (110, 64, 26), "B": (160, 100, 44), "Y": (210, 150, 70)},
                           ((255, 210, 90), (255, 130, 30)), (10, 8, 6), ((70, 40, 16), (110, 66, 26)), 425)
    return v

if __name__ == "__main__":
    import os
    o = sys.argv[1]; os.makedirs(o, exist_ok=True)
    for k, im in variantes().items(): im.save(os.path.join(o, k + ".png"))
    print("ok")
