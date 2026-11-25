# Installe le relais cinétique d'airain : textures, trois modèles (émetteur, récepteur, éteint), états (6 faces x mode x œil), objet
import sys, json, copy, os
sys.path.insert(0, '.'); sys.path.insert(0, '/home/claude/travail/lot9')
import rtex2
from rmod2 import relais
M = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
for k, im in rtex2.TEX.items(): im.save(M + 'textures/block/kinetic_relay_' + k + '.png')
LUMINEUX = ('oeil', 'coeur', 'dessus')

def miroir(e, allume):
    """La maquette regarde le sud ; Minecraft dessine face au nord : miroir en z (faces nord et sud échangées)."""
    e = copy.deepcopy(e); f, t = e['from'], e['to']
    e['from'], e['to'] = [f[0], f[1], 16 - t[2]], [t[0], t[1], 16 - f[2]]
    x1, y1, z1 = e['from']; x2, y2, z2 = e['to']
    auto = {'north': (16 - x2, 16 - y2, 16 - x1, 16 - y1), 'south': (x1, 16 - y2, x2, 16 - y1), 'west': (z1, 16 - y2, z2, 16 - y1),
            'east': (16 - z2, 16 - y2, 16 - z1, 16 - y1), 'up': (x1, z1, x2, z2), 'down': (x1, 16 - z2, x2, 16 - z1)}
    fs = {}
    for nom, fc in e['faces'].items():
        nn = {'north': 'south', 'south': 'north'}.get(nom, nom)
        tex = fc['texture'].lstrip('#')
        uv = list(fc['uv']) if tex in ('coin', 'shaft') else list(auto[nn])
        d = {'texture': '#' + tex, 'uv': [round(v, 3) for v in uv]}
        if allume and tex in LUMINEUX: d['neoforge_data'] = {'block_light': 15, 'sky_light': 15}
        fs[nn] = d
    e['faces'] = fs
    return e

def modele(oeil):
    allume = oeil != 'oeil_off'
    tx = {k: 'airain:block/kinetic_relay_' + k for k in ('arete', 'coin', 'coeur', 'dos', 'dessus')}
    tx['oeil'] = 'airain:block/kinetic_relay_' + oeil
    tx['particle'] = 'airain:block/kinetic_relay_arete'
    el = [miroir(e, allume) for e in relais() if e['faces'][next(iter(e['faces']))]['texture'] != '#shaft']   # l'arbre est dessiné par Create
    return {'parent': 'block/block', 'textures': tx, 'elements': el}

os.makedirs(M + 'models/block/kinetic_relay', exist_ok=True)
for nom, oeil in (('emitter', 'oeil'), ('receiver', 'oeil_r'), ('off', 'oeil_off')):
    json.dump(modele(oeil), open(M + 'models/block/kinetic_relay/' + nom + '.json', 'w'), indent=1)
ROT = {'north': {}, 'south': {'y': 180}, 'east': {'y': 90}, 'west': {'y': 270}, 'up': {'x': 270}, 'down': {'x': 90}}
v = {}
for f, r in ROT.items():
    for rec in ('false', 'true'):
        for ouv in ('false', 'true'):
            nom = 'off' if ouv == 'false' else ('receiver' if rec == 'true' else 'emitter')
            v['facing=%s,open=%s,receiver=%s' % (f, ouv, rec)] = {'model': 'airain:block/kinetic_relay/' + nom} | r
json.dump({'variants': v}, open(M + 'blockstates/kinetic_relay.json', 'w'), indent=1)
json.dump({'parent': 'airain:block/kinetic_relay/emitter'}, open(M + 'models/item/kinetic_relay.json', 'w'), indent=1)
print('ok', len(v))
