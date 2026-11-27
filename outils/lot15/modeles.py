# Mobilier impérial : modèles (avant = z bas, comme la table du carreleur)
import sys; sys.path.insert(0, '/home/claude/travail/lot9')
from proj import boite
def b(f, t, tex):
    """Élément ; au-dessus de 16, uv repris modulo 16 (pas d'étirement : un texel = un pixel)."""
    if t[1] <= 16: return boite(f, t, tex)
    if f[1] >= 16:
        e = boite([f[0], f[1] - 16, f[2]], [t[0], t[1] - 16, t[2]], tex); e['from'], e['to'] = f, t; return e
    e = boite([f[0], 0, f[2]], [t[0], 16, t[2]], tex)   # élément à cheval : uv du bas, hauteur réelle
    for k, fc in e['faces'].items():
        if k in ('up', 'down'): continue
        u1, v1, u2, v2 = fc['uv']; fc['uv'] = (u1, 0, u2, 16)
    e['from'], e['to'] = f, t; return e
def pieds(l, pts, h, s=2, cerclage=None):
    for (x, z) in pts:
        l.append(b([x - .3, 0, z - .3], [x + s + .3, 1, z + s + .3], 'air'))          # sabot d'airain
        l.append(b([x, 1, z], [x + s, h, z + s], 'boisv'))
        if cerclage: l.append(b([x - .3, cerclage, z - .3], [x + s + .3, cerclage + 1, z + s + .3], 'air'))
def chaise():
    l = []; pieds(l, ((3, 3), (11, 3)), 7, cerclage=4); pieds(l, ((3, 11), (11, 11)), 7, cerclage=4)
    l.append(b([3, 6, 3], [13, 8, 13], {'*': 'bois', 'up': 'bois'}))                     # ceinture de l'assise
    l.append(b([2.8, 7, 2.8], [13.2, 7.5, 13.2], 'air'))                                 # filet d'airain
    l.append(b([3.5, 8, 3.5], [12.5, 9.5, 12.5], {'*': 'cuirl', 'up': 'cuir'}))          # coussin capitonné
    for x in (3, 11): l.append(b([x, 8, 11], [x + 2, 22, 13], 'boisv'))                  # montants du dossier
    l.append(b([5, 10, 11.5], [11, 21, 12.5], {'*': 'cuirl', 'north': 'cuir'}))          # dossier capitonné
    l.append(b([5, 9.5, 11.5], [11, 10, 12.5], 'boisv'))
    l.append(b([2.5, 22, 10.5], [13.5, 23.5, 13.5], 'bande'))                            # traverse d'airain
    l.append(b([6.5, 23.5, 11.5], [9.5, 25.5, 12.5], 'air'))                             # médaillon
    l.append(b([7.5, 25.5, 11.5], [8.5, 26, 12.5], 'air'))
    return l
def fauteuil():
    l = []; pieds(l, ((1, 1), (13, 1), (1, 13), (13, 13)), 4)
    l.append(b([1, 4, 1], [15, 8, 15], {'*': 'panneau', 'up': 'bois'}))                  # caisse
    l.append(b([0.7, 7.5, 0.7], [15.3, 8, 15.3], 'air'))
    l.append(b([2.5, 8, 2], [13.5, 10, 13], {'*': 'cuirl', 'up': 'cuir'}))               # coussin
    for x in (0.5, 13.5):                                                               # accoudoirs
        l.append(b([x, 8, 2], [x + 2, 12, 14], {'*': 'clous'}))
        l.append(b([x - .3, 12, 1.5], [x + 2.3, 13.5, 14.5], 'bois'))
        l.append(b([x - .5, 10.5, 0.8], [x + 2.5, 14, 2], 'air'))                        # crosse d'airain
    l.append(b([1, 8, 13], [15, 28, 15], {'*': 'panneau', 'north': 'cuirl'}))            # dossier haut
    l.append(b([2.5, 10, 12.5], [13.5, 27, 13], {'*': 'cuirl', 'north': 'cuir'}))        # capitonné
    for x in (0.5, 13.5): l.append(b([x, 14, 12.5], [x + 2, 28, 15], 'clous'))          # oreilles
    l.append(b([0.5, 28, 12], [15.5, 29.5, 15.5], 'bande'))                              # couronnement
    l.append(b([5.5, 29.5, 13], [10.5, 31, 14.5], 'air'))
    for x in (5.5, 7.5, 9.5): l.append(b([x, 31, 13], [x + 1, 32, 14.5], 'air'))         # fleurons de couronne
    return l
def banc(gauche=True, droite=True):
    l = []
    l.append(b([0, 6, 3], [16, 8, 13], 'bois'))
    l.append(b([0, 7, 2.8], [16, 7.5, 13.2], 'air'))
    l.append(b([0 + (1 if gauche else 0), 8, 3.5], [16 - (1 if droite else 0), 9.5, 12.5], {'*': 'cuirl', 'up': 'cuir'}))
    for cote, x in ((gauche, 0), (droite, 14)):
        if not cote: continue
        l.append(b([x, 0, 3], [x + 2, 1, 13], 'air'))                                    # patin d'airain
        l.append(b([x, 1, 4], [x + 2, 6, 12], 'panneau'))                                 # joue
        l.append(b([x, 8, 3], [x + 2, 11, 13], 'bois'))                                   # accoudoir
        l.append(b([x - .2, 11, 2.5], [x + 2.2, 12, 13.5], 'bande'))
    return l
def table(bords='nesw', pieds_=True):
    l = []; tex = {'nesw': 'plateau', 'nse': 'plateau_w', 'ns': 'plateau_m', 'nsw': 'plateau_e'}[bords]
    l.append(b([0, 14, 0], [16, 16, 16], {'*': 'bois', 'up': tex}))
    l.append(b([1, 12, 1], [15, 14, 15], 'bois'))                                        # ceinture
    l.append(b([7, 12.5, 0.6], [9, 13.5, 1], 'air'))                                     # écusson
    if pieds_:
        xs = [x for x, c in ((1, 'w'), (13, 'e')) if c in bords]
        pieds(l, [(x, z) for x in xs for z in (1, 13)], 12, cerclage=9)
    return l
def bureau():
    l = []
    l.append(b([0, 14, 0], [16, 16, 16], {'*': 'bois', 'up': 'bureau'}))
    for x0 in (0.5, 10.5):                                                              # caissons à tiroirs
        l.append(b([x0, 0, 1], [x0 + 5, 14, 15], {'*': 'panneau'}))
        l.append(b([x0 - .2, 0, 0.8], [x0 + 5.2, 1, 15.2], 'air'))
        for y0 in (1.5, 6, 10):
            l.append(b([x0 + .5, y0, 0.5], [x0 + 4.5, y0 + 3.5, 1], 'tiroir'))
            l.append(b([x0 + 2, y0 + 1.5, 0], [x0 + 3, y0 + 2, 0.5], 'air'))
    l.append(b([5.5, 11, 1], [10.5, 14, 15], 'bois'))                                   # tiroir central
    l.append(b([6, 11.5, 0.5], [10, 13.5, 1], 'tiroir'))
    l.append(b([7.5, 12.3, 0], [8.5, 12.8, 0.5], 'air'))
    l.append(b([5.5, 2, 14], [10.5, 11, 15], 'panneau'))                                 # panneau de fond
    l.append(b([11.5, 16, 10], [13.5, 18, 12], 'air'))                                   # encrier
    return l
def etagere():
    l = []
    for x in (0, 14.5): l.append(b([x, 0, 4], [x + 1.5, 16, 16], {'*': 'boisv', 'north': 'boisv'}))
    l.append(b([1.5, 0, 15], [14.5, 16, 16], 'panneau'))
    for y in (0, 7, 14.5):
        l.append(b([1.5, y, 4], [14.5, y + 1.5, 15], 'bois'))
        l.append(b([1.5, y + .5, 3.6], [14.5, y + 1.5, 4], 'bande'))                     # chant d'airain
    l.append(b([2, 1.5, 6], [11, 6.5, 14], {'*': 'livres', 'up': 'bois'}))                # objets posés (aperçu)
    l.append(b([2, 8.5, 7], [8, 13.5, 14], {'*': 'livres', 'up': 'bois'}))
    l.append(b([10, 8.5, 8], [13, 11.5, 11], 'air'))
    return l
def armoire():
    l = []
    l.append(b([0, 0, 1], [16, 2, 16], 'bois'))                                          # plinthe
    l.append(b([-.3, 0, 0.7], [16.3, .7, 16.3], 'air'))
    l.append(b([.5, 2, 1.5], [15.5, 30, 16], {'*': 'panneau', 'north': 'boisv'}))       # caisse
    for x0 in (1, 8):                                                                   # deux portes, deux panneaux chacune
        l.append(b([x0, 2.5, 1], [x0 + 7, 16, 1.5], 'panneau'))
        l.append(b([x0, 16, 1], [x0 + 7, 29.5, 1.5], 'panneau'))
    for x in (6.6, 8.6): l.append(b([x, 13, .5], [x + .8, 19, 1], 'air'))                # poignées
    for x in (.6, 14.6):
        for y in (5, 25): l.append(b([x, y, .7], [x + .8, y + 2, 1.2], 'air'))           # charnières
    l.append(b([-.3, 30, .5], [16.3, 31, 16.3], 'bois'))                                 # corniche : bois mouluré
    l.append(b([-.6, 31, .2], [16.6, 32, 16.6], {'*': 'air', 'up': 'bois'}))                                # chapeau d'airain
    l.append(b([6, 30.5, .2], [10, 31.5, .5], 'air'))
    return l

def bureau2(cote):
    """Bureau raccordé sur deux blocs : un caisson par bloc, côté extérieur ; niche commune au milieu."""
    l = []; g = cote == 'gauche'
    l.append(b([0, 14, 0], [16, 16, 16], {'*': 'bois', 'up': 'bureau_g' if g else 'bureau_d'}))
    x0 = 0.5 if g else 10.5
    l.append(b([x0, 0, 1], [x0 + 5, 14, 15], {'*': 'panneau'}))
    l.append(b([x0 - .2, 0, 0.8], [x0 + 5.2, 1, 15.2], 'air'))
    for y0 in (1.5, 6, 10):
        l.append(b([x0 + .5, y0, 0.5], [x0 + 4.5, y0 + 3.5, 1], 'tiroir'))
        l.append(b([x0 + 2, y0 + 1.5, 0], [x0 + 3, y0 + 2, 0.5], 'air'))
    n0, n1 = (5.5, 16) if g else (0, 10.5)                                               # niche, côté intérieur
    l.append(b([n0, 11, 1], [n1, 14, 15], 'bois'))
    l.append(b([n0 + .5 if g else n0, 11.5, 0.5], [n1 if g else n1 - .5, 13.5, 1], 'tiroir'))   # grand tiroir central
    hx_ = 15.5 if g else 0
    l.append(b([hx_, 12.3, 0], [hx_ + .5, 12.8, 0.5], 'air'))                            # poignée au milieu du bureau
    l.append(b([n0, 2, 14], [n1, 11, 15], 'panneau'))                                    # panneau de fond
    if g:                                                                               # lampe de bureau d'airain
        l.append(b([2, 16, 10], [5, 16.5, 13], 'air')); l.append(b([3.2, 16.5, 11.2], [3.8, 21, 11.8], 'air'))
        l.append(b([2, 21, 9.5], [6, 22.5, 12.5], {'*': 'air', 'down': 'bande'}))
    else:
        l.append(b([11.5, 16, 10], [13.5, 18, 12], 'air'))                               # encrier
        l.append(b([4, 16, 4], [10, 16.2, 8], {'*': 'bois', 'up': 'marbre'}))            # feuillet
    return l
