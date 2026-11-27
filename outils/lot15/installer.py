# Mobilier impérial : textures, modèles, états, objets, butins, recettes, étiquettes
import sys, json, os, copy; sys.path.insert(0, '/home/claude/travail/lot9'); sys.path.insert(0, '/home/claude/travail/lot15')
import tex as T, modeles as M
from proj import boite
R = '/home/claude/airain-mod-create-integration/src/main/resources/'
AS = R + 'assets/airain/'; DA = R + 'data/airain/'
def ecrire(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(o, open(p, 'w'), indent=1, ensure_ascii=False)
# ---- textures (noms anglais) ; airain et marbre : textures du pack
NOMS = dict(bois='furniture_wood', boisv='furniture_wood_vertical', cuir='furniture_leather_tufted', cuirl='furniture_leather',
            clous='furniture_leather_studded', panneau='furniture_panel', tiroir='furniture_drawer', livres='furniture_books')
for k, n in NOMS.items(): T.TEX[k].save(AS + 'textures/block/' + n + '.png')
REF = dict(NOMS, air='airain_block', bande='airain_band', marbre='white_marble_0')
# plateaux de table : 16 combinaisons de bords (n, e, s, w = côté non raccordé)
for m in range(16):
    bords = ''.join(c for i, c in enumerate('nesw') if m >> i & 1)
    T.t_plateau(bords).save(AS + 'textures/block/furniture_table_top_%d.png' % m)
for k, bords in (('', 'nesw'), ('_left', 'nsw'), ('_right', 'nse')):
    T.t_plateau(bords, 'cuir').save(AS + 'textures/block/furniture_desk_top%s.png' % k)
def modele(nom, el, particule='furniture_wood', display=None):
    el = copy.deepcopy(el); tx = {}
    for e in el:
        for f in e['faces'].values():
            t = f['texture'].lstrip('#')
            if t.startswith('plateau') or t.startswith('bureau'):
                vrai = {'plateau': 'furniture_table_top_15', 'plateau_w': 'furniture_table_top_%d' % (1 | 2 | 4), 'plateau_m': 'furniture_table_top_5',
                        'plateau_e': 'furniture_table_top_%d' % (1 | 4 | 8), 'bureau': 'furniture_desk_top', 'bureau_g': 'furniture_desk_top_left', 'bureau_d': 'furniture_desk_top_right'}.get(t, t)
            else: vrai = REF[t]
            tx[t] = 'airain:block/' + vrai
            f['uv'] = [round(v, 3) for v in f['uv']]
        e['from'] = [round(v, 3) for v in e['from']]; e['to'] = [round(v, 3) for v in e['to']]
    tx['particle'] = 'airain:block/' + particule
    o = {'parent': 'block/block', 'textures': tx, 'elements': el}
    if display: o['display'] = display
    ecrire(AS + 'models/block/' + nom + '.json', o)
GRAND = {'gui': {'rotation': [30, 225, 0], 'translation': [0, -3, 0], 'scale': [0.42] * 3},
         'ground': {'rotation': [0, 0, 0], 'translation': [0, 3, 0], 'scale': [0.2] * 3},
         'fixed': {'rotation': [0, 0, 0], 'translation': [0, -4, 0], 'scale': [0.4] * 3},
         'thirdperson_righthand': {'rotation': [75, 45, 0], 'translation': [0, 2.5, 0], 'scale': [0.3] * 3},
         'firstperson_righthand': {'rotation': [0, 45, 0], 'translation': [0, -2, 0], 'scale': [0.3] * 3}}
def facing(modele_, extra=''):
    v = {}
    for d, y in (('north', 0), ('east', 90), ('south', 180), ('west', 270)):
        e = {'model': 'airain:block/' + modele_}
        if y: e['y'] = y
        v['facing=' + d + extra] = e
    return v
def objet(nom, parent): ecrire(AS + 'models/item/' + nom + '.json', {'parent': 'airain:block/' + parent})
def butin(nom, double=False):
    p = {'rolls': 1, 'bonus_rolls': 0, 'entries': [{'type': 'minecraft:item', 'name': 'airain:' + nom}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}
    if double: p['conditions'].append({'condition': 'minecraft:block_state_property', 'block': 'airain:' + nom, 'properties': {'half': 'lower'}})
    ecrire(DA + 'loot_table/blocks/' + nom + '.json', {'type': 'minecraft:block', 'pools': [p]})
vide = {'parent': 'block/block', 'textures': {'particle': 'airain:block/furniture_wood'}, 'elements': []}

# ---- chaise
modele('imperial_chair', M.chaise())
ecrire(AS + 'blockstates/imperial_chair.json', {'variants': facing('imperial_chair')}); objet('imperial_chair', 'imperial_chair')
# ---- fauteuil de commandement (deux blocs : le haut ne porte pas de géométrie)
modele('command_armchair', M.fauteuil(), display=GRAND); ecrire(AS + 'models/block/command_armchair_top.json', vide)
v = facing('command_armchair', ',half=lower'); v.update({k.replace('lower', 'upper'): {'model': 'airain:block/command_armchair_top'} for k in v})
ecrire(AS + 'blockstates/command_armchair.json', {'variants': v}); objet('command_armchair', 'command_armchair')
# ---- banc : bouts (joues), milieu, milieu à pieds (tous les trois blocs)
def pieds_milieu():
    l = []
    for z in (4, 10):
        l.append(boite([6.7, 0, z - .3], [9.3, 1, z + 2.3], 'air')); l.append(boite([7, 1, z], [9, 6, z + 2], 'boisv'))
    return l
for nom, el in (('imperial_bench', M.banc(True, True)), ('imperial_bench_left', M.banc(True, False)), ('imperial_bench_right', M.banc(False, True)),
                ('imperial_bench_middle', M.banc(False, False)), ('imperial_bench_middle_legs', M.banc(False, False) + pieds_milieu())):
    modele(nom, el)
v = {}
for d, y in (('north', 0), ('east', 90), ('south', 180), ('west', 270)):
    for l_ in ('false', 'true'):
        for r_ in ('false', 'true'):
            for pi in ('false', 'true'):
                n = 'imperial_bench' + ({('false', 'false'): '', ('false', 'true'): '_left', ('true', 'false'): '_right', ('true', 'true'): '_middle'}[(l_, r_)])
                if n.endswith('_middle') and pi == 'true': n += '_legs'
                e = {'model': 'airain:block/' + n}
                if y: e['y'] = y
                v['facing=%s,left=%s,legs=%s,right=%s' % (d, l_, pi, r_)] = e
ecrire(AS + 'blockstates/imperial_bench.json', {'variants': v}); objet('imperial_bench', 'imperial_bench')
# ---- table : plateau selon les bords, ceinture par côté libre, pied à chaque coin libre (multipart)
import itertools
for m in range(16):
    modele('imperial_table_top_%d' % m, [boite([0, 14, 0], [16, 16, 16], {'*': 'bois', 'up': 'plateau'})])
    j = json.load(open(AS + 'models/block/imperial_table_top_%d.json' % m)); j['textures']['plateau'] = 'airain:block/furniture_table_top_%d' % m
    ecrire(AS + 'models/block/imperial_table_top_%d.json' % m, j)
# ceinture nord (z bas) ; les autres côtés : même modèle tourné ; prolongée jusqu'au bord quand le côté voisin est raccordé
for g in (0, 1):
    for d in (0, 1):
        x0, x1 = (1 if g else 0), (15 if d else 16)
        el = [boite([x0, 12, 1], [x1, 14, 2], 'bois')]
        if g and d: el.append(boite([7, 12.5, 0.6], [9, 13.5, 1], 'air'))      # écusson : seulement au milieu d'un côté entier
        modele('imperial_table_apron_%d%d' % (g, d), el)
leg = []; M.pieds(leg, ((1, 1),), 12, cerclage=9); modele('imperial_table_leg', leg)
parts = []
for m in range(16):
    parts.append({'when': {k: ('true' if not (m >> i & 1) else 'false') for i, k in enumerate(('north', 'east', 'south', 'west'))},
                  'apply': {'model': 'airain:block/imperial_table_top_%d' % m}})
# côté libre (non raccordé) -> ceinture ; rotation y : nord 0, est 90, sud 180, ouest 270 ; « gauche » du côté = sens antihoraire
COTES = (('north', 0, 'west', 'east'), ('east', 90, 'north', 'south'), ('south', 180, 'east', 'west'), ('west', 270, 'south', 'north'))
for cote, y, gauche, droite in COTES:
    for g in ('false', 'true'):
        for d in ('false', 'true'):
            # g/d : le voisin à gauche/droite est-il libre ? libre -> ceinture en retrait (1) ; raccordé -> jusqu'au bord (0)
            e = {'model': 'airain:block/imperial_table_apron_%d%d' % (g == 'false', d == 'false')}
            if y: e['y'] = y
            parts.append({'when': {cote: 'false', gauche: 'true' if g == 'true' else 'false', droite: 'true' if d == 'true' else 'false'}, 'apply': e})
for cote, y, gauche, droite in COTES:   # pied au coin nord-ouest du côté tourné
    e = {'model': 'airain:block/imperial_table_leg'}
    if y: e['y'] = y
    parts.append({'when': {cote: 'false', gauche: 'false'}, 'apply': e})
ecrire(AS + 'blockstates/imperial_table.json', {'multipart': parts})
modele('imperial_table_item', M.table()); objet('imperial_table', 'imperial_table_item')
# ---- bureau : seul, moitié gauche, moitié droite
modele('imperial_desk', M.bureau()); modele('imperial_desk_left', M.bureau2('gauche')); modele('imperial_desk_right', M.bureau2('droite'))
v = {}
for part, n in (('single', 'imperial_desk'), ('left', 'imperial_desk_left'), ('right', 'imperial_desk_right')):
    v.update(facing(n, ',part=' + part))
ecrire(AS + 'blockstates/imperial_desk.json', {'variants': {k: v[k] for k in v}}); objet('imperial_desk', 'imperial_desk')
# ---- étagère : le meuble seul (les objets posés sont rendus par l'entité)
el = [e for e in M.etagere() if not any(f['texture'] in ('#livres',) for f in e['faces'].values())]
el = el[:-1] if False else [e for e in el if e['from'] != [10, 8.5, 8]]
modele('imperial_shelf', el); ecrire(AS + 'blockstates/imperial_shelf.json', {'variants': facing('imperial_shelf')}); objet('imperial_shelf', 'imperial_shelf')
# ---- armoire (deux blocs)
modele('imperial_wardrobe', M.armoire(), display=GRAND); ecrire(AS + 'models/block/imperial_wardrobe_top.json', vide)
v = facing('imperial_wardrobe', ',half=lower'); v.update({k.replace('lower', 'upper'): {'model': 'airain:block/imperial_wardrobe_top'} for k in v})
ecrire(AS + 'blockstates/imperial_wardrobe.json', {'variants': v}); objet('imperial_wardrobe', 'imperial_wardrobe')
# ---- butins
for n in ('imperial_chair', 'imperial_bench', 'imperial_table', 'imperial_desk', 'imperial_shelf'): butin(n)
for n in ('command_armchair', 'imperial_wardrobe'): butin(n, True)
# ---- recettes (établi) : noyer = chêne noir, cuir rouge = laine rouge ou cuir
P, N, S, W, L = 'minecraft:dark_oak_planks', 'airain:airain_nugget', 'airain:airain_sheet', 'minecraft:red_wool', 'minecraft:leather'
def recette(nom, motif, cles, n=1):
    ecrire(DA + 'recipe/' + nom + '.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': motif,
           'key': {k: {'item': v} for k, v in cles.items()}, 'result': {'id': 'airain:' + nom, 'count': n}})
recette('imperial_chair', ['P N', 'PWP', 'P P'], {'P': P, 'N': N, 'W': W}, 2)
recette('command_armchair', ['NSN', 'WCW', 'P P'], {'N': N, 'S': S, 'W': W, 'C': 'airain:imperial_chair', 'P': P})
recette('imperial_bench', ['WWW', 'PSP', 'P P'], {'W': W, 'P': P, 'S': S}, 3)
recette('imperial_table', ['PMP', 'NSN', 'P P'], {'P': P, 'M': 'airain:polished_white_marble', 'N': N, 'S': S}, 2)
recette('imperial_desk', ['PLP', 'NCN', 'P P'], {'P': P, 'L': L, 'N': N, 'C': 'minecraft:chest'})
recette('imperial_shelf', ['PSP', 'P P', 'PSP'], {'P': P, 'S': S}, 2)
recette('imperial_wardrobe', ['PSP', 'NCN', 'PSP'], {'P': P, 'S': S, 'N': N, 'C': 'minecraft:chest'})
# ---- étiquettes : à la hache
t = json.load(open(R + 'data/minecraft/tags/block/mineable/axe.json'))
for n in ('imperial_chair', 'command_armchair', 'imperial_bench', 'imperial_table', 'imperial_desk', 'imperial_shelf', 'imperial_wardrobe'):
    if 'airain:' + n not in t['values']: t['values'].append('airain:' + n)
ecrire(R + 'data/minecraft/tags/block/mineable/axe.json', t)
print('ok')
