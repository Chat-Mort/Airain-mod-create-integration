import sys, math, random; sys.path.insert(0, '../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
random.seed(2); R = 2
def bx(V, x0, y0, z0, x1, y1, z1, c, b=6):
    for X in range(round(x0*R), round(x1*R)):
        for Y in range(round(y0*R), round(y1*R)):
            for Z in range(round(z0*R), round(z1*R)):
                V[(X, Y, Z)] = c if len(c) == 4 else tuple(max(0, min(255, k + random.randint(-b, b))) for k in c)
WH, WH2, GOLD, GOLD2, RED, IRON, GLASS, WOOD, WOOD2 = (236,234,224),(200,196,186),(232,192,72),(180,135,40),(150,26,32),(80,82,90),(150,200,215,1),(140,98,58),(110,74,42)
NOIR, NOIR2, VIO, LAV, PALE = (24,20,34),(44,36,62),(96,58,156),(186,156,255,1),(232,218,255,1)
def borne_empire():
    V = {}
    bx(V, 2, 0, 2, 14, 2, 14, GOLD2); bx(V, 3, 2, 3, 13, 22, 13, WH)
    bx(V, 3, 2, 2.5, 13, 3, 3, GOLD); bx(V, 3, 21, 2.5, 13, 22, 3, GOLD)
    bx(V, 4, 11, 2.4, 12, 19, 3, IRON); bx(V, 5, 12, 2.2, 11, 18, 2.4, GLASS)   # écran
    bx(V, 6, 8, 2.2, 10, 9, 2.6, (30,30,30)); bx(V, 5, 7.5, 2.4, 11, 9.5, 2.6, GOLD)  # fente à pièces
    bx(V, 4, 4, 2.2, 7, 6, 2.6, RED); bx(V, 9, 4, 2.2, 12, 6, 2.6, RED)           # boutons
    bx(V, 13, 14, 6, 14.5, 15, 7, GOLD2); bx(V, 14, 12, 6.25, 15, 17, 6.75, IRON) # levier
    bx(V, 6, 22, 6, 10, 28, 10, GOLD); bx(V, 5, 28, 5, 11, 29, 11, GOLD2)        # tube pneumatique
    bx(V, 6.5, 22, 6.5, 9.5, 28, 9.5, GLASS)
    return V
def borne_echo():
    V = {}
    bx(V, 2, 0, 2, 14, 2, 14, VIO); bx(V, 3, 2, 3, 13, 20, 13, NOIR)
    bx(V, 4, 4, 2.5, 12, 18, 3, NOIR2)
    for y in (6, 9, 12, 15): bx(V, 5, y, 2, 11, y + 1, 2.5, LAV)               # runes
    bx(V, 4, 20, 4, 12, 21, 12, VIO)
    bx(V, 7, 23, 7, 9, 28, 9, LAV); bx(V, 6.5, 24, 7.5, 9.5, 27, 8.5, PALE)      # cristal flottant
    return V
def plateforme(emp):
    V = {}
    bx(V, 0, 0, 0, 48, 2, 48, WH if emp else NOIR2)
    bx(V, 0, 2, 0, 48, 2.5, 2, GOLD if emp else VIO); bx(V, 0, 2, 46, 48, 2.5, 48, GOLD if emp else VIO)
    bx(V, 0, 2, 2, 2, 2.5, 46, GOLD if emp else VIO); bx(V, 46, 2, 2, 48, 2.5, 46, GOLD if emp else VIO)
    if emp:
        for k in range(-10, 11):
            bx(V, 24 + k - 1, 2, 24 + k - 1, 24 + k + 1, 2.3, 24 + k + 1, RED, 0); bx(V, 24 + k - 1, 2, 24 - k - 1, 24 + k + 1, 2.3, 24 - k + 1, RED, 0)
    else:
        for a in range(0, 360, 4):
            r = 14; x, z = 24 + math.cos(math.radians(a)) * r, 24 + math.sin(math.radians(a)) * r
            bx(V, x - .5, 2, z - .5, x + .5, 2.5, z + .5, LAV)
        for a in range(0, 360, 60):
            x, z = 24 + math.cos(math.radians(a)) * 9, 24 + math.sin(math.radians(a)) * 9
            bx(V, x - 1, 2, z - 1, x + 1, 2.5, z + 1, PALE)
    return V
def caisse(emp, para=False):
    V = {}
    bx(V, 2, 0, 2, 14, 12, 14, WOOD if emp else NOIR2)
    for y in (0, 11): bx(V, 2, y, 2, 14, y + 1, 14, WOOD2 if emp else NOIR)
    for x, z in ((2, 2), (13, 2), (2, 13), (13, 13)): bx(V, x, 0, z, x + 1, 12, z + 1, GOLD if emp else LAV)
    if not emp: bx(V, 5, 3, 1.5, 11, 9, 2, LAV)
    if para:
        for x, z in ((3, 3), (12.5, 3), (3, 12.5), (12.5, 12.5)): bx(V, x, 12, z, x + .5, 24, z + .5, (90, 80, 70))
        for X in range(-10, 26):
            for Z in range(-10, 26):
                d = math.hypot(X - 8, Z - 8)
                if d < 15: bx(V, X, 24 + (15 - d) * .4, Z, X + 1, 24.8 + (15 - d) * .4, Z + 1, RED if (int(math.degrees(math.atan2(Z - 8, X - 8))) // 30) % 2 else WH, 3)
    return V
def F(V): return {(x, y, -z): c for (x, y, z), c in V.items()}
ims = [(rendu(F(borne_empire()), T=4), "Borne (Empire)"), (rendu(plateforme(True), T=2), "Zone d'arrivage"), (rendu(caisse(True, True), T=3), "Colis parachuté"),
       (rendu(F(borne_echo()), T=4), "Borne (Écho)"), (rendu(plateforme(False), T=2), "Zone d'arrivage"), (rendu(F(caisse(False)), T=4), "Colis téléporté")]
cols = 3; W = 3 * 330; H = 2 * 330
out = Image.new('RGB', (W, H), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
for i, (im, t) in enumerate(ims):
    im.thumbnail((310, 280)); x = (i % 3) * 330 + 10; y = (i // 3) * 330 + 10
    out.paste(im, (x + (310 - im.width) // 2, y + 30 + (280 - im.height))); d.text((x, y), t, fill=(230, 220, 200), font=f)
out.save('apercu_borne.png'); print(out.size)
