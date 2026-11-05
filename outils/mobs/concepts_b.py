"""Lot B, les machines."""
import random, math
from atelier import *
import lot3b, lot4

def F(b): return faces(*b)

# ---------------- ENDERMAN : la Sentinelle du vide (treillis télescopique d'acier bleui, lampe violette)
def sentinelle():
    t = Toile((64, 32)); v = vanilla("enderman/enderman.png").load()
    treillis = lambda i, j, w, h, f: ACIER_BLEU[4] if (i + j) % 4 == 0 or (i - j) % 4 == 0 else ramp(ACIER_BLEU, 0.28 + 0.1*(f == "up"))
    t.boite(0, 0, 8, 8, 8, metal(ACIER_BLEU, 0.4, 0.04, graine=21), force=True)
    t.boite(0, 16, 8, 8, 8, metal(ACIER_BLEU, 0.3, 0.04), force=True)
    t.boite(32, 16, 8, 12, 4, treillis, force=True)
    t.boite(56, 0, 2, 30, 2, lambda i, j, w, h, f: NICKEL[4] if j % 10 == 0 else ACIER_BLEU[4] if (j % 4 == 0) else ACIER_BLEU[1], force=True)   # segments télescopiques
    x, y, _, _ = F((0, 0, 8, 8, 8))["front"]
    t.rect(x, y+3, 8, 2, ACIER_BLEU[0], True)                                                     # fente de la lampe
    for xx in range(64):                                                                          # yeux violets d'origine
        for yy in range(32):
            c = v[xx, yy]
            if c[3] and c[2] > 150 and c[0] > 150 and c[1] < 120: t.pt(xx, yy, (224, 121, 255), True)
    x, y, _, _ = F((32, 16, 8, 12, 4))["front"]
    t.cadre(x+2, y+2, 4, 4, NICKEL[4], NICKEL[0], True); t.rect(x+3, y+3, 2, 2, (204, 110, 255), True)
    return t.im

# ---------------- SILVERFISH : le Ver de forage
def ver_de_forage():
    t = Toile((64, 32)); rnd = random.Random(22)
    segs = lot3b.SEG_SILVER
    for n, ((w, h, d), (u, v)) in enumerate(segs):
        f = t.boite(u, v, w, h, d, lambda i, j, fw, fh, k: ramp(FER, 0.45 + (0.25 if j == 0 else 0) + (0.12 if rnd.random() < 0.08 else 0)), force=True)
        if n == 0:                                                                                 # tête : foret chromé
            x, y, fw, fh = f["front"]
            for j in range(fh):
                for i in range(fw): t.pt(x+i, y+j, CHROME[5] if (i + j) % 2 else CHROME[2], True)
        for k in COTES:                                                                            # reflet d'huile
            x, y, fw, fh = f[k]
            if fw > 2: t.pt(x + fw//2, y + fh - 1, (120, 80, 140), True)
    for (u, v, w, h, d) in ((20, 0, 10, 8, 3), (20, 11, 6, 4, 3), (20, 18, 6, 5, 2)):
        t.boite(u, v, w, h, d, lambda i, j, fw, fh, k: ramp(NICKEL, 0.4 + 0.25*(i % 3 == 0)), force=True)
    return t.im

# ---------------- ENDERMITE : la Puce du vide (carapace de verre violet)
def puce():
    t = Toile((64, 32))
    for n, ((w, h, d), (u, v)) in enumerate(lot3b.SEG_ENDERMITE):
        t.boite(u, v, w, h, d, lambda i, j, fw, fh, k: (240, 200, 255) if (i == 1 and j == 0) else ramp(VIOLET_VERRE, 0.35 + 0.35*(1 - abs(i - fw/2)/max(1, fw/2))), force=True)
    x, y, fw, fh = faces(0, 0, 4, 3, 2)["front"]
    t.pt(x, y+1, (255, 230, 255), True); t.pt(x+fw-1, y+1, (255, 230, 255), True)
    return t.im

# ---------------- GARDIEN : le Torpilleur (acier naval gris, coque rouge) ; ANCIEN : le Cuirassé (bronze vert, tourelles)
def navire(ancien=False):
    v = vanilla("guardian_elder.png" if ancien else "guardian.png")
    t = Toile((64, 64), v); src = v.load()
    coque = BRONZE_VERT if ancien else GRIS_NAVAL
    CARENE = R((50, 14, 10), (80, 22, 16), (112, 32, 24), (140, 44, 32), (164, 62, 46), (186, 84, 66))
    for y in range(64):
        for x in range(64):
            if src[x, y][3]: t.pt(x, y, ramp(coque, 0.45 + (0.06 if (x//4 + y//4) % 2 else 0)))
    tete = F((0, 0, 12, 12, 16))
    for k in COTES:                                                                                # flottaison : carène rouge sous la ligne
        x, y, w, h = tete[k]
        for j in range(h):
            for i in range(w):
                if j >= 8: t.pt(x+i, y+j, ramp(CARENE, 0.5 - 0.06*(j-8)))
                if j == 7: t.pt(x+i, y+j, (236, 232, 222) if not ancien else OR[3])
                if i % 4 == 1 and j in (2, 5): t.rivet(x+i, y+j, NICKEL if not ancien else LAITON)
    x, y, w, h = tete["down"]; t.rect(x, y, w, h, CARENE[2])
    x, y, _, _ = tete["front"]
    t.disque(x+6, y+6, 4.6, lambda r, a: (LAITON[4] if a > 180 else LAITON[1]) if r > 3.3 else None)  # hublot de l'œil
    if not ancien:
        for (i, j) in ((1, 1), (2, 1), (9, 1), (10, 1)): t.pt(x+i, y+j, (236, 232, 222))            # numéro de coque
        t.ligne_h(x+1, y+2, 2, (236, 232, 222)); t.ligne_h(x+9, y+2, 2, (236, 232, 222))
    x, y, w, d = tete["up"]
    if ancien:                                                                                      # tourelles
        for (cx, cy) in ((3, 4), (8, 4), (5.5, 11)):
            t.disque(x+cx, y+cy, 2.2, lambda r, a: BRONZE_VERT[1] if r > 1.4 else BRONZE_VERT[4])
            t.ligne_h(x+int(cx), y+int(cy)-3, 1, FER[1])
    else:
        t.disque(x+6, y+8, 2.4, lambda r, a: (200, 40, 28) if r > 1.4 else NICKEL[3])                # trappe à volant
    nag = faces(25, 19, 1, 9, 9)                                                                    # hélice
    for k in ("right", "left"):
        x, y, w, h = nag[k]
        for j in range(h):
            for i in range(w):
                pale = abs(i - 4) <= 1 or abs(j - 4) <= 1
                t.pt(x+i, y+j, (LAITON[4] if (i+j) % 3 else LAITON[2]) if pale else FER[1])
    for y in range(64):                                                                             # épines : acier sombre
        for x in range(64):
            c = src[x, y]
            if c[3] and 15 <= (math.degrees(math.atan2(0, 1))) and c[0] > 150 and c[1] < 140 and c[2] < 90:
                t.pt(x, y, ramp(FER, 0.5))
    return t.im

# ---------------- BLAZE : la Lanterne de forge (verre fumé, fer forgé, flamme intérieure)
def lanterne():
    t = Toile((64, 32))
    tete = t.boite(0, 0, 8, 8, 8, lambda i, j, w, h, f: FER[0] if i in (0, w-1) or j in (0, h-1) else
                   (BRAISE[0] if (abs(i - 3.5) < 1 and 3 <= j <= 5) else BRAISE[1] if (abs(i - 3.5) < 2 and 2 <= j <= 6) else ramp(FUME, 0.35 + 0.1*(j/h))), force=True)
    x, y, w, h = tete["up"]; t.rect(x, y, w, h, FER[1], True); t.cadre(x, y, w, h, FER[3], FER[0], True)
    t.disque(x+4, y+4, 1.6, lambda r, a: FER[3], True)                                              # anneau de suspension
    x, y, _, _ = tete["front"]
    for (i, c) in ((2, (255, 240, 200)), (5, (255, 240, 200))): t.pt(x+i, y+2, c, True)            # deux yeux plus vifs dans la flamme
    t.boite(0, 16, 2, 8, 2, lambda i, j, w, h, f: FER[3] if (i + j) % 2 else FER[1], force=True)      # barres torsadées
    x, y, w, d = faces(0, 16, 2, 8, 2)["down"]; t.rect(x, y, w, d, BRAISE[2], True)
    return t.im

# ---------------- BREEZE : le Régulateur (nickel poli) et son souffle de vapeur
def regulateur():
    v = vanilla("breeze/breeze.png"); src = v.load(); t = Toile(v.size, v)
    for y in range(v.height):
        for x in range(v.width):
            c = src[x, y]
            if not c[3]: continue
            l = (c[0]+c[1]+c[2]) / 765
            col = ramp(NICKEL, 0.2 + l*0.85)
            if y % 4 == 0 and l > 0.3: col = LAITON[3]
            t.pt(x, y, col)
    return t.im

def vapeur():
    v = vanilla("breeze/breeze_wind.png"); src = v.load(); t = Toile(v.size, v)
    for y in range(v.height):
        for x in range(v.width):
            c = src[x, y]
            if c[3]: t.pt(x, y, ramp(R((170, 170, 176), (210, 210, 216), (240, 240, 244)), (c[0]+c[1]+c[2])/765))
    return t.im

# ---------------- SHULKER : le Coffre-fort (émail vert bouteille, filets dorés, cadran de combinaison)
def coffre_fort():
    t = Toile((64, 64))
    email = lambda i, j, w, h, f: OR[3] if (i == 1 or i == w-2 or j == 1 or j == h-2) and 0 < i < w-1 and 0 < j < h-1 else ramp(VERT_BOUTEILLE, 0.45 + 0.08*(j == 0) - 0.1*(j == h-1))
    couv = t.boite(0, 0, 16, 12, 16, email, force=True)
    socle = t.boite(0, 28, 16, 8, 16, email, force=True)
    x, y, _, _ = couv["front"]
    t.disque(x+8, y+6, 4.4, lambda r, a: OR[4] if r > 3.4 else (OR[1] if int(a) % 30 < 6 else FER[1]) if r > 2.2 else OR[3] if r > 1 else FER[0], True)
    t.pt(x+8, y+2, (200, 30, 20), True)                                                             # repère du cadran
    for k in ("right", "left", "back"):
        x, y, w, h = couv[k]; t.ligne_h(x+3, y+6, w-6, OR[2], True)
    x, y, w, d = couv["up"]
    for (i, j) in ((3, 3), (12, 3), (3, 12), (12, 12)): t.disque(x+i, y+j, 1.2, lambda r, a: OR[4], True)
    tete = t.boite(0, 52, 6, 6, 6, metal(FER, 0.35, 0.04), force=True)
    x, y, _, _ = tete["front"]
    t.cadre(x+1, y+1, 4, 4, OR[4], OR[1], True); t.rect(x+2, y+2, 2, 2, (120, 255, 160), True)       # œil émeraude
    return t.im

LOT_B = {
    "enderman/enderman.png": sentinelle,
    "silverfish.png": ver_de_forage,
    "endermite.png": puce,
    "guardian.png": lambda: navire(False),
    "guardian_elder.png": lambda: navire(True),
    "blaze.png": lanterne,
    "breeze/breeze.png": regulateur,
    "breeze/breeze_wind.png": vapeur,
    "shulker/shulker.png": coffre_fort,
    "slime/slime.png": lambda: lot3b.gelee_v3(vanilla("slime/slime.png")),
    "slime/magmacube.png": lambda: lot3b.creuset_v3(vanilla("slime/magmacube.png")),
    "phantom.png": lambda: lot3b.ame_v3(vanilla("phantom.png")),
    "phantom_eyes.png": lambda: lot3b.yeux_echo(vanilla("phantom_eyes.png")),
    "ghast/ghast.png": lambda: lot4.ballon(vanilla("ghast/ghast.png")),
    "ghast/ghast_shooting.png": lambda: lot4.ballon(vanilla("ghast/ghast_shooting.png"), True),
}
