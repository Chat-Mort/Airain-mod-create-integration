import math, sys
from PIL import Image, ImageDraw, ImageFont
from mobs3d import cube, dessiner, bipede
O = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2/out5/"
A = "/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"
TR = [(0, 0), (0, 1), (24, 10), (24, 19), (0, 4), (0, 5), (0, 6), (0, 7)]
piglin = [cube(-5, 24, -4, 10, 8, 8, 0, 0), cube(5, 25, -2, 1, 5, 4, 51, 6), cube(-6, 25, -2, 1, 5, 4, 39, 6), cube(-2, 25, 4, 4, 4, 1, 31, 1),
          cube(-4, 12, -2, 8, 12, 4, 16, 16), cube(4, 12, -2, 4, 12, 4, 32, 48), cube(-8, 12, -2, 4, 12, 4, 40, 16),
          cube(0, 0, -2, 4, 12, 4, 16, 48), cube(-4, 0, -2, 4, 12, 4, 0, 16)]
creeper = [cube(-4, 18, -4, 8, 8, 8, 0, 0), cube(-4, 6, -2, 8, 12, 4, 16, 16)] + [cube(x, 0, z, 4, 6, 4, 0, 16) for x, z in ((-4, 2), (0, 2), (-4, -6), (0, -6))]
araignee = [cube(-5, 4, -15, 10, 8, 12, 0, 12), cube(-3, 5, -3, 6, 6, 6, 0, 0), cube(-4, 4, 3, 8, 8, 8, 32, 4)] + \
           [cube(4, 6, z, 16, 2, 2, 18, 0) for z in (-6, -3, 0, 3)] + [cube(-20, 6, z, 16, 2, 2, 18, 0) for z in (-6, -3, 0, 3)]
M = [("creeper", "creeper/creeper.png", creeper, 7),
     ("araignée", "spider/spider.png", araignee, 6), ("araignée des cavernes", "spider/cave_spider.png", araignee, 6),
     ("cube de magma", "slime/magmacube.png", [cube(-4, 7 - i, -4, 8, 1, 8, u, v) for i, (u, v) in enumerate(TR)], 13),
     ("shulker (fermé)", "shulker/shulker.png", [cube(-8, 0, -8, 16, 8, 16, 0, 28), cube(-8, 4, -8, 16, 12, 16, 0, 0)], 6),
     ("shulker (ouvert)", "shulker/shulker.png", [cube(-8, 0, -8, 16, 8, 16, 0, 28), cube(-8, 12, -8, 16, 12, 16, 0, 0), cube(-3, 6, -3, 6, 6, 6, 0, 52)], 6),
     ("breeze", "breeze/breeze.png", [cube(-4, 14, -4, 8, 8, 8, 0, 0), cube(-5, 13, -2, 10, 3, 4, 4, 24)] +
        [cube(-1 + 4 * math.cos(a), 2, -1 + 4 * math.sin(a), 2, 8, 2, 0, 17) for a in (0.3, 2.4, 4.5)], 10),
     ("wither", "wither/wither.png", [cube(-4, 20, -4, 8, 8, 8, 0, 0), cube(-15, 17, -3, 6, 6, 6, 32, 0), cube(9, 17, -3, 6, 6, 6, 32, 0),
        cube(-10, 15, -1.5, 20, 3, 3, 0, 16), cube(-1.5, 4, -1.5, 3, 10, 3, 0, 22), cube(-5.5, 11.5, -1, 11, 2, 2, 24, 22),
        cube(-5.5, 9, -1, 11, 2, 2, 24, 22), cube(-5.5, 6.5, -1, 11, 2, 2, 24, 22), cube(-1.5, -2, -1.5, 3, 6, 3, 12, 22)], 7),
     ("wither (invulnérable)", "wither/wither_invulnerable.png", None, 7),
     ("squelette de fonte", "skeleton/wither_skeleton.png", bipede(2, 2), 7),
     ("piglin", "piglin/piglin.png", piglin, 7), ("piglin zombifié", "piglin/zombified_piglin.png", piglin, 7)]
M[8] = (M[8][0], M[8][1], M[7][2], 7)
W, H = 300, 360
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17); g = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
rang = len(M)
pl = Image.new("RGBA", (W * 6, (H * 2 + 40) * 2), (40, 42, 48, 255)); dd = ImageDraw.Draw(pl)
for i, (nom, chemin, geo, S) in enumerate(M):
    x, y = (i % 6) * W, (i // 6) * (H * 2 + 40)
    for k, (src, lab) in enumerate(((A, "avant"), (O, "après"))):
        im = Image.new("RGBA", (W, H), (40, 42, 48, 255) if k else (34, 34, 38, 255))
        dessiner(im, Image.open(src + chemin).convert("RGBA"), geo, S, W / 2, H - 70)
        pl.alpha_composite(im, (x, y + k * H))
        dd.text((x + 8, y + k * H + 6), lab, font=g, fill=(180, 170, 150))
    dd.text((x + W / 2, y + 2 * H + 8), nom, font=f, fill=(240, 205, 110), anchor="mt")
pl.save("/home/claude/apercus/revue_mobs_lot5.png"); print("ok")
