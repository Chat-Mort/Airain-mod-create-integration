import sys, math, random; sys.path.insert(0, '../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
random.seed(3)
R = 2
def bx(V, x0, y0, z0, x1, y1, z1, c, bruit=6):
    for X in range(round(x0 * R), round(x1 * R)):
        for Y in range(round(y0 * R), round(y1 * R)):
            for Z in range(round(z0 * R), round(z1 * R)):
                if len(c) == 3: n = random.randint(-bruit, bruit); V[(X, Y, Z)] = tuple(max(0, min(255, k + n)) for k in c)
                else: V[(X, Y, Z)] = c
def anneau(V, cx, cy, z0, z1, r0, r1, c):
    for X in range(round((cx - r1 - 1) * R), round((cx + r1 + 1) * R)):
        for Y in range(round((cy - r1 - 1) * R), round((cy + r1 + 1) * R)):
            d = math.hypot(X / R + 0.25 - cx, Y / R + 0.25 - cy)
            if r0 <= d <= r1:
                for Z in range(round(z0 * R), round(z1 * R)): V[(X, Y, Z)] = c
WH, WH2, GOLD, GOLD2, RED, RED2, NETH, STAR = (238, 236, 226), (205, 200, 190), (235, 195, 75), (185, 140, 40), (150, 25, 32), (115, 15, 22), (50, 45, 50), (255, 240, 170, 1)
def trone():
    V = {}
    bx(V, 0, 0, 0, 16, 1.5, 16, NETH); bx(V, 0, 1.5, 0, 16, 2, 16, GOLD2)
    bx(V, 2, 2, 3, 14, 7, 14, WH); bx(V, 2, 2, 2.5, 3, 7, 3, GOLD); bx(V, 13, 2, 2.5, 14, 7, 3, GOLD); bx(V, 3, 6, 2.5, 13, 7, 3, GOLD)
    bx(V, 3, 7, 2, 13, 9, 13, RED); bx(V, 3, 8.5, 2, 13, 9, 2.5, RED2)
    for x0 in (1, 13):
        bx(V, x0, 7, 2, x0 + 2, 12, 13, WH); bx(V, x0, 12, 1.5, x0 + 2, 13, 13, GOLD); bx(V, x0, 7, 1.5, x0 + 2, 12, 2, GOLD2)
    bx(V, 2, 9, 13, 14, 27, 15, WH); bx(V, 4, 10, 12.5, 12, 25, 13, RED)
    bx(V, 2, 26, 12.5, 14, 27, 15.5, GOLD); bx(V, 2, 9, 12.5, 3, 27, 13, GOLD); bx(V, 13, 9, 12.5, 14, 27, 13, GOLD)
    for x in (2, 12.5): bx(V, x, 27, 13, x + 1.5, 30, 14.5, GOLD); bx(V, x + 0.25, 30, 13.25, x + 1.25, 31, 14.25, STAR)
    anneau(V, 8, 29.5, 13, 14.5, 2.2, 3.6, GOLD)
    for k in range(8):
        a = k * math.pi / 4; bx(V, 8 + math.cos(a) * 4 - 0.5, 29.5 + math.sin(a) * 4 - 0.5, 13, 8 + math.cos(a) * 4 + 0.5, 29.5 + math.sin(a) * 4 + 0.5, 14.5, GOLD)
    bx(V, 7, 28.5, 12.5, 9, 30.5, 13.5, STAR); bx(V, 7.5, 27.5, 12.75, 8.5, 31.5, 13.25, STAR); bx(V, 6, 29, 12.75, 10, 30, 13.25, STAR)
    return V
NOIR, NOIR2, VIO, VIO2, LAV, PALE = (22, 18, 32), (42, 34, 60), (95, 58, 155), (62, 32, 102), (186, 156, 255, 1), (232, 218, 255, 1)
def solium():
    V = {}
    for X in range(0, 16 * R):
        for Z in range(0, 16 * R):
            d = math.hypot(X / R + 0.25 - 8, Z / R + 0.25 - 8)
            if d <= 8:
                for Y in range(0, 2 * R): V[(X, Y, Z)] = NOIR2 if d < 7.4 else VIO
                if 6.3 < d < 6.9 and (int(math.atan2(Z / R - 8, X / R - 8) * 6)) % 2 == 0: V[(X, 2 * R - 1, Z)] = LAV
    bx(V, 3, 2, 3, 13, 7, 13, NOIR); bx(V, 3, 6.5, 2.5, 13, 7, 3, VIO)
    bx(V, 3, 7, 3, 13, 8.5, 13, VIO)
    for x0 in (2, 12):
        bx(V, x0, 7, 3, x0 + 2, 10, 12, NOIR); bx(V, x0 + 0.5, 10, 3, x0 + 1.5, 12, 4, LAV); bx(V, x0 + 0.75, 12, 3.25, x0 + 1.25, 13, 3.75, PALE)
    bx(V, 3, 8, 12, 5, 22, 14, NOIR); bx(V, 11, 8, 12, 13, 22, 14, NOIR); bx(V, 5, 9, 13, 11, 19, 14, VIO2)
    bx(V, 3.5, 22, 12.5, 4.5, 24, 13.5, LAV); bx(V, 11.5, 22, 12.5, 12.5, 24, 13.5, LAV)
    anneau(V, 8, 22, 13, 14, 5.2, 6.2, PALE)
    bx(V, 7, 21, 12.5, 9, 23, 13.5, LAV); bx(V, 7.5, 21.5, 12.2, 8.5, 22.5, 12.5, PALE)
    for (x, y) in ((-1.5, 14), (16.5, 16)):
        bx(V, x - 0.5, y, 7.5, x + 0.5, y + 2.5, 8.5, LAV); bx(V, x - 0.25, y + 2.5, 7.75, x + 0.25, y + 3, 8.25, PALE)
    return V
def vue(V, dos=False):
    if dos: return {(x, y, -z): c for (x, y, z), c in V.items()}
    return {(-x, y, z): c for (x, y, z), c in V.items()}
ims = [(rendu(vue(trone(), True), T=4), "Trône impérial"), (rendu(vue(trone()), T=4), "(dos)"),
       (rendu(vue(solium(), True), T=4), "Solium"), (rendu(vue(solium()), T=4), "(dos)")]
W = sum(i.width for i, _ in ims) + 50; H = max(i.height for i, _ in ims) + 40
out = Image.new('RGB', (W, H), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
x = 10
for i, t in ims: out.paste(i, (x, H - i.height - 5)); d.text((x + 5, 6), t, fill=(230, 220, 200), font=f); x += i.width + 10
out.save('apercu_trone.png'); print(out.size)
