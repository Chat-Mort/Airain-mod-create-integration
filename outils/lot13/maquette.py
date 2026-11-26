import sys; sys.path.insert(0, '.')
from ecran import *
import math
blanc, noir, air, cuivre = tex('white_marble_0'), tex('black_marble_0'), tex('airain_block'), tex('cut_airain')
def damier(x, z):
    if x in (0, 11) or z in (0, 11): return air                                  # bordure
    return blanc if ((x - 1) // 2 + (z - 1) // 2) % 2 == 0 else noir

def creation():
    e = Ecran(264, 276)
    for i, ic in enumerate(ICONES): e.onglet(6 + i * 28, 2, ic, i == 0)
    e.panneau(0, 24, 264, 250)
    e.texte("Tiler's Table", 186, 9, OR, True)
    for (t, x, w, a) in (("Floor", 8, 22, True), ("Wall", 31, 22, False), ("Ceiling", 54, 30, False)): e.bouton(t, x, 31, w, 12, a)
    e.creux(8, 46, 76, 108)
    for i, t in enumerate(("Checkerboard", "Herringbone", "Offset pavers", "Diamonds", "Stripes", "Diagonals", "Rosette", "Basketweave", "Bordered")):
        if i == 0: e.R(9, 47 + i * 11, 74, 11, (90, 60, 40))
        e.texte(t, 11, 48 + i * 11, OR if i == 0 else BLANC)
    e.creux(88, 31, 100, 100)
    e.im.alpha_composite(motif_grille(12, damier).resize((96 * S, 96 * S), Image.NEAREST), (90 * S, 33 * S))
    for k, (t, img) in enumerate((("Color A", blanc), ("Color B", noir), ("Border", air), ("Accent", None))):
        y = 31 + k * 24
        e.texte(t, 194, y, BLANC); e.case(240, y - 1)
        if img is not None: e.objet(img, 241, y)
    for k, (t, v) in enumerate((("Cell size", "2"), ("Border width", "1"))):
        y = 136 + k * 14
        e.texte(t, 88, y + 1, BLANC); e.texte(v, 152, y + 1, OR, True); e.bouton("-", 162, y, 12); e.bouton("+", 176, y, 12)
    e.texte("Name", 8, 157, (190, 190, 190))
    e.creux(8, 166, 76, 14); e.texte("Hall floor", 11, 168, BLANC)
    e.case(194, 133); e.objet(carton(), 195, 134)
    e.texte("→", 215, 136, OR, True)
    e.case(228, 133); e.objet(carton([hx('e8e4dc'), hx('2c2a30')]), 229, 134)
    e.bouton("Print", 194, 156, 52, 14, True)
    e.inventaire(51, 190)
    return e.im

def rangement():
    e = Ecran(264, 276)
    for i, ic in enumerate(ICONES): e.onglet(6 + i * 28, 2, ic, i == 1)
    e.panneau(0, 24, 264, 250)
    e.texte("Floors", 8, 31, OR, True)
    noms = ["Hall floor", "Herringbone", "Forge tiles", "Diamonds", "Courtyard"]
    for r in range(4):
        for c in range(9):
            x, y = 51 + c * 18, 46 + r * 18
            e.case(x, y)
            if r * 9 + c < 5: e.objet(carton([hx('e8e4dc'), hx('2c2a30')] if c % 2 == 0 else [hx('e1ba6e'), hx('704425')]), x + 1, y + 1)
    # bulle d'aide sur le premier carton : nom, taille, aperçu miniature
    bx, by = 70, 60
    e.R(bx, by, 104, 92, (16, 6, 22)); e.R(bx + 1, by + 1, 102, 90, (40, 10, 60)); e.R(bx + 2, by + 2, 100, 88, (16, 6, 22))
    e.texte("Hall floor", bx + 5, by + 4, BLANC); e.texte("Floor 12 × 1 × 12", bx + 5, by + 14, (170, 170, 170))
    e.im.alpha_composite(motif_grille(12, damier).resize((60 * S, 60 * S), Image.NEAREST), ((bx + 5) * S, (by + 26) * S))
    e.inventaire(51, 190)
    return e.im

def apercu():
    """Fenêtre d'aperçu (clic droit dans le vide, carton en main) : le motif répété 3 x 3, vu en 3D, à tourner."""
    from proj import rendre, boite
    U = {k: (0, 0, 16, 16) for k in ('north', 'south', 'east', 'west', 'up', 'down')}
    TX = {'b': np.array(blanc), 'n': np.array(noir), 'a': np.array(air)}
    el = []
    N = 12
    for z in range(N):
        for x in range(N):
            v = damier(x, z); t = 'b' if v is blanc else 'n' if v is noir else 'a'
            el.append(boite([x * 16 - N * 8 + 8, 0, z * 16 - N * 8 + 8], [x * 16 + 16 - N * 8 + 8, 16, z * 16 + 16 - N * 8 + 8], t, uvs=U))
    r = rendre(el, TX, {'vue': [38, 30], 'scale': [0.09] * 3}, 210 * S // 1)
    e = Ecran(230, 190)
    e.panneau(0, 0, 230, 190)
    e.texte("Hall floor", 8, 6, OR, True); e.texte("Floor 12 × 1 × 12 · 144 blocks", 8, 17, (190, 190, 190))
    e.creux(8, 28, 214, 136)
    e.im.alpha_composite(r.crop((0, 40 * S, 210 * S, 172 * S)), (10 * S, 30 * S))
    e.bouton("<", 8, 170, 16, 14); e.bouton(">", 206, 170, 16, 14)
    e.texte("Drag to turn · scroll to zoom", 58, 172, (170, 170, 170))
    return e.im

if __name__ == '__main__':
    from PIL import ImageFont
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
    FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    a, b, c = creation(), rangement(), apercu()
    W = Image.new('RGBA', (a.width + b.width + 60, a.height + c.height + 90), (52, 54, 60, 255)); d = ImageDraw.Draw(W)
    d.text((20, 10), "Table du carreleur — onglet Création (gauche), onglet Sols (droite) ; en bas, la fenêtre d'aperçu du carton", font=F, fill=(240, 220, 160))
    W.alpha_composite(a, (20, 40)); W.alpha_composite(b, (a.width + 40, 40)); W.alpha_composite(c, (20, a.height + 60))
    notes = ["Création : type (sol, mur, plafond), motif tout fait, blocs des rôles pris dans l'inventaire,",
             "réglages + / −, aperçu en direct, nom ; un carton vierge en entrée, « Print » donne le carton imprimé.",
             "Sols / Murs / Plafonds : 4 rangées de 9 cartons par onglet, rangés selon leur type ;",
             "bulle d'aide : nom, taille, aperçu miniature. Les cartons pris à la main sur un échantillon y vont aussi.",
             "La table est partagée : chacun retrouve les cartons de l'autre ; elle garde son contenu quand on la casse.",
             "Clic droit dans le vide avec un carton imprimé : fenêtre d'aperçu 3D, à tourner (glisser) et zoomer (molette).",
             "Motifs tout faits rangés dans des fichiers du mod : les tiens pourront s'y ajouter plus tard.",
             "Textes en jeu en anglais. Blocs pleins seulement pour cette première version."]
    for k, t in enumerate(notes): d.text((c.width + 50, a.height + 70 + k * 24), "• " + t if not t.startswith(("réglages", "bulle")) else "   " + t, font=FP, fill=(220, 220, 220))
    W.convert('RGB').save('/mnt/user-data/outputs/tilers_table_mockup.png')
