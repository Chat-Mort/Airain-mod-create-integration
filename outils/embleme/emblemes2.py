import math
from PIL import Image, ImageDraw, ImageFont
W, H = 20, 40
def vide(): return [[0] * W for _ in range(H)]
def miroir(m):                                   # copie la moitié gauche (x 0-9) sur la droite : symétrie parfaite
    for y in range(H):
        for x in range(10): m[y][19 - x] = m[y][x]
    return m
def dessin(m, y0, lignes, x0=0, val=1):          # lignes = moitié gauche (10 colonnes), '#' = plein, '.' = vide, 'o' = efface
    for j, l in enumerate(lignes):
        for i, c in enumerate(l):
            if c == "#": m[y0 + j][x0 + i] = val
            elif c == "o": m[y0 + j][x0 + i] = 0
    return m
def roue(m, cy, rc=5.7, rd=8.0, trou=0.0, garde=lambda dx, dy: True, plein=True):
    """Roue dentée « dessinée » : disque, 4 dents droites (4 px de large) et 4 dents en diagonale ; symétrie parfaite."""
    for y in range(H):
        for x in range(10):
            dx, dy = x + .5 - 10, y + .5 - cy
            d = math.hypot(dx, dy); ax, ay = abs(dx), abs(dy)
            dent = (ax < 2 and d < rd) or (ay < 2 and d < rd) or (abs(ax - ay) < 1.45 and d < rd - 0.6)
            if (d <= rc or dent) and d > trou and garde(dx, dy):
                m[y][x] = 1
    return miroir(m)
def troue(m, y0, lignes):        # perce le motif (moitié gauche) : '#' = trou
    for j, l in enumerate(lignes):
        for i, c in enumerate(l):
            if c == "#": m[y0 + j][i] = 0
    return miroir(m)
# ---------------------------------------------------------------- l'Empire
def A_coeur():                    # roue pleine, percée d'un cœur
    m = roue(vide(), 14)
    return troue(m, 11, [".......##.", "......####", "......####", ".......###", "........##", ".........#"])
def B_couronne():                 # demi-roue en couronne sur un piston
    m = roue(vide(), 13, garde=lambda dx, dy: dy < 0)
    m = troue(m, 9, ["........##", "........##", ".......###", "......####"])
    for y in range(13, 30): dessin(m, y, ["........##"])
    dessin(m, 13, ["...#######"]); dessin(m, 20, [".......###"]); dessin(m, 30, ["....######", "....######"])
    return miroir(m)
def C_oeil():                     # roue pleine, percée d'un œil et de sa pupille
    m = roue(vide(), 14)
    m = troue(m, 12, [".......###", "......##..", "......#...", "......##..", ".......###"])
    return m
def D_brise():                    # roue fendue de haut en bas, les deux moitiés écartées d'un pixel
    m = roue(vide(), 14, trou=2.6)
    for y in range(H): m[y] = m[y][1:10] + [0] + m[y][10:]
    for y in range(H):
        if y % 3 == 1: m[y][8] = 0                         # bord de cassure dentelé
    return miroir(m)
def E_eclat():                    # cristal d'améthyste planté au cœur d'une roue ouverte
    m = roue(vide(), 18, trou=4.7, garde=lambda dx, dy: not (dy < 0 and abs(dx) < 3.2))
    return miroir(dessin(m, 4, [".........#", "........##", "........##", ".......###", ".......###", ".......###",
                                ".......###", ".......###", ".......###", ".......###", ".......###", ".......###",
                                ".......###", ".......###", "........##", ".........#"]))
def F_flamme():                   # flamme qui s'échappe d'une moitié de roue
    m = roue(vide(), 21, trou=3.6, garde=lambda dx, dy: dy > 0)
    return miroir(dessin(m, 8, [".........#", "........##", "........##", ".......###", "......####", "......####",
                                ".....#####", ".....#####", ".....####o", "......##oo", ".......#oo"]))
def bordure():
    m = vide()
    for y in range(H):
        for x in range(W):
            if x in (0, W - 1) or y in (0, H - 1): m[y][x] = 1
    return m
def franges():
    m = vide()
    for y in range(35, 40):
        for x in range(W):
            if (x % 4 in (1, 2)) or y >= 38: m[y][x] = 1
    return m
# ---------------------------------------------------------------- rendu
def banniere(couches, nom, sous, S=9):
    im = Image.new("RGBA", (W * S + 120, H * S + 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox, oy = 60, 50
    d.rectangle([ox - 30, oy - 26, ox + W * S + 30, oy - 14], fill=(92, 64, 40))
    d.rectangle([ox + W * S // 2 - 6, oy - 14, ox + W * S // 2 + 6, oy + H * S + 40], fill=(110, 78, 48))
    for y in range(H):
        for x in range(W):
            c = couches[0][1]
            for (m, col) in couches[1:]:
                if m[y][x]: c = col
            d.rectangle([ox + x * S, oy + y * S, ox + x * S + S - 1, oy + y * S + S - 1], fill=c)
    # petite taille réelle dans le coin, comme vue en jeu
    for y in range(H):
        for x in range(W):
            c = couches[0][1]
            for (m, col) in couches[1:]:
                if m[y][x]: c = col
            d.rectangle([4 + x * 2, oy + H * S - 80 + y * 2, 5 + x * 2, oy + H * S - 79 + y * 2], fill=c)
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    F2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    tw = d.textlength(nom, font=F); d.text((im.width / 2 - tw / 2, oy + H * S + 48), nom, font=F, fill=(240, 232, 215))
    tw = d.textlength(sous, font=F2); d.text((im.width / 2 - tw / 2, oy + H * S + 72), sous, font=F2, fill=(180, 170, 155))
    return im
NOIR, CUIVRE, LAITON, VERT = (29, 29, 33), (200, 110, 62), (224, 180, 66), (68, 132, 116)
ROUGE, VIOLET, BLANC, BRUN = (153, 42, 38), (140, 64, 196), (234, 230, 222), (104, 70, 44)
EMBLEMES = {"A": A_coeur, "B": B_couronne, "C": C_oeil, "D": D_brise, "E": E_eclat, "F": F_flamme}
if __name__ == "__main__":
    emp = [banniere([(None, NOIR), (A_coeur(), CUIVRE), (bordure(), LAITON), (franges(), LAITON)], "A · Le Cœur d'Airain", "cuivre sur noir"),
           banniere([(None, VERT), (B_couronne(), LAITON), (bordure(), NOIR)], "B · La Couronne de fer", "laiton sur vert-de-gris"),
           banniere([(None, NOIR), (C_oeil(), LAITON), (bordure(), CUIVRE), (franges(), CUIVRE)], "C · L'Œil de la machine", "laiton sur noir")]
    ref = [banniere([(None, ROUGE), (D_brise(), BLANC)], "D · L'engrenage brisé", "blanc sur rouge"),
           banniere([(None, BRUN), (E_eclat(), VIOLET), (franges(), VIOLET)], "E · L'éclat d'Écho", "violet sur toile brune"),
           banniere([(None, ROUGE), (F_flamme(), BLANC)], "F · La flamme", "blanc sur rouge")]
    pl = Image.new("RGB", (3 * emp[0].width + 40, 2 * emp[0].height + 150), (24, 24, 28)); d = ImageDraw.Draw(pl)
    FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    d.text((24, 16), "L'Empire d'Airain", font=FT, fill=(222, 177, 64))
    for i, b in enumerate(emp): pl.paste(b, (20 + i * b.width, 50), b)
    y2 = 50 + emp[0].height + 30
    d.text((24, y2), "Les Réfractaires", font=FT, fill=(190, 140, 230))
    for i, b in enumerate(ref): pl.paste(b, (20 + i * b.width, y2 + 34), b)
    pl.save("propositions_emblemes_v2.png")
    for k, f in EMBLEMES.items():                                   # contrôle de symétrie
        m = f(); assert all(m[y][x] == m[y][19 - x] for y in range(H) for x in range(W)), k
    print("symétrie parfaite pour les six")
