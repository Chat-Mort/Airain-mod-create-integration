import json, sys
sys.path.insert(0, "butin")
from rendu_modele import *
M = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/"
inner = json.load(open("create-src/src/main/resources/assets/create/models/block/millstone/inner.json"))
face_sud = lambda p: (16 - p[0], p[1], 16 - p[2])
W, H = 1900, 1000; im = Image.new("RGBA", (W, H), (44, 46, 52, 255)); d = ImageDraw.Draw(im)
L = quads(json.load(open(M + "table_enchantement.json")), face_sud)
dessiner(d, L, 26, 480, 700)
L = quads(json.load(open(M + "desenchanteur/block.json")), face_sud)
L += quads(inner, lambda p: face_sud(rot(p, {"angle": 10, "axis": "y", "origin": [8, 8, 8]})))
L += quads(json.load(open(M + "desenchanteur/cristal.json")), lambda p: face_sud(rot(p, {"angle": 20, "axis": "y", "origin": [8, 8, 11]})))
L += quads(json.load(open(M + "banc_entretien/huile.json")), lambda p: face_sud((3.25 + (p[0] - 3.25) * 0.5, p[1], p[2])))
dessiner(d, L, 26, 1400, 760)
im.crop((60, 160, 1840, 1000)).save("/home/claude/apercus/enchant_blocs.png")
