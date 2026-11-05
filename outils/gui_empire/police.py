"""Texte façon Minecraft (police ascii.png du jeu) pour les maquettes."""
from PIL import Image
import unicodedata
SC = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/"
A = Image.open(SC + "mcmeta-assets/assets/minecraft/textures/font/ascii.png").convert("RGBA")
def glyphe(ch):
    ch = unicodedata.normalize("NFD", ch)[0]
    o = ord(ch) if ord(ch) < 256 else ord("?")
    g = A.crop(((o % 16) * 8, (o // 16) * 8, (o % 16) * 8 + 8, (o // 16) * 8 + 8))
    cols = [x for x in range(8) if any(g.getpixel((x, y))[3] for y in range(8))]
    w = (max(cols) + 1) if cols else 3
    return g, w
def largeur(t): return sum(glyphe(c)[1] + 1 for c in t)
def texte(im, x, y, t, coul, ombre=False, centre=False):
    if centre: x -= largeur(t) // 2
    for passe in ((1, True), (0, False)) if ombre else ((0, False),):
        d, sombre = passe; cx = x
        for c in t:
            g, w = glyphe(c)
            c2 = tuple(v // 4 for v in coul) if sombre else coul
            m = Image.new("RGBA", g.size, c2 + (255,)); m.putalpha(g.split()[3])
            im.alpha_composite(m, (cx + d, y + d)); cx += w + 1
