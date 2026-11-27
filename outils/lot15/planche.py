import sys; sys.path.insert(0, '/home/claude/travail/lot9'); sys.path.insert(0, '/home/claude/travail/lot15')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from proj import rendre
from tex import TEX
import modeles as M
tx = {k: np.array(v) for k, v in TEX.items()}
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
def vue(el, sc, N=300, ang=(28, 150), dx=0, dy=0):
    for e in el:
        e['from'] = [e['from'][0] + dx, e['from'][1] + dy, e['from'][2]]; e['to'] = [e['to'][0] + dx, e['to'][1] + dy, e['to'][2]]
    return rendre(el, tx, {'vue': list(ang), 'scale': [sc] * 3}, N)
def dec(el, dx):
    return [dict(e, **{'from': [e['from'][0] + dx, *e['from'][1:]], 'to': [e['to'][0] + dx, *e['to'][1:]]}) for e in el]
if 'bureau' in sys.argv:
    W = Image.new('RGBA', (2 * 420, 380), (139, 139, 139, 255)); d = ImageDraw.Draw(W)
    for i, (n, im) in enumerate((('Desk, single block', vue(M.bureau(), .5, N=400)), ('Desk, 2 blocks joined', vue(M.bureau2('gauche') + dec(M.bureau2('droite'), 16), .36, N=400, dx=-8)))):
        W.alpha_composite(im, (i * 420 + 10, 0)); d.text((i * 420 + 16, 8), n, font=F, fill=(255, 255, 255))
    W.save('/tmp/mob/desk_v2.png'); sys.exit()
P = [('Chair', vue(M.chaise(), .5, dy=-5)), ('Command armchair', vue(M.fauteuil(), .42, dy=-8)),
     ('Bench (3 joined)', vue(M.banc(True, False) + [dict(e, **{'from': [e['from'][0] + 16, *e['from'][1:]], 'to': [e['to'][0] + 16, *e['to'][1:]]}) for e in M.banc(False, False)]
                              + [dict(e, **{'from': [e['from'][0] + 32, *e['from'][1:]], 'to': [e['to'][0] + 32, *e['to'][1:]]}) for e in M.banc(False, True)], .26, dx=-16)),
     ('Table', vue(M.table(), .5)),
     ('Long table (3 joined)', vue(M.table('nsw') + [dict(e, **{'from': [e['from'][0] + 16, *e['from'][1:]], 'to': [e['to'][0] + 16, *e['to'][1:]]}) for e in M.table('ns', False)]
                              + [dict(e, **{'from': [e['from'][0] + 32, *e['from'][1:]], 'to': [e['to'][0] + 32, *e['to'][1:]]}) for e in M.table('nse')], .26, dx=-16)),
     ('Desk', vue(M.bureau(), .5)), ('Shelf', vue(M.etagere(), .5)), ('Wardrobe (2 blocks)', vue(M.armoire(), .36, dy=-8))]
W = Image.new('RGBA', (4 * 310, 2 * 340), (139, 139, 139, 255)); d = ImageDraw.Draw(W)
for i, (n, im) in enumerate(P):
    x, y = (i % 4) * 310, (i // 4) * 340
    W.alpha_composite(im, (x + 5, y + 30)); d.text((x + 12, y + 6), n, font=F, fill=(255, 255, 255))
W.save('/tmp/mob/furniture_v1.png')
