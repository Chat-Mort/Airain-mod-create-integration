import math, sys
sys.path.insert(0, "../butin"); sys.path.insert(0, "../apercu_etendard"); sys.path.insert(0, "../gui_empire")
import rendu_modele as R
from rendu_modele import quads, projeter, CAM
from PIL import Image, ImageDraw, ImageFont
import geo
from police import texte
SC = R.SC; T = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/"
FONDS = [0x8E1A16, 0x1E3A6E, 0x1F4D2E, 0x1C1A1C, 0xE6DCC2, 0x5A1E5E, 0xB8792A, 0x5E6670]
ORN = [0xE8BE5A, 0xD8DCE0, 0xC77A48, 0x282222]
def teinte(src, c, nom):
    im = Image.open(src).convert("RGBA"); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3]: px[x, y] = (p[0] * (c >> 16 & 255) // 255, p[1] * (c >> 8 & 255) // 255, p[2] * (c & 255) // 255, p[3])
    f = f"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/socle2/t_{nom}.png"; im.save(f); R.TEX["apercu:" + nom] = f
    return "apercu:" + nom
def boite(f, t, tex, Lq, uv=None):
    m = {"textures": {"x": tex}, "elements": [{"from": list(f), "to": list(t), "faces": {}}]}
    for k in ("north", "south", "east", "west", "up", "down"):
        if k in ("north", "south"): u = [f[0], 16 - t[1], t[0], 16 - f[1]]
        elif k in ("east", "west"): u = [f[2], 16 - t[1], t[2], 16 - f[1]]
        else: u = [f[0], f[2], t[0], t[2]]
        u = [min(16, max(0, v % 16 if v > 16 else v)) for v in u]
        if u[0] == u[2]: u[2] = u[0] + 0.5
        if u[1] == u[3]: u[3] = u[1] + 0.5
        m["elements"][0]["faces"][k] = {"uv": uv or u, "texture": "#x"}
    Lq += quads(m, VUE)
VUE = lambda p: (16 - p[0], p[1], 16 - p[2])
def scene(o):
    Lq = []; verre = []
    mat, col = geo.MATERIAUX[o["mat"]]
    tex = {"m": mat, "c": col, "o": teinte(T + "block/socle_garniture.png", ORN[o["garn"]], f"g{o['garn']}"),
           "v": teinte(T + f"block/socle_velours_{'losange' if o['losange'] else 'simple'}.png", FONDS[o["vel"]], f"v{o['vel']}{o['losange']}")}
    dy = 16 if o["grand"] else 0
    for f, t, k in geo.haut(geo.ELEMENTS, o["grand"]): boite(f, t, tex[k], Lq)
    # calque de garniture sur le velours
    g = teinte(T + f"block/socle_garni_{'losange' if o['losange'] else 'simple'}.png", ORN[o["garn"]], f"gv{o['garn']}{o['losange']}")
    m = {"textures": {"x": g}, "elements": [{"from": [2, 13.02 + dy, 2], "to": [14, 13.03 + dy, 14], "faces": {"up": {"uv": [2, 2, 14, 14], "texture": "#x"}}}]}
    Lq += quads(m, VUE)
    # plaque gravée sur la colonne
    py = 5.5 + (8 if o["grand"] else 0)
    boite((4.4, py, 3.3), (11.6, py + 3.6, 3.5), tex["o"], Lq)
    boite((4.8, py + 0.4, 3.2), (11.2, py + 3.2, 3.3), "minecraft:block/black_concrete", Lq)
    # trophée
    yt = 13 + dy
    it = "apercu:item_" + o["objet"]; R.TEX[it] = SC + f"mcmeta-assets/assets/minecraft/textures/item/{o['objet']}.png"
    pres = o["pres"]
    if pres == 2:  # chevalet
        boite((5, yt, 9), (6, yt + 9, 10), tex["o"], Lq); boite((10, yt, 9), (11, yt + 9, 10), tex["o"], Lq); boite((5, yt + 2, 9), (11, yt + 3, 10), tex["o"], Lq)
    s = 9 if pres in (1, 2) else 8
    cy = yt + (1 if pres == 1 else 3 if pres == 2 else 5.5 if pres == 0 else 1.5)
    ang = math.radians(35 if pres == 0 else 0)
    def P(u, v):
        x = (u - 0.5) * s; z = 8.5 if pres == 2 else 8
        return VUE((8 + x * math.cos(ang), cy + (1 - v) * s, z - x * math.sin(ang) - (v * 1.2 if pres == 2 else 0)))
    for k in (0, 1):
        pts = [P(0, 0), P(1, 0), P(1, 1), P(0, 1)]
        if k: pts = [pts[1], pts[0], pts[3], pts[2]]
        a = [pts[1][i] - pts[0][i] for i in range(3)]; b = [pts[3][i] - pts[0][i] for i in range(3)]
        n = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
        Lq.append((pts, it, [0, 0, 16, 16] if not k else [16, 0, 0, 16], 0, 1.0, n))
    if pres == 3:  # cloche de verre
        R.TEX["apercu:verre"] = T + "block/socle_verre.png"
        for (r, y0, y1) in ((5.5, 0, 9), (4.8, 9, 11), (3.6, 11, 12.5), (2, 12.5, 13.5)):
            boite((8 - r, yt + y0, 8 - r), (8 + r, yt + y1, 8 + r), "apercu:verre", verre)
        boite((2.3, yt, 2.3), (13.7, yt + 0.7, 13.7), tex["o"], Lq)
        boite((7.2, yt + 13.5, 7.2), (8.8, yt + 15, 8.8), tex["o"], Lq)
    return Lq, verre
def dessiner(im, liste, S, ox, oy, alpha=False):
    calque = Image.new("RGBA", im.size); d = ImageDraw.Draw(calque if alpha else im)
    def prof(q): return sum(p[0] * CAM[0] + p[1] * CAM[1] + p[2] * CAM[2] for p in q[0]) / 4
    for pts, tex, uv, urot, lum, n in sorted(liste, key=prof):
        if n[0] * CAM[0] + n[1] * CAM[1] + n[2] * CAM[2] <= 1e-6: continue
        src = R.img(tex); W, H = src.size; k = W / 16
        cu = max(1, min(16, round(abs(uv[2] - uv[0]) * k))); cv = max(1, min(16, round(abs(uv[3] - uv[1]) * k)))
        for j in range(cv):
            for i in range(cu):
                s0, s1, t0, t1 = i / cu, (i + 1) / cu, j / cv, (j + 1) / cv
                Pp = lambda s, t: [pts[0][m] * (1 - s) * (1 - t) + pts[1][m] * s * (1 - t) + pts[2][m] * s * t + pts[3][m] * (1 - s) * t for m in range(3)]
                ss, tt = (s0 + s1) / 2, (t0 + t1) / 2
                px = min(W - 1, max(0, int((uv[0] + (uv[2] - uv[0]) * ss) * k))); py = min(H - 1, max(0, int((uv[1] + (uv[3] - uv[1]) * tt) * k)))
                col = src.getpixel((px, py))
                if col[3] < 20 and not alpha: continue
                poly = [projeter(Pp(a, b), S, ox, oy) for a, b in ((s0, t0), (s1, t0), (s1, t1), (s0, t1))]
                if alpha:
                    tmp = Image.new("RGBA", im.size); ImageDraw.Draw(tmp).polygon(poly, fill=tuple(int(c * lum) for c in col[:3]) + (col[3],)); calque.alpha_composite(tmp)
                else: d.polygon(poly, fill=tuple(int(c * lum) for c in col[:3]) + (255,))
    if alpha: im.alpha_composite(calque)
if __name__ == "__main__":
    V = [("Marbre, velours rouge", "lévitation, or", dict(mat=0, vel=0, losange=1, garn=0, pres=0, grand=0, objet="nether_star")),
         ("Fonte noire, velours violet", "sous cloche de verre, argent", dict(mat=2, vel=5, losange=1, garn=1, pres=3, grand=0, objet="heart_of_the_sea")),
         ("Cuivre patiné, velours vert", "sur chevalet, cuivre", dict(mat=3, vel=2, losange=0, garn=2, pres=2, grand=0, objet="totem_of_undying")),
         ("Tuf, colonne haute", "posé, velours bleu, or", dict(mat=1, vel=1, losange=1, garn=0, pres=1, grand=1, objet="dragon_breath")),
         ("Bois sombre, velours ocre", "lévitation, noir", dict(mat=4, vel=6, losange=0, garn=3, pres=0, grand=0, objet="echo_shard"))]
    PW, PH = 420, 760; S = 13
    pl = Image.new("RGBA", (PW * len(V), PH + 70), (40, 42, 48, 255))
    f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22); f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    dd = ImageDraw.Draw(pl)
    for i, (a, b, o) in enumerate(V):
        im = Image.new("RGBA", (PW, PH), (40, 42, 48, 255))
        L, verre = scene(o)
        dessiner(im, L, S, PW / 2, PH - 150); dessiner(im, verre, S, PW / 2, PH - 150, alpha=True)
        pl.alpha_composite(im, (i * PW, 0))
        dd.text((i * PW + PW / 2, PH + 4), a, font=f1, fill=(240, 205, 110), anchor="mt"); dd.text((i * PW + PW / 2, PH + 36), b, font=f2, fill=(210, 205, 190), anchor="mt")
    pl.save("/home/claude/apercus/socle_v2.png"); print("ok")
