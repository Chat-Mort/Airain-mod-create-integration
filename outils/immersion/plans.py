"""Tableaux v6 : tous les tableaux (sauf les quatre conservés) deviennent des plans d'ingénieur,
chacun d'un élément steampunk différent. 64 px par bloc."""
import math, random
from PIL import Image, ImageDraw
from tableaux2 import POLICE, texte, BLEU_PLAN, BLEU_PLAN2, TRAIT, mix, ramp
from tableaux4 import texte2
import lot1c  # complète la police (chiffres, ponctuation)

T, T2, T3, R = TRAIT, (150, 186, 226), (96, 140, 200), (232, 112, 92)
FOND1, FOND2 = BLEU_PLAN2, BLEU_PLAN

# ------------------------------------------------------------------ pinceau en coordonnées unitaires
class P:
    def __init__(s, d, x, y, w, h): s.d, s.x, s.y, s.w, s.h = d, x, y, w, h
    def X(s, u): return s.x + u*s.w
    def Y(s, v): return s.y + v*s.h
    def pt(s, u, v): return (s.X(u), s.Y(v))
    def L(s, pts, c=T, w=1): s.d.line([s.pt(*p) for p in pts], fill=c, width=w)
    def poly(s, pts, c=T): s.d.polygon([s.pt(*p) for p in pts], outline=c)
    def R(s, u0, v0, u1, v1, c=T): s.d.rectangle([s.X(u0), s.Y(v0), s.X(u1), s.Y(v1)], outline=c)
    def E(s, cu, cv, ru, rv, c=T): s.d.ellipse([s.X(cu - ru), s.Y(cv - rv), s.X(cu + ru), s.Y(cv + rv)], outline=c)
    def C(s, cu, cv, r, c=T):  # r en fraction de la largeur
        x, y, rr = s.X(cu), s.Y(cv), r*s.w; s.d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=c)
    def A(s, cu, cv, r, a0, a1, c=T):
        x, y, rr = s.X(cu), s.Y(cv), r*s.w; s.d.arc([x - rr, y - rr, x + rr, y + rr], a0, a1, fill=c)
    def pix(s, u, v, c=T): s.d.point(s.pt(u, v), fill=c)
    def hachures(s, u0, v0, u1, v1, c=T3, pas=3):
        x0, y0, x1, y1 = s.X(u0), s.Y(v0), s.X(u1), s.Y(v1)
        for k in range(int(x0 - (y1 - y0)), int(x1), pas):
            a = (max(x0, k), y0 + max(0, x0 - k)); b = (min(x1, k + (y1 - y0)), y0 + min(y1 - y0, x1 - k))
            if a[0] <= b[0]: s.d.line([a, b], fill=c)
    def gear(s, cu, cv, r, dents=12, c=T, c2=T2, moyeu=0.3):
        x, y, rr = s.X(cu), s.Y(cv), r*s.w; pts = []
        for k in range(dents):
            a = 2*math.pi*k/dents
            for da, f in ((-0.32, 0.82), (-0.18, 1.0), (0.18, 1.0), (0.32, 0.82)):
                b = a + da*2*math.pi/dents; pts.append((x + math.cos(b)*rr*f, y + math.sin(b)*rr*f))
        s.d.polygon(pts, outline=c)
        s.d.ellipse([x - rr*0.66, y - rr*0.66, x + rr*0.66, y + rr*0.66], outline=c2)
        s.d.ellipse([x - rr*moyeu, y - rr*moyeu, x + rr*moyeu, y + rr*moyeu], outline=c)
        if rr > 9:
            for k in range(5):
                a = 2*math.pi*k/5 + 0.3; s.d.line([(x + math.cos(a)*rr*moyeu, y + math.sin(a)*rr*moyeu), (x + math.cos(a)*rr*0.66, y + math.sin(a)*rr*0.66)], fill=c2)
    def rivets(s, u0, v0, u1, v1, n, c=T2):
        for k in range(n): t = k/max(1, n - 1); s.pix(u0 + (u1 - u0)*t, v0 + (v1 - v0)*t, c)
    def ressort(s, u0, v0, u1, v1, n=8, amp=0.03, c=T2):
        pts = []
        for k in range(n*2 + 1):
            t = k/(n*2); du, dv = u1 - u0, v1 - v0; l = math.hypot(du*s.w, dv*s.h) or 1
            nu, nv = -dv*s.h/l/s.w, du*s.w/l/s.h; o = amp*(1 if k % 2 else -1)*(0 if k in (0, n*2) else 1)
            pts.append((u0 + du*t + nu*o, v0 + dv*t + nv*o))
        s.L(pts, c)
    def roue(s, cu, cv, r, rayons=8, c=T, c2=T2):
        s.C(cu, cv, r, c); s.C(cu, cv, r*0.82, c2); s.C(cu, cv, r*0.15, c)
        for k in range(rayons):
            a = 2*math.pi*k/rayons; s.d.line([(s.X(cu) + math.cos(a)*r*s.w*0.15, s.Y(cv) + math.sin(a)*r*s.w*0.15), (s.X(cu) + math.cos(a)*r*s.w*0.82, s.Y(cv) + math.sin(a)*r*s.w*0.82)], fill=c2)

def tampon(d, x, y, mot, c=R, r=11):
    d.ellipse([x - r, y - r, x + r, y + r], outline=c); d.ellipse([x - r + 2, y - r + 2, x + r - 2, y + r - 2], outline=c)
    texte(d, int(x - len(mot)*2 + 1), int(y - 2), mot, c)

def cote_h(d, x0, x1, y, txt, c=T2):
    d.line([(x0, y), (x1, y)], fill=c); d.line([(x0, y - 2), (x0, y + 2)], fill=c); d.line([(x1, y - 2), (x1, y + 2)], fill=c)
    d.polygon([(x0 + 1, y), (x0 + 4, y - 2), (x0 + 4, y + 2)], fill=c); d.polygon([(x1 - 1, y), (x1 - 4, y - 2), (x1 - 4, y + 2)], fill=c)
    tw = len(txt)*4; xm = (x0 + x1)/2 - tw/2
    d.rectangle([xm - 1, y - 3, xm + tw - 1, y + 3], fill=FOND1); texte(d, int(xm), y - 2, txt, c)
def cote_v(d, x, y0, y1, txt, c=T2):
    d.line([(x, y0), (x, y1)], fill=c); d.line([(x - 2, y0), (x + 2, y0)], fill=c); d.line([(x - 2, y1), (x + 2, y1)], fill=c)
    d.polygon([(x, y0 + 1), (x - 2, y0 + 4), (x + 2, y0 + 4)], fill=c); d.polygon([(x, y1 - 1), (x - 2, y1 - 4), (x + 2, y1 - 4)], fill=c)
    ym = (y0 + y1)/2
    for i, ch in enumerate(txt):
        d.rectangle([x - 2, ym - len(txt)*3 + i*6 - 1, x + 2, ym - len(txt)*3 + i*6 + 5], fill=FOND1); texte(d, x - 1, int(ym - len(txt)*3 + i*6), ch, c)

def fond(W, H, graine):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H): d.line([(0, y), (W, y)], fill=mix(FOND1, FOND2, y/H))
    for k in range(0, max(W, H), 4):
        c = (52, 100, 170) if k % 16 == 0 else (38, 84, 150)
        d.line([(k, 0), (k, H)], fill=c); d.line([(0, k), (W, k)], fill=c)
    rnd = random.Random(graine)
    for _ in range(W*H//3000):                                                  # usure du papier
        x, y, r = rnd.randrange(W), rnd.randrange(H), rnd.randint(6, 16); d.ellipse([x - r, y - r*0.8, x + r, y + r*0.8], outline=(44, 90, 158))
    px = im.load()
    for _ in range(W*H//14):
        x, y = rnd.randrange(W), rnd.randrange(H); r, g, b = px[x, y]; n = rnd.randint(-6, 6); px[x, y] = (r + n//2, g + n, b + n)
    return im, d

def cadre(d, W, H):
    d.rectangle([0, 0, W - 1, H - 1], outline=(18, 36, 74)); d.rectangle([1, 1, W - 2, H - 2], outline=T2); d.rectangle([2, 2, W - 3, H - 3], outline=(18, 36, 74))
    d.rectangle([4, 4, W - 5, H - 5], outline=T3)
    for (x, y) in ((4, 4), (W - 5, 4), (4, H - 5), (W - 5, H - 5)): d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=T2)

# ------------------------------------------------------------------ mise en page d'une planche
def planche(W, H, sujet, graine=0):
    titre, ar, dessin, legende, extra = SUJETS[sujet]
    im, d = fond(W, H, graine)
    petit = W < 128 or H < 128
    m = 7
    bande = 9 if (petit and H < 128) else (11 if petit else 24)
    zx0, zy0, zx1, zy1 = m + (0 if petit else 9), m + (0 if petit else 8), W - m - (0 if petit else 6), H - m - bande - 2
    zw, zh = zx1 - zx0, zy1 - zy0
    if zw/zh > ar: bh = zh; bw = bh*ar
    else: bw = zw; bh = bw/ar
    bx, by = zx0 + (zw - bw)/2, zy0 + (zh - bh)/2
    from PIL import ImageFilter
    calque = Image.new("RGB", (W, H)); dc = ImageDraw.Draw(calque)
    dessin(P(dc, bx, by, bw, bh))
    if min(W, H) >= 192: calque = calque.filter(ImageFilter.MaxFilter(3))
    masque = calque.convert("L").point(lambda v: 255 if v > 20 else 0)
    im.paste(calque, (0, 0), masque); d = ImageDraw.Draw(im)
    p = P(d, bx, by, bw, bh)
    d.line([(bx + bw/2, by - 3), (bx + bw/2, by - 1)], fill=T3); d.line([(bx - 3, by + bh/2), (bx - 1, by + bh/2)], fill=T3)  # axes
    rnd = random.Random(graine*7 + 3)
    if not petit:
        ech = 10*rnd.choice((2, 3, 4, 5, 6))
        cote_h(d, int(bx), int(bx + bw), int(zy0 - 3), str(int(ech*ar)))
        cote_v(d, int(zx0 - 4), int(by), int(by + bh), str(ech))
        for i, (u, v, lab) in enumerate(legende[:4]):                          # repères
            x, y = p.X(u), p.Y(v); L = "ABCD"[i]
            d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=R); texte(d, int(x - 1), int(y - 2), L, R)
        tb = max(66, min(W*0.42, 110)); yb = H - m - bande
        d.rectangle([W - m - tb, yb, W - m, H - m], outline=T); d.line([(W - m - tb, yb + 12), (W - m, yb + 12)], fill=T)
        if len(titre)*8 <= tb - 6: texte2(d, int(W - m - tb + 3), yb + 3, titre, T, 1)
        else: texte(d, int(W - m - tb + 3), yb + 4, titre[:int((tb - 6)//4)], T)
        sep = W - m - 20
        texte(d, int(W - m - tb + 3), yb + 15, f"SHEET {graine % 9 + 1}-{rnd.randint(4, 9)}", T2)
        d.line([(sep, yb + 12), (sep, H - m)], fill=T); texte(d, sep + 3, yb + 15, "IMP", R)
        place = W - m - tb - m - 4
        for i, (_, _, lab) in enumerate(legende[:4]):
            col, lig = i // 3, i % 3
            ligne = f"{'ABCD'[i]}. {lab}"
            if (col + 1)*(len(ligne)*4 + 4) <= place or (col == 0 and len(ligne)*4 <= place):
                texte(d, m + 2 + col*(place//2 + 2), yb + 2 + lig*7, ligne, T2)
        if extra and W >= 192: extra(d, W, H, rnd)
        if rnd.random() < 0.6 or W >= 192:
            if W >= 192: sx, sy = W - m - 18, H - m - bande - 18
            else: sx, sy = (m + 16, m + 18) if ar < 1.4 else (W - m - 20, m + 18)
            tampon(d, sx, sy, rnd.choice(("OK", "IMP", "VU")))
    else:
        yb = H - m - bande
        d.line([(m, yb), (W - m - 1, yb)], fill=T3)
        txt = titre if len(titre)*4 <= W - 2*m else titre.split()[0]
        texte(d, int((W - len(txt)*4)//2 + 1), yb + (bande - 5)//2 + 1, txt[:int((W - 2*m)//4)], T)
    cadre(d, W, H)
    return im

# extras pour les grandes planches : encart de détail et notes
def encart_engrenage(d, W, H, rnd):
    x, y, r = 24, 40, 15
    d.ellipse([x - r, y - r, x + r, y + r], outline=R); d.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], outline=T3)
    P(d, x - r, y - r, 2*r, 2*r).gear(0.5, 0.5, 0.36, 10, T, T2)
    texte(d, x - 10, y + r + 4, "DET.1", R)
def notes(d, W, H, rnd):
    x0, y0 = W - 64, 14
    for k in range(4):
        x = x0
        while x < W - 14:
            l = rnd.randint(2, 7); d.line([(x, y0 + k*4), (min(W - 14, x + l), y0 + k*4)], fill=T3); x += l + 2
def extra_complet(d, W, H, rnd): encart_engrenage(d, W, H, rnd); notes(d, W, H, rnd)

# ------------------------------------------------------------------ les sujets
def s_engrenage(p):
    p.gear(0.5, 0.5, 0.42, 14); p.C(0.5, 0.5, 0.06, T2); p.R(0.47, 0.34, 0.53, 0.38, T2)
def s_vanne(p):
    p.roue(0.5, 0.36, 0.3, 6); p.R(0.46, 0.66, 0.54, 0.76); p.R(0.1, 0.76, 0.9, 0.92); p.E(0.5, 0.84, 0.16, 0.1, T2)
    for u in (0.12, 0.88): p.R(u - 0.04, 0.74, u + 0.04, 0.94, T2)
def s_manometre(p):
    p.C(0.5, 0.44, 0.36); p.C(0.5, 0.44, 0.3, T2)
    for k in range(9):
        a = math.radians(135 + k*33.75); p.L([(0.5 + math.cos(a)*0.25, 0.44 + math.sin(a)*0.25), (0.5 + math.cos(a)*0.3, 0.44 + math.sin(a)*0.3)], T2)
    p.L([(0.5, 0.44), (0.66, 0.3)], R); p.C(0.5, 0.44, 0.04)
    p.R(0.44, 0.8, 0.56, 0.94); p.R(0.4, 0.92, 0.6, 0.96, T2)
def s_ampoule(p):
    p.E(0.5, 0.38, 0.3, 0.3); p.R(0.36, 0.64, 0.64, 0.74)
    for k in range(4): p.L([(0.36, 0.75 + k*0.04), (0.64, 0.75 + k*0.04)], T2)
    p.L([(0.42, 0.66), (0.44, 0.4), (0.48, 0.34), (0.52, 0.42), (0.56, 0.34), (0.58, 0.4), (0.6, 0.66)], R)
    p.L([(0.46, 0.92), (0.54, 0.92)])
def s_ressort(p):
    p.R(0.3, 0.06, 0.7, 0.12); p.R(0.3, 0.88, 0.7, 0.94)
    p.ressort(0.5, 0.13, 0.5, 0.87, 9, 0.18, T)
    p.L([(0.84, 0.13), (0.84, 0.87)], T2); p.L([(0.81, 0.16), (0.84, 0.13), (0.87, 0.16)], T2)
def s_lunettes(p):
    for u in (0.28, 0.72):
        p.C(u, 0.5, 0.2); p.C(u, 0.5, 0.15, T2)
        for k in range(8): a = 2*math.pi*k/8; p.pix(u + math.cos(a)*0.18, 0.5 + math.sin(a)*0.18*1.0)
    p.L([(0.46, 0.48), (0.54, 0.48)]); p.L([(0.08, 0.5), (0.02, 0.4)], T2); p.L([(0.92, 0.5), (0.98, 0.4)], T2)
    p.L([(0.22, 0.42), (0.26, 0.38)], T2)
def s_cle(p):
    p.C(0.5, 0.26, 0.2); p.C(0.5, 0.26, 0.09, T2); p.C(0.32, 0.18, 0.06, T2); p.C(0.68, 0.18, 0.06, T2)
    p.R(0.46, 0.46, 0.54, 0.84)
    for k in range(3): p.R(0.54, 0.62 + k*0.08, 0.66 - k*0.03, 0.66 + k*0.08, T2)
def s_boulon(p):
    pts = [(0.5 + 0.3*math.cos(a), 0.3 + 0.3*math.sin(a)) for a in [k*math.pi/3 for k in range(6)]]
    p.poly(pts); p.C(0.5, 0.3, 0.16, T2)
    p.R(0.12, 0.62, 0.88, 0.72); p.R(0.36, 0.72, 0.64, 0.96)
    for k in range(6): p.L([(0.36, 0.74 + k*0.04), (0.64, 0.76 + k*0.04)], T2)
# -- hauts 1 x 2
def s_reverbere(p):
    p.R(0.42, 0.3, 0.58, 0.9); p.R(0.3, 0.9, 0.7, 0.96); p.R(0.36, 0.86, 0.64, 0.9, T2)
    p.poly([(0.22, 0.14), (0.78, 0.14), (0.66, 0.3), (0.34, 0.3)]); p.poly([(0.18, 0.14), (0.5, 0.04), (0.82, 0.14)])
    p.L([(0.5, 0.15), (0.5, 0.29)], T2); p.L([(0.36, 0.22), (0.64, 0.22)], R)
    for v in (0.4, 0.55, 0.7): p.L([(0.42, v), (0.58, v)], T2)
    p.L([(0.58, 0.36), (0.8, 0.36), (0.8, 0.42)], T2)
def s_tesla(p):
    p.C(0.5, 0.12, 0.3); p.C(0.5, 0.12, 0.18, T2)
    p.R(0.36, 0.24, 0.64, 0.72)
    for k in range(20): p.L([(0.36, 0.26 + k*0.023), (0.64, 0.27 + k*0.023)], T2)
    p.R(0.2, 0.72, 0.8, 0.8); p.R(0.14, 0.8, 0.86, 0.96); p.ressort(0.24, 0.84, 0.76, 0.84, 6, 0.03, T2)
    p.L([(0.8, 0.12), (0.9, 0.06), (0.86, 0.16), (0.98, 0.1)], R)
def s_automate(p):
    p.R(0.36, 0.04, 0.64, 0.18); p.R(0.4, 0.09, 0.6, 0.12, R); p.L([(0.5, 0.04), (0.5, 0.0)], T2)
    p.R(0.26, 0.2, 0.74, 0.5); p.C(0.5, 0.32, 0.12, T2); p.gear(0.5, 0.32, 0.08, 8, T2, T3)
    for u in (0.16, 0.84): p.R(u - 0.08, 0.2, u + 0.08, 0.48); p.C(u, 0.5, 0.06, T2); p.R(u - 0.06, 0.52, u + 0.06, 0.66)
    p.R(0.32, 0.5, 0.68, 0.56, T2)
    for u in (0.38, 0.62): p.R(u - 0.08, 0.56, u + 0.08, 0.76); p.C(u, 0.78, 0.06, T2); p.R(u - 0.07, 0.8, u + 0.07, 0.94); p.R(u - 0.1, 0.94, u + 0.1, 0.98)
    p.rivets(0.3, 0.24, 0.7, 0.24, 6)
# -- larges 2 x 1
def s_locomotive(p):
    p.R(0.18, 0.3, 0.68, 0.66); p.E(0.18, 0.48, 0.03, 0.18, T2)
    p.R(0.62, 0.14, 0.86, 0.66); p.R(0.66, 0.2, 0.8, 0.36, T2)
    p.R(0.26, 0.06, 0.32, 0.3); p.R(0.24, 0.02, 0.34, 0.08); p.E(0.46, 0.28, 0.05, 0.04, T2)
    p.L([(0.04, 0.84), (0.16, 0.66), (0.18, 0.66)])
    for u, r in ((0.3, 0.12), (0.47, 0.12), (0.74, 0.08)): p.roue(u, 0.82, r*0.5, 8)
    p.L([(0.3, 0.82), (0.47, 0.82)], R); p.L([(0.86, 0.66), (0.96, 0.66)], T2)
    for u in (0.36, 0.5): p.rivets(u, 0.32, u, 0.64, 6)
def s_voiture(p):
    p.R(0.12, 0.36, 0.78, 0.66); p.poly([(0.36, 0.36), (0.42, 0.1), (0.72, 0.1), (0.78, 0.36)])
    p.L([(0.57, 0.1), (0.57, 0.36)], T2); p.R(0.78, 0.44, 0.92, 0.66); p.E(0.92, 0.5, 0.02, 0.05, R)
    p.R(0.16, 0.18, 0.24, 0.36); p.E(0.2, 0.12, 0.05, 0.05, T2)
    for u in (0.26, 0.74): p.roue(u, 0.78, 0.09, 10)
    p.L([(0.14, 0.4), (0.04, 0.42)], T2); p.ressort(0.4, 0.5, 0.6, 0.5, 6, 0.04)
def s_sousmarin(p):
    p.E(0.48, 0.56, 0.42, 0.22); p.R(0.4, 0.2, 0.58, 0.36); p.L([(0.5, 0.2), (0.5, 0.04), (0.56, 0.04)])
    for k in range(5): p.C(0.24 + k*0.12, 0.56, 0.025, T2)
    p.L([(0.9, 0.56), (0.98, 0.56)], T2); p.L([(0.98, 0.38), (0.98, 0.74)]); p.L([(0.96, 0.44), (0.99, 0.5), (0.96, 0.56), (0.99, 0.62), (0.96, 0.68)], T2)
    p.L([(0.12, 0.48), (0.06, 0.48)], R); p.L([(0.12, 0.64), (0.06, 0.64)], R)
    p.L([(0.06, 0.56), (0.9, 0.56)], T3)
def s_velocipede(p):
    p.roue(0.24, 0.62, 0.17, 12); p.roue(0.8, 0.74, 0.08, 8)
    p.L([(0.24, 0.62), (0.4, 0.3), (0.8, 0.74)]); p.L([(0.4, 0.3), (0.46, 0.22), (0.54, 0.22)])
    p.R(0.5, 0.36, 0.66, 0.6); p.R(0.54, 0.24, 0.6, 0.36, T2); p.E(0.57, 0.18, 0.04, 0.05, T2)
    p.L([(0.24, 0.62), (0.5, 0.5)], R); p.L([(0.32, 0.26), (0.24, 0.2)], T2)
def s_lunette(p):
    p.poly([(0.16, 0.42), (0.86, 0.22), (0.88, 0.3), (0.18, 0.5)])
    for u in (0.32, 0.5, 0.68): p.L([(u, 0.42 - (u - 0.16)*0.28), (u + 0.01, 0.5 - (u - 0.16)*0.28)], T2)
    p.E(0.87, 0.26, 0.02, 0.06); p.E(0.16, 0.46, 0.015, 0.05, T2)
    p.L([(0.5, 0.38), (0.5, 0.62)]); p.L([(0.5, 0.62), (0.3, 0.96)]); p.L([(0.5, 0.62), (0.7, 0.96)]); p.L([(0.5, 0.62), (0.5, 0.96)])
    p.C(0.5, 0.36, 0.03, R); p.R(0.36, 0.58, 0.64, 0.64, T2); p.L([(0.12, 0.5), (0.1, 0.62)], T2)
# -- 2 x 2
def s_balancier(p):
    p.L([(0.08, 0.22), (0.92, 0.22)]); p.L([(0.08, 0.26), (0.92, 0.26)], T2); p.C(0.5, 0.24, 0.03, R)
    p.R(0.44, 0.27, 0.56, 0.9)
    p.R(0.1, 0.4, 0.26, 0.82); p.L([(0.18, 0.26), (0.18, 0.4)]); p.R(0.08, 0.82, 0.28, 0.9)
    p.roue(0.8, 0.66, 0.16, 8); p.L([(0.88, 0.26), (0.84, 0.56)]); p.L([(0.88, 0.26), (0.8, 0.66)], T2)
    p.R(0.04, 0.9, 0.96, 0.96); p.hachures(0.04, 0.9, 0.96, 0.96)
    p.ressort(0.3, 0.5, 0.42, 0.5, 4, 0.03)
def s_tete(p):
    p.R(0.24, 0.16, 0.76, 0.8); p.poly([(0.24, 0.16), (0.32, 0.06), (0.68, 0.06), (0.76, 0.16)])
    p.R(0.3, 0.32, 0.46, 0.44, T2); p.R(0.54, 0.32, 0.7, 0.44, T2); p.C(0.38, 0.38, 0.04, R); p.C(0.62, 0.38, 0.04, R)
    for k in range(5): p.L([(0.34, 0.56 + k*0.035), (0.66, 0.56 + k*0.035)], T2)
    for u in (0.2, 0.8): p.C(u, 0.4, 0.05); p.gear(u, 0.4, 0.035, 8, T2, T3)
    p.R(0.36, 0.8, 0.64, 0.92); p.rivets(0.28, 0.2, 0.72, 0.2, 8); p.rivets(0.28, 0.76, 0.72, 0.76, 8)
    p.L([(0.5, 0.06), (0.5, 0.0)], T2)
def s_scaphandre(p):
    p.C(0.5, 0.44, 0.34); p.C(0.5, 0.44, 0.3, T2)
    p.C(0.5, 0.44, 0.13); p.C(0.5, 0.44, 0.1, T2); p.L([(0.4, 0.44), (0.6, 0.44)], T2); p.L([(0.5, 0.34), (0.5, 0.54)], T2)
    for u in (0.24, 0.76): p.C(u, 0.4, 0.07); p.L([(u - 0.05, 0.4), (u + 0.05, 0.4)], T2)
    p.R(0.2, 0.76, 0.8, 0.88); p.rivets(0.22, 0.82, 0.78, 0.82, 10)
    p.L([(0.5, 0.1), (0.5, 0.02), (0.86, 0.02)], R)
    for k in range(10): a = 2*math.pi*k/10; p.pix(0.5 + math.cos(a)*0.16, 0.44 + math.sin(a)*0.16)
def s_chaudiere(p):
    p.R(0.14, 0.24, 0.86, 0.82); p.E(0.14, 0.53, 0.04, 0.29, T2); p.E(0.86, 0.53, 0.04, 0.29)
    for u in (0.32, 0.5, 0.68): p.L([(u, 0.24), (u, 0.82)], T2); p.rivets(u, 0.26, u, 0.8, 9)
    p.R(0.6, 0.08, 0.68, 0.24); p.R(0.58, 0.04, 0.7, 0.08); p.C(0.3, 0.16, 0.06); p.L([(0.3, 0.16), (0.33, 0.13)], R)
    p.R(0.22, 0.6, 0.4, 0.78, R); p.hachures(0.23, 0.61, 0.39, 0.77, R)
    p.R(0.1, 0.82, 0.9, 0.9); p.L([(0.86, 0.4), (0.96, 0.4), (0.96, 0.7)], T2)
def s_montre(p):
    p.C(0.5, 0.56, 0.4); p.C(0.5, 0.56, 0.35, T2)
    for k in range(12): a = 2*math.pi*k/12; p.L([(0.5 + math.cos(a)*0.31, 0.56 + math.sin(a)*0.31), (0.5 + math.cos(a)*0.35, 0.56 + math.sin(a)*0.35)])
    p.gear(0.42, 0.62, 0.13, 14); p.gear(0.62, 0.46, 0.09, 10); p.gear(0.62, 0.7, 0.06, 8, T2, T3)
    p.C(0.36, 0.42, 0.06, T2); p.A(0.36, 0.42, 0.04, 0, 300, T3)
    p.R(0.46, 0.08, 0.54, 0.16); p.C(0.5, 0.05, 0.04)
def s_bras(p):
    p.R(0.04, 0.82, 0.3, 0.96); p.hachures(0.04, 0.82, 0.3, 0.96); p.C(0.17, 0.76, 0.07)
    p.L([(0.17, 0.76), (0.42, 0.36)], T); p.L([(0.21, 0.78), (0.46, 0.38)], T2); p.C(0.44, 0.36, 0.06)
    p.L([(0.44, 0.36), (0.78, 0.26)]); p.L([(0.46, 0.4), (0.78, 0.3)], T2); p.C(0.8, 0.28, 0.04)
    p.L([(0.84, 0.26), (0.94, 0.16), (0.96, 0.22)]); p.L([(0.84, 0.32), (0.94, 0.4), (0.96, 0.34)])
    p.ressort(0.24, 0.66, 0.38, 0.44, 5, 0.03, R)
    p.gear(0.17, 0.76, 0.04, 8, T2, T3)
def s_capsule(p):
    p.R(0.3, 0.2, 0.7, 0.86); p.E(0.5, 0.2, 0.2, 0.12)
    p.E(0.5, 0.36, 0.13, 0.12, T2); p.R(0.44, 0.33, 0.56, 0.4, T3)
    for v in (0.5, 0.62, 0.74): p.L([(0.3, v), (0.7, v)], T2)
    p.R(0.42, 0.66, 0.58, 0.72, R); p.R(0.24, 0.86, 0.76, 0.94)
    p.L([(0.7, 0.56), (0.86, 0.56), (0.86, 0.94)], T2); p.L([(0.3, 0.7), (0.14, 0.7), (0.14, 0.94)], T2)
    p.L([(0.5, 0.08), (0.5, 0.0)], T2)
def s_turbine(p):
    p.C(0.5, 0.5, 0.4); p.C(0.5, 0.5, 0.34, T2)
    for k in range(16):
        a = 2*math.pi*k/16; b = a + 0.3
        p.L([(0.5 + math.cos(a)*0.1, 0.5 + math.sin(a)*0.1), (0.5 + math.cos(b)*0.33, 0.5 + math.sin(b)*0.33)])
    p.C(0.5, 0.5, 0.1); p.C(0.5, 0.5, 0.04, R)
    p.R(0.02, 0.44, 0.1, 0.56, T2); p.L([(0.0, 0.5), (0.1, 0.5)], R); p.R(0.9, 0.44, 0.98, 0.56, T2)
def s_cloche(p):
    p.L([(0.5, 0.0), (0.5, 0.1)]); p.E(0.5, 0.48, 0.32, 0.38); p.R(0.14, 0.7, 0.86, 0.82)
    for (u, v) in ((0.38, 0.44), (0.62, 0.44), (0.5, 0.28)): p.C(u, v, 0.06); p.C(u, v, 0.045, T2)
    p.rivets(0.2, 0.6, 0.8, 0.6, 9); p.rivets(0.16, 0.76, 0.84, 0.76, 11)
    p.L([(0.56, 0.0), (0.6, 0.12), (0.7, 0.18)], R)
    p.L([(0.86, 0.76), (0.96, 0.72), (0.98, 0.84)], T2)
def s_moulin(p):
    p.poly([(0.38, 0.96), (0.42, 0.42), (0.58, 0.42), (0.62, 0.96)]); p.poly([(0.38, 0.42), (0.5, 0.3), (0.62, 0.42)])
    p.R(0.46, 0.8, 0.54, 0.96, T2); p.C(0.5, 0.6, 0.03, T2)
    for k in range(4):
        a = math.pi/4 + k*math.pi/2; e = (0.5 + math.cos(a)*0.42, 0.36 + math.sin(a)*0.42)
        p.L([(0.5, 0.36), e]); m1 = (0.5 + math.cos(a)*0.14, 0.36 + math.sin(a)*0.14); b = a + 0.32
        p.poly([m1, e, (0.5 + math.cos(b)*0.4, 0.36 + math.sin(b)*0.4), (0.5 + math.cos(b)*0.15, 0.36 + math.sin(b)*0.15)], T2)
    p.C(0.5, 0.36, 0.04, R)
# -- 3 x 3
def s_ornithoptere(p):
    p.E(0.5, 0.56, 0.24, 0.08); p.E(0.66, 0.54, 0.04, 0.04, T2); p.L([(0.26, 0.56), (0.08, 0.5), (0.1, 0.62), (0.26, 0.6)])
    for s in (-1, 1):
        base = (0.46, 0.5)
        for k in range(5): p.L([base, (0.46 - 0.06*k + 0.12, 0.5 + s*(0.2 + 0.06*k))], T2 if k % 2 else T)
        p.L([(0.46, 0.5), (0.3, 0.5 + s*0.44), (0.62, 0.5 + s*0.24), (0.46, 0.5)])
    p.gear(0.5, 0.56, 0.035, 8, R, T2); p.L([(0.74, 0.56), (0.86, 0.56)], T2); p.L([(0.86, 0.48), (0.86, 0.64)])
def s_oiseau(p):
    p.E(0.46, 0.52, 0.2, 0.12); p.C(0.68, 0.38, 0.09); p.C(0.7, 0.36, 0.025, R); p.poly([(0.77, 0.38), (0.94, 0.42), (0.77, 0.44)])
    p.poly([(0.26, 0.5), (0.04, 0.44), (0.06, 0.6), (0.26, 0.58)], T2)
    for k in range(5): p.L([(0.38 + k*0.03, 0.46), (0.2 + k*0.06, 0.14 + k*0.02)], T2)
    p.L([(0.38, 0.46), (0.2, 0.14), (0.56, 0.46)])
    p.gear(0.46, 0.52, 0.06, 10, T2, T3); p.L([(0.42, 0.64), (0.4, 0.84)]); p.L([(0.52, 0.64), (0.54, 0.84)])
    p.L([(0.36, 0.84), (0.46, 0.84)]); p.L([(0.5, 0.84), (0.6, 0.84)])
def s_marcheur(p):
    p.R(0.24, 0.16, 0.76, 0.44); p.R(0.32, 0.22, 0.68, 0.32, T2); p.C(0.4, 0.27, 0.03, R); p.C(0.6, 0.27, 0.03, R)
    p.R(0.7, 0.06, 0.76, 0.16); p.R(0.3, 0.44, 0.7, 0.5, T2)
    for (u0, s) in ((0.3, -1), (0.7, 1)):
        k = (u0 + s*0.14, 0.66); f = (u0 + s*0.02, 0.92)
        p.L([(u0, 0.5), k, f]); p.C(*k, 0.03); p.R(f[0] - 0.08, 0.92, f[0] + 0.08, 0.96)
        p.ressort(u0, 0.52, k[0], 0.64, 4, 0.02, T2)
    p.rivets(0.26, 0.4, 0.74, 0.4, 10); p.L([(0.24, 0.3), (0.1, 0.36), (0.06, 0.3)], T2)
def s_diapason(p):
    p.R(0.36, 0.86, 0.64, 0.96); p.R(0.46, 0.6, 0.54, 0.86)
    p.L([(0.46, 0.6), (0.36, 0.52), (0.36, 0.08)]); p.L([(0.54, 0.6), (0.64, 0.52), (0.64, 0.08)])
    p.L([(0.4, 0.52), (0.4, 0.1)], T2); p.L([(0.6, 0.52), (0.6, 0.1)], T2)
    for k in range(3): p.A(0.5, 0.3, 0.2 + k*0.08, 200, 340, R); p.A(0.5, 0.3, 0.2 + k*0.08, 20, 160, R)
    p.C(0.5, 0.7, 0.05, T2); p.pix(0.5, 0.7, R)
def s_presse(p):
    p.R(0.14, 0.06, 0.86, 0.22); p.R(0.2, 0.22, 0.28, 0.9); p.R(0.72, 0.22, 0.8, 0.9)
    p.R(0.42, 0.22, 0.58, 0.52); p.R(0.34, 0.52, 0.66, 0.6); p.L([(0.5, 0.6), (0.5, 0.66)], R)
    p.R(0.3, 0.72, 0.7, 0.78, T2); p.R(0.1, 0.9, 0.9, 0.96); p.hachures(0.1, 0.9, 0.9, 0.96)
    p.gear(0.5, 0.14, 0.06, 10, T2, T3); p.L([(0.8, 0.14), (0.96, 0.14)], T2)
def s_foreuse(p):
    p.R(0.3, 0.06, 0.7, 0.34); p.R(0.36, 0.12, 0.64, 0.2, T2); p.R(0.44, 0.34, 0.56, 0.5)
    p.poly([(0.32, 0.5), (0.68, 0.5), (0.5, 0.96)])
    for k in range(6): v = 0.54 + k*0.07; w = 0.18*(1 - (v - 0.5)/0.46); p.L([(0.5 - w, v), (0.5 + w, v + 0.05)], T2)
    p.L([(0.3, 0.2), (0.12, 0.2), (0.12, 0.6)], T2); p.L([(0.7, 0.2), (0.88, 0.2), (0.88, 0.6)], T2)
    p.gear(0.5, 0.06, 0.06, 10, R, T2)
def s_roue_aubes(p):
    p.C(0.5, 0.46, 0.4); p.C(0.5, 0.46, 0.34, T2); p.C(0.5, 0.46, 0.06)
    for k in range(12):
        a = 2*math.pi*k/12
        p.L([(0.5 + math.cos(a)*0.06, 0.46 + math.sin(a)*0.06), (0.5 + math.cos(a)*0.4, 0.46 + math.sin(a)*0.4)], T2)
        x, y = 0.5 + math.cos(a)*0.4, 0.46 + math.sin(a)*0.4; p.L([(x - math.sin(a)*0.06, y + math.cos(a)*0.06), (x + math.sin(a)*0.06, y - math.cos(a)*0.06)])
    p.L([(0.0, 0.84), (1.0, 0.84)], R)
    for k in range(10): p.A(0.05 + k*0.1, 0.86, 0.05, 200, 340, T3)
    p.R(0.04, 0.4, 0.1, 0.96); p.R(0.9, 0.4, 0.96, 0.96)
def s_lanterne(p):
    p.poly([(0.2, 0.2), (0.5, 0.04), (0.8, 0.2)]); p.R(0.2, 0.2, 0.8, 0.26); p.R(0.24, 0.26, 0.76, 0.66)
    for u in (0.37, 0.5, 0.63): p.L([(u, 0.26), (u, 0.66)], T2)
    p.E(0.5, 0.46, 0.1, 0.12, R)
    for k in range(5): p.L([(0.42, 0.36 + k*0.05), (0.58, 0.36 + k*0.05)], T3)
    p.R(0.16, 0.66, 0.84, 0.72); for_u = [0.2 + k*0.06 for k in range(11)]
    for u in for_u: p.L([(u, 0.72), (u, 0.8)], T2)
    p.L([(0.16, 0.8), (0.84, 0.8)]); p.R(0.3, 0.8, 0.7, 0.96); p.L([(0.5, 0.04), (0.5, 0.0)], T2)
    p.L([(0.8, 0.46), (0.98, 0.36)], R); p.L([(0.8, 0.46), (0.98, 0.56)], R)
# -- 3 x 4
def s_horloge(p):
    p.R(0.3, 0.2, 0.7, 0.96); p.poly([(0.26, 0.2), (0.5, 0.02), (0.74, 0.2)])
    p.C(0.5, 0.32, 0.15); p.C(0.5, 0.32, 0.12, T2)
    for k in range(12): a = 2*math.pi*k/12; p.pix(0.5 + math.cos(a)*0.11, 0.32 + math.sin(a)*0.11*0.75)
    p.L([(0.5, 0.32), (0.5, 0.26)], R); p.L([(0.5, 0.32), (0.56, 0.32)], R)
    p.gear(0.42, 0.56, 0.07, 10); p.gear(0.58, 0.62, 0.05, 8, T2, T3)
    p.L([(0.5, 0.7), (0.5, 0.86)], T2); p.C(0.5, 0.88, 0.04, T2)
    for v in (0.48, 0.74): p.L([(0.3, v), (0.7, v)])
    p.R(0.44, 0.9, 0.56, 0.96, T2)
def s_jetpack(p):
    for u in (0.32, 0.68): p.R(u - 0.12, 0.16, u + 0.12, 0.66); p.E(u, 0.16, 0.12, 0.05); p.poly([(u - 0.08, 0.66), (u + 0.08, 0.66), (u + 0.05, 0.76), (u - 0.05, 0.76)])
    for u in (0.32, 0.68):
        for k in range(3): p.L([(u - 0.04 + k*0.04, 0.78), (u - 0.06 + k*0.06, 0.92)], R)
    p.R(0.44, 0.22, 0.56, 0.5, T2); p.C(0.5, 0.3, 0.04); p.L([(0.5, 0.3), (0.52, 0.28)], R)
    p.L([(0.2, 0.28), (0.08, 0.2), (0.08, 0.56)], T2); p.L([(0.8, 0.28), (0.92, 0.2), (0.92, 0.56)], T2)
    p.rivets(0.22, 0.24, 0.22, 0.6, 6); p.rivets(0.78, 0.24, 0.78, 0.6, 6)
# -- 4 x 2
def s_bateau(p):
    p.poly([(0.04, 0.6), (0.96, 0.6), (0.88, 0.8), (0.12, 0.8)]); p.R(0.24, 0.44, 0.74, 0.6); p.R(0.34, 0.32, 0.6, 0.44)
    for u in (0.4, 0.52): p.R(u, 0.04, u + 0.04, 0.32); p.R(u - 0.01, 0.02, u + 0.05, 0.05, T2)
    p.roue(0.66, 0.62, 0.09, 10)
    for k in range(6): p.C(0.28 + k*0.07, 0.52, 0.01, T2)
    p.L([(0.04, 0.82), (0.96, 0.82)], T3); p.L([(0.9, 0.6), (0.96, 0.4)], T2); p.L([(0.12, 0.6), (0.06, 0.36)], T2)
def s_aeroplane(p):
    p.E(0.46, 0.56, 0.3, 0.1); p.L([(0.12, 0.3), (0.84, 0.3)]); p.L([(0.12, 0.36), (0.84, 0.36)], T2)
    p.L([(0.12, 0.76), (0.84, 0.76)]); p.L([(0.12, 0.82), (0.84, 0.82)], T2)
    for u in (0.2, 0.4, 0.6, 0.8): p.L([(u, 0.36), (u, 0.76)], T2); p.L([(u, 0.36), (u + 0.2, 0.76)], T3)
    p.poly([(0.16, 0.56), (0.02, 0.4), (0.04, 0.6)]); p.L([(0.76, 0.56), (0.82, 0.56)]); p.L([(0.84, 0.36), (0.84, 0.76)], R)
    p.R(0.36, 0.42, 0.42, 0.5, T2); p.E(0.39, 0.4, 0.02, 0.06, T2)
    for u in (0.3, 0.6): p.roue(u, 0.92, 0.025, 6)
def s_grue(p):
    p.R(0.08, 0.86, 0.32, 0.96); p.hachures(0.08, 0.86, 0.32, 0.96)
    p.L([(0.14, 0.86), (0.18, 0.12)]); p.L([(0.26, 0.86), (0.22, 0.12)])
    for k in range(8): v = 0.84 - k*0.09; p.L([(0.14 + (0.84 - v)*0.05, v), (0.26 - (0.84 - v)*0.05, v - 0.09)], T2)
    p.L([(0.04, 0.12), (0.94, 0.12)]); p.L([(0.04, 0.18), (0.94, 0.18)])
    for k in range(9): u = 0.06 + k*0.1; p.L([(u, 0.18), (u + 0.05, 0.12)], T2)
    p.R(0.02, 0.1, 0.1, 0.32); p.hachures(0.02, 0.2, 0.1, 0.32)
    p.L([(0.2, 0.12), (0.2, 0.02), (0.94, 0.12)], T2); p.L([(0.2, 0.02), (0.02, 0.1)], T2)
    p.R(0.7, 0.18, 0.78, 0.22); p.L([(0.74, 0.22), (0.74, 0.7)], R); p.R(0.68, 0.7, 0.8, 0.84); p.hachures(0.68, 0.7, 0.8, 0.84, T2)
def s_tramway(p):
    p.R(0.06, 0.24, 0.94, 0.76); p.poly([(0.06, 0.24), (0.12, 0.14), (0.88, 0.14), (0.94, 0.24)])
    for k in range(8): u = 0.12 + k*0.1; p.R(u, 0.32, u + 0.07, 0.5, T2)
    p.R(0.44, 0.52, 0.56, 0.76); p.L([(0.5, 0.14), (0.5, 0.04), (0.3, 0.0)]); p.L([(0.0, 0.0), (1.0, 0.0)], R)
    for u in (0.18, 0.3, 0.7, 0.82): p.roue(u, 0.84, 0.035, 6)
    p.L([(0.0, 0.92), (1.0, 0.92)], T3); p.rivets(0.08, 0.6, 0.42, 0.6, 10); p.rivets(0.58, 0.6, 0.92, 0.6, 10)
def s_excavatrice(p):
    p.R(0.06, 0.4, 0.46, 0.76); p.R(0.14, 0.16, 0.22, 0.4); p.R(0.12, 0.12, 0.24, 0.16, T2); p.R(0.3, 0.46, 0.42, 0.6, T2)
    for u in (0.1, 0.42): p.roue(u, 0.84, 0.04, 6)
    p.L([(0.04, 0.88), (0.48, 0.88)]); p.L([(0.04, 0.8), (0.48, 0.8)], T2)
    p.L([(0.44, 0.44), (0.72, 0.1), (0.9, 0.42)]); p.L([(0.46, 0.5), (0.72, 0.16), (0.86, 0.44)], T2)
    p.poly([(0.84, 0.42), (0.98, 0.42), (0.96, 0.62), (0.86, 0.6)]); for_k = range(4)
    for k in for_k: p.L([(0.86 + k*0.035, 0.62), (0.87 + k*0.035, 0.68)], R)
    p.ressort(0.52, 0.42, 0.66, 0.24, 5, 0.02, T2)
# -- 4 x 3 et 4 x 4
def s_colosse(p):
    p.R(0.36, 0.06, 0.64, 0.22); p.R(0.42, 0.11, 0.58, 0.15, R)
    p.R(0.26, 0.24, 0.74, 0.58); p.C(0.5, 0.4, 0.07, R); p.gear(0.5, 0.4, 0.05, 10, T2, T3)
    for u, s in ((0.18, -1), (0.82, 1)): p.R(u - 0.07, 0.24, u + 0.07, 0.36); p.L([(u, 0.36), (u + s*0.06, 0.58), (u + s*0.04, 0.78)]); p.C(u + s*0.04, 0.82, 0.04)
    for u in (0.4, 0.6): p.R(u - 0.06, 0.6, u + 0.06, 0.8); p.R(u - 0.08, 0.8, u + 0.08, 0.96); p.ressort(u, 0.62, u, 0.78, 4, 0.02, T2)
    p.R(0.3, 0.58, 0.7, 0.62, T2); p.rivets(0.28, 0.28, 0.72, 0.28, 12); p.rivets(0.28, 0.54, 0.72, 0.54, 12)
    for k in range(3): p.R(0.3 + k*0.14, 0.0, 0.34 + k*0.14, 0.06, T2)
def s_cuirasse(p):
    p.E(0.5, 0.32, 0.4, 0.2); p.L([(0.1, 0.32), (0.9, 0.32)], T3)
    for k in range(1, 8): u = 0.1 + k*0.1; h = 0.2*math.sqrt(max(0, 1 - ((u - 0.5)/0.4)**2)); p.L([(u, 0.32 - h), (u, 0.32 + h)], T2)
    p.poly([(0.2, 0.56), (0.8, 0.56), (0.74, 0.76), (0.26, 0.76)]); p.L([(0.36, 0.52), (0.38, 0.56)]); p.L([(0.64, 0.52), (0.62, 0.56)])
    for k in range(3): u = 0.36 + k*0.14; p.R(u - 0.04, 0.48 - 0.0, u + 0.04, 0.56, T2); p.L([(u, 0.5), (u + 0.08, 0.46)], R)
    for k in range(7): p.C(0.29 + k*0.07, 0.66, 0.012, T2)
    p.poly([(0.9, 0.32), (0.99, 0.18), (0.97, 0.32)]); p.poly([(0.9, 0.32), (0.99, 0.46), (0.97, 0.32)])
    for u in (0.14, 0.86): p.L([(u, 0.5), (u, 0.62)], T2); p.C(u, 0.66, 0.04, T2)
def s_marteau(p):
    p.R(0.14, 0.04, 0.86, 0.14); p.R(0.18, 0.14, 0.28, 0.84); p.R(0.72, 0.14, 0.82, 0.84)
    p.R(0.42, 0.14, 0.58, 0.36); p.L([(0.5, 0.36), (0.5, 0.48)]); p.R(0.36, 0.48, 0.64, 0.62); p.hachures(0.36, 0.48, 0.64, 0.62, T2)
    p.R(0.36, 0.74, 0.64, 0.84); p.R(0.08, 0.84, 0.92, 0.96); p.hachures(0.08, 0.84, 0.92, 0.96)
    p.R(0.4, 0.68, 0.6, 0.74, R)
    for (u, v) in ((0.31, 0.2), (0.69, 0.2)): p.C(u, v, 0.04, T2)
    p.L([(0.28, 0.5), (0.36, 0.55)], T2); p.L([(0.72, 0.5), (0.64, 0.55)], T2)
    p.L([(0.86, 0.09), (0.96, 0.09), (0.96, 0.5)], T2); p.C(0.96, 0.54, 0.03); p.L([(0.96, 0.54), (0.98, 0.51)], R)

# titre (blueprint), ratio du dessin, fonction, repères (u, v, légende), extra
SUJETS = {
 "engrenage": ("COGWHEEL", 1, s_engrenage, [], None), "vanne": ("VALVE", 1, s_vanne, [], None), "manometre": ("GAUGE", 1, s_manometre, [], None),
 "ampoule": ("BULB", 0.8, s_ampoule, [], None), "ressort": ("SPRING", 0.7, s_ressort, [], None), "lunettes": ("GOGGLES", 1.4, s_lunettes, [], None),
 "cle": ("KEY", 0.8, s_cle, [], None), "boulon": ("BOLT", 0.9, s_boulon, [], None),
 "reverbere": ("LAMP POST", 0.42, s_reverbere, [], None), "tesla": ("TESLA COIL", 0.45, s_tesla, [], None), "automate": ("AUTOMATON", 0.5, s_automate, [], None),
 "locomotive": ("LOCOMOTIVE", 2.3, s_locomotive, [], None), "voiture": ("STEAM CAR", 2.3, s_voiture, [], None), "sousmarin": ("SUBMARINE", 2.6, s_sousmarin, [], None),
 "velocipede": ("VELOCIPEDE", 2.0, s_velocipede, [], None), "lunette": ("TELESCOPE", 2.1, s_lunette, [], None),
 "balancier": ("BEAM ENGINE", 1.15, s_balancier, [(0.5, 0.24, "PIVOT"), (0.18, 0.6, "CYLINDER"), (0.8, 0.66, "FLYWHEEL"), (0.5, 0.6, "COLUMN")], None),
 "tete": ("AUTOMATON HEAD", 1, s_tete, [(0.38, 0.38, "OPTIC"), (0.2, 0.4, "EAR GEAR"), (0.5, 0.63, "GRILLE"), (0.5, 0.86, "NECK")], None),
 "scaphandre": ("DIVING HELMET", 1, s_scaphandre, [(0.5, 0.44, "VISOR"), (0.24, 0.4, "PORT"), (0.5, 0.82, "COLLAR"), (0.86, 0.02, "AIR HOSE")], None),
 "chaudiere": ("BOILER", 1.15, s_chaudiere, [(0.64, 0.06, "STACK"), (0.3, 0.16, "GAUGE"), (0.31, 0.69, "FIREBOX"), (0.5, 0.5, "SHELL")], None),
 "dirigeable": None, "triple": None,
 "montre": ("POCKET WATCH", 0.85, s_montre, [(0.42, 0.62, "MAIN GEAR"), (0.36, 0.42, "BALANCE"), (0.5, 0.05, "CROWN"), (0.62, 0.46, "ESCAPE")], None),
 "bras": ("MECHANICAL ARM", 1.15, s_bras, [(0.17, 0.76, "SHOULDER"), (0.44, 0.36, "ELBOW"), (0.9, 0.28, "CLAW"), (0.31, 0.55, "SPRING")], None),
 "capsule": ("CAPSULE", 0.85, s_capsule, [(0.5, 0.36, "WINDOW"), (0.5, 0.69, "PLATE"), (0.86, 0.75, "FEED"), (0.5, 0.9, "BASE")], None),
 "turbine": ("STEAM TURBINE", 1, s_turbine, [(0.5, 0.5, "ROTOR"), (0.7, 0.3, "BLADES"), (0.06, 0.5, "INLET"), (0.94, 0.5, "OUTLET")], None),
 "cloche": ("DIVING BELL", 0.95, s_cloche, [(0.5, 0.28, "PORTHOLE"), (0.5, 0.76, "BALLAST"), (0.5, 0.05, "CABLE"), (0.96, 0.78, "ARM")], None),
 "moulin": ("WINDMILL", 0.9, s_moulin, [(0.5, 0.36, "HUB"), (0.8, 0.66, "SAIL"), (0.5, 0.88, "DOOR"), (0.5, 0.33, "CAP")], None),
 "ornithoptere": ("ORNITHOPTER", 1.2, s_ornithoptere, [(0.5, 0.56, "DRIVE"), (0.3, 0.1, "WING"), (0.08, 0.56, "TAIL"), (0.86, 0.56, "PROP")], extra_complet),
 "oiseau": ("CLOCKWORK BIRD", 1.1, s_oiseau, [(0.7, 0.36, "EYE"), (0.46, 0.52, "SPRING"), (0.2, 0.14, "WING"), (0.06, 0.52, "TAIL")], extra_complet),
 "marcheur": ("STEAM WALKER", 1.1, s_marcheur, [(0.5, 0.27, "CABIN"), (0.73, 0.11, "STACK"), (0.16, 0.66, "KNEE"), (0.3, 0.94, "FOOT")], extra_complet),
 "diapason": ("ECHO TUNING FORK", 0.9, s_diapason, [(0.36, 0.1, "PRONG"), (0.5, 0.7, "CORE"), (0.5, 0.91, "BASE"), (0.82, 0.3, "WAVE")], notes),
 "presse": ("MECHANICAL PRESS", 1.1, s_presse, [(0.5, 0.14, "COG"), (0.5, 0.56, "HEAD"), (0.5, 0.75, "SHEET"), (0.24, 0.6, "FRAME")], extra_complet),
 "foreuse": ("DRILL HEAD", 0.9, s_foreuse, [(0.5, 0.06, "DRIVE"), (0.5, 0.2, "MOTOR"), (0.5, 0.7, "BIT"), (0.12, 0.4, "COOLANT")], extra_complet),
 "roue": ("WATER WHEEL", 1.2, s_roue_aubes, [(0.5, 0.46, "AXLE"), (0.5, 0.06, "PADDLE"), (0.5, 0.84, "WATER"), (0.07, 0.6, "PILLAR")], extra_complet),
 "lanterne": ("LIGHTHOUSE LAMP", 1, s_lanterne, [(0.5, 0.46, "FLAME"), (0.3, 0.46, "LENS"), (0.5, 0.76, "RAIL"), (0.5, 0.12, "VENT")], notes),
 "horloge": ("CLOCK TOWER", 0.6, s_horloge, [(0.5, 0.32, "DIAL"), (0.42, 0.56, "TRAIN"), (0.5, 0.88, "PENDULUM"), (0.5, 0.1, "SPIRE")], extra_complet),
 "jetpack": ("JETPACK", 0.75, s_jetpack, [(0.32, 0.4, "TANK"), (0.5, 0.3, "GAUGE"), (0.68, 0.84, "THRUST"), (0.08, 0.4, "STRAP")], extra_complet),
 "bateau": ("PADDLE STEAMER", 2.6, s_bateau, [(0.66, 0.62, "PADDLE"), (0.42, 0.18, "STACKS"), (0.47, 0.38, "BRIDGE"), (0.5, 0.7, "HULL")], extra_complet),
 "aeroplane": ("STEAM BIPLANE", 2.4, s_aeroplane, [(0.84, 0.56, "PROP"), (0.39, 0.46, "BOILER"), (0.5, 0.3, "WING"), (0.08, 0.5, "RUDDER")], extra_complet),
 "grue": ("GANTRY CRANE", 2.2, s_grue, [(0.2, 0.5, "TOWER"), (0.6, 0.15, "JIB"), (0.06, 0.25, "WEIGHT"), (0.74, 0.77, "LOAD")], extra_complet),
 "tramway": ("STEAM TRAM", 2.5, s_tramway, [(0.5, 0.4, "WINDOWS"), (0.5, 0.64, "DOOR"), (0.4, 0.0, "LINE"), (0.18, 0.84, "BOGIE")], extra_complet),
 "excavatrice": ("STEAM SHOVEL", 2.2, s_excavatrice, [(0.18, 0.28, "STACK"), (0.72, 0.13, "BOOM"), (0.91, 0.52, "BUCKET"), (0.26, 0.84, "TRACKS")], extra_complet),
 "colosse": ("IRON COLOSSUS", 1.25, s_colosse, [(0.5, 0.13, "HEAD"), (0.5, 0.4, "CORE"), (0.82, 0.82, "FIST"), (0.4, 0.88, "LEG")], extra_complet),
 "cuirasse": ("SKY DREADNOUGHT", 1.4, s_cuirasse, [(0.5, 0.32, "ENVELOPE"), (0.5, 0.5, "TURRETS"), (0.5, 0.66, "DECK"), (0.86, 0.66, "ENGINE")], extra_complet),
 "marteau": ("STEAM HAMMER", 1.05, s_marteau, [(0.5, 0.25, "CYLINDER"), (0.5, 0.55, "RAM"), (0.5, 0.79, "ANVIL"), (0.96, 0.54, "GAUGE")], extra_complet),
}

# tableau vanilla -> (sujet, titre FR, titre EN)
PLANCHES = {
 "alban": ("engrenage", "Rouage, détail", "Cogwheel, Detail"), "aztec": ("vanne", "Vanne d'arrêt", "Stop Valve"),
 "aztec2": ("manometre", "Manomètre", "Pressure Gauge"), "bomb": ("ampoule", "Ampoule à filament", "Filament Bulb"),
 "kebab": ("ressort", "Ressort de rappel", "Return Spring"), "meditative": ("lunettes", "Lunettes d'atelier", "Workshop Goggles"),
 "plant": ("cle", "Clé de remontage", "Winding Key"), "wasteland": ("boulon", "Boulon de charpente", "Frame Bolt"),
 "graham": ("reverbere", "Réverbère", "Street Lamp"), "prairie_ride": ("tesla", "Bobine de Tesla", "Tesla Coil"),
 "wanderer": ("automate", "Automate de service", "Service Automaton"),
 "courbet": ("locomotive", "Locomotive de ligne", "Line Locomotive"), "creebet": ("voiture", "Voiture à vapeur", "Steam Car"),
 "pool": ("sousmarin", "Sous-marin d'exploration", "Exploration Submarine"), "sea": ("velocipede", "Vélocipède à vapeur", "Steam Velocipede"),
 "sunset": ("lunette", "Lunette astronomique", "Astronomical Telescope"),
 "baroque": ("balancier", "Machine à balancier", "Beam Engine"), "bust": ("tete", "Tête d'automate", "Automaton Head"),
 "earth": ("scaphandre", "Casque de scaphandrier", "Diving Helmet"), "fire": ("chaudiere", "Chaudière tubulaire", "Tubular Boiler"),
 "humble": ("dirigeable", "Dirigeable de classe III", "Class III Airship"), "match": ("montre", "Montre de gousset", "Pocket Watch"),
 "skull_and_roses": ("bras", "Bras mécanique", "Mechanical Arm"), "stage": ("capsule", "Capsule de transfert", "Transfer Capsule"),
 "void": ("turbine", "Turbine à vapeur", "Steam Turbine"), "water": ("cloche", "Cloche de plongée", "Diving Bell"),
 "wind": ("moulin", "Moulin à vent", "Windmill"), "wither": ("triple", "Le Gardien des enfers, prototype", "Infernal Guardian, Prototype"),
 "bouquet": ("ornithoptere", "Ornithoptère", "Ornithopter"), "cavebird": ("oiseau", "Oiseau mécanique", "Clockwork Bird"),
 "cotan": ("marcheur", "Marcheur à vapeur", "Steam Walker"), "endboss": ("diapason", "Diapason d'Écho", "Echo Tuning Fork"),
 "fern": ("presse", "Presse mécanique", "Mechanical Press"), "owlemons": ("foreuse", "Tête de forage", "Drill Head"),
 "sunflowers": ("roue", "Roue à aubes", "Water Wheel"), "tides": ("lanterne", "Lanterne de phare", "Lighthouse Lamp"),
 "backyard": ("horloge", "Tour d'horloge", "Clock Tower"), "pond": ("jetpack", "Propulseur dorsal", "Jetpack"),
 "changing": ("bateau", "Bateau à aubes", "Paddle Steamer"), "fighters": ("aeroplane", "Biplan à vapeur", "Steam Biplane"),
 "finding": ("grue", "Grue portuaire", "Harbour Crane"), "lowmist": ("tramway", "Tramway à vapeur", "Steam Tram"),
 "passage": ("excavatrice", "Pelle à vapeur", "Steam Shovel"),
 "donkey_kong": ("colosse", "Le Colosse de fer", "The Iron Colossus"), "skeleton": ("cuirasse", "Cuirassé du ciel", "Sky Dreadnought"),
 "burning_skull": ("marteau", "Marteau-pilon", "Steam Hammer"),
}
CONSERVES = ("orb", "pigscene", "pointer", "unpacked")
AUTEURS_PLANS = (["Bureau des Ingénieurs", "Atelier Vael", "Ministère des Ponts et Rouages", "Cercle des Ingénieurs"],
                 ["Engineers' Bureau", "Vael Workshop", "Ministry of Bridges and Gears", "Engineers' Circle"])

def generer(nom, w, h):
    sujet = PLANCHES[nom][0]; W, H = w*64, h*64
    if sujet == "dirigeable": return lot1c.humble()
    if sujet == "triple": return lot1c.wither()
    return planche(W, H, sujet, graine=sum(map(ord, nom)))
