import sys, json
sys.argv = [sys.argv[0], "0", "/tmp"]
import apercu_avant_poste as A
from PIL import Image, ImageDraw, ImageFont
P = json.load(open("echo_pieces.json"))
def monde(nom, rot=2):
    d = P[nom]; sx, sy, sz = d["size"]; W = {}
    fin = {(j[0], j[1], j[2]): j[7] for j in d["jigsaws"]}
    for k, s in d["blocks"].items():
        x, y, z = map(int, k.split(","))
        if (x, y, z) in fin: s = fin[(x, y, z)]
        if A.couleur(s) is None: continue
        X, Z = A.rot_xz(x, z, sx, sz, rot); W[(X, y, Z)] = s
    return W
L = [("kubejs:refractaires/sanctuaire", "Le Sanctuaire réfractaire (refuge d'Ada Vesper)", 0), ("kubejs:ruines/grand_relais", "Le Grand Relais (arène du Chœur des Égarés, résonateur au sud)", 2)]
imgs = [(t, A.iso(monde(n, r), 9, marge=1)) for n, t, r in L]
W = sum(i.width for _, i in imgs) + 60; H = max(i.height for _, i in imgs) + 90
sh = Image.new("RGB", (W, H), (30, 31, 36)); d = ImageDraw.Draw(sh)
d.text((20, 16), "La voie de l'Écho · nouvelles structures", font=ImageFont.truetype(A.FB, 24), fill=(240, 240, 240))
x = 20
for t, im in imgs:
    d.text((x + 6, 56), t, font=ImageFont.truetype(A.FB, 15), fill=(250, 220, 140)); sh.paste(im, (x, 80)); x += im.width + 20
sh.save("/home/claude/apercus/echo_structures.png"); print(sh.size)
