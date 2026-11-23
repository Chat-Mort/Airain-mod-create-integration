# Lot 7 : couleur des briques réfractaires (objet, bloc et haut fourneau). Les pixels de brique (rouge sombre, peu saturés)
# changent de teinte en gardant leur clarté relative ; les bandes d'airain, l'émail de l'emblème et les flammes ne bougent pas.
import colorsys
from PIL import Image
import objets
B = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
FOUR = ['fire_bricks', 'fire_bricks_corner', 'blast_furnace_airain', 'blast_furnace_emblem', 'blast_furnace_hopper_side', 'blast_furnace_hopper_side_corner',
        'blast_furnace_hopper_top', 'blast_furnace_hopper_top_lit', 'blast_furnace_plinth', 'blast_furnace_plinth_corner', 'blast_furnace_taphole',
        'blast_furnace_taphole_lit', 'blast_furnace_top_sooty', 'blast_furnace_tuyere']
VARIANTES = {   # teinte, saturation, clarté = a + b x clarté d'origine
    'ocre': (0.095, 0.36, 0.10, 1.55), 'anthracite': (0.61, 0.09, 0.06, 1.0), 'ivoire': (0.11, 0.26, 0.20, 1.85), 'brun': (0.96, 0.17, 0.04, 1.05)}

PALETTE = set(c[:3] for c in Image.open(B + 'fire_bricks.png').convert('RGBA').getdata())
def est_brique(c):
    # rouge sombre peu saturé ; les noirs profonds (fond du trou de coulée, de la tuyère) restent noirs, sauf le mortier du bloc
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in c[:3]])
    return c[3] > 0 and (h > 0.95 or h < 0.035) and s < 0.5 and l < 0.36 and (c[:3] in PALETTE or l >= 0.1)

def teinte(c, v, objet=False):
    H, Sa, a, b = VARIANTES[v]; h, l, s = colorsys.rgb_to_hls(*[x / 255 for x in c[:3]])
    if objet: l = l * 0.72
    r, g, bb = colorsys.hls_to_rgb(H, min(0.93, a + b * l), Sa)
    return (round(r * 255), round(g * 255), round(bb * 255), c[3])

def bloc(nom, v):
    im = Image.open(B + nom + '.png').convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if est_brique(px[x, y]): px[x, y] = teinte(px[x, y], v)
    return im

def objet(v):
    """Brique classique (silhouette d'origine, faces nettes, deux grains, un pore) : on part de la brique rouge validée
    (deuxième maquette) et on lui donne la teinte choisie, avec la même règle que le bloc."""
    im = objets.brique_classique(); px = im.load()
    for y in range(16):
        for x in range(16):
            if px[x, y][3]: px[x, y] = teinte(px[x, y], v, objet=True)
    return im
