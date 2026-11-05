import sys, math
sys.path.insert(0, '../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont

TEXI = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/models/armor/arcanique.png').convert('RGBA')
import importlib.util
G = {}
src = open('gen_arcanique.py').read()
geo = src.split("# --------------------------------------------------------------------- pièces ajoutées (repère des parties)")[1].split("L = ['package")[0]
TUILES = [None]*8
def tuile(i): return (64 + (i % 2) * 32, (i // 2) * 16)
def b(part, x, y, z, w, h, d, t): G.setdefault(part, []).append((x, y, z, w, h, d, t))
exec(geo)
R = 2
def cube(V, tex, u, v, x0, y0, z0, w, h, d, infl, piv, rot=0.0, mirror=False):
    X0, Y0, Z0 = x0 - infl, y0 - infl, z0 - infl; W, H, D = w + 2*infl, h + 2*infl, d + 2*infl
    def tx(face, fx, fy):   # fx, fy in [0,1) on face -> texture pixel
        zones = {'dessus': (u+d, v, w, d), 'dessous': (u+d+w, v, w, d), 'droite': (u, v+d, d, h), 'avant': (u+d, v+d, w, h),
                 'gauche': (u+d+w, v+d, d, h), 'arriere': (u+2*d+w, v+d, w, h)}
        if mirror:
            if face == 'droite': face = 'gauche'
            elif face == 'gauche': face = 'droite'
            fx = 1 - fx
        a, bb, fw, fh = zones[face]
        return TEXI.getpixel((int(a + min(fw - 1e-3, fx * fw)), int(bb + min(fh - 1e-3, fy * fh))))
    nx, ny, nz = max(1, int(round(W*R))), max(1, int(round(H*R))), max(1, int(round(D*R)))
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                faces = []
                if k == 0: faces.append(('avant', (i+.5)/nx, (j+.5)/ny))
                if k == nz-1: faces.append(('arriere', 1-(i+.5)/nx, (j+.5)/ny))
                if i == 0: faces.append(('droite', 1-(k+.5)/nz, (j+.5)/ny))
                if i == nx-1: faces.append(('gauche', (k+.5)/nz, (j+.5)/ny))
                if j == 0: faces.append(('dessus', (i+.5)/nx, 1-(k+.5)/nz))
                if not faces: continue
                c = None
                for f in faces:
                    p = tx(*f)
                    if p[3] > 0: c = p[:3]; break
                if c is None: continue
                mx, my, mz = X0 + (i+.5)/R, Y0 + (j+.5)/R, Z0 + (k+.5)/R
                if rot:
                    cy, sy = math.cos(rot), math.sin(rot)
                    my, mz = my*cy - mz*sy, my*sy + mz*cy
                mx += piv[0]; my += piv[1]; mz += piv[2]
                V[(int(math.floor(-mx*R)), int(math.floor(-my*R)), int(math.floor(-mz*R)))] = c
def pieces(V, part, piv):
    for (x,y,z,w,h,d,t) in G.get(part, []):
        u, v = tuile(t); cube(V, TEXI, u, v, x, y, z, w, h, d, 0, piv)
def peau(V):
    for (x0,y0,z0,w,h,d) in ((-4,-8,-4,8,8,8),(-4,0,-2,8,12,4),(-8,0,-2,4,12,4),(4,0,-2,4,12,4),(-4,12,-2,4,12,4),(0,12,-2,4,12,4)):
        for i in range(w*R):
            for j in range(h*R):
                for k in range(d*R):
                    V[(int(-(x0+(i+.5)/R)*R), int(-(y0+(j+.5)/R)*R), int(-(z0+(k+.5)/R)*R))] = (196,150,120)
def armure(V):
    cube(V, TEXI, 0, 0, -4, -8, -4, 8, 8, 8, 1, (0,0,0)); pieces(V, 'tete', (0,0,0))
    cube(V, TEXI, 16, 16, -4, 0, -2, 8, 12, 4, 1, (0,0,0)); pieces(V, 'corps', (0,0,0)); 
    cube(V, TEXI, 64, 64, -5, 10, -3, 10, 8, 6, 0, (0,0,0))
    cube(V, TEXI, 40, 16, -3, -2, -2, 4, 12, 4, 1, (-5,2,0)); pieces(V, 'bras_d', (-5,2,0))
    cube(V, TEXI, 40, 16, -1, -2, -2, 4, 12, 4, 1, (5,2,0), mirror=True); pieces(V, 'bras_g', (5,2,0))
    cube(V, TEXI, 16, 48, -4, 0, -2, 8, 12, 4, 0.5, (0,0,0))
    for px, m in ((-1.9, False), (1.9, True)):
        cube(V, TEXI, 0, 48, -2, 0, -2, 4, 12, 4, 0.5, (px,12,0), mirror=m); pieces(V, 'jambe_d' if not m else 'jambe_g', (px,12,0))
        cube(V, TEXI, 0, 16, -2, 0, -2, 4, 12, 4, 1, (px,12,0), mirror=m); pieces(V, 'pied_d' if not m else 'pied_g', (px,12,0))
V = {}; peau(V); armure(V)
a = rendu(V, T=4); Vd = {(-x, y, -z): c for (x, y, z), c in V.items()}; b2 = rendu(Vd, T=4)
out = Image.new('RGB', (a.width + b2.width, max(a.height, b2.height)), (32,33,38)); out.paste(a, (0,0)); out.paste(b2, (a.width, 0)); out.save('verif_arcanique.png'); print(out.size)
