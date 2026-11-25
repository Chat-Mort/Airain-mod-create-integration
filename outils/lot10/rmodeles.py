import sys, numpy as np
sys.path.insert(0, '/home/claude/travail/lot9')
from proj import rendre, boite
import rtex
from PIL import Image
def arbre_tex():
    im = Image.new('RGBA', (16, 16)); p = im.load()
    for y in range(16):
        for x in range(16): p[x, y] = (150, 150, 146, 255) if x % 4 == 0 else (120, 121, 118, 255) if x % 4 in (1, 2) else (92, 93, 90, 255)
    return im
def tx(actif=True):
    d = {k: np.array(v) for k, v in rtex.TEX.items()}
    if not actif: d['oeil'] = d['oeil_off']
    d['shaft'] = np.array(arbre_tex())
    return d
LUM = ('oeil', 'dessus')
U = {k: (0, 0, 16, 16) for k in ('north', 'south', 'east', 'west', 'up', 'down')}
SHAFT = [boite([6, 6, -4], [10, 10, 0], 'shaft', uvs={k: (0, 0, 4, 4) for k in U} | {'east': (0, 6, 4, 10), 'west': (0, 6, 4, 10), 'up': (6, 0, 10, 4), 'down': (6, 0, 10, 4)})]

def cube():
    """A : bloc plein d'obsidienne cerclé d'airain, œil devant (sud ici), arbre derrière (nord)."""
    return SHAFT + [boite([0, 0, 0], [16, 16, 16], {'*': 'flanc', 'south': 'oeil', 'north': 'arbre', 'up': 'dessus', 'down': 'dessus'}, uvs=U)]

def cage():
    """B : cœur d'obsidienne dans une cage d'arêtes d'airain."""
    a = []
    for (x0, x1) in ((0, 2), (14, 16)):
        for (z0, z1) in ((0, 2), (14, 16)): a.append(boite([x0, 0, z0], [x1, 16, z1], 'bras'))
    for (y0, y1) in ((0, 2), (14, 16)):
        for (z0, z1) in ((0, 2), (14, 16)): a.append(boite([2, y0, z0], [14, y1, z1], 'bras'))
        for (x0, x1) in ((0, 2), (14, 16)): a.append(boite([x0, y0, 2], [x1, y1, 14], 'bras'))
    return SHAFT + a + [boite([1, 1, 1], [15, 15, 15], {'*': 'obs', 'south': 'oeil', 'north': 'arbre', 'up': 'dessus'}, uvs=U)]

def socle():
    """C : socle d'airain, noyau d'obsidienne, chapeau ; œil devant."""
    return SHAFT + [boite([0, 0, 0], [16, 4, 16], {'*': 'bras', 'up': 'dessus'}),
                    boite([2, 4, 2], [14, 13, 14], {'*': 'flanc', 'south': 'oeil', 'north': 'arbre'}, uvs=U),
                    boite([1, 13, 1], [15, 16, 15], {'*': 'bras', 'up': 'dessus'}, uvs={'up': (0, 0, 16, 16)})]
