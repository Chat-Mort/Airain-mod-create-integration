# Widgets des recettes de Create (jei/widgets.png), affichés dans EMI : mêmes matières que les recettes EMI du pack
# (case d'ardoise au filet d'or, flèches gravées sombres, cadre d'or), coordonnées tirées d'AllGuiTextures (Create 6.0.10).
import math
from PIL import Image, ImageDraw
from kit import *
O = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/jei/widgets.png'
EMI = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/emi/textures/gui/widgets.png'
FL = dict(fond=(45, 48, 56, 255), haut=(37, 40, 47, 255), bas=(69, 74, 86, 255))      # flèche vide d'EMI HD

def grave(p, m, X0, Y0):
    """Flèche gravée comme les flèches vides d'EMI HD : aplat sombre, arête sombre en haut à gauche, claire en bas à droite."""
    w, h = m.size; px = m.load()
    for y in range(h):
        for x in range(w):
            if not px[x, y]: continue
            haut = y == 0 or not px[x, y - 1]; gauche = x == 0 or not px[x - 1, y]
            bas = y == h - 1 or not px[x, y + 1]; droite = x == w - 1 or not px[x + 1, y]
            p.im.putpixel((X0 + x, Y0 + y), FL['haut'] if (haut or gauche) else FL['bas'] if (bas or droite) else FL['fond'])

def masque(w, h, dessin):
    K = 8; m = Image.new('L', (w * K, h * K)); dessin(ImageDraw.Draw(m), K)
    return m.resize((w, h), Image.BOX).point(lambda v: 255 if v >= 128 else 0)

def masque_orig(o, x, y, w, h):
    """Silhouette de l'original (pixels opaques), agrandie au pixel près (aplats droits : pas de retracé)."""
    m = Image.new('L', (w, h))
    for yy in range(h):
        for xx in range(w):
            c = o.getpixel((x + xx, y + yy))
            if c[3] > 0 and c[0] > 200: m.putpixel((xx, yy), 255)
    return m.resize((w * S, h * S), Image.NEAREST)

def ellipse(w, h, coul, a_max, dur=1.6):
    """Ombre ou halo elliptique (texels), opacité décroissante vers le bord."""
    im = Image.new('RGBA', (w, h)); cx, cy = (w - 1) / 2, (h - 1) / 2
    for y in range(h):
        for x in range(w):
            d = ((x - cx) / (w / 2)) ** 2 + ((y - cy) / (h / 2)) ** 2
            if d < 1: im.putpixel((x, y), coul[:3] + (int(a_max * (1 - d) ** (1 / dur)),))
    return im

def barre_chaleur(p, Y, chaud):
    """Barre de chaleur des bassins (169 x 19) : cadre d'or fin, ouverture en haut au milieu (le brûleur s'y pose),
    fond d'ardoise ; lueur ambrée le long du bas si la recette demande de la chaleur."""
    X0, Y0, X1, Y1 = 0, Y * S, 169 * S - 1, (Y + 19) * S - 1
    p.r(X0, Y0, X1, Y1, OR['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, OR['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, OR['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, OR['base']); p.r(X0 + 3, Y0 + 3, X1 - 3, Y1 - 3, OR['trait'])
    p.r(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, hx('2a2e37')); p.r(X0 + 4, Y0 + 4, X1 - 4, Y0 + 5, ARD['ombre'])
    if chaud:
        for k in range(14):
            a = (1 - k / 14) ** 1.5 * 0.55; c = hx('e08a10')
            for X in range(X0 + 4, X1 - 3):
                b = p.im.getpixel((X, Y1 - 4 - k)); p.im.putpixel((X, Y1 - 4 - k), tuple(int(b[i] * (1 - a) + c[i] * a) for i in range(3)) + (255,))

def widgets():
    o = Image.open(O).convert('RGBA'); p = Planche(base=o.resize((768, 768), Image.NEAREST))
    emi = Image.open(EMI).convert('RGBA')
    for r in ((0, 0, 18, 18), (19, 0, 71, 10), (19, 10, 42, 10), (0, 21, 18, 14), (0, 42, 52, 11), (0, 56, 52, 11), (0, 156, 18, 18),
              (20, 156, 18, 18), (0, 178, 12, 16), (0, 201, 169, 19), (0, 221, 169, 19)): p.efface(*r)
    slot = emi.crop((0, 0, 54, 54)); pointille = emi.crop((0, 54, 54, 108))
    p.im.alpha_composite(slot, (0, 0))                                                           # case
    p.im.alpha_composite(pointille, (20 * S, 156 * S))                                           # case de sortie à chance
    cat = slot.copy(); px = cat.load()                                                           # case du catalyseur : filet d'or clair
    for y in range(54):
        for x in range(54):
            k = min(x, y, 53 - x, 53 - y)
            if k == 0: px[x, y] = OR['trait']
            elif k == 1: px[x, y] = OR['hl']
            elif k == 2: px[x, y] = OR['clair']
            elif k == 3: px[x, y] = OR['base']
    p.im.alpha_composite(cat, (0, 156 * S))
    # flèches retracées à la taille HD (formes massives) : fût de 3 px, pointe en triangle net, gravées comme celles d'EMI
    for (x, y, L) in ((19, 0, 71), (19, 10, 42)):
        def d(dd, K, L=L):
            W = L * S; dd.rectangle([0, 10 * K, (W - 18) * K, 20 * K - 1], fill=255)
            dd.polygon([((W - 19) * K, 0), (W * K, 15 * K), ((W - 19) * K, 30 * K)], fill=255)
        grave(p, masque(L * S, 10 * S, d), x * S, y * S)
    def d(dd, K):                                                         # flèche coudée : bras, coude, descente, pointe
        dd.polygon([(6 * K, 0), (45 * K, 0), (45 * K, 21 * K), (33 * K, 21 * K), (33 * K, 15 * K), (0, 15 * K), (0, 6 * K)], fill=255)
        dd.polygon([(24 * K, 21 * K), (54 * K, 21 * K), (39 * K, 42 * K)], fill=255)
    grave(p, masque(18 * S, 14 * S, d), 0, 21 * S)
    p.im.alpha_composite(ellipse(52 * S, 11 * S, hx('ffb347'), 150), (0, 42 * S))                # halo de chaleur
    p.im.alpha_composite(ellipse(52 * S, 11 * S, hx('0c0d10'), 170), (0, 56 * S))                # ombre portée
    q = o.crop((0, 178, 12, 194)); qq = Image.new('RGBA', (36, 48)); qp = q.load()             # point d'interrogation en or
    for y in range(16):
        for x in range(12):
            c = qp[x, y]
            if c[3]:
                v = c[0]; col = OR['hl'] if v > 230 else OR['clair'] if v > 180 else OR['base'] if v > 120 else OR['trait']
                for a in range(3):
                    for b in range(3): qq.putpixel((x * 3 + a, y * 3 + b), col)
    p.im.alpha_composite(qq, (0, 178 * S))
    barre_chaleur(p, 201, True); barre_chaleur(p, 221, False)
    return p.im

if __name__ == '__main__':
    widgets().save('/tmp/nv/jei.png')
