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
