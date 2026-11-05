"""Le Gardien des profondeurs, golem arcanique : un corps de cristal d'Écho tenu dans une armature d'or ciselé."""
import random
from atelier import *
from warden_meca import CORPS_W, TETE_W, BRAS_D, BRAS_G, JAMBE_D, JAMBE_G, COTES_W, VIOLET

def cristal(graine=70):
    rnd = random.Random(graine)
    def f(i, j, w, h, face):
        facette = ((i + j) // 3 + (i - j) // 5) % 3                       # facettes taillées
        t = 0.3 + 0.18*facette + rnd.uniform(-0.04, 0.04) + (0.12 if face == "up" else 0)
        if (i + 2*j) % 13 == 0: t += 0.3                                  # éclats de lumière
        return ramp(VIOLET_VERRE, t)
    return f

def or_cisele(base=0.55):
    def f(i, j, w, h, face):
        c = ramp(OR, base + 0.15*(j == 0) - 0.18*(j == h-1) + 0.06*(i == 0) - 0.06*(i == w-1))
        if (i + j) % 4 == 0 and 0 < i < w-1 and 0 < j < h-1: c = ramp(OR, base - 0.2)   # gravure en chevrons
        return c
    return f

def peindre():
    import random as _r
    t = Toile((128, 128)); glow = []
    def lueur(x, y, c): t.pt(x, y, c, True); glow.append((x, y, c))
    def plaque(x, y, w, h, base=0.55):
        f = or_cisele(base)
        for j in range(h):
            for i in range(w): t.pt(x+i, y+j, f(i, j, w, h, "front"), True)
    corps = t.boite(*CORPS_W, cristal(70), force=True)
    for (x, y, w, h) in [corps[k] for k in ("right", "front", "left", "back")]:
        for (xx, yy, c) in [(x+i, y+j, t.get(x+i, y+j)) for j in range(h) for i in range(w)]:
            if sum(c[:3]) > 520: glow.append((xx, yy, c[:3]))               # les éclats du cristal brillent
    x, y, w, h = corps["front"]
    plaque(x, y, w, 3); plaque(x, y+18, w, 3, 0.45)                      # col et ceinture d'or
    for yy in range(3, 18): t.pt(x+1, y+yy, OR[3], True); t.pt(x+w-2, y+yy, OR[1], True)   # bretelles
    for yy in range(h):
        for xx in range(w):
            r = ((xx - 8.5)**2 + (yy - 9.5)**2) ** 0.5
            if 4.4 < r <= 5.8: t.pt(x+xx, y+yy, OR[5] if xx + yy < 18 else OR[1], True)
            elif r <= 4.4: lueur(x+xx, y+yy, VIOLET[0] if r < 1.8 else VIOLET[1] if r < 3.2 else VIOLET[2])
    for k in ("right", "left", "back"):
        x, y, w, h = corps[k]; plaque(x, y, w, 3); plaque(x, y+18, w, 3, 0.45)
    tete = t.boite(*TETE_W, cristal(71), force=True)
    for k in ("right", "front", "left", "back"):                          # masque d'or sur le haut de la tête
        x, y, w, h = tete[k]; plaque(x, y, w, 10)
    x, y, w, d = tete["up"]; plaque(x, y, w, d, 0.6)
    for yy in range(d): t.pt(x+w//2, y+yy, OR[5], True)
    x, y, w, h = tete["front"]
    t.rect(x+2, y+6, w-4, 2, (30, 10, 40), True)
    for xx in range(3, w-3): lueur(x+xx, y+6, VIOLET[0] if 5 <= xx <= w-6 else VIOLET[1]); lueur(x+xx, y+7, VIOLET[2])
    for (xx, yy) in ((2, 2), (w-3, 2), (w//2, 1)): t.pt(x+xx, y+yy, VIOLET[1], True)      # pierres serties
    xr, yr, wr, hr = COTES_W                                              # côtes : tuyaux d'or et lueur entre eux
    for xx in range(wr):
        for yy in range(hr):
            if xx % 2 == 0 and yy >= xx % 4: t.pt(xr+xx, yr+yy, OR[4] if yy == xx % 4 else OR[2], True)
            elif xx % 2 == 1: lueur(xr+xx, yr+yy, VIOLET[2] if yy > 10 else VIOLET[3])
    van = vanilla("warden/warden.png").load()
    for (u, v) in ((52, 32), (58, 0)):                                    # cornes : or ciselé, cœur de cristal lumineux
        for yy in range(16):
            for xx in range(16):
                if van[u+xx, v+yy][3] == 0: continue
                bord = any(not (0 <= u+xx+dx < 128 and 0 <= v+yy+dy < 128) or van[u+xx+dx, v+yy+dy][3] == 0
                           for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if bord: t.pt(u+xx, v+yy, OR[4] if yy < 8 else OR[2], True)
                else: lueur(u+xx, v+yy, VIOLET[0] if yy < 4 else VIOLET[1] if yy < 9 else VIOLET[2])
    for b in (BRAS_D, BRAS_G):                                            # bras : cristal, brassards et griffes d'or
        f = t.boite(*b, cristal(72), force=True)
        for k in ("right", "front", "left", "back"):
            x, y, w, h = f[k]
            plaque(x, y, w, 3); plaque(x, y+12, w, 11)                     # épaulière, brassard
            for yy in range(14, 22, 3):
                for xx in range(1, w-1): lueur(x+xx, y+yy, VIOLET[2]) if (xx + yy) % 3 == 0 else None   # filigrane lumineux
            for yy in range(24, 28):
                for xx in range(w): t.pt(x+xx, y+yy, OR[4] if xx % 2 else OR[1], True)   # griffes
        x, y, w, d = f["up"]
        for (cx, cy) in ((2, 2), (5, 4), (3, 6)):
            lueur(x+cx, y+cy, VIOLET[0]); lueur(x+cx+1, y+cy, VIOLET[1]); lueur(x+cx, y+cy+1, VIOLET[2])
    for b in (JAMBE_D, JAMBE_G):                                          # jambes : cristal et jambières d'or
        f = t.boite(*b, cristal(73), force=True)
        for k in ("right", "front", "left", "back"):
            x, y, w, h = f[k]; plaque(x, y+5, w, 8, 0.5)
            t.pt(x+w//2, y+8, VIOLET[1], True)
    calque = Image.new("RGBA", (128, 128), (0, 0, 0, 0)); p = calque.load()
    for (x, y, c) in glow: p[x, y] = tuple(c) + (255,)
    coeur = Image.new("RGBA", (128, 128), (0, 0, 0, 0)); pc = coeur.load()
    x, y, w, h = corps["front"]
    for (gx, gy, c) in glow:
        if x <= gx < x+w and y <= gy < y+h: pc[gx, gy] = tuple(c) + (255,)
    return t.im, calque, coeur, Image.new("RGBA", (128, 128), (0, 0, 0, 0))
