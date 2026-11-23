# Écrit le lot 3 (Waystones) dans le pack d'interface HD du mod.
import os, ways
r = ways.lot()
for rel, im in r.items():
    p = ways.D + rel; os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
print(len(r), 'textures écrites')
