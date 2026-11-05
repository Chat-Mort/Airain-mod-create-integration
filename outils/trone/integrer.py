import json, math, random
from PIL import Image
M = '/home/claude/airain-mod-create-integration/src/main/resources'
A = M + '/assets/airain'
random.seed(5)

class Modele:
    def __init__(s, nom, couleurs):
        s.nom, s.couleurs, s.el = nom, couleurs, []
    def b(s, x0, y0, z0, x1, y1, z1, c, lum=False):
        t = s.couleurs.index(c); u, v = (t % 4) * 4, (t // 4) * 4
        f = {"texture": "#t", "uv": [u + 0.5, v + 0.5, u + 3.5, v + 3.5]}
        if lum: f["neoforge_data"] = {"block_light": 15, "sky_light": 15}
        e = {"from": [round(x0, 3), round(y0, 3), round(z0, 3)], "to": [round(x1, 3), round(y1, 3), round(z1, 3)],
             "faces": {k: dict(f) for k in ("north", "south", "east", "west", "up", "down")}}
        if lum: e["shade"] = False
        s.el.append(e)
    def disque_xy(s, cx, cy, z0, z1, r0, r1, c, lum=False):   # anneau dans le plan vertical, en bandes d'un pixel
        y = math.floor(cy - r1)
        while y < cy + r1:
            yc = y + 0.5 - cy
            xs = [x for x in [i * 0.5 for i in range(int((cx - r1 - 1) * 2), int((cx + r1 + 1) * 2))] if r0 <= math.hypot(x + 0.25 - cx, yc) <= r1]
            for run in runs(xs, 0.5): s.b(run[0], y, z0, run[1] + 0.5, y + 1, z1, c, lum)
            y += 1
    def disque_xz(s, cx, cz, y0, y1, r, c):
        z = math.floor(cz - r)
        while z < cz + r:
            zc = z + 0.5 - cz
            if abs(zc) <= r:
                w = math.sqrt(max(0, r * r - zc * zc)); s.b(max(0, cx - w), y0, z, min(16, cx + w), y1, z + 1, c)
            z += 1
    def ecrire(s):
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        for i, c in enumerate(s.couleurs):
            u, v = (i % 4) * 4, (i // 4) * 4
            for x in range(4):
                for y in range(4):
                    n = random.randint(-7, 7) if len(c) == 3 else 0
                    img.putpixel((u + x, v + y), tuple(max(0, min(255, k + n)) for k in c[:3]) + (255,))
        img.save(f'{A}/textures/block/{s.nom}.png')
        m = {"parent": "minecraft:block/block", "ambientocclusion": False, "textures": {"t": f"airain:block/{s.nom}", "particle": f"airain:block/{s.nom}"},
             "elements": s.el,
             "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, -3.5, 0], "scale": [0.42, 0.42, 0.42]},
                         "ground": {"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.25, 0.25, 0.25]},
                         "fixed": {"rotation": [0, 0, 0], "translation": [0, -2, 0], "scale": [0.45, 0.45, 0.45]},
                         "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.3, 0.3, 0.3]},
                         "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 0, 0], "scale": [0.3, 0.3, 0.3]},
                         "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.3, 0.3, 0.3]}}}
        json.dump(m, open(f'{A}/models/block/{s.nom}.json', 'w'), indent=1)
        json.dump({"parent": f"airain:block/{s.nom}"}, open(f'{A}/models/item/{s.nom}.json', 'w'))
        json.dump({"variants": {f"facing={f}": {"model": f"airain:block/{s.nom}", "y": y} for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}},
                  open(f'{A}/blockstates/{s.nom}.json', 'w'), indent=1)
        json.dump({"type": "minecraft:block", "pools": [{"rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"airain:{s.nom}"}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}]}, open(f'{M}/data/airain/loot_table/blocks/{s.nom}.json', 'w'), indent=1)
        print(s.nom, len(s.el), 'éléments')

def runs(xs, pas):
    xs = sorted(set(xs)); out = []
    for x in xs:
        if out and abs(x - out[-1][1] - pas) < 1e-6: out[-1][1] = x
        else: out.append([x, x])
    return out

WH, GOLD, GOLD2, RED, RED2, NETH, STAR = (238, 236, 226), (235, 195, 75), (185, 140, 40), (150, 25, 32), (115, 15, 22), (50, 45, 50), (255, 240, 170, 1)
t = Modele('trone_imperial', [WH, GOLD, GOLD2, RED, RED2, NETH, STAR])
t.b(0, 0, 0, 16, 1.5, 16, NETH); t.b(0, 1.5, 0, 16, 2, 16, GOLD2)
t.b(2, 2, 3, 14, 7, 14, WH); t.b(2, 2, 2.5, 3, 7, 3, GOLD); t.b(13, 2, 2.5, 14, 7, 3, GOLD); t.b(3, 6, 2.5, 13, 7, 3, GOLD)
t.b(3, 7, 2, 13, 9, 13, RED); t.b(3, 8.5, 1.9, 13, 9, 2, RED2)
for x0 in (1, 13):
    t.b(x0, 7, 2, x0 + 2, 12, 13, WH); t.b(x0, 12, 1.5, x0 + 2, 13, 13, GOLD); t.b(x0, 7, 1.5, x0 + 2, 12, 2, GOLD2)
t.b(2, 9, 13, 14, 26, 15, WH); t.b(4, 10, 12.5, 12, 25, 13, RED)
t.b(2, 26, 12.5, 14, 27, 15.5, GOLD); t.b(2, 9, 12.5, 3, 26, 13, GOLD); t.b(13, 9, 12.5, 14, 26, 13, GOLD)
for x in (2, 12.5):
    t.b(x, 27, 13, x + 1.5, 30, 14.5, GOLD); t.b(x + 0.25, 30, 13.25, x + 1.25, 31, 14.25, STAR, True)
t.disque_xy(8, 29.5, 13, 14.5, 2.2, 3.6, GOLD)
for k in range(8):
    a = k * math.pi / 4; cx, cy = 8 + math.cos(a) * 4, 29.5 + math.sin(a) * 4
    if cy + 0.5 <= 32: t.b(cx - 0.5, cy - 0.5, 13, cx + 0.5, cy + 0.5, 14.5, GOLD)
t.b(7, 28.5, 12.5, 9, 30.5, 13.5, STAR, True); t.b(7.5, 27.5, 12.75, 8.5, 31.5, 13.25, STAR, True); t.b(6, 29, 12.75, 10, 30, 13.25, STAR, True)
t.ecrire()

NOIR, NOIR2, VIO, VIO2, LAV, PALE = (22, 18, 32), (42, 34, 60), (95, 58, 155), (62, 32, 102), (186, 156, 255, 1), (232, 218, 255, 1)
s = Modele('solium', [NOIR, NOIR2, VIO, VIO2, LAV, PALE])
s.disque_xz(8, 8, 0, 1.8, 8, VIO); s.disque_xz(8, 8, 0, 2, 7.4, NOIR2)
for k in range(10):
    a = k * math.pi / 5; x, z = 8 + math.cos(a) * 6.6, 8 + math.sin(a) * 6.6
    s.b(x - 0.4, 2, z - 0.4, x + 0.4, 2.1, z + 0.4, LAV, True)
s.b(3, 2, 3, 13, 7, 13, NOIR); s.b(3, 6.5, 2.5, 13, 7, 3, VIO); s.b(3, 7, 3, 13, 8.5, 13, VIO)
for x0 in (2, 12):
    s.b(x0, 7, 3, x0 + 2, 10, 12, NOIR); s.b(x0 + 0.5, 10, 3, x0 + 1.5, 12, 4, LAV, True); s.b(x0 + 0.75, 12, 3.25, x0 + 1.25, 13, 3.75, PALE, True)
s.b(3, 8, 12, 5, 22, 14, NOIR); s.b(11, 8, 12, 13, 22, 14, NOIR); s.b(5, 9, 13, 11, 19, 14, VIO2)
s.b(3.5, 22, 12.5, 4.5, 24, 13.5, LAV, True); s.b(11.5, 22, 12.5, 12.5, 24, 13.5, LAV, True)
s.disque_xy(8, 22, 13, 14, 5.2, 6.2, PALE, True)
s.b(7, 21, 12.5, 9, 23, 13.5, LAV, True); s.b(7.5, 21.5, 12.2, 8.5, 22.5, 12.5, PALE, True)
for (x, y) in ((-1.5, 14), (17.5, 16)):
    s.b(x - 0.5, y, 7.5, x + 0.5, y + 2.5, 8.5, LAV, True); s.b(x - 0.25, y + 2.5, 7.75, x + 0.25, y + 3, 8.25, PALE, True)
s.ecrire()
