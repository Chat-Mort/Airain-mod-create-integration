# Les sprites d'interface du lot 1 (éléments encore en 1x), redessinés en 3x au style du pack HD.
import math
from hd import *

# ------------------------------------------------------------------ icônes de base (masques en texels)
def m_fleche(w, h, sens='droite', marge=0):
    m = masque(w, h); x0, y0, x1, y1 = marge, marge, w - marge, h - marge
    if sens == 'droite': poly(m, [(x0, y0), (x1 - 1, (y0 + y1 - 1) / 2), (x0, y1 - 1)])
    elif sens == 'gauche': poly(m, [(x1 - 1, y0), (x0, (y0 + y1 - 1) / 2), (x1 - 1, y1 - 1)])
    elif sens == 'haut': poly(m, [(x0, y1 - 1), ((x0 + x1 - 1) / 2, y0), (x1 - 1, y1 - 1)])
    else: poly(m, [(x0, y0), ((x0 + x1 - 1) / 2, y1 - 1), (x1 - 1, y0)])
    return m
def m_croix(w, ep):
    m = masque(w, w); trait(m, [(ep / 2, ep / 2), (w - 1 - ep / 2, w - 1 - ep / 2)], ep); trait(m, [(w - 1 - ep / 2, ep / 2), (ep / 2, w - 1 - ep / 2)], ep); return m
def m_coche(w, h, ep):
    m = masque(w, h); trait(m, [(ep / 2 + 1, h * .55), (w * .38, h - 1 - ep / 2), (w - 1 - ep / 2, ep / 2 + 1)], ep); return m
def m_cadenas(w, h, ouvert):
    m = masque(w, h)
    rect(m, 1, h * 45 // 100, w - 1, h - 1)                      # corps
    a = masque(w, h); bw = max(3, w // 6)
    x0, x1 = w * 22 // 100, w - w * 22 // 100
    ImageDraw.Draw(a).arc([x0, 1, x1 - 1, h * 70 // 100], 180, 360, fill=255, width=bw)
    rect(a, x0, h * 35 // 100 - 1, x0 + bw, h * 45 // 100)
    if not ouvert: rect(a, x1 - bw, h * 35 // 100 - 1, x1, h * 45 // 100)
    else: a = ImageChops.offset(a, 0, -h // 8); rect(a, x0, h * 26 // 100, x0 + bw, h * 45 // 100)
    return ImageChops.lighter(m, a)

def icone(m, pal, taille, ep=1):
    """Icône biseautée centrée sur une toile de taille px d'interface."""
    t = toile(*taille); return centre(t, biseau(m, pal, epais=ep))

# ------------------------------------------------------------------ boutons à cadre (verrou, croix, sociaux)
def bouton(w, h, etat):
    cadre = {'': OR, 'survol': ROUGE, 'off': GRIS}[etat]
    fond = ARD['survol'] if etat == 'survol' else ARD['noir'] if etat == 'off' else ARD['fond']
    return plaque(w, h, cadre, fond, ep=3, coin=2)
def verrou(etat, ouvert):
    b = bouton(20, 20, etat)
    pal = {'': OR, 'survol': ROUGE, 'off': GRIS}[etat]
    w, h = 30, 34
    anse = m_cadenas(w, h, ouvert); corps = masque(w, h); rect(corps, 1, h * 45 // 100, w - 1, h - 1)
    anse = ImageChops.subtract(anse, corps)
    c = Image.new('RGBA', (w + 2, h + 2)); colle(c, metal(anse, pal), 1, 1); colle(c, metal(corps, pal), 1, 1)
    # trou de serrure, et deux rivets
    cx, cy = w // 2 + 1, h * 45 // 100 + 1 + (h - h * 45 // 100) // 2 - 2
    k = masque(w + 2, h + 2); ellipse(k, cx - 3, cy - 3, cx + 3, cy + 3); rect(k, cx - 1, cy, cx + 2, cy + 7)
    kp = k.load()
    for y in range(h + 2):
        for x in range(w + 2):
            if kp[x, y]: c.putpixel((x, y), ARD['abime'] if kp[x, y - 1] else pal['trait'])
    for x in (4, w - 4): rivet(c, x, h * 45 // 100 + 4, pal)
    return centre(b, c)
def croix_bouton(etat):
    b = bouton(14, 14, etat)
    return centre(b, metal(m_croix(20, 5), {'': OR, 'survol': ROUGE, 'off': GRIS}[etat]))

# ------------------------------------------------------------------ pastilles de notification : sceau de cire rouge, chiffre d'or
def pastille(t):
    im = toile(8, 8); m = masque(24, 24); ellipse(m, 1, 1, 23, 23)
    colle(im, biseau(m, ROUGE, epais=2))
    if t == 'more':
        for x in (6, 11, 16): colle(im, biseau(_rond(4), OR), x, 10)
    else: colle(im, biseau(texte_masque(t, 17), OR), 0, 0) if False else centre_txt(im, t)
    return im
def _rond(d): m = masque(d, d); ellipse(m, 0, 0, d, d); return m
def centre_txt(im, t, pal=OR, taille=17, dy=0):
    g = biseau(texte_masque(t, taille), pal); colle(im, g, (im.width - g.width) // 2, (im.height - g.height) // 2 + dy); return im

# ------------------------------------------------------------------ liste des serveurs : barres de signal
def ping(n, mode='ok'):
    """10 x 8 px : cinq barres en escalier ; allumées en or (ou cyan qui balaie pendant la mesure)."""
    im = toile(10, 8)
    for i in range(5):
        hb = 6 + i * 4; x = 1 + i * 6
        m = masque(4, hb); rect(m, 0, 0, 4, hb)
        allume = i < n
        pal = (OR if mode == 'ok' else CYAN) if allume else dict(clair=ARD['clair'], base=ARD['base'], mi=ARD['creux'], sombre=ARD['noir'], trait=ARD['abime'])
        colle(im, biseau(m, pal), x, 23 - hb)
    return im
def hors_ligne():
    im = toile(10, 8); return centre(im, biseau(m_croix(16, 4), ROUGE_VIF))

# ------------------------------------------------------------------ flèches de liste (rejoindre, monter, descendre)
def fleche_liste(sens, survol, taille=(32, 32)):
    pal = ROUGE if survol else OR
    if sens in ('haut', 'bas'):
        m = m_fleche(22, 13, sens)
        im = toile(*taille); colle(im, metal(m, pal, facettes=lambda x, y: 1 if x < 11 else -1), 37, 8 if sens == 'haut' else 75)
        return im
    m = m_fleche(30, 44, sens)
    im = toile(*taille); colle(im, metal(m, pal, facettes=lambda x, y: 1 if y < 22 else -1), 33 if sens == 'droite' else 30, 26)
    return im

# ------------------------------------------------------------------ cadres des progrès : tâche (carré), but (arrondi), défi (engrenage)
def cadre_progres(genre, obtenu):
    pal = OR if obtenu else GRIS
    W = 78; m = masque(W, W)
    if genre == 'task': rect(m, 6, 6, W - 6, W - 6)
    elif genre == 'goal': ImageDraw.Draw(m).rounded_rectangle([4, 4, W - 5, W - 5], radius=22, fill=255)
    else:
        # défi : une roue dentée de 12 dents
        c = W / 2; pts = []
        for k in range(48):
            a = 2 * math.pi * k / 48; r = 37 if (k % 4) in (0, 1) else 30
            pts.append((c + r * math.cos(a), c + r * math.sin(a)))
        poly(m, pts)
    inner = masque(W, W); ImageDraw.Draw(inner).rounded_rectangle([14, 14, W - 15, W - 15], radius=6 if genre != 'goal' else 14, fill=255)
    if genre == 'challenge': inner = masque(W, W); ellipse(inner, 17, 17, W - 17, W - 17)
    im = metal(ImageChops.subtract(m, inner), pal)
    f = Image.new('RGBA', (W, W)); fd = biseau(inner, dict(clair=ARD['base'], base=ARD['fond'], mi=ARD['creux'], sombre=ARD['noir'], trait=ARD['abime']), contour=False)
    f.alpha_composite(fd); f.alpha_composite(im)
    if genre == 'task':
        for (x, y) in ((8, 8), (W - 11, 8), (8, W - 11), (W - 11, W - 11)): rivet(f, x, y, pal)
    if genre == 'challenge':
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2; rivet(f, int(W / 2 + 23 * math.cos(a)) - 1, int(W / 2 + 23 * math.sin(a)) - 1, pal)
    return f

# ------------------------------------------------------------------ toasts (160 x 32) : plaque rivetée
def toast(pal=OR):
    t = plaque(160, 32, pal, ARD['fond'], ep=4, coin=3)
    # filet gravé à 3 texels du cadre, et rivets aux coins
    W, H = t.size; d = ImageDraw.Draw(t)
    d.rectangle([9, 9, W - 10, H - 10], outline=ARD['creux']); d.rectangle([10, 10, W - 9, H - 9], outline=None)
    for x in range(10, W - 9): t.putpixel((x, H - 9), ARD['base'])
    for y in range(10, H - 9): t.putpixel((W - 9, y), ARD['base'])
    for (x, y) in ((2, 2), (W - 5, 2), (2, H - 5), (W - 5, H - 5)): rivet(t, x, y, pal)
    return t

# ------------------------------------------------------------------ viseur et indicateur d'attaque (rendus en inversion : blanc seul)
def viseur():
    im = toile(15, 15); m = masque(45, 45)
    rect(m, 21, 4, 24, 17); rect(m, 21, 28, 24, 41); rect(m, 4, 21, 17, 24); rect(m, 28, 21, 41, 24); rect(m, 21, 21, 24, 24)
    p = im.load(); q = m.load()
    for y in range(45):
        for x in range(45):
            if q[x, y]: p[x, y] = (255, 255, 255, 255)
    return im

# ====================================================================== lot 1 complet
PAL_ETAT = {'': OR, 'survol': ROUGE, 'off': GRIS}
def etat_de(nom):
    return 'survol' if 'highlight' in nom else 'off' if 'disabled' in nom else ''

def fleche_seule(w, h, sens, pal, taille, pos=None):
    m = m_fleche(w, h, sens)
    fac = (lambda x, y: 1 if y < h / 2 else -1) if sens in ('droite', 'gauche') else (lambda x, y: 1 if x < w / 2 else -1)
    im = toile(*taille); g = metal(m, pal, facettes=fac)
    return colle(im, g, *(pos if pos else ((im.width - g.width) // 2, (im.height - g.height) // 2)))

def point_excl(pal, taille, haut=20):
    """Point d'exclamation en métal."""
    l = max(6, haut // 3)
    m = masque(l + 2, haut + l + 2); poly(m, [(0, 0), (l + 1, 0), (l * .75 + 1, haut - 2), (l * .25 + 1, haut - 2)]); ellipse(m, 1, haut + 1, l + 1, haut + l + 1)
    im = toile(*taille); return centre(im, metal(m, pal))

def plaque_simple(w, h, pal=OR, fond=None, ep=3):
    return plaque(w, h, pal, fond or ARD['fond'], ep=ep, coin=2)

# ---------------- progrès
def onglet(w, h, ouvert, choisi):
    """Onglet de classeur : cadre d'airain sur trois côtés ; le côté ouvert touche la fenêtre (fermé si non choisi)."""
    W, H = w * S, h * S
    pal = OR
    ext = masque(W, H); ImageDraw.Draw(ext).rounded_rectangle([1, 1, W - 2, H - 2], radius=5, fill=255)
    inn = masque(W, H); ImageDraw.Draw(inn).rounded_rectangle([5, 5, W - 6, H - 6], radius=3, fill=255)
    # côté ouvert : on prolonge jusqu'au bord, sans cadre si l'onglet est choisi
    if ouvert == 'bas': rect(ext, 1, H // 2, W - 1, H); rect(inn, 5, H // 2, W - 5, H if choisi else H - 5)
    if ouvert == 'haut': rect(ext, 1, 0, W - 1, H // 2); rect(inn, 5, 0 if choisi else 5, W - 5, H // 2)
    if ouvert == 'droite': rect(ext, W // 2, 1, W, H - 1); rect(inn, W // 2, 5, W if choisi else W - 5, H - 5)
    if ouvert == 'gauche': rect(ext, 0, 1, W // 2, H - 1); rect(inn, 0 if choisi else 5, 5, W // 2, H - 5)
    im = Image.new('RGBA', (W, H))
    fond = ARD['fond'] if choisi else ARD['creux']
    fp = im.load(); ip = inn.load()
    for y in range(H):
        for x in range(W):
            if ip[x, y]: fp[x, y] = fond
    colle(im, metal(ImageChops.subtract(ext, inn), pal))
    return im

def progres():
    r = {}
    r['box_obtained'] = plaque_simple(200, 26, OR); r['box_unobtained'] = plaque_simple(200, 26, GRIS, ARD['creux'])
    r['title_box'] = plaque(200, 26, OR, ARD['puits'], ep=3, coin=2)
    for g in ('task', 'goal', 'challenge'):
        for o in (True, False): r[f'{g}_frame_{"obtained" if o else "unobtained"}'] = cadre_progres(g, o)
    for pos, ouv, (w, h) in (('above', 'bas', (28, 32)), ('below', 'haut', (28, 32)), ('left', 'droite', (32, 28)), ('right', 'gauche', (32, 28))):
        for cote in (('left', 'middle', 'right') if pos in ('above', 'below') else ('top', 'middle', 'bottom')):
            for ch in (False, True): r[f'tab_{pos}_{cote}' + ('_selected' if ch else '')] = onglet(w, h, ouv, ch)
    return {'advancements/' + k: v for k, v in r.items()}

# ---------------- livre de recettes
def m_livre(w, h):
    m = masque(w, h); rect(m, 2, 1, w - 1, h - 2); return m
def icone_livre(pal, taille):
    w, h = 30, 26; c = Image.new('RGBA', (w + 2, h + 2))
    colle(c, metal(m_livre(w, h), dict(clair=hx('c0403a'), base=hx('9c2622'), mi=hx('7c1a18'), sombre=hx('5c1210'), trait=hx('2c0808'))), 1, 1)
    # tranche des pages et fermoir d'airain
    for y in range(4, h - 2): c.putpixel((w - 1, y), hx('f0e6cc')); c.putpixel((w - 2, y), hx('d8ccae'))
    m = masque(w + 2, h + 2); rect(m, 4, h // 2 - 2, 12, h // 2 + 4); colle(c, metal(m, pal))
    im = toile(*taille); return centre(im, c)
def grille(pal, taille, n=3, case=6):
    m = masque(n * case + 2, n * case + 2)
    for i in range(n):
        for j in range(n): rect(m, 1 + i * case, 1 + j * case, i * case + case, j * case + case)
    im = toile(*taille); return centre(im, metal(m, pal))
def bouche_four(pal, taille):
    w = 24; m = masque(w, w); rect(m, 0, 0, w, w); trou = masque(w, w); ImageDraw.Draw(trou).rounded_rectangle([5, 9, w - 6, w - 4], radius=3, fill=255)
    c = metal(ImageChops.subtract(m, trou), pal)
    f = masque(w, w); poly(f, [(8, w - 5), (12, 11), (16, w - 5)])
    colle(c, biseau(f, ROUGE_VIF, contour=False))
    im = toile(*taille); return centre(im, c)
def livre_recettes():
    r = {}
    for e in ('', '_highlighted'):
        st = etat_de(e)
        r['button' + e] = colle(plaque(20, 18, PAL_ETAT[st], ARD['survol'] if st else ARD['fond'], ep=3, coin=2), icone_livre(OR, (20, 18)))
        for nom, ic in (('crafting', grille), ('furnace', bouche_four)):
            for d in ('', '_disabled'):
                st2 = 'survol' if e else ('off' if d else '')
                b = plaque(24, 24, PAL_ETAT[st2], ARD['survol'] if e else ARD['fond'], ep=3, coin=2)
                r[f'{nom}_overlay{d}{e}'] = colle(b, ic(GRIS if d and not e else PAL_ETAT[st2], (24, 24)))
        for nom in ('filter', 'furnace_filter'):
            for d in ('_enabled', '_disabled'):
                st2 = 'survol' if e else ''
                b = plaque(26, 16, PAL_ETAT[st2], ARD['survol'] if e else ARD['fond'], ep=3, coin=2)
                sym = metal(m_coche(18, 16, 4), VERT) if d == '_enabled' else metal(m_croix(14, 4), ROUGE_VIF)
                colle(b, sym, 12, (48 - sym.height) // 2)
                ic = (grille(OR, (12, 16), 3, 4) if nom == 'filter' else bouche_four(OR, (12, 16)))
                colle(b, ic, 36, 0)
                r[nom + d + e] = b
        r['page_backward' + e] = fleche_seule(24, 36, 'gauche', PAL_ETAT[etat_de(e)], (12, 17))
        r['page_forward' + e] = fleche_seule(24, 36, 'droite', PAL_ETAT[etat_de(e)], (12, 17))
    r['overlay_recipe'] = plaque(32, 32, OR, ARD['puits'], ep=3, coin=2)
    for n, pal in (('slot_craftable', OR), ('slot_uncraftable', ROUGE)):
        r[n] = plaque(25, 25, pal, ARD['fond'], ep=3, coin=2)
    for n, pal in (('slot_many_craftable', OR), ('slot_many_uncraftable', ROUGE)):
        b = toile(25, 25); colle(b, plaque(23, 23, pal, ARD['creux'], ep=3, coin=2), 6, 0); colle(b, plaque(23, 23, pal, ARD['fond'], ep=3, coin=2), 0, 6); r[n] = b
    r['tab'] = onglet(35, 27, 'droite', False); r['tab_selected'] = onglet(35, 27, 'droite', True)
    return {'recipe_book/' + k: v for k, v in r.items()}
def fond_livre_recettes():
    im = Image.new('RGBA', (256 * S, 256 * S))
    p = plaque(147, 166, OR, ARD['fond'], ep=4, coin=3)
    for (x, y) in ((3, 3), (p.width - 6, 3), (3, p.height - 6), (p.width - 6, p.height - 6)): rivet(p, x, y, OR)
    colle(im, p, 3, 3)
    # loupe de la recherche (en haut à gauche, comme l'ancienne)
    m = masque(18, 18); ellipse(m, 5, 0, 18, 13); trou = masque(18, 18); ellipse(trou, 8, 3, 15, 10)
    ImageDraw.Draw(m).line([(1, 16), (7, 10)], fill=255, width=3)
    loupe = metal(ImageChops.subtract(m, trou), OR); tp = trou.load()
    for y in range(18):
        for x in range(18):
            if tp[x, y]: loupe.putpixel((x, y), CYAN['mi'] if y < 7 else CYAN['sombre'])
    colle(im, loupe, 33, 36)
    return {'../recipe_book': im}

# ---------------- listes (serveurs, mondes, paquets)
def listes():
    r = {}
    for e in ('', '_highlighted'):
        pal = PAL_ETAT[etat_de(e)]
        for base in ('server_list', 'world_list', 'transferable_list'):
            pass
        r['server_list/join' + e] = fleche_liste('droite', bool(e))
        r['server_list/move_up' + e] = fleche_liste('haut', bool(e)); r['server_list/move_down' + e] = fleche_liste('bas', bool(e))
        r['transferable_list/move_up' + e] = fleche_liste('haut', bool(e)); r['transferable_list/move_down' + e] = fleche_liste('bas', bool(e))
        r['transferable_list/select' + e] = fleche_liste('droite', bool(e)); r['transferable_list/unselect' + e] = fleche_liste('gauche', bool(e))
        r['world_list/join' + e] = fleche_liste('droite', bool(e))
        mj = fleche_liste('droite', bool(e)); colle(mj, point_excl(OR if not e else ROUGE_VIF, (8, 12), 14), 0, 30); r['world_list/marked_join' + e] = mj
        r['world_list/warning' + e] = point_excl(OR if not e else dict(OR, base=OR['clair']), (32, 32), 34)
        r['world_list/error' + e] = point_excl(ROUGE_VIF if not e else dict(ROUGE_VIF, base=ROUGE_VIF['clair']), (32, 32), 34)
    for n in range(1, 6): r[f'server_list/ping_{n}'] = ping(n); r[f'server_list/pinging_{n}'] = ping(n, 'mesure')
    r['server_list/unreachable'] = hors_ligne(); r['server_list/incompatible'] = hors_ligne()
    return r

# ---------------- widgets, invitations, notifications
def widgets():
    r = {}
    for e in ('', '_highlighted', '_disabled'):
        st = etat_de(e)
        r['widget/locked_button' + e] = verrou(st, False); r['widget/unlocked_button' + e] = verrou(st, True)
    r['widget/cross_button'] = croix_bouton(''); r['widget/cross_button_highlighted'] = croix_bouton('survol')
    sf = toile(80, 80); W = sf.width; m = masque(W, W); rect(m, 0, 0, W, W); rect(m, 9, 9, W - 9, W - 9, 0); colle(sf, metal(m, OR)); r['widget/slot_frame'] = sf
    for e in ('', '_highlighted'):
        b = plaque(18, 18, ROUGE if e else OR, ARD['survol'] if e else ARD['fond'], ep=3, coin=2)
        r['pending_invite/accept' + e] = centre(b.copy(), metal(m_coche(30, 26, 6), VERT))
        r['pending_invite/reject' + e] = centre(b.copy(), metal(m_croix(22, 6), ROUGE_VIF))
    for t in ('1', '2', '3', '4', '5', 'more'): r['notification/' + t] = pastille(t)
    return r

# ---------------- social, popup
def m_bulle(w, h):
    m = masque(w, h); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h * 72 // 100], radius=6, fill=255); poly(m, [(w * .25, h * .6), (w * .25, h - 1), (w * .5, h * .7)]); return m
def social():
    r = {}
    r['social_interactions/background'] = plaque(236, 34, OR, ARD['fond'], ep=3, coin=2)
    r['popup/background'] = plaque(236, 34, OR, ARD['puits'], ep=3, coin=2)
    for e in ('', '_highlighted', '_disabled'):
        st = etat_de(e); pal = PAL_ETAT[st]
        b = lambda: plaque(20, 20, pal, ARD['survol'] if st == 'survol' else ARD['noir'] if st == 'off' else ARD['fond'], ep=3, coin=2)
        bulle = metal(m_bulle(34, 30), BLANC if st != 'off' else GRIS)
        if e != '_disabled':
            r['social_interactions/mute_button' + e] = centre(b(), bulle)
            u = bulle.copy(); colle(u, metal(m_croix(18, 4), ROUGE_VIF), 16, 12)
            r['social_interactions/unmute_button' + e] = centre(b(), u)
        tri = masque(32, 28); poly(tri, [(16, 0), (31, 27), (0, 27)]); g = metal(tri, OR if st != 'off' else GRIS)
        ex = masque(32, 28); rect(ex, 14, 8, 18, 19); rect(ex, 14, 21, 18, 25)
        ep_ = ex.load()
        for y in range(28):
            for x in range(32):
                if ep_[x, y]: g.putpixel((x, y), ARD['abime'])
        r['social_interactions/report_button' + e] = centre(b(), g)
    return r

# ---------------- toasts et leurs icônes de tutoriel
def m_souris(w, h):
    m = masque(w, h); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=w // 2 - 1, fill=255); return m
def icone_souris(droit=False):
    w, h = 26, 36; m = m_souris(w, h); g = metal(m, BLANC)
    d = ImageDraw.Draw(g); d.line([(w // 2, 1), (w // 2, h * 40 // 100)], fill=BLANC['trait']); d.line([(1, h * 40 // 100), (w - 2, h * 40 // 100)], fill=BLANC['trait'])
    if droit:
        bm = masque(w, h); ImageDraw.Draw(bm).rounded_rectangle([w // 2 + 1, 1, w - 2, h * 40 // 100 - 1], radius=6, fill=255)
        bm = ImageChops.multiply(bm, m); colle(g, biseau(bm, ROUGE_VIF, contour=False))
    return centre(toile(20, 20), g)
def icone_touches():
    im = toile(20, 20)
    for (x, y, t) in ((21, 3, 'W'), (3, 29, 'A'), (21, 29, 'S'), (39, 29, 'D')):
        k = plaque(6, 9, GRIS, ARD['base'], ep=2, coin=1).resize((18, 27), Image.NEAREST) if False else None
        m = masque(18, 26); ImageDraw.Draw(m).rounded_rectangle([0, 0, 17, 25], radius=3, fill=255)
        c = metal(m, BLANC); g = texte_masque(t, 13); gp = g.load()
        for yy in range(g.height):
            for xx in range(g.width):
                if gp[xx, yy]: c.putpixel((xx + (18 - g.width) // 2, yy + 4), BLANC['trait'])
        colle(im, c, x, y)
    return im
def icone_arbre():
    im = toile(20, 20)
    tr = masque(60, 60); rect(tr, 26, 34, 34, 58); colle(im, metal(tr, dict(clair=hx('a87848'), base=hx('8a5e36'), mi=hx('6a4426'), sombre=hx('4c2e18'), trait=hx('24140a'))))
    fe = masque(60, 60); ellipse(fe, 8, 2, 52, 42)
    colle(im, metal(fe, dict(clair=hx('8ed07a'), base=hx('5ea84a'), mi=hx('468836'), sombre=hx('326626'), trait=hx('15301a'))))
    return im
def icone_planches():
    im = toile(20, 20); m = masque(48, 48); rect(m, 0, 0, 48, 48); g = metal(m, dict(clair=hx('d8b078'), base=hx('b88c56'), mi=hx('9a7044'), sombre=hx('7a5432'), trait=hx('3a2614')))
    d = ImageDraw.Draw(g)
    for y in (12, 24, 36): d.line([(1, y), (46, y)], fill=hx('6a4426'))
    for (x, y) in ((16, 1), (34, 13), (10, 25), (28, 37)): d.line([(x, y), (x, y + 10)], fill=hx('6a4426'))
    return centre(im, g)
def icone_bulle():
    return centre(toile(20, 20), metal(m_bulle(44, 40), BLANC))
def toasts():
    r = {f'toast/{n}': toast() for n in ('advancement', 'recipe', 'system', 'tutorial')}
    r['toast/mouse'] = icone_souris(); r['toast/right_click'] = icone_souris(True); r['toast/movement_keys'] = icone_touches()
    r['toast/recipe_book'] = icone_livre(OR, (20, 20)); r['toast/social_interactions'] = icone_bulle()
    r['toast/tree'] = icone_arbre(); r['toast/wooden_planks'] = icone_planches()
    return r

# ---------------- HUD : viseur, indicateurs d'attaque, barre de saut
def m_epee(w, h):
    m = masque(w, h); trait(m, [(w * .22, h * .78), (w - 3, 2)], 4); trait(m, [(w * .08, h * .62), (w * .38, h * .92)], 3); trait(m, [(2, h - 3), (w * .2, h * .8)], 3); return m
def hud():
    r = {'hud/crosshair': viseur()}
    def blanc(m, a=255):
        im = Image.new('RGBA', m.size); p = im.load(); q = m.load()
        for y in range(m.height):
            for x in range(m.width):
                if q[x, y]: p[x, y] = (255, 255, 255, a)
        return im
    b = masque(48, 12); rect(b, 0, 3, 48, 9); r['hud/crosshair_attack_indicator_background'] = blanc(b, 110)
    r['hud/crosshair_attack_indicator_progress'] = blanc(b)
    r['hud/crosshair_attack_indicator_full'] = centre(toile(16, 16), blanc(m_epee(30, 30)))
    fond = plaque(18, 18, OR, ARD['fond'], ep=3, coin=2)
    ep = m_epee(36, 36); ombre = biseau(ep, dict(clair=ARD['creux'], base=ARD['creux'], mi=ARD['noir'], sombre=ARD['noir'], trait=ARD['noir']), contour=False)
    r['hud/hotbar_attack_indicator_background'] = centre(fond, ombre)
    r['hud/hotbar_attack_indicator_progress'] = centre(toile(18, 18), metal(ep, OR))
    jb = plaque(182, 5, OR, ARD['puits'], ep=2, coin=1); r['hud/jump_bar_background'] = jb
    for n, pal in (('progress', OR), ('cooldown', GRIS)):
        m = masque(546, 15); rect(m, 3, 3, 543, 12); r['hud/jump_bar_' + n] = metal(m, pal, contour=False)
    return r

# ---------------- conteneurs
def conteneurs():
    r = {}
    for n, (w, h) in (('anvil/error', (28, 21)), ('cartography_table/error', (28, 21)), ('grindstone/error', (28, 21)), ('smithing/error', (28, 21)), ('loom/error', (26, 26))):
        r['container/' + n] = centre(toile(w, h), metal(m_croix(min(w, h) * 3 - 12, 8), ROUGE_VIF))
    r['container/slot'] = plaque(18, 18, OR, ARD['creux'], ep=2, coin=1)
    # établi mécanique (crafter)
    ds = plaque(18, 18, ROUGE, ARD['noir'], ep=2, coin=1); centre(ds, metal(m_croix(30, 5), ROUGE_VIF)); r['container/crafter/disabled_slot'] = ds
    for n, pal in (('powered_redstone', ROUGE_VIF), ('unpowered_redstone', dict(clair=hx('7a2a24'), base=hx('5a1c18'), mi=hx('4a1410'), sombre=hx('380e0c'), trait=hx('1c0606')))):
        m = masque(48, 48); trait(m, [(4, 24), (44, 24)], 6); trait(m, [(24, 4), (24, 44)], 6); ellipse(m, 16, 16, 33, 33)
        r['container/crafter/' + n] = metal(m, pal)
    # sacoche
    r['container/bundle/background'] = plaque(32, 32, OR, ARD['fond'], ep=3, coin=2)
    r['container/bundle/slot'] = plaque(18, 20, OR, ARD['creux'], ep=2, coin=1)
    bs = plaque(18, 20, ROUGE, ARD['noir'], ep=2, coin=1); centre(bs, metal(m_croix(28, 5), ROUGE_VIF)); r['container/bundle/blocked_slot'] = bs
    # cartographie : feuilles de carte
    def feuille(w, h):
        im = toile(w, h); p = plaque(w, h, OR, hx('e8dcb8'), ep=3, coin=2); d = ImageDraw.Draw(p)
        for k in range(12, p.width - 9, 12): d.line([(k, 6), (k, p.height - 7)], fill=hx('d4c69e'))
        for k in range(12, p.height - 9, 12): d.line([(6, k), (p.width - 7, k)], fill=hx('d4c69e'))
        return p
    r['container/cartography_table/map'] = feuille(66, 66)
    sm = feuille(66, 66); ImageDraw.Draw(sm).rectangle([66, 66, 131, 131], outline=ROUGE['mi'], width=3); r['container/cartography_table/scaled_map'] = sm
    dm = toile(50, 66); colle(dm, feuille(44, 58), 18, 0); colle(dm, feuille(44, 58), 0, 24); r['container/cartography_table/duplicated_map'] = dm
    r['container/cartography_table/locked'] = centre(toile(10, 14), metal(m_cadenas(24, 34, False), OR))
    # sélecteur de mode de jeu
    r['gamemode_switcher/slot'] = plaque(26, 26, OR, ARD['fond'], ep=3, coin=2)
    sel = toile(26, 26); W = sel.width; m = masque(W, W); rect(m, 0, 0, W, W); rect(m, 5, 5, W - 5, W - 5, 0); colle(sel, metal(m, ROUGE)); r['gamemode_switcher/selection'] = sel
    return r
def fond_mode_de_jeu():
    im = Image.new('RGBA', (128 * S, 128 * S)); p = plaque(125, 75, OR, (42, 46, 55, 200), ep=4, coin=3)
    d = ImageDraw.Draw(p)
    for y in range(4, 19 * S): d.line([(5, y), (p.width - 6, y)], fill=ARD['puits'])
    d.line([(5, 19 * S), (p.width - 6, 19 * S)], fill=OR['mi'])
    for (x, y) in ((3, 3), (p.width - 6, 3), (3, p.height - 6), (p.width - 6, p.height - 6)): rivet(p, x, y, OR)
    colle(im, p); return {'../container/gamemode_switcher': im}

def tout():
    r = {}
    for f in (progres, livre_recettes, listes, widgets, social, toasts, hud, conteneurs): r.update(f())
    return r
