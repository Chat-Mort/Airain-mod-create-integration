import json, math, sys
from PIL import Image
MODEL, OUT, TEXDIR = sys.argv[1], sys.argv[2], sys.argv[3]
m = json.load(open(MODEL))
T = {k: Image.open(f"{TEXDIR}/{v.split('/')[-1]}.png").convert("RGBA") for k, v in m["textures"].items()}
els = m["elements"]; N = 560; scale = 30 / N
if len(sys.argv) > 4 and sys.argv[4] == "dos":
    SW = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "up", "down": "down"}
    els = [{"from": [16-e["to"][0], e["from"][1], 16-e["to"][2]], "to": [16-e["from"][0], e["to"][1], 16-e["from"][2]],
            "faces": {SW[k]: v for k, v in e["faces"].items()}} for e in els]; scale = 30 / N
r = (1/math.sqrt(2), 0, -1/math.sqrt(2)); up = (-1/math.sqrt(6), 2/math.sqrt(6), -1/math.sqrt(6)); d = (-1/math.sqrt(3),)*3
SH = {"up": 1.0, "south": 0.8, "east": 0.62}
img = Image.new("RGB", (N, N), (38, 36, 40)); px = img.load()
for j in range(N):
    for i in range(N):
        u = (i - N/2)*scale; v = (N/2 - j)*scale + 1.0
        o = [8 + u*r[k] + v*up[k] - 40*d[k] for k in range(3)]
        best = None
        for e in els:
            f, t = e["from"], e["to"]; tmin, tmax, face = -1e9, 1e9, None
            for k, pos in enumerate(("east", "up", "south")):
                t1 = (f[k]-o[k])/d[k]; t2 = (t[k]-o[k])/d[k]
                if t1 > t2: t1, t2 = t2, t1
                if t1 > tmin: tmin, face = t1, pos
                tmax = min(tmax, t2)
            if tmin <= tmax and face in e["faces"] and (best is None or tmin < best[0]): best = (tmin, e, face)
        if not best: continue
        tt, e, face = best; f, t = e["from"], e["to"]; p = [o[k]+tt*d[k] for k in range(3)]
        fy = (t[1]-p[1])/(t[1]-f[1]) if t[1] > f[1] else 0
        if face == "up": a, b = (p[0]-f[0])/(t[0]-f[0]), (p[2]-f[2])/(t[2]-f[2])
        elif face == "south": a, b = (p[0]-f[0])/(t[0]-f[0]), fy
        else: a, b = (t[2]-p[2])/(t[2]-f[2]), fy
        fc = e["faces"][face]; u0, v0, u1, v1 = fc["uv"]; tex = T[fc["texture"][1:]]
        tw = tex.width/16
        col = tex.getpixel((min(tex.width-1, int((u0 + a*(u1-u0))*tw)), min(tex.height-1, int((v0 + b*(v1-v0))*tw))))
        s = SH[face]; px[i, j] = tuple(int(col[c]*s) for c in range(3))
img.save(OUT)
