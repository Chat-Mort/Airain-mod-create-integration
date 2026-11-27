# Texture d'interface de l'armoire impériale : fond (176 x 206) et boutons d'échange (normal / survol) sur une toile de 256 ; 3x (pack HD) et 1x
import sys; sys.path.insert(0, '/home/claude/travail/lot13'); sys.path.insert(0, '/home/claude/travail/lot16')
from ecran import Ecran, S, OR, BLANC
from PIL import Image
import maquette as M
M_ = '/home/claude/airain-mod-create-integration/src/main/resources/'
e = Ecran(256, 256)
e.panneau(0, 0, 176, 206)
for r in range(4):
    for c in range(9): e.case(7 + c * 18, 17 + r * 18)
e.inventaire(7, 121)
M.bouton(e, 180, 0, False); M.bouton(e, 180, 12, True)     # boutons : normal en (180, 0), survol en (180, 12)
hd = e.im
hd.save(M_ + 'resourcepacks/interface_hd/assets/airain/textures/gui/imperial_wardrobe.png')
hd.resize((256, 256), Image.NEAREST).save(M_ + 'assets/airain/textures/gui/imperial_wardrobe.png')
print('ok')
