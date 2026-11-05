import sys; sys.path.insert(0, '../balise7'); sys.path.insert(0, '.')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
from geo import *
R = 4
PEAU, CHEV, OEIL = (196, 150, 118), (70, 48, 30), (60, 70, 140)
def vox(B, dos=False):
    V = {}
    def tete():
        for X in range(-4 * R, 4 * R):
            for Y in range(-8 * R, 0):
                for Z in range(-4 * R, 4 * R):
                    if X in (-4*R, 4*R-1) or Y in (-8*R, -1) or Z in (-4*R, 4*R-1):
                        c = PEAU
                        if Y < -6 * R or (Z > -4 * R and Y < -5 * R) or Z > 2 * R: c = CHEV
                        if Z == -4 * R and -4 * R <= Y < -3 * R and (-3 * R <= X < -1 * R or 1 * R <= X < 3 * R): c = OEIL if (X // R) in (-2, 2) else (240, 240, 240)
                        V[(X, Y, Z)] = c
    tete()
    NT = Image.open('../mcmeta-assets/assets/minecraft/textures/models/armor/netherite_layer_1.png').convert('RGBA')
    for (x, y, z, w, h, d, c) in B:
        if c == NETH:   # casque vanilla texturé
            for X in range(round(x * R), round((x + w) * R)):
                for Y in range(round(y * R), round((y + h) * R)):
                    for Z in range(round(z * R), round((z + d) * R)):
                        fx = X in (round(x*R), round((x+w)*R)-1); fy = Y == round(y*R); fz = Z in (round(z*R), round((z+d)*R)-1)
                        if not (fx or fy or fz): continue
                        i = min(7, int((X / R - x) * 8 / w)); j = min(7, int((Y / R - y) * 8 / h)); k = min(7, int((Z / R - z) * 8 / d))
                        if Z == round(z*R): p = NT.getpixel((8 + i, 8 + j))
                        elif fz: p = NT.getpixel((31 - i, 8 + j))
                        elif fy: p = NT.getpixel((8 + i, k))
                        elif X == round(x*R): p = NT.getpixel((k, 8 + j))
                        else: p = NT.getpixel((16 + 7 - k, 8 + j))
                        if p[3]: V[(X, Y, Z)] = p[:3]
            continue
        for X in range(round(x * R), round((x + w) * R)):
            for Y in range(round(y * R), round((y + h) * R)):
                for Z in range(round(z * R), round((z + d) * R)):
                    V[(X, Y, Z)] = c
    if dos: return {(x, -y, z): c for (x, y, z), c in V.items()}
    return {(-x, -y, -z): c for (x, y, z), c in V.items()}

def face(B, S=5):
    V = vox(B)  # coordonnées négatives : devant = z max
    best = {}
    for (x, y, z), c in V.items():
        k = (-x, y)   # vue de face : x du modèle vers la droite de l'image = gauche du perso
        if k not in best or z > best[k][0]: best[k] = (z, c)
    xs = [k[0] for k in best]; ys = [k[1] for k in best]
    im = Image.new('RGB', ((max(xs) - min(xs) + 1) * S // 2 + 20, (max(ys) - min(ys) + 1) * S // 2 + 20), (32, 33, 38)); dr = ImageDraw.Draw(im)
    for (x, y), (z, c) in best.items():
        X = (x - min(xs)) * S // 2 + 10; Y = (max(ys) - y) * S // 2 + 10
        sh = 1 if len(c) == 4 else max(0.55, 1 - (max(best.values())[0] - z) * 0.01)
        dr.rectangle([X, Y, X + S // 2, Y + S // 2], fill=tuple(int(v * sh) for v in c[:3]))
    return im
P = [("Casque au diadème", diademe_casque()), ("Tiare runique", tiare()), ("Nimbe", nimbe() + halo())]
rows = []
for t, B in P: rows.append((t, face(B, 6), rendu(vox(B), T=3), rendu(vox(B, True), T=3)))
W = max(a.width + b.width + c.width for _, a, b, c in rows) + 60; H = sum(max(a.height, b.height, c.height) + 40 for _, a, b, c in rows)
out = Image.new('RGB', (W, H), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
y = 0
for t, a, b, c in rows:
    d.text((10, y + 8), t + "   (face · 3/4 · dos)", fill=(230, 220, 200), font=f)
    h = max(a.height, b.height, c.height); x = 10
    for im in (a, b, c): out.paste(im, (x, y + 36 + h - im.height)); x += im.width + 20
    y += h + 40
out.save('apercu_tetes.png'); print(out.size)
