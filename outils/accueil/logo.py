import sys, os
from PIL import Image
sys.path.insert(0, "../embleme")
from emblemes3 import J_couronne, centrer
G = {  # police 5×7 (I et ' plus étroits), agrandie ×2 : lettres de 10×14 « logo-pixels »
 "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
 "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
 "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
 "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
 "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
 "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
 "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
 "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
 "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
 "'": ["#", "#", ".", ".", ".", ".", "."],
 " ": ["..", "..", "..", "..", "..", "..", ".."],
 "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
 "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
 "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
 "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
 "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
 "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
 "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
 "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
 "·": [".", ".", ".", "#", ".", ".", "."],
 "1": [".#.", "##.", ".#.", ".#.", ".#.", ".#.", "###"], "2": ["###.", "...#", "...#", ".##.", "#...", "#...", "####"],
 ".": [".", ".", ".", ".", ".", ".", "#"],
}
def texte(t, k=2, esp=1):
    """Masque d'un texte : liste de lignes de 0/1, chaque pixel de police agrandi k fois."""
    cols = []
    for i, ch in enumerate(t):
        g = G[ch]
        for c in range(len(g[0])):
            col = [g[r][c] == "#" for r in range(7)]
            cols += [col] * k
        if i < len(t) - 1: cols += [[False] * 7] * (esp * k)
    return [[cols[x][y // k] for x in range(len(cols))] for y in range(7 * k)]
# palette
LAITON = [(255, 238, 168), (247, 214, 112), (231, 184, 74), (206, 150, 52), (176, 116, 38), (146, 90, 30)]   # du haut vers le bas
RELIEF = [(108, 62, 22), (86, 48, 18), (66, 36, 14)]
CONTOUR = (30, 18, 10)
CUIVRE = [(240, 160, 110), (214, 120, 70), (176, 88, 48), (130, 62, 34)]
def peindre(img, masque, ox, oy, couleurs, prof=3):
    h, w = len(masque), len(masque[0])
    px = img.load()
    plein = lambda x, y: 0 <= y < h and 0 <= x < w and masque[y][x]
    # relief (extrusion vers le bas-droite) puis contour, puis face
    for d in range(prof, 0, -1):
        for y in range(h):
            for x in range(w):
                if masque[y][x]: px[ox + x + (d + 1) // 2, oy + y + d] = RELIEF[min(d - 1, 2)]
    for y in range(-1, h + prof + 1):
        for x in range(-1, w + prof):
            if px[ox + x, oy + y][3] == 0 and any(plein(x + a, y + b) or (0 < y + b - 1 and plein(x + a - 1, y + b - prof))
                                                  for a in (-1, 0, 1) for b in (-1, 0, 1)):
                pass
    for y in range(h):
        for x in range(w):
            if masque[y][x]:
                c = couleurs[min(len(couleurs) - 1, y * len(couleurs) // h)]
                if not plein(x, y - 1) or not plein(x - 1, y): c = tuple(min(255, v + 28) for v in c)   # arête éclairée
                px[ox + x, oy + y] = c + (255,)
    # contour sombre autour de tout ce qui est peint
    occ = {(x, y) for x in range(img.width) for y in range(img.height) if px[x, y][3]}
    for (x, y) in list(occ):
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, y + b)
            if q not in occ and 0 <= q[0] < img.width and 0 <= q[1] < img.height:
                px[q] = CONTOUR + (255,); occ.add(q)
def roue_couronnee():
    m = centrer(J_couronne())
    lignes = [y for y in range(40) if any(m[y])]
    colonnes = [x for x in range(20) if any(m[y][x] for y in range(40))]
    return [[m[y][x] for x in range(colonnes[0], colonnes[-1] + 1)] for y in range(lignes[0], lignes[-1] + 1)]
HAUT, BAS = "THE AIRAIN", "EMPIRE"
def logo(W=256, Hh=44):
    img = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    haut = texte(HAUT, k=2)
    bas = texte(BAS, k=3)
    r = roue_couronnee()
    gap = 7
    total = len(r[0]) + gap + len(bas[0]) + gap + len(r[0])
    ox = (W - total) // 2
    yb = Hh - len(bas) - 5                      # la grande ligne, en bas
    yh = yb - len(haut) - 3                     # la petite, au-dessus
    yr = yb + (len(bas) - len(r)) // 2 - 1
    peindre(img, haut, (W - len(haut[0])) // 2, yh, CUIVRE, prof=2)
    peindre(img, bas, ox + len(r[0]) + gap, yb, LAITON, prof=3)
    peindre(img, r, ox, yr, LAITON, prof=2)
    peindre(img, r, ox + len(r[0]) + gap + len(bas[0]) + gap, yr, LAITON, prof=2)
    return img
if __name__ == "__main__":
    L = logo(256, 44)
    print("logo", L.getbbox())
    L.resize((1024, 176), Image.NEAREST).save("logo_titre_1024.png")
    L.resize((1024, 176), Image.NEAREST).resize((512, 88), Image.NEAREST)
    big = Image.new("RGB", (1100, 260), (40, 36, 34)); big.paste(L.resize((1024, 176), Image.NEAREST), (38, 40), L.resize((1024, 176), Image.NEAREST)); big.save("apercu_logo.png")
