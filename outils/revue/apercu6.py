from PIL import Image, ImageDraw, ImageFont
from mobs3d import cube, dessiner, bipede
O = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs/v2/out6/"
A = "/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"
SH = [cube(-8, 0, -8, 16, 8, 16, 0, 28), cube(-8, 4, -8, 16, 12, 16, 0, 0)]
SHO = [cube(-8, 0, -8, 16, 8, 16, 0, 28), cube(-8, 12, -8, 16, 12, 16, 0, 0), cube(-3, 6, -3, 6, 6, 6, 0, 52)]
WI = [cube(-4, 20, -4, 8, 8, 8, 0, 0), cube(-15, 17, -3, 6, 6, 6, 32, 0), cube(9, 17, -3, 6, 6, 6, 32, 0), cube(-10, 15, -1.5, 20, 3, 3, 0, 16),
      cube(-1.5, 4, -1.5, 3, 10, 3, 0, 22), cube(-5.5, 11.5, -1, 11, 2, 2, 24, 22), cube(-5.5, 9, -1, 11, 2, 2, 24, 22), cube(-5.5, 6.5, -1, 11, 2, 2, 24, 22),
      cube(-1.5, -2, -1.5, 3, 6, 3, 12, 22)]
L = [[("A · d'origine, corrigé", A + "shulker/shulker.png", SH, 6), ("B · carapace du Néant", O + "shulker_B.png", SH, 6), ("C · coffre de cuivre", O + "shulker_C.png", SH, 6),
      ("A · ouvert", A + "shulker/shulker.png", SHO, 6), ("B · ouvert", O + "shulker_B.png", SHO, 6), ("C · ouvert", O + "shulker_C.png", SHO, 6)],
     [("actuel", A + "wither/wither.png", WI, 7), ("A · fonte sombre, sans laiton", O + "wither_A.png", WI, 7), ("B · os et laiton", O + "wither_B.png", WI, 7),
      ("C · feu des âmes", O + "wither_C.png", WI, 7), ("C · invulnérable", O + "wither_C_inv.png", WI, 7)],
     [("actuel", A + "skeleton/wither_skeleton.png", bipede(2, 2), 7), ("A · os calcinés", O + "wsq_A.png", bipede(2, 2), 7),
      ("B · acier noirci, âmes", O + "wsq_B.png", bipede(2, 2), 7), ("C · bronze calciné", O + "wsq_C.png", bipede(2, 2), 7)]]
W, H = 300, 330
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15); g = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
titres = ["Shulker", "Wither", "Squelette de fonte (wither squelette)"]
pl = Image.new("RGBA", (W * 6, (H + 70) * 3), (40, 42, 48, 255)); dd = ImageDraw.Draw(pl)
for r, ligne in enumerate(L):
    y = r * (H + 70); dd.text((10, y + 6), titres[r], font=g, fill=(255, 220, 140))
    for i, (nom, p, geo, S) in enumerate(ligne):
        im = Image.new("RGBA", (W, H), (40, 42, 48, 255))
        dessiner(im, Image.open(p).convert("RGBA"), geo, S, W / 2, H - 50)
        pl.alpha_composite(im, (i * W, y + 34)); dd.text((i * W + W / 2, y + H + 38), nom, font=f, fill=(240, 205, 110), anchor="mt")
pl.save("/home/claude/apercus/revue_variantes.png"); print("ok")
