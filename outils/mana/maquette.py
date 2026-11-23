# Maquettes de la barre de mana d'Ars Nouveau (style réfractaire : argent et améthyste), même taille que l'actuelle.
# Géométrie d'Ars (GuiManaHUD) en pixels d'interface, bas de l'écran = y :
#   fond  : texture lignes 0..18  dessinée à y-18 ;  liquide : x 9..105, lignes y-8..y-3 (5 px) ;  devant : lignes 18..38 à y-17.
# On dessine sur une toile de 108 x 21 (ligne r = écran y-18+r) en 3x, puis on découpe en « fond » et « devant ».
from PIL import Image, ImageDraw
S = 3
H = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/ars_nouveau/textures/gui/'
LIQ = Image.open(H + 'manabar_gui_mana.png').convert('RGBA')
def hx(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
C = {k: hx(v) for k, v in dict(ar0='fbfaff', ar1='e4e0ee', ar2='c8c4d8', ar3='a9a3bd', ar4='7a7490', ar5='4a4460', ar6='2a2438',
                                 am0='efe6ff', am1='c9a8ff', am2='9b6ae0', am3='6a3fb0', am4='3b2458', verre='130c20', verre2='1d1430').items()}
class Toile:
    def __init__(s): s.f = Image.new('RGBA', (108 * S, 21 * S)); s.d = Image.new('RGBA', (108 * S, 21 * S))
    def r(s, couche, x, y, w, h, c):      # rectangle en pixels de texture (3x)
        ImageDraw.Draw(couche).rectangle([x, y, x + w - 1, y + h - 1], fill=c)
    def R(s, couche, x, y, w, h, c): s.r(couche, x * S, y * S, w * S, h * S, c)   # en pixels d'interface
    def poly(s, couche, pts, c): ImageDraw.Draw(couche).polygon([(x * S, y * S) for x, y in pts], fill=c)
def cristal(t, couche, cx, cy, rx, ry, vers=None):
    """Losange d'améthyste à facettes, centré (cx, cy) en px d'interface (demi-pixels permis)."""
    t.poly(couche, [(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)], C['am3'])
    t.poly(couche, [(cx, cy - ry), (cx + rx, cy), (cx, cy)], C['am2'])
    t.poly(couche, [(cx, cy - ry), (cx - rx, cy), (cx, cy)], C['am1'])
    ImageDraw.Draw(couche).line([(cx * S, (cy - ry) * S + 2), (cx * S, cy * S)], fill=C['am0'])
# ------------------------------------------------------------------ A : fiole d'argent
def A():
    t = Toile()
    t.R(t.f, 7, 10, 100, 5, C['verre'])                    # verre vide (fond)
    t.R(t.f, 7, 10, 100, 1, C['verre2'])
    # rebords du tube (devant) : ligne 8 au-dessus du liquide, ligne 15 dessous
    t.R(t.d, 6, 9, 102, 1, C['ar2']); t.r(t.d, 6 * S, 9 * S, 102 * S, 1, C['ar0'])
    t.R(t.d, 6, 15, 102, 1, C['ar4']); t.r(t.d, 6 * S, 16 * S - 1, 102 * S, 1, C['ar5'])
    for x in range(21, 100, 12): t.R(t.d, x, 8, 1, 1, C['ar3'])          # graduations
    t.r(t.d, 9 * S, 10 * S, 96 * S, 1, (255, 255, 255, 70))               # reflet du verre sur le liquide
    for gauche in (True, False):
        x0 = 1 if gauche else 97
        t.R(t.d, x0, 5, 10, 14, C['ar5']); t.R(t.d, x0 + 1, 6, 8, 12, C['ar2'])
        t.R(t.d, x0 + 1, 6, 8, 1, C['ar0']); t.R(t.d, x0 + 1, 17, 8, 1, C['ar4'])
        for k in (3, 6): t.R(t.d, x0 + k, 7, 1, 10, C['ar3'])              # bagues
        cristal(t, t.d, 0.5 + (0 if gauche else 107) , 12, 2.5, 4.5)
    t.R(t.d, 50, 5, 8, 4, C['ar5']); t.R(t.d, 51, 6, 6, 3, C['ar2']); cristal(t, t.d, 54, 5.5, 2.5, 3.5)
    return t
# ------------------------------------------------------------------ B : reliquaire (cadre en ogive, rivets)
def B():
    t = Toile()
    t.R(t.f, 4, 8, 100, 9, C['ar6']); t.R(t.f, 7, 10, 98, 5, C['verre'])
    t.R(t.d, 4, 9, 101, 1, C['ar3']); t.r(t.d, 4 * S, 9 * S, 101 * S, 1, C['ar1'])
    t.R(t.d, 4, 15, 101, 1, C['ar4'])
    for x in range(16, 100, 16): t.R(t.d, x, 9, 1, 1, C['am2'])            # petites gemmes serties dans le rebord
    t.r(t.d, 9 * S, 10 * S, 96 * S, 1, (255, 255, 255, 55))
    for gauche in (True, False):
        def X(v): return v if gauche else 108 - v
        # ogive : pointe vers l'extérieur
        t.poly(t.d, [(X(0), 12), (X(5), 4), (X(11), 4), (X(11), 20), (X(5), 20)], C['ar5'])
        t.poly(t.d, [(X(1.5), 12), (X(5.5), 5.5), (X(10), 5.5), (X(10), 18.5), (X(5.5), 18.5)], C['ar2'])
        t.poly(t.d, [(X(1.5), 12), (X(5.5), 5.5), (X(10), 5.5), (X(10), 6.5), (X(5.8), 6.5)], C['ar0'])
        cristal(t, t.d, X(6), 12, 2.5, 4)
    return t
# ------------------------------------------------------------------ C : géode (grappes d'améthyste aux deux bouts)
def Cg():
    t = Toile()
    t.R(t.f, 7, 10, 100, 5, C['verre'])
    t.R(t.d, 7, 9, 100, 1, C['ar4']); t.r(t.d, 7 * S, 9 * S, 100 * S, 1, C['ar2'])
    t.R(t.d, 7, 15, 100, 1, C['ar5'])
    t.r(t.d, 9 * S, 10 * S, 96 * S, 1, (255, 255, 255, 60))
    for gauche in (True, False):
        def X(v): return v if gauche else 108 - v
        t.poly(t.d, [(X(0), 19), (X(2), 8), (X(10), 8), (X(12), 19)], C['ar6'])      # socle de roche
        t.poly(t.d, [(X(1), 18), (X(2.5), 9.5), (X(9.5), 9.5), (X(11), 18)], C['ar5'])
        for (cx, cy, rx, ry) in ((4, 9, 2, 6), (8.5, 10, 1.6, 5), (2, 14, 1.5, 3.5), (10.5, 15, 1.5, 3)):
            cristal(t, t.d, X(cx), cy, rx, ry)
    return t
def apercu(t, remplissage, fond):
    """Assemble comme le jeu : fond, liquide (largeur selon le mana), devant."""
    W, Ht = 120 * S, 26 * S
    im = Image.new('RGBA', (W, Ht), fond); L, y = 6 * S, 23 * S
    im.alpha_composite(t.f.crop((0, 0, 108 * S, 18 * S)), (L, y - 18 * S))
    n = int(96 * remplissage) * S
    if n: im.alpha_composite(LIQ.crop((0, 0, n, 6 * S)), (L + 9 * S, y - 9 * S))
    im.alpha_composite(t.d.crop((0, S, 108 * S, 21 * S)), (L, y - 17 * S))
    return im
if __name__ == '__main__':
    from PIL import ImageFont
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    # barre actuelle, pour comparer
    act_b = Image.open(H + 'manabar_gui_border.png').convert('RGBA')
    class Act: pass
    act = Act(); act.f = act_b.crop((0, 0, 108 * S, 21 * S)); act.d = Image.new('RGBA', (108 * S, 21 * S)); act.d.alpha_composite(act_b.crop((0, 18 * S, 108 * S, 38 * S)), (0, S))
    rangs = (("Aujourd'hui", act), ("A : fiole d'argent", A()), ("B : reliquaire", B()), ("C : géode", Cg()))
    z = 2; out = Image.new('RGB', (3 * 120 * S * z + 80, len(rangs) * (26 * S * z + 70) + 20), (24, 22, 30)); d = ImageDraw.Draw(out)
    for i, (titre, t) in enumerate(rangs):
        y0 = 20 + i * (26 * S * z + 70); d.text((20, y0), titre, font=F, fill=(235, 235, 235))
        for j, (rem, fond) in enumerate(((1, (58, 92, 44, 255)), (.55, (40, 40, 48, 255)), (.12, (120, 150, 190, 255)))):
            im = apercu(t, rem, fond).resize((120 * S * z, 26 * S * z), Image.NEAREST)
            out.paste(im, (20 + j * (120 * S * z + 20), y0 + 45))
    out.save('/mnt/user-data/outputs/mana_bar_mockup.png')
