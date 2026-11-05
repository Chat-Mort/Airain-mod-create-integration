"""Plans v7 : mise en page commune, dessins via kit.K."""
import random
from PIL import Image, ImageDraw
from plans import fond, cadre, cote_h, cote_v, tampon, notes, texte, texte2, P, PLANCHES, CONSERVES, AUTEURS_PLANS
from kit import K, T, T2, T3, R

def encart(d, W, H, rnd, sujet_encart):
    x, y, r = 25, 40, 16
    d.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], outline=T3); d.ellipse([x - r, y - r, x + r, y + r], outline=R)
    texte(d, x - 10, y + r + 4, "DET.1", R)
    return (x - r + 3, y - r + 3, 2*r - 6, 2*r - 6)

def planche(W, H, sujets, nom, graine=0):
    titre, ar, dessin, legende, detail = sujets[nom]
    im, d = fond(W, H, graine)
    petit = W < 128 or H < 128; grand = min(W, H) >= 192
    m = 7
    bande = 9 if (petit and H < 128) else (11 if petit else 24)
    gauche = 9 if not petit else 7
    if grand and detail: gauche = 44
    zx0, zy0, zx1, zy1 = m + gauche, m + (7 if petit else 8), W - m - (0 if petit else 6), H - m - bande - 2
    zw, zh = zx1 - zx0, zy1 - zy0
    if zw/zh > ar: bh = zh; bw = bh*ar
    else: bw = zw; bh = bw/ar
    bx, by = zx0 + (zw - bw)/2, zy0 + (zh - bh)/2
    lw = 0.85 if W*H <= 64*64 else (1.0 if min(W, H) < 192 else 1.35)
    k = K(W, H, bx, by, bw, bh, lw); dessin(k)
    rnd = random.Random(graine*7 + 3)
    if grand and detail:
        ex, ey, ew, eh = encart(d, W, H, rnd, detail)
        k2 = K(W, H, ex, ey, ew, eh, 0.8); detail(k2); im = k2.rendu(im)
    im = k.rendu(im); d = ImageDraw.Draw(im)
    if not petit:
        ech = 10*rnd.choice((2, 3, 4, 5, 6))
        cote_h(d, int(bx), int(bx + bw), int(zy0 - 3), str(int(ech*ar)))
        cote_v(d, int(bx - 5), int(by), int(by + bh), str(ech))
        import math
        cx0, cy0 = bx + bw/2, by + bh/2; deja = []
        for i, (u, v, lab) in enumerate(legende[:4]):                       # repères avec ligne de rappel
            x, y = bx + u*bw, by + v*bh; dx, dy = x - cx0, y - cy0; L = math.hypot(dx, dy) or 1
            dist = 9 if W < 192 else 14
            qx, qy = x + dx/L*dist, y + dy/L*dist
            qx = min(max(qx, m + 6), W - m - 7); qy = min(max(qy, m + 6), H - m - bande - 6)
            for (ox, oy) in deja:
                if abs(ox - qx) < 10 and abs(oy - qy) < 10: qy += 10 if qy < oy else -10
            deja.append((qx, qy))
            d.line([(x, y), (qx, qy)], fill=R); d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=R)
            d.ellipse([qx - 4, qy - 4, qx + 4, qy + 4], fill=(30, 66, 124), outline=R); texte(d, int(qx - 1), int(qy - 2), "ABCD"[i], R)
        tb = max(66, min(W*0.42, 110)); yb = H - m - bande
        d.rectangle([W - m - tb, yb, W - m, H - m], outline=T); d.line([(W - m - tb, yb + 12), (W - m, yb + 12)], fill=T)
        if len(titre)*8 <= tb - 6: texte2(d, int(W - m - tb + 3), yb + 3, titre, T, 1)
        else: texte(d, int(W - m - tb + 3), yb + 4, titre[:int((tb - 6)//4)], T)
        sep = W - m - 20
        texte(d, int(W - m - tb + 3), yb + 15, f"SHEET {graine % 9 + 1}-{rnd.randint(4, 9)}", T2)
        d.line([(sep, yb + 12), (sep, H - m)], fill=T); texte(d, sep + 3, yb + 15, "IMP", R)
        place = int(W - m - tb - m - 4)
        for i, (_, _, lab) in enumerate(legende[:4]):
            col, lig = i // 3, i % 3; ligne = f"{'ABCD'[i]}. {lab}"
            if col == 0: texte(d, m + 2, yb + 2 + lig*7, ligne[:max(1, place//4)], T2)
            elif place >= 110: texte(d, m + 2 + place//2 + 2, yb + 2 + lig*7, ligne[:max(1, (place//2)//4)], T2)
        if grand: notes(d, W, H, rnd)
        if grand:
            sx, sy = (W - m - 18, H - m - bande - 18) if grand else ((m + 16, m + 18) if ar < 1.3 else (W - m - 20, m + 18))
            tampon(d, sx, sy, rnd.choice(("OK", "IMP", "VU")))
    else:
        # petits formats : mêmes codes que les grandes planches, en réduit (cotes, repère, cartouche numéroté)
        ech = 10*rnd.choice((2, 3, 4, 6))
        cote_h(d, int(bx), int(bx + bw), int(zy0 - 4), str(int(ech*ar))[:3])
        if bh >= 24: cote_v(d, int(bx - 4), int(by), int(by + bh), str(ech)[:2])
        import math
        for i, (u, v, lab) in enumerate(legende[:2] if W * H > 64 * 64 else []):
            x, y = bx + u*bw, by + v*bh; qx, qy = min(W - m - 6, x + 8), max(m + 6, y - 6)
            d.line([(x, y), (qx, qy)], fill=R); d.ellipse([qx - 3, qy - 3, qx + 3, qy + 3], fill=(30, 66, 124), outline=R); texte(d, int(qx - 1), int(qy - 2), "AB"[i], R)
        yb = H - m - bande
        d.line([(m, yb), (W - m - 1, yb)], fill=T3)
        num = f"{graine % 9 + 1}-{rnd.randint(2, 9)}"
        place = W - 2*m - (len(num)*4 + 6)
        if len(titre)*4 <= place:                                           # titre complet + numéro de feuille
            texte(d, m + 2, yb + (bande - 5)//2 + 1, titre, T)
            sep = W - m - len(num)*4 - 4
            d.line([(sep, yb), (sep, H - m)], fill=T3); texte(d, sep + 2, yb + (bande - 5)//2 + 1, num, R)
        else:                                                               # sinon le titre complet passe avant le numéro
            txt = titre if len(titre)*4 <= W - 2*m else titre.split()[0]
            texte(d, int((W - len(txt)*4)//2 + 1), yb + (bande - 5)//2 + 1, txt[:int((W - 2*m)//4)], T)
        for (cx, cy) in ((m + 2, m + 2), (W - m - 3, m + 2)):              # croix de repérage
            d.line([(cx - 1, cy), (cx + 1, cy)], fill=R); d.line([(cx, cy - 1), (cx, cy + 1)], fill=R)
    cadre(d, W, H)
    return im
