"""Propositions de dessus (16x16, seule la zone 2..14 est visible) + textures de la table de l'Empire."""
import random
from PIL import Image

OUT = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/hauts/"
VAN = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/"

def neuf(c):
    im = Image.new("RGBA", (16, 16), c + (255,)); return im, im.load()

def bruit(px, base, var, rng, zone=(0, 0, 16, 16)):
    for x in range(zone[0], zone[2]):
        for y in range(zone[1], zone[3]):
            k = rng.choice(var); c = base
            px[x, y] = tuple(max(0, min(255, c[i] + k)) for i in range(3)) + (255,)

LAITON = [(244, 214, 128), (222, 180, 86), (184, 138, 58), (128, 90, 36)]  # clair → sombre

def rivet(px, x, y):
    px[x, y] = LAITON[0] + (255,); px[x + 1, y] = LAITON[1] + (255,)
    px[x, y + 1] = LAITON[1] + (255,); px[x + 1, y + 1] = LAITON[3] + (255,)

# ---------- A : plateau de noyer, équerres de laiton ----------
def bois():
    rng = random.Random(3); im, px = neuf((120, 82, 50))
    planches = [(2, 6), (6, 10), (10, 14)]
    teintes = [(124, 85, 52), (114, 77, 46), (128, 89, 55)]
    for (y0, y1), t in zip(planches, teintes):
        for x in range(16):
            for y in range(y0, y1):
                c = t
                # veines horizontales
                if (x * 3 + y * 7 + y0) % 11 == 0: c = tuple(v - 18 for v in c)
                elif (x + y * 5) % 9 == 0: c = tuple(v + 10 for v in c)
                px[x, y] = c + (255,)
        for x in range(16):
            px[x, y0] = tuple(v + 14 for v in t) + (255,)      # arête éclairée
            px[x, y1 - 1] = tuple(v - 22 for v in t) + (255,)  # joint sombre
        # bout de planche décalé
        cx = 5 if y0 == 6 else 10
        for y in range(y0, y1): px[cx, y] = (70, 46, 28, 255)
    for y in (0, 1, 14, 15):
        for x in range(16): px[x, y] = (90, 60, 36, 255)
    # équerres de laiton aux 4 coins de la zone visible
    for (x, y, sx, sy) in ((2, 2, 1, 1), (13, 2, -1, 1), (2, 13, 1, -1), (13, 13, -1, -1)):
        for i in range(3):
            px[x + sx * i, y] = LAITON[1] + (255,); px[x, y + sy * i] = LAITON[1] + (255,)
        px[x, y] = LAITON[0] + (255,); px[x + sx, y + sy] = LAITON[3] + (255,)
    return im

# ---------- B : tôle striée de laiton ----------
def tole():
    im, px = neuf(LAITON[2])
    for x in range(16):
        for y in range(16):
            px[x, y] = ((176, 130, 54) if (x + y) % 2 else (170, 125, 51)) + (255,)
    # stries en chevrons alternés (motif de tôle larmée)
    for bx in range(2, 14, 4):
        for by in range(2, 14, 4):
            if ((bx + by) // 4) % 2 == 0:   # strie « / »
                pts = [(bx + 1, by + 2), (bx + 2, by + 1)]
            else:                          # strie « \ »
                pts = [(bx + 1, by + 1), (bx + 2, by + 2)]
            for (x, y) in pts:
                px[x, y] = LAITON[0] + (255,)
                if y + 1 < 16: px[x, y + 1] = LAITON[3] + (255,)
    # cadre et rivets
    for i in range(2, 14):
        px[i, 2] = LAITON[1] + (255,); px[2, i] = LAITON[1] + (255,)
        px[i, 13] = LAITON[3] + (255,); px[13, i] = LAITON[3] + (255,)
    for (x, y) in ((2, 2), (12, 2), (2, 12), (12, 12)): rivet(px, x, y)
    return im

# ---------- C : dalle de pierre polie gravée d'un cercle ----------
def pierre():
    rng = random.Random(7); im, px = neuf((140, 138, 132))
    bruit(px, (142, 140, 134), [-6, -3, 0, 0, 3, 5], rng)
    import math
    for x in range(16):
        for y in range(16):
            r = math.hypot(x - 7.5, y - 7.5)
            if 3.6 < r < 4.6: px[x, y] = (96, 94, 90, 255)            # sillon
            elif 4.6 <= r < 5.3 and y > 7.5: px[x, y] = (170, 168, 160, 255)  # lèvre éclairée
    for i in range(2, 14):                                           # biseau
        px[i, 2] = (172, 170, 162, 255); px[2, i] = (164, 162, 154, 255)
        px[i, 13] = (102, 100, 96, 255); px[13, i] = (110, 108, 102, 255)
    for (x, y) in ((7, 7), (8, 7), (7, 8), (8, 8)): px[x, y] = (110, 108, 104, 255)  # moyeu
    return im

# ---------- D : plaques de cuivre rivetées, patine vert-de-gris ----------
def cuivre():
    rng = random.Random(11); im, px = neuf((184, 100, 62))
    bruit(px, (186, 102, 64), [-8, -4, 0, 0, 4, 8], rng)
    for x in range(16):                     # jointure centrale entre deux plaques
        px[x, 7] = (120, 60, 36, 255); px[x, 8] = (214, 132, 88, 255)
    for i in range(2, 14):
        px[i, 2] = (222, 140, 96, 255); px[2, i] = (214, 132, 88, 255)
        px[i, 13] = (120, 60, 36, 255); px[13, i] = (130, 66, 40, 255)
    for x in (3, 6, 9, 12):
        for y in (3, 10):
            px[x, y] = (236, 170, 120, 255); px[x, y + 1] = (120, 60, 36, 255)
    for (x, y) in ((4, 5), (5, 5), (11, 11), (10, 12), (12, 5), (5, 12), (6, 11)):
        px[x, y] = (88, 150, 120, 255)
    for (x, y) in ((5, 6), (11, 12)): px[x, y] = (64, 120, 96, 255)
    return im

# ---------- E : ardoise sombre incrustée d'un cercle d'améthyste ----------
def ardoise():
    rng = random.Random(5); im, px = neuf((52, 50, 60))
    bruit(px, (54, 52, 62), [-5, -2, 0, 0, 3, 6], rng)
    import math
    for x in range(16):
        for y in range(16):
            r = math.hypot(x - 7.5, y - 7.5)
            if 4.0 < r < 5.0: px[x, y] = (150, 104, 204, 255) if (x + y) % 3 else (196, 150, 240, 255)
    # 4 runes d'améthyste aux points cardinaux
    for (x, y) in ((7, 3), (8, 3), (7, 12), (8, 12), (3, 7), (3, 8), (12, 7), (12, 8)):
        px[x, y] = (110, 72, 160, 255)
    for i in range(2, 14):
        px[i, 2] = LAITON[1] + (255,); px[2, i] = LAITON[1] + (255,)
        px[i, 13] = LAITON[3] + (255,); px[13, i] = LAITON[3] + (255,)
    for (x, y) in ((2, 2), (12, 2), (2, 12), (12, 12)): rivet(px, x, y)
    return im

PROPS = {"A_noyer": bois, "B_tole_laiton": tole, "C_pierre_gravee": pierre, "D_cuivre_patine": cuivre, "E_ardoise_amethyste": ardoise}

# ---------- Table de l'Empire : vanilla recoloré ----------
# rouge du tapis → cuir vert de bureau ; diamants → laiton ; obsidienne gardée, un peu bleuie
REMAP = {
    (162, 41, 41): (52, 110, 74), (127, 7, 40): (36, 84, 56), (116, 29, 50): (40, 90, 60),
    (107, 0, 47): (28, 66, 46), (88, 22, 44): (24, 58, 42),
    (195, 251, 241): LAITON[0], (162, 246, 231): LAITON[1], (74, 237, 209): LAITON[2],
    (44, 205, 177): LAITON[3], (255, 255, 255): (255, 240, 190),
}
def recolore(nom):
    im = Image.open(VAN + nom).convert("RGBA"); px = im.load()
    for x in range(im.width):
        for y in range(im.height):
            r, g, b, a = px[x, y]
            if (r, g, b) in REMAP: px[x, y] = REMAP[(r, g, b)] + (a,)
    return im

def table_dessus():
    im = recolore("block/enchanting_table_top.png"); px = im.load()
    # emblème : petit rouage de laiton au centre du tapis
    g = ["..#..", ".###.", "##.##", ".###.", "..#.."]
    for j, l in enumerate(g):
        for i, ch in enumerate(l):
            if ch == "#": px[6 + i, 6 + j] = (LAITON[1] if (i + j) % 2 else LAITON[2]) + (255,)
    for (x, y) in ((8, 6), (6, 8), (10, 8), (8, 10)): px[x, y] = LAITON[0] + (255,)
    return im

def livre():
    """Livre flottant : couverture de cuir vert, coins et fermoir de laiton."""
    im = Image.open(VAN + "entity/enchanting_table_book.png").convert("RGBA"); px = im.load()
    rm = {(119, 78, 34): (30, 72, 50), (135, 86, 34): (36, 82, 56), (167, 110, 45): (46, 104, 70),
          (197, 132, 57): (62, 128, 86), (255, 216, 0): LAITON[0], (255, 177, 0): LAITON[2]}
    for x in range(im.width):
        for y in range(im.height):
            r, g, b, a = px[x, y]
            if (r, g, b) in rm: px[x, y] = rm[(r, g, b)] + (a,)
    return im

if __name__ == "__main__":
    for k, f in PROPS.items(): f().save(OUT + f"plan_{k}.png")
    table_dessus().save(OUT + "table_dessus.png")
    recolore("block/enchanting_table_side.png").save(OUT + "table_cote.png")
    recolore("block/enchanting_table_bottom.png").save(OUT + "table_dessous.png")
    livre().save(OUT + "table_livre.png")
    print("ok")
