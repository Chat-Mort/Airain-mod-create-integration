# Maquette lot 12, passe 2 : formes de référence recolorées en airain à patine rouge, câble, rouage, portillon en 3D
import sys, json, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, '/home/claude/travail/lot9')
from PIL import Image, ImageDraw, ImageFont
from patine import recolorer, C, ORIG
import passe2, objets2, portillon3d
from proj import rendre
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
K = '/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/'
M = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
W, H = 1500, 1000
im = Image.new('RGBA', (W, H), (52, 54, 60, 255)); d = ImageDraw.Draw(im)
d.text((20, 14), "Objets, passe 2 — formes de référence, airain à patine rouge (ombres cuivrées, reflets rouge impérial)", font=F, fill=(240, 220, 160))
def case(x, y, tex, k=3):
    d.rectangle([x, y, x + 18 * k - 1, y + 18 * k - 1], fill=(139, 139, 139))
    d.line([(x, y), (x + 18 * k - 1, y)], fill=(55, 55, 55), width=k); d.line([(x, y), (x, y + 18 * k - 1)], fill=(55, 55, 55), width=k)
    d.line([(x, y + 18 * k - 1), (x + 18 * k - 1, y + 18 * k - 1)], fill=(255, 255, 255), width=k); d.line([(x + 18 * k - 1, y), (x + 18 * k - 1, y + 18 * k - 1)], fill=(255, 255, 255), width=k)
    im.alpha_composite(tex.resize((16 * k, 16 * k), Image.NEAREST) if tex.size[0] == 16 else tex.resize((16 * k, 16 * k), Image.LANCZOS), (x + k, y + k))
def bloc(x, y, titre, sous, paires):
    w = 30 + len(paires) * 170
    d.rectangle([x, y, x + w, y + 300], fill=(70, 72, 80))
    d.text((x + 10, y + 8), titre, font=F, fill=(240, 220, 160)); d.text((x + 10, y + 30), sous, font=FP, fill=(190, 190, 190))
    for k, (t, tex) in enumerate(paires):
        xx = x + 15 + k * 170
        d.rectangle([xx, y + 54, xx + 160, y + 214], fill=(139, 139, 139))
        im.alpha_composite(tex.resize((128, 128), Image.NEAREST), (xx + 16, y + 70))
        d.text((xx + 4, y + 218), t, font=FP, fill=(200, 200, 200)); case(xx + 52, y + 238, tex)
    return w
pl_or = recolorer(Image.open(C + 'golden_sheet.png')); pl_la = recolorer(Image.open(C + 'brass_sheet.png'))
x = 20
x += bloc(x, 50, "Plaque d'airain", "Formes de Create : A (or, fer), B (laiton)", [("A", pl_or), ("B", pl_la)]) + 15
x += bloc(x, 50, "Lingot", "Forme d'origine gardée", [("avant", Image.open(ORIG + 'airain_ingot.png').convert('RGBA')), ("après", recolorer(Image.open(ORIG + 'airain_ingot.png')))]) + 15
bloc(x, 50, "Pépite", "Forme d'origine gardée", [("avant", Image.open(ORIG + 'airain_nugget.png').convert('RGBA')), ("après", recolorer(Image.open(ORIG + 'airain_nugget.png')))])
x = 20
x += bloc(x, 370, "Fil d'airain", "Forme d'origine, couleurs de la patine", [("avant", Image.open(ORIG + 'airain_wire.png').convert('RGBA')), ("après", recolorer(Image.open(ORIG + 'airain_wire.png')))]) + 15
x += bloc(x, 370, "Câble d'airain", "Spires de métal, plus de quadrillage", [("passe 1", objets2.__dict__.get('x') or __import__('objets').cable()), ("passe 2", passe2.cable())]) + 15
bloc(x, 370, "Rouage brisé", "Dents carrées comme les rouages de Create", [("passe 1", objets2.rouage_brise()), ("passe 2", passe2.rouage_brise())])
# portillon : en 3D comme le reste du jeu de passerelles
y = 690
d.rectangle([20, y, 1480, y + 290], fill=(70, 72, 80))
d.text((30, y + 8), "Portillon de passerelle — objet en 3D comme le reste du jeu (passerelle, palier, pont-levis), le portillon seul et recentré", font=F, fill=(240, 220, 160))
def charge(m):
    tx = {k: np.array(Image.open(M + 'textures/' + v.split(':')[1] + '.png').convert('RGBA').crop((0, 0, 16, 16))) for k, v in m['textures'].items()}
    for e in m['elements']:
        for fc in e['faces'].values(): fc.setdefault('uv', [0, 0, 16, 16])
    return m['elements'], tx
rend = []
for n in ('airain_catwalk_item', 'airain_catwalk_landing_item', 'airain_catwalk_drawbridge_item'):
    rend.append(({'airain_catwalk_item': 'passerelle', 'airain_catwalk_landing_item': 'palier', 'airain_catwalk_drawbridge_item': 'pont-levis'}[n], charge(json.load(open(M + 'models/block/' + n + '.json')))))
rend.append(("portillon (nouveau)", charge(portillon3d.modele())))
d.rectangle([40, y + 40, 200, y + 200], fill=(139, 139, 139)); im.alpha_composite(Image.open(T + 'airain_catwalk_gate.png').convert('RGBA').resize((128, 128), Image.NEAREST), (56, y + 56))
d.text((44, y + 205), "portillon (avant, à plat)", font=FP, fill=(200, 200, 200))
for k, (n, (el, tx)) in enumerate(rend):
    xx = 260 + k * 300
    d.rectangle([xx, y + 40, xx + 260, y + 270], fill=(139, 139, 139))
    im.alpha_composite(rendre(el, tx, {'vue': [30, 225], 'scale': [0.8 if k == 3 else 0.625] * 3}, 230), (xx + 15, y + 40))
    d.text((xx + 6, y + 252), n, font=FP, fill=(30, 30, 30))
im.convert('RGB').save('/mnt/user-data/outputs/item_textures_mockup_2.png')
