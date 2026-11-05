from emblemes2 import *
def centrer(m, cy=19.5):
    """Recale le motif pour que le milieu de sa hauteur tombe sur la ligne cy (milieu de la bannière, franges comprises)."""
    lignes = [y for y in range(H) if any(m[y])]
    h0, h1 = lignes[0], lignes[-1]
    dec = round(cy - (h0 + h1 + 1) / 2)
    n = vide()
    for y in range(H):
        if 0 <= y + dec < H: n[y + dec] = m[y][:]
    return n
def depuis(lignes):
    m = vide(); dessin(m, 0, lignes); return miroir(m)
def G_aigle():           # l'aigle à deux têtes, une roue dentée sur la poitrine
    m = depuis([".....#....", "....###...", "....##.#..", ".....##...", "#.....##..", "##...#####", "###.######",
                "##########", ".####.####", "..####.#o#", "...###.o##", "....##.#o#", ".....##.##", "......####",
                ".......###", "......####", ".....##.##", "....##...."])
    return m
def H_cle():             # la clé de remontage : celle qui relance le Cœur
    return depuis(["....###...", "...#####..", "...##.###.", "...#...###", "...##.####", "....######", ".....####.",
                   "........##", "........##", "........##", ".......###", "........##", "........##", "........##",
                   "........##", ".......###", ".......#.#", ".......###", ".......#.#", ".......###"])
def I_horloge():         # la tour d'horloge des cités, cadran en roue dentée
    return depuis([".........#", ".........#", "........##", "........##", ".......###", "......####", ".......###",
                   ".......###", "......####", "......##.#", "......#.##", "......##.#", "......####", ".......###",
                   ".......###", ".......#.#", ".......#.#", ".......###", "......####", ".....#####"])
def J_couronne():        # la roue couronnée
    m = roue(vide(), 25, trou=2.4)
    dessin(m, 10, ["....#....#", "....##..##", "....######", "....######"])
    return miroir(m)
def K_cles():            # deux clés à molette croisées derrière la roue
    m = vide(); cx, cy = 10, 15
    for t in [i / 40 for i in range(41)]:              # deux demi-diagonales dans la moitié gauche : avec le miroir, un X
        for (x0, y0) in ((2.0, 5.0), (2.0, 25.0)):
            x, y = x0 + (cx - x0) * t, y0 + (cy - y0) * t
            for dx in (0, 0.9):
                xi, yi = int(x + dx), int(y)
                if xi < 10: m[yi][xi] = 1
    dessin(m, 3, ["#..#......", "##.#......", ".###......"])          # mâchoire ouverte en haut
    dessin(m, 25, [".###......", "##.#......", "#..#......"])         # et en bas
    miroir(m)
    for y in range(H):
        for x in range(W):
            if math.hypot(x + .5 - cx, y + .5 - cy) < 6.6: m[y][x] = 0
    r = roue(vide(), cy, rc=4.2, rd=5.9, trou=1.8)
    for y in range(H):
        for x in range(W): m[y][x] = m[y][x] or r[y][x]
    return m
NOUVEAUX = {"H": H_cle, "I": I_horloge, "J": J_couronne, "K": K_cles}
if __name__ == "__main__":
    emp = [banniere([(None, NOIR), (centrer(K_cles()), LAITON), (bordure(), CUIVRE)], "K · Les Clés croisées", "laiton sur noir"),
           banniere([(None, NOIR), (centrer(H_cle()), CUIVRE), (bordure(), LAITON)], "H · La Clé de remontage", "cuivre sur noir"),
           banniere([(None, VERT), (centrer(I_horloge()), LAITON)], "I · La Tour d'horloge", "laiton sur vert-de-gris"),
           banniere([(None, NOIR), (centrer(J_couronne()), LAITON), (bordure(), CUIVRE)], "J · La Roue couronnée", "laiton sur noir")]
    ref = [banniere([(None, NOIR), (centrer(E_eclat()), VIOLET), (franges(), VIOLET)], "E · L'éclat d'Écho", "violet sur noir")]
    pl = Image.new("RGB", (4 * emp[0].width + 40, 2 * emp[0].height + 150), (24, 24, 28)); d = ImageDraw.Draw(pl)
    FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    d.text((24, 16), "L'Empire d'Airain : nouvelles pistes", font=FT, fill=(222, 177, 64))
    for i, b in enumerate(emp): pl.paste(b, (20 + i * b.width, 50), b)
    y2 = 50 + emp[0].height + 30
    d.text((24, y2), "Les Réfractaires : E, fond noir, recentré", font=FT, fill=(190, 140, 230))
    pl.paste(ref[0], (20, y2 + 34), ref[0])
    pl.save("propositions_emblemes_v3.png")
    for k, f in list(NOUVEAUX.items()) + [("E", E_eclat)]:
        m = centrer(f()); assert all(m[y][x] == m[y][19 - x] for y in range(H) for x in range(W)), k
        l = [y for y in range(H) if any(m[y])]; print(k, "lignes", l[0], "à", l[-1])
