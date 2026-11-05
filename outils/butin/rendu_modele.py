"""Rendu isométrique approximatif de modèles JSON Minecraft (éléments, rotations simples, UV)."""
import json, math
from PIL import Image, ImageDraw
SC = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/"
TEX = {"create:block/millstone": SC + "butin/ctex/millstone.png", "create:block/gearbox": SC + "butin/ctex/gearbox.png",
       "create:block/axis": SC + "butin/ctex/axis.png", "create:block/axis_top": SC + "butin/ctex/axis_top.png"}
def chemin(t):
    if t in TEX: return TEX[t]
    ns, p = t.split(":")
    if ns == "minecraft": return SC + f"mcmeta-assets/assets/minecraft/textures/{p}.png"
    return f"/home/claude/airain-mod-create-integration/src/main/resources/assets/{ns}/textures/{p}.png"
_cache = {}
def img(t):
    if t not in _cache: _cache[t] = Image.open(chemin(t)).convert("RGBA")
    return _cache[t]
def resoudre(textures, ref):
    while ref.startswith("#"): ref = textures.get(ref[1:], "minecraft:block/stone")
    return ref
def rot(p, r):
    if not r or not r.get("angle"): return p
    a = math.radians(r["angle"]); o = r["origin"]; x, y, z = (p[i] - o[i] for i in range(3)); c, s = math.cos(a), math.sin(a)
    if r["axis"] == "y": x, z = x * c + z * s, -x * s + z * c
    elif r["axis"] == "x": y, z = y * c - z * s, y * s + z * c
    else: x, y = x * c - y * s, x * s + y * c
    return (x + o[0], y + o[1], z + o[2])
FACES = {  # coins dans l'ordre (haut-gauche, haut-droite, bas-droite, bas-gauche) de l'UV, normale
 "north": (lambda f, t: [(t[0], t[1], f[2]), (f[0], t[1], f[2]), (f[0], f[1], f[2]), (t[0], f[1], f[2])], (0, 0, -1)),
 "south": (lambda f, t: [(f[0], t[1], t[2]), (t[0], t[1], t[2]), (t[0], f[1], t[2]), (f[0], f[1], t[2])], (0, 0, 1)),
 "west": (lambda f, t: [(f[0], t[1], f[2]), (f[0], t[1], t[2]), (f[0], f[1], t[2]), (f[0], f[1], f[2])], (-1, 0, 0)),
 "east": (lambda f, t: [(t[0], t[1], t[2]), (t[0], t[1], f[2]), (t[0], f[1], f[2]), (t[0], f[1], t[2])], (1, 0, 0)),
 "up": (lambda f, t: [(f[0], t[1], f[2]), (t[0], t[1], f[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2])], (0, 1, 0)),
 "down": (lambda f, t: [(f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], f[1], f[2]), (f[0], f[1], f[2])], (0, -1, 0)),
}
LUM = {"up": 1.0, "south": 0.8, "north": 0.8, "east": 0.62, "west": 0.62, "down": 0.5}
CAM = (1, 1.15, 1)
def quads(modele, transfo=lambda p: p, yrot=0):
    textures = modele.get("textures", {}); out = []
    for e in modele["elements"]:
        f, t = e["from"], e["to"]
        for nom, fc in e["faces"].items():
            coins, n = FACES[nom]
            pts = [transfo(rot(p, e.get("rotation"))) for p in coins(f, t)]
            nn = rot((n[0] + 8, n[1] + 8, n[2] + 8), dict(e.get("rotation", {}), origin=[8, 8, 8]) if e.get("rotation") else None)
            nn = (nn[0] - 8, nn[1] - 8, nn[2] - 8)
            o = transfo(rot((8, 8, 8), e.get("rotation"))); q = transfo(rot((8 + n[0], 8 + n[1], 8 + n[2]), e.get("rotation")))
            nn = tuple(q[i] - o[i] for i in range(3))
            out.append((pts, resoudre(textures, fc["texture"]), fc.get("uv"), fc.get("rotation", 0), LUM[nom], nn))
    return out
def projeter(p, S, ox, oy):
    x, y, z = p
    return (ox + (x - z) * S * 0.866, oy + (x + z) * S * 0.5 - y * S)
def dessiner(d, liste, S, ox, oy, pas=1):
    def prof(q): return sum(p[0] * CAM[0] + p[1] * CAM[1] + p[2] * CAM[2] for p in q[0]) / 4
    for pts, tex, uv, urot, lum, n in sorted(liste, key=prof):
        if n[0] * CAM[0] + n[1] * CAM[1] + n[2] * CAM[2] <= 1e-6: continue
        im = img(tex); W, H = im.size; k = W / 16
        uv = uv or [0, 0, 16, 16]
        cu, cv = 12, 12
        for j in range(cv):
            for i in range(cu):
                s0, s1, t0, t1 = i / cu, (i + 1) / cu, j / cv, (j + 1) / cv
                def P(s, t):
                    return [pts[0][m] * (1 - s) * (1 - t) + pts[1][m] * s * (1 - t) + pts[2][m] * s * t + pts[3][m] * (1 - s) * t for m in range(3)]
                ss, tt = (s0 + s1) / 2, (t0 + t1) / 2
                if urot == 90: ss, tt = tt, 1 - ss
                elif urot == 180: ss, tt = 1 - ss, 1 - tt
                elif urot == 270: ss, tt = 1 - tt, ss
                px = min(W - 1, max(0, int((uv[0] + (uv[2] - uv[0]) * ss) * k))); py = min(H - 1, max(0, int((uv[1] + (uv[3] - uv[1]) * tt) * k)))
                col = im.getpixel((px, py))
                if col[3] < 20: continue
                poly = [projeter(P(s0, t0), S, ox, oy), projeter(P(s1, t0), S, ox, oy), projeter(P(s1, t1), S, ox, oy), projeter(P(s0, t1), S, ox, oy)]
                d.polygon(poly, fill=tuple(int(c * lum) for c in col[:3]) + (255,))
