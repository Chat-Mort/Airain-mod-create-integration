import sys
sys.path.insert(0, '../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
exec(open('armure.py').read().split("# ---------------------------------------------------------------- SACRÉE")[0])
S1, S2, S3 = (14,22,28), (22,34,42), (34,50,60)          # noir du sculk
T1, T2 = (8,82,94), (14,112,124)                          # sarcelle
CY = (70,235,245,1); CY2 = (150,250,255,1)                # veines lumineuses (pleine lumière)
V1, V2, V3 = (52,28,86), (78,44,124), (112,70,170)        # violet des arcanes
AR, AR2 = (176,186,204), (214,222,236)                    # argent
AM = (170,110,230,1)                                      # cristal d'améthyste

def diademe(V, sacre=False):
    """Diadème d'Écho : un cercle fin d'argent noirci, cristaux cyan, gemme au front, vrilles de sculk."""
    for x in range(-5, 5):
        for z in (-5, 4): V[(x, 29, z)] = S3 if (x % 2) else AR
    for z in range(-5, 5):
        for x in (-5, 4): V[(x, 29, z)] = S3 if (z % 2) else AR
    V[(-1, 29, 5)] = CY2; V[(0, 29, 5)] = CY2; V[(-1, 30, 5)] = CY; V[(0, 30, 5)] = CY
    V[(-2, 29, 5)] = AR2; V[(1, 29, 5)] = AR2; V[(-1, 31, 4)] = CY; V[(0, 31, 4)] = CY
    for (x, z) in ((-5, 2), (4, 2), (-5, -2), (4, -2)):
        V[(x, 30, z)] = T2; V[(x, 31, z)] = CY if sacre else T2
    for (x, z) in ((-3, 4), (2, 4)): V[(x, 30, z)] = T1

def runique(V):
    """Palier runique : netherite noire, runes cyan gravées, filets d'argent (le pendant du sacré)."""
    def casque(x,y,z,w,h,d):
        if z == d-1 and 2 <= y <= 4 and 1 <= x <= w-2: return None if y == 3 and x in (2,3,6,7) else S2
        if y == 6: return AR if (x+z) % 2 else S3
        if y == 4 and (x + z) % 4 == 1 and z != d-1: return CY          # une ligne de runes autour du casque
        return S2 if (x*3+y) % 5 else S3
    boite(V, -5, 23, -5, 5, 33, 5, casque)
    diademe(V)
    def plastron(x,y,z,w,h,d):
        if z == d-1:
            if x in (0, w-1) or y in (0, h-1): return AR
            if (x, y) in ((4, 9), (5, 9), (4, 8), (5, 10), (3, 6), (6, 6), (2, 4), (7, 4), (4, 3), (5, 3), (4, 11), (5, 11)): return CY
            return S2 if (x+y) % 4 else S3
        return S2 if (x+y+z) % 5 else S1
    boite(V, -5, 11, -3, 5, 25, 3, plastron)
    for s in (1, -1):
        x0 = 4 if s == 1 else -9
        boite(V, x0, 11, -3, x0+5, 25, 3, lambda x,y,z,w,h,d: AR if y in (h-1, 1) else (CY if y == 7 and (x+z) % 2 == 0 else (S3 if (x+z) % 3 == 0 else S2)))
        boite(V, x0 - (1 if s == -1 else 0), 23, -4, x0+5+(1 if s == 1 else 0), 26, 4, lambda x,y,z,w,h,d: AR if y == h-1 else (CY if y == 1 and (x+z) % 4 == 0 else S1))
    for x0 in (-5, 0):
        boite(V, x0, 3, -3, x0+5, 13, 3, lambda x,y,z,w,h,d: CY if (z == d-1 and y == 5 and x == 2) else (AR if y in (4, h-1) and z == d-1 else (S2 if (x+y) % 4 else S3)))
        boite(V, x0, -1, -3, x0+5, 4, 4, lambda x,y,z,w,h,d: AR if y == h-1 else (S1 if y == 0 else (CY if z == d-1 and y == 1 and x == 2 else S2)))

def arcanique(V):
    """Armure de Morgana Dalmont : noir et violet des arcanes, veines cyan, cristaux, capuche et tabard."""
    def capuche(x,y,z,w,h,d):
        if z == d-1 and 1 <= y <= 5 and 1 <= x <= w-2: return None if y in (2, 3) and x in (2, 3, 6, 7) else (S1 if y < 6 else V1)
        if z == d-1 and y in (6, 7): return V2 if 1 <= x <= w-2 else V1
        if y >= h-2 and (x + z) % 4 == 0: return V3
        if x in (0, w-1) and (y + z) % 6 == 0: return CY
        return V1 if (x + y + z) % 5 else V2
    boite(V, -5, 23, -5, 5, 34, 5, capuche)
    for (x, y, z) in ((-5, 34, -5), (4, 34, -5), (-4, 35, -4), (3, 35, -4)): pass
    for k in range(4): V[(-1 + (k % 2), 34 + k // 2, -5 + 0)] = V2      # pointe de la capuche
    diademe(V, sacre=True)
    for (x, y) in ((-1, 31), (0, 31)): V[(x, y, 5)] = CY2
    def plastron(x,y,z,w,h,d):
        if z == d-1:
            if x in (0, w-1): return AR
            if x in (w//2 - 1, w//2) and 2 <= y <= h-3: return CY if y % 3 == 0 else T2
            if y in (0, h-1): return AR
            if (x + y) % 5 == 0: return V3
            return V1 if (x+y) % 3 else V2
        return S2
    boite(V, -5, 11, -3, 5, 25, 3, plastron)
    for (x, y) in ((-1, 21), (0, 21), (-1, 20), (0, 20)): V[(x, y, 3)] = AM
    for (x, y) in ((-2, 21), (1, 21), (-2, 20), (1, 20), (-1, 22), (0, 22), (-1, 19), (0, 19)): V[(x, y, 3)] = AR2
    for s in (1, -1):
        x0 = 4 if s == 1 else -9
        boite(V, x0, 11, -3, x0+5, 25, 3, lambda x,y,z,w,h,d: AR if y == 1 else (V1 if y < 6 else (CY if (x + y + z) % 7 == 0 else S2)))
        # épaulières de cristal : arêtes d'argent, cristaux qui pointent vers le haut
        boite(V, x0 - (1 if s == -1 else 0), 23, -4, x0+5+(1 if s == 1 else 0), 26, 4, lambda x,y,z,w,h,d: AR if y == 0 else (T1 if (x+z) % 2 else S2))
        for (dx, dz, hh) in ((1, -2, 3), (2, 1, 4), (3, -1, 2)):
            for k in range(hh):
                V[(x0 + dx + (1 if s == 1 else -1), 26 + k, dz)] = CY if k == hh - 1 else (T2 if k % 2 else CY2)
    # jupe et tabard (devant et derrière), longues pans violets à runes
    for x in range(-4, 4):
        for y in range(2, 13):
            col = AR if x in (-4, 3) or y == 2 else (CY if (x + y) % 6 == 0 and y < 11 else (V2 if (x + y) % 3 else V1))
            V[(x, y, 3)] = col
            V[(x, y, -4)] = col
    for x0 in (-5, 0):
        boite(V, x0, 3, -3, x0+5, 13, 3, lambda x,y,z,w,h,d: S2 if (x+y) % 4 else S3)
        boite(V, x0, -1, -3, x0+5, 4, 4, lambda x,y,z,w,h,d: AR if y == h-1 else (S1 if y == 0 else (CY if z == d-1 and y == 1 and x == 2 else V1)))

def vue(f, dos=False, T=7):
    V = {}; corps(V); f(V)
    if dos: V = {(-x, y, -z): c for (x, y, z), c in V.items()}
    return rendu(V, T=T)

cas = [("Palier runique", runique, False), ("… de dos", runique, True), ("Armure de Morgana", arcanique, False), ("… de dos", arcanique, True)]
ims = [vue(f, d) for _, f, d in cas]
font = ImageFont.truetype(FB, 22)
cw = max(i.width for i in ims) + 20; ch = max(i.height for i in ims) + 50
out = Image.new('RGB', (cw * 4, ch), (32, 33, 38)); dr = ImageDraw.Draw(out)
for n, ((t, _, _), im) in enumerate(zip(cas, ims)):
    out.paste(im, (n * cw + (cw - im.width) // 2, 5))
    dr.text((n * cw + cw // 2 - dr.textlength(t, font=font) / 2, ch - 38), t, fill=(150, 230, 240), font=font)
out.save('apercu_arcane.png'); print(out.size)
# le diadème seul, sur une tête nue
V = {}; corps(V); diademe(V)
tete = {k: v for k, v in V.items() if k[1] >= 23}
rendu(tete, T=14).save('apercu_diademe.png')
