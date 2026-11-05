import random, math
from PIL import Image
R = random.Random(7)
im = Image.new("RGBA", (64, 64), (0, 0, 0, 0)); px = im.load()
def tuile(k, f):
    ox, oy = (k % 4) * 16, (k // 4) * 16
    for y in range(16):
        for x in range(16):
            c = f(x, y)
            if c is not None: px[ox + x, oy + y] = tuple(max(0, min(255, int(v))) for v in c[:3]) + ((c[3],) if len(c) > 3 else (255,))
def n(a=6): return R.randint(-a, a)
def plaques(base, joint, rivet, h=8):
    def f(x, y):
        if y % h == h - 1: return tuple(v - 18 for v in base)
        if y % h == 0: return tuple(v + 10 for v in base)
        if (x in (2, 13)) and y % h in (2, h - 3): return rivet
        if x == 0 and (y // h) % 2 == 0 or x == 8 and (y // h) % 2 == 1: return joint
        return tuple(v + n(5) for v in base)
    return f
tuile(0, plaques((52, 54, 60), (34, 35, 40), (150, 110, 50)))                       # fonte
tuile(1, plaques((88, 90, 98), (60, 62, 68), (170, 130, 60)))                       # fer
tuile(2, lambda x, y: (205 + n(8) - (12 if y in (0, 15) else 0), 160 + n(8) - (12 if y in (0, 15) else 0), 70 + n(5)) if y % 5 else (240, 205, 120))   # laiton
tuile(3, lambda x, y: (190 + n(10), 110 + n(8), 75 + n(6)) if (x + y) % 7 else (215, 140, 95))                     # cuivre
def tuf(x, y):
    rang = y // 4; dec = 4 if rang % 2 else 0
    if y % 4 == 3 or (x + dec) % 8 == 7: return (78, 80, 74)
    return (112 + n(7), 114 + n(7), 106 + n(7))
tuile(4, tuf)
tuile(5, lambda x, y: (200, 175, 90, 255) if x in (0, 15) or y in (0, 15) else ((190, 225, 235, 90) if (x + y) % 9 else (235, 250, 255, 150)))   # verre
tuile(6, lambda x, y: (255, 90 + int(60 * (1 - math.hypot(x - 7.5, y - 7.5) / 11)), 50 + n(10)))                 # lampe
def cadran(x, y):
    d = math.hypot(x - 7.5, y - 7.5)
    if d > 7.5: return (150, 108, 40)
    if d > 6.5: return (205, 160, 70)
    if abs(x - 7.5) < 1 and y < 8 and y > 2: return (40, 30, 20)
    if abs(y - 7.5) < 1 and 7 < x < 12: return (180, 30, 20)
    return (230, 225, 200)
tuile(7, cadran)
tuile(8, lambda x, y: (40, 30, 22) if 2 <= x <= 13 and 2 <= y else ((150, 108, 40) if x % 15 == 0 or y < 2 else (100, 70, 40)))   # porte
tuile(9, lambda x, y: (85 + n(10), 165 + n(10), 140 + n(8)))                         # cuivre oxydé
tuile(10, lambda x, y: (90 + n(6), 92 + n(6), 86 + n(6)) if (x // 4 + y // 4) % 2 else (100 + n(6), 102 + n(6), 96 + n(6)))   # dalle de tuf
tuile(11, lambda x, y: (150 + n(6), 108 + n(6), 40 + n(4)) if y % 4 else (110, 78, 28))                          # laiton sombre
# faisceau (tuile 12) : blanc, alpha dégressif
tuile(12, lambda x, y: (255, 200, 170, int(160 * (1 - y / 16))))
im.save("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/balise_tour.png")
im.resize((256, 256), Image.NEAREST).save("/home/claude/apercus/balise_atlas.png")
