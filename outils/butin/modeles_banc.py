import json, os, copy
from PIL import Image
C = "create-src/src/main/resources/assets/create/models/block/millstone/"
R = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/"
mill = json.load(open(C + "block.json")); inner = json.load(open(C + "inner.json"))
cadre = mill["elements"][:5]                               # le socle de la meule de Create
def boite(f, t, tex, uv=None, faces="nsewud", rot=None):
    noms = {"n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down"}
    e = {"from": f, "to": t, "faces": {noms[c]: {"uv": uv or [0, 0, 16, 16], "texture": tex} for c in faces}}
    if rot: e["rotation"] = rot
    return e
haut = [
    boite([2, 12, 2], [14, 16, 14], "#cuivre", [2, 0, 14, 4], "nsew"),
    {"from": [2, 12, 2], "to": [14, 16, 14], "faces": {"up": {"uv": [2, 2, 14, 14], "texture": "#plan"}, "down": {"uv": [2, 2, 14, 14], "texture": "#cuivre"}}},
    boite([3, 12.75, 1.9], [13, 15.25, 1.95], "#fond", [0, 0, 10, 2.5], "n"),              # fond gradué de la jauge
    boite([3, 12.75, 1.25], [13, 15.25, 2], "#verre", [3, 1, 13, 3.5]),                    # jauge d'huile
    boite([2.5, 12.5, 1], [3.25, 15.5, 2], "#laiton", [0, 0, 1, 3]),
    boite([12.75, 12.5, 1], [13.5, 15.5, 2], "#laiton", [0, 0, 1, 3]),
    boite([3, 16, 10], [4.5, 21.5, 12], "#laiton", [0, 0, 2, 6]),                          # montants de la meule
    boite([11.5, 16, 10], [13, 21.5, 12], "#laiton", [0, 0, 2, 6]),
]
textures = {"particle": "create:block/millstone", "0": "create:block/gearbox", "5": "create:block/millstone",
            "cuivre": "airain:block/banc_cuivre", "plan": "airain:block/banc_plan", "verre": "minecraft:block/glass",
            "laiton": "airain:block/banc_laiton", "fond": "airain:block/jauge_fond"}
bloc = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout", "textures": textures, "elements": cadre + haut}
def carre(angle):
    e = {"from": [7, 16.5, 7], "to": [9, 24.5, 15], "faces": {
        "east": {"uv": [4, 4, 12, 12], "texture": "#disque"}, "west": {"uv": [4, 4, 12, 12], "texture": "#disque"},
        "north": {"uv": [0, 0, 2, 8], "texture": "#tranche"}, "south": {"uv": [0, 0, 2, 8], "texture": "#tranche"},
        "up": {"uv": [0, 0, 2, 8], "texture": "#tranche"}, "down": {"uv": [0, 0, 2, 8], "texture": "#tranche"}}}
    if angle: e["rotation"] = {"angle": angle, "axis": "x", "origin": [8, 20.5, 11]}
    return e
meule_el = [carre(a) for a in (0, 22.5, 45, -22.5)] + [
    boite([6.5, 19.5, 10], [9.5, 21.5, 12], "#pivot", [0, 0, 3, 2]),     # moyeu
    boite([4.5, 20, 10.5], [11.5, 21, 11.5], "#pivot", [0, 0, 7, 1]),    # axe
]
meule = {"parent": "minecraft:block/block", "textures": {"particle": "airain:block/meule_pierre", "disque": "airain:block/meule_pierre",
         "tranche": "airain:block/meule_tranche", "pivot": "airain:block/banc_laiton"}, "elements": meule_el}
huile = {"parent": "minecraft:block/block", "textures": {"particle": "airain:block/huile_jauge", "huile": "airain:block/huile_jauge"},
         "elements": [boite([3.25, 13, 1.4], [12.75, 15, 1.95], "#huile", [0, 0, 16, 4])]}
objet = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout",
         "textures": dict(textures, **{k: v for k, v in inner["textures"].items() if k != "particle"}, **meule["textures"]),
         "elements": cadre + haut + inner["elements"] + meule_el,
         "display": {"gui": {"rotation": [30, 225, 0], "scale": [0.55, 0.55, 0.55], "translation": [0, -1.5, 0]},
                     "ground": {"scale": [0.25, 0.25, 0.25]}, "fixed": {"scale": [0.45, 0.45, 0.45]},
                     "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.35, 0.35, 0.35]},
                     "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.38, 0.38, 0.38]}}}
os.makedirs(R + "models/block/banc_entretien", exist_ok=True)
for n, m in (("block", bloc), ("meule", meule), ("huile", huile)): json.dump(m, open(R + f"models/block/banc_entretien/{n}.json", "w"), indent=1)
json.dump(objet, open(R + "models/item/banc_entretien.json", "w"), indent=1)
for old in ("models/block/banc_entretien.json",):
    if os.path.exists(R + old): os.remove(R + old)
bs = {"variants": {f"facing={f}": {"model": "airain:block/banc_entretien/block", **({"y": y} if y else {})} for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}}
json.dump(bs, open(R + "blockstates/banc_entretien.json", "w"), indent=1)

# textures
TX = R + "textures/block/"
for f in ("banc_axe.png", "banc_face.png", "banc_dessus.png", "banc_dessous.png"):
    if os.path.exists(TX + f): os.remove(TX + f)
CU = [(92, 50, 30), (140, 76, 44), (184, 104, 62), (214, 140, 88), (236, 178, 122)]
FE = [(40, 40, 46), (66, 66, 74), (98, 98, 106), (138, 138, 146), (182, 182, 188)]
LA = [(110, 80, 30), (170, 128, 50), (214, 172, 80), (240, 210, 130)]
def tex(f):
    im = Image.new("RGBA", (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16): px[x, y] = f(x, y) + (255,)
    return im
tex(lambda x, y: CU[4] if y == 0 else CU[0] if y == 15 else (CU[3] if (x in (1, 14) and y in (1, 3)) else CU[2] if (x + y * 3) % 7 else CU[1])).save(TX + "banc_cuivre.png")
def plan(x, y):
    if x in (2, 13) or y in (2, 13): return FE[3]
    if 2 < x < 13 and 2 < y < 13: return FE[2] if (x // 3 + y // 3) % 2 else FE[1]
    return CU[2]
tex(plan).save(TX + "banc_plan.png")
tex(lambda x, y: LA[3] if x == 0 else LA[0] if x >= 1 and y % 4 == 3 else LA[2] if (x + y) % 3 else LA[1]).save(TX + "banc_laiton.png")
tex(lambda x, y: (196, 130, 40) if y % 4 == 0 else (150, 96, 26) if y % 4 == 1 else (120, 74, 20)).save(TX + "huile_jauge.png")
import random
rnd = random.Random(3)
tex(lambda x, y: tuple(int(c) for c in [118 + rnd.randint(-16, 16)] * 3)).save(TX + "meule_pierre.png")
tex(lambda x, y: (84, 82, 80) if (x + y) % 3 else (64, 62, 60)).save(TX + "meule_tranche.png")
tex(lambda x, y: (230, 220, 190) if (x % 2 == 0 and y < 3 and x < 10) else (34, 30, 28)).save(TX + "jauge_fond.png")
print("ok")
