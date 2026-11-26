# Motifs, version corrigée (1.70.2) : même calcul que le Generateur.java corrigé
import math
from motifs import ROLES, Image, ImageDraw, ImageFont
def R(w, h, f): return [[f(u, v) for u in range(w)] for v in range(h)]
def tuile(d, p):
    c = n = p
    if d == 'CHECKERBOARD': return R(2*c, 2*c, lambda u, v: (u//c + v//c) % 2)
    if d == 'STRIPES': return R(2*c, 1, lambda u, v: (u//c) % 2)
    if d == 'DIAGONALS': return R(2*c, 2*c, lambda u, v: 1 if (u + v) % (2*c) < c else 0)
    if d == 'CHEVRONS': P = 2*c; return R(2*P, 2*c, lambda u, v: ((abs(u % (2*P) - P) + v) // c) % 2)
    if d in ('OFFSET_PAVERS', 'RUNNING_BOND'):
        # pavés / briques de 2c x c en couleur A, joints d'un bloc en couleur B, rangs décalés d'une demi-brique
        L, H = 2*c + 1, c + 1
        def f(u, v):
            if v % H == c: return 1
            x = (u + ((v // H) % 2) * (L // 2 + 1)) % L
            return 1 if x == L - 1 else 0
        return R(2*L, 2*H, f)
    if d == 'CABOCHONS': return R(n, n, lambda u, v: 1 if (u == 0 and v == 0) else 0)
    if d == 'DIAMONDS':
        m = (n-1)/2
        def f(u, v):
            e = abs(u-m) + abs(v-m); return 2 if e <= 1 else 1 if (m-1.5 < e <= m+0.01) else 0
        return R(n, n, f)
    if d == 'ROSETTE':
        m = (n-1)/2
        def f(u, v):
            x, y = (u-m)/(n/2), (v-m)/(n/2); r = math.hypot(x, y)
            if r < 0.2: return 2
            for k in range(8):
                a = k * math.pi / 4; dx, dy = x - 0.55*math.cos(a), y - 0.55*math.sin(a)
                ra = dx*math.cos(a) + dy*math.sin(a); ta = -dx*math.sin(a) + dy*math.cos(a)
                if (ra/0.3)**2 + (ta/0.14)**2 <= 1: return 1
            return 1 if 0.9 < r < 1.04 else 0
        return R(n, n, f)
    if d == 'WAINSCOT': return R(1, n, lambda u, v: 1 if v < n - 1 else 2)
    if d == 'PILASTERS': return R(n, 1, lambda u, v: 1 if u == 0 else 0)
    if d == 'FRIEZE': return R(4, n + 2, lambda u, v: (1 if u % 4 < 2 else 2) if v >= n else 0)
    if d == 'COFFERS': return R(n, n, lambda u, v: 1 if (u == 0 or v == 0) else 2 if (u == n//2 and v == n//2) else 0)
    if d == 'CROSSED_BEAMS': return R(n, n, lambda u, v: 1 if (u == 0 or v == 0 or u == v or u == n-v) else 0)
    if d == 'GRID': return R(c+1, c+1, lambda u, v: 1 if (u == 0 or v == 0) else 0)
UNIQUE_V = {'WAINSCOT', 'FRIEZE'}
DEF = dict(CHECKERBOARD=1, CHEVRONS=2, OFFSET_PAVERS=2, DIAMONDS=9, STRIPES=1, DIAGONALS=2, ROSETTE=15, CABOCHONS=4, RUNNING_BOND=2,
           WAINSCOT=4, PILASTERS=5, FRIEZE=4, COFFERS=5, CROSSED_BEAMS=8, GRID=3)
NOMS = dict(CHECKERBOARD="Damier", CHEVRONS="Chevrons", OFFSET_PAVERS="Pavés décalés", DIAMONDS="Losanges", STRIPES="Bandes", DIAGONALS="Diagonales",
            ROSETTE="Rosace", CABOCHONS="Cabochons", RUNNING_BOND="Appareil", WAINSCOT="Soubassement", PILASTERS="Pilastres", FRIEZE="Frise",
            COFFERS="Caissons", CROSSED_BEAMS="Poutres croisées", GRID="Grille")
TYPES = [("Sols", "floor", ["CHECKERBOARD", "CHEVRONS", "OFFSET_PAVERS", "DIAMONDS", "STRIPES", "DIAGONALS", "ROSETTE", "CABOCHONS"]),
         ("Murs", "wall", ["RUNNING_BOND", "WAINSCOT", "PILASTERS", "FRIEZE", "CHECKERBOARD", "STRIPES", "DIAGONALS"]),
         ("Plafonds", "ceiling", ["COFFERS", "CROSSED_BEAMS", "GRID", "CHECKERBOARD", "ROSETTE", "DIAMONDS"])]
def rendu(d, mur, n=16, c=10, bord=0):
    tl = tuile(d, DEF[d]); h, w = len(tl), len(tl[0])
    im = Image.new('RGBA', (n*c, n*c))
    for r in range(n):
        for col in range(n):
            v = n-1-r if mur else r
            if bord and (col < bord or col >= n-bord or v < bord or v >= n-bord): role = 2
            else:
                vv, uu = v - bord, col - bord
                role = (tl[vv][uu % w] if vv < h else 0) if d in UNIQUE_V else tl[vv % h][uu % w]
            im.alpha_composite(ROLES[role].resize((c, c), Image.NEAREST), (col*c, r*c))
    return im
if __name__ == '__main__':
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
    FP = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    W = Image.new('RGBA', (8*190+20, 3*240+60), (52, 54, 60, 255)); d = ImageDraw.Draw(W)
    d.text((10, 8), "Motifs de la table du carreleur (version corrigée) — réglage par défaut, zone 16 × 16 ; couleur A blanc, couleur B noir, accent airain", font=F, fill=(240, 220, 160))
    for i, (titre, typ, l) in enumerate(TYPES):
        y = 40 + i*240
        d.text((10, y), titre + (" (vus de face, le bas en bas)" if typ == 'wall' else " (vus de dessus)"), font=F, fill=(240, 220, 160))
        for k, m in enumerate(l):
            x = 10 + k*190
            W.alpha_composite(rendu(m, typ == 'wall'), (x, y + 24))
            d.text((x, y + 190), NOMS[m] + ("  (taille %d)" % DEF[m] if m not in ('CHECKERBOARD', 'STRIPES', 'DIAGONALS', 'CHEVRONS', 'OFFSET_PAVERS', 'RUNNING_BOND', 'GRID') else "  (cases %d)" % DEF[m]), font=FP, fill=(220, 220, 220))
    W.convert('RGB').save('/mnt/user-data/outputs/tiler_patterns_fixed.png')
