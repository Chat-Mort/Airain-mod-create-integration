from PIL import Image, ImageDraw
T = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/"
I = "mcmeta-assets/assets/minecraft/textures/item/"
tex = {n: Image.open(T + f"banc_{n}.png").convert("RGBA") for n in ("axe", "face", "dessus", "dessous")}
S = 22                      # pixels écran par pixel de texture
W, H = 1200, 900
def P(x, y, z, ox=600, oy=470):  # repère bloc : x vers l'est, y vers le haut, z vers le sud (vue du sud-est)
    return (ox + (x - z) * S * 0.866, oy + (x + z) * S * 0.5 - y * S)
def ombre(c, k): return tuple(int(v * k) for v in c[:3]) + (c[3],)
def face(d, tex_img, coin, du, dv, k):
    for v in range(16):
        for u in range(16):
            c = tex_img.getpixel((u, v))
            if c[3] < 10: continue
            p0 = [coin[i] + du[i] * u + dv[i] * v for i in range(3)]
            pts = [P(*p0), P(*[p0[i] + du[i] for i in range(3)]), P(*[p0[i] + du[i] + dv[i] for i in range(3)]), P(*[p0[i] + dv[i] for i in range(3)])]
            d.polygon(pts, fill=ombre(c, k))
def boite(d, x0, y0, z0, x1, y1, z1, coul):
    for (pts, k) in ((((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)), 1.0),
                     (((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)), 0.78),
                     (((x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)), 0.6)):
        d.polygon([P(*p) for p in pts], fill=ombre(coul, k), outline=ombre(coul, k * 0.6))
im = Image.new("RGBA", (W, H), (44, 46, 52, 255)); d = ImageDraw.Draw(im)
# arbre de Create derrière (nord) puis au travers et devant (sud)
FE = (150, 150, 158, 255)
boite(d, 6, 6, -14, 10, 10, 0, FE)
# bloc : on dessine la face sud avec son trou, puis l'arbre visible dans le trou, puis la face est et le dessus
face(d, tex["axe"], (0, 16, 16), (1, 0, 0), (0, -1, 0), 0.78)          # sud
boite(d, 6, 6, 14, 10, 10, 30, FE)                                     # arbre qui sort vers le sud
for z in (18, 23, 28): d.line([P(6, 10, z), P(10, 10, z)], fill=(110, 110, 118, 255), width=2)
face(d, tex["face"], (16, 16, 16), (0, 0, -1), (0, -1, 0), 0.6)         # est
face(d, tex["dessus"], (0, 16, 0), (1, 0, 0), (0, 0, 1), 1.0)           # dessus
# objets posés à plat sur le plan de travail
for nom, cx, cz in (("iron_pickaxe", 8, 6.7), ("iron_ingot", 8, 12.5)):
    it = Image.open(I + nom + ".png").convert("RGBA")
    for v in range(16):
        for u in range(16):
            c = it.getpixel((u, v))
            if c[3] < 10: continue
            x = cx - 3.6 + u * 0.45; z = cz - 3.6 + v * 0.45; y = 16.4
            d.polygon([P(x, y, z), P(x + .45, y, z), P(x + .45, y, z + .45), P(x, y, z + .45)], fill=c)
# étincelles
for (x, z) in ((7, 9), (9.5, 8), (8.5, 10.5)):
    px, py = P(x, 18.5, z); d.line([(px - 6, py), (px + 6, py)], fill=(255, 230, 150, 255), width=2); d.line([(px, py - 6), (px, py + 6)], fill=(255, 230, 150, 255), width=2)
im.crop((140, 60, 1100, 860)).save("/home/claude/apercus/banc_3d.png")
