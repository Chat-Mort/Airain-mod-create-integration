"""Tableaux de l'Empire, deuxième version : résolution doublée (32 px par bloc), détails, ombrages et petits textes."""
import math, random
from PIL import Image, ImageDraw
from tableaux import (CREME, PAPIER, ENCRE, ROUGE, ROUGE2, BLEU_PLAN, BLEU_PLAN2, TRAIT, CREPUSCULE,
                      LAITON, CUIVRE, FER, SUIE, ramp, mix, OR, ECHO, LAQUE_ROUGE, TABLEAUX as T1, AUTEURS, AUTEURS_EN)

POLICE = {  # 3 x 5
 "A": ["010", "101", "111", "101", "101"], "B": ["110", "101", "110", "101", "110"], "C": ["011", "100", "100", "100", "011"],
 "D": ["110", "101", "101", "101", "110"], "E": ["111", "100", "110", "100", "111"], "F": ["111", "100", "110", "100", "100"],
 "G": ["011", "100", "101", "101", "011"], "H": ["101", "101", "111", "101", "101"], "I": ["111", "010", "010", "010", "111"],
 "L": ["100", "100", "100", "100", "111"], "M": ["101", "111", "111", "101", "101"], "N": ["101", "111", "111", "111", "101"],
 "O": ["010", "101", "101", "101", "010"], "P": ["110", "101", "110", "100", "100"], "R": ["110", "101", "110", "101", "101"],
 "S": ["011", "100", "010", "001", "110"], "T": ["111", "010", "010", "010", "010"], "U": ["101", "101", "101", "101", "111"],
 "V": ["101", "101", "101", "101", "010"], "Y": ["101", "101", "010", "010", "010"], "W": ["101", "101", "111", "111", "101"], "K": ["101", "110", "100", "110", "101"], "Z": ["111", "001", "010", "100", "111"], "'": ["010", "010", "000", "000", "000"],
 " ": ["000", "000", "000", "000", "000"], "9": ["111", "101", "111", "001", "111"], "4": ["101", "101", "111", "001", "001"],
}
def texte(d, x, y, s, c):
    for ch in s:
        g = POLICE.get(ch, POLICE[" "])
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == "1": d.point((x + i, y + j), fill=c)
        x += 4
def texte_centre(d, W, y, s, c): texte(d, (W - len(s)*4 + 1)//2, y, s, c)

def cadre(d, W, H, c1=LAITON[0], c2=LAITON[3], c3=LAITON[1]):
    d.rectangle([0, 0, W-1, H-1], outline=c1); d.rectangle([1, 1, W-2, H-2], outline=c2); d.rectangle([2, 2, W-3, H-3], outline=c3)
    for (x, y) in ((1, 1), (W-2, 1), (1, H-2), (W-2, H-2)): d.point((x, y), fill=LAITON[5])

def engrenage(d, cx, cy, r, c, ombre, clair, dents=10, trou=(40, 26, 16), rayons=True):
    for k in range(dents):
        a = 2*math.pi*k/dents
        pts = []
        for da, rr in ((-0.13, 0.86), (-0.08, 1.08), (0.08, 1.08), (0.13, 0.86)):
            pts.append((cx + math.cos(a + da)*r*rr, cy + math.sin(a + da)*r*rr))
        d.polygon(pts, fill=c)
    d.ellipse([cx - r*0.9, cy - r*0.9, cx + r*0.9, cy + r*0.9], fill=c)
    d.arc([cx - r*0.9, cy - r*0.9, cx + r*0.9, cy + r*0.9], 160, 290, fill=clair)
    d.arc([cx - r*0.9, cy - r*0.9, cx + r*0.9, cy + r*0.9], 340, 110, fill=ombre)
    if rayons and r > 6:
        d.ellipse([cx - r*0.62, cy - r*0.62, cx + r*0.62, cy + r*0.62], fill=trou)
        for k in range(5):
            a = 2*math.pi*k/5 + 0.3
            d.line([(cx, cy), (cx + math.cos(a)*r*0.62, cy + math.sin(a)*r*0.62)], fill=c, width=max(1, int(r*0.14)))
    d.ellipse([cx - r*0.24, cy - r*0.24, cx + r*0.24, cy + r*0.24], fill=c)
    d.ellipse([cx - r*0.1, cy - r*0.1, cx + r*0.1, cy + r*0.1], fill=trou)

def roue_couronnee(d, cx, cy, r, fond=ENCRE):
    engrenage(d, cx, cy, r, LAITON[3], LAITON[1], LAITON[5], dents=8, trou=fond)
    w = r*1.5; base = cy - r*1.0; top = cy - r*1.75
    d.rectangle([cx - w/2, base - r*0.2, cx + w/2, base], fill=OR[3])
    d.line([(cx - w/2, base), (cx + w/2, base)], fill=OR[1])
    for k in range(3):
        px = cx - w/2 + k*w/2
        d.polygon([(px - r*0.22, base - r*0.2), (px + r*0.22, base - r*0.2), (px, top)], fill=OR[4])
        d.point((px, top + r*0.12), fill=(220, 40, 40))
    d.point((cx, base - r*0.1), fill=(60, 140, 220))

def lignes(d, x0, y0, w, n, c, pas=3):
    rnd = random.Random(int(x0*7 + y0*13 + w))
    for i in range(n):
        x = x0
        while x < x0 + w - 2:
            l = rnd.randint(2, 6); d.line([(x, y0 + i*pas), (min(x0 + w - 1, x + l - 1), y0 + i*pas)], fill=c); x += l + 2

# ---------------------------------------------------------------- affiches
SLOGANS = {"baroque": "GLORY", "prairie_ride": "SERVE", "skull_and_roses": "TRANSFER", "owlemons": "UNITED",
           "backyard": "THE CORE BEATS", "burning_skull": "AWAKEN", "unpacked": "EMPEROR"}
def affiche(W, H, slogan="AIRAIN", fond=CREME, ray=ROUGE, sombre=False):
    im = Image.new("RGB", (W, H), fond); d = ImageDraw.Draw(im)
    cy = H*0.42; cx = W/2
    for k in range(20):
        a1, a2 = 2*math.pi*k/20, 2*math.pi*(k+0.5)/20; R = W + H
        d.polygon([(cx, cy), (cx + math.cos(a1)*R, cy + math.sin(a1)*R), (cx + math.cos(a2)*R, cy + math.sin(a2)*R)], fill=ray)
    for y in range(H):                                                       # vieillissement du papier
        for x in range(0, W, 7):
            if (x*31 + y*17) % 23 == 0: d.point((x, y), fill=mix(im.getpixel((x, y)), (120, 96, 60), 0.35))
    r = min(W, H)*0.24
    d.ellipse([cx - r*1.42, cy - r*1.42, cx + r*1.42, cy + r*1.42], fill=LAITON[1])
    d.ellipse([cx - r*1.32, cy - r*1.32, cx + r*1.32, cy + r*1.32], fill=ENCRE)
    roue_couronnee(d, cx, cy + r*0.2, r*0.78)
    bande = 11 if H >= 48 else 9
    if W >= 24:
        d.rectangle([3, H - bande - 3, W - 4, H - 4], fill=ENCRE)
        mots = slogan if len(slogan)*4 <= W - 8 else slogan.split()[0]
        texte_centre(d, W, H - bande + (bande - 5)//2 - 3, mots, OR[4] if sombre else CREME)
    cadre(d, W, H, ENCRE, ROUGE2, ENCRE)
    return im

# ---------------------------------------------------------------- scènes au crépuscule
def ciel(d, W, H, rnd):
    for y in range(H):
        d.line([(0, y), (W, y)], fill=ramp(CREPUSCULE, (y/H)**0.9))
    for _ in range(W*H//180):
        x, y = rnd.randrange(W), rnd.randrange(int(H*0.35))
        d.point((x, y), fill=(240, 220, 200))
    for _ in range(max(2, W//24)):                                             # nuages en bandes
        cx, cy, l = rnd.randrange(W), rnd.randrange(int(H*0.2), int(H*0.55)), rnd.randint(W//6, W//3)
        d.line([(cx, cy), (cx + l, cy)], fill=(232, 160, 120)); d.line([(cx + 2, cy + 1), (cx + l - 3, cy + 1)], fill=(170, 96, 90))

def ville(d, W, H, base, rnd, tour=True):
    x = 0
    while x < W:
        w = rnd.randint(max(4, W//12), max(6, W//6)); h = rnd.randint(H//8, H//3)
        d.rectangle([x, base - h, x + w, base], fill=(30, 24, 30))
        d.line([(x, base - h), (x + w, base - h)], fill=(70, 50, 56))
        if rnd.random() < 0.5:
            d.rectangle([x + 2, base - h - H//9, x + 4, base - h], fill=(30, 24, 30))
            for j in range(3):
                r = 1 + j; d.ellipse([x + 3 + j*2 - r, base - h - H//9 - j*4 - r, x + 3 + j*2 + r, base - h - H//9 - j*4 + r], fill=(150, 130, 130))
        for yy in range(base - h + 3, base - 2, 4):
            for xx in range(x + 2, x + w - 1, 3):
                if rnd.random() < 0.35: d.rectangle([xx, yy, xx + 1, yy + 1], fill=rnd.choice(((250, 200, 110), (240, 160, 70))))
        x += w + 1
    if tour:
        tx = W*0.64; th = H*0.6
        d.rectangle([tx - 5, base - th, tx + 5, base], fill=(22, 18, 24))
        d.ellipse([tx - 5, base - th + 3, tx + 5, base - th + 13], fill=CREME, outline=LAITON[2])
        d.line([(tx, base - th + 8), (tx, base - th + 5)], fill=ENCRE); d.line([(tx, base - th + 8), (tx + 3, base - th + 8)], fill=ENCRE)
        d.polygon([(tx - 7, base - th), (tx + 7, base - th), (tx, base - th - 12)], fill=CUIVRE[1])
        d.line([(tx, base - th - 12), (tx, base - th - 16)], fill=LAITON[4])

def dirigeable(d, cx, cy, s):
    d.ellipse([cx - s, cy - s*0.36, cx + s, cy + s*0.36], fill=(226, 208, 170), outline=(60, 44, 36))
    d.arc([cx - s, cy - s*0.36, cx + s, cy + s*0.36], 190, 340, fill=(248, 236, 210))
    for k in (-0.6, -0.2, 0.2, 0.6): d.line([(cx + k*s, cy - s*0.33), (cx + k*s, cy + s*0.33)], fill=(190, 170, 134))
    d.line([(cx - s, cy), (cx + s, cy)], fill=LAQUE_ROUGE[3])
    gy = cy + s*0.5
    for k in (-0.3, 0, 0.3): d.line([(cx + k*s, cy + s*0.3), (cx + k*s*0.8, gy)], fill=(60, 44, 36))
    d.rectangle([cx - s*0.35, gy, cx + s*0.35, gy + s*0.16], fill=LAITON[2], outline=(60, 44, 36))
    for k in range(4): d.point((cx - s*0.25 + k*s*0.17, gy + s*0.08), fill=(250, 200, 110))
    d.polygon([(cx + s*0.92, cy), (cx + s*1.28, cy - s*0.32), (cx + s*1.2, cy)], fill=LAQUE_ROUGE[3])
    d.polygon([(cx + s*0.92, cy), (cx + s*1.28, cy + s*0.32), (cx + s*1.2, cy)], fill=LAQUE_ROUGE[2])
    d.line([(cx - s*1.05, cy - s*0.15), (cx - s*1.05, cy + s*0.15)], fill=LAITON[4])

def scene(W, H, sujet, graine):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); rnd = random.Random(graine)
    ciel(d, W, H, rnd)
    sr = H*0.12; d.ellipse([W*0.12, H*0.14, W*0.12 + sr*2, H*0.14 + sr*2], fill=(252, 214, 130)); d.ellipse([W*0.12 + 2, H*0.14 + 2, W*0.12 + sr*2 - 2, H*0.14 + sr*2 - 2], fill=(255, 232, 170))
    base = int(H*0.8)
    if sujet == "dirigeable":
        ville(d, W, H, base, rnd)
        dirigeable(d, W*0.42, H*0.33, min(W*0.24, H*0.5))
        if W >= 64: dirigeable(d, W*0.83, H*0.18, min(W, H*2)*0.08)
        d.rectangle([0, base, W, H], fill=(24, 20, 26))
    elif sujet == "train":
        ville(d, W, H, base - 2, rnd, tour=False)
        d.rectangle([0, base, W, H], fill=(46, 36, 40))
        for x in range(0, W, 4): d.line([(x, base + 2), (x + 2, base + 2)], fill=(90, 70, 60))
        d.line([(0, base + 1), (W, base + 1)], fill=FER[5])
        lx, lw, lh = W*0.16, W*0.56, H*0.26
        d.rectangle([lx, base - lh, lx + lw*0.68, base - 4], fill=LAQUE_ROUGE[3], outline=ENCRE)
        d.line([(lx + 1, base - lh + 1), (lx + lw*0.68 - 1, base - lh + 1)], fill=LAQUE_ROUGE[5])
        d.ellipse([lx - lh*0.25, base - lh, lx + lh*0.25, base - 4], fill=SUIE[2], outline=ENCRE)       # avant de chaudière
        d.rectangle([lx + lw*0.68, base - lh*1.55, lx + lw, base - 4], fill=LAQUE_ROUGE[2], outline=ENCRE)
        d.rectangle([lx + lw*0.74, base - lh*1.4, lx + lw*0.92, base - lh*0.95], fill=(250, 200, 110))  # fenêtre
        d.rectangle([lx + lw*0.08, base - lh*1.6, lx + lw*0.18, base - lh], fill=SUIE[0])
        d.rectangle([lx + lw*0.06, base - lh*1.7, lx + lw*0.2, base - lh*1.6], fill=LAITON[3])
        for k in range(4):
            wx = lx + lw*(0.06 + k*0.24); r = lh*0.3
            d.ellipse([wx, base - 4 - r*2 + 4, wx + r*2, base + 4], fill=SUIE[0], outline=LAITON[3])
            d.line([(wx + r, base - r + 0), (wx + r*1.6, base - r*0.4)], fill=LAITON[4])
        d.line([(lx + lw*0.06 + lh*0.3, base - lh*0.1), (lx + lw*0.78, base - lh*0.1)], fill=LAITON[4])   # bielle
        for k in range(6):
            r = 2 + k; x = lx + lw*0.13 - k*W*0.05; y = base - lh*1.8 - k*H*0.05
            d.ellipse([x - r, y - r, x + r, y + r], fill=mix((214, 206, 200), (150, 120, 130), k/6))
    elif sujet == "usine":
        ville(d, W, H, base, rnd, tour=False)
        for k in range(4):
            x = W*(0.12 + 0.22*k); h = H*rnd.uniform(0.42, 0.62); w = max(4, W//14)
            d.rectangle([x, base - h, x + w, base], fill=(26, 20, 24))
            for j in range(0, int(h), 6): d.line([(x, base - h + j), (x + w, base - h + j)], fill=(56, 40, 44))
            d.rectangle([x - 1, base - h - 2, x + w + 1, base - h], fill=(60, 44, 46))
            d.point((x + w//2, base - h + 3), fill=(255, 140, 50))
            for j in range(6):
                r = 2 + j; cx = x + w/2 + j*3; cy = base - h - 4 - j*H*0.06
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix((200, 190, 186), (150, 110, 110), j/6))
        d.rectangle([0, base, W, H], fill=(24, 20, 26))
        for x in range(0, W, 5): d.point((x, base + 2), fill=(255, 150, 60))
    elif sujet == "navire":
        d.rectangle([0, base, W, H], fill=(30, 58, 70))
        for y in range(base + 1, H, 2):
            for x in range((y*3) % 5, W, 5): d.line([(x, y), (x + 2, y)], fill=(70, 110, 120))
        for x in range(int(W*0.1), int(W*0.4), 2): d.point((x, base + 2), fill=(250, 200, 120))      # reflet du soleil
        hx0, hx1 = W*0.18, W*0.82
        d.polygon([(hx0, base - 5), (hx1, base - 5), (hx1 - 6, base + 3), (hx0 + 4, base + 3)], fill=(96, 104, 112))
        d.rectangle([hx0 + 4, base, hx1 - 6, base + 3], fill=LAQUE_ROUGE[2])
        d.rectangle([W*0.38, base - H*0.2, W*0.6, base - 5], fill=(120, 128, 136))
        for x in range(int(W*0.4), int(W*0.58), 3): d.point((x, base - H*0.14), fill=(250, 210, 140))
        d.rectangle([W*0.45, base - H*0.34, W*0.5, base - H*0.2], fill=SUIE[0]); d.line([(W*0.45, base - H*0.3), (W*0.5, base - H*0.3)], fill=LAQUE_ROUGE[3])
        d.rectangle([W*0.24, base - 9, W*0.32, base - 5], fill=(80, 88, 96)); d.line([(W*0.32, base - 7), (W*0.38, base - 8)], fill=(60, 66, 72))
        for j in range(4):
            r = 2 + j; d.ellipse([W*0.475 - j*4 - r, base - H*0.36 - j*4 - r, W*0.475 - j*4 + r, base - H*0.36 - j*4 + r], fill=(180, 170, 176))
    else:
        ville(d, W, H, base, rnd)
        d.rectangle([0, base, W, H], fill=(24, 20, 26))
        for x in range(0, W, 3): d.point((x, base + 1), fill=(250, 190, 100))
    cadre(d, W, H)
    return im

# ---------------------------------------------------------------- plans
def plan(W, H, sujet, titre="PLAN"):
    im = Image.new("RGB", (W, H), BLEU_PLAN); d = ImageDraw.Draw(im)
    for x in range(0, W, 4): d.line([(x, 0), (x, H)], fill=BLEU_PLAN2)
    for y in range(0, H, 4): d.line([(0, y), (W, y)], fill=BLEU_PLAN2)
    for x in range(0, W, 16): d.line([(x, 0), (x, H)], fill=(52, 100, 170))
    for y in range(0, H, 16): d.line([(0, y), (W, y)], fill=(52, 100, 170))
    cx, cy, r = W/2, H*0.45, min(W, H)*0.3
    T = TRAIT; T2 = (150, 186, 226)
    if sujet == "engrenage":
        for k in range(12):
            a = 2*math.pi*k/12; pts = [(cx + math.cos(a + da)*r*rr, cy + math.sin(a + da)*r*rr) for da, rr in ((-0.12, 0.86), (-0.07, 1.08), (0.07, 1.08), (0.12, 0.86))]
            d.line(pts, fill=T)
        d.ellipse([cx - r*0.86, cy - r*0.86, cx + r*0.86, cy + r*0.86], outline=T); d.ellipse([cx - r*0.6, cy - r*0.6, cx + r*0.6, cy + r*0.6], outline=T2)
        d.ellipse([cx - r*0.2, cy - r*0.2, cx + r*0.2, cy + r*0.2], outline=T)
        d.line([(cx - r*1.3, cy), (cx + r*1.3, cy)], fill=T2); d.line([(cx, cy - r*1.3), (cx, cy + r*1.3)], fill=T2)
        d.line([(cx - r*1.08, cy + r*1.35), (cx + r*1.08, cy + r*1.35)], fill=T)
        d.line([(cx - r*1.08, cy + r*1.25), (cx - r*1.08, cy + r*1.45)], fill=T); d.line([(cx + r*1.08, cy + r*1.25), (cx + r*1.08, cy + r*1.45)], fill=T)
    elif sujet == "capsule":
        d.rounded_rectangle([cx - r*0.55, cy - r*1.15, cx + r*0.55, cy + r*1.15], radius=max(3, int(r*0.5)), outline=T)
        d.rounded_rectangle([cx - r*0.4, cy - r*1.0, cx + r*0.4, cy + r*1.0], radius=max(2, int(r*0.4)), outline=T2)
        d.ellipse([cx - r*0.25, cy - r*0.75, cx + r*0.25, cy - r*0.25], outline=T)
        for k in range(-2, 3): d.point((cx + k*r*0.12, cy + r*0.4), fill=T)
        d.line([(cx, cy + r*1.15), (cx, H - 12)], fill=T); d.line([(cx - 3, cy + r*1.15), (cx - 3, H - 12)], fill=T2)
        d.line([(cx + r*0.75, cy - r*1.15), (cx + r*0.75, cy + r*1.15)], fill=T2)
    else:
        bx, by, bw, bh = W*0.1, cy - r*0.5, W*0.62, r*0.9
        d.rectangle([bx, by, bx + bw, by + bh], outline=T); d.ellipse([bx - r*0.25, by, bx + r*0.25, by + bh], outline=T)
        d.rectangle([bx + bw, by - r*0.6, bx + bw + W*0.18, by + bh], outline=T)
        d.rectangle([bx + bw + 3, by - r*0.45, bx + bw + W*0.13, by - r*0.1], outline=T2)
        d.rectangle([bx + bw*0.12, by - r*0.7, bx + bw*0.22, by], outline=T)
        for k in range(4):
            wx = bx + bw*(0.08 + k*0.27); d.ellipse([wx, by + bh - 2, wx + r*0.55, by + bh + r*0.53], outline=T)
            d.point((wx + r*0.27, by + bh + r*0.26), fill=T)
        d.line([(bx, by + bh + r*0.75), (bx + bw + W*0.18, by + bh + r*0.75)], fill=T2)
    if W >= 32 and H >= 32:                                                    # cartouche
        cw, ch = min(W - 8, 4*len(titre) + 5), 9
        d.rectangle([W - cw - 4, H - ch - 4, W - 5, H - 5], outline=T)
        texte(d, W - cw - 1, H - ch - 2, titre, T)
    cadre(d, W, H, (10, 26, 54), T, (30, 60, 110))
    return im

# ---------------------------------------------------------------- capsules
def capsules(W, H):
    im = Image.new("RGB", (W, H), (26, 20, 24)); d = ImageDraw.Draw(im); rnd = random.Random(W*H)
    for y in range(H): d.line([(0, y), (W, y)], fill=mix((40, 30, 34), (16, 12, 16), y/H))
    cw = max(7, W//6); ch = max(16, int(H*0.38))
    for row in range(2):
        y = H*0.08 + row*(ch + 4)
        for k in range(2, W - cw, cw + 3):
            d.rounded_rectangle([k, y, k + cw, y + ch], radius=cw//2, fill=LAITON[2], outline=LAITON[0])
            d.line([(k + 2, y + cw//2), (k + 2, y + ch - cw//2)], fill=LAITON[4])
            d.ellipse([k + cw*0.22, y + ch*0.14, k + cw*0.78, y + ch*0.14 + cw*0.56], fill=(50, 30, 76), outline=LAITON[1])
            if rnd.random() < 0.35: d.point((k + cw//2, y + ch*0.14 + cw*0.28), fill=(200, 140, 250))
            d.rectangle([k + cw*0.35, y + ch*0.7, k + cw*0.65, y + ch*0.78], fill=LAITON[0])
            d.line([(k + cw//2, y + ch), (k + cw//2, y + ch + 3)], fill=CUIVRE[2])
    for k in range(4, W, cw + 3): d.line([(k + cw//2, H*0.08 + 2*ch + 7), (k + cw//2, H)], fill=CUIVRE[1])
    cadre(d, W, H)
    return im

# ---------------------------------------------------------------- Écho
def echo(W, H, graine, ames=False):
    im = Image.new("RGB", (W, H), (12, 4, 22)); d = ImageDraw.Draw(im); rnd = random.Random(graine)
    cx, cy = W/2, H/2; R = min(W, H)/2
    for k in range(W*H//3):
        bras = rnd.randrange(3); t = rnd.random()
        a = bras*2*math.pi/3 + t*4.2 + rnd.uniform(-0.25, 0.25); r = t*R
        x, y = cx + math.cos(a)*r, cy + math.sin(a)*r
        if 0 <= x < W and 0 <= y < H: d.point((x, y), fill=mix(ramp(ECHO, 1 - t), im.getpixel((int(x), int(y))), 0.3))
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(200, 140, 255)); d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 240, 255))
    if ames:
        for k in range(5):
            a = 2*math.pi*k/5; x, y = cx + math.cos(a)*R*0.62, cy + math.sin(a)*R*0.62
            d.ellipse([x - 3, y - 4, x + 3, y + 2], fill=(220, 190, 255)); d.polygon([(x - 3, y), (x + 3, y), (x, y + 7)], fill=(170, 120, 230))
            d.point((x - 1, y - 2), fill=(60, 20, 90)); d.point((x + 1, y - 2), fill=(60, 20, 90))
    cadre(d, W, H, (30, 12, 50), (130, 70, 190), (60, 26, 96))
    return im

# ---------------------------------------------------------------- portrait d'automate
def buste(W, H):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H): d.line([(0, y), (W, y)], fill=mix((70, 50, 40), (26, 18, 16), y/H))
    s = min(W, H); hx, hy = W/2, H*0.4
    d.rectangle([hx - s*0.36, H*0.7, hx + s*0.36, H], fill=LAITON[1])                                # épaules
    d.line([(hx - s*0.36, H*0.7), (hx + s*0.36, H*0.7)], fill=LAITON[4])
    for k in (-0.24, 0.24): engrenage(d, hx + k*s, H*0.82, s*0.08, LAITON[3], LAITON[0], LAITON[5], dents=8, rayons=False)
    d.rectangle([hx - s*0.07, hy + s*0.2, hx + s*0.07, H*0.7], fill=FER[2])                          # cou
    for j in range(int(hy + s*0.22), int(H*0.7), 2): d.line([(hx - s*0.07, j), (hx + s*0.07, j)], fill=FER[1])
    d.rectangle([hx - s*0.2, hy - s*0.24, hx + s*0.2, hy + s*0.22], fill=LAITON[3], outline=LAITON[0])   # tête
    d.line([(hx - s*0.19, hy - s*0.23), (hx + s*0.19, hy - s*0.23)], fill=LAITON[5])
    d.rectangle([hx - s*0.16, hy - s*0.06, hx + s*0.16, hy + s*0.02], fill=SUIE[0])                 # visière
    for k in (-0.09, 0.09): d.rectangle([hx + k*s - 1, hy - s*0.04, hx + k*s + 1, hy], fill=(255, 170, 60))
    for j in range(3): d.line([(hx - s*0.1, hy + s*0.08 + j*2), (hx + s*0.1, hy + s*0.08 + j*2)], fill=LAITON[0])   # grille
    for (x, y) in ((-0.17, -0.2), (0.17, -0.2), (-0.17, 0.18), (0.17, 0.18)): d.point((hx + x*s, hy + y*s), fill=LAITON[5])
    d.rectangle([hx - s*0.03, hy - s*0.36, hx + s*0.03, hy - s*0.24], fill=CUIVRE[2])                 # antenne
    d.ellipse([hx - s*0.04, hy - s*0.4, hx + s*0.04, hy - s*0.33], fill=(255, 120, 60))
    cadre(d, W, H, OR[0], OR[3], OR[1])
    return im

def engrenages(W, H, graine):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); rnd = random.Random(graine)
    for y in range(H): d.line([(0, y), (W, y)], fill=mix((70, 46, 30), (34, 22, 16), y/H))
    for k in range(max(3, W*H//500)):
        cx, cy, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(min(W, H)*0.1, min(W, H)*0.28)
        pal = rnd.choice((LAITON, CUIVRE, LAITON, FER))
        engrenage(d, cx, cy, r, pal[3], pal[1], pal[5], dents=rnd.choice((8, 10, 12)), trou=(30, 20, 14))
    cadre(d, W, H)
    return im

def icone(W, H, n):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    fonds = [CREME, (40, 30, 26), BLEU_PLAN, (14, 6, 24), ROUGE, (40, 30, 26), (60, 44, 32), (14, 6, 24)]
    d.rectangle([0, 0, W, H], fill=fonds[n])
    c = W/2
    if n == 0: roue_couronnee(d, c, c + 3, 8, fond=CREME)
    elif n == 1:
        d.rounded_rectangle([10, 3, 21, 28], radius=5, fill=LAITON[2], outline=LAITON[0]); d.line([(12, 8), (12, 24)], fill=LAITON[4])
        d.ellipse([12, 7, 19, 14], fill=(50, 30, 76), outline=LAITON[1]); d.point((15, 10), fill=(220, 170, 255))
        d.line([(15, 28), (15, 31)], fill=CUIVRE[2])
    elif n == 2:
        return plan(W, H, "engrenage", "")
    elif n == 3:
        return echo(W, H, 31)
    elif n == 4:
        d.ellipse([5, 5, 26, 26], fill=OR[3], outline=OR[1]); d.ellipse([9, 9, 22, 22], fill=ROUGE2); roue_couronnee(d, c, c + 2, 4, fond=ROUGE2)
    elif n == 5:
        return buste(W, H)
    elif n == 6:
        d.rectangle([0, 18, W, 23], fill=CUIVRE[2]); d.line([(0, 18), (W, 18)], fill=CUIVRE[4]); d.line([(0, 23), (W, 23)], fill=CUIVRE[0])
        d.rectangle([13, 10, 18, 18], fill=FER[3]); d.ellipse([7, 3, 24, 11], outline=(200, 40, 28)); d.line([(15, 3), (15, 11)], fill=(200, 40, 28)); d.line([(7, 7), (24, 7)], fill=(200, 40, 28))
        for x in (4, 27): d.rectangle([x - 1, 16, x + 1, 25], fill=LAITON[3])
    else:
        d.polygon([(16, 3), (22, 15), (16, 28), (10, 15)], fill=(150, 80, 220)); d.polygon([(16, 3), (22, 15), (16, 15)], fill=(200, 140, 250))
        d.line([(16, 5), (16, 26)], fill=(240, 210, 255)); d.polygon([(8, 20), (11, 26), (6, 27)], fill=(120, 60, 190))
    cadre(d, W, H)
    return im

# ---------------------------------------------------------------- attribution (taille x2)
X2 = {
 "alban": lambda: icone(32, 32, 0), "aztec": lambda: icone(32, 32, 1), "aztec2": lambda: icone(32, 32, 2), "bomb": lambda: icone(32, 32, 3),
 "kebab": lambda: icone(32, 32, 4), "meditative": lambda: icone(32, 32, 5), "plant": lambda: icone(32, 32, 6), "wasteland": lambda: icone(32, 32, 7),
 "graham": lambda: plan(32, 64, "capsule", "N4"), "prairie_ride": lambda: affiche(32, 64, SLOGANS["prairie_ride"]), "wanderer": lambda: buste(32, 64),
 "courbet": lambda: scene(64, 32, "train", 1), "creebet": lambda: scene(64, 32, "usine", 2), "pool": lambda: scene(64, 32, "navire", 3),
 "sea": lambda: plan(64, 32, "locomotive", "LINE"), "sunset": lambda: scene(64, 32, "dirigeable", 4),
 "baroque": lambda: affiche(64, 64, SLOGANS["baroque"]), "bust": lambda: buste(64, 64), "earth": lambda: echo(64, 64, 5),
 "fire": lambda: scene(64, 64, "usine", 6), "humble": lambda: plan(64, 64, "engrenage", "GEAR"), "match": lambda: engrenages(64, 64, 7),
 "skull_and_roses": lambda: affiche(64, 64, SLOGANS["skull_and_roses"], fond=(34, 28, 26), ray=(70, 50, 34), sombre=True),
 "stage": lambda: capsules(64, 64), "void": lambda: echo(64, 64, 8), "water": lambda: scene(64, 64, "navire", 9),
 "wind": lambda: scene(64, 64, "dirigeable", 10), "wither": lambda: plan(64, 64, "capsule", "PROTO"),
 "bouquet": lambda: engrenages(96, 96, 11), "cavebird": lambda: scene(96, 96, "dirigeable", 12), "cotan": lambda: buste(96, 96),
 "endboss": lambda: echo(96, 96, 13, ames=True), "fern": lambda: plan(96, 96, "engrenage", "THEORY"),
 "owlemons": lambda: affiche(96, 96, SLOGANS["owlemons"]), "sunflowers": lambda: scene(96, 96, "usine", 14), "tides": lambda: scene(96, 96, "navire", 15),
 "backyard": lambda: affiche(96, 128, SLOGANS["backyard"]), "pond": lambda: capsules(96, 128),
 "changing": lambda: scene(128, 64, "train", 16), "fighters": lambda: scene(128, 64, "dirigeable", 17), "finding": lambda: plan(128, 64, "locomotive", "LINE 9"),
 "lowmist": lambda: scene(128, 64, "usine", 18), "passage": lambda: capsules(128, 64),
 "donkey_kong": lambda: scene(128, 96, "ville", 19), "skeleton": lambda: engrenages(128, 96, 20),
 "burning_skull": lambda: affiche(128, 128, SLOGANS["burning_skull"], fond=(34, 28, 26), ray=(100, 34, 26), sombre=True),
 "orb": lambda: echo(128, 128, 21, ames=True), "pigscene": lambda: scene(128, 128, "dirigeable", 22),
 "pointer": lambda: plan(128, 128, "engrenage", "AIRAIN CORE"), "unpacked": lambda: affiche(128, 128, SLOGANS["unpacked"]),
}
