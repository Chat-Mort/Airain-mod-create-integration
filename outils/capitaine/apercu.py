import colorsys
src = open('../modules/apercu.py').read()
src = src[:src.index("out = Image.new")]
g = {}; exec(src, g)
Image, ImageDraw, ImageFont, FB = g['Image'], g['ImageDraw'], g['ImageFont'], g['FB']
TEX0 = g['TEX']

def recolor(f):
    t = TEX0.copy(); px = t.load()
    for y in range(t.height):
        for x in range(t.width):
            r, gg, b, a = px[x, y]
            if a: px[x, y] = f(r, gg, b) + (a,)
    return t
def lerp(cs, v):
    v = max(0, min(.999, v)) * (len(cs) - 1); i = int(v); k = v - i
    return tuple(int(cs[i][j] * (1 - k) + cs[i + 1][j] * k) for j in range(3))
def lum(r, g_, b): return (0.3 * r + 0.59 * g_ + 0.11 * b) / 255
OR_ = [(70, 45, 10), (160, 115, 30), (225, 185, 70), (255, 235, 150)]
BLANC = [(95, 90, 85), (175, 170, 160), (225, 222, 212), (250, 248, 240)]
NOIR = [(14, 12, 20), (34, 28, 48), (58, 48, 80), (85, 72, 110)]
VIOLET = [(40, 20, 70), (95, 55, 150), (160, 125, 215), (215, 200, 250)]
def chaud(r, g_, b): return r > b + 25
def detail(r, g_, b): return g_ > r or lum(r, g_, b) < 0.28
def f_cap(r, g_, b): return lerp(OR_, 0.45 + lum(r, g_, b)) if detail(r, g_, b) else lerp(BLANC, lum(r, g_, b) * 1.4)
def f_echo(r, g_, b): return lerp(VIOLET, 0.35 + lum(r, g_, b) * 1.2) if detail(r, g_, b) else lerp(NOIR, lum(r, g_, b) * 1.5)

bloc, put, cyl = g['bloc'], g['put'], g['cyl']
GOLD, GOLD2, WH, RED, RED2 = (235, 195, 75), (185, 140, 40), (248, 246, 236), (150, 25, 32), (110, 15, 22)
LAV, LAVG, CYAN = (190, 165, 240), (205, 185, 255, 1), (120, 235, 230, 1)

def capitaine(V):
    # couronne
    bloc(V, -4.5, -20, -8, 9, 1, 9, None, lambda x, y, z: GOLD if (x < -4 or x >= 4 or z < -7.5 or z >= 0.5) else None)
    for V_ in list(V):
        if V[V_] is None: del V[V_]
    for (x, z) in [(-4.5, -8), (-0.5, -8), (3.5, -8), (-4.5, -3.5), (3.5, -3.5), (-4.5, 0), (-0.5, 0), (3.5, 0)]:
        bloc(V, x, -22, z, 1, 2, 1, GOLD)
    bloc(V, -1, -21.5, -8.5, 2, 1.5, 0.5, (255, 255, 255, 1))      # gemme blanche
    # épaulettes
    for x0 in (-14.5, 8.5):
        bloc(V, x0, -11, -4, 6, 1.5, 8, GOLD)
        for i in range(0, 12):
            bloc(V, x0 + i * 0.5, -9.5, -4.5, 0.5, 1.5 + (i % 2), 0.5, WH)
    # écharpe impériale (diagonale) et cape
    bloc(V, -8, -9, 5, 16, 1, 1.5, GOLD2)
    bloc(V, -8.5, -8, 5.5, 17, 24, 0.5, None, lambda x, y, z: RED if (int(x * 2) + int(y)) % 7 else RED2)
    # plumet
    for i in range(8): bloc(V, -0.5 + (i * 0.25), -23 - i * 0.6, -3 + i * 0.6, 1, 1, 1, WH)

def gardien_echo(V):
    # cœur de résonance sur la poitrine
    bloc(V, -3.5, -7, -6.5, 7, 7, 0.5, None, lambda x, y, z: CYAN if (abs(x) < 1.6 and abs(y + 3.5) < 1.6) else (LAVG if (abs(x) < 2.6 and abs(y + 3.5) < 2.6) else (20, 16, 30)))
    # cristaux d'écho sur les épaules et le dos
    for (x, z, h) in [(-12.5, -2, 5), (-11, 1, 3.5), (-13, 1.5, 2.5), (10.5, -2, 5), (12, 1, 3.5), (9.5, 1.5, 2.5)]:
        bloc(V, x, -9.5 - h, z, 1.5, h, 1.5, None, lambda X, Y, Z, h=h: LAVG if Y < -9.5 - h + 1 else LAV)
    for (x, h) in [(-5, 6), (-2, 8), (1, 7), (4, 5)]:
        bloc(V, x, -9 - h, 4, 1.5, h, 1.5, None, lambda X, Y, Z, h=h: LAVG if Y < -9 - h + 1.5 else (120, 90, 180))
    # anneau sonore autour de la tête

def rend(tex, extra, dos=False):
    g['TEX'] = tex
    V = g['golem']()
    extra(V)
    if dos: V = {(-x, y, -z): c for (x, y, z), c in V.items()}
    return g['rendu'](V, T=3)

ims = [(rend(TEX0, lambda V: None), "Gardien"), (rend(recolor(f_cap), capitaine), "Capitaine impérial"), (rend(recolor(f_cap), capitaine, True), "(dos)"),
       (rend(recolor(f_echo), gardien_echo), "Gardien d'Écho"), (rend(recolor(f_echo), gardien_echo, True), "(dos)")]
W = sum(i.width for i, _ in ims) + 40; H = max(i.height for i, _ in ims) + 50
out = Image.new('RGB', (W, H), (32, 33, 38)); d = ImageDraw.Draw(out); fnt = ImageFont.truetype(FB, 18)
x = 10
for i, t in ims:
    out.paste(i, (x, H - i.height - 10 if t == "Gardien" else 40)); d.text((x + 10, 8), t, fill=(230, 220, 200), font=fnt); x += i.width + 10
out.save('apercu_capitaine.png'); print(out.size)
