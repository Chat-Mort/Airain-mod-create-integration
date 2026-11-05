"""Icônes de la lignée de l'Écho (palier runique) : diadème, matériaux, armure, armes."""
import sys, random
sys.path.insert(0, '../armure2'); sys.path.insert(0, '../armes2')
from PIL import Image, ImageDraw, ImageFont
import icones_armure as IA
import icones as IW
K = (14, 10, 20)
NE1, NE2, NE3, NE4 = (38,32,42), (58,50,64), (84,74,92), (112,100,122)
V1, V2, V3 = (58,30,96), (86,48,140), (122,84,190)
LV, LV2 = (186,156,255), (228,214,255)
AR1, AR2, AR3 = (120,122,142), (168,170,190), (220,222,236)
F1 = (24,14,34)

def contour(im):
    a = im.copy(); n = im.width
    for x in range(n):
        for y in range(n):
            if a.getpixel((x, y))[3] == 0 and any(0 <= x+dx < n and 0 <= y+dy < n and a.getpixel((x+dx, y+dy))[3] > 0 for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                im.putpixel((x, y), K + (255,))
    return im

def grille(g, pal):
    im = Image.new('RGBA', (16, 16), (0,0,0,0))
    for y, r in enumerate(g):
        for x, ch in enumerate(r):
            if ch != '.': im.putpixel((x, y), pal[ch] + (255,))
    return im
PAL = dict(a=AR1, b=AR2, c=AR3, l=LV, L=LV2, v=V1, w=V2, W=V3, n=NE2, N=NE3, f=F1, k=K)

def diademe():
    return grille(["................", "................", "................", "................",
                   ".......L........", "...w...l...w....", "...W..lLl..W....", "..kbbbklkbbbk...",
                   ".kbaaccbccaab.k.".replace('.k', 'k.'), ".kbf........fbk.", "..kbb......bbk..", "...kbbbbbbbbk...",
                   "................", "................", "................", "................"], PAL)

def katana_liam(_P=None):
    """Le katana dessiné par Liam (version sacrée), recoloré : or -> lavande sur la lame, argent ailleurs ; poignée violette."""
    src = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/katana_sacre.png').convert('RGBA')
    im = src.copy(); px = im.load()
    for x in range(32):
        for y in range(32):
            r, g, b, a = px[x, y]
            if a == 0: continue
            c = (r, g, b)
            if c == (214, 170, 70): c = LV if x - y > -6 else AR2
            elif c == (150, 112, 40): c = AR1
            elif c == (28, 22, 32): c = V1
            elif c == (0, 0, 0): c = F1
            elif c == (120, 110, 134): c = (112, 100, 124)
            px[x, y] = c + (a,)
    return im

def lingot():
    """Forme du lingot de fer vanilla : face du dessus claire, flanc avant, bout ombré."""
    g = ["................",
         "................",
         "................",
         "................",
         ".......kkkkkkk..",
         "......kLLLLLLLk.",
         ".....kLWWWWWWLvk",
         "....kLWWWWWWLvvk",
         "...kLWWWWWWLvvk.",
         "..kwwwwwwwwvvk..",
         "..kwwwwwwwwvk...",
         "..kvvvvvvvvk....",
         "...kkkkkkkk.....",
         "................",
         "................",
         "................"]
    return grille(g, PAL)

def lingot_ancien():
    return grille(["................", "................", "................", "................",
                   "................", ".....kkkkkk.....", "....kLWWWWwk....", "...kLWwwwwvvk...",
                   "..kLWwwlwwvvvk..", "..kkwwwwwvvvkk..", "...kkvvvvvvkk...", ".....kkkkkk.....",
                   "................", "................", "................", "................"], PAL)

def bloc():
    im = Image.new('RGBA', (16, 16)); r = random.Random(3)
    for x in range(16):
        for y in range(16):
            c = F1 if (x + y + r.randint(0, 2)) % 4 else (34, 22, 48)
            if x in (0, 15) or y in (0, 15): c = AR2 if (x + y) % 3 else AR1
            im.putpixel((x, y), c + (255,))
    for (cx, cy) in ((4, 4), (11, 5), (5, 11), (11, 11), (8, 8)):
        for (dx, dy, c) in ((0,0,LV2),(1,0,LV),(-1,0,LV),(0,1,LV),(0,-1,LV),(1,1,V3),(-1,-1,V3),(1,-1,V3),(-1,1,V3)):
            im.putpixel((cx+dx, cy+dy), c + (255,))
    return im

# ---- armure runique (silhouettes de l'armure impériale/sacrée)
def casque_runique():
    def f(x, y, d):
        if y == 6: return AR2 if x % 2 else AR3                     # diadème
        if y == 4 and x in (4, 8, 11): return LV
        return IA.ombrer(d, x, y, NE4, NE2, NE1)
    im = IA.piece('casque', f)
    IA.ajouter(im, [(7, 6), (8, 6)], LV2); IA.ajouter(im, [(7, 5), (8, 5)], LV)
    return im
def plastron_runique():
    def f(x, y, d):
        if y <= 3 and (x <= 5 or x >= 10): return AR3 if y == 1 else (AR2 if y == 2 else NE1)
        if y in (12,): return AR2
        if y in (10, 11) and 3 <= x <= 12: return V2 if (x + y) % 3 else V3     # ceinture de tissu
        if x - (12 - y) in (0, 1) and 4 <= y <= 9: return V3 if x % 2 else V2   # écharpe
        if (x, y) in ((6, 5), (9, 6), (5, 8), (10, 8), (7, 7), (8, 4)): return LV
        return IA.ombrer(d, x, y, NE4, NE2, NE1)
    return IA.piece('plastron', f)
def jambieres_runiques():
    def f(x, y, d):
        if y == 1: return AR3 if x < 8 else AR2
        if 2 <= y <= 5 and 5 <= x <= 10: return V2 if (x + y) % 3 else V1      # pan de tissu
        if y == 8 and x in (5, 10): return LV
        return IA.ombrer(d, x, y, NE4, NE2, NE1)
    return IA.piece('jambieres', f)
def bottes_runiques():
    def f(x, y, d):
        if y == 4: return AR3 if x in (2, 3, 10, 11) else AR2
        if y == 11: return NE1
        if y == 7 and x in (4, 12): return LV
        return IA.ombrer(d, x, y, NE4, NE2, NE1)
    return IA.piece('bottes', f)

# ---- armes runiques (même dessin que les impériales, palette de l'Écho)
R = dict(l0=(30,24,36), l1=(50,42,58), l2=(72,62,82), l3=(112,100,124), f1=AR1, f2=AR2, f3=AR3,
         g0=F1, g1=V1, g2=V3, j1=LV, j2=LV2)

def runes(im):
    """Fait luire la lame : runes lavande au cœur, tranchant éclairci."""
    px = im.load()
    for x in range(im.width):
        for y in range(im.height):
            c = px[x, y][:3]
            if px[x, y][3] == 0: continue
            if c == R['l2'] and (x - y) % 3 == 0: px[x, y] = LV + (255,)
            elif c == R['l3']: px[x, y] = (150, 138, 172, 255)
    return im

ARMURE = [("casque_runique", casque_runique), ("plastron_runique", plastron_runique), ("jambieres_runiques", jambieres_runiques), ("bottes_runiques", bottes_runiques)]
AUTRES = [("diademe_echo", diademe), ("lingot_arcanium", lingot), ("bloc_echo_primordial", bloc)]
ARMES = [("epee_runique", lambda P: runes(IW.epee(P))), ("katana_runique", katana_liam), ("espadon_runique", lambda P: runes(IW.espadon(P))),
         ("twinblade_runique", lambda P: runes(IW.twinblade(P))), ("pioche_runique", lambda P: runes(IW.pioche(P)))]

if __name__ == '__main__':
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; f = ImageFont.truetype(FB, 14)
    C = 128
    lignes = [[(n, fn()) for n, fn in AUTRES], [(n, fn()) for n, fn in ARMURE], [(n, fn(R)) for n, fn in ARMES]]
    out = Image.new('RGB', (5 * (C + 50) + 20, 3 * (C + 45) + 10), (31, 32, 36)); d = ImageDraw.Draw(out)
    for j, l in enumerate(lignes):
        for i, (n, im) in enumerate(l):
            g = im.resize((C, C), Image.NEAREST); X = 25 + i * (C + 50); Y = 8 + j * (C + 45)
            out.paste(g, (X, Y), g); t = n.replace('_', ' ')
            d.text((X + C // 2 - d.textlength(t, font=f) / 2, Y + C + 6), t, fill=(200, 180, 255), font=f)
    out.save('apercu_icones_echo.png'); print(out.size)
