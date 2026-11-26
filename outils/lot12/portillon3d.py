# Portillon de passerelle : objet en 3D comme le reste du jeu de passerelles (le portillon seul, recentré)
import json, copy
M = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/'
def modele():
    m = json.load(open(M + 'airain_catwalk_gate_bottom.json'))
    el = copy.deepcopy(m['elements'])
    zs = [e['from'][2] for e in el] + [e['to'][2] for e in el]
    dz = 8 - (min(zs) + max(zs)) / 2
    ys = [e['from'][1] for e in el] + [e['to'][1] for e in el]
    dy = 8 - (min(ys) + max(ys)) / 2
    for e in el:
        e['from'] = [e['from'][0], e['from'][1] + dy, e['from'][2] + dz]; e['to'] = [e['to'][0], e['to'][1] + dy, e['to'][2] + dz]
        if 'rotation' in e: o = e['rotation']['origin']; e['rotation']['origin'] = [o[0], o[1] + dy, o[2] + dz]
    return {'parent': 'minecraft:block/block', 'textures': m['textures'], 'elements': el}
