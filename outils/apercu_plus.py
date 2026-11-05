"""Planche des structures « plus » : camps réfractaires, étal, station (coupe), ruines."""
import sys, json
sys.argv = [sys.argv[0], "0", "/tmp"]
import apercu_avant_poste as A
from PIL import Image, ImageDraw, ImageFont
P = json.load(open("plus_pieces.json"))
def monde(nom, rot=2, coupe=None, sous_sol=False):
    d = P[nom]; sx, sy, sz = d["size"]; W = {}
    fin = {(j[0], j[1], j[2]): j[7] for j in d["jigsaws"]}
    for k, s in d["blocks"].items():
        x, y, z = map(int, k.split(","))
        if (x, y, z) in fin: s = fin[(x, y, z)]
        if A.couleur(s) is None: continue
        if coupe and coupe(x, y, z): continue
        X, Z = A.rot_xz(x, z, sx, sz, rot)
        W[(X, y, Z)] = s
    return W
LISTE = [("kubejs:refractaires/camp_a", "Camp réfractaire (A)", {}), ("kubejs:refractaires/camp_b", "Camp réfractaire (B)", {}),
         ("kubejs:refractaires/etal_fiole", "Étal de fiole funeste (1 camp sur 3)", {}),
         ("kubejs:refractaires/etal_echo", "Étal d'Écho (dans chaque camp)", {}),
         ("kubejs:ruines/relais_brise", "Relais brisé (l'Écho s'en échappe)", {}),
         ("kubejs:station/station_capsules", "Station de capsules (toit retiré)", {"coupe": lambda x, y, z: y >= 18}),
         ("kubejs:station/station_capsules", "Station · sous-sol (le collecteur)", {"coupe": lambda x, y, z: y >= 5}),
         ("kubejs:ruines/reservoir_tombe", "Ruine : château d'eau effondré", {}), ("kubejs:ruines/conduite_rompue", "Ruine : conduite rompue", {})]
imgs = [(t, A.iso(monde(n, **kw), 9 if "station" in n or "camp" in n else 12, sol="station" not in n, marge=1)) for n, t, kw in LISTE]
COLS = 2; cw = max(i.width for _, i in imgs); chh = max(i.height for _, i in imgs) + 30
rows = (len(imgs) + COLS - 1) // COLS
sh = Image.new("RGB", (COLS * cw + 40, rows * chh + 70), (30, 31, 36)); d = ImageDraw.Draw(sh)
d.text((20, 16), "Réfractaires et Écho, station de capsules, ruines", font=ImageFont.truetype(A.FB, 24), fill=(240, 240, 240))
for k, (t, im) in enumerate(imgs):
    x = 20 + (k % COLS) * cw; y = 60 + (k // COLS) * chh
    d.text((x + 6, y), t, font=ImageFont.truetype(A.FB, 15), fill=(250, 220, 140))
    sh.paste(im, (x + (cw - im.width) // 2, y + 24))
sh.save("/home/claude/apercus/autres_structures.png"); print(sh.size)
