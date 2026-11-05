"""Les monstres de base deviennent des machines de l'Empire : recoloration des textures vanilla, motifs ajoutés."""
import colorsys, os, sys, random
from PIL import Image
E = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/entity/"
OUT = sys.argv[1] if len(sys.argv) > 1 else "sortie"
random.seed(3)

def rampe(*cs): return list(cs)
LAITON = rampe((70, 42, 16), (120, 78, 28), (170, 118, 44), (206, 154, 64), (232, 190, 102), (252, 226, 160))
FER = rampe((20, 20, 24), (36, 36, 42), (54, 54, 62), (78, 78, 88), (108, 106, 116), (140, 138, 146))
ROUILLE = rampe((52, 26, 14), (92, 44, 22), (134, 66, 32), (164, 92, 46), (186, 120, 70), (206, 150, 100))
VERT_DE_GRIS = rampe((28, 70, 62), (44, 104, 88), (66, 138, 112), (96, 170, 136), (140, 200, 166), (190, 230, 200))
CUIVRE = rampe((92, 40, 22), (140, 66, 38), (184, 98, 60), (214, 130, 86), (234, 164, 120), (248, 200, 160))
TOILE = rampe((44, 34, 24), (70, 54, 38), (98, 78, 54), (124, 100, 70), (150, 124, 90), (176, 150, 112))
SOMBRE = rampe((16, 16, 20), (26, 26, 32), (38, 38, 46), (52, 52, 60), (66, 66, 76), (82, 82, 92))

def sur_rampe(r, lum):
    lum = max(0, min(0.999, lum)); k = lum*(len(r)-1); i = int(k); f = k-i
    a, b = r[i], r[min(i+1, len(r)-1)]
    return tuple(int(a[c]+(b[c]-a[c])*f) for c in range(3))

def recolorer(img, regle):
    img = img.convert("RGBA"); p = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = p[x, y]
            if a == 0: continue
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            res = regle(x, y, h*360, s, v)
            if res: p[x, y] = tuple(res) + (a,)
    return img

def etirer(v, lo, hi): return (v-lo)/(hi-lo) if hi > lo else 0.5

# ---------------- squelette -> automate de laiton (os -> laiton, creux -> fer sombre, orbites -> braises)
def squelette(base, rampe_os=LAITON):
    def regle(x, y, h, s, v):
        if v < 0.35: return sur_rampe(FER, v*1.6)
        return sur_rampe(rampe_os, etirer(v, 0.35, 1.0)*0.95)
    t = recolorer(base, regle); p = t.load()
    for (x, y) in ((9, 12), (10, 12), (13, 12), (14, 12)):        # yeux : braises dans les orbites (face avant de la tête)
        p[x, y] = (255, 150, 40, 255)
    for (x, y) in ((9, 13), (14, 13)): p[x, y] = (200, 70, 20, 255)
    return t

# ---------------- zombie -> ouvrier rouillé (peau -> fer rouillé, chemise -> toile huilée, pantalon -> drap sombre)
def zombie(base):
    def regle(x, y, h, s, v):
        if 60 <= h <= 150 and s > 0.15: return sur_rampe(ROUILLE, etirer(v, 0.15, 0.75))           # peau verte
        if 165 <= h <= 200 and s > 0.2: return sur_rampe(TOILE, etirer(v, 0.3, 0.95))              # chemise cyan
        if 200 < h <= 290 and s > 0.15: return sur_rampe(SOMBRE, etirer(v, 0.15, 0.8))             # pantalon
        if s < 0.15: return sur_rampe(FER, v)                                                      # chaussures, gris
        return None
    t = recolorer(base, regle); p = t.load()
    for (x, y) in ((9, 12), (10, 12), (13, 12), (14, 12)): p[x, y] = (230, 120, 40, 255)      # yeux de braise
    for y in range(20, 32): p[24, y] = (120, 84, 40, 255)                                       # couture du tablier
    return t

# ---------------- creeper -> chaudière instable (vert -> cuivre et vert-de-gris, visage -> grille et braises)
def creeper(base):
    def regle(x, y, h, s, v):
        if v < 0.2: return (20, 16, 14)                                                            # visage
        if (x*7 + y*13) % 11 < 4: return sur_rampe(CUIVRE, etirer(v, 0.3, 1.0))
        return sur_rampe(VERT_DE_GRIS, etirer(v, 0.3, 1.0))
    t = recolorer(base, regle); p = t.load()
    # visage (face avant de la tête : x 8..15, y 8..15) : yeux de foyer brûlants, gueule de grille avec braises
    for y in range(8, 16):
        for x in range(8, 16):
            if p[x, y][:3] != (20, 16, 14): continue
            if y in (10, 11): p[x, y] = ((255, 214, 90, 255) if y == 10 else (255, 130, 30, 255))
            else: p[x, y] = ((230, 80, 20, 255) if (y == 14 and x in (11, 12)) or (y == 13 and x == 12) else (24, 18, 16, 255))
    for (x, y) in ((8, 8), (15, 8), (8, 15), (15, 15)): p[x, y] = LAITON[4] + (255,)          # rivets du visage
    return t

# ---------------- araignée -> araignée mécanique (corps -> fer sombre, reflets -> laiton, yeux rouges conservés)
def araignee(base, metal=FER, accent=LAITON):
    def regle(x, y, h, s, v):
        if (h < 20 or h > 340) and s > 0.5 and v > 0.3: return None                                 # yeux
        if v > 0.42: return sur_rampe(accent, etirer(v, 0.42, 0.75))
        return sur_rampe(metal, etirer(v, 0.05, 0.42))
    return recolorer(base, regle)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    o = lambda f: Image.open(E + f)
    squelette(o("skeleton/skeleton.png")).save(f"{OUT}/skeleton.png")
    zombie(o("zombie/zombie.png")).save(f"{OUT}/zombie.png")
    creeper(o("creeper/creeper.png")).save(f"{OUT}/creeper.png")
    araignee(o("spider/spider.png")).save(f"{OUT}/spider.png")
