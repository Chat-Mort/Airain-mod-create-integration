import sys
sys.path.insert(0, '../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
exec(open('armure.py').read().split("# ---------------------------------------------------------------- SACRÉE")[0])
NE1, NE2, NE3 = (40,34,42), (60,52,62), (86,76,88)       # netherite
F1, F2 = (24,14,34), (34,22,48)                           # noir-violet des fragments
V1, V2, V3 = (58,30,96), (86,48,140), (122,84,190)        # violet des arcanes (tissu)
LV = (190,160,255,1); LV2 = (226,210,255,1)               # lueur de l'Écho primordial
AR, AR2 = (168,170,190), (210,212,228)                    # argent

def diademe(V, sacre=False):
    for x in range(-5, 5):
        for z in (-5, 4): V[(x, 29, z)] = F2 if x % 2 else AR
    for z in range(-5, 5):
        for x in (-5, 4): V[(x, 29, z)] = F2 if z % 2 else AR
    for (x, y) in ((-1, 29), (0, 29), (-1, 30), (0, 30)): V[(x, y, 5)] = LV2 if y == 30 else LV
    V[(-2, 29, 5)] = AR2; V[(1, 29, 5)] = AR2
    for (x, z) in ((-5, 2), (4, 2), (-5, -2), (4, -2)):
        V[(x, 30, z)] = V2; V[(x, 31, z)] = LV if sacre else V3

def runique(V):
    """Encore de la netherite, avec du tissu qui annonce la robe : écharpe, ceinture, pans ; runes violettes lumineuses."""
    def casque(x,y,z,w,h,d):
        if z == d-1 and 2 <= y <= 4 and 1 <= x <= w-2: return None if y == 3 and x in (2,3,6,7) else NE1
        if y == 4 and (x + z) % 4 == 1 and z != d-1: return LV
        return NE2 if (x*3+y) % 5 else NE3
    boite(V, -5, 23, -5, 5, 33, 5, casque)
    diademe(V)
    def plastron(x,y,z,w,h,d):
        if z == d-1:
            if (x, y) in ((4, 9), (5, 9), (4, 8), (5, 10), (3, 6), (6, 6), (4, 11), (5, 11)): return LV
            if y in (0, h-1): return AR
            return NE2 if (x+y) % 4 else NE3
        return NE2 if (x+y+z) % 5 else NE1
    boite(V, -5, 11, -3, 5, 25, 3, plastron)
    for k in range(10):                                   # écharpe de tissu en travers du torse
        x, y = -4 + k, 23 - k
        for dy in (0, -1): V[(x, y + dy, 3)] = V2 if k % 3 else V3
    for x in range(-5, 5): V[(x, 12, 3)] = V1; V[(x, 12, -3)] = V1; V[(x, 13, 3)] = V2   # ceinture
    for s in (1, -1):
        x0 = 4 if s == 1 else -9
        boite(V, x0, 11, -3, x0+5, 25, 3, lambda x,y,z,w,h,d: AR if y == h-1 else (LV if y == 7 and (x+z) % 2 == 0 else (V1 if y < 4 else NE2)))
        boite(V, x0 - (1 if s == -1 else 0), 23, -4, x0+5+(1 if s == 1 else 0), 26, 4, lambda x,y,z,w,h,d: AR if y == h-1 else NE1)
    for x0 in (-5, 0):
        boite(V, x0, 3, -3, x0+5, 13, 3, lambda x,y,z,w,h,d: NE2 if (x+y) % 4 else NE3)
        boite(V, x0, -1, -3, x0+5, 4, 4, lambda x,y,z,w,h,d: AR if y == h-1 else (NE1 if y == 0 else NE2))
    for x in range(-4, 4):                                # pans de tissu devant et derrière
        for y in range(6, 12):
            V[(x, y, 4)] = V2 if (x + y) % 3 else V1
            V[(x, y, -4)] = V1

def arcanique(V):
    """La robe de Morgana : capuche, mantelet d'argent, robe longue jusqu'aux chevilles, runes brodées lumineuses."""
    def capuche(x,y,z,w,h,d):
        if z == d-1 and 1 <= y <= 6 and 1 <= x <= w-2: return None if y in (2, 3) and x in (2, 3, 6, 7) else F1
        if z == d-1 and y == 7: return AR
        if y >= h-2 and (x + z) % 4 == 0: return V3
        return V1 if (x + y + z) % 5 else V2
    boite(V, -5, 23, -5, 5, 34, 5, capuche)
    for k in range(4): V[(-1 + (k % 2), 34 + k // 2, -5)] = V2
    diademe(V, sacre=True)
    # robe : le corps et une jupe longue évasée qui couvre les jambes
    def robe(x,y,z,w,h,d):
        if z == d-1:
            if x in (w//2 - 1, w//2): return LV if y % 3 == 0 else F2      # broderie centrale
            if y in (0, h-1): return AR
            return V1 if (x + y) % 4 else V2
        return V1 if (x + y + z) % 4 else V2
    boite(V, -5, 11, -3, 5, 25, 3, robe)
    for y in range(-1, 12):
        e = 1 + (11 - y) // 5                             # s'évase vers le bas
        def jupe(x,yy,z,w,h,d, y=y):
            if yy == 0 and y == -1: return AR
            if (x + z + y) % 7 == 0 and y < 10: return LV
            return V2 if (x + y) % 3 else V1
        boite(V, -5 - e + 1, y, -3 - e + 1, 5 + e - 1, y + 1, 3 + e - 1, jupe)
    for x in range(-5, 5): V[(x, 12, 3)] = AR; V[(x, 13, 3)] = F2           # ceinture d'argent
    for (x, y) in ((-1, 20), (0, 20), (-1, 19), (0, 19)): V[(x, y, 3)] = LV2  # l'Écho primordial serti
    for (x, y) in ((-2, 20), (1, 20), (-2, 19), (1, 19), (-1, 21), (0, 21), (-1, 18), (0, 18)): V[(x, y, 3)] = AR2
    for s in (1, -1):
        x0 = 4 if s == 1 else -9
        # manches larges qui s'évasent au poignet
        boite(V, x0, 11, -3, x0+5, 25, 3, lambda x,y,z,w,h,d: AR if y == 1 else (LV if y == 2 and (x+z) % 2 == 0 else (V1 if (x+y) % 4 else V2)))
        boite(V, x0 - (1 if s == -1 else 0), 10, -4, x0 + 5 + (1 if s == 1 else 0), 14, 4, lambda x,y,z,w,h,d: AR if y == 0 else V2)
        # mantelet d'argent sur les épaules
        boite(V, x0 - (1 if s == -1 else 0), 23, -4, x0+5+(1 if s == 1 else 0), 26, 4, lambda x,y,z,w,h,d: AR2 if y == h-1 else (AR if (x+z) % 2 else F2))
    for x in range(-6, 6): V[(x, 24, -4)] = F2                             # dos du mantelet

def vue(f, dos=False, T=7):
    V = {}; corps(V); f(V)
    if dos: V = {(-x, y, -z): c for (x, y, z), c in V.items()}
    return rendu(V, T=T)

cas = [("Palier runique", runique, False), ("… de dos", runique, True), ("Robe de Morgana", arcanique, False), ("… de dos", arcanique, True)]
ims = [vue(f, d) for _, f, d in cas]
font = ImageFont.truetype(FB, 22)
cw = max(i.width for i in ims) + 20; ch = max(i.height for i in ims) + 50
out = Image.new('RGB', (cw * 4, ch), (32, 33, 38)); dr = ImageDraw.Draw(out)
for n, ((t, _, _), im) in enumerate(zip(cas, ims)):
    out.paste(im, (n * cw + (cw - im.width) // 2, 5))
    dr.text((n * cw + cw // 2 - dr.textlength(t, font=font) / 2, ch - 38), t, fill=(200, 180, 255), font=font)
out.save('apercu_arcane2.png'); print(out.size)
