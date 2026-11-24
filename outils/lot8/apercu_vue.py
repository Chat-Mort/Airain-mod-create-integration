# Maquette : clé à molette d'airain (objet) et loupe de la couronne améliorée (affichage pendant le zoom, cible marquée)
import sys; sys.path.insert(0, '/home/claude/travail/lot5b')
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cle, marteau
from kit import Planche, EXP, ARD, OR, hx
S = 3
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 8 * S - 2)
T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'

def scene(w, h, marque):
    """Vue schématique : ciel, collines, un mob au loin (rectangles), vu à la loupe (vignette ronde) ou à l'œil nu."""
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        c = (int(120 + 60 * y / h), int(160 + 40 * y / h), 215) if y < h * 0.55 else (70, 110, 60)
        d.line([(0, y), (w, y)], fill=c)
    d.polygon([(0, h * .55), (w * .3, h * .42), (w * .6, h * .5), (w, h * .4), (w, h * .55)], fill=(88, 128, 74))
    zx, zy, k = w // 2 + 10, int(h * .56), 6                          # le mob, en blocs de 6 px
    corps = [(-2, -32, 2, -24, (60, 140, 120)), (-2, -24, 2, -12, (50, 90, 150)), (-2, -12, 2, 0, (70, 70, 120)), (-6, -24, -2, -12, (60, 140, 120)), (2, -24, 6, -12, (60, 140, 120))]
    if marque:                                                          # contour blanc de l'effet « surbrillance »
        g = Image.new('L', (w, h)); gd = ImageDraw.Draw(g)
        for (a, b, c, e, _) in corps: gd.rectangle([zx + a * k // 2 - 3, zy + b * k // 2 - 3, zx + c * k // 2 + 3, zy + e * k // 2 + 3], fill=255)
        im.paste((255, 255, 255, 255), (0, 0), g)
    for (a, b, c, e, col) in corps: d.rectangle([zx + a * k // 2, zy + b * k // 2, zx + c * k // 2, zy + e * k // 2], fill=col)
    return im, (zx, zy - 16 * k)

def plaque(texte, coul=(255, 255, 255)):
    """Plaque d'information de la loupe : ardoise, filet d'airain, texte blanc (comme les écrans du pack)."""
    tw = int(FT.getlength(texte)) + 36; p = Planche(tw // S + 1, 13)
    p.creux(0, 0, tw // S + 1, 13, fond=hx('23262d'))
    im = p.im.crop((0, 0, tw, 39)); d = ImageDraw.Draw(im); d.text((18, 6), texte, font=FT, fill=coul)
    return im

out = Image.new('RGBA', (1500, 760), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
d.text((10, 10), "Clé à molette d'airain (outil de chantier) et loupe de la couronne améliorée — textes en jeu en anglais", font=F, fill=(240, 220, 160))
# --- clé à molette
c = cle.cle(); bg = Image.new('RGBA', (320, 320), (139, 139, 139, 255)); bg.alpha_composite(c.resize((320, 320), Image.NEAREST)); out.alpha_composite(bg, (10, 50))
m = marteau.marteau(); b2 = Image.new('RGBA', (160, 160), (139, 139, 139, 255)); b2.alpha_composite(m.resize((160, 160), Image.NEAREST)); out.alpha_composite(b2, (340, 50))
d.text((340, 215), 'marteau-pilon', font=F, fill=(170, 170, 170))
for k, im in enumerate((c, m)):
    x = 345 + k * 70; d.rectangle([x, 250, x + 53, 303], fill=(112, 68, 37)); d.rectangle([x + 2, 252, x + 51, 301], fill=(42, 46, 55)); out.alpha_composite(im.resize((48, 48), Image.BOX), (x + 3, 253))
def barre(t, x, y, coul=(255, 255, 255)):                      # message de la barre d'action (texte du jeu, ombré)
    d.text((x + 3, y + 3), t, font=FT, fill=(40, 40, 40)); d.text((x, y), t, font=FT, fill=coul)
d.text((10, 385), "Barre d'action après un clic droit (tourner) :", font=F, fill=(170, 170, 170)); barre('Oak Log: lying east-west', 10, 410)
d.text((10, 455), "Après un clic droit accroupi (variante suivante) :", font=F, fill=(170, 170, 170)); barre('Stone Stairs: inner corner, left', 10, 480)
# --- loupe : vue de celui qui porte la couronne
W, H = 460, 330
v, cible = scene(W, H, False)
vig = Image.new('L', (W, H), 255); ImageDraw.Draw(vig).ellipse([W / 2 - 150, H / 2 - 150, W / 2 + 150, H / 2 + 150], fill=0); vig = vig.filter(ImageFilter.GaussianBlur(6))
v.paste((10, 10, 12, 255), (0, 0), vig)
dv = ImageDraw.Draw(v); cx, cy = W // 2, H // 2
for (a, b, c2, e) in ((cx - 18, cy, cx - 6, cy), (cx + 6, cy, cx + 18, cy), (cx, cy - 18, cx, cy - 6), (cx, cy + 6, cx, cy + 18)): dv.line([(a, b), (c2, e)], fill=(243, 214, 148), width=3)
p1 = plaque('Zombie  ·  34 m  ·  +6 m  ·  18 / 20'); v.alpha_composite(p1, ((W - p1.width) // 2, H - 60))
out.alpha_composite(v, (560, 50))
for k, t in enumerate(("Couronne portée, touche H maintenue :", "plaque avec distance, hauteur et vie de la cible.", "Clic gauche pendant le zoom : la cible est marquée.")):
    d.text((560, 392 + k * 20), t, font=F, fill=(200, 200, 200))
# --- vue de l'ami : cible marquée
v2, (mx, my) = scene(W, H, True)
dv2 = ImageDraw.Draw(v2)
for k in range(9): dv2.rectangle([mx - 1, my - 40 - k * 12, mx + 1, my - 34 - k * 12], fill=(255, 250, 220))   # colonne de lumière
dd = ImageDraw.Draw(v2); t = 'Liam marked a Zombie (34 m, north-east)'; tw = dd.textlength(t, font=FT)
dd.text(((W - tw) / 2 + 3, H - 52), t, font=FT, fill=(40, 40, 40)); dd.text(((W - tw) / 2, H - 55), t, font=FT, fill=(243, 214, 148))
out.alpha_composite(v2, (1030, 50))
for k, t in enumerate(("Vous deux : la cible brille à travers les murs 8 s,", "une colonne de lumière la signale, la barre d'action", "dit qui l'a marquée. Un bloc ou un lieu : il brille", "et la colonne monte de là.")):
    d.text((1030, 392 + k * 20), t, font=F, fill=(200, 200, 200))
out.convert('RGB').save('/mnt/user-data/outputs/wrench_and_crown_scope_mockup.png'); print(out.size)
