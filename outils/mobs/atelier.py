"""Atelier de peinture des monstres : matières, toile masquée par la texture vanilla, peinture face par face."""
import math, random
from PIL import Image
E = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/entity/"

def R(*cs): return list(cs)
def ramp(r, t):
    t = max(0, min(0.999, t)); k = t*(len(r)-1); i = int(k); f = k-i
    a, b = r[i], r[min(i+1, len(r)-1)]
    return tuple(int(a[c]+(b[c]-a[c])*f) for c in range(3))
def mix(a, b, t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

# ---------------------------------------------------------------- palettes
SUIE = R((10, 9, 9), (22, 20, 19), (36, 33, 31), (52, 48, 45), (70, 65, 60), (92, 86, 80))
FERBLANC = R((110, 106, 96), (146, 142, 130), (178, 174, 160), (204, 200, 186), (224, 220, 206), (242, 238, 226))
KAKI = R((70, 60, 38), (98, 86, 56), (126, 112, 76), (152, 138, 98), (176, 162, 120), (198, 186, 146))
ARDOISE = R((32, 40, 48), (48, 58, 68), (66, 78, 90), (86, 100, 112), (108, 122, 134), (134, 148, 160))
PORCELAINE = R((150, 160, 172), (186, 194, 204), (214, 220, 228), (232, 236, 242), (244, 247, 250), (252, 253, 255))
NICKEL = R((70, 74, 80), (110, 116, 124), (150, 156, 164), (186, 192, 200), (216, 222, 228), (244, 248, 252))
ACIER_BLEU = R((14, 20, 40), (24, 36, 66), (36, 54, 96), (52, 76, 126), (78, 104, 156), (120, 148, 196))
VERT_USINE = R((24, 40, 26), (38, 62, 40), (54, 86, 56), (72, 108, 72), (96, 132, 90), (128, 160, 116))
ROUILLE = R((52, 26, 14), (92, 44, 22), (134, 66, 32), (164, 92, 46), (186, 120, 70), (206, 150, 100))
LAITON = R((70, 42, 16), (120, 78, 28), (170, 118, 44), (206, 154, 64), (232, 190, 102), (252, 226, 160))
CUIVRE = R((92, 40, 22), (140, 66, 38), (184, 98, 60), (214, 130, 86), (234, 164, 120), (248, 200, 160))
VDG = R((28, 70, 62), (44, 104, 88), (66, 138, 112), (96, 170, 136), (140, 200, 166), (190, 230, 200))
EMAIL_NOIR = R((8, 8, 10), (16, 16, 20), (26, 26, 32), (40, 40, 48), (90, 92, 104), (200, 204, 216))
CHROME = R((60, 64, 70), (104, 110, 118), (160, 166, 174), (206, 212, 220), (232, 236, 242), (255, 255, 255))
LAQUE_ROUGE = R((60, 10, 10), (104, 18, 16), (150, 28, 22), (188, 44, 32), (214, 74, 56), (236, 120, 100))
VERT_BOUTEILLE = R((8, 30, 20), (14, 48, 32), (22, 68, 46), (32, 90, 62), (50, 114, 80), (80, 140, 104))
OR = R((110, 74, 10), (160, 112, 20), (204, 156, 34), (232, 192, 64), (248, 222, 120), (255, 244, 190))
CUIR = R((40, 22, 12), (64, 38, 20), (90, 56, 30), (116, 76, 42), (140, 96, 56), (164, 118, 74))
FER = R((20, 20, 24), (36, 36, 42), (54, 54, 62), (78, 78, 88), (108, 106, 116), (140, 138, 146))
GRIS_NAVAL = R((48, 54, 60), (72, 80, 88), (98, 106, 114), (124, 132, 140), (150, 158, 164), (178, 184, 190))
BRONZE_VERT = R((22, 30, 20), (36, 48, 32), (52, 68, 44), (70, 88, 58), (92, 110, 74), (120, 136, 96))
VIOLET_VERRE = R((30, 8, 50), (60, 18, 96), (96, 36, 150), (136, 64, 200), (180, 110, 240), (230, 180, 255))
FUME = R((24, 16, 10), (44, 30, 18), (70, 48, 26), (100, 70, 36), (140, 100, 50), (190, 150, 80))
OBSIDIENNE = R((8, 4, 14), (16, 8, 26), (26, 14, 40), (38, 22, 58), (58, 36, 86), (96, 66, 130))
TOILE = R((150, 132, 104), (184, 166, 134), (212, 196, 164), (230, 218, 190), (242, 234, 214), (250, 246, 234))
CORDE = R((44, 30, 18), (70, 50, 30), (100, 74, 44), (130, 100, 62), (156, 124, 80), (180, 150, 104))
BRAISE = [(255, 236, 160), (255, 196, 80), (255, 130, 30), (210, 70, 16), (140, 30, 10)]
ECHO = R((40, 12, 60), (80, 30, 120), (130, 60, 190), (180, 100, 240), (220, 160, 255), (245, 220, 255))

def faces(u, v, w, h, d):
    return {"up": (u+d, v, w, d), "down": (u+d+w, v, w, d), "right": (u, v+d, d, h),
            "front": (u+d, v+d, w, h), "left": (u+d+w, v+d, d, h), "back": (u+2*d+w, v+d, w, h)}
COTES = ("right", "front", "left", "back")

def metal(pal, base=0.5, bruit=0.06, biseau=True, stries=0.0, graine=1):
    rnd = random.Random(graine)
    def f(i, j, w, h, face):
        t = base + rnd.uniform(-bruit, bruit)
        if stries and j % 3 == 0: t += stries
        if biseau:
            if j == 0: t += 0.16
            elif j == h-1: t -= 0.16
            if i == 0: t += 0.06
            elif i == w-1: t -= 0.08
        if face == "up": t += 0.08
        if face == "down": t -= 0.12
        return ramp(pal, t)
    return f

def uni(c):
    return lambda i, j, w, h, face: c

class Toile:
    def __init__(self, taille, masque=None):
        self.im = Image.new("RGBA", taille, (0, 0, 0, 0)); self.p = self.im.load()
        self.m = masque.convert("RGBA").load() if masque is not None else None
        self.W, self.H = taille
    def pt(self, x, y, c, force=False):
        if not (0 <= x < self.W and 0 <= y < self.H): return
        if not force and self.m is not None and self.m[x, y][3] == 0: return
        self.p[x, y] = tuple(int(v) for v in c[:3]) + (255,)
    def get(self, x, y): return self.p[x, y]
    def boite(self, u, v, w, h, d, mat, quelles=None, force=False):
        f = faces(u, v, w, h, d)
        for k, (x0, y0, fw, fh) in f.items():
            if quelles and k not in quelles: continue
            for j in range(fh):
                for i in range(fw): self.pt(x0+i, y0+j, mat(i, j, fw, fh, k), force)
        return f
    def rect(self, x0, y0, w, h, c, force=False):
        for j in range(h):
            for i in range(w): self.pt(x0+i, y0+j, c if not callable(c) else c(i, j), force)
    def cadre(self, x0, y0, w, h, clair, sombre, force=False):
        for i in range(w): self.pt(x0+i, y0, clair, force); self.pt(x0+i, y0+h-1, sombre, force)
        for j in range(h): self.pt(x0, y0+j, clair, force); self.pt(x0+w-1, y0+j, sombre, force)
    def disque(self, cx, cy, r, fn, force=False):
        for y in range(int(cy-r-1), int(cy+r+2)):
            for x in range(int(cx-r-1), int(cx+r+2)):
                dx, dy = x+0.5-cx, y+0.5-cy; rr = math.hypot(dx, dy)
                if rr <= r:
                    c = fn(rr, math.degrees(math.atan2(dy, dx)) % 360)
                    if c: self.pt(x, y, c, force)
    def rivet(self, x, y, pal=LAITON, force=False): self.pt(x, y, pal[5], force)
    def ligne_h(self, x0, y0, w, c, force=False):
        for i in range(w): self.pt(x0+i, y0, c if not callable(c) else c(i), force)
    def ligne_v(self, x0, y0, h, c, force=False):
        for j in range(h): self.pt(x0, y0+j, c if not callable(c) else c(j), force)

def vanilla(chemin): return Image.open(E + chemin).convert("RGBA")
