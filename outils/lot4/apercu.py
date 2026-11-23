# Maquette avant/après du lot 4 : textures agrandies + mises en situation (sol, tableau d'émail, verrière)
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/claude/travail/lot4'); import textures as tx

T = tx.T; A = '/tmp/l4/apres'
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
def av(k): return Image.open(f'{T}/{k}.png').convert('RGBA')
def ap(k): return Image.open(f'{A}/{k}.png').convert('RGBA')
def gros(im, s): return im.resize((im.width * s, im.height * s), Image.NEAREST)

def sol(src, sch, fond='block/small_slate_tiles'):
    """Scène 5x3 blocs vue de dessus : une ligne en T, une flèche, un passage piéton, des hachures."""
    try: base = av(fond)
    except Exception: base = av('block/cut_airain')
    W, H = 6, 3; im = Image.new('RGBA', (16 * W, 16 * H))
    for j in range(H):
        for i in range(W): im.alpha_composite(base, (16 * i, 16 * j))
    L = src('block/yellow_floor_line')
    def bras(bx, by, n, s, e, o):
        t = Image.new('RGBA', (16, 16)); t.alpha_composite(L.crop((7, 7, 9, 9)), (7, 7))
        if n: t.alpha_composite(L.crop((7, 0, 9, 7)), (7, 0))
        if s: t.alpha_composite(L.crop((7, 9, 9, 16)), (7, 9))
        if e: t.alpha_composite(L.crop((9, 7, 16, 9)), (9, 7))
        if o: t.alpha_composite(L.crop((0, 7, 7, 9)), (0, 7))
        im.alpha_composite(t, (16 * bx, 16 * by))
    bras(0, 1, 0, 0, 1, 0); bras(1, 1, 0, 0, 1, 1); bras(2, 1, 1, 1, 0, 1); bras(2, 0, 0, 1, 0, 0); bras(2, 2, 1, 0, 0, 0)
    im.alpha_composite(src('block/white_floor_arrow'), (16 * 1, 0))
    im.alpha_composite(src('block/white_floor_crossing'), (16 * 3, 1 * 16))
    for j in range(3): im.alpha_composite(src('block/red_hazard_stripes'), (16 * 5, 16 * j))
    for j in range(3): im.alpha_composite(src('block/yellow_hazard_stripes'), (16 * 4, 16 * j)) if j != 1 else None
    im.alpha_composite(src('block/red_floor_line'), (0, 0)) if False else None
    return gros(im, sch)

def tableau(src, sch):
    """Tableau d'émail 3x2 blocs, teinté bleu nuit comme en jeu, cadre d'airain."""
    e = src('block/enamel'); W, H = 3, 2
    im = Image.new('RGBA', (16 * W + 4, 16 * H + 4), (0, 0, 0, 0))
    cad = av('block/airain_beam_plate')
    for j in range(0, 16 * H + 4, 16):
        for i in range(0, 16 * W + 4, 16): im.alpha_composite(cad, (i, j))
    im = im.crop((0, 0, 16 * W + 4, 16 * H + 4))
    em = Image.new('RGBA', (16 * W, 16 * H))
    for j in range(H):
        for i in range(W): em.alpha_composite(e, (16 * i, 16 * j))
    teinte = (46, 74, 128)
    px = em.load()
    for y in range(em.height):
        for x in range(em.width):
            r, g, b, a = px[x, y]; px[x, y] = (r * teinte[0] // 255, g * teinte[1] // 255, b * teinte[2] // 255, 255)
    im.alpha_composite(em, (2, 2))
    out = gros(im, sch); d = ImageDraw.Draw(out)
    d.text((2 * sch + 10, 2 * sch + 8), 'NORTH STATION', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 3 * sch), fill=(236, 228, 206))
    return out

def verriere(src, sch):
    """Verre d'airain 3x2 posé devant un ciel et une poutre, pour juger la transparence et le raccord."""
    W, H = 3, 2; im = Image.new('RGBA', (16 * W, 16 * H))
    d = ImageDraw.Draw(im)
    for y in range(16 * H): d.line([(0, y), (16 * W, y)], fill=(120 + y, 165 + y, 215, 255))
    d.rectangle([0, 22, 48, 26], fill=(110, 80, 50, 255))
    g = src('block/airain_glass')
    for j in range(H):
        for i in range(W): im.alpha_composite(g, (16 * i, 16 * j))
    return gros(im, sch)

def echo(src, sch):
    """Vitre d'écho (centre) dans son pourtour, devant une source de mana."""
    im = Image.new('RGBA', (48, 32), (40, 34, 58, 255)); d = ImageDraw.Draw(im)
    d.ellipse([18, 8, 30, 24], fill=(120, 200, 255, 255))
    for i in range(3):
        b = src('block/echo_glass_edge'); im.alpha_composite(b, (16 * i, 0)) if i != 1 else None
        im.alpha_composite(b, (16 * i, 16)) if i != 1 else None
    im.alpha_composite(src('block/echo_glass'), (16, 0)); im.alpha_composite(src('block/echo_glass'), (16, 16))
    return gros(im, sch)

LISTE = ['block/white_floor_line', 'block/yellow_floor_line', 'block/red_floor_line', 'block/white_floor_arrow', 'block/yellow_floor_arrow',
         'block/white_floor_crossing', 'block/red_hazard_stripes', 'block/yellow_hazard_stripes', 'block/enamel', 'block/enamel_matte',
         'block/airain_glass', 'block/echo_glass', 'block/echo_glass_edge']
OBJETS = ['item/white_floor_line', 'item/yellow_floor_line', 'item/red_floor_line',
          'item/rack_reinforcement_1', 'item/rack_reinforcement_2', 'item/rack_reinforcement_3', 'item/rack_reinforcement_4']

def damier(w, h, c1=(64, 64, 64), c2=(78, 78, 78), p=12):
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    for y in range(0, h, p):
        for x in range(0, w, p): d.rectangle([x, y, x + p - 1, y + p - 1], fill=(c1 if (x // p + y // p) % 2 else c2) + (255,))
    return im

def planche(liste, sch, titre, case=None):
    n = len(liste); cw = 16 * sch + 16
    out = Image.new('RGBA', (110 + n * cw, 2 * (16 * sch + 30) + 30), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
    d.text((10, 6), titre, font=F, fill=(240, 220, 160))
    for r, (lab, src) in enumerate((('AVANT', av), ('APRÈS', ap))):
        y = 30 + r * (16 * sch + 30)
        d.text((10, y + 16 * sch // 2), lab, font=F, fill=(220, 220, 220))
        for i, k in enumerate(liste):
            x = 110 + i * cw
            bg = case.copy() if case else damier(16 * sch, 16 * sch)
            bg.alpha_composite(gros(src(k), sch)); out.alpha_composite(bg, (x, y + 16))
            if r == 0: d.text((x, y), k.split('/')[1].replace('_floor', '')[:20], font=f, fill=(170, 170, 180))
    return out

if __name__ == '__main__':
    tx_dest = A
    import os; os.makedirs(A, exist_ok=True)
    for k, fn in tx.SORTIES.items():
        os.makedirs(os.path.dirname(f'{A}/{k}'), exist_ok=True); fn().save(f'{A}/{k}.png')
    p1 = planche(LISTE, 8, 'Lot 4 — textures de blocs (x8, sur damier pour voir la transparence)')
    slot = Image.new('RGBA', (16 * 8, 16 * 8), (139, 139, 139, 255))
    p2 = planche(OBJETS, 8, 'Lot 4 — objets (x8, sur le gris des cases)', slot)
    scenes = []
    for lab, src in (('AVANT', av), ('APRÈS', ap)):
        rang = [sol(src, 5), tableau(src, 4), verriere(src, 4), echo(src, 4)]
        scenes.append((lab, rang))
    hW = sum(i.width + 20 for i in scenes[0][1]) + 110; hH = max(i.height for i in scenes[0][1])
    p3 = Image.new('RGBA', (hW, 40 + 2 * (hH + 30)), (30, 32, 38, 255)); d = ImageDraw.Draw(p3)
    d.text((10, 6), 'En situation : sol d\'atelier, tableau d\'émail bleu, verrière d\'airain, vitre d\'écho', font=F, fill=(240, 220, 160))
    for r, (lab, rang) in enumerate(scenes):
        y = 40 + r * (hH + 30); x = 110; d.text((10, y + hH // 2), lab, font=F, fill=(220, 220, 220))
        for im in rang: p3.alpha_composite(im, (x, y)); x += im.width + 20
    W = max(p.width for p in (p1, p2, p3))
    out = Image.new('RGBA', (W, p1.height + p2.height + p3.height), (30, 32, 38, 255))
    out.alpha_composite(p1, (0, 0)); out.alpha_composite(p2, (0, p1.height)); out.alpha_composite(p3, (0, p1.height + p2.height))
    out.convert('RGB').save('/mnt/user-data/outputs/lot4_mockup.png'); print(out.size)
