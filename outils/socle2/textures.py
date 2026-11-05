"""Textures du piédestal v2 : velours en gris (teinté en jeu), simple ou capitonné, garnitures (passepoil, boutons) en calque,
métal des garnitures en gris, halo lumineux, verre de la cloche."""
import math, random
from PIL import Image
SC = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/"
OUT = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/"
def velours(losange):
    im = Image.new("RGBA", (16, 16)); px = im.load(); r = random.Random(4)
    for y in range(16):
        for x in range(16):
            if losange:
                a, b = abs(x - 7.5), abs(y - 7.5); d = min(abs(a - b), abs(a + b - 5)) / 1.414
                v = 120 + min(d, 1.8) / 1.8 * 120
            else:
                v = 205 + 18 * math.cos((x - 7.5) / 8) - 10 * ((x + y) % 3 == 0)
            v += r.randint(-5, 5)
            px[x, y] = (int(v),) * 3 + (255,)
    return im
def garni(losange):
    im = Image.new("RGBA", (16, 16)); px = im.load()
    for i in range(16):
        for j in (2, 13):
            px[i, j] = (200, 200, 200, 255); px[j, i] = (200, 200, 200, 255)
    if losange:
        for (x, y) in ((5, 5), (10, 5), (5, 10), (10, 10)): px[x, y] = (255, 255, 255, 255)
    else:
        for (x, y) in ((3, 3), (12, 3), (3, 12), (12, 12)): px[x, y] = (255, 255, 255, 255)
    return im
def metal_gris():
    g = Image.open(SC + "mcmeta-assets/assets/minecraft/textures/block/gold_block.png").convert("RGBA"); px = g.load()
    for y in range(16):
        for x in range(16):
            r, gg, b, a = px[x, y]; l = (r * 3 + gg * 6 + b) // 10
            v = min(255, int(l * 1.12)); px[x, y] = (v, v, v, 255)
    return g
def halo():
    im = Image.new("RGBA", (32, 32)); px = im.load()
    for y in range(32):
        for x in range(32):
            d = math.hypot(x + .5 - 16, y + .5 - 16) / 16
            a = max(0, 1 - d) ** 1.6
            px[x, y] = (255, 230, 170, int(255 * a))
    return im
def verre():
    im = Image.new("RGBA", (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16):
            a = 40
            if x in (0, 15) or y in (0, 15): a = 90
            if x - y in (3, 4) and 2 < x < 13: a = 150         # reflet
            px[x, y] = (230, 240, 255, a)
    return im
velours(False).save(OUT + "block/socle_velours_simple.png"); velours(True).save(OUT + "block/socle_velours_losange.png")
garni(False).save(OUT + "block/socle_garni_simple.png"); garni(True).save(OUT + "block/socle_garni_losange.png")
metal_gris().save(OUT + "block/socle_garniture.png"); halo().save(OUT + "block/socle_halo.png"); verre().save(OUT + "block/socle_verre.png")
print("ok")
