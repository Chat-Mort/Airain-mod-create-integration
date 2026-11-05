"""Textures 16×16 des objets de l'Écho."""
import sys, math
from PIL import Image
sys.argv = [sys.argv[0], sys.argv[1]]
import importlib.util
spec = importlib.util.spec_from_file_location("tex", "tex.py"); tex = importlib.util.module_from_spec(spec)
out = sys.argv[1]
def img(): return Image.new("RGBA", (16, 16), (0, 0, 0, 0))
def contour(im):
    p = im.load(); pts = [(x, y) for x in range(16) for y in range(16) if p[x, y][3] > 0]
    for x, y in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 16 and 0 <= ny < 16 and p[nx, ny][3] == 0: p[nx, ny] = (28, 18, 40, 255)
# fragment de résonance : éclat violet-bleu, translucide
im = img(); p = im.load()
for y in range(16):
    for x in range(16):
        d = abs(x - 8) * 1.4 + abs(y - 8)
        if d < 6.5 and (x + y) % 7 != 0:
            t = 1 - d / 6.5
            p[x, y] = (int(110 + 90 * t), int(90 + 80 * t), int(200 + 50 * t), 235)
p[7, 5] = p[8, 6] = (240, 230, 255, 255); contour(im); im.save(f"{out}/fragment_resonance.png")
# diapason d'Écho : fourche de laiton, cristal à la base
im = img(); p = im.load(); laiton = (214, 170, 70, 255); lh = (250, 215, 120, 255); ls = (150, 110, 40, 255)
for y in range(1, 9):
    p[5, y] = laiton; p[10, y] = laiton; p[6, y] = lh if y < 4 else laiton; p[9, y] = ls
for x in range(5, 11): p[x, 9] = laiton
p[7, 10] = p[8, 10] = laiton; p[7, 11] = p[8, 11] = ls
for (x, y) in ((7, 12), (8, 12), (6, 13), (7, 13), (8, 13), (9, 13), (7, 14), (8, 14)): p[x, y] = (170, 110, 230, 255)
p[7, 12] = (230, 200, 255, 255)
for (x, y) in ((3, 2), (12, 3), (2, 5), (13, 6)): p[x, y] = (190, 160, 255, 160)
contour(im); im.save(f"{out}/diapason_echo.png")
# Écho primordial : orbe lumineux avec un halo
im = img(); p = im.load()
for y in range(16):
    for x in range(16):
        r = math.hypot(x - 7.5, y - 7.5)
        if r < 5.2:
            t = 1 - r / 5.2
            p[x, y] = (int(150 + 100 * t), int(110 + 140 * t), 255, 255)
        elif r < 7 and (x * 3 + y) % 4 == 0:
            p[x, y] = (180, 150, 255, 120)
p[6, 5] = p[5, 6] = (255, 255, 255, 255); im.save(f"{out}/echo_primordial.png")
print("ok")
