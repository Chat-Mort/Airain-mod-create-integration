# Écrit le lot 1 dans le pack d'interface HD du mod (et les .mcmeta des sprites en neuf parts).
import os, json, shutil
import sprites
D = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/minecraft/textures/gui/'
MCM = '/tmp/mcm/assets/minecraft/textures/gui/sprites/'
r = sprites.tout()
r.update({k.replace('../', ''): v for k, v in sprites.fond_livre_recettes().items()})
r.update({k.replace('../', ''): v for k, v in sprites.fond_mode_de_jeu().items()})
n = 0
for k, im in r.items():
    rel = k if k in ('recipe_book', 'container/gamemode_switcher') else 'sprites/' + k
    p = D + rel + '.png'; os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p); n += 1
    m = MCM + k + '.png.mcmeta'
    if rel.startswith('sprites/') and os.path.exists(m): shutil.copy(m, p + '.mcmeta')
print(n, 'sprites écrits')
