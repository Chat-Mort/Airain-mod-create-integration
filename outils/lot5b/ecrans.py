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
