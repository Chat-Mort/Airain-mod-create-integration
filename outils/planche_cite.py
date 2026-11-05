import sys
sys.argv = [sys.argv[0], "0", "/tmp"]
import apercu_avant_poste as A
from PIL import Image, ImageDraw, ImageFont
def monde(nom, coupe=None, rot=2):
    d = A.P[A.NS + nom]; sx, sy, sz = d["size"]; W = {}
    fin = {(j[0], j[1], j[2]): j[7] for j in d["jigsaws"]}
    for k, s in d["blocks"].items():
        x, y, z = map(int, k.split(","))
        if (x, y, z) in fin: s = fin[(x, y, z)]
        if A.couleur(s) is None or (coupe and coupe(x, y, z)): continue
        X, Z = A.rot_xz(x, z, sx, sz, rot); W[(X, y, Z)] = s
    return W
L = [("grand_marche_c", "Grand marché (6 machines)", None, True), ("stand_tir_c", "Stand de tir", None, True),
     ("laboratoire_c", "Laboratoire d'essais (toit retiré)", lambda x, y, z: y >= 11, False),
     ("laboratoire_c", "Laboratoire · sous-sol (salle d'essai)", lambda x, y, z: y >= 5, False),
     ("kiosque", "Kiosque (remplissage)", None, True), ("chateau_eau", "Petit château d'eau (remplissage)", None, True)]
imgs = [(t, A.iso(monde(n, c), 12, sol=s, marge=1)) for n, t, c, s in L]
COLS = 2; cw = max(i.width for _, i in imgs); ch = max(i.height for _, i in imgs) + 30
sh = Image.new("RGB", (COLS * cw + 40, 3 * ch + 70), (30, 31, 36)); d = ImageDraw.Draw(sh)
d.text((20, 16), "Nouveaux bâtiments des cités", font=ImageFont.truetype(A.FB, 24), fill=(240, 240, 240))
for k, (t, im) in enumerate(imgs):
    x = 20 + (k % COLS) * cw; y = 60 + (k // COLS) * ch
    d.text((x + 6, y), t, font=ImageFont.truetype(A.FB, 15), fill=(250, 220, 140)); sh.paste(im, (x + (cw - im.width) // 2, y + 24))
sh.save("/home/claude/apercus/cite_batiments.png"); print(sh.size)
