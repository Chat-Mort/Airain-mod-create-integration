# Installe le projecteur de chantier (allure A) : textures, modèles (éteint / allumé), états, objet ; et le cordeau de maçon
import sys, json, copy; sys.path.insert(0, '.')
from tex import TEX
from modeles import lyre
from cordeau import cordeau
M = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
NOMS = {'flanc': 'side', 'dessus': 'top', 'dessous': 'bottom', 'tete': 'head', 'bras': 'arm', 'l8': 'lens'}
for k, n in NOMS.items(): TEX[k].save(M + 'textures/block/worksite_projector_' + n + '.png')
TEX['l8_off'].save(M + 'textures/block/worksite_projector_lens_off.png')
cordeau().save(M + 'textures/item/chalk_line.png')

def miroir(e):
    """Le modèle de la maquette regarde le sud ; Minecraft dessine face au nord : miroir en z."""
    e = copy.deepcopy(e)
    f, t = e['from'], e['to']
    e['from'], e['to'] = [f[0], f[1], 16 - t[2]], [t[0], t[1], 16 - f[2]]
    fs = {}
    for nom, fc in e['faces'].items():
        nn = {'north': 'south', 'south': 'north'}.get(nom, nom)
        x1, y1, z1 = e['from']; x2, y2, z2 = e['to']
        auto = {'north': (16 - x2, 16 - y2, 16 - x1, 16 - y1), 'south': (x1, 16 - y2, x2, 16 - y1), 'west': (z1, 16 - y2, z2, 16 - y1),
                'east': (16 - z2, 16 - y2, 16 - z1, 16 - y1), 'up': (x1, z1, x2, z2), 'down': (x1, 16 - z2, x2, 16 - z1)}
        uv = list(fc['uv']) if fc['texture'] == '#l8' else list(auto[nn])
        d = {'texture': fc['texture'], 'uv': [round(v, 3) for v in uv]}
        if fc['texture'] == '#l8': d['neoforge_data'] = {'block_light': 15, 'sky_light': 15}
        fs[nn] = d
    e['faces'] = fs
    if 'rotation' in e:
        r = e['rotation']; o = r['origin']
        e['rotation'] = {'axis': r['axis'], 'angle': -r['angle'] if r['axis'] in ('x', 'y') else r['angle'], 'origin': [o[0], o[1], 16 - o[2]]}
    return e

def modele(allume):
    tx = {k: 'airain:block/worksite_projector_' + n for k, n in NOMS.items()}
    if not allume: tx['l8'] = 'airain:block/worksite_projector_lens_off'
    tx['particle'] = 'airain:block/worksite_projector_side'
    el = [miroir(e) for e in lyre()]
    if not allume:
        for e in el:
            for fc in e['faces'].values(): fc.pop('neoforge_data', None)
    return {'parent': 'block/block', 'textures': tx, 'elements': el}

import os
os.makedirs(M + 'models/block/worksite_projector', exist_ok=True)
json.dump(modele(False), open(M + 'models/block/worksite_projector/off.json', 'w'), indent=1)
json.dump(modele(True), open(M + 'models/block/worksite_projector/on.json', 'w'), indent=1)
v = {}
for f, y in (('north', 0), ('east', 90), ('south', 180), ('west', 270)):
    for l in ('false', 'true'):
        d = {'model': 'airain:block/worksite_projector/' + ('on' if l == 'true' else 'off')}
        if y: d['y'] = y
        v['facing=%s,lit=%s' % (f, l)] = d
json.dump({'variants': v}, open(M + 'blockstates/worksite_projector.json', 'w'), indent=1)
json.dump({'parent': 'airain:block/worksite_projector/on'}, open(M + 'models/item/worksite_projector.json', 'w'), indent=1)
json.dump({'parent': 'minecraft:item/handheld', 'textures': {'layer0': 'airain:item/chalk_line'}}, open(M + 'models/item/chalk_line.json', 'w'), indent=1)
print('ok')
