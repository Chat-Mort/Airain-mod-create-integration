# Barre de mana d'Ars Nouveau, dessinée au texel près (3x) : cadre, embouts et liquide animé.
# Géométrie d'Ars (GuiManaHUD), en texels (1 px d'interface = 3 texels), toile de 324 x 63 (ligne r = écran (y-18)*3 + r) :
#   liquide visible : x 27..314, lignes 30..41 ; voiles rouge/réserve : x 24..317, lignes 24..47 (à recouvrir par le devant)
#   fond : texture lignes 0..53 posées en 0..53 ;  devant : texture lignes 54..113 posées en 3..62.
# Le liquide n'est pas centré dans les 108 px (marges 9 et 3) : tout le décor est centré sur le liquide (axe x = 170,5).
import math
from PIL import Image
W, Hc = 324, 63
def hx(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
O = hx('1a1424')                                                          # trait de contour
ARG = [hx(c) for c in ('f6f4fc', 'dcd8ea', 'bdb7d0', '9c95b4', '78718f', '575070', '3c3652')]   # argent, clair -> sombre
AME = [hx(c) for c in ('f1e8ff', 'cfb3ff', 'a77ff0', '8152d0', '5d34a0', '3d2070', '28134c')]   # améthyste
VERRE = [hx('0d0918'), hx('120c20'), hx('160f27'), hx('1a122d')]
class Toile:
    def __init__(s): s.im = Image.new('RGBA', (W, Hc)); s.p = s.im.load()
    def px(s, x, y, c):
        if 0 <= x < W and 0 <= y < Hc: s.p[x, y] = c
    def rect(s, x0, y0, x1, y1, c):                                       # bornes incluses
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.px(x, y, c)
    def blend(s, x, y, c, a):
        if 0 <= x < W and 0 <= y < Hc:
            r, g, b, al = s.p[x, y]
            if al == 0: return
            s.p[x, y] = (int(r + (c[0] - r) * a), int(g + (c[1] - g) * a), int(b + (c[2] - b) * a), al)
def nuance(t, pal, decal=0):
    """Ombrage d'un cylindre couché, éclairé d'en haut : t = 0 en haut, 1 en bas."""
    paliers = (.08, .2, .38, .58, .76, .9)
    i = sum(1 for v in paliers if t > v) + decal
    return pal[max(0, min(len(pal) - 1, i))]
# ------------------------------------------------------------------ devant : cadre du tube
def cadre(d):
    X0, X1 = 44, 297
    haut = [O, ARG[1], ARG[0], ARG[1], ARG[2], ARG[3], ARG[4], ARG[6]]    # lignes 22..29 (la dernière : ombre sur le verre)
    bas = [ARG[3], ARG[2], ARG[3], ARG[3], ARG[4], ARG[5], ARG[5], O]     # lignes 42..49
    for i, c in enumerate(haut): d.rect(X0, 22 + i, X1, 22 + i, c)
    for i, c in enumerate(bas): d.rect(X0, 42 + i, X1, 42 + i, c)
    # graduations au quart, à la moitié et aux trois quarts du liquide (27 + 288 k/8)
    for k in range(1, 8):
        x = 27 + 36 * k
        h = 3 if k % 2 == 0 else 2
        for y in range(23, 23 + h): d.px(x, y, ARG[4]); d.px(x + 1, y, ARG[0])
    # reflets du verre sur le liquide (en segments, comme sur une fiole)
    for x in range(48, 294):
        seg = (x // 37) % 3 != 2
        if seg: d.blend(x, 31, (255, 255, 255), .0)
    return d
def reflets(d):
    for x in range(48, 294):
        if (x - 48) % 74 < 52: d.p[x, 31] = (255, 255, 255, 95)
        if (x - 48) % 74 < 30: d.p[x, 32] = (255, 255, 255, 35)
        d.p[x, 41] = (200, 170, 255, 40)
# ------------------------------------------------------------------ devant : embouts (gauche, puis miroir exact)
def embout(d, droite):
    def X(x): return 341 - x if droite else x
    # silhouette : collerette (18..23, 14..57), corps (24..40, 18..53), lèvre (41..44, 21..50) ; coins adoucis
    parts = [(19, 23, 14, 57, 2), (24, 40, 18, 53, 1), (41, 44, 21, 50, 1)]
    forme = {}
    for (x0, x1, y0, y1, coin) in parts:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                cx = min(x - x0, x1 - x); cy = min(y - y0, y1 - y)
                if cx + cy < coin: continue
                forme[(x, y)] = (y - y0) / (y1 - y0)
    for (x, y), t in forme.items():
        c = nuance(t, ARG)
        # bagues gravées sur le corps : creux puis arête
        if x in (28, 36) and 18 < y < 53: c = nuance(t, ARG, 2)
        if x in (29, 37) and 18 < y < 53: c = nuance(t, ARG, -1)
        if x == 23 and 14 < y < 57: c = nuance(t, ARG, 2)                 # ombre de la collerette sur le corps
        d.px(X(x), y, c)
    # contour : tout point hors forme qui touche la forme
    for (x, y) in list(forme):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in forme and not (q[0] > 44): d.px(X(q[0]), q[1], O)
    # gemme sertie au milieu du corps (même éclairage des deux côtés : on ne la retourne pas)
    gx = X(32) if not droite else X(32)
    gemme(d, gx, 35.5)
def gemme(d, cx, cy, rx=5.5, ry=9):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, v = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            n = abs(u) + abs(v)
            if n > 1.18: continue
            if n > 1: d.px(x, y, ARG[5]); continue                         # sertissure
            if n > .82: d.px(x, y, AME[5] if v > 0 or u > 0 else AME[3]); continue
            if v < 0: c = AME[1] if u < 0 else AME[2]
            else: c = AME[3] if u < 0 else AME[4]
            d.px(x, y, c)
    for (x, y) in ((cx - 2, cy - 4), (cx - 1, cy - 4), (cx - 2, cy - 3)): d.px(int(x), int(y), AME[0])
# ------------------------------------------------------------------ fond : verre vide
def fond(f):
    for y in range(30, 42):
        c = VERRE[min(3, (y - 30) // 3)]
        f.rect(27, y, 314, y, c)
    f.rect(27, 30, 314, 30, hx('07050d'))                                 # ombre du rebord sur le verre
# ------------------------------------------------------------------ liquide animé (33 images, boucle parfaite)
LIQ_PAL = [hx(c) for c in ('efe4ff', 'd2b8ff', 'b38cf6', '9667e4', '7a4cc8', '6038a8', '47267f')]
def liquide():
    im = Image.new('RGBA', (768, 768)); p = im.load()
    for k in range(33):
        for x in range(288):
            for r in range(-3, 15):
                t = max(0, min(11, r)) / 11
                ph = 2 * math.pi * (x + 3 * k) / 99                        # 99 texels, 3 par image : boucle en 33 images
                vague = .55 * math.sin(ph) + .3 * math.sin(3 * ph + 1.3) + .15 * math.sin(2 * math.pi * (x - 3 * k) / 33)
                v = t * 5.2 + 1 - vague * (1 - t) * 1.1
                if r <= 0: v = 0 if vague > -.2 else 1                    # surface : arête claire qui ondule
                c = LIQ_PAL[max(0, min(6, int(round(v))))]
                p[x, 18 * k + 3 + r] = c
            # bulles qui montent en dérivant (périodiques sur 33 images)
        for b in range(9):
            bx = (b * 37 + 11 + 3 * k) % 288
            by = 10 - ((k + b * 7) % 33) * 10 // 33
            if 1 <= by <= 10:
                p[bx, 18 * k + 3 + by] = LIQ_PAL[0]
                if by + 1 <= 11: p[bx, 18 * k + 3 + by + 1] = LIQ_PAL[1]
    return im
def construire():
    f, d = Toile(), Toile()
    fond(f); cadre(d); reflets(d); embout(d, False); embout(d, True)
    return f.im, d.im, liquide()
if __name__ == '__main__':
    f, d, liq = construire()
    f.save('fond.png'); d.save('devant.png'); liq.save('liquide.png')
