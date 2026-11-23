# Lot 7 : laitier et brique réfractaire (objets 16 x 16), remontés au niveau des lingots d'airain du mod
from PIL import Image, ImageDraw
def hx(s, a=255): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (a,)

def grille(lignes, pal):
    im = Image.new('RGBA', (16, 16))
    for y, l in enumerate(lignes):
        for x, c in enumerate(l):
            if c != '.': im.putpixel((x, y), pal[c])
    return im

def laitier():
    """Laitier : scorie vitreuse sortie du haut fourneau. Bloc poreux gris-noir, facettes éclairées en haut à gauche,
    bulles (creux sombres bordés de clair dessous), reflets vitreux bleu-violet, une fissure encore rougeoyante."""
    pal = dict(O=hx('16141a'), D=hx('36333b'), M=hx('4b4650'), L=hx('67616c'), H=hx('8d8592'), G=hx('7f93b0'), V=hx('9a86b4'),
               h=hx('0f0e12'), r=hx('7a7480'), E=hx('d8641e'), Y=hx('ffb85a'))
    return grille([
        '................',
        '................',
        '......OOOOO.....',
        '....OOLHHHLOO...',
        '...OLHGHLLMMDO..',
        '..OLHVLhMLMMDDO.',
        '..OLGLMrLMMDhDO.',
        '.OMLLMLMMMDDrDO.',
        '.OMLhMMLMDDDDDDO',
        '.OMLrMMDEYDDDhDO',
        '.ODMMMDDDEDDDrDO',
        '..ODMDhDDDDDDDO.',
        '..OODDrDDDDDOO..',
        '....OODDDDOO....',
        '......OOOO......',
        '................'], pal)

def brique(variante='rouge'):
    """Brique réfractaire : silhouette de brique d'origine (barre de trois quarts). Pour ne pas la confondre avec la brique
    vanilla : teinte du bloc (rouge sombre) ou chamotte (crème), bout noirci par le feu, marque de briquetier imprimée."""
    T = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/fire_brick.png'
    o = Image.open(T).convert('RGBA'); im = o.copy()
    teintes = {'rouge': {'eedebc': '8e4636', 'dcc6a0': '3a1a16', 'c4aa84': '652c26', 'a88c6c': '53221f', '76604c': '2e1412', '46362c': '1c0b0c'},
               'creme': {'eedebc': 'e6d2a8', 'dcc6a0': '4a3a2e', 'c4aa84': 'bfa078', 'a88c6c': '9c7e5c', '76604c': '5a4636', '46362c': '2a2018'}}[variante]
    for y in range(16):
        for x in range(16):
            c = o.getpixel((x, y))
            if c[3]:
                k = '%02x%02x%02x' % c[:3]
                if k == 'dcc6a0' and x >= 5: k = 'eedebc'                       # le reflet du haut n'est pas le bout : teinte du dessus
                im.putpixel((x, y), hx(teintes[k]))
    # bout noirci par le feu : le bout (colonne de gauche) passe au noir de suie, qui mord un peu sur le dessus
    suie = hx('2a1612') if variante == 'rouge' else hx('3e3028')
    for (x, y) in ((1, 6), (2, 6), (1, 7)): im.putpixel((x, y), suie)
    # marque de briquetier imprimée au milieu du dessus : creux sombre, arête claire dessous
    creux, arete = (hx('5e2a22'), hx('a85a44')) if variante == 'rouge' else (hx('9c7e5c'), hx('f4e6c4'))
    for (x, y) in ((7, 6), (8, 6), (9, 5)): im.putpixel((x, y), creux)
    for (x, y) in ((7, 7), (8, 7), (9, 6)): im.putpixel((x, y), arete)
    return im

def grains(im):
    """Grains de chamotte (clairs) sur le dessus, pores (sombres) sur la face : posés à la main après lecture des faces."""
    return im

if __name__ == '__main__':
    laitier().save('/tmp/nv/slag.png'); brique().save('/tmp/nv/brick.png')

def brique_classique():
    """Brique de la deuxième maquette (jugée « bien mieux ») : silhouette d'origine, teintes de terre cuite, deux grains, un pore."""
    T = '/home/claude/travail/lot7/origine/fire_brick_item.png'          # la brique crème d'origine
    o = Image.open(T).convert('RGBA'); im = o.copy()
    t = {'eedebc': 'bc6a50', 'dcc6a0': '9a4b39', 'c4aa84': '7a3a2e', 'a88c6c': '652c26', '76604c': '4a1f1c', '46362c': '1c0b0c'}
    for y in range(16):
        for x in range(16):
            c = o.getpixel((x, y))
            if c[3]: im.putpixel((x, y), hx(t['%02x%02x%02x' % c[:3]]))
    for (x, y) in ((5, 7), (10, 5)): im.putpixel((x, y), hx('d08a6c'))
    im.putpixel((10, 10), hx('5a2622'))
    return im
