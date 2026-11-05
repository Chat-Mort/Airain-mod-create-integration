from PIL import Image
import math
CU = [(92, 50, 30), (140, 76, 44), (184, 104, 62), (214, 140, 88), (236, 178, 122)]   # cuivre
FE = [(40, 40, 46), (66, 66, 74), (98, 98, 106), (138, 138, 146), (182, 182, 188)]    # fer
AN = [(84, 88, 86), (120, 126, 122), (156, 162, 156)]                                 # andésite
K = (26, 20, 18)
def cadre(im):
    """Boîtier de cuivre façon Create : bord biseauté et coins rivetés."""
    px = im.load()
    for i in range(16):
        for (x, y) in ((i, 0), (0, i)): px[x, y] = CU[3]
        for (x, y) in ((i, 15), (15, i)): px[x, y] = CU[0]
        for (x, y) in ((i, 1), (1, i)): px[x, y] = CU[2] if 1 <= i <= 14 else px[x, y]
        for (x, y) in ((i, 14), (14, i)): px[x, y] = CU[1] if 1 <= i <= 14 else px[x, y]
    for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)): px[x, y] = CU[4]; px[x + (1 if x < 8 else -1), y + (1 if y < 8 else -1)] = CU[0]
def fond(c):
    im = Image.new("RGB", (16, 16), c[2]); px = im.load()
    for y in range(2, 14):
        for x in range(2, 14): px[x, y] = c[2] if (x + y) % 5 else c[1]
    return im
# --- côté : fenêtre ronde sur un rouage, emboîture d'arbre au centre
cote = fond(CU); px = cote.load(); cadre(cote)
for y in range(16):
    for x in range(16):
        r = math.hypot(x - 7.5, y - 7.5)
        if 3.2 < r <= 5.6:
            a = (math.degrees(math.atan2(y - 7.5, x - 7.5)) + 360) % 360
            px[x, y] = AN[2] if (a % 45) < 22 and r > 4.6 else AN[1]
        elif r <= 3.2: px[x, y] = FE[1]
        elif 5.6 < r <= 6.4: px[x, y] = K
for (x, y) in ((7, 7), (8, 7), (7, 8), (8, 8)): px[x, y] = FE[3]
for (x, y) in ((6, 7), (6, 8), (9, 7), (9, 8), (7, 6), (8, 6), (7, 9), (8, 9)): px[x, y] = FE[0]
# --- face : jauge d'huile et petit cadran
face = fond(CU); px = face.load(); cadre(face)
for y in range(3, 13):
    for x in (4, 5, 6): px[x, y] = (40, 30, 18) if y >= 7 else (150, 170, 176)
    px[3, y] = FE[2]; px[7, y] = FE[2]
for x in range(3, 8): px[x, 2] = FE[3]; px[x, 13] = FE[1]
for y in range(7, 13): px[5, y] = (70, 52, 26)
px[4, 7] = (110, 84, 40)
for y in range(16):
    for x in range(16):
        r = math.hypot(x - 10.5, y - 6.5)
        if r <= 2.2: px[x, y] = (226, 214, 180)
        elif r <= 3.1: px[x, y] = FE[3] if y < 7 else FE[1]
px[10, 6] = K; px[11, 5] = (190, 40, 30); px[12, 4] = (190, 40, 30)
for x in range(9, 13): px[x, 11] = FE[3]; px[x, 12] = FE[1]
# --- dessus : plaque de fer, étau et goutte d'huile
dessus = Image.new("RGB", (16, 16), FE[2]); px = dessus.load()
for y in range(16):
    for x in range(16): px[x, y] = FE[2] if (x // 4 + y // 4) % 2 == 0 else FE[1]
    px[0, y] = FE[3]; px[15, y] = FE[0]
for x in range(16): px[x, 0] = FE[3]; px[x, 15] = FE[0]
for y in range(5, 11):                                                    # étau
    for x in (4, 5, 10, 11): px[x, y] = CU[2] if x in (4, 10) else CU[1]
for x in range(6, 10): px[x, 7] = FE[4]; px[x, 8] = FE[3]
for x in range(2, 14): px[x, 12] = FE[0]
px[12, 3] = (40, 30, 18); px[12, 4] = (70, 52, 26); px[13, 4] = (40, 30, 18)
# --- dessous : boîtier avec grille de sortie
dessous = fond(CU); px = dessous.load(); cadre(dessous)
for y in range(4, 12):
    for x in range(4, 12): px[x, y] = K if (y % 2 == 0) else FE[1]
base = "/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/block/"
for n, im in (("banc_cote", cote), ("banc_face", face), ("banc_dessus", dessus), ("banc_dessous", dessous)): im.save(base + n + ".png")
c = Image.new("RGB", (4*170, 170), (60, 60, 64))
for i, im in enumerate((face, cote, dessus, dessous)): c.paste(im.resize((160, 160), Image.NEAREST), (5 + i*170, 5))
c.save("/home/claude/apercus/banc_textures.png")
