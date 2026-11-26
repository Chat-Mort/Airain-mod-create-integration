# Deuxième lecture : grilles de 8 x 8 ; le cadrage de la face du dessus est ajusté pour chaque motif (meilleur accord)
import sys; sys.path.insert(0, '.')
from lecture import *
import json, itertools
COUL = {0: (92, 62, 38), 1: (160, 122, 74), 2: (226, 204, 150)}
def meilleur_cadrage(im, b):
    best = None
    for haut, gauche, cote, bas in itertools.product((0, .02, .04), (0, .02, .04), (.04, .07, .10, .13), (.05, .08, .11, .14)):
        y0, x0, y1, x1 = b; h, w = y1 - y0, x1 - x0
        fc = im[int(y0 + h * haut):int(y1 - h * bas), int(x0 + w * gauche):int(x1 - w * cote)]
        g, s = lire(fc, 8)
        if best is None or s > best[0]: best = (s, fc, g)
    return best
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
W = Image.new('RGB', (6 * 260 + 10, 4 * 160 + 50), (52, 54, 60)); d = ImageDraw.Draw(W)
d.text((10, 8), "Deuxième lecture, en 8 × 8 — à gauche ta capture, à droite ma grille (foncé = A, moyen = B, clair = accent)", font=F, fill=(240, 220, 160))
k = 0; lectures = {}
for f in FICH:
    im, bx = echantillons(f)
    for b in bx:
        k += 1; s, fc, g = meilleur_cadrage(im, b)
        lectures[k] = g.tolist()
        x0, y0 = 10 + ((k - 1) % 6) * 260, 40 + ((k - 1) // 6) * 160
        W.paste(Image.fromarray(fc.astype('uint8')).resize((120, 120)), (x0, y0))
        gi = Image.new('RGB', (8, 8))
        for j in range(8):
            for i in range(8): gi.putpixel((i, j), COUL[int(g[j][i])])
        W.paste(gi.resize((120, 120), Image.NEAREST), (x0 + 125, y0))
        d.text((x0, y0 + 124), "%d" % k, font=F, fill=(230, 230, 230))
W.save('/mnt/user-data/outputs/pattern_reading_24_8x8.png')
json.dump(lectures, open('lectures8.json', 'w'))
