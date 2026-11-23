# Lot 3 : Waystones. Icônes d'origine agrandies en Scale3x (le sens reste), boutons au style du pack,
# quatre icônes redessinées pour l'univers (avant-postes au lieu des villages, voyageurs, équipes, foyers), menu des modificateurs.
import os
from hd import *
from sprites import bouton, metal, OR, ROUGE
from ars import scale3x
O = '/tmp/ways/common/src/main/resources/assets/waystones/textures/gui/'
D = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/waystones/textures/gui/'
DISP = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/minecraft/textures/gui/container/dispenser.png'

def couleurs(*noms):
    s = set()
    for n in noms:
        for c in Image.open(O + n).convert('RGBA').getdata():
            if c[3]: s.add(c[:3])
    return s
FOND_BOUTON = couleurs('sprites/widgets/small_button_blank.png', 'sprites/widgets/small_button_blank_highlighted.png')
def contour(im, c=hx('15171b')):
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0); g = a.filter(ImageFilter.MaxFilter(3))
    out = Image.new('RGBA', (im.width + 2, im.height + 2)); m = Image.new('L', out.size); m.paste(g, (1, 1))
    out.paste(Image.new('RGBA', out.size, c), (0, 0), m); out.alpha_composite(im, (1, 1)); return out
def icone(rel, sans_fond=False):
    im = Image.open(O + rel).convert('RGBA')
    if sans_fond:
        # on retire le fond du bouton d'origine par remplissage depuis les bords : seules les couleurs du fond,
        # reliées au bord, partent (les blancs et gris de l'icône restent)
        p = im.load(); w, h = im.size
        # le liseré du bouton (2 px) part en entier ; dedans, seules les teintes de fond du bouton vierge, sans le blanc
        fond = {c for c in FOND_BOUTON if c != (255, 255, 255)}
        for y in range(h):
            for x in range(w):
                if x < 2 or y < 2 or x >= w - 2 or y >= h - 2: p[x, y] = (0, 0, 0, 0)
        pile = [(x, y) for x in range(w) for y in range(h) if x in (2, w - 3) or y in (2, h - 3)]; vu = set()
        while pile:
            x, y = pile.pop()
            if (x, y) in vu or not (0 <= x < w and 0 <= y < h): continue
            vu.add((x, y))
            if p[x, y][3] == 0 or p[x, y][:3] in fond:
                p[x, y] = (0, 0, 0, 0); pile += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    bb = im.getbbox(); return contour(scale3x(im.crop(bb))), bb

# ---------------- icônes de groupe redessinées pour l'univers du pack
CUIR = dict(clair=hx('c08a5a'), base=hx('9a6638'), mi=hx('7a4c28'), sombre=hx('5a361a'), trait=hx('24140a'))
def ic_avant_poste():
    """Avant-poste (remplace les villages) : tour d'airain crénelée, porte, fanion cramoisi."""
    im = Image.new('RGBA', (48, 48)); m = masque(48, 48)
    rect(m, 12, 16, 36, 46); rect(m, 10, 11, 38, 17)
    for x in (10, 18, 26, 34): rect(m, x, 6, x + 4, 11)
    g = metal(m, OR); colle(im, g)
    porte = masque(48, 48); ImageDraw.Draw(porte).rounded_rectangle([20, 32, 28, 46], radius=3, fill=255)
    pp = porte.load()
    for y in range(48):
        for x in range(48):
            if pp[x, y]: im.putpixel((x, y), ARD['abime'])
    for y in range(0, 7): im.putpixel((24, y), OR['trait'])
    f = masque(48, 48); poly(f, [(25, 0), (34, 2), (25, 5)]); colle(im, biseau(f, ROUGE, contour=False))
    return im
def silhouette(cx, pal, w=48, h=48, tete=7, buste=13):
    m = masque(w, h); ellipse(m, cx - tete, 6, cx + tete + 1, 6 + 2 * tete + 1)
    ImageDraw.Draw(m).rounded_rectangle([cx - buste, 6 + 2 * tete + 3, cx + buste, h - 2], radius=8, fill=255)
    return metal(m, pal)
def ic_voyageur(): return centre(Image.new('RGBA', (48, 48)), silhouette(24, OR))
def ic_equipes():
    im = Image.new('RGBA', (48, 48)); colle(im, silhouette(30, dict(OR, base=OR['mi'], clair=OR['base']), tete=6, buste=11)); colle(im, silhouette(17, OR, tete=6, buste=11)); return im
def ic_foyer():
    im = Image.new('RGBA', (48, 48)); m = masque(48, 48); rect(m, 10, 22, 38, 46); poly(m, [(4, 24), (24, 4), (44, 24)])
    colle(im, metal(m, OR))
    for (x0, y0, x1, y1, c) in ((20, 32, 28, 46, ARD['abime']), (13, 27, 18, 32, hx('ffd070')), (30, 27, 35, 32, hx('ffd070'))):
        ImageDraw.Draw(im).rectangle([x0, y0, x1 - 1, y1 - 1], fill=c)
    rect_c = masque(48, 48); rect(rect_c, 32, 6, 37, 16); colle(im, metal(rect_c, ARD and dict(clair=hx('8a8e9a'), base=hx('6a6e7a'), mi=hx('54586a'), sombre=hx('40444e'), trait=hx('15171b'))))
    return im
import icones as I
def ic_alias():
    im = Image.new('RGBA', (46, 46)); m = masque(46, 46)
    ImageDraw.Draw(m).arc([4, 4, 22, 22], 0, 330, fill=255, width=3); ImageDraw.Draw(m).arc([9, 9, 17, 17], 90, 360, fill=255, width=3)
    colle(im, metal(m, dict(clair=hx('ffffff'), base=hx('f0f2f6'), mi=hx('c8ccd6'), sombre=hx('a0a6b2'), trait=hx('15171b'))))
    c = I.crayon().resize((32, 32), Image.NEAREST); colle(im, c, 14, 14); return im
def ic_pierre():
    g = I.P('a8adb6', '8a909a', '6c727c', '50565e')
    return I.facettes(40, 38, [([(6, 10), (18, 3), (34, 8), (36, 26), (22, 35), (4, 28)], g[2]), ([(6, 10), (18, 3), (20, 15), (8, 19)], g[0]),
                               ([(18, 3), (34, 8), (20, 15)], g[1]), ([(20, 15), (34, 8), (36, 26), (22, 35)], g[3])], hx('1c2024'))
# icônes faites d'objets texturés : redessinées au pixel (agrandies, elles faisaient « upscale »)
DESSINS_ABANDONNES = {'sprites/edit_waystone/modifier_button.png': I.rose_wither,
           'sprites/edit_waystone/visibility/visibility_button_activation.png': I.perle_ender,
           'sprites/edit_waystone/visibility/visibility_button_global.png': I.oeil_ender,
           'sprites/edit_waystone/visibility/visibility_button_shard_only.png': I.eclat,
           'sprites/edit_waystone/visibility/visibility_button_sharestone.png': I.pierre_partage,
           'sprites/groups/community_hubs.png': I.cloche, 'sprites/groups/dimension.png': I.dimension,
           'sprites/groups/dimension/minecraft/overworld.png': I.monde, 'sprites/groups/dimension/minecraft/the_end.png': I.pierre_end,
           'sprites/groups/dimension/minecraft/the_nether.png': I.nether, 'sprites/groups/dungeons.png': I.coffre,
           'sprites/groups/favorites.png': I.etoile, 'sprites/groups/global.png': I.oeil_ender, 'sprites/groups/resource_sites.png': I.pioches,
           'sprites/inventory/inventory_button.png': I.carte,
           'sprites/waystone_selection/dimension/minecraft/the_end.png': I.pierre_end, 'sprites/waystone_selection/dimension/minecraft/the_nether.png': I.nether,
           'sprites/waystone_selection/manage_waystones.png': I.livre_plume, 'sprites/waystone_selection/sort_distance.png': I.boussole,
           'sprites/widgets/edit.png': I.crayon, 'sprites/widgets/edit_button.png': I.crayon,
           'sprites/widgets/alias.png': ic_alias, 'sprites/widgets/alias_button.png': ic_alias,
           'sprites/widgets/hidden.png': lambda: I.oeil(False), 'sprites/widgets/shown.png': I.oeil, 'sprites/widgets/small_button.png': ic_pierre}
DESSINS = {}
# ---------------- les icônes signalées : agrandies en Scale3x puis « redessinées » texel par texel
#   1. palette resserrée : les teintes voisines de l'original fusionnent (fini les mélanges) ;
#   2. texels isolés retirés (fini les taches) ;
#   3. contour net d'un texel.
from collections import Counter
def resserrer(im, seuil=30):
    cs = Counter(c for c in im.getdata() if c[3]); ordre = [c for c, _ in cs.most_common()]; rep = {}
    for c in ordre:
        for r_ in set(rep.values()):
            if sum((c[i] - r_[i]) ** 2 for i in range(3)) < seuil * seuil: rep[c] = r_; break
        else: rep[c] = c
    p = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if p[x, y][3]: p[x, y] = rep[p[x, y]]
    return im
def epurer(im, passes=2):
    for _ in range(passes):
        src = im.copy(); s = src.load(); p = im.load(); w, h = im.size
        for y in range(h):
            for x in range(w):
                c = s[x, y]
                if not c[3]: continue
                voisins = [s[x + a, y + b] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)) if 0 <= x + a < w and 0 <= y + b < h]
                if sum(1 for v in voisins if v == c) <= 1:
                    n4 = [s[x + a, y + b] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + a < w and 0 <= y + b < h and s[x + a, y + b][3]]
                    if n4: p[x, y] = Counter(n4).most_common(1)[0][0]
    return im
def nettoyer16(im, seuil=22):
    """Nettoyage de l'original en 16 px, avant l'agrandissement : teintes presque identiques fusionnées, texels isolés
    de l'intérieur repris par leurs voisins (la silhouette ne bouge pas). L'agrandissement Scale3x n'a plus de bruit à arrondir."""
    im = resserrer(im, seuil); src = im.copy(); s_ = src.load(); p = im.load(); w, h = im.size
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            c = s_[x, y]
            if not c[3]: continue
            n4 = [s_[x + a, y + b] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if any(not v[3] for v in n4): continue                      # bord de la silhouette : on garde
            if sum(1 for v in n4 if v == c) == 0:
                cnt = Counter(n4).most_common(1)[0]
                if cnt[1] >= 2: p[x, y] = cnt[0]
    return im
def icone_nette(rel, sans_fond=False):
    im = Image.open(O + rel).convert('RGBA')
    if sans_fond:
        # fond du bouton retiré sur l'original (même règle que icone())
        p = im.load(); w, h = im.size
        fond = {c for c in FOND_BOUTON if c != (255, 255, 255)}
        for y in range(h):
            for x in range(w):
                if x < 2 or y < 2 or x >= w - 2 or y >= h - 2: p[x, y] = (0, 0, 0, 0)
        pile = [(x, y) for x in range(w) for y in range(h) if x in (2, w - 3) or y in (2, h - 3)]; vu = set()
        while pile:
            x, y = pile.pop()
            if (x, y) in vu or not (0 <= x < w and 0 <= y < h): continue
            vu.add((x, y))
            if p[x, y][3] == 0 or p[x, y][:3] in fond:
                p[x, y] = (0, 0, 0, 0); pile += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    im = im.crop(im.getbbox())
    return contour(hybride(im))
def hybride(im):
    """Agrandissement « propre » : l'intérieur garde les pixels de Minecraft en blocs nets de 3 x 3 (comme les objets dans
    les cases), seule la silhouette est adoucie par Scale3x (les marches des diagonales disparaissent). Aucun mélange de teintes."""
    nn = im.resize((im.width * 3, im.height * 3), Image.NEAREST); sc = scale3x(im)
    out = nn.copy(); o = out.load(); a = sc.load(); n = nn.load()
    for y in range(out.height):
        for x in range(out.width):
            if a[x, y][3] == 0: o[x, y] = (0, 0, 0, 0)          # la silhouette adoucie retire les marches
            elif n[x, y][3] == 0: o[x, y] = a[x, y]             # ... ou les comble avec la couleur voisine
    return out
NETTES = ['sprites/edit_waystone/modifier_button.png', 'sprites/edit_waystone/visibility/visibility_button_sharestone.png',
          'sprites/edit_waystone/visibility/visibility_button_activation.png', 'sprites/edit_waystone/visibility/visibility_button_global.png',
          'sprites/edit_waystone/visibility/visibility_button_shard_only.png', 'sprites/groups/dimension/minecraft/overworld.png',
          'sprites/groups/resource_sites.png', 'sprites/waystone_selection/sort_distance.png', 'sprites/waystone_selection/manage_waystones.png',
          'sprites/widgets/edit.png', 'sprites/widgets/edit_button.png', 'sprites/groups/global.png', 'sprites/widgets/shown.png', 'sprites/groups/favorites.png']
for _r in NETTES: DESSINS[_r] = (lambda r_: (lambda: icone_nette(r_, 'button' in r_)))(_r)
def ajuste(im, w, h):
    # l'icône dessinée tient dans sa toile (marge d'un texel), sans être agrandie
    if im.width > w - 2 or im.height > h - 2:
        s = min((w - 2) / im.width, (h - 2) / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.NEAREST)
    return centre(Image.new('RGBA', (w, h)), im)
REDESSINEES = {'sprites/groups/villages.png': ic_avant_poste, 'sprites/groups/players.png': ic_voyageur,
               'sprites/groups/teams.png': ic_equipes, 'sprites/groups/player_homes.png': ic_foyer}

# ---------------- boutons : cadre du pack, icône d'origine agrandie
def bouton_icone(rel, w, h):
    survol = 'highlighted' in rel
    b = bouton(w, h, 'survol' if survol else '')
    base = rel.replace('_highlighted', '')
    if os.path.basename(rel).startswith('small_button'): return b       # boutons vierges (l'icône est posée par le jeu)
    # la visibilité « équipe » prend la même icône que le groupe des équipes (deux voyageurs) au lieu du cookie
    ic = ic_equipes().resize((42, 42), Image.NEAREST) if 'visibility_team' in base else DESSINS[base]() if base in DESSINS else icone(base, True)[0]
    return centre(b, ajuste(ic, b.width - 12, b.height - 12))

# ---------------- menu des modificateurs : le distributeur HD agrandi de 20 px, cases en croix reliées par des tiges
def menu_modificateurs():
    d = Image.open(DISP).convert('RGBA'); S3 = 3
    im = Image.new('RGBA', (256 * S3, 256 * S3))
    haut = d.crop((0, 0, d.width, 74 * S3)).copy(); p = haut.load()
    # on efface le contenu (cases et tuyaux) : chaque ligne reprend l'ardoise du bord gauche
    for y in range(4 * S3, 74 * S3):
        ref = p[5 * S3, y]
        for x in range(5 * S3, 171 * S3): p[x, y] = ref
    im.paste(haut, (0, 0))
    im.paste(haut.crop((0, 54 * S3, haut.width, 74 * S3)), (0, 74 * S3))           # 20 px de plus, même ardoise
    im.paste(d.crop((0, 74 * S3, d.width, 166 * S3)), (0, 94 * S3))                 # inventaire du joueur, descendu de 20 px
    case = d.crop((61 * S3, 16 * S3, 79 * S3, 34 * S3))                              # une case du distributeur (cadre compris)
    for (x, y) in ((79, 16), (51, 44), (79, 44), (107, 44), (79, 72)): im.paste(case, (x * S3, y * S3))
    # tiges d'airain entre les cases
    for (x0, y0, x1, y1) in ((69, 51, 79, 55), (97, 51, 107, 55), (86, 34, 90, 44), (86, 62, 90, 72)):
        m = masque(im.width, im.height); rect(m, x0 * S3, y0 * S3, x1 * S3, y1 * S3); colle(im, metal(m, OR))
    o = Image.open(O + 'menu/waystone_modifiers.png').convert('RGBA')
    im.alpha_composite(scale3x(o.crop((176, 0, 186, 16))), (176 * S3, 0))
    return im

def lot():
    r = {}
    for rel in [l.strip() for l in open('/tmp/w_orig.txt')]:
        o = Image.open(O + rel); w, h = o.size
        if rel in REDESSINEES: r[rel] = REDESSINEES[rel]()
        elif rel == 'menu/waystone_modifiers.png': r[rel] = menu_modificateurs()
        elif rel.endswith('drag_handle.png') or rel.endswith('drag_handle_highlighted.png'):
            m = masque(w * 3, h * 3)
            for y in (12, 21, 30): rect(m, 6, y, w * 3 - 6, y + 6)
            r[rel] = metal(m, ROUGE if 'highlighted' in rel else OR)
        elif 'button' in os.path.basename(rel) and rel not in ('sprites/inventory/inventory_button.png', 'sprites/widgets/small_button.png'): r[rel] = bouton_icone(rel, w, h)
        elif rel in DESSINS: r[rel] = ajuste(DESSINS[rel](), w * 3, h * 3)
        else:
            ic, bb = icone(rel)
            t = toile(w, h); r[rel] = centre(t, ic) if ic.width <= t.width and ic.height <= t.height else ic.resize(t.size)
    return r
