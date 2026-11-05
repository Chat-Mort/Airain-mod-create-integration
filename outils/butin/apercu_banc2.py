import json, math, sys
sys.path.insert(0, "butin")
from rendu_modele import *
M = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/banc_entretien/"
bloc = json.load(open(M + "block.json")); meule = json.load(open(M + "meule.json")); huile = json.load(open(M + "huile.json"))
inner = json.load(open("create-src/src/main/resources/assets/create/models/block/millstone/inner.json"))
def rendu(angle_rouage, angle_meule, plein, nom):
    W, H = 1100, 1300; im = Image.new("RGBA", (W, H), (44, 46, 52, 255)); d = ImageDraw.Draw(im)
    face_sud = lambda p: (16 - p[0], p[1], 16 - p[2])          # façade tournée vers nous
    L = quads(bloc, face_sud)
    L += quads(inner, lambda p: face_sud(rot(p, {"angle": angle_rouage, "axis": "y", "origin": [8, 8, 8]})))
    L += quads(meule, lambda p: face_sud(rot(p, {"angle": angle_meule, "axis": "x", "origin": [8, 20.5, 11]})))
    if plein > 0:
        L += quads(huile, lambda p: face_sud((3.25 + (p[0] - 3.25) * plein, p[1], p[2])))
    for tex, cx, cz in (("minecraft:item/iron_pickaxe", 0.33, 0.3), ("minecraft:item/iron_ingot", 0.68, 0.3)):
        x0, z0 = cx * 16 - 2.6, cz * 16 - 2.6
        L += quads({"textures": {"t": tex}, "elements": [{"from": [x0, 16.4, z0], "to": [x0 + 5.2, 16.45, z0 + 5.2], "faces": {"up": {"uv": [0, 0, 16, 16], "texture": "#t"}}}]}, face_sud)
    # rouage voisin de Create (pour montrer l'entraînement) : petit rouage à l'ouest
    dessiner(d, L, 26, W / 2, H / 2 + 260)
    im.crop((120, 120, 980, 1240)).save(nom)
rendu(10, 15, 0.62, "/home/claude/apercus/banc_v2.png")
