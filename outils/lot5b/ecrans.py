# Lot 5b : écrans de Create, élément par élément (coordonnées en pixels d'interface, relevées sur les planches de Create 6.0.10).
# Les boutons (valider, etc.) sont dessinés par Create par-dessus : leur emplacement reste de l'ardoise.
from kit import *
from PIL import Image
O = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/'
def original(nom): return Image.open(O + nom + '.png').convert('RGBA')

def lien_affichage():
    p = Planche()
    # Lien d'affichage (0,0 235x162, la pointe de droite part) : plaque, bandeau du titre, zone source -> cible en creux,
    # tuyau de liaison à voyants (source verte en haut, cible ambre en bas), engrenages gravés dans la colonne de droite
    p.plaque(0, 0, 226, 162, graine=3)
    p.bandeau(3, 3, 220)
    p.creux(25, 15, 186, 117)
    for y in (25, 104): p.case_riche(36, y); p.champ(60, y, 137, 18, molette=True)
    for y in (46, 64, 84): p.filet_creux(60, 197, y)
    p.filet_creux(28, 208, 93)
    p.chevron(118, 93)                                                 # de la source vers la cible
    p.tuyau(13, 15, 132, brides=(20, 127)); p.lampe(13, 34, 'vert'); p.lampe(13, 113, 'ambre')
    p.engrenage(217, 38, 18, 10); p.engrenage(216, 70, 12, 7); p.engrenage(218, 100, 18, 10)
    p.socle(3, 133, 220, 26)
    # morceaux de la zone de données (163) : début, milieu (étiré), fin, bulle
    for (x, w) in ((0, 2), (3, 1), (5, 2), (8, 5)): p.efface(x, 163, w, 18)
    X0, Y0, Y1 = 0, 163 * S, 181 * S - 1
    def bande(X0, X1):
        p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0, Y0 + 1, X1, Y0 + 2, EXP['sombre']); p.r(X0, Y1 - 2, X1, Y1 - 1, EXP['base'])
        p.r(X0, Y0 + 3, X1, Y0 + 4, ARD['ombre']); p.r(X0, Y0 + 5, X1, Y1 - 3, ARD['creux'])
    bande(0, 6 * S - 1 - 9); bande(3 * S, 4 * S - 1); bande(5 * S, 7 * S - 1); bande(8 * S, 13 * S - 1)
    p.r(0, Y0, 0, Y1, EXP['trait']); p.r(1, Y0 + 1, 2, Y1 - 1, EXP['sombre'])           # bord gauche du début
    p.r(7 * S - 1, Y0, 7 * S - 1, Y1, EXP['trait']); p.r(7 * S - 3, Y0 + 1, 7 * S - 2, Y1 - 1, EXP['clair'])   # bord droit de la fin
    # Contact d'ascenseur (20,172 233x82)
    p.plaque(20, 174, 224, 80, graine=5)
    p.bandeau(23, 177, 218)
    p.champ(41, 197, 30, 18); p.champ(74, 197, 150, 18, molette=True)
    p.socle(23, 225, 218, 26)
    p.case_riche(59, 231, 12, 16); p.champ(74, 230, 58, 18, molette=True)
    return p.im

def interrupteur_seuil():
    p = Planche()
    p.plaque(0, 0, 173, 103, graine=7)                                 # (0,0 182x103), la pointe part
    p.bandeau(3, 3, 167)
    for y in (23, 47): p.case_riche(23, y)
    p.engrenage(11, 31, 17, 9); p.engrenage(12, 58, 13, 7)
    p.socle(3, 74, 167, 26)
    p.case_riche(12, 79)
    # champs des réglages (0,105 / 0,129 115x22) : bande d'ardoise de la plaque, champs en creux
    for y in (105, 129):
        p.efface(0, y, 115, 22)                  # fond transparent : la plaque de l'écran passe dessous
        if y == 105: p.champ(3, y + 1, 49, 19); p.champ(55, y + 1, 52, 19, molette=True)
        else: p.champ(3, y + 1, 104, 19, molette=True)
    # état courant (0,153 24x24) : case dans un cadre d'airain neuf
    p.efface(0, 153, 24, 24)
    B = bande_or()
    X0, Y0 = 0, 153 * S
    for k, c in enumerate(B[:6] + [B[-1]]): p.r(X0 + k, Y0 + k, X0 + 24 * S - 1 - k, Y0 + 24 * S - 1 - k, c)
    p.creux(2, 155, 20, 20)
    return p.im

def interrupteur_seuil_B():
    """Piste B : carter de machine."""
    p = Planche()
    p.carter(0, 0, 173, 103, graine=7)
    p.plaque_nom(40, 2, 102)                                           # centrée sur le titre (x + 182/2)
    for y in (23, 47): p.case_riche(23, y)
    p.grille(6, 21, 11, 46)
    # plateau du bas centré sur la case (79-97) : de 234 à 293 texels, le bas touche le cadre du carter (retour de Liam)
    p.socle(0, 0, 0, 0, texels=(5 * S, 234, 168 * S - 1, 293))
    p.case_riche(12, 79, ep=3)
    for y in (105, 129):
        p.efface(0, y, 115, 22)
        if y == 105: p.champ(3, y + 1, 49, 19); p.champ(55, y + 1, 52, 19, molette=True)
        else: p.champ(3, y + 1, 104, 19, molette=True)
    # état courant (0,153 24x24) : repris de la piste A
    A = interrupteur_seuil(); p.im.paste(A.crop((0, 153 * S, 24 * S, 177 * S)), (0, 153 * S))
    return p.im

def lien_affichage_B():
    """Piste B (retenue par Liam) : carter de machine."""
    p = Planche()
    p.carter(0, 0, 226, 162, graine=3)
    p.plaque_nom(66, 2, 102)                                           # centrée sur le titre (x + 235/2)
    p.creux(25, 15, 186, 117)
    for y in (25, 104): p.case_riche(36, y); p.champ(60, y, 137, 18, molette=True)
    for y in (46, 64, 84): p.filet_creux(60, 197, y)
    p.filet_creux(28, 208, 93); p.chevron(118, 93)
    p.tuyau(13, 16, 132); p.voyant_monte(13, 34, 'vert'); p.voyant_monte(13, 113, 'ambre')
    p.grille(214, 22, 7, 102)
    # plateau du bas centré sur le bouton de Create (138-156) : 411 à 470 texels
    p.socle(0, 0, 0, 0, texels=(5 * S, 411, 221 * S - 1, 470))
    # zone de données (163) : inchangée depuis la piste A
    A = lien_affichage(); p.im.paste(A.crop((0, 163 * S, 14 * S, 181 * S)), (0, 163 * S))
    # contact d'ascenseur (20,174 224x80)
    p.carter(20, 174, 224, 80, graine=5)
    p.plaque_nom(81, 177, 102)                                         # titre en (x + 112, y + 6)
    p.champ(41, 197, 30, 18); p.champ(74, 197, 150, 18, molette=True)
    # plateau du bas : case 231-247 et champ 230-248 -> centré sur 239, du texel 690 au 748 (bas du carter)
    # plateau en tiroir, entaillé dans le cadre du bas : centré sur le champ (690-743) avec 12 texels de jeu en haut et en bas
    # (le carter seul laissait trop peu de place sous les éléments de Create pour les centrer)
    p.socle(0, 0, 0, 0, texels=(25 * S, 678, 239 * S - 1, 755))
    p.r(25 * S - 1, 756, 239 * S, 756, EXP['trait'])
    p.case_riche(59, 231, 12, 16, ep=3); p.champ(74, 230, 58, 18, molette=True)
    return p.im

def engrenage_sequence():
    """Engrenage séquencé (0,0 173x161), piste B. Les lignes d'instruction (162x22) sont posées par Create sur n'importe quelle
    rangée : chaque bande est identique (même fond, mêmes joints, tuyau, cadre sans boulon dans cette zone) pour se raccorder."""
    p = Planche()
    p.carter(0, 0, 165, 161, graine=9)
    p.plaque_nom(31, 2, 102)                                           # centrée sur le titre (x + (173 - 8) / 2)
    # --- fond d'une rangée (22 px), construit une fois puis recopié
    from PIL import Image as I
    base = Planche(); b = base
    b.carter(0, 0, 165, 161, graine=9)                                  # mêmes bandes de cadre que l'écran
    Y0, Y1 = 16 * S, 38 * S - 1
    b.r(15, Y0, 165 * S - 16, Y1, ARD['base'])                          # ardoise de la rangée
    import random as _r
    rnd = _r.Random(4)
    x = 15
    while x < 165 * S - 16:                                             # un joint par rangée, toujours au même endroit
        L = rnd.randint(40, 150); b.r(x, Y0 + 9, min(165 * S - 16, x + L), Y0 + 9, ARD['joint']); b.r(x, Y0 + 10, min(165 * S - 16, x + L), Y0 + 10, ARD['joint_clair']); x += L + rnd.randint(14, 40)
    for X in (0, 165 * S - 1):                                          # pas de boulon sur les côtés dans cette zone
        pass
    rangee = b.im.crop((0, Y0, 165 * S, Y1 + 1))
    # le tuyau de la rangée ne doit pas porter d'embouts : on le redessine en continu
    rr = Planche(); rr.im.paste(rangee, (0, 0)); C = 15 * S + 1
    for k, c in enumerate([EXP['trait'], EXP['clair'], EXP['clair'], EXP['base'], EXP['mi'], EXP['sombre'], EXP['trait']]):
        rr.r(C - 3 + k, 0, C - 3 + k, 66 - 1, c)
    rr.r(C - 7, 0, C + 7, 5, (0, 0, 0, 0)) if False else None
    # bandes de cadre gauche/droite sans boulon : on recopie une colonne de bande « propre » sur toute la hauteur
    propre = b.im.crop((0, 100 * S, 165 * S, 100 * S + 1))              # rangée de cadre sans boulon (y 100)
    for yy in range(66):
        for X in list(range(0, 15)) + list(range(165 * S - 15, 165 * S)):
            rr.im.putpixel((X, yy), propre.getpixel((X, 0)))
    # grille d'aération à droite des champs, au pas de 6 texels (66 = 11 x 6 : elle se raccorde d'une rangée à l'autre)
    for Y in range(2, 66, 6):
        rr.r(149 * S, Y, 157 * S - 1, Y + 1, ARD['noir']); rr.r(149 * S, Y + 2, 157 * S - 1, Y + 2, hx('454a57'))
    rangee = rr.im.crop((0, 0, 165 * S, 66))
    for k in range(5): p.im.paste(rangee, (0, (16 + 22 * k) * S))
    # tuyau : bride à l'entrée, sous le bandeau du titre, et à la sortie, au-dessus du plateau
    for Y in (15 * S,):                                                # bride d'entrée du tuyau, sous le titre
        C = 15 * S + 1
        p.r(C - 6, Y, C + 6, Y + 5, EXP['trait']); p.r(C - 5, Y + 1, C + 5, Y + 4, EXP['base'])
        p.r(C - 5, Y + 1, C + 5, Y + 1, EXP['clair']); p.r(C - 5, Y + 4, C + 5, Y + 4, EXP['mi']); p.rivet(C, Y + 2)
    # plateau du bas centré sur le bouton de Create (137-154) : de 408 à 467 texels
    p.socle(0, 0, 0, 0, texels=(5 * S, 408, 160 * S - 1, 467))
    # --- les lignes (sur la planche, à leur place d'origine) : fond de rangée + champs / emplacements + repère sur le tuyau
    A, B_, C_ = (30, 56), (88, 28), (118, 28)
    def ligne(y, champs, vides, repere):
        p.im.paste(rangee, (0, y * S))
        for (x, w) in champs: p.champ(x, y + 4, w, 18)
        for (x, w) in vides: p.emplacement(x, y + 4, w, 18)
        repere(y)
    def r_instruction(y):                                               # rotation : chevron d'airain sur un collier
        p.voyant_monte(15, y + 12, 'ambre') if False else None
        X, Y = 15 * S + 1, (y + 12) * S + 1
        p.r(X - 8, Y - 8, X + 8, Y + 8, EXP['trait']); p.r(X - 7, Y - 7, X + 7, Y + 7, EXP['base']); p.r(X - 7, Y - 7, X + 6, Y - 7, EXP['clair']); p.r(X - 7, Y + 7, X + 7, Y + 7, EXP['mi'])
        for k in range(5): p.r(X - 4 + k, Y - 3 + k, X + 4 - k, Y - 3 + k, EXP['trait'])
    def r_delai(y):                                                     # attente : petit cadran à aiguilles
        X, Y = 15 * S + 1, (y + 12) * S + 1
        for dy in range(-8, 9):
            for dx in range(-8, 9):
                d = (dx * dx + dy * dy) ** 0.5
                if d <= 8.3: p.im.putpixel((X + dx, Y + dy), EXP['trait'] if d > 7.3 else EXP['clair'] if (d > 5.8 and dx + dy < 0) else EXP['mi'] if d > 5.8 else hx('f3ead6'))
        p.r(X, Y - 4, X, Y, EXP['trait']); p.r(X, Y, X + 3, Y, EXP['trait'])
    def r_fin(y):                                                       # fin : le tuyau s'arrête sur une bride pleine
        X = 15 * S + 1; Y = (y + 12) * S
        p.r(X - 3, Y + 4, X + 3, (y + 22) * S - 1, ARD['base'])
        p.r(X - 7, Y - 2, X + 7, Y + 4, EXP['trait']); p.r(X - 6, Y - 1, X + 6, Y + 3, EXP['base']); p.r(X - 6, Y - 1, X + 6, Y - 1, EXP['clair']); p.r(X - 6, Y + 3, X + 6, Y + 3, EXP['mi']); p.rivet(X, Y + 1)
    def r_vide(y):                                                      # rangée vide : pas de tuyau, sa rainure gravée seulement
        X = 15 * S + 1; Y0, Y1 = y * S, (y + 22) * S - 1
        p.r(X - 3, Y0, X + 3, Y1, ARD['base']); p.r(X - 1, Y0, X - 1, Y1, ARD['ombre']); p.r(X, Y0, X, Y1, ARD['creux']); p.r(X + 1, Y0, X + 1, Y1, hx('454a57'))
    def r_attente(y): p.voyant_monte(15, y + 12, 'rouge')               # attente d'un signal de redstone : voyant rouge
    ligne(16, [A, B_, C_], [], r_instruction)
    ligne(60, [A, B_], [C_], r_delai)
    ligne(82, [A], [B_, C_], r_fin)
    ligne(104, [], [A, B_, C_], r_vide)
    ligne(162, [A], [B_, C_], r_attente)
    # rangées 2 (38) : vide aussi sur le fond
    for yy in (16, 38, 60, 82): pass
    vide = p.im.crop((0, 104 * S, 165 * S, 126 * S))
    p.im.paste(vide, (0, 38 * S))
    return p.im

def _carter_vertical(x, w, h, graine):
    """Carter haut de h px, côtés sans boulon (les morceaux de Create s'empilent : recette ou réassort, puis bas)."""
    v = Planche(256, 256)
    v.carter(x, 0, w, h, graine=graine)
    propre = v.im.crop((0, (h // 2) * S + 1, 256 * S, (h // 2) * S + 2))
    # bande de côté sans boulon : on cherche une rangée sans boulon (les boulons sont tous les 60 texels, à partir de 30)
    Yp = 45
    propre = v.im.crop((0, Yp, 256 * S, Yp + 1))
    for Y in range(15, h * S - 15):
        for X in list(range(x * S, x * S + 15)) + list(range((x + w) * S - 15, (x + w) * S)):
            v.im.putpixel((X, Y), propre.getpixel((X, 0)))
    return v.im

def jauge_usine():
    """Jauge d'usine (Create 6) : recette (32,0 192x96) ou réassort (32,112 192x40), puis bas (32,176 200x64), empilés."""
    p = Planche(base=original('factory_gauge').resize((768, 768), Image.NEAREST))
    for (u, v_, w, h) in ((32, 0, 192, 96), (32, 112, 192, 40), (32, 176, 200, 64)): p.efface(u, v_, w, h)
    V = _carter_vertical(32, 192, 160, 11)
    p.im.paste(V.crop((0, 0, 256 * S, 96 * S)), (0, 0))                         # recette : haut + côtés
    p.im.paste(V.crop((0, 20 * S, 256 * S, 60 * S)), (0, 112 * S))              # réassort : côtés seuls
    p.im.paste(V.crop((0, 96 * S, 256 * S, 160 * S)), (0, 176 * S))             # bas : côtés + bas
    for (u, v_, w, h) in ((0, 96, 256, 16), (0, 152, 256, 24), (0, 240, 256, 16), (0, 0, 32, 96), (224, 0, 32, 256)): pass
    p.plaque_nom(78, 2, 102)                                                    # titre centré en x + 97
    # recette : grille 3x3 sertie, flèche, sortie ; colonne des boutons de Create (x+31) laissée libre ; engrenage gravé
    X0, Y0, X1, Y1 = 95 * S, 23 * S, 161 * S - 1, 89 * S - 1                  # 4 px de marge autour des cases (99-157, 27-85)
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); p.r(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, ARD['ombre'])
    for (X, Y) in ((X0 + 2, Y0 + 2), (X1 - 2, Y0 + 2), (X0 + 2, Y1 - 2), (X1 - 2, Y1 - 2)): p.boulon(X + (1 if X < X1 else -1), Y + (1 if Y < Y1 else -1))
    for j in range(3):
        for i in range(3): p.creux(99 + 20 * i, 27 + 20 * j, 18, 18)
    for k in range(6):                                                           # flèche d'airain vers la sortie
        Xf = 170 * S + k
    fl = Image.new('L', (17 * S, 11 * S)); from PIL import ImageDraw as D; dd = D.Draw(fl)
    dd.polygon([(0, 12), (27, 12), (27, 3), (48, 16), (27, 29), (27, 20), (0, 20)], fill=255)
    for yy in range(fl.height):
        for xx in range(fl.width):
            if fl.getpixel((xx, yy)):
                bord = any(not (0 <= xx + a < fl.width and 0 <= yy + b < fl.height) or not fl.getpixel((xx + a, yy + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                p.im.putpixel((168 * S + xx, 50 * S + yy), EXP['trait'] if bord else EXP['clair'] if yy < 15 else EXP['mi'])
    p.case_riche(191, 47)
    p.engrenage(46, 36, 24, 10); p.engrenage(48, 70, 15, 8)                    # (habillage de la première version, retenu)
    # réassort : la case de l'objet suivi (x+87, y+11), dans un cadre riveté
    p.case_riche(119, 123)
    p.grille(40, 118, 14, 28); p.grille(186, 118, 14, 28)
    # bas : étiquette d'adresse (texte en x+36, 10 de haut), ficelle gravée ; plateau centré sur les boutons (215-232)
    from PIL import Image as I
    et = original('stock_keeper') if False else None
    # étiquette d'adresse qui sort du téléscripteur, dessinée comme un vrai ticket ancien (retour de Liam) : papier vieilli,
    # double filet autour du texte, souche détachable à droite après un pointillé, coins de la souche découpés en quart de rond,
    # petit engrenage tamponné et « No. » imprimé sur la souche. Le texte de Create va de x+36 à x+144 (sheet 68-176).
    p.etiqueteuse_dessus(46, 66, 182, 207, 186, 202, partie='socle', x1_socle=71)   # le socle passe sous l'étiquette
    import random as _rr
    rnd = _rr.Random(3)
    Xa, Ya, Xb, Yb = 56 * S, 186 * S, 198 * S - 1, 202 * S - 1
    # ombre portée de l'étiquette sur l'ardoise et sur le socle (en bas et à droite)
    p.r(Xa + 3, Yb + 1, Xb + 2, Yb + 3, ARD['ombre']); p.r(Xb + 1, Ya + 3, Xb + 3, Yb + 3, ARD['ombre'])
    for X in range(Xa + 3, 71 * S - 1):
        for Y in range(Yb + 1, Yb + 4): c = p.im.getpixel((X, Y)); p.im.putpixel((X, Y), tuple(int(v * 0.7) for v in c[:3]) + (255,))
    PAP = [hx('f3ead6'), hx('efe4cc'), hx('f6eedc')]; BORD = hx('7a6a4a'); FIL = hx('b8a27a')
    fond = p.im.copy()                                                             # l'ardoise derrière (pour les coins découpés)
    for Y in range(Ya, Yb + 1):
        for X in range(Xa, Xb + 1):
            p.im.putpixel((X, Y), PAP[rnd.randint(0, 2)] if rnd.random() < 0.35 else PAP[0])
    p.r(Xa, Ya, Xb, Ya, BORD); p.r(Xa, Yb, Xb, Yb, BORD); p.r(Xb, Ya, Xb, Yb, BORD)
    p.r(Xa, Yb - 1, Xb - 1, Yb - 1, hx('d8ccae'))
    # double filet autour de la zone de texte (66-177 x 187-201)
    for (x0, y0, x1, y1, c) in ((66 * S, Ya + 2, 178 * S, Yb - 2, FIL), (66 * S + 2, Ya + 4, 178 * S - 2, Yb - 4, hx('d8c6a0'))):
        p.r(x0, y0, x1, y0, c); p.r(x0, y1, x1, y1, c); p.r(x1, y0, x1, y1, c)
    # pointillé de la souche
    for Y in range(Ya + 2, Yb - 1, 3): p.r(181 * S, Y, 181 * S, Y + 1, BORD)
    # coins de la souche découpés en quart de rond
    R = 6
    for j in range(R):
        for i in range(R):
            if (i + 0.5) ** 2 + (j + 0.5) ** 2 < R * R:
                for (X, Y) in ((Xb - i, Ya + j), (Xb - i, Yb - j)): p.im.putpixel((X, Y), fond.getpixel((X, Y)))
            elif (i + 0.5) ** 2 + (j + 0.5) ** 2 < (R + 1.2) ** 2:
                for (X, Y) in ((Xb - i, Ya + j), (Xb - i, Yb - j)): p.im.putpixel((X, Y), BORD)
    # souche : « No. » imprimé en rouge, un numéro de ticket dessous (retour de Liam : plus d'engrenage)
    from PIL import ImageFont as _F, ImageDraw as _Dd
    def imprime(t, x, y, taille, c):
        tx = Image.new('L', (60, 16)); _Dd.Draw(tx).text((0, -1), t, font=_F.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', taille), fill=255)
        tx = tx.point(lambda v: 255 if v > 110 else 0)
        for yy in range(tx.height):
            for xx in range(tx.width):
                if tx.getpixel((xx, yy)) and x + xx < Xb - 3: p.im.putpixel((x + xx, y + yy), c)
    # « No. » et numéro : redessinés au pixel par Liam (repris de sa retouche, texel pour texel)
    lt = Image.open('/home/claude/travail/lot5b/liam_souche.png').convert('RGBA')
    for yy in range(lt.height):
        for xx in range(lt.width):
            c = lt.getpixel((xx, yy))
            if c[3]: p.im.putpixel((90 + 440 + xx, 522 + 28 + yy), c)
    # téléscripteur compact, refait : entre le cadre (x 37) et le début du texte (x 68), du haut du morceau (176) au plateau (213)
    # étiqueteuse (refaite de zéro, dans l'esprit des machines de Create), entre le cadre (x 37) et le texte (x 68)
    p.etiqueteuse_dessus(46, 66, 182, 207, 186, 202, partie='dessus')        # vue du dessus, comme l'étiquette posée à plat
    p.socle(0, 0, 0, 0, texels=(37 * S, 639, 219 * S - 1, 704))
    p.case_riche(99, 215); p.champ(127, 216, 30, 16, molette=True)     # (la case de la grenouille, à gauche, est posée par Create quand il y en a une)
    # petite horloge gravée devant le délai de promesse
    X, Y = 92 * S, 224 * S                                                     # (à la place de celle de Create, devant la case)
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            d = (dx * dx + dy * dy) ** 0.5
            if d <= 7.3: p.im.putpixel((X + dx, Y + dy), EXP['trait'] if d > 6.3 else hx('f3ead6') if d < 5 else EXP['base'])
    p.r(X, Y - 4, X, Y, EXP['trait']); p.r(X, Y, X + 3, Y, EXP['trait'])
    return p.im

def _ticket(p, xa, ya, yb, x_souche, xb, graine=3):
    """Étiquette d'adresse en ticket ancien (même dessin que la jauge d'usine) : papier vieilli, ombre, double filet autour
    du texte (jusqu'à x_souche), souche après un pointillé, coins découpés, « No. » et numéro (souche de la jauge)."""
    import random as _rr
    rnd = _rr.Random(graine)
    Xa, Ya, Xb, Yb = xa * S, ya * S, xb * S - 1, yb * S - 1
    PAP = [hx('f3ead6'), hx('efe4cc'), hx('f6eedc')]; BORD = hx('7a6a4a'); FIL = hx('b8a27a')
    fond = p.im.copy()
    p.r(Xa + 3, Yb + 1, Xb + 2, Yb + 3, ARD['ombre']); p.r(Xb + 1, Ya + 3, Xb + 3, Yb + 3, ARD['ombre'])
    for X in range(Xa + 3, 71 * S - 1):
        for Y in range(Yb + 1, Yb + 4): c = fond.getpixel((X, Y)); p.im.putpixel((X, Y), tuple(int(v * 0.7) for v in c[:3]) + (255,))
    fond = p.im.copy()
    for Y in range(Ya, Yb + 1):
        for X in range(Xa, Xb + 1): p.im.putpixel((X, Y), PAP[rnd.randint(0, 2)] if rnd.random() < 0.35 else PAP[0])
    p.r(Xa, Ya, Xb, Ya, BORD); p.r(Xa, Yb, Xb, Yb, BORD); p.r(Xb, Ya, Xb, Yb, BORD); p.r(Xa, Yb - 1, Xb - 1, Yb - 1, hx('d8ccae'))
    xs = x_souche * S
    for (x0, y0, x1, y1, c) in ((66 * S, Ya + 2, xs, Yb - 2, FIL), (66 * S + 2, Ya + 4, xs - 2, Yb - 4, hx('d8c6a0'))):
        p.r(x0, y0, x1, y0, c); p.r(x0, y1, x1, y1, c); p.r(x1, y0, x1, y1, c)
    for Y in range(Ya + 2, Yb - 1, 3): p.r(xs + 3 * S - 3, Y, xs + 3 * S - 3, Y + 1, BORD)
    R = 6
    for j in range(R):
        for i in range(R):
            dd = (i + 0.5) ** 2 + (j + 0.5) ** 2
            for (X, Y) in ((Xb - i, Ya + j), (Xb - i, Yb - j)):
                if dd < R * R: p.im.putpixel((X, Y), fond.getpixel((X, Y)))
                elif dd < (R + 1.2) ** 2: p.im.putpixel((X, Y), BORD)
    # souche : « No. » et numéro, repris de la jauge (même position par rapport au pointillé)
    lt = Image.open('/home/claude/travail/lot5b/liam_souche.png').convert('RGBA')
    ox = xs + 3 * S - 3 - (181 * S) + (90 + 440); oy = Ya - 186 * S + (522 + 28)
    for yy in range(lt.height):
        for xx in range(lt.width):
            c = lt.getpixel((xx, yy))
            if c[3] and c[:3] in ((42, 42, 50), (138, 42, 34)) and ox + xx < Xb - 3: p.im.putpixel((ox + xx, oy + yy), c)

def demandeur():
    """Demandeur de redstone (requester 16,16 232x120, dessiné en x+3) et réglage d'objet de la jauge (16,160 184x88, en x-5)."""
    p = Planche(base=original('requester').resize((768, 768), Image.NEAREST))
    p.efface(16, 16, 232, 120); p.efface(16, 160, 184, 88)
    # ---------- demandeur
    p.carter(17, 16, 222, 120, graine=13)
    p.plaque_nom(79, 18, 102)                                              # titre centré en x + 117 (planche 130)
    X0, Y0, X1, Y1 = 35 * S, 39 * S, 221 * S - 1, 65 * S - 1                # rangée de 9 cases sertie, 4 px de marge
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); p.r(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, ARD['ombre'])
    for (X, Y) in ((X0 + 3, Y0 + 3), (X1 - 3, Y0 + 3), (X0 + 3, Y1 - 3), (X1 - 3, Y1 - 3)): p.boulon(X, Y)
    for i in range(9): p.creux(39 + 20 * i, 43, 18, 18)
    # étiquette d'adresse (texte en x+55 -> planche 68, y 84) sortie de l'étiqueteuse
    p.etiqueteuse_dessus(46, 66, 77, 102, 81, 97, partie='socle', x1_socle=71)
    _ticket(p, 56, 81, 97, 178, 198)
    p.etiqueteuse_dessus(46, 66, 77, 102, 81, 97, partie='dessus')
    p.grille(22, 74, 12, 30); p.engrenage(219, 89, 22, 10)
    # plateau centré sur les boutons (111-128) : 327 à 392 texels
    p.socle(0, 0, 0, 0, texels=(22 * S, 327, 234 * S - 1, 392))
    # ---------- réglage d'objet de la jauge
    p.carter(17, 160, 171, 88, graine=17)
    p.plaque_nom(57, 162, 102)                                             # titre centré en x + 87 (planche 108)
    p.case_riche(94, 187)
    from PIL import Image as _I, ImageDraw as _D
    for (xa, sens) in ((71, 1), (119, -1)):                                 # deux flèches d'airain pointées vers la case, symétriques autour de son centre (103)
        fl = _I.new('L', (16 * S, 11 * S)); dd = _D.Draw(fl)
        pts = [(0, 12), (27, 12), (27, 3), (47, 16), (27, 29), (27, 20), (0, 20)]
        if sens < 0: pts = [(47 - x, y) for (x, y) in pts]
        dd.polygon(pts, fill=255)
        for yy in range(fl.height):
            for xx in range(fl.width):
                if fl.getpixel((xx, yy)):
                    bord = any(not (0 <= xx + a < fl.width and 0 <= yy + b < fl.height) or not fl.getpixel((xx + a, yy + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    p.im.putpixel((xa * S + xx, 190 * S + yy), EXP['trait'] if bord else EXP['clair'] if yy < 15 else EXP['mi'])
    p.engrenage(36, 196, 20, 9); p.engrenage(168, 196, 20, 9)
    # plateau centré sur le bouton (223-240) : 663 à 728 texels
    p.socle(0, 0, 0, 0, texels=(22 * S, 663, 183 * S - 1, 728))
    return p.im

def _ticket_entete(p, xa, ya, xb, yb, graine=7):
    """Étiquette d'adresse dans l'en-tête (le nom du port y est écrit, centré) : ticket en papier vieilli, double filet,
    coins découpés aux deux bouts, deux épingles d'airain. Coordonnées en px d'interface."""
    import random as _rr
    rnd = _rr.Random(graine)
    Xa, Ya, Xb, Yb = xa * S, ya * S, xb * S - 1, yb * S - 1
    PAP = [hx('f3ead6'), hx('efe4cc'), hx('f6eedc')]; BORD = hx('7a6a4a'); FIL = hx('b8a27a')
    fond = p.im.copy()
    for Y in range(Ya, Yb + 1):
        for X in range(Xa, Xb + 1): p.im.putpixel((X, Y), PAP[rnd.randint(0, 2)] if rnd.random() < 0.35 else PAP[0])
    p.r(Xa, Ya, Xb, Ya, BORD); p.r(Xa, Yb, Xb, Yb, BORD); p.r(Xa, Ya, Xa, Yb, BORD); p.r(Xb, Ya, Xb, Yb, BORD)
    p.r(Xa + 1, Yb - 1, Xb - 1, Yb - 1, hx('d8ccae'))
    for (d, c) in ((2, FIL), (4, hx('d8c6a0'))):
        p.r(Xa + d + 6, Ya + d, Xb - d - 6, Ya + d, c); p.r(Xa + d + 6, Yb - d, Xb - d - 6, Yb - d, c)
        p.r(Xa + d + 6, Ya + d, Xa + d + 6, Yb - d, c); p.r(Xb - d - 6, Ya + d, Xb - d - 6, Yb - d, c)
    R = 5
    for j in range(R):
        for i in range(R):
            dd = (i + 0.5) ** 2 + (j + 0.5) ** 2
            for (X, Y) in ((Xa + i, Ya + j), (Xa + i, Yb - j), (Xb - i, Ya + j), (Xb - i, Yb - j)):
                if dd < R * R: p.im.putpixel((X, Y), fond.getpixel((X, Y)))
                elif dd < (R + 1.2) ** 2: p.im.putpixel((X, Y), BORD)
    for X in (Xa + 5, Xb - 5):                                               # épingles d'airain
        Y = (Ya + Yb) // 2
        p.r(X - 1, Y - 1, X + 1, Y + 1, EXP['trait']); p.im.putpixel((X, Y), EXP['clair']); p.im.putpixel((X - 1, Y - 1), EXP['base'])

def _crayon(p, X, Y):
    """Icône « renommer » (13 x 13 px) : crayon en biais, mine graphite, corps à l'encre du texte, virole d'airain, gomme rouge."""
    from PIL import Image as _I, ImageDraw as _D
    K = 8; m = _I.new('RGBA', (39 * K, 39 * K)); d = _D.Draw(m)
    def seg(a, b, w, c): d.line([(a[0] * K, a[1] * K), (b[0] * K, b[1] * K)], fill=c, width=int(w * K))
    seg((7, 32), (11, 28), 7, hx('f3ead6'))                       # bois taillé
    seg((5, 34), (7, 32), 4, hx('2a2a32'))                        # mine
    seg((11, 28), (27, 12), 8, hx('3d3c48'))                      # corps
    seg((12, 25), (26, 11), 2, hx('5a5a6a'))                      # reflet du corps
    seg((27, 12), (30, 9), 8, EXP['base'])                        # virole
    seg((30, 9), (34, 5), 8, hx('c04343'))                        # gomme
    im = m.resize((39, 39), _I.BOX)
    px = im.load()
    for y in range(39):
        for x in range(39):
            if px[x, y][3] >= 128: p.im.putpixel((X + x, Y + y), px[x, y][:3] + (255,))

def grenouille_boite():
    """Grenouille-port et boîte aux lettres : en-têtes (0,0 214x17 et 0,23 214x24) posés au-dessus du fond commun (0,47 220x82)."""
    p = Planche(base=original('frogport_and_mailbox').resize((768, 768), Image.NEAREST))
    p.efface(0, 0, 214, 47); p.efface(0, 47, 220, 82); p.efface(230, 3, 13, 13)
    # en-tête de la grenouille + fond : un carter continu, côtés sans boulon
    V = _carter_vertical(1, 212, 99, 19)
    p.im.paste(V.crop((0, 0, 256 * S, 17 * S)), (0, 0))
    p.im.paste(V.crop((0, 17 * S, 256 * S, 99 * S)), (0, 47 * S))
    # en-tête de la boîte aux lettres : même carter, commencé 9 px plus bas (le drapeau dépasse au-dessus)
    W2 = Planche(256, 256); W2.carter(1, 9, 212, 15 + 82, graine=19)
    Yp = 45
    propre = W2.im.crop((0, Yp, 256 * S, Yp + 1))
    for Y in range(9 * S + 15, 24 * S):
        for X in list(range(3, 3 + 15)) + list(range(213 * S - 15, 213 * S)): W2.im.putpixel((X, Y), propre.getpixel((X, 0)))
    p.im.paste(W2.im.crop((0, 0, 256 * S, 24 * S)), (0, 23 * S))
    # étiquettes d'adresse (texte centré en x + 110, 11 px au-dessus du fond ; crayon 14 px au-dessus)
    _ticket_entete(p, 14, 4, 207, 17, graine=7)
    _ticket_entete(p, 14, 23 + 11, 207, 23 + 24, graine=8)
    # drapeau de la boîte aux lettres : tige d'airain, drapeau rouge émaillé, dressé au-dessus de l'en-tête à droite
    X0 = 199 * S
    p.r(X0, 23 * S, X0 + 3, 33 * S, EXP['trait']); p.r(X0 + 1, 23 * S + 1, X0 + 2, 33 * S, EXP['base'])
    for k in range(13):
        p.r(X0 + 4, 23 * S + 1 + k, X0 + 4 + 22 - k, 23 * S + 1 + k, hx('c04343') if k else hx('520019'))
    p.r(X0 + 4, 23 * S + 1, X0 + 26, 23 * S + 2, hx('e06060')); p.r(X0 + 4, 23 * S + 12, X0 + 14, 23 * S + 13, hx('8a0018'))
    # fond : grille de 2 x 9 cases sertie, engrenages gravés de chaque côté, plateau du bas centré sur les boutons
    X0, Y0, X1, Y1 = 22 * S, 51 * S, 192 * S - 1, 95 * S - 1
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); p.r(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, ARD['ombre'])
    for (X, Y) in ((X0 + 3, Y0 + 3), (X1 - 3, Y0 + 3), (X0 + 3, Y1 - 3), (X1 - 3, Y1 - 3)): p.boulon(X, Y)
    for j in range(2):
        for i in range(9): p.creux(26 + 18 * i, 55 + 18 * j, 18, 18)
    p.engrenage(13, 64, 18, 9); p.engrenage(13, 84, 12, 7); p.engrenage(202, 64, 18, 9); p.engrenage(202, 84, 12, 7)
    p.socle(0, 0, 0, 0, texels=(6 * S, 312, 208 * S - 1, 371))
    _crayon(p, 230 * S, 3 * S)
    return p.im

# ---------------- conversion des écrans restants (même langue : carter, plaque, cases et champs en creux, plateau du bas)
from zones import zones as _zones
def _cases_auto(p, feuille, rect, couleurs=('8b8b8b', 'a3a3a3'), maxi=40):
    """Cases et champs de l'original (remplissage gris) -> creux gravés ; les cases carrées deviennent des cases serties."""
    x, y, w, h = rect
    for (x0, y0, x1, y1) in _zones(feuille, list(couleurs), mini=6):
        if x0 < x or y0 < y or x1 > x + w or y1 > y + h or (x1 - x0) > 200: continue
        X, Y, W, H = x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2
        if abs(W - H) <= 2 and W <= maxi: p.case_riche(X, Y, W, H, ep=3)
        else: p.champ(X, Y, W, H)
def _garde(p, orig, rects):
    """Petits dessins de Create à garder (icônes de touches, trains…) : pixels nets, silhouette adoucie."""
    import sys; sys.path.insert(0, '/home/claude/travail/lot5'); import ftbq
    for (x, y, w, h) in rects:
        c = orig.crop((x, y, x + w, y + h)); bb = c.getbbox()
        if not bb: continue
        hy = ftbq.hybride(c.crop(bb)); p.im.alpha_composite(hy, ((x + bb[0]) * S, (y + bb[1]) * S))
def _socle_bas(p, x, y, w, h):
    """Plateau du bas, centré sur la rangée de boutons de Create (h - 24 à h - 6) et sur la hauteur libre du carter."""
    Y0 = (y + h) * S - 75; Y1 = (y + h) * S - 16
    p.socle(0, 0, 0, 0, texels=(x * S + 15, Y0, (x + w) * S - 16, Y1))

def filtre_colis():
    o = original('filters_2'); p = Planche(base=o.resize((768, 768), Image.NEAREST)); p.efface(0, 0, 218, 79)
    p.carter(0, 0, 210, 79, graine=21); p.plaque_nom(54, 2, 102)                 # titre centré en x + (218 - 8) / 2
    p.creux(6, 17, 200, 34)                                                        # bac de l'adresse
    _cases_auto(p, 'filters_2', (0, 0, 218, 79)); _socle_bas(p, 0, 0, 210, 79)
    return p.im

def assemblage():
    o = original('assemble'); p = Planche(base=o.resize((768, 768), Image.NEAREST)); p.efface(0, 0, 200, 178)
    p.carter(0, 0, 192, 178, graine=23); _ticket_entete(p, 14, 2, 178, 14, graine=9)   # nom de la gare : champ à l'encre sombre
    p.creux(6, 15, 180, 13, fond=hx('2e323b'))                                     # bandeau du nom du train
    p.creux(6, 30, 180, 117)                                                       # vue du train
    p.creux(22, 43, 148, 96, fond=ARD['noir'])
    p.filet_creux(26, 166, 55)
    p.grille(8, 34, 10, 40); p.grille(174, 34, 10, 40)
    _socle_bas(p, 0, 0, 192, 178)
    # bulle d'information (1,179 haut 150x18 ; 1,198 milieu 1 px étiré ; 1,200 bas 150x4 ; 152,179 pointe 8x6)
    for r_ in ((1, 179, 150, 18), (1, 198, 150, 1), (1, 200, 150, 4), (152, 179, 8, 6)): p.efface(*r_)
    X0, X1 = 1 * S, 151 * S - 1
    def cotes(Y0, Y1):
        p.r(X0, Y0, X1, Y1, hx('2a2e37')); p.r(X0, Y0, X0, Y1, EXP['trait']); p.r(X1, Y0, X1, Y1, EXP['trait'])
        p.r(X0 + 1, Y0, X0 + 1, Y1, EXP['base']); p.r(X1 - 1, Y0, X1 - 1, Y1, EXP['mi'])
    cotes(179 * S, 197 * S - 1); p.r(X0, 179 * S, X1, 179 * S, EXP['trait']); p.r(X0 + 1, 179 * S + 1, X1 - 1, 179 * S + 1, EXP['clair'])
    p.filet_creux(4, 148, 192)
    cotes(198 * S, 199 * S - 1)
    cotes(200 * S, 204 * S - 1); p.r(X0, 204 * S - 1, X1, 204 * S - 1, EXP['trait']); p.r(X0 + 1, 204 * S - 2, X1 - 1, 204 * S - 2, EXP['mi'])
    for k in range(6 * S):
        w = max(0, (6 * S - k) * 8 * S // (6 * S) // 2)
        p.r(156 * S - w, 179 * S + k, 156 * S + w, 179 * S + k, hx('2a2e37') if 0 < k < 6 * S - 1 else EXP['trait'])
    return p.im

def telecommande_plan():
    o = original('curiosities_2'); p = Planche(base=o.resize((768, 768), Image.NEAREST)); p.efface(0, 0, 179, 109); p.efface(0, 109, 179, 109)
    # télécommande liée (0,0 179x109) : deux rangées de touches, icône de chaque touche gardée au-dessus de ses cases
    p.carter(0, 0, 171, 109, graine=25); p.plaque_nom(11, 2, 102)                  # titre à gauche, en x + 15
    p.creux(6, 15, 102, 61); p.creux(110, 15, 55, 61)
    _cases_auto(p, 'curiosities_2', (0, 0, 179, 109))
    _garde(p, o, [(11 + 24 * k, 23, 18, 9) for k in range(4)] + [(118 + 24 * k, 23, 18, 9) for k in range(2)])
    _socle_bas(p, 0, 0, 171, 109)
    # plan (0,109 179x109) : grille 3x3 sertie, flèche d'airain, cases de résultat
    p.carter(0, 109, 171, 109, graine=27); p.plaque_nom(11, 111, 102)
    X0, Y0, X1, Y1 = 24 * S, 125 * S, 87 * S - 1, 187 * S - 1
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); p.r(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, ARD['ombre'])
    for (X, Y) in ((X0 + 3, Y0 + 3), (X1 - 3, Y0 + 3), (X0 + 3, Y1 - 3), (X1 - 3, Y1 - 3)): p.boulon(X, Y)
    _cases_auto(p, 'curiosities_2', (0, 109, 179, 109))
    from PIL import Image as _I, ImageDraw as _D
    fl = _I.new('L', (16 * S, 11 * S)); _D.Draw(fl).polygon([(0, 12), (27, 12), (27, 3), (47, 16), (27, 29), (27, 20), (0, 20)], fill=255)
    for yy in range(fl.height):
        for xx in range(fl.width):
            if fl.getpixel((xx, yy)):
                bord = any(not (0 <= xx + a < fl.width and 0 <= yy + b < fl.height) or not fl.getpixel((xx + a, yy + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                p.im.putpixel((95 * S + xx, 150 * S + yy), EXP['trait'] if bord else EXP['clair'] if yy < 15 else EXP['mi'])
    _socle_bas(p, 0, 109, 171, 109)
    return p.im

def _sertie(p, x0, y0, x1, y1):
    X0, Y0, X1, Y1 = x0 * S, y0 * S, x1 * S - 1, y1 * S - 1
    p.r(X0, Y0, X1, Y1, EXP['trait']); p.r(X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, EXP['mi']); p.r(X0 + 1, Y0 + 1, X1 - 2, Y1 - 2, EXP['clair'])
    p.r(X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, EXP['base']); p.r(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, ARD['ombre'])
    for (X, Y) in ((X0 + 3, Y0 + 3), (X1 - 3, Y0 + 3), (X0 + 3, Y1 - 3), (X1 - 3, Y1 - 3)): p.boulon(X, Y)

def _etiquette_claire(p, x0, y0, x1, y1, graine=1, oeillet=True):
    """Petite étiquette de papier vieilli (catégories du gardien) : bord brun, coins gauches coupés, œillet d'airain."""
    import random as _rr
    rnd = _rr.Random(graine); PAP = [hx('f3ead6'), hx('efe4cc'), hx('f6eedc')]; BORD = hx('7a6a4a')
    X0, Y0, X1, Y1 = x0 * S, y0 * S, x1 * S - 1, y1 * S - 1
    for Y in range(Y0, Y1 + 1):
        for X in range(X0, X1 + 1): p.im.putpixel((X, Y), PAP[rnd.randint(0, 2)] if rnd.random() < 0.35 else PAP[0])
    p.r(X0, Y0, X1, Y0, BORD); p.r(X0, Y1, X1, Y1, BORD); p.r(X1, Y0, X1, Y1, BORD); p.r(X0, Y0, X0, Y1, BORD); p.r(X0 + 1, Y1 - 1, X1 - 1, Y1 - 1, hx('d8ccae'))
    for k in range(4):                                                # coins gauches coupés en biseau
        p.r(X0, Y0 + k, X0 + 3 - k, Y0 + k, (0, 0, 0, 0)); p.r(X0, Y1 - k, X0 + 3 - k, Y1 - k, (0, 0, 0, 0))
        p.im.putpixel((X0 + 4 - k, Y0 + k), BORD); p.im.putpixel((X0 + 4 - k, Y1 - k), BORD)
    if oeillet:
        Y = (Y0 + Y1) // 2; X = X0 + 7
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                d = abs(dx) + abs(dy)
                if d <= 3: p.im.putpixel((X + dx, Y + dy), EXP['trait'] if d == 3 or (abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2) else ARD['ombre'] if d == 0 else EXP['base'])

def categories_gardien():
    o = original('stock_keeper_categories'); p = Planche(base=o.resize((768, 768), Image.NEAREST))
    for r in ((32, 0, 192, 18), (32, 32, 192, 20), (32, 79, 200, 33), (32, 208, 192, 38), (38, 127, 27, 18), (38, 159, 171, 18), (211, 160, 8, 17), (238, 86, 14, 20)): p.efface(*r)
    V = _carter_vertical(32, 192, 109, 29)                             # en-tête 18 + rangées + bas 33
    p.im.paste(V.crop((0, 0, 256 * S, 18 * S)), (0, 0))
    p.im.paste(V.crop((0, 18 * S, 256 * S, 38 * S)), (0, 32 * S))
    p.im.paste(V.crop((0, 76 * S, 256 * S, 109 * S)), (0, 79 * S))
    p.im.paste(V.crop((0, 30 * S, 256 * S, 68 * S)), (0, 208 * S))
    p.plaque_nom(77, 2, 102)                                          # titre centré sur la fenêtre (192 / 2)
    p.socle(0, 0, 0, 0, texels=(37 * S, 261, 219 * S - 1, 320))
    _cases_auto(p, 'stock_keeper_categories', (32, 208, 192, 38))
    # étiquettes : nouvelle catégorie (+ rouge), entrée (✕ rouge), flèches de rang d'airain, bulle
    _etiquette_claire(p, 39, 128, 64, 144, graine=2)
    for k in range(-2, 3): p.r(56 * S + k, 136 * S - 7, 56 * S + k, 136 * S + 5, hx('8a2a22')) if False else None
    p.r(57 * S - 1, 133 * S, 57 * S + 1, 139 * S - 1, hx('8a2a22')); p.r(54 * S, 136 * S - 1, 60 * S - 1, 136 * S + 1, hx('8a2a22'))
    _etiquette_claire(p, 39, 160, 208, 176, graine=4)
    for k in range(7):
        p.im.putpixel((200 * S + k, 165 * S + k), hx('8a2a22')); p.im.putpixel((200 * S + 6 - k, 165 * S + k), hx('8a2a22'))
        p.im.putpixel((200 * S + k + 1, 165 * S + k), hx('8a2a22')); p.im.putpixel((200 * S + 7 - k, 165 * S + k), hx('8a2a22'))
    for (y, haut) in ((160, True), (169, False)):
        X, Y = 215 * S, y * S + 4
        for k in range(6):
            yy = Y + (k if haut else 6 - k) - 3
            p.r(X - k, yy, X + k, yy, EXP['trait'] if k in (0, 5) else EXP['base'] if haut else EXP['mi'])
    X0, Y0 = 238 * S, 86 * S
    for k in range(21):                                                # bulle : pointe de papier vers la gauche
        p.r(X0 + 41 - k * 2, Y0 + 10 + k // 2, X0 + 41, Y0 + 10 + k // 2, hx('f3ead6')) if k < 20 else None
    return p.im

def horaire_gare():
    o = original('schedule_2'); p = Planche(base=o.resize((768, 768), Image.NEAREST))
    p.efface(0, 0, 256, 89); p.efface(0, 111, 200, 127); p.efface(55, 47, 32, 18)
    # éditeur d'horaire (0,0 256x89)
    p.carter(0, 0, 256, 89, graine=31); p.plaque_nom(77, 2, 102)
    p.creux(36, 15, 184, 64)
    _cases_auto(p, 'schedule_2', (0, 0, 256, 89)); p.filet_creux(56, 196, 63)
    p.grille(8, 18, 22, 58); p.grille(226, 18, 22, 58)
    p.creux(55, 47, 32, 18)                                            # case supplémentaire (posée par Create)
    # gare (0,111 200x127) : même dessin que l'assemblage
    p.carter(0, 111, 192, 127, graine=33); _ticket_entete(p, 14, 113, 178, 125, graine=10)
    p.creux(6, 126, 180, 13, fond=hx('2e323b')); p.creux(6, 141, 180, 64); p.creux(22, 150, 148, 48, fond=ARD['noir'])
    _socle_bas(p, 0, 111, 192, 127)
    _cases_auto(p, 'schedule_2', (0, 205, 200, 33))
    return p.im

def curiosites():
    o = original('curiosities'); p = Planche(base=o.resize((768, 768), Image.NEAREST))
    p.efface(0, 0, 234, 103); p.efface(0, 131, 188, 101)
    # façonneur (0,0 234x103) : réglages à gauche, grille du motif à droite
    p.carter(0, 0, 226, 103, graine=35); p.plaque_nom(62, 2, 102)
    p.creux(6, 15, 141, 48); p.creux(150, 15, 70, 48)
    _cases_auto(p, 'curiosities', (0, 0, 234, 103), maxi=40)
    _sertie(p, 154, 17, 216, 61)                                        # grille du motif, 3 x 2 cases
    for j in range(2):
        for i in range(3): p.creux(158 + 18 * i, 21 + 18 * j, 18, 18)
    _socle_bas(p, 0, 0, 226, 103)
    # baguette de symétrie (0,131 188x101)
    p.carter(0, 131, 180, 101, graine=37); p.plaque_nom(43, 133, 102)
    p.creux(6, 146, 168, 50)
    _cases_auto(p, 'curiosities', (0, 131, 188, 101))
    # l'icône de rotation de la 2e case, gardée de Create, sur fond d'ardoise
    ic = o.crop((22, 177, 38, 193)); px = ic.load()
    for yy in range(16):
        for xx in range(16):
            if px[xx, yy][:3] in ((0x8b, 0x8b, 0x8b), (0xa3, 0xa3, 0xa3)): px[xx, yy] = (0, 0, 0, 0)
    import sys; sys.path.insert(0, '/home/claude/travail/lot5'); import ftbq
    bb = ic.getbbox()
    if bb: p.im.alpha_composite(ftbq.hybride(ic.crop(bb)), ((22 + bb[0]) * S, (177 + bb[1]) * S))
    _socle_bas(p, 0, 131, 180, 101)
    return p.im
