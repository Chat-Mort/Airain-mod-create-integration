import sys; sys.path.insert(0, '../balise7'); sys.path.insert(0, '.')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
from geo import *
R = 4
PEAU, CHEV, OEIL = (196, 150, 118), (70, 48, 30), (60, 70, 140)
def vox(B, dos=False):
    V = {}
    def tete():
        for X in range(-4 * R, 4 * R):
            for Y in range(-8 * R, 0):
                for Z in range(-4 * R, 4 * R):
                    if X in (-4*R, 4*R-1) or Y in (-8*R, -1) or Z in (-4*R, 4*R-1):
                        c = PEAU
                        if Y < -6 * R or (Z > -4 * R and Y < -5 * R) or Z > 2 * R: c = CHEV
                        if Z == -4 * R and -4 * R <= Y < -3 * R and (-3 * R <= X < -1 * R or 1 * R <= X < 3 * R): c = OEIL if (X // R) in (-2, 2) else (240, 240, 240)
                        V[(X, Y, Z)] = c
    tete()
    for (x, y, z, w, h, d, c) in B:
        for X in range(round(x * R), round((x + w) * R)):
            for Y in range(round(y * R), round((y + h) * R)):
                for Z in range(round(z * R), round((z + d) * R)):
                    V[(X, Y, Z)] = c
    if dos: return {(x, -y, z): c for (x, y, z), c in V.items()}
    return {(-x, -y, -z): c for (x, y, z), c in V.items()}
ims = [(rendu(vox(diademe_casque()), T=2), "Casque au diadème"), (rendu(vox(tiare()), T=2), "Tiare runique"),
       (rendu(vox(nimbe() + halo()), T=2), "Nimbe de la Haute-Prêtresse"), (rendu(vox(nimbe() + halo(), True), T=2), "(dos)")]
W = sum(i.width for i, _ in ims) + 50; H = max(i.height for i, _ in ims) + 50
out = Image.new('RGB', (W, H), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
x = 10
for i, t in ims:
    out.paste(i, (x, H - i.height - 10)); d.text((x + 5, 8), t, fill=(230, 220, 200), font=f); x += i.width + 10
out.save('apercu_tetes.png'); print(out.size)
