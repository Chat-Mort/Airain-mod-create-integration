"""Aperçus du grand étendard : reprend la géométrie du rendu en jeu (EtendardRenderer) et les vrais modèles."""
import json, math, sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/butin")
import rendu_modele as R
from rendu_modele import quads, projeter, LUM, CAM
from PIL import Image, ImageDraw, ImageFont
SC = R.SC; RES = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/"
R.TEX.update({"create:block/brass_block": SC + "create-src/src/main/resources/assets/create/textures/block/brass_block.png",
              "create:block/industrial_iron_block": SC + "create-src/src/main/resources/assets/create/textures/block/industrial_iron_block.png"})
FONDS = [0x8E1A16, 0x1E3A6E, 0x1F4D2E, 0x1C1A1C, 0xE6DCC2, 0x5A1E5E, 0xB8792A, 0x5E6670]
ORN = [0xE8BE5A, 0xD8DCE0, 0xC77A48, 0x282222]
FORMES = ["aronde", "droit", "pointe"]
LONG, LARG, VENT = [48, 56, 64], [20, 24, 28, 32], [0.45, 1, 1.7]

def charger(nom):
    m = json.load(open(nom))
    if "parent" in m and "elements" not in m:
        ns, p = m["parent"].split(":") if ":" in m["parent"] else ("minecraft", m["parent"])
        base = charger(SC + f"mcmeta-assets/assets/minecraft/models/{p}.json" if ns == "minecraft" else RES + f"models/{p}.json")
        base["textures"] = {**base.get("textures", {}), **m.get("textures", {})}
        return base
    return m

def teinte(nom, c):
    im = Image.open(RES + f"textures/entity/etendard/{nom}.png").convert("RGBA"); px = im.load()
    r, g, b = c >> 16 & 255, c >> 8 & 255, c & 255
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3]: px[x, y] = (p[0] * r // 255, p[1] * g // 255, p[2] * b // 255, p[3])
    return im

def partition(t, x, y):
    return {1: y >= 15, 2: x >= 8, 3: y >= 15 + abs(x - 7.5) * 1.1, 4: abs(y - 5 - x * 1.3) < 3.2, 5: x <= 3 or x >= 12 or y <= 6}.get(t, False)

def bruit(x, y, g):
    h = (x * 73856093 ^ y * 19349663 ^ g * 83492791) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0x5bd1e995) & 0xFFFFFFFF; h ^= h >> 15
    return (h & 0xFFFF) / 65535

def toile(o):
    """Même composition que TexturesBanniere (Java)."""
    fo = Image.open(RES + f"textures/entity/etendard/fond_{FORMES[o['forme']]}.png").convert("RGBA")
    orn = Image.open(RES + f"textures/entity/etendard/ornement_{FORMES[o['forme']]}.png").convert("RGBA")
    mo = Image.open(RES + f"textures/entity/etendard/motif_{o['motif']}.png").convert("RGBA") if o["motif"] else None
    c1, c2, co = FONDS[o["fond"]], FONDS[o.get("fond2", 4)], ORN[o["orn"]]
    cm = o.get("cmotif", co)
    out = Image.new("RGBA", (16, 32)); px = out.load()
    T = lambda v, c: ((c >> 16 & 255) * v // 255, (c >> 8 & 255) * v // 255, (c & 255) * v // 255, 255)
    for y in range(32):
        for x in range(16):
            p = (0, 0, 0, 0)
            if fo.getpixel((x, y))[3]: p = T(fo.getpixel((x, y))[0], c2 if partition(o.get("partition", 0), x, y) else c1)
            if mo and mo.getpixel((x, y))[3]: p = T(mo.getpixel((x, y))[0], cm)
            if orn.getpixel((x, y))[3]: p = T(orn.getpixel((x, y))[0], co)
            px[x, y] = p
    e = o.get("etat", 0)
    if e:
        d = e == 2; pale = 0.42 if d else 0.28
        bas = [max([y for y in range(32) if px[x, y][3]] or [-1]) for x in range(16)]
        for y in range(32):
            for x in range(16):
                r, g, b, a = px[x, y]
                if not a: continue
                l = (r * 3 + g * 6 + b) // 10; so = 1 - bruit(x, y, 7) * (0.22 if d else 0.12)
                r = int((r + (l + 25 - r) * pale) * so); g = int((g + (l + 22 - g) * pale) * so); b = int((b + (l + 15 - b) * pale) * so)
                bord = x in (0, 15) or y >= bas[x] - (int(bruit(x, 0, 3) * 5) if d else 0)
                ret = bord and y > 3 and bruit(x, y, 11) < (0.75 if d else 0.35)
                if d:
                    ret |= y > 3 and bruit(x, y, 29) < 0.035
                    ret |= 18 <= y <= 26 and abs(x - (13 - (y - 18) * 0.5)) < 0.6
                px[x, y] = (0, 0, 0, 0) if ret else (min(255, r), min(255, g), min(255, b), 255)
    return out

def banniere(o):
    im = toile(o)
    cle = "apercu:" + str(id(o)); f = f"ban_{id(o)}.png"; im.save(f); R.TEX[cle] = f
    fr = teinte("frange", ORN[o["orn"]]); f2 = f"fr_{id(o)}.png"; fr.save(f2); R.TEX[cle + "f"] = f2
    return cle

LONG_MUR, LARG_MUR = [32, 48, 64], [16, 20, 24, 32]
def point(o, u, v, t=37.0):
    if o.get("murale"):
        W, L, vent = LARG_MUR[o["larg"]], LONG_MUR[o["long"]], VENT[o["vent"]]
        oo = 0.7 * vent * v ** 1.2 * math.sin(t * 0.06 * (0.7 + 0.3 * vent) + v * 3 + u * 2)
        return (8 - W / 2 + u * W, 12.75 - v * L, 12.5 - abs(oo))
    if o.get("petit"):
        s = o["style"]
        if s == 0: return (16 + u * 11, 44.5 - v * 22, 8 + 1.3 * v ** 1.3 * math.sin(t * 0.1 + v * 4 + u * 2))
        if s == 1:
            oo = 1.1 * v ** 1.3 * math.sin(t * 0.09 + v * 3.5 + u * 1.5); return (1 + u * 14, 44.5 - v * 28, -1.2 - abs(oo) * 0.6 + oo * 0.4)
        return (9.5 + v * 16, 46.5 - u * 12 - 0.8 * v * v, 8 + 1.6 * v ** 1.1 * math.sin(t * 0.16 - v * 5 + u))
    W, L, vent = LARG[o["larg"]], LONG[o["long"]], VENT[o["vent"]]; vit = 0.7 + 0.3 * vent
    s = o["style"]
    if s == 0:
        x, y, z = 10.5 + u * W, 102.5 - v * L, 8
        return (x, y, z + 2.2 * vent * v ** 1.3 * math.sin(t * 0.08 * vit + v * 3 + u * 2))
    if s == 1:
        oo = 1.8 * vent * v ** 1.3 * math.sin(t * 0.07 * vit + v * 3 + u * 1.5)
        return (8 - W / 2 + u * W, 101.5 - v * L, -2 - abs(oo) * 0.6 + oo * 0.4)
    x, y = 9.5 + v * L, 104 - u * W - min(10, 2.4 / vent) * v * v
    return (x, y, 8 + 2.6 * vent * v ** 1.1 * math.sin(t * 0.13 * vit - v * 5 + u))

def bas(forme, u):
    x = u * 16 - 0.5; d = abs(x - 7.5) * 0.85
    rang = 25 + d if forme == 0 else 31.4 - d if forme == 2 else 31
    return min(1, (rang + 1) / 32)

def normale(p):
    a = [p[1][i] - p[0][i] for i in range(3)]; b = [p[3][i] - p[0][i] for i in range(3)]
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def drap(o, tex, T, Lq):
    nu, nv = 12, 24
    for i in range(nu):
        for j in range(nv):
            u0, u1, v0, v1 = i / nu, (i + 1) / nu, j / nv, (j + 1) / nv
            p = [T(point(o, u0, v0)), T(point(o, u1, v0)), T(point(o, u1, v1)), T(point(o, u0, v1))]
            uv = [u0 * 16, v0 * 32, u1 * 16, v1 * 32]
            n = normale(p)
            Lq.append((p, tex, uv, 0, 0.92, n))
            Lq.append((p[::-1], tex, [uv[2], uv[1], uv[0], uv[3]], 0, 0.75, tuple(-c for c in n)))
    if o.get("franges"):
        n = 24
        for i in range(n):
            a0, a1 = i / n, (i + 1) / n
            if o["style"] == 2 and not o.get("murale"):
                fin = bas(o["forme"], 1); h0, h1 = point(o, 1, a0 * fin), point(o, 1, a1 * fin)
                t0, t1 = a0 * fin * LONG[o["long"]], a1 * fin * LONG[o["long"]]
            else:
                h0, h1 = point(o, a0, bas(o["forme"], a0)), point(o, a1, bas(o["forme"], a1))
                lw = (LARG_MUR if o.get("murale") else LARG)[o["larg"]]
                t0, t1 = a0 * lw, a1 * lw
            b0, b1 = (h0[0], h0[1] - 4, h0[2]), (h1[0], h1[1] - 4, h1[2])
            p = [T(h0), T(h1), T(b1), T(b0)]
            for k in range(2):
                q = p if k == 0 else [p[1], p[0], p[3], p[2]]
                uv = [t0 % 16, 0, t0 % 16 + (t1 - t0), 4] if k == 0 else [t0 % 16 + (t1 - t0), 0, t0 % 16, 4]
                Lq.append((q, tex + "f", uv, 0, 1.0, normale(q)))

def boite(f, t, tex, T, Lq):
    m = {"textures": {"x": tex}, "elements": [{"from": list(f), "to": list(t), "faces": {k: {"uv": None, "texture": "#x"} for k in ("north", "south", "east", "west", "up", "down")}}]}
    for e in m["elements"]:
        for k, fc in e["faces"].items():
            fc["uv"] = [0, 0, min(16, abs(t[0] - f[0]) if k in ("north", "south", "up", "down") else abs(t[2] - f[2])), min(16, abs(t[1] - f[1]) if k not in ("up", "down") else abs(t[2] - f[2]))]
    Lq += quads(m, T)

def bloc(modele, dy, T, Lq, yrot=0):
    Lq += quads(charger(modele), lambda p: T((p[0], p[1] + dy, p[2])))

def lanterne(x, y, z, T, Lq):
    m = charger(SC + "mcmeta-assets/assets/minecraft/models/block/lantern_hanging.json")
    Lq += quads(m, lambda p: T((p[0] + x - 8, p[1] + y - 16, p[2] + z - 8)))

def fleuron(type_, T, Lq, dy):
    G = "minecraft:block/gold_block"; B = lambda f, t: boite((f[0], f[1] + dy, f[2]), (t[0], t[1] + dy, t[2]), G, T, Lq)
    if type_ == 0:
        B((6.25, 108, 6.25), (9.75, 111.5, 9.75)); B((5.75, 108.75, 5.75), (10.25, 110.75, 10.25)); B((7.25, 111.5, 7.25), (8.75, 115, 8.75)); B((7.6, 115, 7.6), (8.4, 117, 8.4))
    elif type_ == 1:
        B((7.25, 108, 7.25), (8.75, 109.5, 8.75)); B((5.5, 110.5, 6.5), (10.5, 113.5, 9.5)); B((6.5, 110.5, 5.5), (9.5, 113.5, 10.5)); B((6.5, 109.5, 6.5), (9.5, 114.5, 9.5)); B((7.5, 114.5, 7.5), (8.5, 115.5, 8.5))
    elif type_ == 2:
        B((7.25, 108, 7.25), (8.75, 110.5, 8.75))
        for k in range(8):
            a = math.radians(k * 45 + 10)
            def RZ(p, a=a): return (8 + p[0] * math.cos(a) - p[1] * math.sin(a), 114.5 + dy + p[0] * math.sin(a) + p[1] * math.cos(a), 8 + p[2])
            for f, t in (((-1.3, 2.4, -0.6), (1.3, 3.4, 0.6)), ((-0.8, 3.4, -0.6), (0.8, 4.6, 0.6))) + ((((-0.4, 1.25, -0.4), (0.4, 2.4, 0.4)),) if k % 2 == 0 else ()):
                boite(f, t, G, lambda p, RZ=RZ: T(RZ(p)), Lq)
        boite((-1.25, -1.25, -0.9), (1.25, 1.25, 0.9), G, lambda p: T((8 + p[0], 114.5 + dy + p[1], 8 + p[2])), Lq)
    else:
        B((7, 108, 7), (9, 109, 9)); B((5.5, 109, 5.5), (10.5, 111, 10.5))
        for c in ((5.5, 5.5), (9.5, 5.5), (5.5, 9.5), (9.5, 9.5)): B((c[0], 111, c[1]), (c[0] + 1, 113, c[1] + 1))
        for c in ((7.5, 5.5), (7.5, 9.5), (5.5, 7.5), (9.5, 7.5)): B((c[0], 111, c[1]), (c[0] + 1, 112.5, c[1] + 1))
        B((7.25, 111, 7.25), (8.75, 113.5, 8.75)); B((7.6, 113.5, 7.6), (8.4, 115.5, 8.4)); B((7, 114.2, 7.6), (9, 114.8, 8.4))

def ferrures(o, T, Lq):
    F, LA = "create:block/industrial_iron_block", "create:block/brass_block"; W = LARG[o["larg"]]
    b = lambda f, t, x: boite(f, t, x, T, Lq)
    if o["style"] == 0:
        e = 6 if o["lanternes"] else 3
        b((9.5, 102.5, 7.25), (9.5 + e + W, 104, 8.75), F); b((9.5, 99, 7.5), (11, 102.5, 8.5), F)
        b((8.5 + e + W, 102, 7), (10.5 + e + W, 104.5, 9), LA); b((5.5, 101.5, 5.5), (10.5, 103, 10.5), LA)
        if o["lanternes"]: lanterne(15.5 + W, 102.5, 8, T, Lq)
    elif o["style"] == 1:
        e = 5 if o["lanternes"] else 1
        b((7.25, 101, -2.5), (8.75, 102.5, 6), F); b((8 - W / 2 - e, 101.5, -2.75), (8 + W / 2 + e, 103, -1.25), F)
        b((8 - W / 2 - e - 1.5, 101, -3.25), (8 - W / 2 - e, 103.5, -0.75), LA); b((8 + W / 2 + e, 101, -3.25), (8 + W / 2 + e + 1.5, 103.5, -0.75), LA)
        b((5.5, 100.5, 5.5), (10.5, 102, 10.5), LA)
        if o["lanternes"]: lanterne(8 - W / 2 - 4, 101.5, -2, T, Lq); lanterne(8 + W / 2 + 4, 101.5, -2, T, Lq)
    else:
        b((5.5, 103.5, 5.5), (10.5, 105, 10.5), LA); b((5.5, 103.5 - W, 5.5), (10.5, 105 - W, 10.5), LA)

def scene(o, vue):
    """vue : fonction (x,y,z) pixels étendard -> monde."""
    Lq = []; h = o["h"]; dy = (h - 6) * 16
    bloc(RES + "models/block/etendard_socle.json", 0, vue, Lq)
    for k in range(1, h + 1):
        m = "grand_mat_haut" if k == h else "grand_mat_pied" if k == 1 else ("grand_mat_bague" if k % 2 else "grand_mat")
        bloc(RES + f"models/block/{m}.json", 16 * k, vue, Lq)
    tex = banniere(o)
    fleuron(o["fleuron"], vue, Lq, dy)
    for c in range(2 if o["double"] and o["style"] != 1 else 1):
        mir = (lambda p: p) if c == 0 else (lambda p: (16 - p[0], p[1], p[2]))
        T = lambda p, mir=mir: vue(mir((p[0], p[1] + dy, p[2])))
        ferrures(o, T, Lq); drap(o, tex, T, Lq)
    if o["lanternes"] and o["style"] == 2:
        T = lambda p: vue((p[0], p[1] + dy, p[2]))
        boite((7.25, 100, -3), (8.75, 101.5, 6.5), "create:block/industrial_iron_block", T, Lq)
        boite((7.25, 100, 9.5), (8.75, 101.5, 19), "create:block/industrial_iron_block", T, Lq)
        lanterne(8, 100, -2, T, Lq); lanterne(8, 100, 18, T, Lq)
    return Lq

def dessiner(d, liste, S, ox, oy):
    def prof(q): return sum(p[0] * CAM[0] + p[1] * CAM[1] + p[2] * CAM[2] for p in q[0]) / 4
    for pts, tex, uv, urot, lum, n in sorted(liste, key=prof):
        if n[0] * CAM[0] + n[1] * CAM[1] + n[2] * CAM[2] <= 1e-6: continue
        im = R.img(tex); W, H = im.size; k = W / 16
        uv = uv or [0, 0, 16, 16]
        cu = max(1, min(16, round(abs(uv[2] - uv[0]) * k))); cv = max(1, min(16, round(abs(uv[3] - uv[1]) * k)))
        for j in range(cv):
            for i in range(cu):
                s0, s1, t0, t1 = i / cu, (i + 1) / cu, j / cv, (j + 1) / cv
                P = lambda s, t: [pts[0][m] * (1 - s) * (1 - t) + pts[1][m] * s * (1 - t) + pts[2][m] * s * t + pts[3][m] * (1 - s) * t for m in range(3)]
                ss, tt = (s0 + s1) / 2, (t0 + t1) / 2
                px = int((uv[0] + (uv[2] - uv[0]) * ss) * k) % W; py = min(H - 1, max(0, int((uv[1] + (uv[3] - uv[1]) * tt) * k)))
                col = im.getpixel((px, py))
                if col[3] < 20: continue
                d.polygon([projeter(P(a, b), S, ox, oy) for a, b in ((s0, t0), (s1, t0), (s1, t1), (s0, t1))], fill=tuple(int(c * lum) for c in col[:3]) + (255,))

VUE = lambda p: (16 - p[0], p[1], 16 - p[2])          # le devant de l'étendard tourné vers nous

def scene_murale(o, vue):
    Lq = []; W = LARG_MUR[o["larg"]]; e = 6.5 if o["lanternes"] else 1.5
    F, LA = "create:block/industrial_iron_block", "create:block/brass_block"
    # pan de mur derrière
    for bx in range(-24, 40, 16):
        for by in range(-56, 24, 16):
            boite((bx, by, 16), (bx + 16, by + 16, 20), "minecraft:block/stone_bricks", vue, Lq)
    boite((8 - W / 2 - e, 12.25, 11.75), (8 + W / 2 + e, 13.75, 13.25), F, vue, Lq)
    for x in (8 - W / 2 + 1, 8 + W / 2 - 1):
        boite((x - 0.75, 12, 13.25), (x + 0.75, 14, 16), LA, vue, Lq); boite((x - 1.5, 11, 15.4), (x + 1.5, 15, 16), LA, vue, Lq)
    for c in (0, 1):
        ex = 8 + W / 2 + e if c == 0 else 8 - W / 2 - e; ang = math.radians(-90 if c == 0 else 90)
        def T(p, ex=ex, ang=ang):
            x, y, z = (p[0] - 8) * 0.4, (p[1] - 108) * 0.4, (p[2] - 8) * 0.4
            return vue((ex + x * math.cos(ang) - y * math.sin(ang), 13 + x * math.sin(ang) + y * math.cos(ang), 12.5 + z))
        fleuron(o["fleuron"], T, Lq, 0)
    if o["lanternes"]:
        lanterne(8 - W / 2 - 3.5, 12.25, 12.5, vue, Lq); lanterne(8 + W / 2 + 3.5, 12.25, 12.5, vue, Lq)
    drap(o, banniere(o), vue, Lq)
    return Lq

def scene_petit(o, vue):
    Lq = []
    bloc(RES + "models/block/etendard_socle.json", 0, vue, Lq)
    bloc(RES + "models/block/etendard_mat_" + ["potence", "vexillum", "ceremonie"][o["style"]] + ".json", 16, vue, Lq)
    drap(o, banniere(o), vue, Lq)
    return Lq
