"""Trousse de dessin des plans v7 : tracé suréchantillonné, formes pleines qui masquent ce qu'elles recouvrent,
courbes de Bézier, hachures de coupe et traits d'axe. Coordonnées unitaires dans la boîte du dessin."""
import math
from PIL import Image, ImageDraw, ImageChops

T, T2, T3, R = (226, 236, 250), (160, 194, 232), (104, 146, 204), (238, 116, 96)
SS = 4

def bez(p0, p1, p2, p3, n=18):
    out = []
    for i in range(n + 1):
        t = i/n; a = (1 - t)**3; b = 3*(1 - t)**2*t; c = 3*(1 - t)*t*t; d = t**3
        out.append((a*p0[0] + b*p1[0] + c*p2[0] + d*p3[0], a*p0[1] + b*p1[1] + c*p2[1] + d*p3[1]))
    return out
def quad(p0, p1, p2, n=14):
    return [((1 - t)**2*p0[0] + 2*(1 - t)*t*p1[0] + t*t*p2[0], (1 - t)**2*p0[1] + 2*(1 - t)*t*p1[1] + t*t*p2[1]) for t in [i/n for i in range(n + 1)]]

class K:
    def __init__(s, W, H, bx, by, bw, bh, lw=1.0):
        s.W, s.H, s.bx, s.by, s.bw, s.bh, s.lw = W, H, bx, by, bw, bh, lw
        s.L = Image.new("RGBA", (W*SS, H*SS), (0, 0, 0, 0)); s.dl = ImageDraw.Draw(s.L)
        s.F = Image.new("L", (W*SS, H*SS), 0); s.df = ImageDraw.Draw(s.F)
        s.k = s.bw/s.bh   # rapport pour les cercles
    # conversions
    def P(s, p): return ((s.bx + p[0]*s.bw)*SS, (s.by + p[1]*s.bh)*SS)
    def Ps(s, pts): return [s.P(p) for p in pts]
    def ww(s, w): return max(1, int(round(w*s.lw*SS)))
    # tracés
    def line(s, pts, c=T, w=1.0):
        q = s.Ps(pts)
        if len(q) >= 2: s.dl.line(q, fill=c + (255,), width=s.ww(w), joint="curve")
        r = s.ww(w)/2
        if r >= 2:
            for x, y in (q[0], q[-1]): s.dl.ellipse([x - r + 1, y - r + 1, x + r - 1, y + r - 1], fill=c + (255,))
    def closed(s, pts, c=T, w=1.0): s.line(list(pts) + [pts[0], pts[1]], c, w)
    def solid(s, pts, c=T, w=1.0, fill=True):
        q = s.Ps(pts); s.dl.polygon(q, fill=(0, 0, 0, 0))
        if fill: s.df.polygon(q, fill=255)
        else: s.df.polygon(q, fill=0)
        s.closed(pts, c, w)
    def hole(s, pts, c=T2, w=0.8):
        """Ouverture : efface le remplissage, garde un contour."""
        q = s.Ps(pts); s.dl.polygon(q, fill=(0, 0, 0, 0)); s.df.polygon(q, fill=0); s.closed(pts, c, w)
    def dash(s, pts, c=T3, w=0.7, on=5, off=3):
        q = s.Ps(pts); tot = 0; dessin = True; pas = (on*SS*s.lw, off*SS*s.lw)
        for (x0, y0), (x1, y1) in zip(q, q[1:]):
            L = math.hypot(x1 - x0, y1 - y0); t = 0
            while t < L:
                seg = min(pas[0 if dessin else 1] - tot, L - t)
                if dessin:
                    a = (x0 + (x1 - x0)*t/L, y0 + (y1 - y0)*t/L); b = (x0 + (x1 - x0)*(t + seg)/L, y0 + (y1 - y0)*(t + seg)/L)
                    s.dl.line([a, b], fill=c + (255,), width=s.ww(w))
                t += seg; tot += seg
                if tot >= pas[0 if dessin else 1] - 1e-6: tot = 0; dessin = not dessin
    def axe(s, a, b): s.dash([a, b], T3, 0.6, 7, 2)
    def dot(s, p, r=0.9, c=T2):
        x, y = s.P(p); rr = r*s.lw*SS; s.dl.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c + (255,))
    def hatch(s, pts, c=T3, pas=3.0, ang=1):
        tmp = Image.new("RGBA", s.L.size, (0, 0, 0, 0)); dt = ImageDraw.Draw(tmp); q = s.Ps(pts)
        xs = [p[0] for p in q]; ys = [p[1] for p in q]; x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); h = y1 - y0
        st = max(2, int(pas*SS*s.lw)); k = int(x0 - h)
        while k < x1 + h:
            if ang > 0: dt.line([(k, y1), (k + h, y0)], fill=c + (255,), width=s.ww(0.6))
            else: dt.line([(k, y0), (k + h, y1)], fill=c + (255,), width=s.ww(0.6))
            k += st
        m = Image.new("L", s.L.size, 0); ImageDraw.Draw(m).polygon(q, fill=255)
        s.L.paste(tmp, (0, 0), ImageChops.multiply(m, tmp.getchannel("A")))
    # formes
    def ell(s, cu, cv, ru, rv, a0=0, a1=360, n=None):
        n = n or max(24, int((a1 - a0)/6))
        return [(cu + ru*math.cos(math.radians(a0 + (a1 - a0)*i/n)), cv + rv*math.sin(math.radians(a0 + (a1 - a0)*i/n))) for i in range(n + 1)]
    def cer(s, cu, cv, r, a0=0, a1=360): return s.ell(cu, cv, r, r*s.k, a0, a1)
    def rrect(s, u0, v0, u1, v1, r):
        rv = r*s.k; pts = []
        for (cu, cv, a) in ((u1 - r, v0 + rv, -90), (u1 - r, v1 - rv, 0), (u0 + r, v1 - rv, 90), (u0 + r, v0 + rv, 180)):
            pts += s.ell(cu, cv, r, rv, a, a + 90, 6)
        return pts
    def rect(s, u0, v0, u1, v1): return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    def gear(s, cu, cv, r, n, prof=0.16):
        pts = []
        for k in range(n):
            a = 2*math.pi*k/n; dp = 2*math.pi/n
            for f, rr in ((-0.5, 1 - prof), (-0.3, 1 - prof), (-0.18, 1), (0.18, 1), (0.3, 1 - prof)):
                b = a + f*dp; pts.append((cu + math.cos(b)*r*rr, cv + math.sin(b)*r*rr*s.k))
        return pts
    def rivets(s, a, b, n, c=T2, r=0.7):
        for i in range(n):
            t = i/max(1, n - 1); s.dot((a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t), r, c)
    def wheel(s, cu, cv, r, rayons=10, moyeu=0.14, jante=0.12, c=T, contrepoids=False):
        s.solid(s.cer(cu, cv, r), c, 1.1); s.closed(s.cer(cu, cv, r*(1 - jante)), T2, 0.8)
        for k in range(rayons):
            a = 2*math.pi*k/rayons
            s.line([(cu + math.cos(a)*r*moyeu, cv + math.sin(a)*r*moyeu*s.k), (cu + math.cos(a)*r*(1 - jante), cv + math.sin(a)*r*(1 - jante)*s.k)], T2, 0.8)
        if contrepoids: s.solid(s.cer(cu, cv, r*(1 - jante), 200, 260) + [(cu, cv)], T2, 0.8)
        s.solid(s.cer(cu, cv, r*moyeu), c, 0.9); s.dot((cu, cv), 0.8, T)
    def spring(s, a, b, n, rayon, front=T, back=T3):
        """Ressort hélicoïdal vu de côté, de a vers b (axe quelconque)."""
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx*s.bw, dy*s.bh); ux, uy = dx*s.bw/L, dy*s.bh/L; nx, ny = -uy, ux
        def pt(t, ph):
            x = a[0]*s.bw + dx*s.bw*t + nx*rayon*s.bw*math.sin(ph) + ux*rayon*s.bw*0.25*math.cos(ph)
            y = a[1]*s.bh + dy*s.bh*t + ny*rayon*s.bw*math.sin(ph) + uy*rayon*s.bw*0.25*math.cos(ph)
            return (x/s.bw, y/s.bh)
        N = n*24
        for half in (1, 0):
            for i in range(N):
                ph = 2*math.pi*i/24
                if (math.cos(ph) > 0) == bool(half): continue
                s.line([pt(i/N, ph), pt((i + 1)/N, ph + 2*math.pi/24)], front if math.cos(ph) <= 0 else back, 1.0 if math.cos(ph) <= 0 else 0.7)
    def rendu(s, fond):
        """Réduit et compose sur le fond : remplissage légèrement plus clair, puis les traits."""
        W, H = s.W, s.H
        F = s.F.resize((W, H), Image.BOX)
        clair = Image.new("RGB", (W, H), (70, 124, 196))
        out = Image.composite(clair, fond, F.point(lambda v: int(v*0.55)))
        Lr = s.L.convert("RGBa").resize((W, H), Image.LANCZOS).convert("RGBA")
        out = out.convert("RGBA"); out.alpha_composite(Lr)
        return out.convert("RGB")
