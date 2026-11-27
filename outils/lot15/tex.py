# Mobilier impérial : textures 16 x 16 (bois sombre, cuir capitonné, panneaux, plateaux, livres)
import sys; sys.path.insert(0, '/home/claude/travail/lot12')
from px import hx, neuf
from PIL import Image
# noyer sombre, du reflet à l'ombre
W = [hx('80573a'), hx('6a462d'), hx('573924'), hx('472e1d'), hx('382316'), hx('28180f')]
# cuir rouge impérial (même famille que le velours du socle des trophées)
L = [hx('c2414a'), hx('a3303a'), hx('86232e'), hx('6b1a24'), hx('4f111a'), hx('360a11')]
A = dict(h=hx('fff4cf'), c=hx('f3d694'), b=hx('e1ba6e'), m=hx('c99b52'), s=hx('a8763c'), d=hx('704425'))
B_ = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
def vrai(n): return Image.open(B_ + n + '.png').convert('RGBA').crop((0, 0, 16, 16))

# veinage : longues traînées horizontales, sans joints de planches (mobilier massif)
# veinage : fil continu (longues traînées), tons groupés par bandes, quelques nœuds de fil plus sombres
VEINE = ["2222222222222222", "2222333333322222", "2222222222222222", "1111112222222111",
         "2222222222222222", "2223333222222222", "2222222222333332", "2222222222222222",
         "3322222222222222", "2222221111111222", "2222222222222222", "2222223333333332",
         "2222222222222222", "1122222222222111", "2222222222222222", "2233332222222222"]
def t_bois(vertical=False):
    im = neuf(); p = im.load()
    for y in range(16):
        for x in range(16):
            v = int(VEINE[y][x]) if not vertical else int(VEINE[x][y])
            p[x, y] = W[v]
    return im
def t_plateau(bords='nesw', centre='marbre'):
    """Plateau : bois en bordure (seulement côtés non raccordés), filet d'airain, incrustation au centre."""
    im = t_bois(); p = im.load()
    ins = vrai('white_marble_0') if centre == 'marbre' else t_cuir(lisse=True)
    q = ins.load()
    if centre == 'marbre':   # veine d'or en biais, comme le marbre du pack
        # veine d'or fine et sinueuse, interrompue, avec un filet gris qui la prolonge
        for x, y in ((3,11),(4,11),(5,10),(6,10),(7,10),(9,8),(10,7),(11,7),(12,6)):
            q[x, y] = A['b']
        for x, y in ((8,9),(13,5)): q[x, y] = A['m']
        for x, y in ((4,5),(5,5),(6,4),(8,4),(9,3)): q[x, y] = hx('cfc9bc')
    x0 = 3 if 'w' in bords else 0; x1 = 13 if 'e' in bords else 16
    y0 = 3 if 'n' in bords else 0; y1 = 13 if 's' in bords else 16
    for y in range(y0, y1):
        for x in range(x0, x1): p[x, y] = q[x, y]
    # filet d'airain autour de l'incrustation (lumière en haut à gauche)
    for x in range(x0 - (1 if 'w' in bords else 0), x1 + (1 if 'e' in bords else 0)):
        if 'n' in bords and 0 <= x < 16: p[x, y0 - 1] = A['c']
        if 's' in bords and 0 <= x < 16: p[x, y1] = A['s']
    for y in range(y0 - (1 if 'n' in bords else 0), y1 + (1 if 's' in bords else 0)):
        if 'w' in bords and 0 <= y < 16: p[x0 - 1, y] = A['b']
        if 'e' in bords and 0 <= y < 16: p[x1, y] = A['m']
    return im
def t_cuir(lisse=False):
    """Capitonnage en losanges de 8 x 8, boutons d'airain aux sommets, plis sombres, bombé éclairé en haut à gauche."""
    im = neuf(); p = im.load()
    centres = [(4 + 8 * i + 4 * j, 4 * j) for i in range(-2, 4) for j in range(-2, 6)]
    for y in range(16):
        for x in range(16):
            if lisse:
                p[x, y] = L[2] if (x * 5 + y * 3) % 11 else L[3]; continue
            cx, cy = min(centres, key=lambda c: abs(x + .5 - c[0]) + abs(y + .5 - c[1]))
            dx, dy = x + .5 - cx, y + .5 - cy; d = (abs(dx) + abs(dy)) / 4
            if d > .85: col = L[4]
            elif d < .45: col = L[1] if dx + dy < 0 else L[2]
            else: col = L[2] if dx + dy < 0 else L[3]
            if d < .3 and dx + dy < -.2: col = L[0]
            p[x, y] = col
    if not lisse:
        for (bx, by) in ((0, 0), (8, 0), (4, 4), (12, 4), (0, 8), (8, 8), (4, 12), (12, 12)):
            p[bx, by] = A['c']
    return im
def t_cuir_clous():
    """Cuir lisse bordé d'une rangée de clous d'airain (accoudoirs, côtés du fauteuil)."""
    im = t_cuir(lisse=True); p = im.load()
    for x in range(16):
        for y in (1, 14):
            if x % 3 == 1: p[x, y] = A['c']; p[x, y + 1 if y == 1 else y - 1] = L[4] if False else p[x, y + 1 if y == 1 else y - 1]
    return im
def t_panneau():
    """Panneau encadré : cadre de bois vertical, panneau central en relief (biseau clair en haut à gauche)."""
    im = t_bois(); p = im.load(); v = t_bois(True).load()
    for y in range(16):
        for x in range(16):
            if x < 2 or x > 13: p[x, y] = v[x, y]
    for y in range(3, 13):
        for x in range(3, 13):
            if y == 3 or x == 3: p[x, y] = W[0]
            elif y == 12 or x == 12: p[x, y] = W[4]
            elif y == 4 or x == 4: p[x, y] = W[1]
    for x in range(2, 14): p[x, 2] = W[5]; p[x, 13] = W[1]
    for y in range(2, 14): p[2, y] = W[5]; p[13, y] = W[1]
    return im
def t_tiroir():
    im = t_bois(); p = im.load()
    for x in range(16): p[x, 0] = W[1]; p[x, 15] = W[5]
    for y in range(16): p[0, y] = W[1]; p[15, y] = W[5]
    return im
def t_livres():
    """Dos de livres alignés : couleurs sourdes, nervures d'or."""
    im = neuf(); p = im.load()
    dos = [('7a1c24', 3), ('2f4a3a', 2), ('3a2a1c', 3), ('243652', 2), ('6b4a1c', 2), ('7a1c24', 2), ('2f4a3a', 2)]
    x = 0
    for col, w in dos:
        c = hx(col)
        for dx in range(w):
            for y in range(16):
                ombre = 0.75 if dx == w - 1 else 1.0
                cc = tuple(int(c[i] * ombre) for i in range(3)) + (255,)
                p[x, y] = A['b'] if y in (3, 12) else cc
            x += 1
            if x >= 16: break
        if x >= 16: break
    return im
TEX = dict(bois=t_bois(), boisv=t_bois(True), cuir=t_cuir(), cuirl=t_cuir(lisse=True), clous=t_cuir_clous(), panneau=t_panneau(),
           tiroir=t_tiroir(), livres=t_livres(), air=vrai('airain_block'), bande=vrai('airain_band'), marbre=vrai('white_marble_0'),
           plateau=t_plateau(), plateau_w=t_plateau('nse'), plateau_m=t_plateau('ns'), plateau_e=t_plateau('nsw'), bureau=t_plateau(centre='cuir'), bureau_g=t_plateau('nsw', 'cuir'), bureau_d=t_plateau('nse', 'cuir'))
if __name__ == '__main__':
    n = list(TEX)
    S = Image.new('RGBA', (len(n) * 104, 104), (139, 139, 139, 255))
    for i, k in enumerate(n): S.paste(TEX[k].resize((96, 96), Image.NEAREST), (i * 104 + 4, 4))
    S.save('/tmp/mob/textures.png')
