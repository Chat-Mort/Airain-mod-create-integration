# Installe la table du carreleur en relief : textures dédiées et modèle à éléments (avant au nord)
import sys, json; sys.path.insert(0, '.')
import bloc3d
from PIL import Image
from px import hx
M = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
NOMS = {'damier': 'tilers_table_tiles', 'caisson': 'tilers_table_panel', 'cote': 'tilers_table_panel_sample', 'tiroir': 'tilers_table_drawer', 'carton': 'tilers_table_card'}
for k, n in NOMS.items(): bloc3d.TEX[k].save(M + 'textures/block/' + n + '.png')
TX = {k: 'airain:block/' + n for k, n in NOMS.items()}
TX.update(air='airain:block/airain_block', bande='airain:block/airain_band', pilier='airain:block/airain_band', particle='airain:block/airain_band')
def propre(uv):
    u1, v1, u2, v2 = uv
    if min(uv) < 0 or max(uv) > 16:                                   # petit élément qui dépasse du bloc : uv ramenés dans la texture
        w, h = abs(u2 - u1), abs(v2 - v1); return [0, 0, round(w, 3), round(h, 3)]
    return [round(x, 3) for x in uv]
el = []
for e in bloc3d.modele():
    fs = {}
    for nom, fc in e['faces'].items():
        tex = fc['texture'].lstrip('#')
        d = {'texture': '#' + tex, 'uv': propre(list(fc['uv']))}
        if tex == 'pilier' and nom in ('north', 'south', 'east', 'west'): d['rotation'] = 90      # bande d'airain posée à la verticale
        fs[nom] = d
    el.append({'from': [round(v, 3) for v in e['from']], 'to': [round(v, 3) for v in e['to']], 'faces': fs})
json.dump({'parent': 'block/block', 'textures': TX, 'elements': el}, open(M + 'models/block/tilers_table.json', 'w'), indent=1)
print(len(el), 'éléments')
