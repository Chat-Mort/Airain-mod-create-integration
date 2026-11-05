import math
from PIL import Image, ImageDraw, ImageFont
W, H = 20, 40
def vide(): return [[0]*W for _ in range(H)]
def engrenage(m, cx, cy, rc, rd, dents, trou, phase=0.0, casse=None):
    for y in range(H):
        for x in range(W):
            dx, dy = x + .5 - cx, y + .5 - cy; d = math.hypot(dx, dy); a = math.atan2(dy, dx)
            dent = math.cos(dents * (a + phase)) > 0.25
            if (d <= rc or (d <= rd and dent)) and d > trou:
                if casse and casse(x, y): continue
                m[y][x] = 1
    return m
def coeur(m, cx, cy):
    motif = ["011011", "111111", "111111", "011110", "001100"]
    for j, l in enumerate(motif):
        for i, c in enumerate(l):
            if c == "1": m[cy + j][cx + i] = 1
def oeil(m, cx, cy):
    motif = ["00111100", "01100110", "11011011", "01100110", "00111100"]
    for j, l in enumerate(motif):
        for i, c in enumerate(l):
            if c == "1": m[cy + j][cx + i] = 1
def pix(m, pts):
    for (x, y) in pts:
        if 0 <= x < W and 0 <= y < H: m[y][x] = 1
def bordure(): 
    m = vide()
    for y in range(H):
        for x in range(W):
            if x in (0, W-1) or y in (0, H-1): m[y][x] = 1
    return m
def bas_dents():   # franges en dents de scie en bas
    m = vide()
    for y in range(34, 40):
        for x in range(W):
            if (39 - y) <= (2 - abs((x % 4) - 1.5)) * 2: m[y][x] = 1
    return m
# ---------------------------------------------------------------- emblèmes de l'Empire
def E_coeur():          # le Cœur d'Airain : engrenage, cœur au centre
    m = engrenage(vide(), 10, 15, 6.6, 8.6, 8, 5.4, phase=math.pi / 8)
    coeur(m, 7, 13); return m
def E_couronne():       # la couronne d'engrenage : demi-roue dentée au-dessus d'un piston
    m = engrenage(vide(), 10, 13, 6.0, 8.2, 10, 3.2, casse=lambda x, y: y > 13)
    for y in range(14, 30):
        for x in range(8, 12): m[y][x] = 1
    for x in range(5, 15): m[30][x] = m[31][x] = 1
    for x in range(6, 14): m[16][x] = 1
    return m
def E_oeil():           # l'œil de la machine : engrenage et œil
    m = engrenage(vide(), 10, 15, 6.2, 8.4, 8, 5.0)
    oeil(m, 6, 13); return m
# ---------------------------------------------------------------- emblèmes réfractaires
def R_brise():          # l'engrenage brisé : roue fendue en deux
    m = engrenage(vide(), 10, 15, 6.2, 8.4, 8, 3.0, casse=lambda x, y: abs((x - 10) - (y - 15) * 0.45) < 1.2)
    return m
def R_eclat():          # l'éclat d'Écho : cristal d'améthyste dans une roue ouverte
    m = engrenage(vide(), 10, 15, 6.4, 8.4, 8, 5.2, casse=lambda x, y: y < 11 and abs(x - 10) < 4)
    pts = [(10, 6), (9, 7), (10, 7), (11, 7)] + [(x, y) for y in range(8, 19) for x in range(10 - (2 if y < 16 else 18 - y), 11 + (2 if y < 16 else 18 - y))]
    pix(m, pts); return m
def R_main():           # la flamme : une flamme qui sort d'un engrenage brisé
    m = engrenage(vide(), 10, 21, 6.0, 8.0, 8, 3.5, casse=lambda x, y: y < 19)
    flamme = ["0001000", "0011000", "0011100", "0111100", "0111110", "1111110", "1110111", "1100011", "0100010"]
    for j, l in enumerate(flamme):
        for i, c in enumerate(l):
            if c == "1": m[8 + j][7 + i] = 1
    return m
# ---------------------------------------------------------------- rendu en bannière
def banniere(couches, nom, sous):
    S = 9
    im = Image.new("RGBA", (W * S + 120, H * S + 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = 60, 50
    d.rectangle([ox - 30, oy - 26, ox + W * S + 30, oy - 14], fill=(92, 64, 40))        # traverse
    d.rectangle([ox + W * S // 2 - 6, oy - 14, ox + W * S // 2 + 6, oy + H * S + 40], fill=(110, 78, 48))   # mât
    for y in range(H):
        for x in range(W):
            c = couches[0][1]
            for (m, col) in couches[1:]:
                if m[y][x]: c = col
            k = 1 - 0.10 * (x / W) - 0.06 * (y % 5 == 0)
            c = tuple(int(v * k) for v in c)
            d.rectangle([ox + x * S, oy + y * S, ox + x * S + S - 1, oy + y * S + S - 1], fill=c)
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    F2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    tw = d.textlength(nom, font=F); d.text((im.width / 2 - tw / 2, oy + H * S + 48), nom, font=F, fill=(240, 232, 215))
    tw = d.textlength(sous, font=F2); d.text((im.width / 2 - tw / 2, oy + H * S + 72), sous, font=F2, fill=(180, 170, 155))
    return im
NOIR, CUIVRE, LAITON, VERT = (30, 28, 32), (205, 112, 60), (222, 177, 64), (73, 140, 120)
ROUGE, VIOLET, BLANC, BRUN = (150, 40, 36), (137, 60, 190), (232, 228, 220), (100, 66, 42)
emp = [banniere([(None, NOIR), (E_coeur(), CUIVRE), (bordure(), LAITON), (bas_dents(), LAITON)], "A · Le Cœur d'Airain", "cuivre sur noir"),
       banniere([(None, VERT), (E_couronne(), LAITON), (bordure(), NOIR)], "B · La Couronne de fer", "laiton sur vert-de-gris"),
       banniere([(None, NOIR), (E_oeil(), LAITON), (bordure(), CUIVRE), (bas_dents(), CUIVRE)], "C · L'Œil de la machine", "laiton sur noir")]
ref = [banniere([(None, ROUGE), (R_brise(), BLANC)], "D · L'engrenage brisé", "blanc sur rouge"),
       banniere([(None, BRUN), (R_eclat(), VIOLET), (bas_dents(), VIOLET)], "E · L'éclat d'Écho", "violet sur toile brune"),
       banniere([(None, ROUGE), (R_main(), BLANC)], "F · La flamme", "blanc sur rouge")]
pl = Image.new("RGB", (3 * emp[0].width + 40, 2 * emp[0].height + 150), (24, 24, 28)); d = ImageDraw.Draw(pl)
FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
d.text((24, 16), "L'Empire d'Airain", font=FT, fill=(222, 177, 64))
for i, b in enumerate(emp): pl.paste(b, (20 + i * b.width, 50), b)
y2 = 50 + emp[0].height + 30
d.text((24, y2), "Les Réfractaires", font=FT, fill=(190, 140, 230))
for i, b in enumerate(ref): pl.paste(b, (20 + i * b.width, y2 + 34), b)
pl.save("propositions_emblemes.png"); print(pl.size)
