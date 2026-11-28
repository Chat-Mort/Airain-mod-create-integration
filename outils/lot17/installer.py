# Petits vitraux (1.72) : 16 couleurs x 2 dessins de plombs (losanges, carreaux) ; panneau fin, cadre doré sur les côtés libres
import sys, json, os; sys.path.insert(0, '/home/claude/travail/lot12'); sys.path.insert(0, '/home/claude/travail/lot9')
from px import hx
from PIL import Image
from proj import boite
R = '/home/claude/airain-mod-create-integration/src/main/resources/'
AS = R + 'assets/airain/'; DA = R + 'data/airain/'
def ecrire(p, o): os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(o, open(p, 'w'), indent=1, ensure_ascii=False)
PLOMB = [hx('fff0c4'), hx('e1ba6e'), hx('a8763c'), hx('5a3a1e')]
# teintes des 16 couleurs du jeu (couleur de teinture), opacité réglée pour garder la vue au travers
COUL = [('white', 'f9fffe', 'blanc', 'White'), ('orange', 'f9801d', 'orange', 'Orange'), ('magenta', 'c74ebd', 'magenta', 'Magenta'),
        ('light_blue', '3ab3da', 'bleu clair', 'Light Blue'), ('yellow', 'fed83d', 'jaune', 'Yellow'), ('lime', '80c71f', 'vert clair', 'Lime'),
        ('pink', 'f38baa', 'rose', 'Pink'), ('gray', '474f52', 'gris', 'Gray'), ('light_gray', '9d9d97', 'gris clair', 'Light Gray'),
        ('cyan', '169c9c', 'cyan', 'Cyan'), ('purple', '8932b8', 'violet', 'Purple'), ('blue', '3c44aa', 'bleu', 'Blue'),
        ('brown', '835432', 'marron', 'Brown'), ('green', '5e7c16', 'vert', 'Green'), ('red', 'b02e26', 'rouge', 'Red'), ('black', '1d1d21', 'noir', 'Black')]
DESSINS = [('diamond', 'à losanges', 'Diamond'), ('square', 'à carreaux', 'Square')]
def verre(c, a, x, y):
    r, g, b, _ = hx(c); k = ((x * 7 + y * 13) % 11) / 10.0
    f = 1.0 + 0.10 * (k - 0.5) + (0.18 if (x + y) < 6 and (x * 3 + y) % 5 == 0 else 0)
    return (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
def tex(c, dessin):
    a = 150 if c in ('f9fffe', '9d9d97') else 195
    im = Image.new('RGBA', (16, 16)); p = im.load()
    for y in range(16):
        for x in range(16):
            p[x, y] = verre(c, a, x, y)
            if dessin == 'diamond' and ((x + y) % 8 == 0 or (x - y) % 8 == 0): p[x, y] = PLOMB[2]
            if dessin == 'square' and (x % 8 == 0 or y % 8 == 0): p[x, y] = PLOMB[2]
    return im
def cadre():
    im = Image.new('RGBA', (16, 16), PLOMB[1]); p = im.load()
    for i in range(16):
        p[i, 0] = PLOMB[0]; p[i, 1] = PLOMB[1]; p[i, 15] = PLOMB[3]; p[i, 14] = PLOMB[2]
        p[0, i] = PLOMB[0]; p[1, i] = PLOMB[1]; p[15, i] = PLOMB[3]; p[14, i] = PLOMB[2]
    return im
os.makedirs(AS + 'textures/block/leaded_glass', exist_ok=True)
cadre().save(AS + 'textures/block/leaded_glass/frame.png')
# modèles communs : cadres (haut, bas, gauche = x bas, droite = x haut), panneau dans le plan x-y (normale selon z)
def m(nom, el, tx):
    for e in el:
        for f in e['faces'].values(): f['uv'] = [round(v, 3) for v in f['uv']]
    ecrire(AS + 'models/block/' + nom + '.json', {'parent': 'block/block', 'render_type': 'minecraft:translucent', 'textures': tx, 'elements': el})
FR = {'cadre': 'airain:block/leaded_glass/frame', 'particle': 'airain:block/leaded_glass/frame'}
CADRES = {'up': ([0, 14, 6.9], [16, 16, 9.1]), 'down': ([0, 0, 6.9], [16, 2, 9.1]), 'left': ([0, 0, 6.9], [2, 16, 9.1]), 'right': ([14, 0, 6.9], [16, 16, 9.1])}
for k, (f, t) in CADRES.items(): m('leaded_glass_frame_' + k, [boite(f, t, 'cadre')], FR)
def panneau():
    e = boite([0, 0, 7], [16, 16, 9], 'verre')
    for k, cf in (('west', 'west'), ('east', 'east'), ('up', 'up'), ('down', 'down')): e['faces'][k]['cullface'] = cf
    return e
noms_fr, noms_en, blocs = {}, {}, []
for cid, hexa, cfr, cen in COUL:
    for did, dfr, den in DESSINS:
        n = '%s_%s_leaded_glass' % (cid, did); blocs.append(n)
        tex(hexa, did).save(AS + 'textures/block/leaded_glass/%s_%s.png' % (cid, did))
        tx = {'verre': 'airain:block/leaded_glass/%s_%s' % (cid, did), 'particle': 'airain:block/leaded_glass/%s_%s' % (cid, did)}
        m(n, [panneau()], tx)
        # objet : le panneau et ses quatre cadres
        el = [panneau()] + [boite(f, t, 'cadre') for f, t in CADRES.values()]
        m(n + '_full', el, dict(tx, cadre=FR['cadre']))
        ecrire(AS + 'models/item/' + n + '.json', {'parent': 'airain:block/' + n + '_full'})
        parts = []
        for ax, y in (('z', 0), ('x', 90)):
            base = {'model': 'airain:block/' + n}
            if y: base['y'] = y
            parts.append({'when': {'axis': ax}, 'apply': base})
            for k in CADRES:
                a = {'model': 'airain:block/leaded_glass_frame_' + k}
                if y: a['y'] = y
                parts.append({'when': {'axis': ax, k: 'false'}, 'apply': a})
        ecrire(AS + 'blockstates/' + n + '.json', {'multipart': parts})
        ecrire(DA + 'loot_table/blocks/' + n + '.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1, 'bonus_rolls': 0,
               'entries': [{'type': 'minecraft:item', 'name': 'airain:' + n}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}]})
        noms_fr['block.airain.' + n] = 'Vitrail %s %s' % (dfr, cfr)
        noms_en['block.airain.' + n] = '%s %s Leaded Glass' % (cen, den)
    # recettes : 8 vitres teintées autour d'une pépite d'airain -> 8 vitraux à losanges ; tailleur : losanges <-> carreaux
    ecrire(DA + 'recipe/%s_diamond_leaded_glass.json' % cid, {'type': 'minecraft:crafting_shaped', 'category': 'building', 'group': 'leaded_glass',
           'pattern': ['GGG', 'GNG', 'GGG'], 'key': {'G': {'item': 'minecraft:%s_stained_glass_pane' % cid}, 'N': {'item': 'airain:airain_nugget'}},
           'result': {'id': 'airain:%s_diamond_leaded_glass' % cid, 'count': 8}})
    for a, b in (('diamond', 'square'), ('square', 'diamond')):
        ecrire(DA + 'recipe/%s_%s_leaded_glass_stonecutting.json' % (cid, b), {'type': 'minecraft:stonecutting',
               'ingredient': {'item': 'airain:%s_%s_leaded_glass' % (cid, a)}, 'result': {'id': 'airain:%s_%s_leaded_glass' % (cid, b), 'count': 1}})
json.dump({'blocs': blocs, 'fr': noms_fr, 'en': noms_en}, open('/tmp/mob/vitraux_noms.json', 'w'), ensure_ascii=False)
for f, d in (('assets/airain/lang/fr_fr.json', noms_fr), ('assets/airain/lang/en_us.json', noms_en)):
    t = open(R + f, encoding='utf-8').read(); j = json.loads(t)
    add = ''.join(',\n %s: %s' % (json.dumps(k), json.dumps(v, ensure_ascii=False)) for k, v in d.items() if k not in j)
    t = t.rstrip()[:-1].rstrip() + add + '\n}\n'; json.loads(t); open(R + f, 'w', encoding='utf-8').write(t)
print(len(blocs), 'vitraux')
