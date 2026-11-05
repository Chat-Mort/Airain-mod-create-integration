"""Cornes en tuyaux du Warden, et textures d'attaque des monstres hostiles."""
import math, colorsys, random, os
from PIL import Image
from atelier import *
TX = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/"
VIOLET = [(250, 220, 255), (214, 150, 255), (170, 90, 240), (110, 40, 180)]

# ------------------------------------------------ cornes : tuyaux carrés coudés, brides et buse lumineuse
def cornes(base, calque):
    p, g = base.load(), calque.load()
    for (u, v, miroir) in ((52, 32, False), (58, 0, True)):
        for y in range(16):
            for x in range(16): p[u+x, v+y] = (0, 0, 0, 0); g[u+x, v+y] = (0, 0, 0, 0)
        def px(x, y, c, lum=False):
            xx = 15 - x if miroir else x
            p[u+xx, v+y] = c + (255,)
            if lum: g[u+xx, v+y] = c + (255,)
        for x in range(7, 16):                                       # départ horizontal depuis la tête
            for y in range(11, 15):
                px(x, y, OR[5] if y == 11 else OR[3] if y < 13 else OR[1] if y == 13 else OR[0])
        for y in range(3, 15):                                        # coude puis montée verticale
            for x in range(6, 10):
                px(x, y, OR[5] if x == 6 else OR[3] if x < 8 else OR[1] if x == 8 else OR[0])
        for (y, x0, x1) in ((8, 5, 11), (12, 12, 14)):                # brides
            for x in range(x0, x1): px(x, y, OR[4] if x < (x0+x1)//2 else OR[1])
        if True:
            for x in range(13, 15):
                for y in range(10, 16): px(x, y, OR[4] if x == 13 else OR[1])
        for x in range(5, 11):                                        # buse : lumière d'Écho
            px(x, 2, VIOLET[1], True); px(x, 3, OR[2])
        for x in range(6, 10): px(x, 1, VIOLET[0], True)
        for y in (5, 6, 10):
            px(7, y, VIOLET[2], True)                                  # fentes lumineuses le long du tuyau
    return base, calque

# ------------------------------------------------ rayon du Warden : cercles runiques d'Écho (16 images)
def rayon_echo(k):
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0)); p = im.load()
    r = 4 + k*0.72; ep = 1.6; fondu = 1 - max(0, k-9)/7
    for y in range(32):
        for x in range(32):
            dx, dy = x+0.5-16, y+0.5-16; d = math.hypot(dx, dy); a = math.degrees(math.atan2(dy, dx)) % 360
            if abs(d - r) < ep:
                c = VIOLET[0] if abs(d - r) < 0.6 else VIOLET[1]
                p[x, y] = c + (int(255*fondu),)
            elif r-3.2 < d < r-ep and int((a + k*12) / 30) % 3 == 0:                # runes en couronne, qui tournent
                p[x, y] = VIOLET[2] + (int(220*fondu),)
            elif d < r*0.35 and k < 6:
                p[x, y] = VIOLET[0] + (int(200*(1 - k/6)),)
    return im

# ------------------------------------------------ recolorations génériques
def recolore(chemin, fn):
    im = Image.open(TX + chemin).convert("RGBA"); p = im.load()
    for y in range(im.height):
        for x in range(im.width):
            c = p[x, y]
            if c[3]:
                h, s, v = colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
                n = fn(x, y, h*360, s, v)
                if n: p[x, y] = tuple(n[:3]) + (c[3],)
    return im

def orbe_violet():                                                   # boule de feu du dragon : orbe d'Écho cerclé d'or
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); p = im.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x+0.5-8, y+0.5-8)
            if d < 7.5:
                c = OR[4] if 6.2 < d else VIOLET[0] if d < 2 else VIOLET[1] if d < 3.8 else VIOLET[2] if d < 5.2 else VIOLET[3]
                p[x, y] = c + (255,)
    return im

def boulet():                                                        # boules de feu (blaze, ghast) : boulet de fonte incandescent
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); p = im.load(); rnd = random.Random(3)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x+0.5-8, y+0.5-8)
            if d < 6.6:
                c = ramp(SUIE, 0.4 + 0.3*(x+y < 13))
                if rnd.random() < 0.28: c = BRAISE[1] if d < 4 else BRAISE[2]
                if d > 5.6: c = BRAISE[3]
                p[x, y] = c + (255,)
    return im

GENERER = {
    "particle/sonic_boom_%d.png": None,
    "entity/enderdragon/dragon_fireball.png": orbe_violet,
    "item/fire_charge.png": boulet,
    "entity/shulker/spark.png": lambda: recolore("entity/shulker/spark.png",                     # balle de tourelle chauffée au rouge
        lambda x, y, h, s, v: BRAISE[1] if v > 0.9 else BRAISE[2] if v > 0.7 else BRAISE[3] if v > 0.5 else ramp(GRIS_NAVAL, v)),
    "entity/projectiles/wind_charge.png": lambda: recolore("entity/projectiles/wind_charge.png",  # charge de vent -> bouffée de vapeur
        lambda x, y, h, s, v: ramp(R((150, 150, 156), (196, 196, 202), (236, 236, 240)), v)),
    "entity/guardian_beam.png": lambda: recolore("entity/guardian_beam.png",                      # rayon du gardien -> faisceau de visée rouge
        lambda x, y, h, s, v: mix((255, 60, 40), (255, 220, 200), v*0.6) if v > 0.2 else (60, 10, 8)),
    "entity/projectiles/arrow.png": lambda: recolore("entity/projectiles/arrow.png",               # carreaux : tige d'acier, pointe de laiton, empennage blanc
        lambda x, y, h, s, v: ramp(PORCELAINE, v) if (s < 0.15 and v > 0.7) else ramp(LAITON, v) if (s < 0.25 and v > 0.4) else ramp(FER, v*1.3)),
    "entity/projectiles/tipped_arrow.png": lambda: recolore("entity/projectiles/tipped_arrow.png",
        lambda x, y, h, s, v: ramp(PORCELAINE, v) if (s < 0.15 and v > 0.7) else ramp(LAITON, v) if (s < 0.25 and v > 0.4) else ramp(FER, v*1.3)),
    "entity/trident.png": lambda: recolore("entity/trident.png",                                  # harpon du scaphandrier
        lambda x, y, h, s, v: ramp(LAITON, v*1.1) if s > 0.2 else ramp(CHROME, v)),
    "item/trident.png": lambda: recolore("item/trident.png",
        lambda x, y, h, s, v: ramp(LAITON, v*1.1) if s > 0.2 else ramp(CHROME, v)),
}
