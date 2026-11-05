from PIL import Image, ImageDraw, ImageFont
REG = Image.open("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/registre_fondations.png").convert("RGBA")
pal = REG.load()
NOIR = (24, 16, 14, 255)
LA = [(92, 62, 22, 255), (150, 108, 40, 255), (205, 160, 70, 255), (240, 210, 130, 255)]
PAGE = [(236, 222, 190, 255), (200, 182, 146, 255)]
def livre(cuir, cuir_s, cuir_c, embleme, ruban):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); p = im.load()
    # contour
    for y in range(0, 16):
        for x in range(1, 15):
            p[x, y] = NOIR
    import random
    R = random.Random(4)
    for y in range(1, 15):
        for x in range(2, 14):
            k = R.choice((-10, -5, 0, 0, 0, 6)) - (y - 7) * 1      # grain du cuir, plus clair en haut
            p[x, y] = tuple(max(0, min(255, v + k)) for v in cuir[:3]) + (255,)
    for y in range(2, 14): p[12, y] = tuple(max(0, v - 14) for v in cuir[:3]) + (255,)   # ombre avant la tranche
    for y in range(1, 15): p[2, y] = cuir_s; p[3, y] = cuir_s          # dos
    for x in range(4, 13): p[x, 1] = cuir_c                            # reflet haut
    for y in range(1, 15): p[13, y] = PAGE[0] if y % 3 else PAGE[1]    # tranche des pages
    p[12, 1] = PAGE[1]; p[12, 14] = PAGE[1]
    # coins de laiton
    for (x, y) in ((3, 1), (3, 14), (12, 1), (12, 14)): p[x, y] = LA[2]
    p[4, 1] = LA[1]; p[3, 2] = LA[1]; p[4, 14] = LA[1]; p[3, 13] = LA[1]
    # nervures du dos
    for y in (4, 8, 11): p[2, y] = LA[1]; p[3, y] = LA[2]
    embleme(p)
    ruban(p)
    return im
def rouage_oeil(p):      # A : rouage de laiton avec un œil (le regard de l'ingénieur)
    for (x, y) in ((7, 4), (8, 4), (9, 4), (5, 6), (11, 6), (5, 9), (11, 9), (7, 11), (8, 11), (9, 11), (6, 5), (10, 5), (6, 10), (10, 10), (5, 7), (5, 8), (11, 7), (11, 8)):
        p[x, y] = LA[2]
    for (x, y) in ((6, 6), (7, 5), (8, 5), (9, 5), (10, 6), (6, 9), (7, 10), (8, 10), (9, 10), (10, 9), (6, 7), (6, 8), (10, 7), (10, 8)):
        p[x, y] = LA[1]
    for (x, y) in ((7, 6), (8, 6), (9, 6), (7, 9), (8, 9), (9, 9)): p[x, y] = LA[3]
    p[7, 7] = (230, 225, 200, 255); p[9, 7] = (230, 225, 200, 255); p[7, 8] = (230, 225, 200, 255); p[9, 8] = (230, 225, 200, 255)
    p[8, 7] = (160, 30, 24, 255); p[8, 8] = (90, 18, 14, 255)
def trois(p):            # B : les trois emblèmes en triangle, dans un cadre de laiton
    for x in range(5, 12): p[x, 3] = LA[1]; p[x, 12] = LA[1]
    for y in range(3, 13): p[5, y] = LA[1]; p[11, y] = LA[1]
    for (x, y) in ((7, 5), (8, 5), (9, 5), (7, 6), (9, 6), (8, 6)): p[x, y] = (220, 175, 60, 255)   # rouage d'or
    p[8, 6] = (160, 30, 24, 255)
    for (x, y) in ((6, 9), (7, 8), (7, 9), (7, 10), (8, 9)): p[x, y] = (155, 100, 210, 255)        # cristal
    p[7, 8] = (200, 160, 240, 255)
    for (x, y) in ((9, 8), (10, 9), (9, 10), (10, 10)): p[x, y] = (165, 30, 28, 255)                 # rouage brisé
    p[10, 8] = (240, 220, 200, 255)
def fermoir(p):          # C : rouage à couronne et sangle à boucle
    for (x, y) in ((6, 6), (7, 5), (8, 5), (9, 6), (6, 8), (9, 8), (7, 9), (8, 9), (5, 7), (10, 7)):
        p[x, y] = LA[2]
    for (x, y) in ((7, 6), (8, 6), (6, 7), (9, 7), (7, 8), (8, 8)): p[x, y] = LA[1]
    p[7, 7] = (160, 30, 24, 255); p[8, 7] = (160, 30, 24, 255)
    for (x, y) in ((6, 3), (7, 2), (8, 3), (9, 2), (10, 3)): p[x, y] = LA[3]                       # couronne
    for x in range(6, 11): p[x, 4] = LA[2]
    for x in range(11, 15): p[x, 11] = (70, 44, 26, 255); p[x, 12] = (50, 30, 18, 255)            # sangle
    p[12, 11] = LA[3]; p[12, 12] = LA[2]; p[13, 11] = LA[2]
def ruban_rouge(p): p[10, 15] = (160, 30, 24, 255); p[10, 14] = (190, 40, 30, 255)
def sans(p): pass
V = {"A": livre((46, 52, 48, 255), (30, 34, 32, 255), (66, 74, 68, 255), rouage_oeil, ruban_rouge),
     "B": livre((40, 30, 24, 255), (26, 18, 14, 255), (60, 46, 36, 255), trois, ruban_rouge),
     "C": livre((24, 40, 58, 255), (14, 26, 40, 255), (40, 62, 86, 255), fermoir, sans)}
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
out = Image.new("RGBA", (4 * 220, 250), (32, 33, 38, 255)); d = ImageDraw.Draw(out)
for i, (k, im) in enumerate([("Registre", REG)] + list(V.items())):
    out.alpha_composite(im.resize((192, 192), Image.NEAREST), (i * 220 + 14, 40))
    d.text((i * 220 + 14, 8), k if k == "Registre" else "Codex " + k, font=F, fill=(240, 210, 140))
    if k != "Registre": im.save("codex_%s.png" % k)
out.save("/home/claude/apercus/codex_icones.png")
