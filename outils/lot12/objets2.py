# Lot 12 (suite) : rouage brisé, ferraille, burette d'huile, nacelle, portillon de passerelle
import math
from px import *
from objets import ligne
from PIL import Image
A = AIR
FER = dict(h=hx('f2f2f2'), c=hx('c8c8c8'), b=hx('a2a2a2'), m=hx('7c7c7c'), s=hx('5a5a5a'), o=hx('26262a'))
ROUILLE = [hx('c2662e'), hx('8a3e1c')]
HUILE = [hx('5a4214'), hx('2a1e0a')]

def rouage_brise():
    """Rouage d'airain cassé : huit dents, moyeu percé, un quart arraché (bord en dents de scie, métal frais), un éclat à côté."""
    im = neuf(); px = im.load()
    cx, cy = 7.0, 7.5
    for y in range(16):
        for x in range(16):
            dx, dy = x - cx, y - cy; d = math.hypot(dx, dy); a = math.degrees(math.atan2(dy, dx))
            if 5 < a < 95 and d > 2.6 - ((x * 7 + y * 3) % 3) * 0.6: continue          # quart arraché, cassure irrégulière
            dent = math.cos(math.radians(a) * 8) > 0.3
            if d <= 4.7 or (d <= 6.6 and dent):
                l = (-dx - dy) / max(d, 0.1)
                px[x, y] = A['c'] if l > 0.55 else A['b'] if l > -0.1 else A['m'] if l > -0.6 else A['s']
                if 1.5 < d <= 2.5: px[x, y] = A['d']                    # moyeu
                if d <= 1.5: px[x, y] = (0, 0, 0, 0)                     # trou de l'arbre
    # métal frais le long de la cassure
    for y in range(16):
        for x in range(16):
            if not px[x, y][3]: continue
            dx, dy = x - cx, y - cy; a = math.degrees(math.atan2(dy, dx)); d = math.hypot(dx, dy)
            if d > 2.5 and (abs(a - 5) < 12 or abs(a - 95) < 12): px[x, y] = A['h']
    for (x, y, c) in ((12, 12, 'b'), (13, 12, 'm'), (12, 13, 's'), (13, 13, 's'), (11, 14, 'c')): px[x, y] = A[c]   # éclat
    return contour(im)

def ferraille():
    """Ferraille : tas de tôle de fer cabossée, un boulon et un bout de rouage d'airain, taches de rouille."""
    g = ["................",
         "................",
         "..........ooo...",
         ".........ochbo..",
         ".........obmso..",
         "....ooo...oso...",
         "...oaabo...o....",
         "..oaabbdo.oooo..",
         "..oabddo.ochbbo.",
         ".oooodooochbmmso",
         "ochhcbbccbbmrmso",
         "ocbbbbmmbbmmmso.",
         "obbrbmmmmmmsRso.",
         ".ommmmsssmssso..",
         "..oossssssooo...",
         "....oooooo......"]
    pal = dict(FER); pal.update(a=A['c'], d=A['s'], r=ROUILLE[0], R=ROUILLE[1])
    pal['b'] = FER['b']
    im = depuis([l.replace('a', 'a') for l in g], pal)
    # les lettres a/d du rouage restent airain, b ailleurs en fer
    px = im.load()
    for (x, y) in ((5, 6), (6, 6), (4, 7), (5, 7), (4, 8)): px[x, y] = A['c']
    for (x, y) in ((6, 7), (7, 7), (5, 8), (6, 8)): px[x, y] = A['b']
    return im

def burette():
    """Burette d'huile de machine : corps rond d'airain, long bec fin, anse, goutte noire au bout du bec."""
    g = ["................",
         "..............hd",
         ".............co.",
         "............co..",
         "...........co...",
         "....ooo...co....",
         "...ochbo.co.....",
         "...oommoco......",
         "..ohccbbbmo.ooo.",
         ".ohccbbbbmmoosso",
         ".ocbbbbbmmmsdo.o",
         ".obbbbbmmmssdo.o",
         ".ommmmmmsssddoso",
         "..oddddddddddooo",
         "...oooooooooo...",
         "................"]
    im = depuis(g, A); px = im.load()
    px[15, 1] = HUILE[1]; px[14, 1] = HUILE[0]                        # goutte
    return im

def nacelle():
    """Nacelle du téléphérique : crochet sur le câble, tige, cabine d'airain à deux fenêtres, plancher sombre."""
    g = ["................",
         "oooooooooooooooo",
         "sssssssooosssssss"[:16],
         ".......ocdo.....",
         ".......omso.....",
         "........oo......",
         "........ms......",
         "...oooooooooo...",
         "..ochhcccccbmo..",
         "..ocoooocoooso..",
         "..oco..oco..so..",
         "..ocoooocoooso..",
         "..obbbbbbbmmso..",
         "..ommmmmmmsssdo.",
         "...ooooooooooo..",
         "................"]
    im = depuis(g, A); px = im.load()
    for x in range(16): px[x, 2] = FER['b'] if x % 2 else FER['m']     # câble
    for (x, y) in ((4, 10), (5, 10), (8, 10), (9, 10), (10, 10)): px[x, y] = hx('9ad0e8')   # vitres
    px[4, 10] = hx('d8f0ff')
    return im

def portillon():
    """Portillon de passerelle : deux montants d'airain, trois barreaux, écharpe en diagonale, gond en haut."""
    im = neuf(); px = im.load()
    for y in range(2, 15):
        px[2, y] = A['c']; px[3, y] = A['m']                            # montant gond
        px[13, y] = A['b']; px[14, y] = A['s']                          # montant battant
    for yy in (3, 8, 13):
        for x in range(4, 13): px[x, yy] = A['b']; px[x, yy + 1] = A['s'] if yy < 13 else A['s']
    ligne(px, 4, 12, 12, 5, A['c'])                                     # écharpe
    ligne(px, 5, 12, 12, 6, A['m'])
    for (x, y) in ((1, 4), (1, 12)): px[x, y] = FER['b']                 # gonds
    return contour(im)

OBJETS2 = dict(rouage_brise=rouage_brise, ferraille=ferraille, huile_machine=burette, airain_gondola=nacelle, airain_catwalk_gate=portillon)
if __name__ == '__main__':
    K = '/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/'
    T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
    W = Image.new('RGBA', (len(OBJETS2) * 400, 200), (139, 139, 139, 255))
    for i, (n, f) in enumerate(OBJETS2.items()):
        src = (K if n in ('rouage_brise', 'ferraille', 'huile_machine') else T) + n + '.png'
        W.alpha_composite(Image.open(src).convert('RGBA').crop((0, 0, 16, 16)).resize((160, 160), Image.NEAREST), (i * 400 + 10, 20))
        W.alpha_composite(f().resize((160, 160), Image.NEAREST), (i * 400 + 200, 20))
    W.save('/tmp/nv/lot12b.png')
