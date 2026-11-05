"""Squelettes v2 : un automate dessiné pixel par pixel (grilles de lettres = matières), décliné en 4 variantes.
Lettres : K creux, D/M/L/H métal (sombre → reflet), b/B/Y laiton, E/e yeux, G/g rouage intérieur, R rivet."""
import random, sys
from PIL import Image
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs")

def faces(u, v, w, h, d):
    return {"up": (u+d, v, w, d), "down": (u+d+w, v, w, d), "right": (u, v+d, d, h),
            "front": (u+d, v+d, w, h), "left": (u+d+w, v+d, d, h), "back": (u+2*d+w, v+d, w, h)}

# ------------------------------------------------------------------ tête 8x8x8 (0,0)
TETE = {
 "front": ["LHHHHHHL",
           "LMMRMMRD",
           "DKKKKKKD",
           "DEEKKEED",
           "DeeKKeeD",
           "MDKbbKDM",
           "KLKLKLKK",
           "DDMMMMDD"],
 "right": ["HHHHHHHL",
           "LMMMMMMD",
           "MMMMMDMD",
           "MMbBBbMD",
           "MMbYBbMD",
           "MMMbbMMD",
           "DMMMMMDD",
           "KDDDDDDK"],
 "back":  ["HHHHHHHH",
           "LMMMMMML",
           "MKMKMKMD",
           "MKMKMKMD",
           "MKMKMKMD",
           "MMMbBMMD",
           "DMMMMMDD",
           "KDDDDDDK"],
 "up":    ["LHHDHHHL",
           "HHHDHRHL",
           "HRHDHHHL",
           "DDDDDDDD",
           "HHHDHHHL",
           "HHRDHHRL",
           "HHHDHHHL",
           "LLLDLLLD"],
 "down":  ["DDDDDDDD",
           "DMMMMMMD",
           "DMKKKKMD",
           "DMKbbKMD",
           "DMKbbKMD",
           "DMKKKKMD",
           "DMMMMMMD",
           "DDDDDDDD"],
}
TETE["left"] = [l[::-1] for l in TETE["right"]]

# ------------------------------------------------------------------ corps 8x12x4 (16,16)
CORPS = {
 "front": ["LBBYYBBL",
           "DbbBBbbD",
           "HLLMMLLH",
           "OOgMMgOO",
           "HLLMMLLH",
           "OGgMMgGO",
           "LLLMMLLL",
           "OOOMMOOO",
           "DMMBBMMD",
           "bBBYYBBb",
           "DMDMMDMD",
           "KDKDDKDK"],
 "back":  ["LBBBBBBL",
           "DbbbbbbD",
           "KDMbBMDK",
           "OOMLLMOO",
           "KDMbBMDK",
           "OOMLLMOO",
           "KDMbBMDK",
           "OOMLLMOO",
           "DMMMMMMD",
           "bBBBBBBb",
           "DMDMMDMD",
           "KDKDDKDK"],
 "right": ["LBBL", "DbbD", "HLLH", "OOOO", "HLLH", "OOOO", "LLLL", "OOOO", "DMMD", "bBBb", "DMMD", "KDDK"],
 "up":    ["LBBYYBBL", "bBBBBBBb", "bBBKKBBb", "DbbbbbbD"],
 "down":  ["DKDKDKDK", "KDKDDKDK", "DKDKDKDK", "KDKDDKDK"],
}
CORPS["left"] = [l[::-1] for l in CORPS["right"]]

# ------------------------------------------------------------------ bras et jambes 2x12x2
BRAS = ["BY", "bB", "LH", "ML", "ML", "bB", "Yb", "LH", "ML", "ML", "DM", "KD"]
JAMBE = ["bB", "DM", "LH", "ML", "ML", "bB", "Yb", "LH", "ML", "DM", "MB", "KK"]
def membre(c):
    sombre = [l.replace("H", "L").replace("Y", "B") for l in c]
    return {"front": c, "right": c, "left": [l[::-1] for l in c], "back": sombre,
            "up": [c[0], c[1]], "down": ["KD", "DK"]}

PIECES = [((0, 0, 8, 8, 8), TETE), ((16, 16, 8, 12, 4), CORPS), ((40, 16, 2, 12, 2), membre(BRAS)), ((0, 16, 2, 12, 2), membre(JAMBE))]

# dessus de crâne de l'Arbalétrier : crête de laiton d'avant en arrière, plaques rivetées, valve
DESSUS_ARBALETRIER = ["DLMbBMLD",
                      "LMMbBMML",
                      "LRMbBMRL",
                      "LMDbYDML",
                      "LMDbYDML",
                      "LRMbBMRL",
                      "LMMbBMML",
                      "DLMbBMLD"]

DESSUS_ARBALETRIER = ["".join(l[i] for l in DESSUS_ARBALETRIER) for i in range(8)]   # crête d'avant en arrière

def peindre(pal, graine=1, bruit=5, retouche=None, dessus=None):
    rnd = random.Random(graine)
    im = Image.new("RGBA", (64, 32), (0, 0, 0, 0)); px = im.load()
    for (u, v, w, h, d), grilles in PIECES:
        for nom, (x0, y0, fw, fh) in faces(u, v, w, h, d).items():
            g = dessus if (dessus and grilles is TETE and nom == "up") else grilles[nom]
            assert len(g) == fh and all(len(l) == fw for l in g), (nom, u, v)
            for j, l in enumerate(g):
                for i, c in enumerate(l):
                    col = pal[c]
                    if c in "DMLH":                 # grain du métal
                        k = rnd.randint(-bruit, bruit); col = tuple(max(0, min(255, x + k)) for x in col)
                    px[x0 + i, y0 + j] = col + (255,)
    if retouche: retouche(px, rnd)
    return im

LAITON = {"b": (150, 100, 36), "B": (206, 154, 64), "Y": (246, 210, 130)}
def pal(metal, laiton=LAITON, yeux=((255, 96, 40), (170, 40, 20)), creux=(16, 15, 18), rouage=((96, 64, 24), (150, 104, 40)), rivet=None, cavite=None):
    D, M, L, H = metal
    p = {"K": creux, "D": D, "M": M, "L": L, "H": H, "E": yeux[0], "e": yeux[1], "G": rouage[1], "g": rouage[0], "R": rivet or H, "O": cavite or creux}
    p.update(laiton); return p

VARIANTES = {
 # acier nickelé, laiton poli, yeux rouges
 "skeleton": pal(((74, 78, 86), (122, 128, 138), (176, 182, 192), (226, 230, 236))),
 # acier bleui par le froid, yeux cyan, givre
 "stray": pal(((52, 70, 96), (86, 112, 142), (140, 170, 198), (214, 234, 248)),
              laiton={"b": (96, 120, 140), "B": (150, 178, 198), "Y": (228, 244, 252)},
              yeux=((120, 250, 255), (40, 160, 190)), rouage=((50, 70, 96), (110, 140, 170))),
 # bronze corrodé, vert-de-gris, yeux verts
 "bogged": pal(((50, 60, 40), (78, 92, 58), (108, 124, 80), (150, 166, 112)),
               laiton={"b": (60, 104, 84), "B": (92, 150, 120), "Y": (150, 200, 166)},
               yeux=((170, 255, 90), (70, 150, 40)), creux=(14, 18, 12), rouage=((60, 44, 20), (110, 80, 36))),
 # fonte noircie, creux en fusion : le fourneau est à l'intérieur
 "wither_skeleton": pal(((22, 20, 22), (40, 37, 40), (62, 58, 62), (92, 86, 90)),
                        laiton={"b": (120, 50, 20), "B": (176, 82, 30), "Y": (236, 140, 60)},
                        yeux=((255, 210, 90), (255, 120, 30)), creux=(14, 12, 14), cavite=(220, 84, 18), rouage=((255, 150, 40), (255, 220, 110))),
}

# givre sur le Veilleur, mousse et suintements sur le Drainier
def givre(px, rnd):
    for _ in range(70):
        x, y = rnd.randrange(64), rnd.randrange(32)
        if px[x, y][3] and rnd.random() < 0.6:
            px[x, y] = (236, 248, 255, 255)
def mousse(px, rnd):
    for _ in range(90):
        x, y = rnd.randrange(64), rnd.randrange(32)
        if px[x, y][3]:
            px[x, y] = rnd.choice([(52, 92, 30, 255), (74, 120, 40, 255), (38, 70, 26, 255)])
def braise(px, rnd):
    for _ in range(40):
        x, y = rnd.randrange(64), rnd.randrange(32)
        if px[x, y][3] and px[x, y][0] < 80:
            px[x, y] = rnd.choice([(150, 50, 14, 255), (220, 96, 24, 255)])
RETOUCHES = {"stray": givre, "bogged": mousse, "wither_skeleton": braise}

if __name__ == "__main__":
    out = sys.argv[1]
    for k, p in VARIANTES.items():
        peindre(p, graine=len(k) * 7, retouche=RETOUCHES.get(k), dessus=DESSUS_ARBALETRIER if k == "skeleton" else None).save(f"{out}/{k}.png")
    print("ok")
