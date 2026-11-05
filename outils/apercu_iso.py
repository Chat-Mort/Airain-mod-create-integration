#!/usr/bin/env python3
"""Vue isométrique d'une structure posée sur un terrain d'herbe, sous deux angles. usage: json titre sortie.png"""
import json, sys
from PIL import Image, ImageDraw, ImageFont
d = json.load(open(sys.argv[1])); titre = sys.argv[2]
SX, SY, SZ = d["size"]
B = {tuple(map(int, k.split(","))): v for k, v in d["blocks"].items()}
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TABLE = [("white_sail", (235, 232, 220)), ("windmill_bearing", (150, 115, 70)), ("water_wheel", (140, 100, 60)), ("millstone", (150, 150, 145)), ("hopper", (70, 70, 75)), ("chest", (170, 120, 50)), ("stone_brick_wall", (125, 125, 125)), ("stone_bricks", (125, 125, 125)), ("oak_wall_sign", (160, 120, 70)), ("wall_sign", (160, 120, 70)), ("red_wool", (170, 40, 36)), ("dark_oak_planks", (66, 44, 22)), ("dark_oak_fence", (60, 40, 20)), ("stripped_dark_oak", (90, 66, 40)), ("dark_oak", (60, 40, 20)), ("spruce_trapdoor", (110, 80, 50)), ("barrel", (120, 85, 50)), ("polished_blackstone", (50, 46, 52)), ("blackstone", (50, 46, 52)), ("ladder", (130, 100, 60)), ("polished_andesite", (150, 150, 145)), ("andesite", (135, 135, 130)), ("cobblestone", (115, 115, 115)), ("copper_ore", (140, 120, 105)),
 ("brass_casing", (190, 140, 60)), ("brass_block", (222, 172, 72)), ("light_gray_wool", (180, 180, 180)), ("white_wool", (236, 236, 236)),
 ("hanging_roots", (140, 100, 70)), ("rooted_dirt", (125, 92, 62)), ("glass_pane", (170, 205, 215)), ("tinted_glass", (60, 50, 75)),
 ("bookshelf", (125, 85, 50)), ("spruce_planks", (115, 85, 52)), ("spruce_fence", (105, 78, 48)), ("lectern", (150, 108, 64)),
 ("spruce_stairs", (115, 85, 52)), ("lantern", (235, 195, 95)), ("dandelion", (230, 210, 60)), ("stone", (125, 125, 125)), ("fern", (90, 130, 60)),
 ] + [("structure_void", None), ("air", None), ("fluid_pipe", (200, 130, 80)), ("industrial_iron_window", (150, 190, 205)), ("industrial_iron_block", (88, 90, 96)), ("weathered_iron_block", (120, 98, 82)), ("copper_shingle", (95, 140, 115)), ("weathered_cut_copper", (100, 145, 110)), ("weathered_copper", (105, 150, 112)), ("moss_carpet", (95, 125, 50)), ("cobweb", (230, 230, 230)),
 ("lootr_chest", (220, 170, 40)), ("crafting_table", (150, 100, 55)), ("large_cogwheel", (150, 115, 70)), ("cogwheel", (160, 125, 80)),
 ("shaft", (150, 150, 145)), ("andesite_casing", (165, 160, 145)), ("lightning_rod", (90, 150, 130)), ("chain", (70, 75, 85)),
 ("copper_grate", (60, 120, 105)), ("copper_trapdoor", (70, 135, 115)), ("copper_bulb", (80, 140, 120)),
 ("oxidized_cut_copper", (75, 150, 125)), ("oxidized_copper", (85, 165, 140)), ("iron_bars", (160, 160, 165)),
 ("stripped_spruce", (120, 90, 55)), ("spruce_log", (70, 50, 30)), ("spruce_slab", (110, 80, 50)),
 ("mossy_cobblestone", (100, 115, 90)), ("cobbled_deepslate", (75, 75, 80)), ("deepslate_tiles", (55, 55, 62)),
 ("tuff_bricks", (105, 108, 98)), ("tuff_slab", (110, 112, 104)), ("polished_tuff", (120, 124, 115)), ("tuff", (110, 112, 104)),
 ("coarse_dirt", (110, 80, 55)), ("gravel", (125, 118, 112)), ("grass", (110, 140, 70)), ("dirt", (120, 85, 60))]
def couleur(s):
    n = s.split("[")[0].split(":")[1]
    for k, c in TABLE:
        if k in n: return c
    return (200, 0, 200)
def plat(s):
    n = s.split(":")[1]
    return any(k in n for k in ("carpet", "slab", "trapdoor", "rail"))
T = 20
def rendu(rot):
    blocs = {}
    M = 3
    for x in range(-M, SX + M):              # terrain : herbe sous la structure (y = 0 est enterré)
        for z in range(-M, SZ + M):
            blocs[(x, -1, z)] = "minecraft:dirt"
            s = B.get((x, 0, z), "minecraft:structure_void")
            if "structure_void" in s: blocs[(x, 0, z)] = "minecraft:grass_block"
    for p, s in B.items():
        if couleur(s) is not None: blocs[p] = s
    def tr(x, z):
        return (x, z) if rot == 0 else (SZ - 1 - z, x)
    pts = []
    for (x, y, z), s in blocs.items():
        X, Z = tr(x, z); pts.append((X, y, Z, s))
    proj = lambda x, y, z: ((x - z) * T, (x + z) * T / 2 - y * T * 1.15)
    xs = [proj(p[0], p[1], p[2]) for p in pts]
    minx = min(a for a, b in xs) - T; maxx = max(a for a, b in xs) + T
    miny = min(b for a, b in xs) - T; maxy = max(b for a, b in xs) + 3 * T
    im = Image.new("RGB", (int(maxx - minx) + 40, int(maxy - miny) + 40), (30, 31, 36)); dr = ImageDraw.Draw(im)
    ox, oy = -minx + 20, -miny + 20
    pts.sort(key=lambda p: (p[0] + p[2], p[1]))
    for X, y, Z, s in pts:
        c = couleur(s); px, py = proj(X, y, Z); px += ox; py += oy
        h = T * 1.15 * (0.25 if plat(s) else 1)
        top = [(px, py + T * 1.15 - h if plat(s) else py), (px + T, py + T / 2 + (T * 1.15 - h if plat(s) else 0)),
               (px, py + T + (T * 1.15 - h if plat(s) else 0)), (px - T, py + T / 2 + (T * 1.15 - h if plat(s) else 0))]
        dy = (T * 1.15 - h) if plat(s) else 0
        left = [(px - T, py + T / 2 + dy), (px, py + T + dy), (px, py + T + dy + h), (px - T, py + T / 2 + dy + h)]
        right = [(px, py + T + dy), (px + T, py + T / 2 + dy), (px + T, py + T / 2 + dy + h), (px, py + T + dy + h)]
        f = lambda c, k: tuple(int(v * k) for v in c)
        dr.polygon(left, fill=f(c, .62)); dr.polygon(right, fill=f(c, .8)); dr.polygon(top, fill=c)
        if "cobweb" in s or "iron_bars" in s: dr.polygon(top, outline=(120, 120, 120))
    return im
a, b = rendu(0), rendu(1)
W = a.width + b.width + 30; H = max(a.height, b.height) + 70
out = Image.new("RGB", (W, H), (30, 31, 36)); out.paste(a, (10, 60)); out.paste(b, (a.width + 20, 60))
dr = ImageDraw.Draw(out); dr.text((20, 18), titre, font=ImageFont.truetype(FB, 22), fill=(240, 240, 240))
dr.text((20, H - 26), "Deux angles · le reste du terrain n'est pas touché (blocs vides de la structure)", font=ImageFont.truetype(F, 13), fill=(190, 190, 190))
out.save(sys.argv[3])
