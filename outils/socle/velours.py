"""Coussin capitonné symétrique (zone visible 2..13) : 4 boutons dorés, plis en X et en losange, passepoil doré."""
import sys, random
from PIL import Image
im = Image.new("RGBA", (16, 16)); px = im.load(); rnd = random.Random(3)
OR, OR_S, OR_C = (232, 190, 90), (176, 128, 48), (255, 236, 160)
BAS, HAUT = (84, 10, 18), (164, 28, 38)
def vel(t): t = max(0, min(1, t)); return tuple(int(BAS[i] + (HAUT[i] - BAS[i]) * t) for i in range(3))
for y in range(16):
    for x in range(16):
        if x in (0, 1, 14, 15) or y in (0, 1, 14, 15): px[x, y] = OR + (255,); continue
        if x in (2, 13) or y in (2, 13): px[x, y] = OR_S + (255,); continue          # passepoil doré
        a, b = abs(x - 7.5), abs(y - 7.5)
        d = min(abs(a - b), abs(a + b - 5)) / 1.414                                   # distance au pli
        t = min(d, 1.8) / 1.8 * 0.85 + 0.1 + rnd.uniform(-0.03, 0.03)
        px[x, y] = vel(t) + (255,)
for x, y in [(5, 5), (10, 5), (5, 10), (10, 10)]: px[x, y] = OR_C + (255,)
im.save(sys.argv[1])
im.crop((2, 2, 14, 14)).resize((240, 240), Image.NEAREST).save("apercu.png")
