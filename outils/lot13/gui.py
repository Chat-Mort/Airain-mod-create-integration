# Textures d'interface de la table du carreleur : fond Création, fond Rangement, onglets ; en 3x (pack HD) et en 1x
import sys; sys.path.insert(0, '.')
import ecran
from ecran import Ecran, ICONES, S
from PIL import Image
M = '/home/claude/airain-mod-create-integration/src/main/resources/'
BASE = M + 'assets/airain/textures/gui/'
HD = M + 'resourcepacks/interface_hd/assets/airain/textures/gui/'
def toile(n):
    e = Ecran(n, n); return e
def creation():
    e = toile(512)
    e.panneau(0, 24, 264, 250)
    e.creux(8, 52, 78, 100)                    # liste des motifs
    e.creux(90, 30, 100, 100)                  # aperçu
    e.creux(8, 166, 78, 14)                    # nom
    e.case(208, 122); e.case(240, 122)         # carton vierge, carton imprimé
    e.inventaire(51, 190)
    e.case(300, 0)                             # case de rôle (copiée à l'écran selon le motif)
    return e.im
def rangement():
    e = toile(512)
    e.panneau(0, 24, 264, 250)
    for r in range(4):
        for c in range(9): e.case(51 + c * 18, 46 + r * 18)
    e.inventaire(51, 190)
    return e.im
def onglets():
    e = Ecran(128, 64)
    for i, ic in enumerate(ICONES):
        e.onglet(i * 26, 0, ic, True)
        # onglet inactif : dessiné 3 pixels plus bas dans Ecran.onglet ; on le place en (i*26, 24)
        f = Ecran(26, 24); f.onglet(0, 0, ic, False)
        e.im.alpha_composite(f.im.crop((0, 3 * S, 26 * S, 24 * S)), (i * 26 * S, 24 * S))
    return e.im
for nom, f in (('tilers_table', creation), ('tilers_table_storage', rangement), ('tilers_table_tabs', onglets)):
    hd = f()
    hd.save(HD + nom + '.png')
    w, h = hd.size
    hd.resize((w // S, h // S), Image.NEAREST).save(BASE + nom + '.png')
    print(nom, hd.size)
