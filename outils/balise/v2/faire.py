import json, os, random
from PIL import Image
OUT = os.path.dirname(os.path.abspath(__file__))
random.seed(7)
def img(): return Image.new("RGBA", (16, 16), (0, 0, 0, 0))
def bruit(c, a=6):
    d = random.randint(-a, a); return tuple(max(0, min(255, v + d)) for v in c[:3]) + (255,)

# palettes
FONTE = [(34, 32, 38), (46, 44, 52), (58, 56, 64), (74, 72, 80)]
LAI = {"sombre": (128, 84, 30), "bas": (176, 120, 44), "moy": (214, 160, 64), "haut": (240, 196, 104), "eclat": (255, 232, 160)}
CUI = {"sombre": (110, 52, 32), "moy": (176, 92, 56), "haut": (220, 132, 88)}
ROUGE = {"sombre": (110, 10, 10), "bas": (170, 24, 18), "moy": (225, 48, 30), "haut": (255, 110, 70), "coeur": (255, 210, 170)}

# ---- socle (fonte) : côté [0,0,14,2], dessus [0,2,14,16] (14 x 14)
s = img(); p = s.load()
for x in range(14):
    p[x, 0] = bruit(FONTE[3]); p[x, 1] = bruit(FONTE[1])
for x in range(14):
    for y in range(2, 16):
        bord = x in (0, 13) or y in (2, 15)
        p[x, y] = bruit(FONTE[2] if bord else FONTE[1], 4)
for (bx, by) in ((1, 3), (12, 3), (1, 14), (12, 14)):          # boulons
    p[bx, by] = (150, 140, 120, 255)
s.save(f"{OUT}/balise_socle.png")

# ---- corps (laiton) : côté [0,0,10,6], dessus [0,6,10,16]
c = img(); p = c.load()
for x in range(10):
    for y in range(6):
        col = LAI["moy"]
        if y == 0: col = LAI["haut"]
        if y == 5: col = LAI["bas"]
        if x in (0, 9): col = LAI["bas"] if y else LAI["moy"]
        p[x, y] = bruit(col, 5)
for (rx, ry) in ((1, 1), (8, 1), (1, 4), (8, 4)): p[rx, ry] = LAI["eclat"] + (255,)          # rivets
# cadran : 4 x 4 au centre (anneau sombre, fond crème, aiguille rouge)
CAD = ["BDDB", "DWRD", "DWWD", "BDDB"]
for yy, ligne in enumerate(CAD):
    for xx, ch in enumerate(ligne):
        if ch == "B": continue
        p[3 + xx, 1 + yy] = {"D": LAI["sombre"], "W": (238, 230, 208), "R": (210, 30, 20)}[ch] + (255,)
for x in range(10):
    for y in range(6, 16):
        bord = x in (0, 9) or y in (6, 15)
        p[x, y] = bruit(LAI["bas"] if bord else LAI["moy"], 5)
for x in range(3, 7):
    for y in range(9, 13):
        p[x, y] = LAI["sombre"] + (255,)                                                       # logement de la tige
for (rx, ry) in ((1, 7), (8, 7), (1, 14), (8, 14)): p[rx, ry] = LAI["eclat"] + (255,)
c.save(f"{OUT}/balise_corps.png")

# ---- col (cuivre) : côté [0,0,4,2], dessus [0,2,4,6]
k = img(); p = k.load()
for y in range(3):
    p[0, y] = CUI["haut"] + (255,); p[1, y] = CUI["moy"] + (255,)
for x in range(2):
    for y in range(3, 5): p[x, y] = CUI["moy"] + (255,)
k.save(f"{OUT}/balise_col.png")

# ---- lampe : côté [0,0,8,5] (cage de laiton, verre rouge) ; dessus/dessous [0,5,8,13] ; chapeau côté [8,0,14,1], dessus [8,1,14,7]
l = img(); p = l.load()
for x in range(6):
    for y in range(5):
        if y in (0, 4) or x in (0, 5):
            col = LAI["haut"] if y == 0 else LAI["bas"] if y == 4 else LAI["moy"]
        else:
            dx = abs(x - 2.5); dy = abs(y - 2)
            col = ROUGE["coeur"] if dx < 1 and dy == 0 else ROUGE["haut"] if dx < 1 or dy == 0 and dx < 2 else ROUGE["moy"]
        p[x, y] = col + (255,)
for x in range(6):
    for y in range(5, 11):
        bord = x in (0, 5) or y in (5, 10)
        p[x, y] = (LAI["bas"] if bord else ROUGE["haut"]) + (255,)
for x in range(8, 12):
    p[x, 0] = LAI["haut"] + (255,)
    for y in range(1, 5):
        bord = x in (8, 11) or y in (1, 4)
        p[x, y] = bruit(LAI["bas"] if bord else LAI["eclat"], 4)
l.save(f"{OUT}/balise_lampe.png")

def faces(tex, cote, dessus, dessous=None, sans_bas=False):
    f = {d: {"texture": tex, "uv": cote} for d in ("north", "south", "east", "west")}
    f["up"] = {"texture": tex, "uv": dessus}
    if not sans_bas: f["down"] = {"texture": tex, "uv": dessous or dessus}
    return f
modele = {"parent": "minecraft:block/block",
  "textures": {"particle": "kubejs:block/balise_corps", "socle": "kubejs:block/balise_socle", "corps": "kubejs:block/balise_corps",
               "col": "kubejs:block/balise_col", "lampe": "kubejs:block/balise_lampe"},
  "elements": [
    {"from": [1, 0, 1], "to": [15, 2, 15], "faces": faces("#socle", [0, 0, 14, 2], [0, 2, 14, 16])},
    {"from": [3, 2, 3], "to": [13, 8, 13], "faces": faces("#corps", [0, 0, 10, 6], [0, 6, 10, 16], sans_bas=True)},
    {"from": [7, 8, 7], "to": [9, 11, 9], "faces": faces("#col", [0, 0, 2, 3], [0, 3, 2, 5], sans_bas=True)},
    {"from": [5, 10.5, 5], "to": [11, 15.5, 11], "faces": faces("#lampe", [0, 0, 6, 5], [0, 5, 6, 11])},
    {"from": [6, 15.5, 6], "to": [10, 16, 10], "faces": faces("#lampe", [8, 0, 12, 0.5], [8, 1, 12, 5], sans_bas=True)}]}
json.dump(modele, open(f"{OUT}/balise_defense_forme.json", "w"), indent=2)
for f in ("balise_socle", "balise_corps", "balise_col", "balise_lampe"):
    Image.open(f"{OUT}/{f}.png").resize((128, 128), Image.NEAREST).save(f"{OUT}/zoom_{f}.png")
