import sys, math
sys.path.insert(0, '../armes2'); sys.path.insert(0, '../echo')
from PIL import Image, ImageDraw, ImageFont
import icones as IW
K = IW.K
# palette arcanique : lame noir-violet à tranchant lavande, garnitures noires, gemmes lavande, poignées violettes
A = dict(l0=(22,14,30), l1=(44,28,62), l2=(70,44,104), l3=(190,160,255), f1=(40,26,58), f2=(74,50,108), f3=(120,90,170),
         g0=(14,10,20), g1=(58,30,96), g2=(122,84,190), j1=(186,156,255), j2=(232,218,255))
LV, LV2 = (186,156,255), (232,218,255)

def lueur(im):
    """Runes lavande au cœur de la lame ; la netherite de la pioche passe au violet."""
    px = im.load()
    viol = {IW.N['n0']: (44,28,62), IW.N['n1']: (70,44,104), IW.N['n2']: (110,74,160)}
    for x in range(32):
        for y in range(32):
            if px[x, y][3] and px[x, y][:3] in viol: px[x, y] = viol[px[x, y][:3]] + (255,)
            if px[x, y][3] and px[x, y][:3] == A['l2'] and (x - y) % 4 == 0: px[x, y] = LV + (255,)
    return im

def katana_arcanique(_=None):
    """Crépuscule : le katana impérial de Liam (Aube), recoloré."""
    src = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/katana_imperial.png').convert('RGBA')
    px = src.load()
    table = {(232,235,244): (112,76,166), (200,204,220): (74,48,110), (255,255,255): LV, (228,188,96): (74,50,108), (170,130,50): (40,26,58),
             (130,26,32): (58,30,96), (176,0,27): (122,84,190)}
    for x in range(32):
        for y in range(32):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in table: px[x, y] = table[(r, g, b)] + (a,)
    return src

# ------------------------------------------------------------------------- sceptres
def sceptre(imperial):
    ic = IW.Icone()
    O1, O2, O3 = (170,130,50), (228,188,96), (255,228,150)
    B2, B3, N1 = (232,235,244), (255,255,255), (30,24,34)
    def f(u, v):
        d = v - 31
        if -26 <= u <= 10 and abs(d) <= 0.5:                                   # hampe
            if imperial: return B2 if (u // 3) % 2 else O2
            return A['f2'] if u % 5 else LV
        if u in (-27, -28) and abs(d) <= 1: return O2 if imperial else A['f3']  # talon
        if u in (-14, -13) and abs(d) <= 1: return O1 if imperial else A['g1']  # bague de prise
        return None
    ic.uv(f)
    cx, cy = 23, 8                                                            # tête du sceptre
    for x in range(32):
        for y in range(32):
            r = math.hypot(x + .5 - cx - .5, y + .5 - cy - .5)
            a = math.degrees(math.atan2(y - cy, x - cx)) % 360
            if imperial:
                if 3.2 < r <= 4.6 and int(a / 30) % 2 == 0: ic.p(x, y, O2)      # couronne de dents (rouage)
                elif 2.2 < r <= 3.2: ic.p(x, y, O1 if a > 180 else O3)
                elif r <= 2.2: ic.p(x, y, B3 if r < 1.2 else B2)
            else:
                if 2.6 < r <= 4.4 and not (200 < a < 250): ic.p(x, y, A['f2'] if a % 60 > 30 else A['f3'])   # croissant ouvert
                elif r <= 2.3: ic.p(x, y, LV2 if r < 1.2 else LV)                # l'Écho primordial
    if imperial:
        IW.etoile(ic, cx, cy, IW.I)
        for (x, y) in ((cx, cy - 6), (cx - 1, cy - 5), (cx + 1, cy - 5)): ic.p(x, y, O3)   # pointe de couronne
    else:
        for (x, y, c) in ((cx + 5, cy - 4, LV), (cx + 6, cy - 5, LV2), (cx - 5, cy + 4, A['g2']), (cx + 4, cy + 5, A['g2'])): ic.p(x, y, c)
    return ic.contour()

ARC = [("Lame de la Prêtresse", lambda: lueur(IW.epee(A))), ("Crépuscule", katana_arcanique), ("Glas", lambda: lueur(IW.espadon(A))),
       ("Jumelles d'Écho", lambda: lueur(IW.twinblade(A))), ("Sonde arcanique", lambda: lueur(IW.pioche(A)))]
SCE = [("Sceptre impérial", lambda: sceptre(True)), ("Sceptre arcanique", lambda: sceptre(False))]

if __name__ == '__main__':
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; f = ImageFont.truetype(FB, 15)
    C = 150
    out = Image.new('RGB', (5 * (C + 30) + 30, 2 * (C + 45) + 20), (31, 32, 36)); d = ImageDraw.Draw(out)
    for j, l in enumerate((ARC, SCE)):
        for i, (n, fn) in enumerate(l):
            g = fn().resize((C, C), Image.NEAREST); X = 25 + i * (C + 30); Y = 10 + j * (C + 45)
            out.paste(g, (X, Y), g)
            d.text((X + C // 2 - d.textlength(n, font=f) / 2, Y + C + 8), n, fill=(200, 180, 255) if j == 0 or i == 1 else (240, 205, 120), font=f)
    out.save('apercu_final.png'); print(out.size)
