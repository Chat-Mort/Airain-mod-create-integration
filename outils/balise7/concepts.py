import math
from PIL import Image, ImageDraw, ImageFont
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LA=(205,160,70); LA2=(150,108,40); LA3=(240,205,120); FER=(70,72,78); FONTE=(48,50,56); CU=(190,110,75); OX=(85,165,140)
TUF=(112,114,106); TUF2=(90,92,86); ROUGE=(120,28,24); ROUGE_ON=(255,70,40); VERRE=(150,190,205); BOIS=(110,80,50); TOILE=(160,28,26); OR=(220,175,60)
def boite(V, a, b, c):
    for x in range(int(a[0]), int(b[0])):
        for y in range(int(a[1]), int(b[1])):
            for z in range(int(a[2]), int(b[2])):
                V[(x, y, z)] = c
def cyl(V, cx, cz, r, y0, y1, c, axe="y", c2=None):
    for y in range(y0, y1):
        for x in range(int(cx - r - 1), int(cx + r + 1)):
            for z in range(int(cz - r - 1), int(cz + r + 1)):
                if (x + .5 - cx) ** 2 + (z + .5 - cz) ** 2 <= r * r:
                    V[(x, y, z)] = c2 if c2 and (x + .5 - cx) ** 2 + (z + .5 - cz) ** 2 > (r - 1) ** 2 else c
def cylx(V, cy, cz, r, x0, x1, c, rf=None):
    for x in range(x0, x1):
        rr = r if rf is None else rf(x)
        for y in range(int(cy - rr - 1), int(cy + rr + 1)):
            for z in range(int(cz - rr - 1), int(cz + rr + 1)):
                if (y + .5 - cy) ** 2 + (z + .5 - cz) ** 2 <= rr * rr: V[(x, y, z)] = c
def rendu(V, T=8):
    pts = sorted(V.items(), key=lambda kv: (kv[0][0] + kv[0][2], kv[0][1]))
    proj = lambda x, y, z: ((x - z) * T, (x + z) * T / 2 - y * T * 1.15)
    co = [proj(*p) for p, _ in pts]
    mnx = min(a for a, _ in co) - 2 * T; mxx = max(a for a, _ in co) + 2 * T; mny = min(b for _, b in co) - 2 * T; mxy = max(b for _, b in co) + 3 * T
    im = Image.new("RGB", (int(mxx - mnx) + 10, int(mxy - mny) + 10), (32, 33, 38)); d = ImageDraw.Draw(im)
    ox, oy = -mnx + 5, -mny + 5
    for (x, y, z), c in pts:
        X, Y = proj(x, y, z); X += ox; Y += oy; h = T * 1.15
        top = [(X, Y - h), (X + T, Y + T / 2 - h), (X, Y + T - h), (X - T, Y + T / 2 - h)]
        left = [(X - T, Y + T / 2 - h), (X, Y + T - h), (X, Y + T), (X - T, Y + T / 2)]
        right = [(X, Y + T - h), (X + T, Y + T / 2 - h), (X + T, Y + T / 2), (X, Y + T)]
        glow = len(c) == 4
        c = c[:3]
        d.polygon(top, fill=c); d.polygon(left, fill=c if glow else tuple(int(v * .78) for v in c)); d.polygon(right, fill=c if glow else tuple(int(v * .6) for v in c))
    return im

def socle(V):
    boite(V, (0, 0, 0), (16, 2, 16), TUF2); boite(V, (1, 2, 1), (15, 3, 15), TUF)
    for (x, z) in ((1, 1), (14, 1), (1, 14), (14, 14)): boite(V, (x, 3, z), (x + 1, 4, z + 1), LA)

def A(alerte):    # sirène d'alerte : 2 blocs, tête qui tourne
    V = {}; socle(V)
    cyl(V, 8, 8, 5.5, 3, 15, FONTE, c2=FER)
    for y in (5, 12): cyl(V, 8, 8, 6, y, y + 1, LA)
    boite(V, (13, 7, 6), (15, 12, 10), LA2); boite(V, (15, 9, 7), (16, 10, 9), LA3)      # manivelle
    boite(V, (6, 6, 2), (10, 10, 3), CU)                                                   # cadran
    boite(V, (7, 7, 1), (9, 9, 2), (230, 225, 200))
    cyl(V, 8, 8, 2, 15, 21, FER)
    a = 0 if not alerte else 1
    cylx(V, 23.5, 8, 3, 3, 13, LA, rf=lambda x: 2.5 if x < 9 else 2.5 + (x - 9) * 0.55)   # le pavillon
    cylx(V, 23.5, 8, 1.5, 12, 13, FONTE)
    boite(V, (2, 21, 6), (4, 26, 10), LA2)
    cyl(V, 8, 8, 2, 26, 30, ROUGE_ON + (1,) if alerte else ROUGE)
    cyl(V, 8, 8, 2.5, 30, 31, LA); boite(V, (7, 31, 7), (9, 32, 9), LA3)
    if alerte:
        for k in range(1, 9): boite(V, (8 + k, 27, 7), (9 + k, 29, 9), (255, 90, 60, 1))
    return V

def B(alerte):    # phare de garnison : 2 blocs, faisceau tournant
    V = {}; socle(V)
    cyl(V, 8, 8, 6, 3, 13, FER, c2=FONTE)
    for y in (4, 12): cyl(V, 8, 8, 6.5, y, y + 1, CU)
    boite(V, (6, 3, 1), (10, 9, 2), LA2); boite(V, (7, 4, 1), (9, 8, 2), FONTE)              # porte
    for (x, z) in ((2, 8), (14, 8)): boite(V, (x - 1, 8, z - 1), (x + 1, 10, z + 1), (230, 225, 200))   # manomètres
    cyl(V, 8, 8, 8, 13, 14, LA)
    for k in range(12):
        a = k * math.pi / 6; boite(V, (8 + math.cos(a) * 7.4, 14, 8 + math.sin(a) * 7.4), (9 + math.cos(a) * 7.4, 16, 9 + math.sin(a) * 7.4), LA2)
    cyl(V, 8, 8, 4, 14, 24, (255, 80, 50, 1) if alerte else ROUGE, c2=VERRE)
    for (x, z) in ((4, 4), (11, 4), (4, 11), (11, 11)): boite(V, (x, 14, z), (x + 1, 24, z + 1), LA2)
    cyl(V, 8, 8, 5, 24, 26, CU); cyl(V, 8, 8, 3.5, 26, 28, CU); cyl(V, 8, 8, 2, 28, 29, OX)
    boite(V, (7, 29, 7), (9, 32, 9), LA3)
    if alerte:
        for k in range(1, 14):
            w = 1 + k // 4
            boite(V, (12 + k, 18 - w // 2, 8 - w), (13 + k, 20 + w // 2, 8 + w), (255, 110, 70, 1))
    return V

def C(alerte):    # tour de vigie : 3 blocs, cloche, lampe, bannière hissée à l'alerte
    V = {}; socle(V)
    for (x, z) in ((2, 2), (13, 2), (2, 13), (13, 13)): boite(V, (x, 3, z), (x + 1, 40, z + 1), FONTE)
    for y in range(6, 38, 8):
        for (a, b) in (((2, 2), (13, 2)), ((2, 13), (13, 13)), ((2, 2), (2, 13)), ((13, 2), (13, 13))):
            for t in range(12):
                x = a[0] + (b[0] - a[0]) * t / 11; z = a[1] + (b[1] - a[1]) * t / 11
                yy = y + (t if (y // 8) % 2 else 11 - t) * 0.6
                boite(V, (x, yy, z), (x + 1, yy + 1, z + 1), FER)
    boite(V, (1, 38, 1), (15, 40, 15), LA2); boite(V, (2, 40, 2), (14, 41, 14), BOIS)
    cyl(V, 8, 8, 3.5, 30, 37, LA, c2=LA2); boite(V, (7, 37, 7), (9, 38, 9), FONTE); boite(V, (7, 29, 7), (9, 30, 9), LA3)   # cloche
    for (x, z) in ((2, 2), (13, 2), (2, 13), (13, 13)): boite(V, (x, 41, z), (x + 1, 45, z + 1), LA2)
    boite(V, (1, 45, 1), (15, 46, 15), CU); boite(V, (4, 46, 4), (12, 47, 12), CU)
    cyl(V, 8, 8, 2, 47, 51, (255, 80, 50, 1) if alerte else ROUGE); boite(V, (7, 51, 7), (9, 53, 9), LA3)
    boite(V, (14, 40, 7), (15, 62, 8), FER); boite(V, (14, 61, 7), (23, 62, 8), FER)      # mât et potence de la bannière
    if alerte:
        boite(V, (16, 44, 7), (23, 61, 8), TOILE); boite(V, (18, 52, 7), (21, 55, 7.5), OR)
    else:
        boite(V, (16, 59, 7), (23, 61, 8), TOILE)
    return V

out = []
for nom, f, titre in (("A", A, "A · La sirène d'alerte (2 blocs)"), ("B", B, "B · Le phare de garnison (2 blocs)"), ("C", C, "C · La tour de vigie (3 blocs)")):
    a = rendu(f(False)); b = rendu(f(True))
    h = max(a.height, b.height); w = a.width + b.width + 40
    im = Image.new("RGB", (w, h + 60), (32, 33, 38)); d = ImageDraw.Draw(im)
    d.text((10, 8), titre, font=ImageFont.truetype(FB, 20), fill=(240, 210, 140))
    im.paste(a, (0, 40 + h - a.height)); im.paste(b, (a.width + 40, 40 + h - b.height))
    d.text((a.width // 2 - 30, h + 40), "au repos", font=ImageFont.truetype(F, 15), fill=(200, 200, 200))
    d.text((a.width + 40 + b.width // 2 - 40, h + 40), "en alerte", font=ImageFont.truetype(F, 15), fill=(255, 120, 90))
    out.append(im)
W = max(i.width for i in out); H = sum(i.height for i in out)
g = Image.new("RGB", (W, H), (32, 33, 38)); y = 0
for i in out: g.paste(i, (0, y)); y += i.height
g.save("/home/claude/apercus/balise_concepts_v7.png"); print(g.size)
