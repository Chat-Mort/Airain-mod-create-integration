"""Le Gardien des profondeurs, version mécanique : blindage de fonte, cœur d'Écho, côtes en tuyaux d'orgue, bras à vérins."""
from atelier import *

CORPS_W, TETE_W = (0, 0, 18, 21, 11), (0, 32, 16, 16, 10)
BRAS_D, BRAS_G = (44, 50, 8, 28, 8), (0, 58, 8, 28, 8)
JAMBE_D, JAMBE_G = (76, 48, 6, 13, 6), (76, 76, 6, 13, 6)
COTES_W = (90, 11, 9, 21)
VIOLET = [(250, 220, 255), (214, 150, 255), (170, 90, 240), (110, 40, 180)]

def blindage(pal, base=0.4, pas=6, graine=60):
    m = metal(pal, base, 0.05, graine=graine)
    def f(i, j, w, h, face):
        c = m(i, j, w, h, face)
        if i % pas == 0 or j % pas == 0: c = pal[0]                       # joints des plaques
        if i % pas == 3 and j % pas == 2: c = LAITON[4]                   # rivets
        return c
    return f

def peindre():
    t = Toile((128, 128)); glow = []                                      # glow : pixels qui brillent (calques émissifs)
    def lueur(x, y, c): t.pt(x, y, c, True); glow.append((x, y, c))
    corps = t.boite(*CORPS_W, blindage(FER, 0.38), force=True)
    x, y, w, h = corps["front"]                                           # hublot du cœur d'Écho
    for yy in range(h):
        for xx in range(w):
            r = ((xx - 8.5)**2 + (yy - 8.5)**2) ** 0.5
            if 4.6 < r <= 6.2: t.pt(x+xx, y+yy, LAITON[5] if xx + yy < 17 else LAITON[1], True)
            elif r <= 4.6: lueur(x+xx, y+yy, VIOLET[0] if r < 1.6 else VIOLET[1] if r < 3 else VIOLET[2])
    for xx in range(2, 16, 3): t.pt(x+xx, y+17, BRAISE[3], True)          # grille de ventilation
    x, y, w, h = corps["back"]                                            # dos : deux cheminées
    for cx in (4, 13):
        for yy in range(h): t.pt(x+cx, y+yy, FER[3], True); t.pt(x+cx+1, y+yy, FER[1], True)
        lueur(x+cx, y, VIOLET[2]); lueur(x+cx+1, y, VIOLET[3])
    tete = t.boite(*TETE_W, blindage(FER, 0.42, pas=8, graine=61), force=True)
    x, y, w, h = tete["front"]                                            # casque sans visage, visière lumineuse
    t.rect(x+1, y+6, w-2, 4, FER[0], True)
    for xx in range(2, w-2): lueur(x+xx, y+7, VIOLET[1] if 4 <= xx <= w-5 else VIOLET[2]); lueur(x+xx, y+8, VIOLET[2])
    for xx in range(3, w-3, 2): t.pt(x+xx, y+12, LAITON[3], True)         # grille de mâchoire
    x, y, w, d = tete["up"]
    for yy in range(d): t.pt(x+7, y+yy, LAITON[4], True); t.pt(x+8, y+yy, LAITON[2], True)   # crête
    xr, yr, wr, hr = COTES_W                                              # côtes -> tuyaux d'orgue
    for xx in range(wr):
        for yy in range(hr):
            if xx % 2 == 0 and yy >= xx % 4: t.pt(xr+xx, yr+yy, LAITON[4] if yy == xx % 4 else LAITON[2] if xx % 4 == 0 else LAITON[3], True)
            elif xx % 2 == 1 and yy > hr - 6: lueur(xr+xx, yr+yy, VIOLET[3])
    van = vanilla("warden/warden.png").load()
    for (u, v) in ((52, 32), (58, 0)):                                    # cornes : forme d'origine, laiton creux rempli d'Écho
        for yy in range(16):
            for xx in range(16):
                if van[u+xx, v+yy][3] == 0: continue
                bord = any(not (0 <= u+xx+dx < 128 and 0 <= v+yy+dy < 128) or van[u+xx+dx, v+yy+dy][3] == 0
                           for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if bord: t.pt(u+xx, v+yy, LAITON[4] if yy < 8 else LAITON[2], True)
                else: lueur(u+xx, v+yy, VIOLET[0] if yy < 4 else VIOLET[1] if yy < 9 else VIOLET[2])
    for b in (BRAS_D, BRAS_G):                                            # bras à vérins
        f = t.boite(*b, blindage(FER, 0.36, pas=7, graine=62), force=True)
        for k in COTES:
            x, y, w, h = f[k]
            for yy in range(10, 20):
                for xx in range(2, 6): t.pt(x+xx, y+yy, CHROME[4] if xx == 2 else CHROME[2] if xx < 5 else CHROME[0], True)   # tige de vérin
            t.ligne_h(x, y+9, w, LAITON[4], True); t.ligne_h(x, y+20, w, LAITON[2], True)
            for yy in range(24, 28):
                for xx in range(w): t.pt(x+xx, y+yy, FER[0] if xx % 2 else FER[3], True)   # griffes
    for b in (JAMBE_D, JAMBE_G):
        f = t.boite(*b, blindage(FER, 0.34, pas=6, graine=63), force=True)
        for k in COTES:
            x, y, w, h = f[k]
            for yy in range(3, 9): t.pt(x+2, y+yy, CHROME[4], True); t.pt(x+3, y+yy, CHROME[2], True)
            t.ligne_h(x, y+2, w, LAITON[3], True)
    RUNES = [["X.X", ".X.", "X.X"], ["XXX", "X..", "XXX"], [".X.", "XXX", ".X."], ["X..", "XXX", "..X"], ["XX.", ".X.", ".XX"]]
    def rune(x0, y0, n):
        for j, ligne in enumerate(RUNES[n % len(RUNES)]):
            for i, ch in enumerate(ligne):
                if ch == "X": lueur(x0+i, y0+j, VIOLET[2])
    n = 0
    for k in ("right", "left"):                                           # runes gravées sur les flancs et la tête
        x, y, w, h = corps[k]; rune(x+4, y+3, n); rune(x+4, y+13, n+1); n += 2
        x, y, w, h = tete[k]; rune(x+3, y+3, n); n += 1
    x, y, w, h = corps["back"]; rune(x+7, y+8, n); rune(x+7, y+14, n+2)
    for b in (BRAS_D, BRAS_G):
        f = faces(*b)
        for k in COTES:
            x, y, w, h = f[k]; rune(x+2, y+3, n); n += 1
            for xx in range(w): lueur(x+xx, y+21, VIOLET[3])               # veine d'Écho sous le vérin
        x, y, w, d = f["up"]                                              # cristaux d'améthyste sur les épaules
        for (cx, cy) in ((2, 2), (5, 4), (3, 6)):
            lueur(x+cx, y+cy, VIOLET[0]); lueur(x+cx+1, y+cy, VIOLET[1]); lueur(x+cx, y+cy+1, VIOLET[2])
    x, y, w, h = corps["front"]                                           # veines qui partent du cœur
    for (dx, dy) in ((1, 0), (-1, 0), (0, 1)):
        for k in range(7, 12):
            gx, gy = int(8.5 + dx*k), int(8.5 + dy*k)
            if 0 <= gx < w and 0 <= gy < h: lueur(x+gx, y+gy, VIOLET[2])
    calque = Image.new("RGBA", (128, 128), (0, 0, 0, 0)); p = calque.load()
    for (x, y, c) in glow: p[x, y] = c + (255,)
    coeur = Image.new("RGBA", (128, 128), (0, 0, 0, 0)); pc = coeur.load()
    x, y, w, h = corps["front"]
    for (gx, gy, c) in glow:
        if x <= gx < x+w and y <= gy < y+h: pc[gx, gy] = c + (255,)
    vide = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    return t.im, calque, coeur, vide
