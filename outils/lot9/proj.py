# Projecteur de chantier : maquettes de modèles (rendu orthographique, plusieurs textures par modèle)
import sys, math, numpy as np
sys.path.insert(0, '/home/claude/travail/lot8')
from cle_create import rot, FACES
from PIL import Image, ImageDraw, ImageFont
B = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
def T(n): 
    im = Image.open(B + n + '.png').convert('RGBA')
    return np.array(im.crop((0, 0, 16, 16)))
GUI = {'rotation': [30, 225, 0], 'scale': [0.625] * 3}

def rendre(elements, texs, gui=GUI, N=480, lumineux=()):
    img = np.zeros((N, N, 4), np.uint8); zb = np.full((N, N), -1e9)
    R = rot('x', gui['vue'][0]) @ rot('y', gui['vue'][1]) if 'vue' in gui else rot('z', gui['rotation'][2]) @ rot('y', gui['rotation'][1]) @ rot('x', gui['rotation'][0])
    sc = gui['scale'][0]; lum = np.array([-0.3, 0.8, 0.5]); lum /= np.linalg.norm(lum)
    for e in elements:
        f, t = np.array(e['from'], float), np.array(e['to'], float)
        r = e.get('rotation'); Rr = rot(r['axis'], r['angle']) if r else np.eye(3); org = np.array(r['origin'], float) if r else np.zeros(3)
        for nom, fc in e['faces'].items():
            coins, n = FACES[nom]
            P = [(R @ (Rr @ (f + (t - f) * np.array(k) - org) + org - 8)) * sc for k in coins]
            nn = R @ (Rr @ np.array(n, float))
            if nn[2] <= 0: continue
            tex = texs[fc['texture'].lstrip('#')]
            u1, v1, u2, v2 = fc['uv']; uv = [(u1, v1), (u2, v1), (u2, v2), (u1, v2)]
            ombre = 1.0 if fc['texture'].lstrip('#') in lumineux else 0.55 + 0.45 * max(0, float(nn @ lum))
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
                        zb[yy, xx] = z; img[yy, xx] = [min(255, int(col[0] * ombre)), min(255, int(col[1] * ombre)), min(255, int(col[2] * ombre)), 255]
    return Image.fromarray(img)

def boite(f, t, tex, faces=None, uvs=None):
    """Élément : uv tirés des coordonnées (comme Minecraft sans uv explicite)."""
    x1, y1, z1 = f; x2, y2, z2 = t; tx = tex if isinstance(tex, dict) else {}
    auto = {'north': (16 - x2, 16 - y2, 16 - x1, 16 - y1), 'south': (x1, 16 - y2, x2, 16 - y1), 'west': (z1, 16 - y2, z2, 16 - y1),
            'east': (16 - z2, 16 - y2, 16 - z1, 16 - y1), 'up': (x1, z1, x2, z2), 'down': (x1, 16 - z2, x2, 16 - z1)}
    fs = {}
    for k in faces or auto:
        fs[k] = {'texture': '#' + (tx.get(k, tx.get('*')) if tx else tex), 'uv': (uvs or {}).get(k, auto[k])}
    return {'from': f, 'to': t, 'faces': fs}

def tourne(el, axe, angle, origine):
    for e in el: e['rotation'] = {'axis': axe, 'angle': angle, 'origin': origine}
    return el
