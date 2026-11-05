#!/usr/bin/env python3
"""Aperçus du laboratoire : plan de dessus annoté + vue isométrique sans plafond."""
import json, sys
from PIL import Image, ImageDraw, ImageFont

d = json.load(open(sys.argv[1]))
SX, SY, SZ = d["size"]
B = {tuple(map(int, k.split(","))): v for k, v in d["blocks"].items()}
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def couleur(s):
    n = s.split("[")[0].split(":")[1]
    table = [
        ("air", None), ("fluid_pipe", (200, 130, 80)), ("industrial_iron_block", (88, 90, 96)), ("weathered_iron_block", (120, 98, 82)), ("weathered_copper", (105, 150, 112)), ("oxidized_copper", (85, 165, 140)), ("ladder", (150, 110, 60)), ("lectern", (170, 120, 60)), ("lootr_chest", (220, 170, 40)),
        ("crafting_table", (150, 100, 55)), ("furnace", (110, 110, 110)), ("bookshelf", (140, 95, 50)),
        ("creative_vendor", (230, 200, 70)), ("bank_terminal", (120, 200, 120)), ("wall_sign", (190, 150, 90)), ("cobweb", (235, 235, 235)),
        ("glass", (190, 225, 235)), ("iron_bars", (160, 160, 165)), ("soul_lantern", (90, 210, 220)),
        ("lantern", (255, 200, 90)), ("chain", (80, 85, 95)), ("copper_bulb", (255, 190, 90)),
        ("oxidized_copper_grate", (80, 160, 140)), ("weathered_copper_grate", (100, 150, 120)),
        ("cut_copper", (190, 120, 80)), ("deepslate_tiles", (55, 55, 62)), ("deepslate_bricks", (65, 65, 72)),
        ("cobbled_deepslate", (75, 75, 80)), ("tuff_bricks", (105, 108, 98)), ("polished_tuff", (120, 124, 115)),
        ("tuff", (110, 112, 104)), ("polished_andesite", (140, 142, 140)), ("andesite", (130, 130, 128)),
        ("gravel", (125, 118, 112)),
    ]
    for k, c in table:
        if k in n:
            return c
    return (200, 0, 200)

# ---------------------------------------------------------------- plan de dessus
C = 34
W, H = SX * C + 80, SZ * C + 150
im = Image.new("RGB", (W, H), (30, 31, 36)); dr = ImageDraw.Draw(im)
ox, oy = 40, 70
for x in range(SX):
    for z in range(SZ):
        # bloc le plus marquant entre y=1 et y=3 (sinon le sol)
        s = None
        for y in (1, 2, 3):
            v = B.get((x, y, z), "minecraft:air")
            if "air" not in v.split(":")[1]:
                s = v; break
        if s is None:
            s = B[(x, 0, z)]
        c = couleur(s)
        dr.rectangle([ox + x * C, oy + z * C, ox + x * C + C - 1, oy + z * C + C - 1], fill=c)
        if "cobweb" in s:
            dr.line([ox + x * C + 4, oy + z * C + 4, ox + x * C + C - 5, oy + z * C + C - 5], fill=(170, 170, 170))
            dr.line([ox + x * C + C - 5, oy + z * C + 4, ox + x * C + 4, oy + z * C + C - 5], fill=(170, 170, 170))
fT, fL, fS = ImageFont.truetype(FB, 22), ImageFont.truetype(FB, 15), ImageFont.truetype(F, 13)
dr.text((ox, 20), "Laboratoire 7 · plan (hauteur des yeux)", font=fT, fill=(240, 240, 240))
def label(x, z, t, sub=None):
    tw = dr.textlength(t, font=fL)
    dr.rectangle([ox + x * C - tw / 2 - 6, oy + z * C - 12, ox + x * C + tw / 2 + 6, oy + z * C + (26 if sub else 10)], fill=(20, 20, 24))
    dr.text((ox + x * C - tw / 2, oy + z * C - 10), t, font=fL, fill=(250, 220, 140))
    if sub:
        sw = dr.textlength(sub, font=fS); dr.text((ox + x * C - sw / 2, oy + z * C + 8), sub, font=fS, fill=(210, 210, 210))
label(4.5, 5.6, "Salle de réveil", "2 capsules (spawn)")
label(4.5, 12.6, "Capsules vides", "porte entrouverte")
label(17.5, 5.6, "Bureau", "pupitre, coffre Lootr")
label(17.5, 12.2, "Comptoir", "8 distributeurs + banque")
label(11.5, 1.6, "Couloir")
label(11.5, 14.0, "Sortie", "échelle")
leg = [("capsule", (80, 160, 140)), ("verre", (190, 225, 235)), ("pupitre", (170, 120, 60)), ("coffre", (220, 170, 40)),
       ("distributeur", (230, 200, 70)), ("banque", (120, 200, 120)), ("bibliothèque", (140, 95, 50)), ("toile", (235, 235, 235)), ("échelle", (150, 110, 60))]
lx = ox
for t, c in leg:
    dr.rectangle([lx, H - 52, lx + 16, H - 36], fill=c); dr.text((lx + 22, H - 53), t, font=fS, fill=(220, 220, 220))
    lx += 26 + dr.textlength(t, font=fS) + 18
im.save(sys.argv[2])

# ---------------------------------------------------------------- vue isométrique, plafond retiré
T = 22                          # demi-largeur d'un losange
def proj(x, y, z):
    return ((x - z) * T, (x + z) * T / 2 - y * T * 1.15)
xs = [proj(x, y, z) for x in (0, SX) for y in (0, SY) for z in (0, SZ)]
minx, maxx = min(p[0] for p in xs), max(p[0] for p in xs)
miny, maxy = min(p[1] for p in xs), max(p[1] for p in xs)
W2, H2 = int(maxx - minx + 2 * T + 60), int(maxy - miny + 2 * T + 90)
iso = Image.new("RGB", (W2, H2), (30, 31, 36)); di = ImageDraw.Draw(iso)
offx, offy = -minx + T + 30, -miny + T + 60
def ombre(c, f): return tuple(int(v * f) for v in c)
blocs = [(p, s) for p, s in B.items() if p[1] < SY - 1 and "air" not in s.split(":")[1]]
# murs extérieurs côté spectateur abaissés à 1 bloc pour voir l'intérieur
MURS = ("deepslate", "tuff", "andesite", "gravel")
def garde(p, s):
    x, y, z = p
    if (x == SX - 1 or z == SZ - 1) and y > 1: return False      # murs côté spectateur : 1 bloc
    if y >= 3 and any(m in s for m in MURS): return False         # murs coupés à 2 blocs
    if "cobweb" in s or "chain" in s: return False
    return True
blocs = [(p, s) for p, s in blocs if garde(p, s)]
blocs.sort(key=lambda ps: (ps[0][0] + ps[0][2], ps[0][1]))
for (x, y, z), s in blocs:
    c = couleur(s)
    if c is None: continue
    px, py = proj(x, y, z); px += offx; py += offy
    h = T * 1.15
    top = [(px, py), (px + T, py + T / 2), (px, py + T), (px - T, py + T / 2)]
    left = [(px - T, py + T / 2), (px, py + T), (px, py + T + h), (px - T, py + T / 2 + h)]
    right = [(px, py + T), (px + T, py + T / 2), (px + T, py + T / 2 + h), (px, py + T + h)]
    di.polygon(left, fill=ombre(c, 0.62)); di.polygon(right, fill=ombre(c, 0.8)); di.polygon(top, fill=c)
    if "cobweb" in s or "glass" in s:
        di.polygon(top, outline=ombre(c, 0.7))
di.text((30, 18), "Laboratoire 7 · maquette (murs coupés à mi-hauteur)", font=fT, fill=(240, 240, 240))
iso.save(sys.argv[3])
