# Lot 2 : interface d'Ars Nouveau au style réfractaire (pierre pâle argentée, pierre d'écho violet nuit, cristaux),
# au niveau de la barre de mana. Pas d'airain, pas de rivet, pas de mécanique ; survol et choix : les cristaux s'éveillent en cyan.
import math, random
from hd import *
from PIL import ImageOps
ARG = dict(clair=hx('f6f4fc'), base=hx('d6d1e4'), mi=hx('aaa3c0'), sombre=hx('7c7596'), trait=hx('2a2438'))
NUIT = dict(clair=hx('4a3a68'), base=hx('2e2146'), mi=hx('231936'), sombre=hx('1a1228'), trait=hx('0d0816'))
AME = dict(clair=hx('e6d8ff'), base=hx('b48cf0'), mi=hx('8a5ad8'), sombre=hx('5d34a0'), trait=hx('28134c'))
EVEIL = dict(clair=hx('e8fdff'), base=hx('8ef0ff'), mi=hx('3fc8e8'), sombre=hx('1f8ab0'), trait=hx('0a3448'))
VELIN = dict(clair=hx('fbf8ff'), base=hx('efe8f8'), mi=hx('ddd2ec'), sombre=hx('c4b6da'), trait=hx('6a5a88'))

def cristal(im, cx, cy, rx, ry, pal=AME):
    """Losange à facettes (en texels), comme sur la barre de mana."""
    m = masque(im.width, im.height); poly(m, [(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)])
    q = m.load(); p = im.load()
    for y in range(max(0, int(cy - ry) - 1), min(im.height, int(cy + ry) + 2)):
        for x in range(max(0, int(cx - rx) - 1), min(im.width, int(cx + rx) + 2)):
            if q[x, y] > 127:
                haut, gauche = y < cy, x < cx
                p[x, y] = pal['clair'] if haut and gauche else pal['base'] if haut else pal['mi'] if gauche else pal['sombre']
            elif any(0 <= x + dx < im.width and 0 <= y + dy < im.height and q[x + dx, y + dy] > 127 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                p[x, y] = pal['trait']
    p[int(cx - 1), int(cy - ry / 2)] = pal['clair'] if pal is not EVEIL else (255, 255, 255, 255)

def pierre(m, pal, grain=0.0, graine=1):
    """Pierre taillée : même relief que le métal, avec un léger grain (pas de dégradé brillant)."""
    im = metal(m, pal)
    if grain:
        r = random.Random(graine); p = im.load(); q = m.load()
        for y in range(im.height):
            for x in range(im.width):
                if q[x, y] > 127 and r.random() < grain: p[x, y] = mix(p[x, y], pal['sombre'], .35)
    return im

# ---------------- marque-pages (23 x 20) : ruban de pierre pâle à queue d'aronde côté extérieur (gauche), cœur violet nuit
def marque_page(icone, choisi=False, droite=False):
    """droite : marque-page posé sur le bord droit du livre (filtres des glyphes), queue d'aronde à droite."""
    W, H = 69, 60
    ext = masque(W, H); poly(ext, [(0, 1), (W - 1, 1), (W - 1, H - 2), (0, H - 2), (14, H / 2)])
    inn = masque(W, H); poly(inn, [(13, 7), (W - 1, 7), (W - 1, H - 8), (13, H - 8), (24, H / 2)])
    if droite: ext, inn = ImageOps.mirror(ext), ImageOps.mirror(inn)
    im = Image.new('RGBA', (W, H))
    colle(im, pierre(ImageChops.subtract(ext, inn), ARG, .06))
    colle(im, biseau(inn, dict(NUIT, clair=NUIT['clair'] if not choisi else hx('3a5a78')), contour=False))
    # le côté collé au livre (droite) reste ouvert : pas de contour
    bx = 0 if droite else W - 1
    for y in range(H):
        if im.getpixel((bx, y))[3]: im.putpixel((bx, y), ARG['mi'] if 1 < y < H - 2 else ARG['trait'])
    cristal(im, W - 8 if droite else 7, H // 2, 3, 5, EVEIL if choisi else AME)
    if choisi:
        d = ImageDraw.Draw(im)
        for y in range(7, H - 7): pass
        bord = ImageChops.subtract(inn.filter(ImageFilter.MaxFilter(3)), inn)
        bp = bord.load(); ip = im.load()
        for y in range(H):
            for x in range(W):
                if bp[x, y] > 127 and 0 < x < W - 1: ip[x, y] = EVEIL['mi']
    if icone is not None: colle(im, icone, (3 if droite else 26) + (40 - icone.width) // 2, (H - icone.height) // 2)
    return im

# ---------------- icônes des marque-pages (≈ 33 x 33 texels)
def ic_livre_ouvert():
    m = masque(36, 26); poly(m, [(1, 3), (17, 6), (17, 25), (1, 22)]); poly(m, [(34, 3), (18, 6), (18, 25), (34, 22)])
    im = biseau(m, VELIN); d = ImageDraw.Draw(im)
    for y in (10, 14, 18): d.line([(5, y - 1), (13, y + 1)], fill=VELIN['sombre']); d.line([(22, y + 1), (30, y - 1)], fill=VELIN['sombre'])
    return im
def ic_manette():
    m = masque(36, 26); ImageDraw.Draw(m).rounded_rectangle([1, 3, 34, 22], radius=9, fill=255); rect(m, 4, 18, 11, 25); rect(m, 25, 18, 32, 25)
    im = metal(m, ARG); d = ImageDraw.Draw(im)
    for cx in (12, 24): d.ellipse([cx - 3, 9, cx + 3, 15], fill=NUIT['base'])
    return im
def ic_familier():
    m = masque(34, 32); ellipse(m, 5, 9, 29, 31); poly(m, [(6, 14), (4, 0), (14, 10)]); poly(m, [(28, 14), (30, 0), (20, 10)])
    im = metal(m, dict(clair=hx('ffd0f0'), base=hx('f08ac8'), mi=hx('d060a8'), sombre=hx('a03c80'), trait=hx('3c0a2c')))
    d = ImageDraw.Draw(im)
    for cx in (12, 22): d.rectangle([cx, 18, cx + 2, 21], fill=NUIT['trait'])
    return im
def ic_reglages():
    im = Image.new('RGBA', (34, 30))
    for k, y in enumerate((3, 13, 23)):
        m = masque(34, 30); rect(m, 11, y, 32, y + 4); colle(im, metal(m, ARG))
        cristal(im, 5, y + 2, 3, 4, AME)
    return im
def ic_son():
    m = masque(36, 30); rect(m, 2, 10, 9, 20); poly(m, [(8, 10), (17, 2), (17, 28), (8, 20)])
    im = metal(m, ARG)
    for r, c in ((7, AME['base']), (12, AME['mi'])):
        a = masque(36, 30); ImageDraw.Draw(a).arc([20 - r, 15 - r, 20 + r, 15 + r], -50, 50, fill=255, width=3)
        colle(im, biseau(a, dict(AME, base=c)))
    return im
def ic_pinceau():
    m = masque(34, 34); trait(m, [(26, 4), (12, 22)], 4)
    im = metal(m, dict(clair=hx('e8c89a'), base=hx('c49a62'), mi=hx('9a7244'), sombre=hx('6a4a28'), trait=hx('2a1a0a')))
    p = masque(34, 34); poly(p, [(12, 18), (17, 23), (8, 32), (3, 31), (4, 26)]); colle(im, metal(p, AME))
    return im
def ic_roue():
    im = Image.new('RGBA', (34, 34)); cx = cy = 16.5
    p = im.load()
    for y in range(34):
        for x in range(34):
            d = math.hypot(x - cx, y - cy)
            if 8 <= d <= 15:
                a = (math.degrees(math.atan2(y - cy, x - cx)) + 360) % 360
                import colorsys
                r, g, b = colorsys.hsv_to_rgb(a / 360, .65, .95 if d < 13 else .75)
                p[x, y] = (int(r * 255), int(g * 255), int(b * 255), 255)
            elif 7 <= d < 8 or 15 < d <= 16: p[x, y] = NUIT['trait']
    return im
def ic_vieux_livre():
    m = masque(34, 28); rect(m, 1, 2, 31, 26)
    im = metal(m, dict(clair=hx('c08a5a'), base=hx('9a6638'), mi=hx('7a4c28'), sombre=hx('5a361a'), trait=hx('24140a')))
    d = ImageDraw.Draw(im)
    for y in range(5, 24): im.putpixel((31, y), VELIN['base']); im.putpixel((30, y), VELIN['sombre'])
    d.line([(4, 8), (26, 8)], fill=hx('5a361a')); d.line([(4, 20), (26, 20)], fill=hx('5a361a'))
    return im
def ic_cercle():
    im = Image.new('RGBA', (34, 34)); m = masque(34, 34); ImageDraw.Draw(m).ellipse([2, 2, 31, 31], outline=255, width=3)
    colle(im, biseau(m, ARG))
    for k, c in enumerate((hx('f05a7a'), hx('5aa0f0'), hx('f0c85a'), hx('7af08a'))):
        a = math.pi / 4 + k * math.pi / 2; cristal(im, 16.5 + 13 * math.cos(a), 16.5 + 13 * math.sin(a), 3, 3, dict(clair=mix(c, (255, 255, 255, 255), .5), base=c, mi=mix(c, (0, 0, 0, 255), .2), sombre=mix(c, (0, 0, 0, 255), .45), trait=mix(c, (0, 0, 0, 255), .8)))
    cristal(im, 16.5, 16.5, 4, 6, AME)
    return im
def ic_grille():
    m = masque(28, 28)
    for i in range(3):
        for j in range(3): rect(m, 1 + i * 9, 1 + j * 9, 8 + i * 9, 8 + j * 9)
    return metal(m, ARG)
def ic_chiffre(n):
    m = masque(10 * n + 4, 30)
    for k in range(n): rect(m, 2 + k * 10, 4, 8 + k * 10, 26)
    rect(m, 0, 1, 10 * n + 4, 5); rect(m, 0, 25, 10 * n + 4, 29)
    return metal(m, ARG)
ICONES = {'documentation_tab': ic_livre_ouvert, 'discord_tab': ic_manette, 'familiar_tab': ic_familier, 'settings_tab': ic_reglages,
          'sounds_tab': ic_son, 'spell_style_tab': ic_pinceau, 'color_wheel_bookmark': ic_roue, 'worn_book_bookmark': ic_vieux_livre,
          'summon_circle_bookmark': ic_cercle}

# ---------------- onglets de sort (18 x 13) : fanion de pierre pâle, pointe vers l'extérieur
def onglet_sort(choisi):
    W, H = 54, 39
    ext = masque(W, H); poly(ext, [(0, 1), (W - 14, 1), (W - 1, H / 2), (W - 14, H - 2), (0, H - 2)])
    inn = masque(W, H); poly(inn, [(0, 7), (W - 17, 7), (W - 8, H / 2), (W - 17, H - 8), (0, H - 8)])
    im = Image.new('RGBA', (W, H)); colle(im, pierre(ImageChops.subtract(ext, inn), ARG, .05)); colle(im, biseau(inn, NUIT, contour=False))
    cristal(im, W - 20, H // 2, 3, 5, EVEIL if choisi else AME)
    if choisi:
        bord = ImageChops.subtract(inn.filter(ImageFilter.MaxFilter(3)), inn); bp = bord.load(); ip = im.load()
        for y in range(H):
            for x in range(W):
                if bp[x, y] > 127 and x > 0: ip[x, y] = EVEIL['mi']
    return im

# ---------------- case de glyphe (22 x 20) : alvéole creusée dans la pierre pâle, cristaux aux coins
def case_glyphe():
    W, H = 66, 60
    ext = masque(W, H); ImageDraw.Draw(ext).rounded_rectangle([1, 1, W - 2, H - 2], radius=6, fill=255)
    inn = masque(W, H); ImageDraw.Draw(inn).rounded_rectangle([8, 7, W - 9, H - 8], radius=4, fill=255)
    im = pierre(ImageChops.subtract(ext, inn), ARG, .05)
    # alvéole : creux violet nuit, ombre portée en haut/gauche
    cp = biseau(inn, dict(clair=NUIT['sombre'], base=NUIT['base'], mi=NUIT['clair'], sombre=NUIT['clair'], trait=NUIT['trait']), contour=False)
    im.alpha_composite(cp)
    for (x, y) in ((5, 5), (W - 6, 5), (5, H - 6), (W - 6, H - 6)): cristal(im, x, y, 2, 2, AME)
    return im
def glyphe_choisi():
    """Repère du glyphe choisi (18 x 18) : quatre équerres de cristal éveillé."""
    W = 54; im = Image.new('RGBA', (W, W))
    for (sx, sy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        m = masque(W, W); x0 = 1 if not sx else W - 14; y0 = 1 if not sy else W - 14
        rect(m, x0, (y0 if not sy else W - 5), x0 + 13, (y0 if not sy else W - 5) + 4)
        rect(m, (x0 if not sx else W - 5), y0, (x0 if not sx else W - 5) + 4, y0 + 13)
        colle(im, metal(m, EVEIL))
    return im

# ---------------- bandes de vélin (15 px de haut) : bouts frangés, deux filets gravés, un cristal épinglé à chaque bout
def velin(w, icone=None, graine=3):
    W, H = w * S, 45; r = random.Random(graine + w)
    m = masque(W, H)
    gauche = [6 + r.randint(-2, 2) for _ in range(H)]; droite = [W - 7 + r.randint(-2, 2) for _ in range(H)]
    for y in range(4, H - 4):
        for x in range(gauche[y // 3 * 3], droite[y // 3 * 3]): m.putpixel((x, y), 255)
    im = biseau(m, VELIN)
    p = im.load(); q = m.load()
    for y in range(H):
        for x in range(W):
            if q[x, y] > 127 and r.random() < .08: p[x, y] = mix(p[x, y], VELIN['sombre'], .5)
    d = ImageDraw.Draw(im)
    d.line([(14, 9), (W - 15, 9)], fill=VELIN['sombre']); d.line([(14, H - 10), (W - 15, H - 10)], fill=VELIN['sombre'])
    cristal(im, 10, H // 2, 3, 5, AME); cristal(im, W - 11, H // 2, 3, 5, AME)
    if icone is not None: colle(im, icone, 17, (H - icone.height) // 2)
    return im
def ic_coche():
    from sprites import m_coche
    return metal(m_coche(18, 16, 4), dict(clair=hx('c8f0d0'), base=hx('7ac890'), mi=hx('4a9a64'), sombre=hx('336e46'), trait=hx('15301a')))
def ic_loupe():
    m = masque(18, 18); ellipse(m, 5, 0, 18, 13); t = masque(18, 18); ellipse(t, 8, 3, 15, 10)
    ImageDraw.Draw(m).line([(1, 16), (7, 10)], fill=255, width=3)
    return metal(ImageChops.subtract(m, t), ARG)
def ic_plume():
    m = masque(18, 20); poly(m, [(16, 0), (6, 10), (3, 19), (9, 12), (17, 4)])
    return metal(m, AME)
PAPIERS = {'clear_paper': (47, None), 'clear_bar': (47, None), 'create_paper': (56, None), 'save_bar': (56, ic_coche),
           'search_paper': (72, ic_loupe), 'spell_name_paper': (109, ic_plume), 'doc_search_bar': (110, ic_loupe)}

def lot():
    r = {}
    for n, f in ICONES.items(): r[n] = marque_page(f())
    r['filter_tab_all'] = marque_page(ic_grille(), droite=True); r['filter_tab_all_selected'] = marque_page(ic_grille(), True, True)
    for k in (1, 2, 3):
        r[f'filter_tab_tier{k}'] = marque_page(ic_chiffre(k), droite=True); r[f'filter_tab_tier{k}_selected'] = marque_page(ic_chiffre(k), True, True)
    r['spell_tab'] = onglet_sort(False); r['spell_tab_selected'] = onglet_sort(True)
    r['spell_glyph_slot'] = case_glyphe(); r['glyph_selected'] = glyphe_choisi()
    for n, (w, ic) in PAPIERS.items(): r[n] = velin(w, ic() if ic else None)
    return r

# ---------------- icônes reprises des originales d'Ars (lisibles du premier coup d'œil), agrandies en Scale3x
ORIG = '/tmp/arsm/src/main/resources/assets/ars_nouveau/textures/gui/'
# couleurs du ruban d'origine : tout ce qui, dans les marque-pages, n'est pas l'icône
FOND_ARS = set()
for _f in ('filter_tab_all', 'filter_tab_tier1', 'spell_tab', 'documentation_tab', 'discord_tab'):
    _im = Image.open(ORIG + _f + '.png').convert('RGBA')
    for _c in _im.getdata():
        if _c[3] and (_c[0] < 150 and _c[2] < 170): FOND_ARS.add(_c[:3])
def scale3x(im):
    """AdvMAME3x : agrandit un dessin au pixel par 3 en adoucissant les diagonales sans flou."""
    w, h = im.size; p = im.load(); out = Image.new('RGBA', (w * 3, h * 3)); o = out.load()
    def g(x, y): return p[min(w - 1, max(0, x)), min(h - 1, max(0, y))]
    for y in range(h):
        for x in range(w):
            A, B, C = g(x - 1, y - 1), g(x, y - 1), g(x + 1, y - 1)
            D, E, F = g(x - 1, y), g(x, y), g(x + 1, y)
            G, H, I = g(x - 1, y + 1), g(x, y + 1), g(x + 1, y + 1)
            e = [E] * 9
            if B != H and D != F:
                e[0] = D if D == B else E
                e[1] = B if (D == B and E != C) or (B == F and E != A) else E
                e[2] = F if B == F else E
                e[3] = D if (D == B and E != G) or (D == H and E != A) else E
                e[5] = F if (B == F and E != I) or (H == F and E != C) else E
                e[6] = D if D == H else E
                e[7] = H if (D == H and E != I) or (H == F and E != G) else E
                e[8] = F if H == F else E
            for k in range(9): o[x * 3 + k % 3, y * 3 + k // 3] = e[k]
    return out
def icone_originale(nom):
    im = Image.open(ORIG + nom + '.png').convert('RGBA'); p = im.load()
    ic = Image.new('RGBA', im.size)
    for y in range(2, im.height - 2):
        for x in range(4, im.width - 1):
            c = p[x, y]
            if c[3] and c[:3] not in FOND_ARS: ic.putpixel((x, y), c)
    bb = ic.getbbox(); ic = ic.crop(bb)
    big = scale3x(ic)
    # contour sombre d'un texel, comme les autres icônes du pack
    a = big.split()[3]; contour = a.filter(ImageFilter.MaxFilter(3))
    out = Image.new('RGBA', (big.width + 2, big.height + 2))
    tr = Image.new('RGBA', out.size, NUIT['trait']); m = Image.new('L', out.size); m.paste(contour, (1, 1))
    out.paste(tr, (0, 0), m); out.alpha_composite(big, (1, 1))
    return out
for _n in ('documentation_tab', 'discord_tab', 'familiar_tab', 'spell_style_tab', 'worn_book_bookmark'):
    ICONES[_n] = (lambda n: (lambda: icone_originale(n)))(_n)

# ---------------- le reste d'Ars : dessin d'origine agrandi en Scale3x, encres beiges passées en encres violettes
import colorsys, glob, os
RAMPE = [(0, (20, 12, 32)), (90, (58, 42, 88)), (160, (106, 90, 144)), (205, (150, 136, 190)), (225, (215, 206, 236)), (245, (245, 240, 252)), (256, (252, 250, 255))]
def encre(c):
    """Beige, brun et gris (les encres d'Ars) -> même luminosité en violet de l'Écho ; les couleurs franches sont gardées."""
    r, g, b, a = c
    if not a: return c
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    neutre = s < .22 or (s < .55 and .05 < h < .17 and v > .45)
    if not neutre: return c
    L = .3 * r + .59 * g + .11 * b
    for (l0, c0), (l1, c1) in zip(RAMPE, RAMPE[1:]):
        if l0 <= L < l1:
            t = (L - l0) / (l1 - l0); return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)) + (a,)
    return c
def generique(rel):
    im = Image.open(ORIG + rel).convert('RGBA')
    im = Image.eval(im, lambda v: v) if False else im
    p = im.load()
    for y in range(im.height):
        for x in range(im.width): p[x, y] = encre(p[x, y])
    return scale3x(im)
def bille():
    """Bille de défilement (12 x 12) : perle d'améthyste."""
    m = masque(36, 36); ellipse(m, 2, 2, 34, 34); im = metal(m, AME)
    im.putpixel((11, 9), (255, 255, 255, 255)); im.putpixel((12, 9), AME['clair']); im.putpixel((11, 10), AME['clair'])
    return im
def curseur_son():
    """Bouton du curseur de son (8 x 20) : pièce de pierre pâle avec un cristal."""
    m = masque(24, 60); ImageDraw.Draw(m).rounded_rectangle([1, 1, 22, 58], radius=4, fill=255)
    im = pierre(m, ARG, .05); cristal(im, 12, 30, 4, 8, AME); return im
def onglet_rangement(w, choisi):
    """Onglets du terminal de rangement (pierre pâle, cœur violet nuit), comme les onglets de sort."""
    W, H = w * S, 39
    ext = masque(W, H); poly(ext, [(0, 1), (W - 10, 1), (W - 1, 10), (W - 1, H - 11), (W - 10, H - 2), (0, H - 2)])
    inn = masque(W, H); poly(inn, [(0, 7), (W - 12, 7), (W - 7, 12), (W - 7, H - 13), (W - 12, H - 8), (0, H - 8)])
    im = Image.new('RGBA', (W, H)); colle(im, pierre(ImageChops.subtract(ext, inn), ARG, .05)); colle(im, biseau(inn, NUIT, contour=False))
    if choisi:
        bord = ImageChops.subtract(inn.filter(ImageFilter.MaxFilter(3)), inn); bp = bord.load(); ip = im.load()
        for y in range(H):
            for x in range(1, W):
                if bp[x, y] > 127: ip[x, y] = EVEIL['mi']
    return im
def terminal_agrandi():
    """Le terminal sans la zone d'artisanat : 4 rangées de cases de plus, reprises de la 3e rangée du terminal HD."""
    t = Image.open(HD + 'crafting_terminal.png').convert('RGBA')
    bande = t.crop((0, 57 * S, t.width, 75 * S))
    for k in range(4): t.paste(bande, (0, (75 + 18 * k) * S))
    return t
HD = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/ars_nouveau/textures/gui/'
GARDER = {'manabar_gui_border.png', 'manabar_gui_grayscale.png', 'manabar_gui_mana.png', 'spell_book_template.png', 'crafting_terminal.png'}
def lot_complet():
    r = {k + '.png': v for k, v in lot().items()}
    r['scroll_ball.png'] = bille(); r['sound_bar_knob.png'] = curseur_son()
    r['storage_tab1.png'] = onglet_rangement(22, False); r['storage_tab2.png'] = onglet_rangement(18, False); r['storage_tab2_selected.png'] = onglet_rangement(18, True)
    r['crafting_terminal_expanded.png'] = terminal_agrandi()
    for f in sorted(glob.glob(ORIG + '**/*.png', recursive=True)):
        rel = f[len(ORIG):]
        if rel in r or rel in GARDER or rel.startswith(('entries/', 'advancements/', 'hanging_signs/')): continue
        r[rel] = generique(rel)
    return r
