# Maquette : carton de motif (enregistrer un échantillon, le répéter au cordeau)
import sys; sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
from scene2 import scene
from carton import carton, hx
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
W, H = 1500, 1000
im = Image.new('RGBA', (W, H), (52, 54, 60, 255)); d = ImageDraw.Draw(im)
OR = (240, 220, 160)
d.text((20, 14), "Carton de motif — on construit un échantillon une fois, le cordeau le répète sur toute la zone", font=F, fill=OR)
for k, (t, m) in enumerate((("vierge", None), ("motif enregistré", [hx('e8e4dc'), hx('2c2a30')]))):
    x0 = 20 + k * 150
    d.rectangle([x0, 46, x0 + 140, 186], fill=(139, 139, 139))
    im.alpha_composite(carton(m).resize((128, 128), Image.NEAREST), (x0 + 6, 52))
    d.text((x0 + 6, 192), t, font=FP, fill=(220, 220, 220))
d.text((20, 216), "Objet 32 × 32, famille des outils de chantier.", font=FP, fill=(170, 170, 170))
motif = lambda x, z: 'blanc' if (x + z) % 2 == 0 else 'noir'
ech = {(x, z): motif(x, z) for x in range(4) for z in range(4)}; ech[(0, 0)] = 'airain'
def barre(t, x, y):
    d.text((x + 2, y + 2), t, font=FT, fill=(40, 40, 40)); d.text((x, y), t, font=FT, fill=(243, 214, 148))
x0 = 340
d.rectangle([x0, 46, x0 + 520, 446], fill=(139, 139, 139))
im.alpha_composite(scene(6, 6, {(x + 1, z + 1): t for (x, z), t in ech.items()}, {}, [], [(1, 1), (4, 4)], 0.17, 520).crop((0, 60, 520, 460)), (x0, 46))
d.text((x0 + 8, 52), "1 · Échantillon construit à la main, coins pris au carton", font=FS, fill=(30, 30, 30))
barre("Pattern saved: floor 4 × 4, 16 blocks", x0 + 4, 454)
x0 = 900
d.rectangle([x0, 46, x0 + 580, 446], fill=(139, 139, 139))
fan = {(x, z): ech[(x % 4, z % 4)] for x in range(12) for z in range(8)}
im.alpha_composite(scene(12, 8, {}, fan, [], [(0, 0), (11, 7)], 0.068, 580).crop((0, 90, 580, 490)), (x0, 46))
d.text((x0 + 8, 52), "2 · Zone 12 × 8 au cordeau, carton dans l'autre main", font=FS, fill=(30, 30, 30))
barre("Floor 12 × 8: 96 blocks (pattern) · right click: lay", x0 + 4, 454)
y = 500
d.line([(20, y - 10), (W - 20, y - 10)], fill=(90, 92, 100), width=2)
d.text((20, y), "Enregistrer (carton en main)", font=F, fill=OR)
r1 = ("Clic droit sur un coin de l'échantillon, puis sur le coin opposé : le carton enregistre la grille, jusqu'à 32 × 32.",
      "Une seule couche : sol, plafond ou mur. Les cases d'air sont gardées comme « ne rien poser » (motifs ajourés).",
      "Chaque bloc est enregistré avec son état complet : sens des marches, axe des bûches, dalle haute ou basse, tapis, etc.",
      "Clic gauche : effacer le carton. L'infobulle donne la taille, le type (sol / mur) et la liste des blocs à prévoir.")
for k, t in enumerate(r1): d.text((20, y + 30 + k * 22), "• " + t, font=FP, fill=(220, 220, 220))
y = 640
d.text((20, y), "Poser (cordeau en main, carton dans l'autre main)", font=F, fill=OR)
r2 = ("Les mêmes gestes que d'habitude : piquets A et B, aperçu, clic droit pour poser, clic gauche pour annuler.",
      "Le motif part du piquet A et se répète dans les deux sens ; zone jusqu'à 32 × 32 avec un carton (64 en ligne).",
      "Accroupi + clic droit : tourner le motif d'un quart de tour ; les états tournent avec (une marche vers le nord devient vers l'est).",
      "Pose exacte : chaque bloc reprend son état enregistré, sans dépendre de l'endroit où l'on regarde. Seules les cases vides sont remplies.",
      "Un motif de sol se pose au sol ou au plafond, un motif de mur sur n'importe quel mur (il est tourné pour suivre la façade).",
      "Les blocs sont pris dans l'inventaire ; s'il en manque : « Laid 80, missing: 12 Black Marble, 4 Airain Block », les piquets restent pour compléter.")
for k, t in enumerate(r2): d.text((20, y + 30 + k * 22), "• " + t, font=FP, fill=(220, 220, 220))
y = 830
d.text((20, y), "Plus tard (noté)", font=F, fill=OR)
d.text((20, y + 30), "• Un écran de motifs tout faits (sol, mur, plafond) avec choix des blocs, pour ceux qui n'aiment pas construire : il remplirait un carton vierge.", font=FP, fill=(220, 220, 220))
d.text((20, y + 52), "  Le carton est conçu pour l'accueillir sans rien changer au cordeau.", font=FP, fill=(220, 220, 220))
d.text((20, H - 30), "Textes en jeu en anglais. Recette proposée : papier ×4, plaque d'airain, colorant noir.", font=FP, fill=(170, 170, 170))
im.convert('RGB').save('/mnt/user-data/outputs/pattern_card_mockup.png')
