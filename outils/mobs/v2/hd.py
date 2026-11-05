"""Essai haute résolution (×4) : même dessin, mais chaque texel vanilla devient 4×4 pixels.
Minecraft accepte une texture d'entité plus grande que celle du modèle : les UV sont proportionnels."""
import math, random, sys
from PIL import Image
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2")
from kit import ramp, mix, R, FER, CUIVRE, VDG, LAITON, NICKEL, SUIE, BRAISE, AMBRE, NOIR

S = 4
def faces(u, v, w, h, d):
    u, v, w, h, d = u*S, v*S, w*S, h*S, d*S
    return {"up": (u+d, v, w, d), "down": (u+d+w, v, w, d), "right": (u, v+d, d, h),
            "front": (u+d, v+d, w, h), "left": (u+d+w, v+d, d, h), "back": (u+2*d+w, v+d, w, h)}
COTES = ("right", "front", "left", "back")

class HD:
    def __init__(self, w, h, graine=1):
        self.im = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0)); self.px = self.im.load(); self.rnd = random.Random(graine)
    def pt(self, f, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < f[2] and 0 <= y < f[3]: self.px[f[0]+x, f[1]+y] = tuple(c[:3]) + (255,)
    def get(self, f, x, y): return self.px[f[0]+int(x), f[1]+int(y)][:3]
    # ------------------------------------------------------------ matière brossée, éclairée par le haut
    def metal(self, f, pal, base=0.5, nom="front", brosse="h", grain=0.04, biseau=2):
        x0, y0, w, h = f
        stries = [self.rnd.uniform(-0.035, 0.035) for _ in range(max(w, h))]
        for j in range(h):
            for i in range(w):
                t = base + self.rnd.uniform(-grain, grain) + (stries[j] if brosse == "h" else stries[i])
                t += 0.08 * (1 - j / max(1, h - 1)) - 0.04            # lumière venant du haut
                if j < biseau: t += 0.14
                elif j >= h - biseau: t -= 0.16
                if i < biseau: t += 0.05
                elif i >= w - biseau: t -= 0.08
                t += {"up": 0.1, "down": -0.18, "back": -0.04}.get(nom, 0)
                self.px[x0+i, y0+j] = ramp(pal, t) + (255,)
    def panneau(self, f, x, y, w, h, pal, base=0.5, b=2):
        for j in range(h):
            for i in range(w):
                t = base + self.rnd.uniform(-0.03, 0.03) + 0.06 * (1 - j / max(1, h-1))
                if j < b or i < b: t += 0.16
                if j >= h - b or i >= w - b: t -= 0.18
                self.pt(f, x+i, y+j, ramp(pal, t))
    def couture(self, f, y, pal, x=0, w=None):
        w = f[2] - x if w is None else w
        for i in range(x, x+w): self.pt(f, i, y, ramp(pal, 0.08)); self.pt(f, i, y+1, ramp(pal, 0.75))
    def vcouture(self, f, x, pal, y=0, h=None):
        h = f[3] - y if h is None else h
        for j in range(y, y+h): self.pt(f, x, j, ramp(pal, 0.08)); self.pt(f, x+1, j, ramp(pal, 0.72))
    def rivet(self, f, cx, cy, pal):
        """Rivet bombé 3×3 : reflet en haut à gauche, ombre portée en bas à droite."""
        for (dx, dy, t) in ((0, 0, 0.6), (1, 0, 0.75), (2, 0, 0.6), (0, 1, 0.75), (1, 1, 0.98), (2, 1, 0.55), (0, 2, 0.5), (1, 2, 0.45), (2, 2, 0.3)):
            self.pt(f, cx+dx-1, cy+dy-1, ramp(pal, t))
        self.pt(f, cx+2, cy+2, ramp(pal, 0.08))
    def disque(self, f, cx, cy, r, couleur):
        for j in range(int(cy-r-1), int(cy+r+2)):
            for i in range(int(cx-r-1), int(cx+r+2)):
                d = math.hypot(i+0.5-cx, j+0.5-cy)
                if d <= r: self.pt(f, i, j, couleur(d / r, math.atan2(j+0.5-cy, i+0.5-cx)))
    def jauge(self, f, cx, cy, r, angle=-0.6):
        def c(d, a):
            if d > 0.78: return ramp(LAITON, 0.75 if math.sin(a) < 0 else 0.35)
            if d > 0.68: return ramp(LAITON, 0.2)
            return (238, 232, 212) if d < 0.62 or int((a+math.pi) / (math.pi/6)) % 2 else (40, 34, 28)
        self.disque(f, cx, cy, r, c)
        for k in range(int(r*0.62)):                                      # aiguille
            self.pt(f, cx + math.cos(angle)*k, cy + math.sin(angle)*k, (200, 30, 20))
        for (ax, ay) in ((0.7, 0.55),):                                   # zone rouge
            for k in range(-2, 3): self.pt(f, cx + r*0.5 + k*0.4, cy - r*0.45 + k*0.2, (190, 40, 30))
        self.pt(f, cx, cy, ramp(LAITON, 0.2))
    def lueur(self, f, x, y, w, h, coul=BRAISE, centre=None):
        cx, cy = (x + w/2, y + h/2) if centre is None else centre
        rmax = math.hypot(w/2, h/2)
        for j in range(h):
            for i in range(w):
                d = math.hypot(x+i+0.5-cx, y+j+0.5-cy) / rmax + self.rnd.uniform(-0.06, 0.06)
                self.pt(f, x+i, y+j, coul[0] if d < 0.3 else coul[1] if d < 0.6 else coul[2] if d < 0.85 else coul[3])
    def grille(self, f, x, y, w, h, pal, pas=3, epais=2, vertical=False):
        for j in range(h):
            for i in range(w):
                k = (i if vertical else j) % pas
                if k < epais: self.pt(f, x+i, y+j, ramp(pal, 0.65 if k == 0 else 0.4))
    def taches(self, f, pal, n, r=2.5, base=0.5):
        for _ in range(n):
            cx, cy = self.rnd.uniform(0, f[2]), self.rnd.uniform(0, f[3])
            rr = self.rnd.uniform(1, r)
            for j in range(int(cy-rr), int(cy+rr)+1):
                for i in range(int(cx-rr), int(cx+rr)+1):
                    if math.hypot(i-cx, j-cy) < rr and self.rnd.random() < 0.8:
                        if 0 <= i < f[2] and 0 <= j < f[3]:
                            self.pt(f, i, j, mix(self.get(f, i, j), ramp(pal, base + self.rnd.uniform(-0.1, 0.1)), 0.6))
    def fissure(self, f, x, y, n, coul=BRAISE):
        for k in range(n):
            self.pt(f, x, y, coul[1] if k % 3 else coul[0]); self.pt(f, x+1, y, coul[2])
            x += self.rnd.choice((-1, 0, 1)); y += 1

# =========================================================================== CHAUDIÈRE INSTABLE ×4
JAUNE = R((80, 60, 10), (140, 108, 20), (196, 156, 30), (232, 196, 52), (248, 222, 100), (255, 240, 170))
def chaudiere():
    t = HD(64, 32, graine=7)
    TETE, CORPS, PATTE = faces(0, 0, 8, 8, 8), faces(16, 16, 8, 12, 4), faces(0, 16, 4, 6, 4)
    for n, f in TETE.items():
        t.metal(f, CUIVRE, 0.45, nom=n); t.taches(f, VDG, 5)
    f = TETE["front"]                                                    # plaque de foyer en fonte
    t.panneau(f, 1, 1, 30, 30, FER, 0.32)
    for (x0, y0) in ((4, 8), (20, 8)):                                   # évents : yeux
        t.lueur(f, x0, y0, 8, 8); t.grille(f, x0, y0, 8, 8, FER, pas=3, epais=1)
    for (x0, y0, w, h) in ((12, 16, 8, 4), (8, 20, 16, 4), (8, 24, 4, 4), (20, 24, 4, 4)):   # bouche
        t.lueur(f, x0, y0, w, h, centre=(16, 22)); t.grille(f, x0, y0, w, h, FER, pas=3, epais=1, vertical=True)
    for (x, y) in ((3, 3), (28, 3), (3, 28), (28, 28)): t.rivet(f, x, y, LAITON)
    for n in ("right", "left", "back"):
        f = TETE[n]; t.couture(f, 15, CUIVRE)
        for x in range(4, 32, 8): t.rivet(f, x, 4, LAITON); t.rivet(f, x, 27, LAITON)
    t.jauge(TETE["back"], 16, 21, 6)
    f = TETE["up"]                                                       # soupape et volant
    t.disque(f, 16, 16, 9, lambda d, a: ramp(LAITON, 0.7 - 0.4*d) if d > 0.75 else ramp(FER, 0.25 + 0.1*d))
    t.disque(f, 16, 16, 6, lambda d, a: ramp(LAITON, 0.8 if abs(math.sin(a*2)) < 0.25 or d > 0.8 else 0.0) if (abs(math.sin(a*2)) < 0.25 or d > 0.8) else ramp(FER, 0.15))
    t.disque(f, 16, 16, 1.6, lambda d, a: ramp(LAITON, 0.9))
    for (x, y) in ((4, 4), (27, 4), (4, 27), (27, 27)): t.rivet(f, x, y, LAITON)
    for n, f in CORPS.items():
        t.metal(f, CUIVRE, 0.48, nom=n, brosse="v"); t.taches(f, VDG, 7)
        if n not in COTES: continue
        for y in (0, 44): t.panneau(f, 0, y, f[2], 4, LAITON, 0.5, b=1)
        for i in range(f[2]):                                            # bande d'avertissement
            for j in range(20, 28): t.pt(f, i, j, ramp(JAUNE, 0.65 if (j == 20) else 0.55) if ((i + j) // 4) % 2 == 0 else ramp(SUIE, 0.15))
        for x in range(3, f[2], 6): t.rivet(f, x, 7, LAITON); t.rivet(f, x, 40, LAITON)
    f = CORPS["front"]
    t.jauge(f, 10, 13, 6, angle=-0.3)
    t.fissure(f, 24, 6, 10); t.fissure(f, 21, 30, 9); t.fissure(f, 9, 31, 7)
    f = CORPS["back"]; t.panneau(f, 8, 6, 16, 12, FER, 0.35); t.grille(f, 10, 8, 12, 8, FER, pas=3, epais=1, vertical=True)
    t.lueur(f, 11, 9, 10, 6); t.grille(f, 10, 8, 12, 8, FER, pas=3, epais=1, vertical=True)
    for n, f in PATTE.items():
        t.metal(f, FER, 0.4, nom=n, brosse="v")
        if n in COTES:
            t.panneau(f, 0, 15, 16, 9, LAITON, 0.45); t.rivet(f, 4, 19, LAITON); t.rivet(f, 11, 19, LAITON)
            t.rivet(f, 7, 5, FER)
    return t.im

# =========================================================================== LANTERNE DE FORGE ×4
def lanterne():
    t = HD(64, 32, graine=9)
    TETE, TIGE = faces(0, 0, 8, 8, 8), faces(0, 16, 2, 8, 2)
    for n, f in TETE.items():
        if n in COTES:
            t.lueur(f, 0, 0, 32, 32, coul=[(255, 244, 200), (255, 196, 80), (232, 110, 24), (130, 46, 12)], centre=(16, 19))
            for j in range(32):                                          # verre : reflet diagonal
                for i in range(32):
                    if 4 <= i - j + 14 <= 6: t.pt(f, i, j, mix(t.get(f, i, j), (255, 255, 230), 0.35))
            for k in range(3):                                           # armature de laiton
                for i in range(32): t.pt(f, i, k, ramp(LAITON, 0.8 - 0.15*k)); t.pt(f, i, 31-k, ramp(LAITON, 0.4 - 0.1*k))
                for j in range(32): t.pt(f, k, j, ramp(LAITON, 0.7 - 0.15*k)); t.pt(f, 31-k, j, ramp(LAITON, 0.35 - 0.1*k))
            for j in range(3, 29): t.pt(f, 15, j, ramp(LAITON, 0.55)); t.pt(f, 16, j, ramp(LAITON, 0.3))
            for i in range(3, 29): t.pt(f, i, 15, ramp(LAITON, 0.55)); t.pt(f, i, 16, ramp(LAITON, 0.3))
            for (x, y) in ((2, 2), (29, 2), (2, 29), (29, 29)): t.rivet(f, x, y, LAITON)
        else:
            t.metal(f, LAITON, 0.5, nom=n)
            if n == "up":
                t.disque(f, 16, 16, 8, lambda d, a: ramp(LAITON, 0.85 - 0.5*d))
                t.disque(f, 16, 16, 4, lambda d, a: ramp(FER, 0.15 + 0.15*d))
                for (x, y) in ((4, 4), (27, 4), (4, 27), (27, 27)): t.rivet(f, x, y, LAITON)
    f = TETE["front"]                                                    # suie sur le verre : les yeux
    for (x0, y0) in ((5, 11), (19, 11)):
        for j in range(6):
            for i in range(8):
                if (i - 3.5)**2 / 16 + (j - 2.5)**2 / 9 < 1: t.pt(f, x0+i, y0+j, mix(t.get(f, x0+i, y0+j), (30, 16, 8), 0.75))
    for n, f in TIGE.items():
        t.metal(f, FER, 0.45, nom=n, brosse="v", biseau=1)
        if n in COTES:
            for y0 in (4, 16): t.panneau(f, 0, y0, 8, 3, LAITON, 0.55, b=1)
            t.lueur(f, 0, 24, 8, 8, centre=(4, 32))
    t.lueur(TIGE["down"], 0, 0, 8, 8)
    return t.im

if __name__ == "__main__":
    import os
    out = sys.argv[1]; os.makedirs(out + "/creeper", exist_ok=True)
    chaudiere().save(out + "/creeper/creeper.png"); lanterne().save(out + "/blaze.png")
    print("ok")
