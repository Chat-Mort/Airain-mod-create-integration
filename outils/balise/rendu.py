import json, math, sys
from PIL import Image
D = sys.argv[1]; MODEL = sys.argv[2]; OUT = sys.argv[3]; TEX = json.loads(sys.argv[4])
m = json.load(open(MODEL))
tex = {k: Image.open(v).convert("RGBA").crop((0, 0, 16, 16)) for k, v in TEX.items()}
els = m["elements"]
N = 560
r = (1/math.sqrt(2), 0, -1/math.sqrt(2)); up = (-1/math.sqrt(6), 2/math.sqrt(6), -1/math.sqrt(6)); d = (-1/math.sqrt(3),)*3
c = (8, 8, 8); scale = 30/N
img = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = img.load()
SH = {"up": 1.0, "south": 0.82, "east": 0.66, "north": 0.7, "west": 0.75, "down": 0.5}
for j in range(N):
    for i in range(N):
        u = (i - N/2) * scale; v = (N/2 - j) * scale + 1.0
        o = [c[k] + u*r[k] + v*up[k] - 40*d[k] for k in range(3)]
        best = None
        for e in els:
            f, t = e["from"], e["to"]; tmin, tmax, face = -1e9, 1e9, None
            ok = True
            for k, (neg, pos) in enumerate((("west", "east"), ("down", "up"), ("north", "south"))):
                if abs(d[k]) < 1e-9: continue
                t1 = (f[k] - o[k]) / d[k]; t2 = (t[k] - o[k]) / d[k]
                n1 = neg; 
                if t1 > t2: t1, t2 = t2, t1
                # rayon dirigé vers -x,-y,-z : on entre par la face « positive »
                if t1 > tmin: tmin, face = t1, pos
                tmax = min(tmax, t2)
            if tmin > tmax or face not in e["faces"]: continue
            if best is None or tmin < best[0]: best = (tmin, e, face)
        if not best: continue
        tt, e, face = best; p = [o[k] + tt*d[k] for k in range(3)]
        x, y, z = p
        if face == "up": uu, vv = x, z
        elif face == "south": uu, vv = x, 16 - y
        else: uu, vv = 16 - z, 16 - y
        key = e["faces"][face]["texture"][1:]
        col = tex[key].getpixel((min(15, max(0, int(uu))), min(15, max(0, int(vv)))))
        s = SH[face]
        px[i, j] = (int(col[0]*s), int(col[1]*s), int(col[2]*s), 255)
fond = Image.new("RGBA", (N, N), (38, 36, 40, 255)); fond.alpha_composite(img); fond.convert("RGB").save(OUT)
