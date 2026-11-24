# Maquette : projecteur de chantier (trois allures) et cordeau de maçon
import sys; sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
from modeles import lyre, lanterne, phare, tx, LUM, rendre
from scene import scene
from cordeau import cordeau
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
W, H = 1500, 1160
im = Image.new('RGBA', (W, H), (52, 54, 60, 255)); d = ImageDraw.Draw(im)
OR = (240, 220, 160); GR = (200, 200, 200)
VUE = {'vue': [30, 45], 'scale': [0.625] * 3}

d.text((20, 14), "Projecteur de chantier — trois allures (allumé en grand, éteint en petit)", font=F, fill=OR)
noms = [("A · Projecteur sur lyre", "Tête orientable, à tourner à la clé d'airain."),
        ("B · Lanterne de chantier", "Quatre vitres grillagées, chapeau à ouïes."),
        ("C · Phare vers le ciel", "Tambour à ailettes, lentille sur le dessus.")]
for i, m in enumerate((lyre, lanterne, phare)):
    x0 = 20 + i * 490
    d.rectangle([x0, 46, x0 + 470, 430], fill=(139, 139, 139, 255))
    im.alpha_composite(rendre(m(), tx(True), VUE, 340, LUM), (x0 + 10, 60))
    im.alpha_composite(rendre(m(), tx(False), VUE, 120), (x0 + 345, 300))
    d.text((x0 + 8, 440), noms[i][0], font=F, fill=OR); d.text((x0 + 8, 464), noms[i][1], font=FP, fill=GR)
for k, t in enumerate(("Fonction (la même pour les trois) : entraîné par un arbre de Create par-dessous, il s'allume dès qu'il tourne.",
                       "Allumé : lumière 15, et aucun monstre n'apparaît dans un rayon de 16 blocs autour de lui, de jour comme de nuit.",
                       "Arrêté : lentille éteinte, plus aucune protection.")):
    d.text((20, 496 + k * 20), t, font=FP, fill=(220, 220, 220))

y0 = 580
d.line([(20, y0 - 14), (W - 20, y0 - 14)], fill=(90, 92, 100), width=2)
d.text((20, y0), "Cordeau de maçon — objet 32 × 32 et pose en jeu", font=F, fill=OR)
d.rectangle([20, y0 + 34, 20 + 272, y0 + 34 + 272], fill=(139, 139, 139, 255))
im.alpha_composite(cordeau().resize((256, 256), Image.NEAREST), (28, y0 + 42))
d.rectangle([20, y0 + 318, 20 + 64, y0 + 318 + 64], fill=(139, 139, 139, 255))
im.alpha_composite(cordeau().resize((64, 64), Image.NEAREST), (20, y0 + 318))
d.text((94, y0 + 330), "taille réelle ×2", font=FP, fill=GR)

def barre(t, x, y):
    d.text((x + 2, y + 2), t, font=FT, fill=(40, 40, 40)); d.text((x, y), t, font=FT, fill=(243, 214, 148))
lig = [(x, 0, 1) for x in range(1, 6)]
sol = [(x, 0, z) for x in range(1, 6) for z in range(0, 3)]
mur = [(x, y, 2) for x in range(1, 6) for y in range(0, 3) if x in (1, 5) or y in (0, 2)]
cas = [("1 · Ligne", lig, (1, 0, 1), (5, 0, 1), "Line: 5 blocks · right click to lay"),
       ("2 · Sol, mode plein", sol, (1, 0, 0), (5, 0, 2), "Floor 5 × 3: 15 blocks (fill)"),
       ("3 · Mur, mode contour", mur, (1, 0, 2), (5, 2, 2), "Wall 5 × 3: 12 blocks (outline)")]
for i, (titre, c, a, b, msg) in enumerate(cas):
    x0 = 310 + i * 395
    d.rectangle([x0, y0 + 34, x0 + 380, y0 + 34 + 330], fill=(139, 139, 139, 255))
    im.alpha_composite(scene(c, a, b, N=380).crop((0, 25, 380, 355)), (x0, y0 + 34))
    d.text((x0 + 6, y0 + 40), titre, font=F, fill=(30, 30, 30))
    barre(msg, x0 + 4, y0 + 372)
regles = ("Bloc à poser dans l'autre main. Clic droit sur un bloc : piquet A (là où le bloc serait posé) ; deuxième clic droit : piquet B.",
          "Les cases prévues s'affichent en fil d'airain avec leur nombre ; clic droit pour poser, accroupi + clic droit pour annuler.",
          "Ligne droite (64 blocs au plus) ou plan (16 × 16 au plus), dans n'importe quel sens, sol, plafond ou mur.",
          "Ctrl + clic droit : mode plein ou contour (pour un cadre de mur ou de sol).",
          "Ne remplit que les cases vides (air, herbe, eau) ; pioche dans l'inventaire ; s'il manque des blocs, il pose ce qu'il a et le dit.",
          "Message après la pose : « Laid 15 Stone Bricks » ou « Laid 12 Stone Bricks, missing 3 ».")
for k, t in enumerate(regles):
    d.text((310, y0 + 408 + k * 22), "• " + t, font=FP, fill=(220, 220, 220))
d.text((20, H - 30), "Textes en jeu en anglais. Le fil d'airain n'est visible que par celui qui tient le cordeau.", font=FP, fill=(170, 170, 170))
im.convert('RGB').save('/mnt/user-data/outputs/worksite_projector_and_chalk_line_mockup.png')
