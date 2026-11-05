"""Rendu 3/4 des mobs (géométrie du jeu, UV en boîte) pour la revue des textures."""
import math, sys
from PIL import Image, ImageDraw, ImageFont
T = "/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"
CAM = (0.55, 0.45, 1)          # vue de face, légèrement de côté et du dessus
def boite_uv(u, v, w, h, d):
    return {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d), "west": (u, v + d, d, h), "north": (u + d, v + d, w, h),
            "east": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h)}
def cube(x0, y0, z0, w, h, d, u, v, gonfle=0):
    """Coin bas-gauche-arrière (pixels, y vers le haut), dimensions, UV."""
    x0 -= gonfle; y0 -= gonfle; z0 -= gonfle; W, H, D = w + 2 * gonfle, h + 2 * gonfle, d + 2 * gonfle
    x1, y1, z1 = x0 + W, y0 + H, z0 + D
    f = boite_uv(u, v, w, h, d); q = []
    # face nord = devant (vers la caméra, z grand)
    q.append(([(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)], f["north"], (0, 0, 1)))
    q.append(([(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)], f["west"], (1, 0, 0)))
    q.append(([(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)], f["east"], (-1, 0, 0)))
    q.append(([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], f["up"], (0, 1, 0)))
    return q
def proj(p, S, ox, oy):
    x, y, z = p
    return (ox + (x * 0.94 + z * 0.34) * S, oy - (y * 1.0 - z * 0.22 + x * 0.0) * S)
def dessiner(im, tex, cubes, S, ox, oy):
    d = ImageDraw.Draw(im); tw, th = tex.size; k = 1
    qs = [q for c in cubes for q in c]
    qs.sort(key=lambda q: sum(p[2] * 1 - p[0] * 0.3 + p[1] * 0.2 for p in q[0]) / 4)
    for pts, (u, v, w, h), n in qs:
        lum = {(0, 0, 1): 1.0, (1, 0, 0): 0.78, (-1, 0, 0): 0.6, (0, 1, 0): 1.08}[n]
        cu, cv = max(1, int(w)), max(1, int(h))
        for j in range(cv):
            for i in range(cu):
                s0, s1, t0, t1 = i / cu, (i + 1) / cu, j / cv, (j + 1) / cv
                P = lambda s, t: tuple(pts[0][m] * (1 - s) * (1 - t) + pts[1][m] * s * (1 - t) + pts[2][m] * s * t + pts[3][m] * (1 - s) * t for m in range(3))
                px = int((u + (i + .5) * w / cu) * k); py = int((v + (j + .5) * h / cv) * k)
                if not (0 <= px < tw and 0 <= py < th): continue
                c = tex.getpixel((px, py))
                if c[3] < 20: continue
                d.polygon([proj(P(a, b), S, ox, oy) for a, b in ((s0, t0), (s1, t0), (s1, t1), (s0, t1))],
                          fill=tuple(min(255, int(x * lum)) for x in c[:3]) + (255,))
def bipede(bras=4, jambe=4, tete=(0, 0), corps=(16, 16), ub=(40, 16), uj=(0, 16), couche=None):
    c = [cube(-4, 24, -4, 8, 8, 8, *tete), cube(-4, 12, -2, 8, 12, 4, *corps),
         cube(4, 12, -bras / 2, bras, 12, bras, *ub), cube(-4 - bras, 12, -bras / 2, bras, 12, bras, *ub),
         cube(0, 0, -jambe / 2, jambe, 12, jambe, *uj), cube(-jambe, 0, -jambe / 2, jambe, 12, jambe, *uj)]
    if couche: c.append(cube(-4, 24, -4, 8, 8, 8, 32, 0, 0.5))
    return c
MOBS = {
 "zombie/zombie": bipede(couche=1), "zombie/husk": bipede(couche=1), "zombie/drowned": bipede(couche=1),
 "skeleton/skeleton": bipede(2, 2), "skeleton/stray": bipede(2, 2), "skeleton/wither_skeleton": bipede(2, 2), "skeleton/bogged": bipede(2, 2),
 "creeper/creeper": [cube(-4, 18, -4, 8, 8, 8, 0, 0), cube(-4, 6, -2, 8, 12, 4, 16, 16)] + [cube(x, 0, z, 4, 6, 4, 0, 16) for x, z in ((-4, 2), (0, 2), (-4, -6), (0, -6))],
 "enderman/enderman": [cube(-4, 38, -4, 8, 8, 8, 0, 0), cube(-4, 26, -2, 8, 12, 4, 32, 16), cube(4, 8, -1, 2, 30, 2, 56, 0), cube(-6, 8, -1, 2, 30, 2, 56, 0),
                       cube(0, -4, -1, 2, 30, 2, 56, 0), cube(-2, -4, -1, 2, 30, 2, 56, 0)],
 "blaze": [cube(-4, 22, -4, 8, 8, 8, 0, 0)] + [cube(-1 + 7 * math.cos(a), 10 + 6 * (i % 2), -1 + 7 * math.sin(a), 2, 8, 2, 0, 16) for i, a in enumerate([k * math.pi / 4 for k in range(8)])],
 "spider/spider": [cube(-4, 4, 3, 8, 8, 8, 32, 4), cube(-3, 5, -3, 6, 6, 6, 0, 0), cube(-5, 4, -15, 10, 8, 12, 0, 12)] +
                  [cube(4, 6, z, 16, 2, 2, 18, 0) for z in (-6, -3, 0, 3)] + [cube(-20, 6, z, 16, 2, 2, 18, 0) for z in (-6, -3, 0, 3)],
 "spider/cave_spider": [cube(-4, 4, 3, 8, 8, 8, 32, 4), cube(-3, 5, -3, 6, 6, 6, 0, 0), cube(-5, 4, -15, 10, 8, 12, 0, 12)] +
                  [cube(4, 6, z, 16, 2, 2, 18, 0) for z in (-6, -3, 0, 3)] + [cube(-20, 6, z, 16, 2, 2, 18, 0) for z in (-6, -3, 0, 3)],
 "piglin/piglin": bipede(couche=None), "piglin/piglin_brute": bipede(), "piglin/zombified_piglin": bipede(),
}
if __name__ == "__main__":
    noms = list(MOBS); W, H = 300, 380
    pl = Image.new("RGBA", (W * 6, (H + 30) * ((len(noms) + 5) // 6)), (40, 42, 48, 255))
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18); dd = ImageDraw.Draw(pl)
    for i, n in enumerate(noms):
        tex = Image.open(T + n + ".png").convert("RGBA")
        im = Image.new("RGBA", (W, H), (40, 42, 48, 255))
        S = 7 if "enderman" not in n else 5.2
        dessiner(im, tex, MOBS[n], S if "spider" not in n else 6, W / 2, H - 50)
        x, y = (i % 6) * W, (i // 6) * (H + 30)
        pl.alpha_composite(im, (x, y)); dd.text((x + W / 2, y + H + 4), n.split("/")[-1], font=f, fill=(240, 205, 110), anchor="mt")
    pl.save("/home/claude/apercus/revue_mobs.png"); print("ok")
