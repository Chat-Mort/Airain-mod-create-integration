"""Kit de peinture v2 : primitives par face (matière biseautée, panneaux, coutures, rivets, grilles, jauges, lueurs).
Une face = (x0, y0, w, h) dans la texture ; toutes les coordonnées des primitives sont relatives à la face."""
import random
from PIL import Image

def faces(u, v, w, h, d):
    return {"up": (u+d, v, w, d), "down": (u+d+w, v, w, d), "right": (u, v+d, d, h),
            "front": (u+d, v+d, w, h), "left": (u+d+w, v+d, d, h), "back": (u+2*d+w, v+d, w, h)}
COTES = ("right", "front", "left", "back")

def ramp(r, t):
    t = max(0.0, min(0.999, t)); k = t*(len(r)-1); i = int(k); f = k-i
    a, b = r[i], r[min(i+1, len(r)-1)]
    return tuple(int(a[c]+(b[c]-a[c])*f) for c in range(3))
def mix(a, b, t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

class Toile:
    def __init__(self, w=64, h=64, graine=1):
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); self.px = self.im.load(); self.rnd = random.Random(graine)
    # -------------------------------------------------- bas niveau
    def pt(self, f, x, y, c, a=255):
        x0, y0, w, h = f
        if 0 <= x < w and 0 <= y < h: self.px[x0+x, y0+y] = tuple(c[:3]) + (a,)
    def get(self, f, x, y): return self.px[f[0]+x, f[1]+y]
    def vide(self, f, x, y): self.px[f[0]+x, f[1]+y] = (0, 0, 0, 0)
    # -------------------------------------------------- matière
    def matiere(self, f, pal, base=0.5, bruit=0.05, biseau=0.12, nom="front", taches=None, stries=0):
        x0, y0, w, h = f
        for j in range(h):
            for i in range(w):
                t = base + self.rnd.uniform(-bruit, bruit)
                if biseau:
                    if j == 0: t += biseau
                    elif j == h-1: t -= biseau
                    if i == 0: t += biseau*0.4
                    elif i == w-1: t -= biseau*0.6
                if stries and j % stries == 0: t -= 0.06
                if nom == "up": t += 0.08
                elif nom == "down": t -= 0.14
                elif nom == "back": t -= 0.04
                self.px[x0+i, y0+j] = ramp(pal, t) + (255,)
        if taches:
            pal2, n, base2 = taches
            for _ in range(n):
                i, j = self.rnd.randrange(w), self.rnd.randrange(h)
                self.px[x0+i, y0+j] = ramp(pal2, base2 + self.rnd.uniform(-0.1, 0.1)) + (255,)
    def rect(self, f, x, y, w, h, pal, base=0.5, bruit=0.04, relief=0.14):
        """Panneau en relief : arête claire en haut/à gauche, ombre en bas/à droite."""
        for j in range(h):
            for i in range(w):
                t = base + self.rnd.uniform(-bruit, bruit)
                if relief:
                    if j == 0 or i == 0: t += relief
                    if j == h-1 or i == w-1: t -= relief
                self.pt(f, x+i, y+j, ramp(pal, t))
    def plein(self, f, x, y, w, h, c):
        for j in range(h):
            for i in range(w): self.pt(f, x+i, y+j, c)
    def hligne(self, f, y, c, x=0, w=None):
        for i in range(x, (f[2] if w is None else x+w)): self.pt(f, i, y, c)
    def vligne(self, f, x, c, y=0, h=None):
        for j in range(y, (f[3] if h is None else y+h)): self.pt(f, x, j, c)
    def couture(self, f, y, pal, x=0, w=None):
        """Joint horizontal : ligne sombre + liseré clair dessous."""
        self.hligne(f, y, ramp(pal, 0.12), x, w)
        if y+1 < f[3]: self.hligne(f, y+1, ramp(pal, 0.72), x, w)
    def vcouture(self, f, x, pal, y=0, h=None):
        self.vligne(f, x, ramp(pal, 0.12), y, h)
        if x+1 < f[2]: self.vligne(f, x+1, ramp(pal, 0.7), y, h)
    def rivet(self, f, x, y, pal):
        self.pt(f, x, y, ramp(pal, 0.95))
    def rivets(self, f, pts, pal):
        for x, y in pts: self.rivet(f, x, y, pal)
    def grille(self, f, x, y, w, h, pal, sombre=(14, 12, 12), pas=2):
        for j in range(h):
            for i in range(w):
                self.pt(f, x+i, y+j, sombre if i % pas == 0 else ramp(pal, 0.6 if j == 0 else 0.4))
    def jauge(self, f, x, y, laiton, aiguille=(200, 30, 20)):
        """Manomètre 3x3 : anneau de laiton, cadran clair, aiguille."""
        for j in range(3):
            for i in range(3):
                self.pt(f, x+i, y+j, ramp(laiton, 0.7 if (i+j) < 2 else 0.35))
        self.pt(f, x+1, y+1, (236, 230, 210)); self.pt(f, x+2, y, aiguille)
    def lueur(self, f, x, y, w, h, braise, fort=True):
        """Ouverture incandescente : cœur clair, bords sombres."""
        for j in range(h):
            for i in range(w):
                bord = min(i, j, w-1-i, h-1-j)
                k = 0 if bord >= 1 and fort else (1 if bord >= 1 else 2)
                k = min(k + (1 if self.rnd.random() < 0.2 else 0), len(braise)-1)
                self.pt(f, x+i, y+j, braise[k])
    def usure(self, f, pal, n, base=0.3):
        for _ in range(n):
            self.pt(f, self.rnd.randrange(f[2]), self.rnd.randrange(f[3]), ramp(pal, base + self.rnd.uniform(-0.1, 0.1)))
    def miroir(self, src, dst):
        x0, y0, w, h = src; X0, Y0, _, _ = dst
        for j in range(h):
            for i in range(w): self.px[X0+w-1-i, Y0+j] = self.px[x0+i, y0+j]
    def copie(self, src, dst):
        x0, y0, w, h = src; X0, Y0, _, _ = dst
        for j in range(h):
            for i in range(w): self.px[X0+i, Y0+j] = self.px[x0+i, y0+j]

# ------------------------------------------------------------------ palettes
def R(*cs): return list(cs)
SUIE = R((10, 9, 9), (22, 20, 19), (36, 33, 31), (52, 48, 45), (70, 65, 60), (92, 86, 80))
FER = R((20, 20, 24), (36, 36, 42), (54, 54, 62), (78, 78, 88), (108, 106, 116), (140, 138, 146))
FERBLANC = R((110, 106, 96), (146, 142, 130), (178, 174, 160), (204, 200, 186), (224, 220, 206), (242, 238, 226))
KAKI = R((70, 60, 38), (98, 86, 56), (126, 112, 76), (152, 138, 98), (176, 162, 120), (198, 186, 146))
TOILE = R((120, 104, 80), (150, 132, 104), (184, 166, 134), (212, 196, 164), (230, 218, 190), (246, 238, 220))
CUIR = R((34, 18, 10), (56, 32, 16), (82, 50, 26), (110, 70, 38), (136, 92, 52), (162, 116, 70))
LAITON = R((70, 42, 16), (120, 78, 28), (170, 118, 44), (206, 154, 64), (232, 190, 102), (252, 226, 160))
CUIVRE = R((76, 32, 18), (120, 54, 30), (166, 86, 52), (204, 120, 80), (230, 156, 114), (248, 196, 160))
VDG = R((24, 60, 52), (40, 92, 78), (62, 128, 104), (92, 162, 130), (136, 196, 164), (190, 228, 200))
ROUILLE = R((52, 26, 14), (92, 44, 22), (134, 66, 32), (164, 92, 46), (186, 120, 70), (206, 150, 100))
NICKEL = R((60, 64, 72), (96, 102, 110), (136, 142, 150), (176, 182, 190), (210, 216, 222), (240, 244, 248))
TOILE_MOUILLEE = R((34, 44, 40), (50, 64, 58), (70, 86, 76), (92, 108, 94), (116, 130, 112), (146, 158, 138))
ALGUE = R((14, 40, 22), (22, 62, 32), (34, 86, 44), (52, 112, 58), (76, 140, 76), (110, 170, 100))
GIVRE = R((120, 150, 180), (160, 190, 214), (196, 220, 238), (220, 238, 250), (236, 248, 255), (255, 255, 255))
MOUSSE = R((24, 40, 16), (38, 62, 24), (54, 86, 32), (74, 110, 42), (98, 134, 56), (128, 160, 76))
BRAISE = [(255, 236, 160), (255, 176, 60), (232, 96, 22), (150, 40, 12)]
AMBRE = [(255, 226, 140), (250, 170, 50), (190, 100, 20), (110, 50, 10)]
TEAL = [(200, 255, 245), (110, 240, 225), (40, 170, 170), (16, 90, 96)]
NOIR = (14, 12, 12)
CORDE = R((44, 30, 18), (70, 50, 30), (100, 74, 44), (130, 100, 62), (156, 124, 80), (180, 150, 104))
OR = R((90, 56, 8), (140, 96, 16), (190, 140, 30), (226, 182, 52), (246, 214, 96), (255, 240, 170))
