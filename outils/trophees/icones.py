import math, sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
def neuf(): return Image.new('RGBA', (16, 16), (0, 0, 0, 0))
def px(im, x, y, c):
    if 0 <= x < 16 and 0 <= y < 16: im.putpixel((x, y), c + (255,) if len(c) == 3 else c)
def contour(im, c=(20, 16, 22)):
    a = im.copy()
    for x in range(16):
        for y in range(16):
            if a.getpixel((x, y))[3] == 0 and any(0 <= x + dx < 16 and 0 <= y + dy < 16 and a.getpixel((x + dx, y + dy))[3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                im.putpixel((x, y), c + (255,))
def ombre(x, y, cx, cy, r):   # éclairage depuis le haut-gauche
    return ((x - cx) + (y - cy)) / (2 * r)
def mix(a, b, t): return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

# 1. Rivet du colosse : tête hexagonale en fer, œil rouge, tige filetée
def rivet():
    im = neuf(); cx, cy, r = 7.5, 6, 5.6
    for x in range(16):
        for y in range(16):
            dx, dy = abs(x + 0.5 - cx - 0.5), abs(y + 0.5 - cy - 0.5)
            if dy <= r * 0.87 and dx * 0.5 + dy * 0.87 <= r * 0.87 and dx <= r:
                s = ombre(x, y, cx, cy, r)
                px(im, x, y, mix((205, 205, 215), (70, 70, 82), min(1, max(0, s + 0.5))))
    for x, y in ((3, 4), (11, 8), (4, 8), (10, 3)): px(im, x, y, (150, 80, 40))       # rouille
    for x, y in ((7, 5), (8, 5), (7, 6), (8, 6)): px(im, x, y, (230, 40, 30))
    px(im, 7, 5, (255, 140, 110))
    for y in range(11, 16):
        for x in range(6, 10): px(im, x, y, (120, 120, 132) if (y + x) % 2 else (85, 85, 96))
    contour(im); return im

# 2. Cœur de magma : roche de netherite fendue de lave
def magma():
    im = neuf(); cx, cy, r = 7.5, 8, 6.3
    for x in range(16):
        for y in range(16):
            d = math.hypot(x - cx, (y - cy) * 1.05)
            if d <= r:
                s = ombre(x, y, cx, cy, r)
                px(im, x, y, mix((92, 80, 86), (30, 25, 30), min(1, max(0, s + 0.5))))
    fentes = [(4, 5), (5, 6), (6, 6), (7, 7), (8, 7), (9, 8), (10, 8), (7, 8), (6, 9), (6, 10), (9, 9), (10, 10), (11, 11), (5, 11), (8, 4), (8, 5), (11, 6)]
    for x, y in fentes: px(im, x, y, (255, 120, 20))
    for x, y in ((7, 7), (8, 7), (7, 8)): px(im, x, y, (255, 220, 90))
    contour(im); return im

# 3. Engrenage du Rôdeur : rouage de fer sombre, œil rouge
def engrenage():
    im = neuf(); cx, cy = 7.5, 7.5
    for x in range(16):
        for y in range(16):
            d = math.hypot(x - cx, y - cy); a = math.atan2(y - cy, x - cx)
            dent = (math.cos(a * 8) > 0.35)
            if (d <= 5.2) or (dent and d <= 7.4):
                if d < 2.6: continue
                s = ombre(x, y, cx, cy, 7)
                px(im, x, y, mix((135, 138, 150), (45, 46, 54), min(1, max(0, s + 0.5))))
    for x in range(16):
        for y in range(16):
            if math.hypot(x - cx, y - cy) < 2.2: px(im, x, y, (200, 25, 25))
    px(im, 7, 7, (255, 170, 150)); px(im, 8, 8, (130, 10, 10))
    contour(im); return im

# 4. Œil du Gardien : œil violet, pupille fendue, cadre sombre
def oeil():
    im = neuf(); cx, cy = 7.5, 7.5
    for x in range(16):
        for y in range(16):
            u, v = (x - cx) / 7.2, (y - cy) / 4.6
            if u * u + v * v <= 1:
                px(im, x, y, (40, 26, 56))
            if (x - cx) ** 2 / 3.6 ** 2 + (y - cy) ** 2 / 3.6 ** 2 <= 1:
                d = math.hypot(x - cx, y - cy) / 3.6
                px(im, x, y, mix((215, 175, 255), (110, 50, 190), d))
    for y in range(5, 11): px(im, 7, y, (15, 8, 25)); px(im, 8, y, (15, 8, 25))
    px(im, 6, 5, (255, 255, 255)); px(im, 5, 6, (235, 225, 255))
    for x in (1, 14): px(im, x, 7, (120, 70, 200)); px(im, x, 8, (120, 70, 200))
    contour(im); return im

# 5. Sceau du Centurion : médaille de bronze nain, rune
def sceau():
    im = neuf(); cx, cy, r = 7.5, 7.5, 6.6
    for x in range(16):
        for y in range(16):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                s = ombre(x, y, cx, cy, r)
                base = (150, 100, 45) if d > r - 1.3 else (210, 160, 72)
                px(im, x, y, mix(base, mix(base, (60, 38, 15), 0.6), min(1, max(0, s + 0.35))))
    rune = [(7, 3), (8, 3), (7, 4), (8, 4), (5, 5), (6, 5), (9, 5), (10, 5), (7, 5), (8, 5), (7, 6), (8, 6), (7, 7), (8, 7), (6, 8), (9, 8), (5, 9), (10, 9), (7, 9), (8, 9), (7, 10), (8, 10), (6, 11), (7, 11), (8, 11), (9, 11)]
    for x, y in rune: px(im, x, y, (95, 58, 22))
    px(im, 5, 4, (255, 230, 150)); px(im, 4, 5, (255, 220, 140))
    contour(im); return im

ICONES = {"rivet_colosse": rivet, "coeur_magma": magma, "engrenage_rodeur": engrenage, "oeil_gardien": oeil, "sceau_centurion": sceau}
if __name__ == '__main__':
    noms = list(ICONES)
    feuille = Image.new('RGBA', (len(noms) * 200 + 20, 240), (36, 37, 42, 255)); d = ImageDraw.Draw(feuille)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    for i, n in enumerate(noms):
        ic = ICONES[n](); ic.save(f'{OUT}/{n}.png')
        feuille.alpha_composite(ic.resize((176, 176), 0), (20 + i * 200, 12))
        d.text((20 + i * 200, 200), n, fill=(230, 220, 200), font=f)
    feuille.save('apercu.png')
