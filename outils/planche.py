import sys, json
sys.argv = [sys.argv[0], "0", "/tmp"]
import apercu_avant_poste as A
from PIL import Image, ImageDraw, ImageFont
NS = A.NS
LISTE = [("centre_fontaine", "Place centrale (fontaine à vapeur)"), ("marche", "Marché + 3 emplacements"), ("machine_batisseur", "Machine « Bâtisseur »"),
         ("entrepot", "Entrepôt"), ("atelier", "Atelier"), ("dortoir", "Dortoir"),
         ("salle_cuivre", "Salle scellée · cuivre"), ("salle_laiton", "Salle scellée · laiton"), ("salle_ciel", "Salle scellée · ciel"),
         ("rue_rails", "Rue aux rails"), ("tour", "Pylône de guet"), ("barricade", "Barricade")]
imgs = []
for nom, titre in LISTE:
    inst = A.Inst(nom, 2, 0, 0)   # façade tournée vers le spectateur
    W = A.blocs_monde([inst])
    im = A.iso(W, 11, marge=1)
    imgs.append((titre, im))
COLS = 3; cw = max(i.width for _, i in imgs); chh = max(i.height for _, i in imgs) + 30
rows = (len(imgs) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * cw + 40, rows * chh + 70), (30, 31, 36)); d = ImageDraw.Draw(sheet)
d.text((20, 16), "Avant-poste tempéré · les pièces (vues de face)", font=ImageFont.truetype(A.FB, 24), fill=(240, 240, 240))
for k, (t, im) in enumerate(imgs):
    x = 20 + (k % COLS) * cw; y = 60 + (k // COLS) * chh
    d.text((x + 6, y), t, font=ImageFont.truetype(A.FB, 15), fill=(250, 220, 140))
    sheet.paste(im, (x + (cw - im.width) // 2, y + 24))
sheet.save("/home/claude/apercus/avant_poste_pieces.png")
print(sheet.size)
