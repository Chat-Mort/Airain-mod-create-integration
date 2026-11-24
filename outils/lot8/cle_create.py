# Clé à molette d'airain : le modèle 3D de la clé de Create, retexturé (airain, manche noir des outils impériaux,
# garnitures d'acier, pièce rouge en airain rouge impérial). + un petit rendu de modèle de bloc pour les maquettes.
import json, math, colorsys
import numpy as np
from PIL import Image
C = '/tmp/src5/create/src/main/resources/assets/create/'
def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
RAMPES = {
    'airain': [hx(c) for c in ('8a5a2e', 'a8763c', 'b48242', 'c99b52', 'e1ba6e', 'f3d694', 'fff0c0')],
    'manche': [hx(c) for c in ('100c14', '1a151e', '302936', '4a4258', '625a72')],
    'acier': [hx(c) for c in ('4e5466', '6e7488', '9ea4b8', 'c8ccdc', 'f0faff')],
    'rouge': [hx(c) for c in ('520019', '7e0019', '8b0018', 'af1d25', 'c04343')]}

def famille(c):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in c])
    if s < 0.1: return 'acier'
    if (h < 0.03 or h > 0.95) and s > 0.2: return 'rouge'
    if l < 0.27: return 'manche'
    return 'airain'

def retexturer():
    o = Image.open(C + 'textures/item/wrench.png').convert('RGBA'); im = o.copy(); px = im.load()
    par = {}
    for y in range(16):
        for x in range(16):
            c = px[x, y]
            if c[3]: par.setdefault(famille(c[:3]), set()).add(c[:3])
    table = {}
    for f, cs in par.items():                                  # on garde l'ordre des clartés de l'original dans chaque famille
        cs = sorted(cs, key=lambda c: colorsys.rgb_to_hls(*[v / 255 for v in c])[1]); r = RAMPES[f]
        for i, c in enumerate(cs): table[c] = r[round(i * (len(r) - 1) / max(1, len(cs) - 1))]
    for y in range(16):
        for x in range(16):
            c = px[x, y]
            if c[3]: px[x, y] = table[c[:3]] + (255,)
    return im

# ---------------- rendu orthographique d'un modèle de bloc (éléments, rotation d'élément, vue « gui »)
def rot(axis, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return {'x': np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), 'y': np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]), 'z': np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[axis]

FACES = {'north': ([(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)], (0, 0, -1)), 'south': ([(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)], (0, 0, 1)),
         'west': ([(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)], (-1, 0, 0)), 'east': ([(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)], (1, 0, 0)),
         'up': ([(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], (0, 1, 0)), 'down': ([(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)], (0, -1, 0))}

def rendre(elements, tex, gui, N=480):
    tex = np.array(tex.convert('RGBA')); img = np.zeros((N, N, 4), np.uint8); zb = np.full((N, N), -1e9)
    R = rot('z', gui['rotation'][2]) @ rot('y', gui['rotation'][1]) @ rot('x', gui['rotation'][0])
    sc = gui.get('scale', [1, 1, 1])[0]; tr = np.array(gui.get('translation', [0, 0, 0]))
    lum = np.array([-0.3, 0.8, 0.5]); lum = lum / np.linalg.norm(lum)
    for e in elements:
        f, t = np.array(e['from'], float), np.array(e['to'], float)
        r = e.get('rotation'); Rr = rot(r['axis'], r['angle']) if r and r['angle'] else np.eye(3); org = np.array(r['origin'], float) if r else np.zeros(3)
        for nom, fc in e['faces'].items():
            coins, n = FACES[nom]
            P = [Rr @ (f + (t - f) * np.array(k) - org) + org for k in coins]
            P = [(R @ (p - 8)) * sc + tr for p in P]
            nn = R @ (Rr @ np.array(n, float))
            if nn[2] <= 0: continue                                     # face tournée vers l'arrière
            u1, v1, u2, v2 = fc['uv']; rr = fc.get('rotation', 0) or 0
            uv = [(u1, v1), (u2, v1), (u2, v2), (u1, v2)]
            k = rr // 90; uv = uv[-k:] + uv[:-k] if k else uv
            ombre = 0.55 + 0.45 * max(0, float(nn @ lum))
            # deux triangles, interpolation barycentrique
            pts = [(N / 2 + p[0] * N / 18, N / 2 - p[1] * N / 18, p[2]) for p in P]
            for tri in ((0, 1, 2), (0, 2, 3)):
                (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [pts[i] for i in tri]
                d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
                if abs(d) < 1e-9: continue
                for yy in range(int(max(0, min(y0, y1, y2))), int(min(N - 1, max(y0, y1, y2))) + 1):
                    for xx in range(int(max(0, min(x0, x1, x2))), int(min(N - 1, max(x0, x1, x2))) + 1):
                        px_, py_ = xx + 0.5, yy + 0.5
                        a = ((y1 - y2) * (px_ - x2) + (x2 - x1) * (py_ - y2)) / d; b = ((y2 - y0) * (px_ - x2) + (x0 - x2) * (py_ - y2)) / d; c = 1 - a - b
                        if a < -1e-6 or b < -1e-6 or c < -1e-6: continue
                        z = a * z0 + b * z1 + c * z2
                        if z <= zb[yy, xx]: continue
                        uu = a * uv[tri[0]][0] + b * uv[tri[1]][0] + c * uv[tri[2]][0]; vv = a * uv[tri[0]][1] + b * uv[tri[1]][1] + c * uv[tri[2]][1]
                        col = tex[min(15, max(0, int(vv))), min(15, max(0, int(uu)))]
                        if col[3] < 10: continue
                        zb[yy, xx] = z; img[yy, xx] = [int(col[0] * ombre), int(col[1] * ombre), int(col[2] * ombre), 255]
    return Image.fromarray(img)

def modele():
    it = json.load(open(C + 'models/item/wrench/item.json')); g = json.load(open(C + 'models/item/wrench/gear.json'))
    return it['elements'] + g['elements'], it['display']

if __name__ == '__main__':
    el, disp = modele(); n = retexturer()
    a = rendre(el, Image.open(C + 'textures/item/wrench.png'), disp['gui']); b = rendre(el, n, disp['gui'])
    W = Image.new('RGBA', (980, 500), (139, 139, 139, 255)); W.alpha_composite(a, (0, 10)); W.alpha_composite(b, (490, 10)); W.save('/tmp/nv/cc.png')
    n.save('/tmp/nv/airain_wrench.png')
