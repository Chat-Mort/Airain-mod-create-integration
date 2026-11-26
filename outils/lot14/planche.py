import sys; sys.path.insert(0, '.')
from lecture import *
import json
COUL = {0: (92, 62, 38), 1: (160, 122, 74), 2: (226, 204, 150)}     # foncé (A), moyen (B), clair (accent)
k = 0; lectures = {}
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
W = Image.new('RGB', (6 * 260 + 10, 4 * 160 + 50), (52, 54, 60)); d = ImageDraw.Draw(W)
d.text((10, 8), "Première lecture des 24 motifs — à gauche ta capture, à droite ma grille (foncé = A, moyen = B, clair = accent)", font=F, fill=(240, 220, 160))
for f in FICH:
    im, bx = echantillons(f)
    for b in bx:
        k += 1; fc = face(im, b)
        sc = [(lire(fc, n)[1], n) for n in (7, 8, 9, 10)]
        s, n = max(sc)
        g, _ = lire(fc, n)
        lectures[k] = {'n': n, 'grille': g.tolist()}
        x0, y0 = 10 + ((k - 1) % 6) * 260, 40 + ((k - 1) // 6) * 160
        W.paste(Image.fromarray(fc.astype('uint8')).resize((120, 120)), (x0, y0))
        gi = Image.new('RGB', (n, n))
        for j in range(n):
            for i in range(n): gi.putpixel((i, j), COUL[int(g[j, i])])
        W.paste(gi.resize((120, 120), Image.NEAREST), (x0 + 125, y0))
        d.text((x0, y0 + 124), "%d   (%d × %d)" % (k, n, n), font=F, fill=(230, 230, 230))
W.save('/mnt/user-data/outputs/pattern_reading_24.png')
json.dump(lectures, open('lectures.json', 'w'))
