# Table du carreleur en relief : socle, montants d'angle, caisson en retrait d'un pixel, plateau d'airain,
# damier en relief au-dessus de la bordure, tiroirs qui ressortent, poignées, équerre posée sur le plateau
import sys; sys.path.insert(0, '/home/claude/travail/lot12'); sys.path.insert(0, '/home/claude/travail/lot9')
from px import hx, neuf
from PIL import Image
import numpy as np
from proj import rendre, boite
A = dict(h=hx('fff0c4'), c=hx('f3d694'), b=hx('e1ba6e'), m=hx('c99b52'), s=hx('a8763c'), d=hx('704425'))
ARD = [hx('3f4350'), hx('363a44'), hx('2f333c'), hx('2a2e37'), hx('1b1e24')]
BL = [hx('f2efe8'), hx('e2ded4'), hx('cfc9bc')]; NO = [hx('3a3840'), hx('2c2a30'), hx('1f1d22')]
def t_airain():
    im = neuf(); px = im.load()
    for y in range(16):
        for x in range(16): px[x, y] = A['b'] if (x * 3 + y) % 7 else A['m']
    return im
def t_damier():
    """Damier de 14 x 14 (carreaux de 3 et demi -> 4 x 4 carreaux de 3 texels sur 12, cadre fin de joint)."""
    im = neuf(); px = im.load()
    for y in range(16):
        for x in range(16):
            i, j = (x - 2) // 3, (y - 2) // 3; u, v = (x - 2) % 3, (y - 2) % 3
            if not (2 <= x < 14 and 2 <= y < 14): px[x, y] = BL[2]; continue
            p = BL if (i + j) % 2 == 0 else NO
            px[x, y] = p[0] if u + v == 0 else p[2] if u + v == 4 else p[1]
    return im
def t_caisson(echantillon=False):
    """Panneau d'ardoise du caisson ; sur les côtés, un petit échantillon de damier serti au centre."""
    im = neuf(); px = im.load()
    for y in range(16):
        for x in range(16): px[x, y] = ARD[1] if (x + y * 3) % 7 else ARD[2]
    if echantillon:
        for y in range(5, 11):
            for x in range(5, 11):
                e = min(x - 5, y - 5, 10 - x, 10 - y)
                if e == 0: px[x, y] = A['c'] if (x == 5 or y == 5) and not (x == 10 or y == 10) else A['d']
                else: px[x, y] = (BL if ((x - 6) // 2 + (y - 6) // 2) % 2 == 0 else NO)[1]
    return im
def t_tiroir():
    im = neuf(); px = im.load()
    for y in range(16):
        for x in range(16): px[x, y] = ARD[0] if y % 16 == 0 else ARD[2] if (x + y) % 9 else ARD[3]
    return im
B_ = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
def vrai(n): return Image.open(B_ + n + '.png').convert('RGBA').crop((0, 0, 16, 16))
TEX = dict(air=vrai('airain_block'), pilier=vrai('airain_band').rotate(90), bande=vrai('airain_band'), damier=t_damier(), caisson=t_caisson(), cote=t_caisson(True), tiroir=t_tiroir(), carton=Image.new('RGBA', (16, 16), hx('efdfb6')))
def modele():
    el = []
    el.append(boite([0, 0, 0], [16, 2, 16], 'bande'))                                   # socle
    for (x, z) in ((0, 0), (14, 0), (0, 14), (14, 14)): el.append(boite([x, 2, z], [x + 2, 14, z + 2], 'pilier'))   # montants
    el.append(boite([1, 2, 1], [15, 14, 15], {'*': 'cote', 'north': 'caisson', 'south': 'caisson'}))   # caisson en retrait
    el.append(boite([0, 14, 0], [16, 15, 16], 'bande'))                                 # plateau (bordure, un pixel plus bas)
    el.append(boite([1, 15, 1], [15, 16, 15], {'*': 'air', 'up': 'damier'}))            # damier en relief
    for (y0, y1) in ((3, 7), (8, 12)):                                                  # tiroirs qui ressortent d'un pixel
        el.append(boite([3, y0, 0], [13, y1, 1], 'tiroir'))
        el.append(boite([7, y0 + 1.5, -1], [9, y0 + 2.5, 0], 'air'))                    # poignées
        el.append(boite([4, y1 - 0.5, 0.2], [6, y1 + 0.5, 0.8], 'carton'))              # cartons qui dépassent
        el.append(boite([10, y1 - 0.5, 0.2], [12, y1 + 0.5, 0.8], 'carton'))
    el.append(boite([3, 16, 9], [11, 16.5, 10], 'air'))                                 # équerre posée sur le damier
    el.append(boite([10, 16, 3], [11, 16.5, 10], 'air'))
    return el
if __name__ == '__main__':
    tx = {k: np.array(v) for k, v in TEX.items()}
    W = Image.new('RGBA', (3 * 330, 330), (139, 139, 139, 255))
    for i, (v, t) in enumerate(((30, 205), (30, 135), (55, 225))):
        # avant au sud dans le rendu : on retourne le modèle (avant = z bas -> on regarde depuis -z)
        W.alpha_composite(rendre(modele(), tx, {'vue': [v, t], 'scale': [0.62] * 3}, 330), (i * 330, 0))
    W.save('/tmp/nv/table3d.png')
