# Lot 5a de la passe qualité : FTB Quests.
# - Formes des quêtes : le rond (forme par défaut du pack, la plus vue) et le carré étaient restés ceux d'origine
#   (dégradé blanc) ; les cinq formes utilisées sont refaites d'un même dessin : fond d'ardoise à médaillon gravé,
#   anneau d'airain en biseau (teinté par le jeu selon l'état de la quête), rivets aux angles.
# - Icônes du livre de quêtes passées en 3x selon la règle du lot 3 (trait : Scale3x + contour ; objet texturé : pixels nets).
import math, os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
sys.path.insert(0, '/home/claude/sauvegarde/outils/gui1'); sys.path.insert(0, '/home/claude/sauvegarde/outils/ars'); sys.path.insert(0, '/home/claude/sauvegarde/outils/ways')
from ars import scale3x

SRC = '/tmp/src5/ftbq/common/src/main/resources/assets/ftbquests/textures/'
HD = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/ftbquests/textures/'
N = 128; SS = 4                        # taille des formes, sur-échantillonnage pour des bords propres

def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
ARD = dict(clair=hx('4b5160'), base=hx('3e434f'), fond=hx('343844'), creux=hx('272a32'), noir=hx('1b1e24'))

def masque(nom):
    """Masque de la forme à 4x : celui d'origine (shape.png, il sert aussi au clic), lissé puis seuillé."""
    m = Image.open(f'{SRC}shapes/{nom}/shape.png').convert('RGBA').split()[3]
    if nom in ('circle',):      # le rond d'origine est en marches : on le trace juste
        g = np.mgrid[0:N * SS, 0:N * SS] + 0.5; r = N * SS / 2
        return np.hypot(g[0] - r, g[1] - r) <= r - 0.5 * SS
    big = m.resize((N * SS, N * SS), Image.BILINEAR).filter(ImageFilter.GaussianBlur(SS * 0.6))
    return np.array(big) > 127

def reduit(rgba):
    """Ramène le dessin 4x à 128 px en moyennant (couleur pondérée par l'alpha)."""
    a = rgba[..., 3:4].astype(float) / 255
    pre = rgba[..., :3] * a
    def bloc(x): return x.reshape(N, SS, N, SS, -1).mean(axis=(1, 3))
    A = bloc(a); C = np.where(A > 0, bloc(pre) / np.maximum(A, 1e-6), 0)
    return Image.fromarray(np.concatenate([C, A * 255], axis=-1).round().clip(0, 255).astype(np.uint8), 'RGBA')

def lumiere(d):
    """Éclairage venu d'en haut à gauche, d'après la pente de la carte de distance."""
    gy, gx = np.gradient(d)
    n = np.hypot(gx, gy) + 1e-6
    return (-gx * -0.7071 + -gy * -0.7071) / n     # 1 : face tournée vers la lumière

# Rivets posés au milieu de l'anneau, dans ces directions (degrés, 0 = à droite, sens horaire à l'écran)
RIVETS = {'circle': (45, 135, 225, 315), 'square': (45, 135, 225, 315), 'rsquare': (45, 135, 225, 315),
          'hexagon': (90, 150, 210, 270, 330, 30), 'gear': ()}

def forme(nom, ep=7.5):
    m = masque(nom)
    # distance au bord, en texels ; on borde de vide, sinon le bord de l'image ne compte pas comme un bord (carré)
    d = ndimage.distance_transform_edt(np.pad(m, SS))[SS:-SS, SS:-SS] / SS
    L = lumiere(d)
    H = N * SS
    # --- anneau (outline) : gris neutre, le jeu le teinte (or, airain, gris selon l'état)
    out = np.zeros((H, H, 4))
    anneau = m & (d <= ep)
    v = 0.78 + 0.22 * L                                     # biseau : clair en haut à gauche
    v = np.where(d < 1.2, 0.42, v)                          # arête extérieure sombre
    v = np.where((d > ep - 1.2) & anneau, 0.5 - 0.12 * L, v)   # arête intérieure (le creux vers le fond)
    v = np.where((d > 2.2) & (d < 3.2), v + 0.1, v)         # filet clair sur l'anneau
    g = (np.clip(v, 0, 1) * 255)
    out[anneau] = np.stack([g, g, g, np.full_like(g, 255)], -1)[anneau]
    # rivets : dôme clair, ombre en bas à droite
    yy, xx = np.mgrid[0:H, 0:H] / SS
    pts = []
    for ang in RIVETS[nom]:
        # le long du rayon depuis le centre, on garde le dernier point où la distance au bord vaut encore la moitié de l'anneau
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang)); p = None
        for t in np.arange(0, 64 * 1.5, 0.05):
            x, y = 64 + dx * t, 64 + dy * t
            if not (0 <= x < N and 0 <= y < N) or not m[int(y * SS), int(x * SS)]: break
            if d[int(y * SS), int(x * SS)] >= ep / 2: p = (x, y)
        if p: pts.append(p)
    for (rx, ry) in pts:
        r = np.hypot(xx - rx, yy - ry)
        ombre = (np.hypot(xx - rx - 0.8, yy - ry - 0.8) <= 2.6) & m
        out[ombre] = [70, 70, 70, 255]
        dome = r <= 2.3
        lum = np.clip(1.0 - 0.18 * ((xx - rx + 0.9) ** 2 + (yy - ry + 0.9) ** 2), 0.55, 1.0)
        val = (lum * 255)[..., None]
        out[dome & m] = np.concatenate([np.repeat(val, 3, -1), np.full_like(val, 255)], -1)[dome & m]
    # --- fond : ardoise, plus sombre vers le bord, médaillon gravé au centre (sous l'icône de la quête)
    bg = np.zeros((H, H, 4))
    dedans = m
    rc = np.hypot(xx - 64, yy - 64)
    prof = np.clip(d / 26, 0, 1)
    base = np.array(ARD['creux']) * (1 - prof[..., None]) + np.array(ARD['base']) * prof[..., None]
    grav = (rc > 33) & (rc < 36)                            # gorge du médaillon : sombre en haut à gauche, clair en bas à droite
    cote = ((xx - 64) + (yy - 64)) / np.maximum(rc, 1)      # >0 en bas à droite
    t = np.clip((cote + 1) / 2, 0, 1)[..., None]           # ombre continue tout autour de la gorge
    base = np.where(grav[..., None], np.array(ARD['noir']) * (1 - t) + np.array(ARD['clair']) * t, base)
    base = np.where((rc <= 33)[..., None], np.array(ARD['fond']) * 1.0, base)
    bg[dedans] = np.concatenate([base, np.full(base.shape[:-1] + (1,), 255)], -1)[dedans]
    return reduit(out), reduit(bg)

# ---------- icônes ----------
TRAIT = hx('15171b')
def contour(im):
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0); g = a.filter(ImageFilter.MaxFilter(3))
    out = Image.new('RGBA', (im.width + 2, im.height + 2)); mm = Image.new('L', out.size); mm.paste(g, (1, 1))
    out.paste(Image.new('RGBA', out.size, TRAIT + (255,)), (0, 0), mm); out.alpha_composite(im, (1, 1)); return out
def hybride(im):
    nn = im.resize((im.width * 3, im.height * 3), Image.NEAREST); sc = scale3x(im)
    out = nn.copy(); o = out.load(); a = sc.load(); n = nn.load()
    for y in range(out.height):
        for x in range(out.width):
            if a[x, y][3] == 0: o[x, y] = (0, 0, 0, 0)
            elif n[x, y][3] == 0: o[x, y] = a[x, y]
    return out

# ---------- icônes du livre ----------
# Lot 5a, retour de Liam : Scale3x donne l'aspect « upscale ». Les icônes au trait sont donc retracées à 48 px
# (même dessin, mêmes couleurs, bords nets sans flou) ; celles d'aplats droits sont agrandies au pixel ;
# les objets texturés gardent leurs pixels nets (hybride du lot 3). Pas de contour ajouté : FTB n'en met pas.
from PIL import ImageDraw
K = 8                                        # sur-échantillonnage du tracé, ramené ensuite à des pixels pleins
def calque(w=48, h=48): im = Image.new('L', (w * K, h * K)); return im, ImageDraw.Draw(im)
def plein(m):
    """Masque tracé à 8x -> pixels pleins (un pixel est peint s'il est couvert à moitié) : net, sans demi-teinte."""
    return m.resize((m.width // K, m.height // K), Image.BOX).point(lambda v: 255 if v >= 128 else 0)
def P(pts): return [(x * K, y * K) for x, y in pts]
def peint(dest, m, c): dest.paste(Image.new('RGBA', dest.size, c + (255,)), (0, 0), plein(m))

BL, BL2, GR = hx('ffffff'), hx('f8f8f8'), hx('e7e7e7')
def fleche(sens):
    # triangle plein, face haute éclairée, face basse ombrée (comme l'original), pointe à droite puis tournée
    im = Image.new('RGBA', (48, 48))
    m, d = calque(); d.polygon(P([(3, 3), (3, 45), (38, 24)]), fill=255); peint(im, m, BL)
    m, d = calque(); d.polygon(P([(3, 24), (38, 24), (3, 45)]), fill=255)
    m2, d2 = calque(); d2.polygon(P([(3, 24), (38, 24), (3, 45)]), fill=255); d2.polygon(P([(3, 20), (31, 24), (3, 38)]), fill=0)
    peint(im, m2, GR)
    m3, d3 = calque(); d3.polygon(P([(3, 3), (38, 24), (3, 3.1)]), fill=255); d3.line(P([(3, 4.5), (38, 24)]), fill=255, width=3 * K)
    m3b, d3b = calque(); d3b.polygon(P([(3, 3), (3, 45), (38, 24)]), fill=255)
    from PIL import ImageChops
    peint(im, ImageChops.multiply(m3, m3b), BL2)
    # la gauche est un miroir (la lumière reste en haut) ; le bas, un quart de tour (ombre à gauche, comme l'original)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if sens == 'left' else im.rotate(-90) if sens == 'down' else im

def croix():
    im = Image.new('RGBA', (48, 48))
    def barres(d, ep):
        d.line(P([(9, 9), (39, 39)]), fill=255, width=int(ep * K)); d.line(P([(39, 9), (9, 39)]), fill=255, width=int(ep * K))
    m, d = calque(); barres(d, 13); peint(im, m, hx('383838'))
    m, d = calque(); barres(d, 8); peint(im, m, hx('d72c17'))
    m, d = calque(); d.line(P([(9, 8), (39, 38)]), fill=255, width=4 * K); d.line(P([(39, 8), (9, 38)]), fill=255, width=4 * K)
    m2, d2 = calque(); barres(d2, 8)
    from PIL import ImageChops
    peint(im, ImageChops.multiply(m, m2), hx('ff3f27'))
    return im

def loupe():
    im = Image.new('RGBA', (48, 48))
    m, d = calque(); d.line(P([(5, 43), (19, 29)]), fill=255, width=6 * K); peint(im, m, hx('9b9b9b'))
    m, d = calque(); d.ellipse(P([(15, 0), (49, 34)]) and [15 * K, 0, 47 * K, 32 * K], fill=255); peint(im, m, hx('9b9b9b'))
    m, d = calque(); d.ellipse([18 * K, 3 * K, 44 * K, 29 * K], fill=255); peint(im, m, GR)
    m, d = calque(); d.ellipse([18 * K, 3 * K, 41 * K, 26 * K], fill=255); peint(im, m, BL)
    m, d = calque(); d.arc([22 * K, 7 * K, 38 * K, 23 * K], 160, 250, fill=255, width=3 * K); peint(im, m, GR)   # reflet du verre
    return im

def engrenage():
    im = Image.new('RGBA', (48, 48)); c = 24
    def roue(d, R, r, dents=8, lar=0.34):
        pts = []
        for k in range(dents * 2):
            a0 = math.pi * k / dents
            rr = R if k % 2 == 0 else r
            for t in (-lar, lar):
                a = a0 + t * math.pi / dents * (1 if k % 2 == 0 else 1.6)
                pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
        d.polygon(P(pts), fill=255)
    m, d = calque(); roue(d, 21.5, 17); peint(im, m, hx('878787'))
    m, d = calque(); roue(d, 19, 14.5); peint(im, m, GR)
    m, d = calque(); roue(d, 19, 14.5); d.rectangle([0, 25 * K, 48 * K, 48 * K], fill=0); peint(im, m, BL)
    m, d = calque(); d.ellipse([16 * K, 16 * K, 32 * K, 32 * K], fill=255); peint(im, m, hx('878787'))
    m, d = calque(); d.ellipse([19 * K, 19 * K, 29 * K, 29 * K], fill=255)
    im.paste((0, 0, 0, 0), (0, 0), plein(m)); return im

def oeil():
    im = Image.new('RGBA', (48, 48))
    def amande(d, e):
        d.chord([0 + e, 4 + e, 48 - e, 60 - e], 200, 340, fill=255) if False else None
        d.polygon(P([(1 + e, 24)] + [(24 + (23 - e) * math.cos(a), 24 - (17 - e) * math.sin(a)) for a in [math.pi * i / 24 for i in range(25)]][::-1]
                    + [(24 + (23 - e) * math.cos(a), 24 + (17 - e) * math.sin(a)) for a in [math.pi * i / 24 for i in range(25)]]), fill=255)
    m, d = calque(); amande(d, 0); peint(im, m, hx('383838'))
    m, d = calque(); amande(d, 3); peint(im, m, hx('cacccb'))
    m, d = calque(); amande(d, 3); d.rectangle([0, 30 * K, 48 * K, 48 * K], fill=0); peint(im, m, BL)
    m, d = calque(); d.ellipse([15 * K, 15 * K, 33 * K, 33 * K], fill=255); peint(im, m, hx('383838'))
    m, d = calque(); d.ellipse([18 * K, 18 * K, 30 * K, 30 * K], fill=255); peint(im, m, hx('b7b7b7'))
    m, d = calque(); d.ellipse([20 * K, 19 * K, 28 * K, 26 * K], fill=255); peint(im, m, hx('f7f7f7'))
    return im

def epingle():
    # punaise dessinée droite (tête, corps, collerette, pointe) puis penchée de 45° comme l'original
    def tourne(m): return m.rotate(-45, resample=Image.BILINEAR, center=(24 * K, 24 * K))
    im = Image.new('RGBA', (48, 48))
    def couche(fn, c):
        m, d = calque(); fn(d); peint(im, tourne(m), c)
    couche(lambda d: d.line(P([(24, 30), (24, 47)]), fill=255, width=int(2.4 * K)), GR)                 # pointe
    couche(lambda d: d.rounded_rectangle(P([(13, 26), (35, 31)]), radius=2 * K, fill=255), BL2)          # collerette
    couche(lambda d: d.polygon(P([(18, 9), (30, 9), (28, 27), (20, 27)]), fill=255), BL)                 # corps
    couche(lambda d: d.polygon(P([(24, 9), (30, 9), (28, 27), (24, 27)]), fill=255), GR)                 # flanc ombré
    couche(lambda d: d.rounded_rectangle(P([(15, 2), (33, 9)]), radius=2 * K, fill=255), BL)             # tête
    couche(lambda d: d.rectangle(P([(15, 6.5), (33, 9)]), fill=255), BL2)
    return im

def maillons():
    # deux maillons entrelacés (icône de 32 px -> 96) : le droit passe devant en haut, le gauche devant en bas
    im = Image.new('RGBA', (96, 96))
    G, D = (12, 32, 56, 64), (40, 32, 84, 64)
    def anneau(box, ep=6, plus=0):
        m, d = calque(96, 96)
        b = [box[0] - plus, box[1] - plus, box[2] + plus, box[3] + plus]
        d.rounded_rectangle([v * K for v in b], radius=(b[3] - b[1]) / 2 * K, outline=255, width=int((ep + 2 * plus) * K)); return m
    from PIL import ImageChops
    def haut(m, y=48):
        m = m.copy(); ImageDraw.Draw(m).rectangle([0, y * K, 96 * K, 96 * K], fill=0); return m
    def bas(m, y=48):
        m = m.copy(); ImageDraw.Draw(m).rectangle([0, 0, 96 * K, y * K], fill=0); return m
    mg, md = anneau(G), anneau(D)
    # entailles : là où un maillon passe devant, l'autre s'interrompt de 2 px
    eg = ImageChops.multiply(mg, ImageChops.invert(haut(anneau(D, plus=2))))
    ed = ImageChops.multiply(md, ImageChops.invert(bas(anneau(G, plus=2))))
    for m in (eg, ed): peint(im, m, BL)
    for m in (eg, ed): peint(im, bas(m, 52), GR)            # dessous ombré
    return im

def pixel3(nom):
    im = Image.open(f'{SRC}gui/{nom}.png').convert('RGBA'); return im.resize((im.width * 3, im.height * 3), Image.NEAREST)

TRACES = {'arrow_collapsed': lambda: fleche('right'), 'arrow_right': lambda: fleche('right'), 'arrow_expanded': lambda: fleche('down'),
          'arrow_left': lambda: fleche('left'), 'close': croix, 'search': loupe, 'settings': engrenage, 'hidden': oeil,
          'pin': epingle, 'link': maillons, 'burger': lambda: pixel3('burger'), 'info': lambda: pixel3('info')}
TRAITS = list(TRACES)
TEXTURES = ['eraser', 'editor', 'editor_white', 'pagebreak', 'emergency_items', 'chain_link',
            'alert', 'collect_rewards', 'guide', 'quest_locked', 'shop', 'save']
def icone(nom, net):
    if not net: return TRACES[nom]()
    im = Image.open(f'{SRC}gui/{nom}.png').convert('RGBA'); w, h = im.size
    bb = im.getbbox(); out = Image.new('RGBA', (w * 3, h * 3))
    out.alpha_composite(hybride(im.crop(bb)), (bb[0] * 3, bb[1] * 3)); return out

def sorties():
    s = {}
    for nom in ('circle', 'square', 'rsquare', 'hexagon', 'gear'):
        o, b = forme(nom)
        s[f'shapes/{nom}/outline.png'] = o; s[f'shapes/{nom}/background.png'] = b
        s[f'shapes/{nom}/shape.png'] = Image.open(f'{SRC}shapes/{nom}/shape.png').convert('RGBA')
    for n in TRAITS: s[f'gui/{n}.png'] = icone(n, False)
    for n in TEXTURES: s[f'gui/{n}.png'] = icone(n, True)
    return s

if __name__ == '__main__':
    dest = sys.argv[1] if len(sys.argv) > 1 else '/tmp/l5/apres/'
    for k, im in sorties().items():
        os.makedirs(os.path.dirname(dest + k), exist_ok=True); im.save(dest + k)
    print('ok', dest)
