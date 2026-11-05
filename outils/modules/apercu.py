import sys, math
sys.path.insert(0, '../balise7')
from concepts import rendu, LA, LA2, LA3, FER, FONTE, CU, OR
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TEX = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/entity/gardien.png').convert('RGBA')
R = 2  # voxels par pixel de modèle

def golem():
    V = {}
    def box(u, v, x0, y0, z0, w, h, d):
        for X in range(int(x0 * R), int((x0 + w) * R)):
            for Y in range(int(y0 * R), int((y0 + h) * R)):
                for Z in range(int(z0 * R), int((z0 + d) * R)):
                    mx, my, mz = X / R, Y / R, Z / R
                    fx, fy, fz = X == int(x0 * R), Y == int(y0 * R), Z == int(z0 * R)
                    bx_, by_, bz_ = X == int((x0 + w) * R) - 1, Y == int((y0 + h) * R) - 1, Z == int((z0 + d) * R) - 1
                    if not (fx or fy or fz or bx_ or by_ or bz_): continue
                    i, j, k = int(mx - x0), int(my - y0), int(mz - z0)
                    c = None
                    if fz: c = TEX.getpixel((u + d + i, v + d + j))                  # devant (z min)
                    elif bz_: c = TEX.getpixel((u + 2 * d + w + (w - 1 - i), v + d + j))  # dos
                    if fx and c is None: c = TEX.getpixel((u + (d - 1 - k), v + d + j)) # côté droit du golem (x min)
                    elif bx_ and c is None: c = TEX.getpixel((u + d + w + k, v + d + j))
                    if fy: c = TEX.getpixel((u + d + i, v + (d - 1 - k)))           # dessus
                    if c is None or c[3] == 0: c = (90, 80, 60, 255)
                    V[(-X, -Y, -Z)] = c[:3]
    box(0, 0, -4, -19, -7.5, 8, 10, 8)        # tête
    box(24, 0, -1, -12, -9.5, 2, 4, 2)        # nez
    box(0, 40, -9, -9, -6, 18, 12, 11)        # torse
    box(0, 70, -4.5, 3, -3, 9, 5, 6)          # taille
    box(60, 21, -13, -9.5, -3, 4, 30, 6)      # bras droit
    box(60, 58, 9, -9.5, -3, 4, 30, 6)        # bras gauche
    box(37, 0, -7.5, 8, -3, 6, 16, 5)         # jambe droite
    box(60, 0, 1.5, 8, -3, 6, 16, 5)          # jambe gauche
    return V

def put(V, x, y, z, c):   # coordonnées modèle (pixels, y vers le bas)
    V[(-int(math.floor(x * R)), -int(math.floor(y * R)), -int(math.floor(z * R)))] = c
def bloc(V, x0, y0, z0, w, h, d, c, f=None):
    for X in range(int(x0 * R), int((x0 + w) * R)):
        for Y in range(int(y0 * R), int((y0 + h) * R)):
            for Z in range(int(z0 * R), int((z0 + d) * R)):
                put(V, X / R, Y / R, Z / R, f(X / R, Y / R, Z / R) if f else c)
def cyl(V, axe, c1, c2, r, a0, a1, c, f=None):
    s = 1 / R
    a = a0
    while a < a1:
        u = -r
        while u <= r:
            w = -r
            while w <= r:
                if u * u + w * w <= r * r:
                    col = f(a, u, w) if f else c
                    if col:
                        if axe == 'z': put(V, c1 + u, c2 + w, a, col)
                        elif axe == 'y': put(V, c1 + u, a, c2 + w, col)
                        else: put(V, a, c1 + u, c2 + w, col)
                w += s
            u += s
        a += s

AMBRE = (255, 190, 80, 1); VERRE = (150, 200, 215); CYAN = (140, 230, 255, 1); VAP = (235, 235, 230, 1); RIV = (120, 122, 128)
CU2 = (150, 80, 50); OX = (85, 165, 140)

def lanterne(V):
    bloc(V, -2.5, -20, -5.5, 5, 1, 5, LA2)                 # embase rivetée
    bloc(V, -2, -24, -5, 4, 4, 4, AMBRE)                    # verre ambré allumé
    for (x, z) in ((-2, -5), (1.5, -5), (-2, -1.5), (1.5, -1.5)): bloc(V, x, -24, z, 0.5, 4, 0.5, LA)   # montants
    bloc(V, -2.5, -25, -5.5, 5, 1, 5, LA)                   # chapeau
    bloc(V, -1, -26.5, -4, 2, 1.5, 2, LA3)                  # cheminée
    bloc(V, -0.5, -27.5, -3.5, 1, 1, 1, LA2)
    bloc(V, -3, -21, -7, 6, 0.5, 1.5, LA3)                  # réflecteur vers l'avant

def longue_vue(V):
    bloc(V, -4.5, -17, -8, 9, 1, 8.5, LA2)                  # sangle autour du crâne
    cyl(V, 'z', -2, -15, 2.0, -11, -7.5, LA, lambda a, u, w: VERRE if u * u + w * w < 1.0 and a < -10 else (LA3 if a > -9 else LA))
    cyl(V, 'z', -2, -15, 1.4, -14.5, -11, LA2, lambda a, u, w: VERRE if u * u + w * w < 0.6 and a < -14 else (LA3 if int(a*2) % 3 == 0 else LA2))
    bloc(V, -4.6, -16, -8, 0.6, 1.5, 3, LA3)                # pivot latéral

def canon(V):
    bloc(V, -13.5, -11, -3.5, 5, 1.5, 6, FER)               # support sur l'épaule
    bloc(V, -12.5, -13, -1.5, 3, 2, 2, LA2)                 # tourelle
    cyl(V, 'z', -11, -13.5, 1.6, -9, 3, (176, 120, 70), lambda a, u, w: FONTE if u * u + w * w < 0.7 else ((150, 100, 55) if int(a) % 4 == 0 else (196, 140, 80)))
    cyl(V, 'z', -11, -13.5, 2.0, -9.5, -8, LA3)             # bouche
    cyl(V, 'z', -11, -13.5, 0.9, -9.6, -9.4, FONTE)
    cyl(V, 'z', -11, -13.5, 2.1, 2, 4, LA2)                 # culasse

def tesla(V):
    bloc(V, -3, -10, 4.5, 6, 1.5, 3, FER)                   # embase entre les épaules
    def spire(a, u, w):
        return CU if int((a + 30) * 2) % 2 == 0 else CU2
    cyl(V, 'y', 0, 6, 1.6, -19, -10, CU, spire)            # bobine
    cyl(V, 'y', 0, 6, 2.6, -21.5, -19, LA)                  # tore
    cyl(V, 'y', 0, 6, 1.2, -22.5, -21.5, LA3)
    for (x, y, z) in ((2.5, -23, 6), (3.5, -24, 6.5), (-2.5, -22.5, 5.5), (-3.5, -23.5, 5), (0.5, -24, 8.5), (1, -25, 9)):
        put(V, x, y, z, CYAN)

def blindage(V):
    ACIER = (78, 80, 88); ACIER2 = (100, 102, 112)
    def plaque(x0, x1, y0, y1):
        def f(x, y, z):
            bord = x < x0 + 0.6 or x > x1 - 1.1 or y < y0 + 0.6 or y > y1 - 1.1
            if bord and (round(x * 2) % 5 == 1) and (round(y * 2) % 5 == 1 or y < y0 + 0.6 or y > y1 - 1.1): return LA3   # rivets de laiton
            return LA2 if bord else (ACIER2 if (round(y * 2) % 6) < 3 else ACIER)
        return f
    bloc(V, -7, -8, -7, 14, 7, 1, None, plaque(-7, 7, -8, -1))      # plastron à lames
    bloc(V, -5, -1, -6.8, 10, 2.5, 0.8, None, plaque(-5, 5, -1, 1.5))
    for x0 in (-13.5, 8.5):                                         # brassards
        bloc(V, x0, 5, -3.5, 5, 6, 7, None, plaque(x0, x0 + 5, 5, 11))
    for x0 in (-14, 8.5):                                           # épaulières
        bloc(V, x0, -11, -4, 5.5, 2, 8, None, lambda x, y, z: LA3 if round(z * 2) % 5 == 0 else LA2)

def chaudiere(V):
    cyl(V, 'y', 0, 9.5, 3.5, -8, 2, CU, lambda a, u, w: LA2 if int(a) in (-7, -3, 1) else CU)   # chaudière
    cyl(V, 'y', 0, 9.5, 3.5, -9, -8, LA)
    cyl(V, 'y', 2, 10, 0.9, -14, -9, FONTE)                 # cheminée
    for (x, y, z) in ((2, -15, 10), (2.5, -16, 10.5), (1.5, -17, 11), (2, -18, 10), (3, -17.5, 11.5), (1, -16.5, 9.5)):
        put(V, x, y, z, VAP)
    for s in (-1, 1): bloc(V, s * 5 - 0.5, -8, 5, 1, 1, 4, LA3)   # tuyaux vers les épaules
    bloc(V, -1, -4, 13, 2, 2, 0.5, (220, 60, 40))           # manomètre

def tete_lanterne(V):
    """La tête devient une lanterne : visage gardé, yeux lumineux ; côtés, dos et dessus en verre ambré sous armature de laiton."""
    x0, x1, y0, y1, z0, z1 = -4 * R, 4 * R, -19 * R, -9 * R, int(-7.5 * R), int(0.5 * R)
    AMB = (255, 196, 90, 1); AMB2 = (255, 170, 60, 1)
    for X in range(x0, x1):
        for Y in range(y0, y1):
            for Z in range(z0, z1):
                cle = (-X, -Y, -Z)
                if cle not in V: continue
                front = Z == z0
                if front:
                    c = V[cle]
                    if c[0] > 120 and c[1] < 90 and c[2] < 70: V[cle] = (255, 120, 50, 1)    # yeux : braise vive
                    continue
                # armature : arêtes du cube, montant central et traverse
                ex = X in (x0, x1 - 1); ey = Y in (y0, y1 - 1); ez = Z in (z0 + 1, z1 - 1)
                arete = (ex and ey) or (ex and ez) or (ey and ez) or (ex and Z in (z0, z0 + 1))
                montant = (X in (-1, 0) and (Y == y0 or Z == z1 - 1)) or (Z in (-6, -7) and (X in (x0, x1 - 1) or Y == y0)) or (Y in (-28, -27) and (X in (x0, x1 - 1) or Z == z1 - 1))
                if arete: V[cle] = LA2
                elif montant: V[cle] = LA
                else: V[cle] = AMB if (X * 3 + Y * 5 + Z * 7) % 11 else AMB2
    # rivets aux coins du cadre, chapeau ajouré
    bloc(V, -2, -20, -5, 4, 1, 4, LA)
    bloc(V, -1, -21, -4, 2, 1, 2, LA3)

def rend(mods, dos=False, T=3):
    V = golem()
    for m in mods: m(V)
    if dos: V = {(-x, y, -z): c for (x, y, z), c in V.items()}
    return rendu(V, T=T)

font = ImageFont.truetype(FB, 20)
cas = [("Tête-lanterne · Canon\nBlindage riveté", [tete_lanterne, canon, blindage], False),
       ("Longue-vue · Bobine Tesla\nChaudière de secours", [longue_vue, tesla, chaudiere], False),
       ("Longue-vue · Tesla · Chaudière\nvu de dos", [longue_vue, tesla, chaudiere], True),
       ("Tête-lanterne · Canon · Blindage\nvu de dos", [tete_lanterne, canon, blindage], True)]
ims = [rend(m, d, T=5) for _, m, d in cas]
cw = max(i.width for i in ims) + 40; ch = max(i.height for i in ims) + 80
out = Image.new('RGB', (cw * 2, ch * 2), (32, 33, 38)); d = ImageDraw.Draw(out)
for n, ((t, _, _), im) in enumerate(zip(cas, ims)):
    X, Y = (n % 2) * cw, (n // 2) * ch
    out.paste(im, (X + (cw - im.width) // 2, Y + 10))
    for k, l in enumerate(t.split("\n")):
        d.text((X + cw // 2 - d.textlength(l, font=font) // 2, Y + ch - 66 + k * 26), l, fill=(240, 205, 120), font=font)
out.save('apercu_modules.png'); print(out.size)
