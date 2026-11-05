"""Outils communs des tableaux v5 : dégradés, halos, grain, perspective."""
import math, random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from tableaux2 import *
from tableaux4 import texte2

def degrade(W, H, couleurs, gamma=1.0):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H): d.line([(0, y), (W, y)], fill=ramp(couleurs, (y/max(1, H - 1))**gamma))
    return im

def halo(im, cx, cy, r, c, force=1.0):
    """Lumière additive circulaire, douce."""
    W, H = im.size; L = Image.new("RGB", (W, H)); px = L.load()
    for y in range(max(0, int(cy - r)), min(H, int(cy + r) + 1)):
        for x in range(max(0, int(cx - r)), min(W, int(cx + r) + 1)):
            t = 1 - math.hypot(x - cx, y - cy)/r
            if t > 0:
                k = force*t*t; px[x, y] = (int(c[0]*k), int(c[1]*k), int(c[2]*k))
    return ImageChops.add(im, L)

def grain(im, graine, force=6):
    rnd = random.Random(graine); px = im.load(); W, H = im.size
    for y in range(H):
        for x in range(W):
            n = rnd.randint(-force, force); r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    return im

def poly_degrade(im, pts, c1, c2, axe="y"):
    """Remplit un polygone d'un dégradé vertical (y) ou horizontal (x)."""
    W, H = im.size; m = Image.new("L", (W, H)); ImageDraw.Draw(m).polygon(pts, fill=255)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    a0, a1 = (min(ys), max(ys)) if axe == "y" else (min(xs), max(xs))
    g = Image.new("RGB", (W, H)); dg = ImageDraw.Draw(g)
    for v in range(int(a0), int(a1) + 1):
        c = mix(c1, c2, (v - a0)/max(1, a1 - a0))
        if axe == "y": dg.line([(0, v), (W, v)], fill=c)
        else: dg.line([(v, 0), (v, H)], fill=c)
    im.paste(g, (0, 0), m)

def ellipse_degrade(im, box, c1, c2):
    W, H = im.size; m = Image.new("L", (W, H)); ImageDraw.Draw(m).ellipse(box, fill=255)
    g = Image.new("RGB", (W, H)); dg = ImageDraw.Draw(g)
    for v in range(int(box[1]), int(box[3]) + 1): dg.line([(0, v), (W, v)], fill=mix(c1, c2, (v - box[1])/max(1, box[3] - box[1])))
    im.paste(g, (0, 0), m)

def etincelles(d, x0, y0, n, rnd, dx=(-30, 30), dy=(-40, 0), cols=((255, 230, 140), (255, 170, 60))):
    for _ in range(n):
        x, y = x0 + rnd.uniform(*dx), y0 + rnd.uniform(*dy); l = rnd.uniform(1, 3)
        d.line([(x, y), (x + rnd.uniform(-1, 1)*l, y + l)], fill=rnd.choice(cols))

def apercu(images, chemin, z=2, W=1700):
    x = y = 10; rowh = 0; c = Image.new("RGB", (W, 4000), (36, 34, 38))
    for im in images:
        im = im.resize((im.width*z, im.height*z), Image.NEAREST)
        if x + im.width > W - 10: x = 10; y += rowh + 10; rowh = 0
        c.paste(im, (x, y)); x += im.width + 10; rowh = max(rowh, im.height)
    c.crop((0, 0, W, y + rowh + 10)).save(chemin)
