# Maquette lot 12 : objets refaits (avant / après), à la taille du jeu (×3) et en grand (×8), dans des cases d'inventaire
import sys; sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
import objets, objets2
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
K = '/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/'
T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
L = [("Plaque d'airain", 'airain_sheet', objets.plaque, T), ("Lingot d'airain", 'airain_ingot', objets.lingot, T), ("Pépite d'airain", 'airain_nugget', objets.pepite, T),
     ("Fil d'airain", 'airain_wire', objets.fil, T), ("Câble d'airain", 'airain_cable', objets.cable, T), ("Rouage brisé", 'rouage_brise', objets2.rouage_brise, K),
     ("Nacelle", 'airain_gondola', objets2.nacelle, T), ("Portillon de passerelle", 'airain_catwalk_gate', objets2.portillon, T)]
W, H = 1500, 790
im = Image.new('RGBA', (W, H), (52, 54, 60, 255)); d = ImageDraw.Draw(im)
d.text((20, 14), "Objets refaits — avant / après, en grand (×8) et dans une case d'inventaire à l'échelle 3", font=F, fill=(240, 220, 160))
def case(x, y, tex, k=3):
    d.rectangle([x, y, x + 18 * k - 1, y + 18 * k - 1], fill=(139, 139, 139))
    d.line([(x, y), (x + 18 * k - 1, y)], fill=(55, 55, 55), width=k); d.line([(x, y), (x, y + 18 * k - 1)], fill=(55, 55, 55), width=k)
    d.line([(x, y + 18 * k - 1), (x + 18 * k - 1, y + 18 * k - 1)], fill=(255, 255, 255), width=k); d.line([(x + 18 * k - 1, y), (x + 18 * k - 1, y + 18 * k - 1)], fill=(255, 255, 255), width=k)
    im.alpha_composite(tex.resize((16 * k, 16 * k), Image.NEAREST), (x + k, y + k))
for i, (nom, f, fn, base) in enumerate(L):
    col, row = i % 4, i // 4
    x0, y0 = 20 + col * 370, 50 + row * 330
    avant = Image.open(base + f + '.png').convert('RGBA').crop((0, 0, 16, 16)); apres = fn()
    d.rectangle([x0, y0, x0 + 350, y0 + 300], fill=(70, 72, 80))
    d.text((x0 + 10, y0 + 8), nom, font=F, fill=(240, 220, 160))
    for k, (t, tex) in enumerate((("avant", avant), ("après", apres))):
        xx = x0 + 10 + k * 170
        d.rectangle([xx, y0 + 36, xx + 160, y0 + 196], fill=(139, 139, 139))
        im.alpha_composite(tex.resize((128, 128), Image.NEAREST), (xx + 16, y0 + 52))
        d.text((xx + 4, y0 + 200), t, font=FP, fill=(200, 200, 200))
        case(xx + 40, y0 + 222, tex)
# rangée de comparaison : les nouveaux à côté des objets les mieux réussis
y = 740
d.text((20, y - 22), "À côté des objets de référence (pioche et casque impériaux, couronne, rouage de l'Empire) :", font=FP, fill=(200, 200, 200))
ref = [Image.open(T + n + '.png').convert('RGBA') for n in ('imperial_pickaxe', 'imperial_helmet', 'airain_crown', 'airain_gear')]
row = ref[:2] + [fn() for (_, _, fn, _) in L[:5]] + ref[2:]
for k, tex in enumerate(row):
    t = tex.crop((0, 0, tex.size[0], tex.size[0])).resize((16, 16), Image.NEAREST) if tex.size[0] != 16 else tex
    case(20 + k * 58, y - 2, t if tex.size[0] == 16 else tex.resize((16, 16), Image.LANCZOS))
im.convert('RGB').save('/mnt/user-data/outputs/item_textures_mockup.png')
