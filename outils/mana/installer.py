# Installe la barre de mana HD dans le pack d'interface (textures d'Ars Nouveau, 3x).
import sys; sys.path.insert(0, '/home/claude/travail/mana')
from PIL import Image
import barre_hd
D = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/ars_nouveau/textures/gui/'
f, d, liq = barre_hd.construire()
b = Image.new('RGBA', (768, 768))
b.paste(f.crop((0, 0, 324, 54)), (0, 0))            # fond : lignes 0..17 d'interface, posées à y-18
b.paste(d.crop((0, 3, 324, 63)), (0, 54))           # devant : lignes 18..37, posées à y-17
b.save(D + 'manabar_gui_border.png')
liq.save(D + 'manabar_gui_mana.png')
# voile rouge (manque de mana) : Ars le teinte ; un gris clair uniforme suffit, le cadre en masque les bords
g = Image.new('RGBA', (768, 768)); g.paste((232, 228, 240, 255), (0, 0, 300, 768)); g.save(D + 'manabar_gui_grayscale.png')
print('barre de mana installée')
