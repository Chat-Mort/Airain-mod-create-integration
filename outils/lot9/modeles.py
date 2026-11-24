import numpy as np
from proj import rendre, boite, tourne
from tex import TEX
def tx(allume):
    d = {k: np.array(v) for k, v in TEX.items()}
    if not allume:
        for k in ('lentille', 'carre', 'l8', 'l12'): d[k] = d[k + '_off']
    return d
LUM = ('lentille', 'carre', 'l8', 'l12')
SOCLE = [boite([1, 0, 1], [15, 5, 15], {'*': 'flanc', 'up': 'dessus', 'down': 'dessous'})]

def lyre():
    """A : tête orientable sur une lyre, lentille vers l'avant (sud ici)."""
    return SOCLE + [
        boite([2, 5, 6], [4, 13, 10], 'bras'), boite([12, 5, 6], [14, 13, 10], 'bras'),
    ] + tourne([boite([4.5, 6, 4], [11.5, 13, 12], {'*': 'tete', 'north': 'dessus'}),
                boite([4, 5.5, 11.5], [12, 13.5, 13], {'*': 'bras', 'south': 'l8'}, uvs={'south': (0, 0, 8, 8)}),
                boite([1.5, 8.5, 7], [14.5, 10.5, 9], 'bras', faces=['east', 'west'])], 'x', -22.5, [8, 9.5, 8])

def lanterne():
    """B : lanterne à quatre vitres grillagées et chapeau à ouïes."""
    return [boite([0, 0, 0], [16, 3, 16], {'*': 'flanc', 'up': 'dessus', 'down': 'dessous'}, uvs=None),
            boite([2, 3, 2], [14, 13, 14], {'*': 'carre', 'up': 'dessus', 'down': 'dessus'}, uvs={k: (0, 0, 16, 16) for k in ('north', 'south', 'east', 'west')}),
            boite([1, 3, 1], [3, 13, 3], 'bras'), boite([13, 3, 1], [15, 13, 3], 'bras'), boite([1, 3, 13], [3, 13, 15], 'bras'), boite([13, 3, 13], [15, 13, 15], 'bras'),
            boite([1, 13, 1], [15, 16, 15], {'*': 'tete', 'up': 'chapeau'})]

def phare():
    """C : phare tourné vers le ciel, tambour à ailettes et lentille sur le dessus."""
    return SOCLE + [boite([3, 5, 3], [13, 12, 13], 'tete', faces=['north', 'south', 'east', 'west']),
                    boite([2, 11, 2], [14, 12.5, 14], {'*': 'bras', 'up': 'l12'}, uvs={'up': (0, 0, 12, 12)})]
