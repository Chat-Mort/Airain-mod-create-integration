"""Ailes du Gardien des Cieux : les verres des vitraux deviennent translucides, le plomb et le laiton restent opaques.
usage : python3 vitraux.py <pack> [alpha]"""
import sys
from PIL import Image
P = sys.argv[1]; A = int(sys.argv[2]) if len(sys.argv) > 2 else 150
f = P + "/kubejs/assets/minecraft/textures/entity/enderdragon/dragon.png"
im = Image.open(f).convert("RGBA"); px = im.load(); n = 0
for x in range(0, 112):
    for y in range(88, 200):
        r, g, b, a = px[x, y]
        if a == 255 and b > g:          # verre (violet, bleu, magenta) ; le plomb et le laiton ont g > b
            px[x, y] = (r, g, b, A); n += 1
im.save(f); print(n, "pixels de verre à", A)
