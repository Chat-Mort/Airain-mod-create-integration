import sys; sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
import rmod2 as m
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
W, H = 1500, 560
im = Image.new('RGBA', (W, H), (52, 54, 60, 255)); d = ImageDraw.Draw(im)
d.text((20, 14), "Relais cinétique d'airain — cage noir netherite (forme du B), cœur d'obsidienne à fente violette (texture du A), rivets d'airain aux coins", font=F, fill=(240, 220, 160))
vues = [("Émetteur (œil vert)", 'e', 45), ("Récepteur (œil violet)", 'r', 45), ("À l'arrêt (œil fermé)", 'off', 45), ("Dos : arbre en retrait", 'e', 225)]
for i, (t, mode, v) in enumerate(vues):
    x0 = 20 + i * 367
    d.rectangle([x0, 46, x0 + 352, 420], fill=(139, 139, 139, 255))
    im.alpha_composite(m.rendre(m.relais(), m.tx(mode), {'vue': [30, v], 'scale': [0.6] * 3}, 340, m.LUM if mode != 'off' else ('dessus', 'coeur')), (x0 + 6, 66))
    d.text((x0 + 8, 52), t, font=FS, fill=(30, 30, 30))
for k, t in enumerate(("L'arbre de Create entre par le dos dans un creux de 3 texels : il se voit entre les arêtes sans dépasser du bloc.",
                       "Le dessus (lueur violette) porte la plaque de valeur du canal, comme sur les machines de Create.",
                       "Le reste ne change pas : fonctionnement et recette de la maquette précédente.")):
    d.text((20, 440 + k * 24), "• " + t, font=FP, fill=(220, 220, 220))
im.convert('RGB').save('/mnt/user-data/outputs/kinetic_relay_mockup_2.png')
