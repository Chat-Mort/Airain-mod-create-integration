import json, math, sys
sys.argv=["x"]
exec(open("concepts.py").read().split("def socle")[0])
from PIL import Image, ImageDraw, ImageFont
G = json.load(open("geo.json"))
COUL = {0: (52, 54, 60), 1: (88, 90, 98), 2: (205, 160, 70), 3: (190, 110, 75), 4: (112, 114, 106), 5: (170, 205, 215), 6: (120, 30, 25),
        7: (230, 225, 200), 8: (40, 30, 22), 9: (85, 165, 140), 10: (92, 94, 88), 11: (150, 108, 40)}
def vox(V, b, col=None, rot=None):
    x0, y0, z0, x1, y1, z1, m = b
    c = col or COUL[int(m)]
    for x in range(int(math.floor(x0)), int(math.ceil(x1))):
        for y in range(int(math.floor(y0)), int(math.ceil(y1))):
            for z in range(int(math.floor(z0)), int(math.ceil(z1))):
                if rot is None: V[(x, y, z)] = c
                else:
                    a = math.radians(rot); X = x + .5; Z = z + .5
                    V[(int(24 + X * math.cos(a) - Z * math.sin(a)), y, int(24 + X * math.sin(a) + Z * math.cos(a)))] = c
def tour(alerte):
    V = {}
    for b in G["B"]: vox(V, b)
    for b in G["S"]: vox(V, b, rot=40 if alerte else 0)
    for b in G["L"]: vox(V, b, (255, 90, 50, 1) if alerte else (110, 30, 25))
    for b in G["V"]:
        x0, y0, z0, x1, y1, z1, m = b
        for y in range(int(y0), int(y1)):
            for x in range(int(x0), int(math.ceil(x1))):
                for z in range(int(z0), int(math.ceil(z1))):
                    if (x, y, z) not in V and (x in (int(x0), int(math.ceil(x1)) - 1) or z in (int(z0), int(math.ceil(z1)) - 1)): V[(x, y, z)] = (170, 205, 215)
    for (sx, sz) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        for i in range(31):
            t = i / 30; d = 20 - t * 11.5
            x, z, y = 24 - sx * d, 24 - sz * d, 6 + 30 * t
            vox(V, (x - 1.5, y, z - 1.5, x + 1.5, y + 1, z + 1.5, 0))
    if alerte:
        for k in range(8, 70):
            w = 3 + k * 11 / 73
            for q in range(int(-w), int(w)):
                V[(int(24 + k), int(94 + q * 0.6), int(24 + q * 0.3))] = (255, 120, 80, 1)
                V[(int(24 - k), int(94 + q * 0.6), int(24 - q * 0.3))] = (255, 120, 80, 1)
    return V
a = rendu(tour(False), 4); b = rendu(tour(True), 4)
im = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height) + 40), (32, 33, 38)); d = ImageDraw.Draw(im)
im.paste(a, (0, 40 + max(a.height, b.height) - a.height)); im.paste(b, (a.width + 20, 40))
d.text((10, 8), "Balise de défense : géométrie réelle du mod (au repos / en alerte)", font=ImageFont.truetype(FB, 17), fill=(240, 210, 140))
im.save("/home/claude/apercus/balise_geo_reelle.png"); print(im.size)
