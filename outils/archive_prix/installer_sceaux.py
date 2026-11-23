# Archive résonante : prix en sceau cistercien. Écrit dans resonant_archive.png (3x, repère 512 x 256) :
#  - boutons de lot (330, 20/50/80, 52 x 30) sans la fenêtre sombre du prix ;
#  - planche de sceaux : cellule 8 x 11 ; chiffre c (1..9) du rang q (0 unités, 1 dizaines, 2 centaines, 3 milliers)
#    en (392 + 8 (c-1), 44 + 11 q) ; la hampe en (464, 44).
from PIL import Image, ImageDraw, ImageFilter
P = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/airain/textures/gui/resonant_archive.png'
S = 3
im = Image.open(P).convert('RGBA'); p = im.load()
for v in (20, 50, 80):
    fond = p[(330 + 26) * S, v * S + 30]
    for y in range(v * S + 44, v * S + 81):
        for x in range(330 * S + 9, 330 * S + 147): p[x, y] = fond
CW, CH, H, WQ, EP = 24, 33, 27, 8, 2
CX, Y0 = CW // 2, 3; Y1 = Y0 + H; Q = H // 3
def hx(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
COEUR, HALO = hx('e6fbff'), hx('3fb8e0')
def sprite(dessin):
    m = Image.new('L', (CW, CH)); d = ImageDraw.Draw(m); dessin(d)
    out = Image.new('RGBA', (CW, CH))
    g = m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.8)).point(lambda v: int(min(255, v * .9)))
    out.alpha_composite(Image.composite(Image.new('RGBA', (CW, CH), HALO), Image.new('RGBA', (CW, CH)), g))
    out.alpha_composite(Image.composite(Image.new('RGBA', (CW, CH), COEUR), Image.new('RGBA', (CW, CH)), m))
    return out
def hampe(d): d.rectangle([CX - EP // 2, Y0, CX - EP // 2 + EP - 1, Y1], fill=255)
def chiffre(n, q):
    sx = 1 if q in (0, 2) else -1; haut = q in (0, 1)
    X = lambda u: CX + sx * u; Y = lambda v: (Y0 + v) if haut else (Y1 - v)
    segs = []
    if n in (1, 5, 7, 9): segs.append(((0, 0), (WQ, 0)))
    if n in (2, 8, 9): segs.append(((0, Q), (WQ, Q)))
    if n == 3: segs.append(((0, 0), (WQ, Q)))
    if n in (4, 5): segs.append(((0, Q), (WQ, 0)))
    if n in (6, 7, 8, 9): segs.append(((WQ, 0), (WQ, Q)))
    def dessin(d):
        for a, b in segs: d.line([(X(a[0]), Y(a[1])), (X(b[0]), Y(b[1]))], fill=255, width=EP)
    return dessin
im.paste((0, 0, 0, 0), (392 * S, 44 * S, 472 * S, 88 * S))
for q in range(4):
    for c in range(1, 10): im.paste(sprite(chiffre(c, q)), ((392 + 8 * (c - 1)) * S, (44 + 11 * q) * S))
im.paste(sprite(hampe), (464 * S, 44 * S))
im.save(P)
print('sceaux installés')
