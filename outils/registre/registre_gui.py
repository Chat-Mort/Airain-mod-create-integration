"""Registre des fondations : livre ouvert relié de cuir rouge, coins de laiton, pages de parchemin, signet.
Planche 512 x 256 : le livre (300 x 190) en (0,0) ; sprites à droite : flèche (x=304), sceau (x=320), puces."""
import math, random
from PIL import Image
R = random.Random(9)
W, H = 300, 190
im = Image.new("RGBA", (512, 256), (0, 0, 0, 0)); px = im.load()
CUIR = [(58, 16, 14), (82, 24, 20), (104, 34, 26), (126, 46, 34)]
LAITON = [(92, 62, 22), (150, 108, 40), (205, 160, 70), (240, 210, 130)]
PARCH = (226, 205, 160)
def put(x, y, c, a=255): px[x, y] = tuple(max(0, min(255, int(v))) for v in c) + (a,)
# reliure de cuir, coins arrondis
for y in range(H):
    for x in range(W):
        if (x < 2 or x > W - 3) and (y < 2 or y > H - 3): continue
        b = min(x, y, W - 1 - x, H - 1 - y)
        c = CUIR[1] if b > 1 else CUIR[0]
        n = R.randint(-6, 6)
        if b == 2: c = CUIR[3] if (x < W / 2 and y < H / 2) else CUIR[2]
        put(x, y, tuple(v + n for v in c))
# piqûres le long du bord
for x in range(6, W - 6, 4):
    put(x, 4, CUIR[3]); put(x, H - 5, CUIR[3])
for y in range(6, H - 6, 4):
    put(4, y, CUIR[3]); put(W - 5, y, CUIR[3])
# pages : gauche [12,146) droite [154,288), hauteur [10,180)
def page(x0, x1, gauche):
    for y in range(10, 180):
        for x in range(x0, x1):
            n = R.randint(-5, 5)
            g = (x1 - 1 - x) if gauche else (x - x0)          # ombre vers la reliure
            ombre = max(0, 10 - g) * 4 if g < 10 else 0
            bord = min(y - 10, 179 - y, (x - x0) if gauche else (x1 - 1 - x))
            jaune = max(0, 4 - bord) * 6
            c = (PARCH[0] - ombre - jaune + n, PARCH[1] - ombre - jaune * 1.4 + n, PARCH[2] - ombre - jaune * 2 + n)
            put(x, y, c)
    # tranche des pages (feuillets) sous la page
    for x in range(x0 + 2, x1 - 2):
        put(x, 180, (190, 170, 128)); put(x, 181, (160, 140, 100))
page(12, 146, True); page(154, 288, False)
# dos du livre
for y in range(8, 183):
    for x in range(146, 154):
        put(x, y, CUIR[0] if x in (146, 153) else CUIR[1])
# coins de laiton
def coin(cx, cy, sx, sy):
    for j in range(14):
        for i in range(14):
            if i + j > 16: continue
            x, y = cx + i * sx, cy + j * sy
            c = LAITON[3] if (i == 0 or j == 0) else LAITON[2] if i + j < 8 else LAITON[1]
            if i + j == 16 or i + j == 15: c = LAITON[0]
            put(x, y, c)
    put(cx + 4 * sx, cy + 4 * sy, LAITON[0]); put(cx + 5 * sx, cy + 4 * sy, LAITON[3])
coin(0, 0, 1, 1); coin(W - 1, 0, -1, 1); coin(0, H - 1, 1, -1); coin(W - 1, H - 1, -1, -1)
# signet rouge qui sort en bas de la page droite
for y in range(178, 196):
    for x in range(262, 268):
        if y > 192 and abs(x - 264.5) < (y - 192): continue
        put(x, y, (150, 20, 24) if x in (262, 267) else (190, 34, 36))
# filets décoratifs des pages
for (x0, x1) in ((20, 138), (162, 280)):
    for x in range(x0, x1):
        put(x, 16, (150, 110, 70)); put(x, 173, (150, 110, 70))
# --- sprites
# flèche (13 x 13) pointant vers le haut, en (304, 0)
for y in range(13):
    for x in range(13):
        dx = x - 6
        if y <= 6 and abs(dx) <= y: put(304 + x, y, (120, 30, 24) if abs(dx) == y else (180, 50, 36))
        elif y > 6 and abs(dx) <= 1: put(304 + x, y, (120, 30, 24) if abs(dx) == 1 else (150, 40, 30))
# sceau de cire (28 x 28) en (320, 0)
for y in range(28):
    for x in range(28):
        d = math.hypot(x - 13.5, y - 13.5)
        a = math.atan2(y - 13.5, x - 13.5)
        rr = 12.5 + math.sin(a * 7) * 0.9
        if d < rr:
            c = (150, 22, 26) if d > rr - 1.5 else (178, 34, 38)
            if 7 < d < 8.2: c = (120, 16, 20)
            if d < 4.2 and (abs(x - 13.5) < 1 or abs(y - 13.5) < 1): c = (120, 16, 20)
            if x < 13 and y < 13 and d < rr - 2 and d > rr - 3.5: c = (205, 70, 70)
            put(320 + x, y, c)
# rouage du sceau (dents)
for k in range(8):
    a = k * math.pi / 4
    for r in (5.2, 6.2):
        put(320 + int(13.5 + math.cos(a) * r), int(13.5 + math.sin(a) * r), (120, 16, 20))
# puce de laiton (5 x 5) en (352, 0)
for y in range(5):
    for x in range(5):
        if abs(x - 2) + abs(y - 2) <= 2: put(352 + x, y, LAITON[2] if (x + y) < 4 else LAITON[1])
im.save("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/gui/registre.png")
big = im.crop((0, 0, 360, 200)).resize((1080, 600), Image.NEAREST); big.save("/home/claude/apercus/registre_texture.png")
