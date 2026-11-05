import math, sys
sys.argv=["x"]
exec(open("concepts.py").read().split("out = []")[0])
from PIL import Image, ImageDraw, ImageFont
def octo(V, cx, cz, r, y0, y1, c, c2=None):          # prisme octogonal
    for y in range(y0, y1):
        for x in range(int(cx - r - 1), int(cx + r + 1)):
            for z in range(int(cz - r - 1), int(cz + r + 1)):
                dx, dz = abs(x + .5 - cx), abs(z + .5 - cz)
                if dx <= r and dz <= r and dx + dz <= r * 1.42:
                    bord = dx > r - 1 or dz > r - 1 or dx + dz > r * 1.42 - 1
                    V[(x, y, z)] = c2 if (c2 and bord) else c

def tour(alerte, N=3):
    V = {}; S = 16 * N; c = S / 2
    boite(V, (0, 0, 0), (S, 3, S), TUF2); boite(V, (2, 3, 2), (S - 2, 6, S - 2), TUF)
    for (x, z) in ((2, 2), (S - 3, 2), (2, S - 3), (S - 3, S - 3)): boite(V, (x, 6, z), (x + 1, 7, z + 1), LA)
    # quatre jambes de fonte qui montent des angles vers le fût (contreforts)
    for (sx, sz) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        for y in range(6, 40):
            t = (y - 6) / 34; d = 20 - t * 10
            x, z = c + sx * d, c + sz * d
            boite(V, (x - 1.5, y, z - 1.5), (x + 1.5, y + 1, z + 1.5), FONTE)
            if y % 8 == 0: boite(V, (x - 2, y, z - 2), (x + 2, y + 1, z + 2), LA)
    R0 = 10
    octo(V, c, c, R0, 6, 36, FER, c2=FONTE)
    for y in (8, 20, 35): octo(V, c, c, R0 + 0.8, y, y + 1, LA)
    boite(V, (c - 3, 6, c - R0 - 1), (c + 3, 17, c - R0), LA2); boite(V, (c - 2, 7, c - R0 - 1.5), (c + 2, 16, c - R0 - 0.5), (40, 30, 22))
    boite(V, (c - 1, 24, c - R0 - 1), (c + 2, 27, c - R0), (230, 225, 200))                  # manomètre
    boite(V, (c + R0, 12, c - 2), (c + R0 + 2, 17, c + 2), LA2)                               # manivelle
    # galerie de la sirène
    octo(V, c, c, R0 + 4, 36, 38, LA2)
    for k in range(20):
        a = k * math.pi / 10; r = R0 + 3.5
        boite(V, (c + math.cos(a) * r, 38, c + math.sin(a) * r), (c + math.cos(a) * r + 1, 41, c + math.sin(a) * r + 1), LA)
    R1 = 7
    octo(V, c, c, R1, 38, 84, FER, c2=FONTE)
    for y in (50, 62, 74): octo(V, c, c, R1 + 0.8, y, y + 1, CU)
    for y in (56, 68):
        boite(V, (c - 1, y, c - R1 - 1), (c + 1, y + 3, c - R1), (255, 210, 120) if alerte else (120, 90, 50))   # hublots
    ang = 0.7 if alerte else 0
    for s in (1, -1):
        for t in range(0, 14):
            rr = 1.6 + t * 0.34
            px = c + s * (R1 + t) * math.cos(ang); pz = c + s * (R1 + t) * math.sin(ang)
            for yy in range(int(44 - rr), int(44 + rr) + 1):
                for q in range(-int(rr), int(rr) + 1):
                    if (yy - 44) ** 2 + q * q <= rr * rr:
                        V[(int(px - q * math.sin(ang)), yy, int(pz + q * math.cos(ang)))] = LA if t < 13 else LA2
    # le phare
    octo(V, c, c, R1 + 5, 84, 86, LA2)
    for k in range(20):
        a = k * math.pi / 10; r = R1 + 4.5
        boite(V, (c + math.cos(a) * r, 86, c + math.sin(a) * r), (c + math.cos(a) * r + 1, 89, c + math.sin(a) * r + 1), LA)
    R2 = 7
    octo(V, c, c, R2, 86, 102, (255, 80, 50, 1) if alerte else ROUGE, c2=VERRE)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        boite(V, (c + math.cos(a) * R2 - .5, 86, c + math.sin(a) * R2 - .5), (c + math.cos(a) * R2 + .5, 102, c + math.sin(a) * R2 + .5), LA2)
    octo(V, c, c, R2 + 1.5, 102, 104, CU); octo(V, c, c, R2, 104, 107, CU); octo(V, c, c, R2 - 2.5, 107, 110, CU); octo(V, c, c, 2, 110, 112, OX)
    boite(V, (c - 1, 112, c - 1), (c + 1, 120, c + 1), LA3)
    for k in range(8):
        a = k * math.pi / 4; boite(V, (c + math.cos(a) * 3 - .5, 116, c + math.sin(a) * 3 - .5), (c + math.cos(a) * 3 + .5, 118, c + math.sin(a) * 3 + .5), LA)
    if alerte:
        for k in range(1, 34):
            w = 1 + k // 6
            boite(V, (c + R2 + k, 93 - w // 2, c - w), (c + R2 + k + 1, 95 + w // 2, c + w), (255, 110, 70, 1))
        for k in range(1, 22):
            w = 1 + k // 6
            boite(V, (c - w, 93 - w // 2, c - R2 - k - 1), (c + w, 95 + w // 2, c - R2 - k), (255, 110, 70, 1))
    # un joueur à l'échelle (2 blocs) au pied
    if not alerte:
        boite(V, (c - 2, 6, -6), (c + 2, 18, -4), (60, 90, 160)); boite(V, (c - 2, 18, -6), (c + 2, 30, -4), (90, 140, 200)); boite(V, (c - 2, 30, -6), (c + 2, 38, -4), (220, 180, 140))
    return V

imgs = [("3 × 3 · au repos", rendu(tour(False), 4)), ("3 × 3 · en alerte", rendu(tour(True), 4))]
h = max(i.height for _, i in imgs); w = sum(i.width for _, i in imgs) + 30
im = Image.new("RGB", (w, h + 50), (32, 33, 38)); d = ImageDraw.Draw(im); x = 0
d.text((10, 8), "La balise de défense : tour-phare à sirène (base 3 × 3, 7 blocs et demi de haut)", font=ImageFont.truetype(FB, 18), fill=(240, 210, 140))
for t, i in imgs:
    im.paste(i, (x, 40 + h - i.height)); d.text((x + i.width // 2 - 50, 40), t, font=ImageFont.truetype(F, 14), fill=(220, 220, 220)); x += i.width + 30
# personnage à l'échelle (2 blocs) à côté
im.save("/home/claude/apercus/balise_tour_v7.png"); print(im.size)
