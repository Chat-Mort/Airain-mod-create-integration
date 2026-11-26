# Maquette 2 : carton de motif en volume (accroupi + molette), pose répétée en 3D
import sys; sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
from scene2 import scene
from carton import carton, hx
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
W, H = 1500, 1060
im = Image.new('RGBA', (W, H), (52, 54, 60, 255)); d = ImageDraw.Draw(im)
OR = (240, 220, 160)
d.text((20, 14), "Carton de motif en volume — accroupi + molette agrandit la sélection vers la face regardée", font=F, fill=OR)
def barre(t, x, y):
    d.text((x + 2, y + 2), t, font=FT, fill=(40, 40, 40)); d.text((x, y), t, font=FT, fill=(243, 214, 148))
# échantillon en relief : damier 4 x 4, plot d'airain de 2 de haut dans un coin, marbre noir sur le bord du fond
ech = {(x, 0, z): ('blanc' if (x + z) % 2 == 0 else 'noir') for x in range(4) for z in range(4)}
ech[(0, 1, 0)] = 'airain'; ech[(0, 2, 0)] = 'airain'
for x in range(1, 4): ech[(x, 1, 0)] = 'noir'
def cadre(x0, x1, y0, y1, z0, z1):
    return [(x, y, z) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1) for z in range(z0, z1 + 1)
            if sum((x in (x0, x1), y in (y0, y1), z in (z0, z1))) >= 2]
panneaux = [
    ("1 · Deux coins : une couche", {(x + 1, y, z + 1): t for (x, y, z), t in ech.items()}, [((1, 0, 1), (5, 1, 5), 'fil'), ((1, 0.94, 1), (5, 1, 5), 'rouge')], "Selection: 4 × 1 × 4"),
    ("2 · Regard vers le haut, molette ×2", {(x + 1, y, z + 1): t for (x, y, z), t in ech.items()}, [((1, 0, 1), (5, 3, 5), 'fil'), ((1, 2.94, 1), (5, 3, 5), 'rouge')], "Selection: 4 × 3 × 4 · sneak + scroll"),
]
for i, (titre, poses, cases, msg) in enumerate(panneaux):
    x0 = 20 + i * 480
    d.rectangle([x0, 46, x0 + 465, 420], fill=(139, 139, 139))
    im.alpha_composite(scene(6, 6, poses, {}, [], [], 0.13, 465, boites=cases).crop((0, 45, 465, 420)), (x0, 46))
    d.text((x0 + 8, 52), titre, font=FS, fill=(30, 30, 30))
    barre(msg, x0 + 4, 428)
# pose répétée : 3 x 2 motifs (12 x 8), aperçu des vrais blocs
x0 = 980
d.rectangle([x0, 46, x0 + 500, 420], fill=(139, 139, 139))
fan = {}
for X in range(12):
    for Z in range(8):
        for (x, y, z), t in ech.items():
            if x == X % 4 and z == Z % 4: fan[(X, y, Z)] = t
im.alpha_composite(scene(12, 8, {}, fan, [], [(0, 0, 0), (11, 0, 7)], 0.06, 500).crop((0, 60, 500, 435)), (x0, 46))
d.text((x0 + 8, 52), "3 · Zone 12 × 8 au cordeau : le volume se répète", font=FS, fill=(30, 30, 30))
barre("Floor 12 × 3 × 8: 168 blocks (pattern) · right click: lay", x0 + 4, 428)
y = 475
d.line([(20, y - 10), (W - 20, y - 10)], fill=(90, 92, 100), width=2)
d.text((20, y), "Accroupi + molette (Ctrl + molette chez toi), cordeau ou carton en main, deux coins posés", font=F, fill=OR)
r = ("Molette vers le haut : la face de la zone que tu regardes avance d'un bloc ; vers le bas : elle recule (jamais sous 1 bloc).",
     "Tu regardes en haut ou en bas : la hauteur change ; vers un côté : la longueur ou la largeur de ce côté. La barre d'outils ne défile pas.",
     "La barre d'action donne la taille en direct ; la face qui bouge est surlignée en rouge dans l'aperçu.")
for k, t in enumerate(r): d.text((20, y + 30 + k * 22), "• " + t, font=FP, fill=(220, 220, 220))
y = 600
d.text((20, y), "Carton de motif (enregistrer un volume)", font=F, fill=OR)
r = ("Clic droit sur deux coins, puis accroupi + molette pour l'épaisseur ; clic droit encore : enregistrer. Jusqu'à 32 × 32 de côté et 16 de haut.",
     "Chaque bloc garde son état complet (sens des marches, axe des bûches, dalles…) ; l'air reste « ne rien poser ».",
     "Clic gauche : effacer. Infobulle : taille et liste des blocs à prévoir.")
for k, t in enumerate(r): d.text((20, y + 30 + k * 22), "• " + t, font=FP, fill=(220, 220, 220))
y = 725
d.text((20, y), "Cordeau (poser)", font=F, fill=OR)
r = ("Carton dans l'autre main : le volume part du piquet A et se répète dans les trois directions. Accroupi + clic droit : quart de tour (états tournés avec).",
     "Un seul bloc dans l'autre main : la molette permet aussi de remplir un volume (dalle épaisse, mur de plusieurs blocs), plein ou en contour (accroupi + clic droit).",
     "Pose exacte des états enregistrés, seulement dans les cases vides ; blocs pris dans l'inventaire, liste de ce qui manque, piquets gardés pour compléter.",
     "Au plus 4 000 blocs par clic (un autre clic droit continue) ; aperçu des vrais blocs jusqu'à 1 000 cases, au-delà en fil d'airain.",
     "Clic gauche : annuler.")
for k, t in enumerate(r): d.text((20, y + 30 + k * 22), "• " + t, font=FP, fill=(220, 220, 220))
y = 895
d.text((20, y), "Plus tard (noté)", font=F, fill=OR)
d.text((20, y + 30), "• Écran de motifs tout faits (sol, mur, plafond) avec choix des blocs : il remplira un carton vierge.", font=FP, fill=(220, 220, 220))
im.alpha_composite(carton().resize((96, 96), Image.NEAREST), (1250, 900)); im.alpha_composite(carton([hx('e8e4dc'), hx('2c2a30')]).resize((96, 96), Image.NEAREST), (1360, 900))
d.text((1250, 1000), "vierge", font=FP, fill=(200, 200, 200)); d.text((1360, 1000), "enregistré", font=FP, fill=(200, 200, 200))
d.text((20, H - 30), "Textes en jeu en anglais. Recette proposée : papier ×4, plaque d'airain, colorant noir.", font=FP, fill=(170, 170, 170))
im.convert('RGB').save('/mnt/user-data/outputs/pattern_card_mockup_2.png')
