from atelier import *

def coffre_noir():
    """Option 1 : coffre-fort victorien, émail noir, filets et lettrage d'or, cadran de laiton."""
    t = Toile((64, 64))
    email = lambda i, j, w, h, f: OR[3] if (i in (1, w-2) or j in (1, h-2)) and 0 < i < w-1 and 0 < j < h-1 else ramp(EMAIL_NOIR, 0.3 + 0.25*(j == 0))
    c = t.boite(0, 0, 16, 12, 16, email, force=True); s = t.boite(0, 28, 16, 8, 16, email, force=True)
    x, y, _, _ = c["front"]
    t.disque(x+8, y+6, 4.4, lambda r, a: LAITON[4] if r > 3.4 else (LAITON[1] if int(a) % 30 < 6 else (230, 220, 200)) if r > 2.2 else LAITON[3] if r > 1 else FER[0], True)
    for k in ("right", "left", "back"):
        x, y, w, h = c[k]
        for i in range(3, w-3, 2): t.pt(x+i, y+5, OR[4], True)                                  # lettrage stylisé
    x, y, w, d = c["up"]
    for (i, j) in ((3, 3), (12, 3), (3, 12), (12, 12)): t.disque(x+i, y+j, 1.2, lambda r, a: LAITON[4], True)
    tete = t.boite(0, 52, 6, 6, 6, metal(FER, 0.35, 0.04), force=True)
    x, y, _, _ = tete["front"]; t.cadre(x+1, y+1, 4, 4, LAITON[4], LAITON[1], True); t.rect(x+2, y+2, 2, 2, (255, 170, 60), True)
    return t.im

def capsule():
    """Option 2 : une capsule du Transfert (laiton, hublot) ; dedans, un visage pâle d'Écho."""
    t = Toile((64, 64))
    def plaque(i, j, w, h, f):
        c = ramp(LAITON, 0.55 + 0.1*(j == 0) - 0.12*(j == h-1) - 0.04*((i//4) % 2))
        if i % 4 == 0: c = LAITON[1]
        if i % 4 == 0 and j % 3 == 1: c = LAITON[5]
        return c
    c = t.boite(0, 0, 16, 12, 16, plaque, force=True); s = t.boite(0, 28, 16, 8, 16, plaque, force=True)
    for k in COTES:
        x, y, w, h = s[k]; t.ligne_h(x, y, w, CUIVRE[3], True); t.ligne_h(x, y+h-1, w, CUIVRE[0], True)   # joint de cuivre
    x, y, _, _ = c["front"]
    t.disque(x+8, y+6, 4.6, lambda r, a: (LAITON[5] if a > 180 else LAITON[0]) if r > 3.5 else (60, 30, 90) if r > 2.6 else (150, 110, 200) if r > 1.2 else (220, 190, 255), True)   # hublot violet
    for k in ("right", "left", "back"):
        x, y, w, h = c[k]
        for i in range(2, w-2, 3): t.pt(x+i, y+4, (40, 20, 60), True); t.pt(x+i, y+5, ECHO[3], True)   # câbles
    x, y, w, d = c["up"]
    t.disque(x+8, y+8, 3, lambda r, a: CUIVRE[2] if r > 2 else LAITON[5], True)
    tete = t.boite(0, 52, 6, 6, 6, lambda i, j, w, h, f: ramp(ECHO, 0.55 + 0.15*(j < 2)), force=True)
    x, y, _, _ = tete["front"]
    for (i, j, cc) in ((1, 2, (255, 255, 255)), (4, 2, (255, 255, 255)), (2, 4, ECHO[1]), (3, 4, ECHO[1])): t.pt(x+i, y+j, cc, True)
    return t.im

def tourelle():
    """Option 3 : une tourelle de défense, dôme d'acier sombre, meurtrière et lentille rouge."""
    t = Toile((64, 64))
    acier = lambda i, j, w, h, f: ramp(GRIS_NAVAL, 0.3 + 0.12*(j == 0) - 0.1*(j == h-1) + 0.05*((i//4) % 2))
    c = t.boite(0, 0, 16, 12, 16, acier, force=True); s = t.boite(0, 28, 16, 8, 16, lambda i, j, w, h, f: (240, 196, 30) if ((i+j)//2) % 2 and f not in ("up", "down") else ramp(FER, 0.3), force=True)
    for k in COTES:
        x, y, w, h = c[k]
        t.rect(x+2, y+5, w-4, 2, FER[0], True)                                                    # meurtrière
        for i in (1, w-2): t.rivet(x+i, y+1, NICKEL, True); t.rivet(x+i, y+h-2, NICKEL, True)
    x, y, _, _ = c["front"]; t.rect(x+7, y+5, 2, 2, (255, 40, 30), True)
    x, y, w, d = c["up"]
    t.disque(x+8, y+8, 4, lambda r, a: GRIS_NAVAL[1] if r > 3 else GRIS_NAVAL[3], True)
    tete = t.boite(0, 52, 6, 6, 6, metal(FER, 0.3, 0.04), force=True)
    x, y, _, _ = tete["front"]; t.disque(x+3, y+3, 2, lambda r, a: (255, 60, 40) if r < 1 else (140, 20, 14), True)
    return t.im
