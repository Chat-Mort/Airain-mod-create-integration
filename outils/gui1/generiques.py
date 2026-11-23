# Lot 1 bis : sprites génériques du pack HD (fourneaux, alambic, balise, ascenseurs), redessinés à la grille de qualité.
import math
from hd import *
from sprites import m_croix, m_coche, metal
ORANGE = dict(clair=hx('ffe08a'), base=hx('ffb347'), mi=hx('f07a1e'), sombre=hx('c24a12'), trait=hx('5a1c06'))
JAUNE = dict(clair=hx('fff6c8'), base=hx('ffe066'), mi=hx('ffc22e'), sombre=hx('e08a10'), trait=hx('6a3a06'))
FIOLE = dict(clair=hx('e6fbff'), base=hx('b4ecff'), mi=hx('7ccdf0'), sombre=hx('4a98c4'), trait=hx('1a3a5a'))

def annuler(): return centre(toile(18, 18), metal(m_croix(40, 9), ROUGE_VIF))
def valider(): return centre(toile(18, 18), metal(m_coche(46, 38, 9), VERT))

def fleche_chauffe():
    """Flèche du fourneau (24 x 16) : une flèche d'airain dont le canal rougeoie de métal en fusion (dessinée en progression)."""
    W, H = 72, 48
    m = masque(W, H); rect(m, 3, 15, 46, 33); poly(m, [(44, 3), (69, 24), (44, 45)])
    im = metal(m, EXPOSE)
    canal = masque(W, H); rect(canal, 8, 20, 48, 28); poly(canal, [(47, 13), (60, 24), (47, 35)])
    c = metal(canal, ORANGE, contour=False); im.alpha_composite(c)
    # éclats de chaleur dans le canal
    for x in range(12, 46, 9): im.putpixel((x, 22), ORANGE['clair']); im.putpixel((x + 1, 22), ORANGE['clair'])
    for (x, y) in ((8, 17), (38, 17), (8, 30), (38, 30)): rivet(im, x, y, EXPOSE)
    return im

def flamme():
    """Flamme de chaudière (14 x 14), en trois couches, avec deux escarbilles (dessinée du bas vers le haut)."""
    W = 42; im = Image.new('RGBA', (W, W))
    def goutte(cx, base, larg, haut, pal):
        m = masque(W, W); pts = []
        for k in range(41):
            t = k / 40; y = base - haut * t
            w = larg * (math.sin(math.pi * min(1, t * 1.15)) ** .8) * (1 - t * .55)
            pts.append((cx + w / 2 + math.sin(t * 7) * 1.5, y))
        for k in range(40, -1, -1):
            t = k / 40; y = base - haut * t
            w = larg * (math.sin(math.pi * min(1, t * 1.15)) ** .8) * (1 - t * .55)
            pts.append((cx - w / 2 + math.sin(t * 7) * 1.5, y))
        poly(m, pts); return m
    colle(im, metal(goutte(21, 41, 34, 40, ROUGE_VIF), ROUGE_VIF))
    colle(im, metal(goutte(21, 41, 22, 28, ORANGE), ORANGE, contour=False))
    colle(im, metal(goutte(21, 41, 11, 16, JAUNE), JAUNE, contour=False))
    for (x, y) in ((8, 8), (33, 4)): im.putpixel((x, y), JAUNE['clair']); im.putpixel((x + 1, y), ORANGE['base']); im.putpixel((x, y + 1), ORANGE['mi'])
    return im

def fleche_alambic():
    """Flèche de l'alambic (9 x 28) : un tube d'airain vers le bas, avec la potion qui y coule."""
    W, H = 27, 84
    m = masque(W, H); rect(m, 7, 0, 20, 66); poly(m, [(1, 62), (25, 62), (13, 83)])
    im = metal(m, EXPOSE, facettes=lambda x, y: 1 if x < 13 else -1)
    canal = masque(W, H); rect(canal, 11, 4, 16, 66); poly(canal, [(8, 66), (18, 66), (13, 76)])
    im.alpha_composite(biseau(canal, FIOLE, contour=False))
    for y in (14, 30, 46): rivet(im, 8, y, EXPOSE)
    return im

def bulles():
    """Bulles de l'alambic (12 x 29) : billes de verre qui montent, reflet en haut à gauche."""
    W, H = 36, 87; im = Image.new('RGBA', (W, H))
    for (cx, cy, r) in ((17, 76, 7), (8, 60, 5), (26, 50, 6), (15, 34, 4), (24, 20, 4), (10, 9, 3)):
        m = masque(W, H); ellipse(m, cx - r, cy - r, cx + r + 1, cy + r + 1)
        g = biseau(m, dict(clair=FIOLE['clair'], base=FIOLE['mi'], mi=FIOLE['sombre'], sombre=FIOLE['sombre'], trait=FIOLE['trait']))
        im.alpha_composite(g)
        im.putpixel((cx - r // 2, cy - r // 2), (255, 255, 255, 255))
        if r > 4: im.putpixel((cx - r // 2 + 1, cy - r // 2), (255, 255, 255, 255))
    return im

def jauge_poudre():
    """Jauge de poudre de blaze (18 x 4) : de la braise dans une gouttière d'airain."""
    W, H = 54, 12
    m = masque(W, H); rect(m, 0, 0, W, H); im = metal(m, EXPOSE, contour=False)
    c = masque(W, H); rect(c, 2, 3, W - 2, H - 3); im.alpha_composite(metal(c, ORANGE, contour=False))
    for x in range(4, W - 3, 6): im.putpixel((x, 4), JAUNE['clair'])
    return im

def poignee(etat, famille=None):
    """Poignée d'ascenseur (12 x 15) : plaque d'airain à rainures de prise, rivets ; grise quand rien ne défile."""
    pal = GRIS if etat == 'off' else (famille or OR)
    W, H = 36, 45
    m = masque(W, H); ImageDraw.Draw(m).rounded_rectangle([1, 1, W - 2, H - 2], radius=4, fill=255)
    im = metal(m, pal)
    for y in range(12, 34, 5):
        for x in range(7, W - 7): im.putpixel((x, y), pal['trait']); im.putpixel((x, y + 1), pal['clair'])
    for (x, y) in ((4, 4), (W - 7, 4), (4, H - 7), (W - 7, H - 7)): rivet(im, x, y, pal)
    return im

def tout():
    r = {'container/beacon/cancel': annuler(), 'container/beacon/confirm': valider(),
         'container/brewing_stand/brew_progress': fleche_alambic(), 'container/brewing_stand/bubbles': bulles(),
         'container/brewing_stand/fuel_length': jauge_poudre()}
    for f in ('furnace', 'blast_furnace', 'smoker'):
        r[f'container/{f}/burn_progress'] = fleche_chauffe(); r[f'container/{f}/lit_progress'] = flamme()
    for f in ('creative_inventory', 'loom', 'stonecutter'):
        fam = OR if f == 'creative_inventory' else PATINE      # le métier et le tailleur sont des outils d'atelier
        r[f'container/{f}/scroller'] = poignee('', fam); r[f'container/{f}/scroller_disabled'] = poignee('off')
    return r

# ---------------- empreintes en creux dans les fonds de conteneur (là où la jauge se remplit)
C = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/minecraft/textures/gui/container/'
EMPLACEMENTS = {   # fond : [(sprite, x, y) en px d'interface, comme le jeu]
    'furnace': [('furnace/burn_progress', 79, 34), ('furnace/lit_progress', 56, 36)],
    'blast_furnace': [('blast_furnace/burn_progress', 79, 34), ('blast_furnace/lit_progress', 56, 36)],
    'smoker': [('smoker/burn_progress', 79, 34), ('smoker/lit_progress', 56, 36)],
    'brewing_stand': [('brewing_stand/bubbles', 63, 14), ('brewing_stand/brew_progress', 97, 16, 'd')],
}
ARDOISE = (42, 46, 55)
def effacer(fond, x0, y0, x1, y1, cote='gd'):
    """Efface l'ancienne empreinte : chaque ligne reprend la couleur du fond juste à gauche (les filets du fond sont horizontaux)."""
    p = fond.load()
    for y in range(y0, y1):
        # le côté le plus sombre est l'ardoise du fond (les cadres voisins sont clairs)
        # l'échantillon le plus proche de l'ardoise du fond (ni cadre d'or, ni liseré rouge)
        ref = min((p[x, y] for x in ((x0 - 2, x0 - 5, x0 - 8) if 'g' in cote else ()) + ((x1 + 1, x1 + 4, x1 + 7) if 'd' in cote else ()) if 0 <= x < fond.width),
                  key=lambda c: sum((c[i] - ARDOISE[i]) ** 2 for i in range(3)))
        for x in range(x0, x1): p[x, y] = ref
def graver(fond, sprite, x0, y0):
    """Empreinte en creux de la forme du sprite : fond assombri, ombre en haut/gauche, arête claire en bas/droite."""
    a = sprite.split()[3]; q = a.load(); p = fond.load(); w, h = sprite.size
    def ins(x, y): return 0 <= x < w and 0 <= y < h and q[x, y] > 100
    for y in range(h):
        for x in range(w):
            if not ins(x, y): continue
            c = p[x0 + x, y0 + y]
            if not ins(x, y - 1) or not ins(x - 1, y): c = mix(c, (0, 0, 0, 255), .5)
            elif not ins(x, y + 1) or not ins(x + 1, y): c = mix(c, (255, 255, 255, 255), .1)
            else: c = mix(c, (0, 0, 0, 255), .28)
            p[x0 + x, y0 + y] = c
def fonds(r):
    sortie = {}
    for nom, places in EMPLACEMENTS.items():
        f = Image.open(C + nom + '.png').convert('RGBA')
        for pl in places:
            sp, x, y = pl[:3]; cote = pl[3] if len(pl) > 3 else 'gd'
            s = r['container/' + sp]
            # l'ancienne empreinte occupe la même place que l'ancien sprite (un texel de marge)
            effacer(f, x * S - 1, y * S - 1, x * S + s.width + 1, y * S + s.height + 1, cote)
            graver(f, s, x * S, y * S)
        sortie[nom] = f
    return sortie
