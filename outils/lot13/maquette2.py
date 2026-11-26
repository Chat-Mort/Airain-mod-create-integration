# Maquette 2 : réglages propres à chaque motif (cases pour les simples, taille du motif pour les complexes),
# bordure à cocher, boutons du pack (chaîne d'airain, cases à cocher, flèches, curseur)
import sys, math; sys.path.insert(0, '.')
from ecran import *
W_ = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/minecraft/textures/gui/sprites/widget/'
SP = {n: Image.open(W_ + n + '.png').convert('RGBA') for n in ('button', 'button_highlighted', 'checkbox', 'checkbox_selected', 'page_backward', 'page_forward', 'slider', 'slider_handle')}
blanc, noir, air, cuivre, ard = tex('white_marble_0'), tex('black_marble_0'), tex('airain_block'), tex('cut_airain'), tex('cut_slate')

def bouton_pack(e, t, x, y, w, survol=False, h=20):
    """Bouton nine-slice du pack : chaîne d'airain (rouge au survol), w en pixels d'interface."""
    src = SP['button_highlighted' if survol else 'button']; W, H = w * S, h * S
    if W >= 120:
        g, dr = src.crop((0, 0, 60, 60)), src.crop((540, 0, 600, 60)); m = src.crop((60, 0, 540, 60)).resize((W - 120, 60))
        out = Image.new('RGBA', (W, 60)); out.alpha_composite(g, (0, 0)); out.alpha_composite(m, (60, 0)); out.alpha_composite(dr, (W - 60, 0))
    else:
        out = Image.new('RGBA', (W, 60)); out.alpha_composite(src.crop((0, 0, W // 2, 60)), (0, 0)); out.alpha_composite(src.crop((600 - (W - W // 2), 0, 600, 60)), (W // 2, 0))
    e.im.alpha_composite(out.resize((W, H)) if h != 20 else out, (x * S, y * S))
    tw = e.d.textlength(t, font=FT) / S; e.texte(t, x + (w - tw) / 2, y + (h - 9) / 2, (255, 255, 255))
def case_cocher(e, x, y, oui): e.im.alpha_composite(SP['checkbox_selected' if oui else 'checkbox'], (x * S, y * S))
def fleche(e, x, y, sens): e.im.alpha_composite(SP['page_forward' if sens > 0 else 'page_backward'], (x * S, y * S))
def curseur(e, x, y, w, frac):
    src = SP['slider']; W = w * S
    out = Image.new('RGBA', (W, 60)); out.alpha_composite(src.crop((0, 0, W // 2, 60)), (0, 0)); out.alpha_composite(src.crop((600 - (W - W // 2), 0, 600, 60)), (W // 2, 0))
    e.im.alpha_composite(out, (x * S, y * S))
    e.im.alpha_composite(SP['slider_handle'], (int((x + 2 + frac * (w - 12)) * S), y * S))

def damier(n, cell, bord):
    def f(x, z):
        if bord and (x < bord or z < bord or x >= n - bord or z >= n - bord): return air
        return blanc if (x // cell + z // cell) % 2 == 0 else noir
    return f
def rosace(n, taille, bord):
    def f(x, z):
        if bord and (x < bord or z < bord or x >= n - bord or z >= n - bord): return air
        u = (x - bord) % taille - (taille - 1) / 2; v = (z - bord) % taille - (taille - 1) / 2
        r = math.hypot(u, v) / (taille / 2); a = math.atan2(v, u)
        if r < 0.22: return cuivre                                         # accent au centre
        if 0.32 < r < 0.8 and math.cos(8 * a) > 0.45: return noir            # pétales
        if 0.88 < r < 1.02: return noir                                    # anneau
        return blanc
    return f

def onglet_creation(motif, params, apercu):
    e = Ecran(264, 276)
    for i, ic in enumerate(ICONES): e.onglet(6 + i * 28, 2, ic, i == 0)
    e.panneau(0, 24, 264, 250)
    e.texte("Tiler's Table", 186, 9, OR, True)
    bouton_pack(e, "Floor  ›", 8, 30, 78, True)                         # un seul bouton : sol -> mur -> plafond
    e.creux(8, 52, 78, 100)
    lst = ("Checkerboard", "Herringbone", "Offset pavers", "Diamonds", "Stripes", "Diagonals", "Rosette", "Basketweave")
    for i, t in enumerate(lst):
        if t == motif: e.R(9, 53 + i * 12, 76, 12, (90, 60, 40))
        e.texte(t, 11, 54.5 + i * 12, OR if t == motif else BLANC)
    e.creux(90, 30, 100, 100)
    e.im.alpha_composite(motif_grille(16, apercu).resize((96 * S, 96 * S), Image.NEAREST), (92 * S, 32 * S))
    roles = [("Color A", blanc), ("Color B", noir)] + ([("Accent", cuivre)] if motif == "Rosette" else []) + ([("Border", air)] if params.get('bord') else [])
    for k, (t, img) in enumerate(roles):
        y = 31 + k * 22
        e.texte(t, 196, y + 4, BLANC); e.case(240, y)
        if img is not None: e.objet(img, 241, y + 1)
    y = 136
    if 'cell' in params:
        e.texte("Cell size", 90, y + 5, BLANC); bouton_pack(e, "−", 132, y, 20); e.texte(str(params['cell']), 156, y + 5, OR, True); bouton_pack(e, "+", 166, y, 20)
    else:
        e.texte("Pattern size", 90, y + 1, BLANC); e.texte("%d × %d" % (params['taille'], params['taille']), 150, y + 1, OR, True)
        curseur(e, 90, y + 10, 100, (params['taille'] - 8) / 16)
    y = 169
    case_cocher(e, 90, y, params.get('bord', 0) > 0); e.texte("Border", 110, y + 4, BLANC)
    if params.get('bord'):
        bouton_pack(e, "−", 142, y - 1, 20); e.texte(str(params['bord']), 165, y + 4, OR, True); bouton_pack(e, "+", 174, y - 1, 20)
    e.texte("Name", 8, 157, (190, 190, 190)); e.creux(8, 166, 78, 14); e.texte(params['nom'], 11, 168, BLANC)
    e.case(208, 122); e.objet(carton(), 209, 123); e.texte("→", 228, 125, OR, True); e.case(240, 122); e.objet(carton([hx('e8e4dc'), hx('2c2a30')]), 241, 123)
    bouton_pack(e, "Print", 196, 150, 62, True)
    e.inventaire(51, 190)
    return e.im

if __name__ == '__main__':
    from PIL import ImageFont
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
    FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    a = onglet_creation("Checkerboard", {'cell': 2, 'bord': 0, 'nom': 'Hall floor'}, damier(16, 2, 0))
    b = onglet_creation("Rosette", {'taille': 12, 'bord': 1, 'nom': 'Throne room'}, rosace(16, 12, 1))
    Wd = Image.new('RGBA', (a.width + b.width + 60, a.height + 330), (52, 54, 60, 255)); d = ImageDraw.Draw(Wd)
    d.text((20, 10), "Table du carreleur, maquette 2 — à gauche un motif simple (damier), à droite un motif complexe (rosace)", font=F, fill=(240, 220, 160))
    Wd.alpha_composite(a, (20, 40)); Wd.alpha_composite(b, (a.width + 40, 40))
    notes = ["Chaque motif a ses propres réglages :",
             "  motifs simples (damier, bandes, diagonales, pavés, chevrons, vannerie) : « Cell size », 1 à 4 blocs par case ;",
             "  motifs complexes (rosace, losanges) : « Pattern size », curseur de 8 × 8 à 24 × 24 ; le dessin est recalculé à cette taille, pas agrandi.",
             "Bordure à cocher, sur tous les motifs. Cochée : son rôle (bloc) et sa largeur (1 à 3) apparaissent.",
             "  La bordure fait le tour de la zone tracée au cordeau, quelle que soit sa taille ; le motif se répète à l'intérieur.",
             "  L'aperçu la montre autour d'une zone de 16 × 16.",
             "Boutons du pack : chaîne d'airain (rouge au survol), cases à cocher et curseur d'airain, flèches pour la fenêtre d'aperçu.",
             "Le rôle « Accent » n'apparaît que pour les motifs qui en ont un (centre de la rosace, cœur des losanges)."]
    for k, t in enumerate(notes): d.text((24, a.height + 60 + k * 26), t if t.startswith("  ") else "• " + t, font=FP, fill=(220, 220, 220))
    Wd.convert('RGB').save('/mnt/user-data/outputs/tilers_table_mockup_2.png')
