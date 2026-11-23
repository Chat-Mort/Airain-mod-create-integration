# Lot 5d : écrans de Numismatics 1.1.0 dans la langue « carter » des écrans de Create (coordonnées relevées sur les planches
# et dans le code des écrans de Numismatics : titres, boutons, cases, champs). Les boutons sont posés par le jeu.
import math, random
from kit import *
from PIL import Image, ImageDraw
import ecrans
O = '/tmp/src5/numis/common/src/main/resources/assets/numismatics/textures/gui/'
def original(nom): return Image.open(O + nom + '.png').convert('RGBA')

# ---------------- éléments propres à la banque ----------------
def engrenage_relief(p, X, Y, r, dents=8, vide=True): p.engrenage_relief(X, Y, r, dents, vide)

def afficheur(p, x, y, w, h):
    """Afficheur du solde (le jeu y écrit en blanc, centré) : verre fumé dans une lunette d'airain, vis aux deux bouts."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base'])
    p.r(X0 + 12, Y0 + 3, X1 - 12, Y1 - 3, EXP['trait'])
    p.r(X0 + 13, Y0 + 4, X1 - 13, Y1 - 4, hx('1a1d23')); p.r(X0 + 13, Y0 + 4, X1 - 13, Y0 + 5, hx('101216'))
    p.r(X0 + 14, Y0 + 6, X0 + 40, Y0 + 6, hx('2c313b'))                    # reflet du verre
    for X in (X0 + 6, X1 - 6): p.boulon(X, (Y0 + Y1) // 2)

def fente_pieces(p, x, y, h=18, w=16):
    """Fente à pièces : plaque d'airain rivetée aux coins, lèvre en creux autour d'une fente verticale noire
    (x = centre en px d'interface, y = haut), une pièce à demi engagée dans la fente."""
    X, Y0, Y1 = x * S + 1, y * S, (y + h) * S - 1; L = w * S // 2
    p.r(X - L, Y0, X + L, Y1, EXP['trait']); p.r(X - L + 1, Y0 + 1, X + L - 1, Y1 - 1, EXP['mi']); p.r(X - L + 1, Y0 + 1, X + L - 2, Y1 - 2, EXP['clair'])
    p.r(X - L + 2, Y0 + 2, X + L - 2, Y1 - 2, EXP['base'])
    for (a, b) in ((X - L + 5, Y0 + 5), (X + L - 5, Y0 + 5), (X - L + 5, Y1 - 5), (X + L - 5, Y1 - 5)): p.rivet(a, b)
    p.r(X - 6, Y0 + 9, X + 6, Y1 - 9, EXP['trait']); p.r(X - 5, Y0 + 10, X + 5, Y1 - 10, EXP['sombre']); p.r(X - 4, Y0 + 11, X + 5, Y1 - 10, EXP['mi'])
    p.r(X - 2, Y0 + 12, X + 2, Y1 - 12, ARD['noir']); p.r(X - 2, Y0 + 12, X + 2, Y0 + 13, hx('000000'))
    for k in range(7):                                                   # pièce engagée : tranche dorée qui dépasse au-dessus
        p.r(X - 1, Y0 + 5 + k, X + 1, Y0 + 5 + k, OR['trait'] if k in (0,) else OR['clair'] if k < 3 else OR['base'])

def fente_carte(p, x, y, w, h=12):
    """Lecteur de cartes : boîtier d'airain riveté, lèvre en creux, fente horizontale noire, une carte d'identité
    à demi engagée (papier vieilli, bande d'airain). x, y, w, h en px d'interface."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); p.r(X0 + 2, Y1 - 3, X1 - 2, Y1 - 2, EXP['mi'])
    for (a, b) in ((X0 + 5, Y0 + 5), (X1 - 5, Y0 + 5), (X0 + 5, Y1 - 5), (X1 - 5, Y1 - 5)): p.rivet(a, b)
    cy = (Y0 + Y1) // 2
    p.r(X0 + 11, cy - 5, X1 - 11, cy + 5, EXP['trait']); p.r(X0 + 12, cy - 4, X1 - 12, cy + 4, EXP['sombre']); p.r(X0 + 13, cy - 3, X1 - 12, cy + 4, EXP['mi'])
    p.r(X0 + 14, cy - 1, X1 - 14, cy + 1, ARD['noir'])
    # carte engagée : dépasse vers le haut au milieu de la fente
    cx = (X0 + X1) // 2; cw = min(30, (X1 - X0) // 3)
    p.r(cx - cw, Y0 - 9, cx + cw, cy, hx('7a6a4a')); p.r(cx - cw + 1, Y0 - 8, cx + cw - 1, cy, hx('f3ead6'))
    p.r(cx - cw + 1, Y0 - 5, cx + cw - 1, Y0 - 3, EXP['base']); p.r(cx - cw + 1, Y0 - 3, cx + cw - 1, Y0 - 3, EXP['mi'])
    p.r(cx - cw + 1, cy - 1, cx + cw - 1, cy + 1, ARD['noir'])

def coffre(p, x, y, r=27):
    """Cadran de coffre-fort (centre x, y en px d'interface, rayon en texels) : lunette d'airain, cadran sombre gradué,
    bouton cannelé au centre, repère ivoire en haut."""
    X, Y = x * S + 1, y * S + 1
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d > r + 0.3: continue
            if d > r - 1: c = EXP['trait']
            elif d > r - 4: c = EXP['clair'] if dx + dy < 0 else EXP['mi']
            elif d > r - 5: c = EXP['trait']
            else: c = hx('23262d') if dx + dy < 0 else hx('1e2127')
            p.im.putpixel((X + dx, Y + dy), c)
    for k in range(40):                                                 # graduations : une longue toutes les cinq
        a = 2 * math.pi * k / 40 - math.pi / 2; L = 4 if k % 5 == 0 else 2
        for t in range(L):
            rr = r - 6 - t; p.im.putpixel((X + round(rr * math.cos(a)), Y + round(rr * math.sin(a))), hx('d8ccae') if k % 5 == 0 else hx('8a8576'))
    R = int(r * 0.45)                                                   # bouton cannelé
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            d = math.hypot(dx, dy)
            if d > R + 0.3: continue
            a = math.atan2(dy, dx); cannelure = (int((a + math.pi) / (2 * math.pi) * 16) % 2 == 0) and d > R - 3
            c = EXP['trait'] if d > R - 1 else (EXP['sombre'] if cannelure else EXP['clair'] if dx + dy < 0 else EXP['base'] if dx + dy < R * 0.6 else EXP['mi'])
            p.im.putpixel((X + dx, Y + dy), c)
    p.r(X - 1, Y - 1, X + 1, Y + 1, EXP['trait']); p.im.putpixel((X, Y), EXP['clair'])
    for k in range(4): p.r(X - k, Y - r - 4 + k, X + k, Y - r - 4 + k, hx('f3ead6') if k < 3 else EXP['trait'])   # repère

def fleche(p, x, y, vers_gauche=True):
    """Flèche d'airain de 16 x 11 px (coin haut gauche en px d'interface), même dessin que le choix d'objet de la jauge."""
    fl = Image.new('L', (16 * S, 11 * S)); d = ImageDraw.Draw(fl)
    pts = [(0, 12), (27, 12), (27, 3), (47, 16), (27, 29), (27, 20), (0, 20)]
    if vers_gauche: pts = [(47 - a, b) for (a, b) in pts]
    d.polygon(pts, fill=255)
    for yy in range(fl.height):
        for xx in range(fl.width):
            if fl.getpixel((xx, yy)):
                bord = any(not (0 <= xx + a < fl.width and 0 <= yy + b < fl.height) or not fl.getpixel((xx + a, yy + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                p.im.putpixel((x * S + xx, y * S + yy), EXP['trait'] if bord else EXP['clair'] if yy < 15 else EXP['mi'])

def vitrine(p, x, y, w=28, h=28):
    """Vitrine de l'objet vendu : lunette d'airain épaisse, verre bleuté aux coins (reflets), fond en creux."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); p.r(X0 + 2, Y1 - 3, X1 - 2, Y1 - 2, EXP['mi'])
    for (X, Y) in ((X0 + 3, Y0 + 3), (X1 - 3, Y0 + 3), (X0 + 3, Y1 - 3), (X1 - 3, Y1 - 3)): p.im.putpixel((X, Y), EXP['trait'])
    p.r(X0 + 5, Y0 + 5, X1 - 5, Y1 - 5, EXP['trait'])
    p.r(X0 + 6, Y0 + 6, X1 - 6, Y1 - 6, hx('20262c'))
    for k in range(7):                                                  # reflets du verre en haut à gauche
        p.r(X0 + 7 + k, Y0 + 7, X0 + 7 + k, Y0 + 13 - k, hx('3a5560') if k < 5 else hx('2c3d45'))
    for k in range(3): p.im.putpixel((X1 - 8 - k, Y1 - 8 + k - 2), hx('34474f'))

def rubis(p, x, y, w=32, h=16):
    """Cartouche de l'enseigne du point de vente (le rubis de l'original) : plaque d'airain rivetée, deux fenêtres, rubis au centre."""
    X0, Y0, X1, Y1 = x * S, y * S, (x + w) * S - 1, (y + h) * S - 1
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base'])
    cx, cy = (X0 + X1) // 2, (Y0 + Y1) // 2
    for (a, b) in ((X0 + 9, cx - 12), (cx + 12, X1 - 9)):
        p.r(a, Y0 + 8, b, Y1 - 8, EXP['trait']); p.r(a + 1, Y0 + 9, b - 1, Y1 - 9, hx('2a1a14'))
    p._lampe_texel(cx, cy, 'rouge', 9)
    for (X, Y) in ((X0 + 4, Y0 + 4), (X1 - 4, Y0 + 4), (X0 + 4, Y1 - 4), (X1 - 4, Y1 - 4)): p.rivet(X, Y)

def etiquette_prix(p, x0, y0, x1, y1, graine=5):
    """Étiquette de prix (le jeu y écrit les montants à l'encre sombre, pièces à droite) : papier vieilli, double filet,
    œillet et cordelette en haut à gauche, coins découpés."""
    rnd = random.Random(graine); PAP = [hx('f3ead6'), hx('efe4cc'), hx('f6eedc')]; BORD = hx('7a6a4a')
    X0, Y0, X1, Y1 = x0 * S, y0 * S, x1 * S - 1, y1 * S - 1
    fond = p.im.copy()
    p.r(X0 + 3, Y1 + 1, X1 + 2, Y1 + 3, ARD['ombre']); p.r(X1 + 1, Y0 + 3, X1 + 3, Y1 + 3, ARD['ombre'])
    fond = p.im.copy()
    for Y in range(Y0, Y1 + 1):
        for X in range(X0, X1 + 1): p.im.putpixel((X, Y), PAP[rnd.randint(0, 2)] if rnd.random() < 0.35 else PAP[0])
    p.r(X0, Y0, X1, Y0, BORD); p.r(X0, Y1, X1, Y1, BORD); p.r(X0, Y0, X0, Y1, BORD); p.r(X1, Y0, X1, Y1, BORD)
    p.r(X0 + 1, Y1 - 1, X1 - 1, Y1 - 1, hx('d8ccae'))
    for (d, c) in ((3, hx('b8a27a')), (5, hx('d8c6a0'))):
        p.r(X0 + d, Y0 + d, X1 - d, Y0 + d, c); p.r(X0 + d, Y1 - d, X1 - d, Y1 - d, c)
        p.r(X0 + d, Y0 + d, X0 + d, Y1 - d, c); p.r(X1 - d, Y0 + d, X1 - d, Y1 - d, c)
    R = 5
    for j in range(R):
        for i in range(R):
            dd = (i + 0.5) ** 2 + (j + 0.5) ** 2
            for (X, Y) in ((X0 + i, Y0 + j), (X0 + i, Y1 - j), (X1 - i, Y0 + j), (X1 - i, Y1 - j)):
                if dd < R * R: p.im.putpixel((X, Y), fond.getpixel((X, Y)))
                elif dd < (R + 1.2) ** 2: p.im.putpixel((X, Y), BORD)

def niche(p, x, y, w, h):
    """Niche d'un bouton isolé : même plateau que celui du bas, à 3 px autour du bouton."""
    p.socle(0, 0, 0, 0, texels=(x * S, y * S, (x + w) * S - 1, (y + h) * S - 1))

# ---------------- outils de mise en page ----------------
def cases(p, liste, riche=True):
    """Cases à partir de leur intérieur gris (x, y de l'intérieur 16 x 16) : case sertie ou simple creux."""
    for (x, y) in liste:
        if riche: p.case_riche(x - 1, y - 1)
        else: p.creux(x - 1, y - 1, 18, 18)
def champs(p, liste):
    """Champs à molette à partir de leur intérieur gris (x, y, w, h) relevé sur l'original."""
    for (x, y, w, h) in liste: p.champ(x - 2, y - 3, w + 4, h + 6, molette=True)
def base(nom, w, h, F=None, graine=1):
    o = original(nom); p = Planche(base=o.resize((768, 768), Image.NEAREST)); p.efface(0, 0, w, h)
    F = F or w - 8; p.carter(0, 0, F, h, graine=graine); return p, F
def titre(p, F): p.plaque_nom(F // 2 - 51, 2, 102)                      # centrée sur x + (largeur - 8) / 2
def bas(p, F, h): ecrans._socle_bas(p, 0, 0, F, h)
def rangee(p, x, y, n, riche=False):
    for i in range(n): p.creux(x - 1 + 18 * i, y - 1, 18, 18)

# ---------------- écrans ----------------
def deposant_andesite():
    p, F = base('andesite_depositor', 182, 79, graine=41); titre(p, F)
    niche(p, 16, 20, 24, 24)                                            # bouton de la liste de confiance (19, 23)
    p.champ(79, 24, 74, 16, molette=True)                               # choix de la pièce (84, 23)
    fente_pieces(p, 59, 23)                                             # entre la niche (40) et le champ (79), à la hauteur du bouton
    p.grille(157, 18, 12, 30)
    bas(p, F, 79); rangee(p, 11, 56, 7)
    return p.im

def deposant_laiton():
    p, F = base('brass_depositor', 208, 145, graine=43); titre(p, F); afficheur(p, 6, 17, F - 12, 15)
    for (sx, fx) in ((25, 46), (111, 132)):
        cases(p, [(sx, 46 + 22 * k) for k in range(3)]); champs(p, [(fx, 49 + 22 * k, 40, 10) for k in range(3)])
    # arbre vertical entre les deux colonnes, un engrenage d'airain à la hauteur de chaque rangée
    X = 99 * S + 1; p.r(X - 3, 42 * S, X + 3, 112 * S, EXP['trait']); p.r(X - 2, 42 * S, X + 2, 112 * S, EXP['mi']); p.r(X - 2, 42 * S, X - 1, 112 * S, EXP['clair'])
    for k in range(3): engrenage_relief(p, X, (55 + 22 * k) * S, 26, 9)
    p.grille(7, 40, 13, 70); p.grille(181, 40, 13, 70)
    bas(p, F, 145); rangee(p, 37, 122, 7)
    return p.im

def terminal_bancaire():
    p, F = base('bank_terminal', 200, 132, graine=45); titre(p, F); afficheur(p, 6, 17, F - 12, 15)
    ecrans._sertie(p, 8, 66, 124, 92); rangee(p, 13, 71, 6)            # sorties de pièces, cadre boulonné à 4 px
    p.case_riche(154, 66, 26, 26)                                       # entrée (grande case)
    fleche(p, 131, 74, vers_gauche=True)
    coffre(p, 96, 49, 36)
    p.grille(18, 42, 54, 15); p.grille(120, 42, 54, 15)
    bas(p, F, 132); p.creux(7, 108, 18, 18)                             # carte (8, 109)
    return p.im

def sous_comptes():
    p, F = base('bank_terminal_sub_account_list', 234, 220, graine=47); titre(p, F)
    p.creux(5, 15, F - 10, 176, fond=hx('2a2e37'))                      # liste (cartes de Create posées dessus)
    bas(p, F, 220); p.champ(10, 197, 156, 16)                          # nom du nouveau sous-compte (texte blanc)
    # petites icônes des cartes, gardées au pixel ; étiquette haute du curseur de pièces refaite comme celles du réglage de valeur
    o = original('bank_terminal_sub_account_list')
    for (x, y, w, h) in ((0, 220, 12, 12), (12, 220, 12, 12), (0, 232, 12, 12), (0, 244, 12, 12)):
        p.efface(x, y, w, h); p.im.alpha_composite(o.crop((x, y, x + w, y + h)).resize((w * S, h * S), Image.NEAREST), (x * S, y * S))
    p.efface(12, 242, 81, 14)
    hd = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/create/textures/gui/value_settings.png')
    lab = hd.crop((0, 31 * S, 81 * S, 42 * S))                           # 33 texels -> 42 : on répète le milieu
    haut = lab.crop((0, 0, lab.width, 12)); mil = lab.crop((0, 16, lab.width, 17)); bas_ = lab.crop((0, 21, lab.width, 33))
    t = Image.new('RGBA', (81 * S, 42)); t.paste(haut, (0, 0))
    for k in range(18): t.paste(mil, (0, 12 + k))
    t.paste(bas_, (0, 30)); p.im.paste(t, (12 * S, 242 * S))
    return p.im

def sous_compte_fenetre():
    p, F = base('bank_terminal_sub_account_list_popup', 250, 193, F=250, graine=49); p.efface(0, 133, 250, 60)
    p.carter(0, 0, 250, 133, graine=49)
    ecrans._ticket_entete(p, 14, 2, 236, 14, graine=11)                 # nom du sous-compte, à l'encre sombre
    p.creux(36, 16, 178, 102)
    ecrans._sertie(p, 40, 20, 210, 82); rangee(p, 45, 25, 9); rangee(p, 45, 43, 9); rangee(p, 45, 61, 9)
    p.case_riche(42, 89); p.champ(62, 90, 114, 16, molette=True); p.case_riche(187, 89)
    niche(p, 220, 89, 24, 24)                                           # bouton de validation (223, 92)
    p.grille(9, 20, 22, 94); p.grille(218, 20, 22, 63)
    o = original('bank_terminal_sub_account_list_popup')                # icônes des modes d'autorisation, au pixel, sans le fond gris
    for (x, y) in ((0, 240), (20, 240), (40, 240)):
        ic = o.crop((x, y, x + 16, y + 16)); ic.putdata([(0, 0, 0, 0) if c[:3] == (139, 139, 139) else c for c in ic.getdata()])
        p.efface(x, y, 16, 16); p.im.alpha_composite(ic.resize((48, 48), Image.NEAREST), (x * S, y * S))
    return p.im

def liste_confiance(nom='trust_list', graine=51, banquier=False):
    p, F = base(nom, 200, 110, graine=graine)
    if banquier: ecrans._ticket_entete(p, 14, 2, 178, 14, graine=12)    # nom du banquier, à l'encre sombre
    else: titre(p, F)
    ecrans._sertie(p, 11, 16, 181, 78)
    for k in range(3): rangee(p, 16, 21 + 18 * k, 9)
    bas(p, F, 110)
    if banquier:                                                        # carte du banquier, voyant de la flamme, lecteur
        p.creux(6, 86, 18, 18); p.lampe(36, 95, 'ambre', 12); fente_carte(p, 70, 89, 72)
    else: fente_carte(p, 49, 89, 72)                                    # lecteur centré sur la place libre (5 à 165)
    return p.im

def config_vente():
    p, F = base('salepoint_config', 238, 145, graine=53); titre(p, F); afficheur(p, 6, 17, F - 12, 15)
    for (sx, fx) in ((14, 35), (152, 173)):
        cases(p, [(sx, 46 + 22 * k) for k in range(3)]); champs(p, [(fx, 49 + 22 * k, 40, 10) for k in range(3)])
    ecrans._sertie(p, 86, 44, 142, 104)
    vitrine(p, 100, 54); p.creux(105, 59, 18, 18); rubis(p, 98, 84)
    bas(p, F, 145)
    rangee(p, 48, 122, 6); p.case_riche(168, 121)
    return p.im

def achat_vente():
    p, F = base('salepoint', 226, 137, graine=55); titre(p, F); afficheur(p, 6, 17, F - 12, 15)
    ecrans._sertie(p, 62, 38, 156, 104)
    vitrine(p, 68, 55); p.creux(73, 60, 18, 18); rubis(p, 66, 85)
    etiquette_prix(p, 100, 43, 152, 81)
    p.champ(99, 82, 51, 16, molette=True)                               # quantité (104, 81)
    p.engrenage(33, 60, 27, 11); p.engrenage(33, 87, 15, 7); p.engrenage(188, 60, 27, 11); p.engrenage(188, 87, 15, 7)
    bas(p, F, 137); p.creux(9, 113, 18, 18)
    p.creux(53, 113, 130, 18, fond=hx('1a1d23'))                        # couloir de la jauge d'achat
    for X in range(53 * S + 6 + 12, 183 * S - 6, 13 * S): p.r(X, 113 * S + 6, X, 113 * S + 8, hx('3a3f4a'))
    # jauge (53,137 130x18, rognée par le jeu), réservoir et éclair (fluide, énergie)
    p.efface(53, 137, 130, 18); p.efface(18, 137, 28, 56); p.efface(0, 193, 24, 47)
    X0, Y0, X1, Y1 = 53 * S + 6, 137 * S + 6, 183 * S - 4, 155 * S - 4
    deg = [hx('ffd98a'), hx('f3b04a'), hx('e08a10'), hx('e08a10'), hx('c87310'), hx('a85a0a'), hx('8a4a08')]
    for Y in range(Y0, Y1 + 1):
        c = deg[min(len(deg) - 1, (Y - Y0) * len(deg) // (Y1 - Y0 + 1))]; p.r(X0, Y, X1, Y, c)
    for X in range(X0 + 12, X1, 13 * S): p.r(X, Y0, X, Y0 + 2, hx('8a4a08'))
    # réservoir : fond (18,137) puis cadre (18,165) posé par-dessus le fluide
    p.creux(18, 137, 28, 28, fond=hx('1a1d23'))
    vitrine(p, 18, 165); p.r(18 * S + 6, 165 * S + 6, 46 * S - 7, 193 * S - 7, (0, 0, 0, 0))
    for k in range(7): p.r(18 * S + 7 + k, 165 * S + 7, 18 * S + 7 + k, 165 * S + 13 - k, (138, 180, 196, 90))
    # éclairs : éteint (0,193 24x24, posé en x+2) et allumé (0,217 22x22, rempli du bas vers le haut)
    def eclair(X, Y, n, c_bord, c1, c2):
        K = 8; m = Image.new('L', (n * K, n * K)); d = ImageDraw.Draw(m); s = n * K / 22
        d.polygon([(13 * s, 1 * s), (4 * s, 12 * s), (10 * s, 12 * s), (7 * s, 21 * s), (18 * s, 8 * s), (12 * s, 8 * s), (15 * s, 1 * s)], fill=255)
        m = m.resize((n, n), Image.BOX).point(lambda v: 255 if v >= 128 else 0); px = m.load()
        for y in range(n):
            for x in range(n):
                if not px[x, y]: continue
                bord = any(not (0 <= x + a < n and 0 <= y + b < n) or not px[x + a, y + b] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                p.im.putpixel((X + x, Y + y), c_bord if bord else c1 if x + y < n * 0.9 else c2)
    eclair(0, 193 * S, 24 * S, ARD['noir'], hx('3a3f4a'), hx('2c3039'))
    eclair(0, 217 * S, 22 * S, EXP['trait'], hx('ffd98a'), hx('e08a10'))
    return p.im

def distributeur(nom='vendor'):
    p, F = base(nom, 254, 151, graine=57); titre(p, F); afficheur(p, 6, 17, F - 12, 15)
    for (sx, fx) in ((18, 39), (164, 185)):
        cases(p, [(sx, 46 + 22 * k) for k in range(3)]); champs(p, [(fx, 49 + 22 * k, 40, 10) for k in range(3)])
    ecrans._sertie(p, 91, 38, 153, 117)                                  # le mode et la réserve dans un même cadre, 4 px de marge
    p.champ(94, 42, 53, 14, molette=True)                               # mode (99, 40)
    for k in range(3): rangee(p, 96, 60 + 18 * k, 3)
    bas(p, F, 151); rangee(p, 52, 128, 6); p.case_riche(166, 127); p.creux(191, 127, 18, 18)
    return p.im

ECRANS = {'andesite_depositor': deposant_andesite, 'brass_depositor': deposant_laiton, 'bank_terminal': terminal_bancaire,
          'bank_terminal_sub_account_list': sous_comptes, 'bank_terminal_sub_account_list_popup': sous_compte_fenetre,
          'trust_list': liste_confiance, 'blaze_banker': lambda: liste_confiance('blaze_banker', 59, True),
          'salepoint_config': config_vente, 'salepoint': achat_vente, 'vendor': distributeur, 'creative_vendor': lambda: distributeur('creative_vendor')}
