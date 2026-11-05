import sys
sys.path.insert(0, "../gui_empire")
from police import texte, largeur
from PIL import Image
T = Image.open("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/gui/registre.png").convert("RGBA")
EL = Image.open("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/gui/elements.png").convert("RGBA")
ENCRE, SEPIA, ROUGE, VERT = (58, 26, 10), (110, 80, 52), (138, 26, 20), (46, 90, 30)
def ecran(planche):
    im = Image.new("RGBA", (340, 220), (24, 22, 26, 255)); bx, by = 20, 12
    im.alpha_composite(T.crop((0, 0, 300, 196)), (bx, by))
    im.alpha_composite(EL.crop((0, 16, 16, 32)), (bx + 20, by + 156)); im.alpha_composite(EL.crop((16, 16, 32, 32)), (bx + 264, by + 156))
    def centre(x, y, t, c): texte(im, x + 59 - largeur(t) // 2, y, t, c)
    def filet(x, y):
        for i in range(x + 10, x + 108): im.putpixel((i, y), (154, 112, 70, 255))
        im.alpha_composite(T.crop((352, 0, 357, 5)), (x + 57, y - 2))
    def base(x, y, nom, devise, pos, dist, couleur):
        for i in range(-11, 11): im.putpixel((x + 59 + i, y - 1), (90, 58, 26, 255))
        for j in range(36):
            for i in range(18):
                c = couleur if not (6 <= i <= 11 and 12 <= j <= 20) else (220, 175, 60)
                if j > 32 and abs(i - 9) < (j - 32) * 2: continue
                im.putpixel((x + 50 + i, y + j), c + (255,))
        centre(x, y + 40, nom, ENCRE); centre(x, y + 50, "« " + devise + " »", SEPIA)
        filet(x, y + 63); yy = y + 69
        texte(im, x, yy, "Position", SEPIA); t = pos; texte(im, x + 118 - largeur(t), yy, t, ENCRE); yy += 11
        texte(im, x, yy, "Monde", SEPIA); texte(im, x + 118 - largeur("Surface"), yy, "Surface", ENCRE); yy += 11
        texte(im, x, yy, "Distance", SEPIA); t = dist; texte(im, x + 102 - largeur(t), yy, t, ENCRE)
        im.alpha_composite(T.crop((304, 0, 317, 13)).rotate(-35, resample=Image.NEAREST), (x + 106, yy - 3)); yy += 14
        return yy
    if planche == 0:
        x, y = bx + 20, by + 28
        centre(x, y, "Registre des fondations", ROUGE); centre(x, y + 22, "de l'Empire d'Airain", SEPIA)
        im.alpha_composite(T.crop((320, 0, 348, 28)), (x + 45, y + 46)); filet(x, y + 86)
        centre(x, y + 96, "Fondations : 3", ENCRE); centre(x, y + 108, "Trophées : 2", ENCRE)
        centre(x, y + 124, "Les étendards décoratifs", SEPIA); centre(x, y + 134, "n'y figurent pas.", SEPIA)
        yy = base(bx + 162, by + 22, "La Forge du Nord", "Le feu ne dort jamais", "120  64  -340", "412 blocs", (150, 30, 28))
        texte(im, bx + 162, yy, "Trophées exposés", SEPIA)
        for k, c in enumerate(((200, 200, 120), (90, 60, 120))):
            for j in range(12):
                for i in range(12): im.putpixel((bx + 164 + k * 19 + i, yy + 12 + j), c + (255,))
    texte(im, bx + 79 - 2, by + 162, "1", SEPIA); texte(im, bx + 221 - 2, by + 162, "2", SEPIA)
    return im
a = ecran(0).resize((1020, 660), Image.NEAREST); a.save("/home/claude/apercus/registre_maquette.png")
