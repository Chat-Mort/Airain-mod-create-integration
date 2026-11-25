# Maquette : relais cinétique d'airain (trois allures, émetteur et récepteur, recette)
import sys; sys.path.insert(0, '.'); sys.path.insert(0, '/home/claude/travail/lot9')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rmodeles as m
from tex import TEX as PT
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
W, H = 1500, 1010
im = Image.new('RGBA', (W, H), (52, 54, 60, 255)); d = ImageDraw.Draw(im)
OR = (240, 220, 160); GR = (200, 200, 200)
def tx(recepteur=False, actif=True):
    t = m.tx(actif); t['bras'] = np.array(PT['bras'])
    if recepteur and actif: t['oeil'] = t['oeil_r']
    return t
d.text((20, 14), "Relais cinétique d'airain — trois allures (émetteur, récepteur, vu de dos avec l'arbre)", font=F, fill=OR)
noms = [("A · Bloc cerclé", "Obsidienne dans un cadre d'airain, fentes violettes."), ("B · Cage d'airain", "Cœur d'obsidienne entre douze arêtes d'airain."),
        ("C · Sur socle", "Socle et chapeau d'airain, noyau d'obsidienne.")]
for i, f in enumerate((m.cube, m.cage, m.socle)):
    x0 = 20 + i * 490
    d.rectangle([x0, 46, x0 + 470, 400], fill=(139, 139, 139, 255))
    im.alpha_composite(m.rendre(f(), tx(False), {'vue': [30, 45], 'scale': [0.6] * 3}, 260, m.LUM), (x0 - 5, 60))
    im.alpha_composite(m.rendre(f(), tx(True), {'vue': [30, 45], 'scale': [0.6] * 3}, 200, m.LUM), (x0 + 250, 50))
    im.alpha_composite(m.rendre(f(), tx(False, False), {'vue': [30, 225], 'scale': [0.6] * 3}, 160, ()), (x0 + 290, 235))
    d.text((x0 + 10, 330), "émetteur", font=FS, fill=(30, 30, 30)); d.text((x0 + 395, 56), "récepteur", font=FS, fill=(30, 30, 30))
    d.text((x0 + 330, 380), "dos : arbre", font=FS, fill=(30, 30, 30))
    d.text((x0 + 8, 410), noms[i][0], font=F, fill=OR); d.text((x0 + 8, 434), noms[i][1], font=FP, fill=GR)
y = 475
d.line([(20, y - 8), (W - 20, y - 8)], fill=(90, 92, 100), width=2)
d.text((20, y), "Fonctionnement", font=F, fill=OR)
regles = ("Un arbre de Create entre par le dos. Canal réglé comme sur les machines de Create (petite plaque de valeur sur le dessus, 1 à 99).",
          "Clic droit à main vide : émetteur ou récepteur. Émetteur : l'œil est vert ; récepteur : l'œil est violet ; à l'arrêt : l'œil se ferme.",
          "L'émetteur prend la rotation de son réseau ; chaque récepteur du même canal la rend à la même vitesse, dans n'importe quelle dimension.",
          "Ce que consomment les machines côté récepteur pèse sur le réseau de l'émetteur, plus 10 % de perte (une surcharge d'un côté arrête les deux).",
          "Un seul émetteur par canal, autant de récepteurs qu'on veut. Il faut que les deux côtés soient chargés (joueur présent ou chargeur de chunks).",
          "La clé (Create ou airain) le tourne et le démonte comme les autres machines.")
for k, t in enumerate(regles): d.text((20, y + 30 + k * 22), "• " + t, font=FP, fill=(220, 220, 220))
y = 650
d.line([(20, y - 8), (W - 20, y - 8)], fill=(90, 92, 100), width=2)
d.text((20, y), "Recette — établi mécanique 5 × 5, calquée sur celle du transmetteur (les carapaces de shulker deviennent des plaques d'airain)", font=F, fill=OR)
G = ["OOSOO", "OMPMO", "AEEA?", "OMPMO", "OOSOO"]
G = ["OOSOO", "OMPMO", "AQEQA", "OMPMO", "OOSOO"]
G = ["OOSOO", "OMPMO", "OAEAO", "OMPMO", "OOSOO"]
cl = {'O': ((40, 28, 62), "Obsidienne"), 'S': ((140, 140, 136), "Arbre"), 'M': ((32, 110, 96), "Perle de l'Ender"),
      'P': ((200, 160, 70), "Mécanisme de précision"), 'E': ((60, 170, 120), "Œil de l'Ender"), 'A': ((225, 186, 110), "Plaque d'airain")}
c = 52
for r, ligne in enumerate(G):
    for k, ch in enumerate(ligne):
        x0, y0 = 20 + k * (c + 4), y + 34 + r * (c + 4)
        d.rectangle([x0, y0, x0 + c, y0 + c], fill=(139, 139, 139), outline=(60, 60, 60))
        d.rectangle([x0 + 8, y0 + 8, x0 + c - 8, y0 + c - 8], fill=cl[ch][0])
        d.text((x0 + c / 2 - 5, y0 + c / 2 - 8), ch, font=FS, fill=(255, 255, 255))
for k, (ch, (col, nom)) in enumerate(cl.items()):
    d.rectangle([330, y + 40 + k * 28, 348, y + 58 + k * 28], fill=col); d.text((356, y + 40 + k * 28), ch + " · " + nom, font=FP, fill=(220, 220, 220))
d.text((330, y + 40 + 6 * 28 + 10), "→ 1 relais cinétique d'airain (il en faut deux par liaison, comme pour le transmetteur).", font=FP, fill=GR)
d.text((330, y + 40 + 7 * 28 + 10), "Même schéma que le transmetteur d'énergie du pack : obsidienne, arbres, perles, mécanismes, œil au centre.", font=FP, fill=GR)
d.text((20, H - 30), "Textes en jeu en anglais. Aucune texture ni code de l'autre mod n'est repris : seulement l'esprit (obsidienne et œil de l'Ender) et le schéma de la recette.", font=FP, fill=(170, 170, 170))
im.convert('RGB').save('/mnt/user-data/outputs/kinetic_relay_mockup.png')
