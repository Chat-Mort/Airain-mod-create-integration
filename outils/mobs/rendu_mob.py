"""Rendu 3/4 d'un modèle d'entité en boîtes (UV « box » de Minecraft), pour les aperçus."""
import math
from PIL import Image

def boite(x0, y0, z0, w, h, d, u, v, gonfle=0):
    return {"f": (x0-gonfle, y0-gonfle, z0-gonfle), "t": (x0+w+gonfle, y0+h+gonfle, z0+d+gonfle), "uv": (u, v, w, h, d)}

MODELES = {
 "humanoide": lambda bras=4, jambe=4: [
    boite(-4, 0, -2, jambe, 12, 4, 0, 16) if jambe == 4 else boite(-3, 0, -1, 2, 12, 2, 0, 16),
    boite(0, 0, -2, jambe, 12, 4, 0, 16) if jambe == 4 else boite(1, 0, -1, 2, 12, 2, 0, 16),
    boite(-4, 12, -2, 8, 12, 4, 16, 16),
    boite(-4-bras, 12, -bras/2, bras, 12, bras, 40, 16), boite(4, 12, -bras/2, bras, 12, bras, 40, 16),
    boite(-4, 24, -4, 8, 8, 8, 0, 0), boite(-4, 24, -4, 8, 8, 8, 32, 0, gonfle=0.5)],
 "creeper": lambda: [
    boite(-4, 0, 2, 4, 6, 4, 0, 16), boite(0, 0, 2, 4, 6, 4, 0, 16), boite(-4, 0, -6, 4, 6, 4, 0, 16), boite(0, 0, -6, 4, 6, 4, 0, 16),
    boite(-4, 6, -2, 8, 12, 4, 16, 16), boite(-4, 18, -4, 8, 8, 8, 0, 0)],
 "araignee": lambda: [
    boite(-5, 5, -15, 10, 8, 12, 0, 12), boite(-3, 6, -3, 6, 6, 6, 0, 0), boite(-4, 5, 3, 8, 8, 8, 32, 4)] +
    [boite(3, 8, z, 16, 2, 2, 18, 0) for z in (-4, -1, 2, 5)] + [boite(-19, 8, z, 16, 2, 2, 18, 0) for z in (-4, -1, 2, 5)],
}

def rendre(tex, boites, N=420, centre=(0, 16, 0), taille=40, dos=False):
    tex = tex.convert("RGBA"); W, H = tex.size
    r = (1/math.sqrt(2), 0, -1/math.sqrt(2)); up = (-1/math.sqrt(6), 2/math.sqrt(6), -1/math.sqrt(6)); d = (-1/math.sqrt(3),)*3
    noms = ("east", "up", "south")
    if dos:
        r = (-1/math.sqrt(2), 0, 1/math.sqrt(2)); up = (1/math.sqrt(6), 2/math.sqrt(6), 1/math.sqrt(6))
        d = (1/math.sqrt(3), -1/math.sqrt(3), 1/math.sqrt(3)); noms = ("west", "up", "north")
    img = Image.new("RGB", (N, N), (40, 42, 48)); px = img.load(); sc = taille/N
    SH = {"up": 1.0, "south": 0.84, "east": 0.66, "north": 0.84, "west": 0.66}
    for j in range(N):
        for i in range(N):
            u = (i-N/2)*sc; v = (N/2-j)*sc
            o = [centre[k] + u*r[k] + v*up[k] - 80*d[k] for k in range(3)]
            hits = []
            for b in boites:
                f, t = b["f"], b["t"]; tmin, tmax, face = -1e9, 1e9, None
                for k, nom in enumerate(noms):
                    t1 = (f[k]-o[k])/d[k]; t2 = (t[k]-o[k])/d[k]
                    if t1 > t2: t1, t2 = t2, t1
                    if t1 > tmin: tmin, face = t1, nom
                    tmax = min(tmax, t2)
                if tmin <= tmax: hits.append((tmin, b, face))
            for tt, b, face in sorted(hits, key=lambda h: h[0]):
                f, t = b["f"], b["t"]; p = [o[k]+tt*d[k] for k in range(3)]
                u0, v0, w, h, dd = b["uv"]
                fy = (t[1]-p[1])/(t[1]-f[1])
                if face == "up": x = u0+dd + (p[0]-f[0])/(t[0]-f[0])*w; y = v0 + (p[2]-f[2])/(t[2]-f[2])*dd
                elif face == "south": x = u0+dd + (p[0]-f[0])/(t[0]-f[0])*w; y = v0+dd + fy*h
                elif face == "east": x = u0+dd+w + (t[2]-p[2])/(t[2]-f[2])*dd; y = v0+dd + fy*h
                elif face == "north": x = u0+2*dd+w + (t[0]-p[0])/(t[0]-f[0])*w; y = v0+dd + fy*h
                else: x = u0 + (p[2]-f[2])/(t[2]-f[2])*dd; y = v0+dd + fy*h
                c = tex.getpixel((min(W-1, max(0, int(x))), min(H-1, max(0, int(y)))))
                if c[3] < 128: continue
                s = SH[face]; px[i, j] = tuple(int(c[k]*s) for k in range(3)); break
    return img
