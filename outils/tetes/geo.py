# Géométrie des trois coiffes (coordonnées du modèle Minecraft : y vers le bas, z min = devant). Boîtes : (x, y, z, w, h, d, couleur)
import math
NETH, NETH2 = (66, 60, 64), (44, 40, 44)
ARG, ARG2 = (220, 222, 236), (168, 170, 190)
LAV, PALE = (186, 156, 255), (232, 218, 255)
VIO, VIO2 = (122, 84, 190), (86, 48, 140)
RUN = (55, 50, 65)
NOIR = (14, 11, 21)

def anneau(y, h, r_in, ep, col, col_cote=None):
    """cercle carré autour de la tête (r_in = demi-largeur intérieure)."""
    a, b = -r_in - ep, r_in
    return [(a, y, a, 2 * (r_in + ep), h, ep, col), (a, y, b, 2 * (r_in + ep), h, ep, col),
            (a, y, -r_in, ep, h, 2 * r_in, col_cote or col), (b, y, -r_in, ep, h, 2 * r_in, col_cote or col)]

def diademe_casque():
    B = [(-5, -9, -5, 10, 9, 10, NETH)]                       # casque de netherite (vanilla gonflé de 1)
    B += anneau(-6.9, 0.8, 5, 0.5, ARG, ARG2)
    B += [(-1.5, -8.6, -5.9, 3, 2.2, 0.4, ARG), (-1, -8.3, -6.1, 2, 1.6, 0.4, LAV), (-0.5, -9.6, -5.8, 1, 1, 0.4, PALE)]
    for x, z in ((-5.6, -2.5), (-5.6, 1.5), (5.1, -2.5), (5.1, 1.5)):
        B.append((x, -8.3, z, 0.5, 1.4, 1, VIO))
    return B

def tiare():
    B = anneau(-7.2, 1.4, 4.1, 0.5, RUN)
    B += anneau(-7.5, 0.3, 4.1, 0.5, ARG, ARG2)               # liseré d'argent
    for x in (-3, -1.5, 1, 2.5):                               # rivets lavande sur le devant
        B.append((x - 0.25, -6.7, -4.75, 0.5, 0.5, 0.2, LAV))
    # plaque frontale en gradins
    B += [(-2.6, -8.7, -4.6, 5.2, 1.5, 0.5, RUN), (-1.6, -9.8, -4.6, 3.2, 1.1, 0.5, RUN), (-0.7, -10.9, -4.6, 1.4, 1.1, 0.5, RUN),
          (-0.3, -11.5, -4.6, 0.6, 0.6, 0.5, ARG)]
    B += [(-2.6, -8.9, -4.65, 1, 0.2, 0.55, ARG), (1.6, -8.9, -4.65, 1, 0.2, 0.55, ARG), (-1.6, -10, -4.65, 0.9, 0.2, 0.55, ARG), (0.7, -10, -4.65, 0.9, 0.2, 0.55, ARG)]
    B += [(-0.8, -9.6, -4.85, 1.6, 2, 0.3, LAV), (-0.4, -9.2, -4.95, 0.8, 1.2, 0.2, PALE)]   # gemme
    B += [(-2.2, -8.2, -4.7, 0.4, 0.9, 0.2, VIO), (1.8, -8.2, -4.7, 0.4, 0.9, 0.2, VIO)]       # runes
    for x in (-4.6, 4.1):                                        # pointes latérales
        B += [(x, -8.4, -0.75, 0.5, 1.2, 1.5, RUN), (x, -9.0, -0.25, 0.5, 0.6, 0.5, LAV)]
    return B

def nimbe():
    B = anneau(-6.6, 0.7, 4.1, 0.4, NOIR)
    B += anneau(-6.3, 0.2, 4.1, 0.45, VIO2)
    def branche(x, z, h, cote=False):
        w, d = (0.4, 0.5) if cote else (0.5, 0.4)
        return [(x, -6.6 - h, z, w, h, d, VIO2), (x, -6.6 - h - 0.5, z, w, 0.5, d, LAV)]
    for x, h in ((-3.6, 1.2), (-2.5, 2.0), (-1.4, 1.4), (0.9, 1.4), (2.0, 2.0), (3.1, 1.2)):
        B += branche(x, -4.5, h)
    for z, h in ((-2.8, 1.2), (-1.2, 1.8), (0.6, 1.2), (2.2, 1.8)):
        B += branche(-4.5, z, h, True) + branche(4.1, z, h, True)
    for x, h in ((-3, 1.4), (-0.25, 2.2), (2.5, 1.4)):
        B += branche(x, 4.1, h)
    # branche centrale et gemme
    B += [(-0.25, -11.2, -4.5, 0.5, 4.6, 0.4, VIO2), (-0.75, -10.6, -4.5, 0.5, 0.4, 0.4, VIO2), (0.25, -10.6, -4.5, 0.5, 0.4, 0.4, VIO2),
          (-1.1, -11.4, -4.5, 0.4, 0.8, 0.4, LAV), (0.7, -11.4, -4.5, 0.4, 0.8, 0.4, LAV), (-0.25, -11.8, -4.5, 0.5, 0.6, 0.4, PALE)]
    B += [(-0.9, -9.4, -4.75, 1.8, 1.8, 0.4, LAV), (-0.5, -9.0, -4.95, 1.0, 1.0, 0.3, PALE)]
    return B

def halo():
    """anneau lumineux (rendu en pleine lumière à part)."""
    B = []
    for i in range(-12, 12):
        for k in range(-12, 12):
            r = math.hypot(i / 2 + 0.25, k / 2 + 0.25)
            if 4.8 <= r <= 5.6: B.append((i / 2, -12.8, k / 2, 0.5, 0.4, 0.5, PALE + (1,)))
    return B
