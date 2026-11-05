import sys, math
sys.path.insert(0, '../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PEAU = (196,150,120); CHEV = (70,50,35); YEUX = (60,90,160); HABIT = (60,110,150); PANT = (50,50,90)
N1, N2, N3 = (34,28,38), (52,45,56), (76,66,80)            # netherite
O1, O2, O3 = (176,138,58), (226,186,96), (255,220,130)       # or
B1, B2, B3 = (200,204,218), (228,231,240), (250,251,255)     # blanc nacré
ET = (235,248,255,1); ET2 = (170,220,255,1); RUB = (200,40,40)
CAPE1, CAPE2 = (120,24,30), (90,16,22)

def boite(V, x0, y0, z0, x1, y1, z1, f, coque=True):
    for x in range(x0, x1):
        for y in range(y0, y1):
            for z in range(z0, z1):
                if coque and x0 < x < x1-1 and y0 < y < y1-1 and z0 < z < z1-1: continue
                c = f(x - x0, y - y0, z - z0, x1 - x0, y1 - y0, z1 - z0)
                if c: V[(x, y, z)] = c

def corps(V):
    unie = lambda c: (lambda *a: c)
    boite(V, -4, 24, -4, 4, 32, 4, lambda x,y,z,w,h,d: CHEV if y >= 6 or z == 0 else (YEUX if z == d-1 and y == 3 and x in (1,2,5,6) else PEAU))
    boite(V, -4, 12, -2, 4, 24, 2, unie(HABIT))
    boite(V, 4, 12, -2, 8, 24, 2, lambda x,y,z,w,h,d: PEAU if y < 4 else HABIT)
    boite(V, -8, 12, -2, -4, 24, 2, lambda x,y,z,w,h,d: PEAU if y < 4 else HABIT)
    boite(V, -4, 0, -2, 0, 12, 2, unie(PANT)); boite(V, 0, 0, -2, 4, 12, 2, unie(PANT))

# ---------------------------------------------------------------- SACRÉE : netherite noire, filets d'or
def sacree(V, cape=False):
    # casque couronné sacré
    def casque(x,y,z,w,h,d):
        if z == d-1 and 2 <= y <= 4 and 1 <= x <= w-2: return None if 3 <= y <= 3 and x in (2,3,6,7) else (N1 if y != 4 else N2)
        if y == h-1: return N3 if (x+z) % 3 else N2
        if y == 5: return O2 if (x+z) % 2 else O1
        return N2 if (x*3+y) % 5 else N3
    boite(V, -5, 23, -5, 5, 33, 5, casque)
    for x in range(-5, 5):
        for z in (-5, 4):
            V[(x, 33, z)] = O2
            if x in (-5, -1, 0, 4): V[(x, 34, z)] = O3 if x in (-1, 0) else O2
    for z in range(-5, 5):
        for x in (-5, 4):
            V[(x, 33, z)] = O2
            if z in (-5, 4): V[(x, 34, z)] = O2
    V[(0, 33, 5)] = ET; V[(-1, 33, 5)] = ET2; V[(0, 34, 4)] = O3
    # plastron
    def plastron(x,y,z,w,h,d):
        if z == d-1:
            if x in (0, w-1) or y in (0, h-1): return O2
            if x == w//2 or x == w//2-1: return O1 if y % 3 else O3
            if y == h-3: return O2
            return N2 if (x+y) % 4 else N3
        return N2 if (x+y+z) % 5 else N1
    boite(V, -5, 11, -3, 5, 25, 3, plastron)
    for s in (1, -1):
        x0 = 4 if s == 1 else -9
        boite(V, x0, 11, -3, x0+5, 25, 3, lambda x,y,z,w,h,d: O2 if y in (h-1, h-4, 1) else (N3 if (x+z) % 3 == 0 else N2))
        boite(V, x0 - (1 if s == -1 else 0), 23, -4, x0+5+(1 if s == 1 else 0), 26, 4, lambda x,y,z,w,h,d: O2 if y == h-1 or (x+z) % 4 == 0 else N1)
    # jambières
    for x0 in (-5, 0):
        boite(V, x0, 3, -3, x0+5, 13, 3, lambda x,y,z,w,h,d: O2 if (z == d-1 and y in (4,5) and 1 <= x <= w-2) else (O1 if y == h-1 else (N2 if (x+y) % 4 else N3)))
    # bottes
    for x0 in (-5, 0):
        boite(V, x0, -1, -3, x0+5, 4, 4, lambda x,y,z,w,h,d: O2 if y == h-1 or (z == d-1 and y == 0) else (N1 if y == 0 else N2))

# ---------------------------------------------------------------- IMPÉRIALE : blanc nacré, flancs de netherite, or
def nacre(x, y):
    return B3 if (x - y) % 9 in (0, 1) else ((236, 238, 246) if (x + y) % 11 == 0 else B2)
def imperiale(V):
    def casque(x,y,z,w,h,d):
        if z == d-1:
            if y in (3,) and 1 <= x <= w-2: return N1                      # visière
            if x == w//2 and 5 <= y <= 7: return O2
            if y == 5: return O2
        if x in (0, w-1) and 1 <= y <= 4: return N2                      # joues de netherite
        if y == 5: return O2 if (x+z) % 2 else O1
        if y == h-1: return B2 if (x+z) % 2 else B3
        return nacre(x+z, y)
    boite(V, -5, 23, -5, 5, 33, 5, casque)
    # couronne intégrée : fleurons blancs bordés d'or, étoile au front
    for x in range(-5, 5):
        for z in (-5, 4):
            V[(x, 33, z)] = O2
            if x in (-5, -2, 1, 4): V[(x, 34, z)] = B3; V[(x, 35, z)] = O3
    for z in range(-5, 5):
        for x in (-5, 4):
            V[(x, 33, z)] = O2
            if z in (-2, 1): V[(x, 34, z)] = B3; V[(x, 35, z)] = O3
    for (x, y) in ((-1, 29), (0, 29), (-1, 30), (0, 30)): V[(x, y, 5)] = ET
    for (x, y) in ((-2, 29), (1, 30), (-1, 31), (0, 28)): V[(x, y, 5)] = O2
    for (x, y) in ((-1, 34), (0, 34), (-1, 35), (0, 35), (-1, 36), (0, 36)): V[(x, y, 4)] = O3 if y < 36 else ET
    # loupe sur l'œil droit
    for (x, y) in ((-3, 26), (-4, 26), (-3, 27), (-4, 27)): V[(x, y, 5)] = (150, 205, 220)
    for (x, y) in ((-2, 26), (-5, 26), (-3, 25), (-4, 25), (-3, 28), (-4, 28)): V[(x, y, 5)] = O2
    # plastron : nacre, flancs noirs, étoile au cœur
    def plastron(x,y,z,w,h,d):
        if z == d-1:
            if x in (0, w-1): return N2
            if x in (1, w-2): return O2
            if y in (0, h-1): return O2
            if y == h-2: return O1
            return nacre(x, y)
        if z == 0: return nacre(x, y)
        return N2
    boite(V, -5, 11, -3, 5, 25, 3, plastron)
    for (x, y) in ((-1, 19), (0, 19), (-1, 20), (0, 20)): V[(x, y, 3)] = ET
    for (x, y) in ((-1, 18), (0, 18), (-1, 21), (0, 21), (-2, 19), (-2, 20), (1, 19), (1, 20)): V[(x, y, 3)] = O2
    V[(-1, 22, 3)] = ET2; V[(0, 17, 3)] = ET2
    # bras et grandes épaulières
    for s in (1, -1):
        x0 = 4 if s == 1 else -9
        boite(V, x0, 11, -3, x0+5, 25, 3, lambda x,y,z,w,h,d: O2 if y in (1, 5) else (N2 if y < 5 else nacre(x+z, y)))
        boite(V, x0 - (2 if s == -1 else 0), 22, -4, x0+5+(2 if s == 1 else 0), 27, 4,
              lambda x,y,z,w,h,d: O2 if y == 0 or y == h-1 else (O3 if (x+z) % 5 == 0 and y == h-2 else nacre(x+z, y)))
    # jambières
    for x0 in (-5, 0):
        boite(V, x0, 3, -3, x0+5, 13, 3, lambda x,y,z,w,h,d: N2 if x in (0, w-1) and z != d-1 else
              (O2 if y in (4, h-1) else (O3 if (z == d-1 and y == 5 and x == 2) else nacre(x, y))))
    # bottes
    for x0 in (-5, 0):
        boite(V, x0, -1, -3, x0+5, 4, 4, lambda x,y,z,w,h,d: O2 if y == h-1 else (N1 if y == 0 else (O1 if z == d-1 and y == 1 else nacre(x+z, y))))
    # cape de l'Empereur (rouge sombre, liseré d'or)
    for x in range(-6, 6):
        for y in range(2, 25):
            V[(x, y, -4)] = O2 if x in (-6, 5) or y == 2 else (CAPE1 if (x + y) % 5 else CAPE2)
    for x in range(-6, 6): V[(x, 24, -3)] = O2

def vue(f, dos=False, T=7):
    V = {}; corps(V); f(V)
    if dos: V = {(-x, y, -z): c for (x, y, z), c in V.items()}
    return rendu(V, T=T)

cas = [("Armure sacrée", sacree, False), ("… de dos", sacree, True), ("Armure impériale", imperiale, False), ("… de dos (cape)", imperiale, True)]
ims = [vue(f, d) for _, f, d in cas]
font = ImageFont.truetype(FB, 22)
cw = max(i.width for i in ims) + 20; ch = max(i.height for i in ims) + 50
out = Image.new('RGB', (cw * 4, ch), (32, 33, 38)); dr = ImageDraw.Draw(out)
for n, ((t, _, _), im) in enumerate(zip(cas, ims)):
    out.paste(im, (n * cw + (cw - im.width) // 2, 5))
    dr.text((n * cw + cw // 2 - dr.textlength(t, font=font) / 2, ch - 38), t, fill=(240, 205, 120), font=font)
out.save('apercu_armures.png'); print(out.size)
