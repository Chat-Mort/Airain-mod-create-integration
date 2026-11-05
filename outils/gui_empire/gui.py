"""Interfaces de l'Empire pour le mod : fond de l'écran des bannières, fond de la table de l'Empire, et planche de sprites
(flèches, touches de machine à écrire, onglets). Même métal que le pack d'interface (accueil/interface.py)."""
import math, os, random, sys
from PIL import Image, ImageDraw
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/accueil")
from interface import metal
from ornements import cadre_fenetre, CU, LA, NOIR
RES = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/gui/"
os.makedirs(RES, exist_ok=True)

# ---------------------------------------------------------------- panneau en gris (comme le jeu), puis passé au métal
def panneau(w, h, W=256, H=256):
    im = Image.new("L", (W, H), 0); a = Image.new("L", (W, H), 0); px = im.load(); pa = a.load()
    for y in range(h):
        for x in range(w):
            coin = (x in (0, w - 1) and y in (0, 1, h - 2, h - 1)) or (y in (0, h - 1) and x in (0, 1, w - 2, w - 1))
            if coin: continue
            pa[x, y] = 255
            if x == 0 or y == 0 or x == w - 1 or y == h - 1: px[x, y] = 0
            elif x <= 2 and y <= h - 3 or y <= 2 and x <= w - 3: px[x, y] = 255
            elif x >= w - 3 or y >= h - 3: px[x, y] = 85
            else: px[x, y] = 198
    return im, a

def creux(px, x, y, w, h, fond=139):
    """Creux comme une case : ombre en haut à gauche, reflet en bas à droite."""
    for j in range(h):
        for i in range(w):
            v = fond
            if i == 0 or j == 0: v = 55
            if i == w - 1 or j == h - 1: v = 255
            if (i == 0 and j == h - 1) or (j == 0 and i == w - 1): v = 139
            px[x + i, y + j] = v

def metalliser(gris, alpha, graine=3):
    """Gris → métal de l'Empire, stries de métal brossé, cadre en tuyau de cuivre et roues aux coins."""
    R = random.Random(graine); STRIES = [R.choice((-7, -4, -2, 0, 0, 2, 4, 6)) for _ in range(7)]
    out = Image.new("RGBA", gris.size); po = out.load(); pg = gris.load(); pa = alpha.load()
    for y in range(gris.height):
        for x in range(gris.width):
            if not pa[x, y]: continue
            l = pg[x, y]; c = metal(l)
            if 150 < l < 215:
                k = STRIES[y % 7] + R.randint(-2, 2); c = tuple(max(0, min(255, v + k)) for v in c)
            po[x, y] = c + (255,)
    cadre_fenetre(out)
    return out

def rivet(im, x, y):
    px = im.load()
    px[x, y] = LA[0] + (255,); px[x + 1, y] = LA[1] + (255,); px[x, y + 1] = LA[2] + (255,); px[x + 1, y + 1] = LA[3] + (255,)

def roue(im, cx, cy, r, couleurs=LA, dents=8, trou=1.6):
    px = im.load(); occ = set()
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            dx, dy = x + .5 - cx, y + .5 - cy; d = math.hypot(dx, dy); a = math.atan2(dy, dx)
            if d < r - 1.8 or (d < r and math.cos(dents * a) > 0.1):
                if d < trou: px[x, y] = NOIR + (255,); occ.add((x, y)); continue
                c = couleurs[1] if d < r * 0.45 else couleurs[2] if dy < 0 else couleurs[3]
                px[x, y] = c + (255,); occ.add((x, y))
    for (x, y) in list(occ):
        for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + i, y + j) not in occ and px[x + i, y + j][3]: px[x + i, y + j] = NOIR + (255,)

def tuyau(im, x0, y0, x1, y1):
    """Conduite de cuivre de 3 px (horizontale ou verticale) avec brides."""
    px = im.load()
    if y0 == y1:
        for x in range(x0, x1 + 1):
            for i, c in enumerate((CU[1], CU[2], CU[3])): px[x, y0 + i] = c + (255,)
            if (x - x0) % 12 in (0, 1) and x0 < x < x1: px[x, y0 - 1] = px[x, y0 + 3] = (LA[1] if (x - x0) % 12 == 0 else LA[3]) + (255,)
    else:
        for y in range(y0, y1 + 1):
            for i, c in enumerate((CU[1], CU[2], CU[3])): px[x0 + i, y] = c + (255,)
            if (y - y0) % 12 in (0, 1) and y0 < y < y1: px[x0 - 1, y] = px[x0 + 3, y] = (LA[1] if (y - y0) % 12 == 0 else LA[3]) + (255,)

def fantome(im, x, y, grille):
    """Silhouette pâle dans une case vide (outil, lapis, encre)."""
    px = im.load()
    for j, l in enumerate(grille):
        for i, c in enumerate(l):
            if c == "#": r, g, b, a = px[x + i, y + j]; px[x + i, y + j] = (min(255, r + 28), min(255, g + 22), min(255, b + 12), 255)

PIOCHE = ["................", ".....######.....", "...##......##...", "..#....##....#..", "..#....##....#..", ".......##.......",
          ".......##.......", ".......##.......", ".......##.......", ".......##.......", ".......##.......", ".......##.......",
          ".......##.......", ".......##.......", "................", "................"]
LAPIS = ["................", "................", "......####......", ".....######.....", "....###..###....", "...###....###...",
         "...##......##...", "...##......##...", "...###....###...", "....###..###....", ".....######.....", "......####......",
         "................", "................", "................", "................"]
ENCRE = ["................", "...........##...", "..........##....", ".........##.....", "........##......", ".......##.......",
         "....#######.....", "...#.......#....", "..#.........#...", "..#.........#...", "..#.........#...", "..#.........#...",
         "...#########....", "................", "................", "................"]

# ---------------------------------------------------------------- table de l'Empire (232 x 222)
def table():
    w, h = 232, 222
    g, a = panneau(w, h); px = g.load()
    for (x, y) in ((22, 35), (22, 60), (22, 85)): creux(px, x - 1, y - 1, 18, 18)
    for l in range(3):
        for c in range(9): creux(px, 35 + c * 18 - 1, 140 + l * 18 - 1, 18, 18)
    for c in range(9): creux(px, 35 + c * 18 - 1, 198 - 1, 18, 18)
    creux(px, 49, 17, 178, 110, fond=60)                                 # registre des enchantements
    im = metalliser(g, a, 5)
    # tuyau qui relie les trois cases, roues et rivets
    tuyau(im, 29, 53, 29, 58); tuyau(im, 29, 78, 29, 83)
    roue(im, 30.5, 113.5, 9, dents=10, trou=2.2); roue(im, 41.5, 120.5, 5.5, CU, dents=7, trou=1.2)
    for (x, y) in ((51, 19), (223, 19), (51, 123), (223, 123)): rivet(im, x, y)
    fantome(im, 22, 35, PIOCHE); fantome(im, 22, 60, LAPIS); fantome(im, 22, 85, ENCRE)
    # plaque de titre
    plaque(im, 5, 4, 172, 12)
    return im

def plaque(im, x, y, w, h):
    """Plaque de laiton rivetée pour un titre."""
    px = im.load()
    for j in range(h):
        for i in range(w):
            c = LA[2] if 0 < j < h - 1 else LA[3]
            if j == 1: c = LA[1]
            if i in (0, w - 1): c = LA[3]
            px[x + i, y + j] = c + (255,)
    for i in range(w): px[x + i, y + h] = NOIR + (255,) if 0 < i < w else px[x + i, y + h]
    rivet(im, x + 2, y + h // 2 - 1); rivet(im, x + w - 4, y + h // 2 - 1)

# ---------------------------------------------------------------- étendards (310 x 224) : vitrine d'aperçu baked
def etendard():
    w, h = 310, 226
    g, a = panneau(w, h, 512, 256); px = g.load()
    creux(px, 222, 16, 80, 148, fond=40)                                 # vitrine de l'aperçu
    im = metalliser(g, a, 9)
    pv = im.load()
    for y in range(17, 163):                                             # verre : léger dégradé
        for x in range(223, 301):
            r, gg, b, _ = pv[x, y]; t = (y - 17) / 146
            pv[x, y] = (int(r + 10 * (1 - t)), int(gg + 9 * (1 - t)), int(b + 8 * (1 - t)), 255)
    for (x, y) in ((224, 18), (298, 18), (224, 160), (298, 160)): rivet(im, x, y)
    plaque(im, 8, 4, 160, 12)
    # roues décoratives sous la vitrine
    roue(im, 244.5, 190.5, 12, dents=12, trou=2.6); roue(im, 266.5, 202.5, 7, CU, dents=9, trou=1.6); roue(im, 283.5, 186.5, 5, dents=7, trou=1.2)
    tuyau(im, 226, 170, 296, 170)
    return im

# ---------------------------------------------------------------- sprites (128 x 64)
def touche(face, bague, texte_sombre=True):
    t = Image.new("RGBA", (15, 14)); p = t.load()
    for y in range(14):
        for x in range(15):
            dx, dy = (x + .5 - 7.5) / 7.5, (y + .5 - 7) / 7
            d = dx * dx + dy * dy
            if d <= 1.0: p[x, y] = (bague[2] if dy > 0.2 else bague[1]) + (255,)
            if d <= 0.62: p[x, y] = (face[1] if dy > 0.35 else face[0]) + (255,)
            if 0.9 < d <= 1.0 and dy > 0: p[x, y] = bague[3] + (255,)
    return t

def fleche(droite, survol):
    t = Image.new("RGBA", (16, 16)); p = t.load()
    corps = LA if survol else [(232, 186, 100), (206, 154, 70), (170, 120, 50), (128, 86, 34), (84, 54, 20)]
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + .5 - 8, y + .5 - 8)
            if d < 7.6: p[x, y] = (corps[1] if y < 6 else corps[2] if y < 11 else corps[3]) + (255,)
            if 7.6 <= d < 8.4: p[x, y] = NOIR + (255,)
    for i in range(4):
        col = 6 + i if droite else 9 - i
        for y in range(4 + i, 12 - i): p[col, y] = NOIR + (255,)
    return t

def onglet(actif, w=72):
    t = Image.new("RGBA", (w, 16)); p = t.load()
    for y in range(16):
        for x in range(w):
            if (x < 2 and y < 2) or (x > w - 3 and y < 2): continue
            c = metal(198) if actif else metal(150)
            if x == 0 or x == w - 1 or y == 0: c = NOIR
            elif x == 1 or y == 1: c = metal(255) if actif else metal(198)
            elif x == w - 2: c = metal(85)
            p[x, y] = c + (255,)
    return t

def sprites():
    im = Image.new("RGBA", (128, 64))
    IVOIRE = [(238, 228, 200), (214, 202, 170)]; IV_S = [(255, 246, 220), (232, 220, 188)]
    GRIS = [(92, 86, 78), (74, 68, 62)]; OR = [(255, 226, 120), (232, 190, 70)]; OR_S = [(255, 242, 170), (250, 214, 110)]
    AME = [(206, 160, 255), (150, 96, 220), (110, 64, 176), (70, 36, 120)]; AME_O = [(120, 104, 130), (96, 84, 104), (80, 70, 88), (60, 52, 66)]
    BRONZE = [(0, 0, 0), (200, 150, 62), (150, 104, 38), (96, 62, 22)]; BR_S = [(0, 0, 0), (236, 196, 100), (200, 150, 62), (150, 104, 38)]
    BR_O = [(0, 0, 0), (110, 96, 86), (86, 76, 68), (60, 52, 46)]
    for i, (f, b) in enumerate(((IVOIRE, BRONZE), (IV_S, BR_S), (GRIS, BR_O), (OR, AME), (OR_S, AME), ([(96, 84, 60), (80, 70, 50)], AME_O))):
        im.alpha_composite(touche(f, b), (i * 16, 0))
    for i, (d, s) in enumerate(((False, False), (True, False), (False, True), (True, True))):
        im.alpha_composite(fleche(d, s), (i * 16, 16))
    im.alpha_composite(onglet(True), (0, 32)); im.alpha_composite(onglet(False), (0, 48))
    return im

if __name__ == "__main__":
    table().save(RES + "table_empire.png"); etendard().save(RES + "etendard.png"); sprites().save(RES + "elements.png")
    print("ok")
