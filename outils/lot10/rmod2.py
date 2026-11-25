import sys, numpy as np
sys.path.insert(0, '/home/claude/travail/lot9')
from proj import rendre, boite
import rtex2
from rmodeles import arbre_tex
LUM = ('oeil', 'dessus', 'coeur')
def tx(mode='e'):
    d = {k: np.array(v) for k, v in rtex2.TEX.items()}
    d['oeil'] = d[{'e': 'oeil', 'r': 'oeil_r', 'off': 'oeil_off'}[mode]]
    d['shaft'] = np.array(arbre_tex())
    return d

def relais():
    """Œil au sud (devant), arbre au nord : demi-arbre de Create du centre à la face, en retrait dans la cage."""
    el = []
    C2 = {k: (0, 0, 2, 2) for k in ('north', 'south', 'east', 'west', 'up', 'down')}
    for x in (0, 14):
        for y in (0, 14):
            for z in (0, 14): el.append(boite([x, y, z], [x + 2, y + 2, z + 2], 'coin', uvs=C2))
    for (a0, a1) in ((0, 2), (14, 16)):
        for (b0, b1) in ((0, 2), (14, 16)):
            el.append(boite([a0, 2, b0], [a1, 14, b1], 'arete'))      # montants
            el.append(boite([2, a0, b0], [14, a1, b1], 'arete'))      # traverses est-ouest
            el.append(boite([a0, b0, 2], [a1, b1, 14], 'arete'))      # traverses nord-sud
    el.append(boite([1, 1, 3], [15, 15, 15], {'*': 'coeur', 'south': 'oeil', 'north': 'dos', 'up': 'dessus', 'down': 'dessus'}))
    el.append(boite([6, 6, 0], [10, 10, 3], 'shaft', uvs={k: (0, 0, 4, 4) for k in ('north', 'south')} | {'east': (0, 6, 3, 10), 'west': (0, 6, 3, 10), 'up': (6, 0, 10, 3), 'down': (6, 0, 10, 3)}))
    return el
