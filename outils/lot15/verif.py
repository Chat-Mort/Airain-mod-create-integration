# Vérification : rendu des blocs installés à partir des états et modèles JSON (scènes raccordées)
import sys, json, copy; sys.path.insert(0, '/home/claude/travail/lot9')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from proj import rendre
AS = '/home/claude/airain-mod-create-integration/src/main/resources/assets/'
TX = {}
def tex(ref):
    ns, p = ref.split(':')
    if ref not in TX: TX[ref] = np.array(Image.open(AS + ns + '/textures/' + p + '.png').convert('RGBA').crop((0, 0, 16, 16)))
    return ref
def modele(nom):
    j = json.load(open(AS + 'airain/models/' + nom.split(':')[1] + '.json'))
    el = copy.deepcopy(j.get('elements', []))
    for e in el:
        for f in e['faces'].values(): f['texture'] = '#' + tex(j['textures'][f['texture'].lstrip('#')])
    return el
ROT = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}
def tourne(el, y):
    for _ in range(y // 90):
        for e in el:
            (x1, y1, z1), (x2, y2, z2) = e['from'], e['to']
            e['from'], e['to'] = [16 - z2, y1, x1], [16 - z1, y2, x2]
            e['faces'] = {ROT.get(k, k): v for k, v in e['faces'].items()}
    return el
def bloc(nom, etat):
    bs = json.load(open(AS + 'airain/blockstates/' + nom + '.json')); el = []
    if 'variants' in bs:
        for k, v in bs['variants'].items():
            if dict(p.split('=') for p in k.split(',')) == etat: el += tourne(modele(v['model']), v.get('y', 0))
    else:
        for p in bs['multipart']:
            if all(etat.get(a) == b for a, b in p['when'].items()): el += tourne(modele(p['apply']['model']), p['apply'].get('y', 0))
    return el
def scene(blocs, sc, ang=(28, 150), N=360, dx=0, dy=0, dz=0):
    el = []
    for (x, y, z), nom, etat in blocs:
        for e in bloc(nom, etat):
            e['from'] = [e['from'][0] + 16 * x + dx, e['from'][1] + 16 * y + dy, e['from'][2] + 16 * z + dz]
            e['to'] = [e['to'][0] + 16 * x + dx, e['to'][1] + 16 * y + dy, e['to'][2] + 16 * z + dz]
            el.append(e)
    return rendre(el, TX, {'vue': list(ang), 'scale': [sc] * 3}, N)
def T(n, e, s, w): return dict(north=n, east=e, south=s, west=w)
tf, tt = 'false', 'true'
S = []
S.append(('Table 2 x 3', scene([((x, 0, z), 'imperial_table', T(tf if z == 0 else tt, tt if x < 2 else tf, tt if z == 0 else tf, tt if x > 0 else tf)) for x in range(3) for z in range(2)], .22, dx=-16, dz=-8)))
S.append(('Bench x 5 (legs every 3)', scene([((x, 0, 0), 'imperial_bench', dict(facing='north', left=tt if x > 0 else tf, right=tt if x < 4 else tf, legs=tt if 0 < x < 4 and x % 3 == 0 else tf)) for x in range(5)], .17, dx=-32)))
S.append(('Desk pair (facing south)', scene([((0, 0, 0), 'imperial_desk', dict(facing='south', part='right')), ((1, 0, 0), 'imperial_desk', dict(facing='south', part='left'))], .33, dx=-8)))
S.append(('Wardrobe + armchair (east)', scene([((0, 0, 0), 'imperial_wardrobe', dict(facing='east', half='lower')), ((0, 0, 1), 'command_armchair', dict(facing='east', half='lower'))], .3, dy=-8, dz=-8)))
W = Image.new('RGBA', (4 * 370, 400), (139, 139, 139, 255)); d = ImageDraw.Draw(W); F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
for i, (n, im) in enumerate(S): W.alpha_composite(im, (i * 370 + 5, 35)); d.text((i * 370 + 10, 8), n, font=F, fill=(255, 255, 255))
W.save('/tmp/mob/verif.png')
