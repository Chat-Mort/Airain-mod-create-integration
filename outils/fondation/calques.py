"""Calques de l'étendard (16x32, en niveaux de gris : la couleur est appliquée en jeu).
fond_<forme>, ornement_<forme>, motif_<nom>."""
import math, os, random, sys
from PIL import Image
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
W, H = 16, 32
FORMES = {"aronde": lambda x: 25 + abs(x - 7.5) * 0.85,      # dernière ligne gardée pour la colonne x
          "droit": lambda x: 31,
          "pointe": lambda x: 31.4 - abs(x - 7.5) * 0.85}

def garde(forme, x, y): return y <= FORMES[forme](x)

def fond(forme):
    im = Image.new("RGBA", (W, H)); px = im.load(); rnd = random.Random(4)
    for x in range(W):
        for y in range(H):
            if not garde(forme, x, y): continue
            v = 236 + rnd.randint(-6, 6)
            v -= 18 if x % 5 == 2 else 0                 # plis verticaux
            v += 10 if x % 5 == 4 else 0
            v -= 10 if y % 7 == 6 else 0
            px[x, y] = (v, v, v, 255)
    return im

def ornement(forme):
    im = Image.new("RGBA", (W, H)); px = im.load()
    def p(x, y, v):
        if 0 <= x < W and 0 <= y < H and garde(forme, x, y): px[x, y] = (v, v, v, 255)
    for x in range(W):
        p(x, 0, 150); p(x, 1, 190); p(x, 2, 255)         # fourreau et galon
        p(x, 5, 235) if 2 <= x <= 13 else None
        p(x, 22, 235) if 2 <= x <= 13 else None
        if 4 <= x <= 11: p(x, 23, 190)
    for y in range(H):
        p(0, y, 255); p(15, y, 255); p(1, y, 185); p(14, y, 185)
    for x in range(W):                                  # liseré qui suit la forme du bas
        yb = int(FORMES[forme](x))
        for y in (yb, yb - 1):
            if 0 <= y < H and garde(forme, x, y): px[x, y] = (255 if y == yb else 205,) * 3 + (255,)
    for x in range(0, W, 2):                            # franges
        yb = int(FORMES[forme](x))
        if yb < H - 1 and forme == "droit": pass
    return im

# motifs : 10 x 12, posés en colonnes 3..12 et lignes 8..19 : au moins un pixel libre jusqu'aux ornements
MOTIFS = {
 "rouage": ["..........",
            "....##....",
            ".#.####.#.",
            "..######..",
            ".########.",
            "####..####",
            "####..####",
            ".########.",
            "..######..",
            ".#.####.#.",
            "....##....",
            ".........."],
 "cle": ["..##..##..",
         "..##..##..",
         "..######..",
         "...####...",
         "....##....",
         "....##....",
         "....##....",
         "....##....",
         "...####...",
         "..##..##..",
         "..##..##..",
         "...####..."],
 "flamme": [".#..##..#.",
            ".#..##..#.",
            ".##.##.##.",
            ".########.",
            "##########",
            "####..####",
            "###....###",
            "###.##.###",
            "##..##..##",
            "##.####.##",
            ".##.##.##.",
            "..######.."],
 "couronne": ["..........",
              "#...##...#",
              "##..##..##",
              "##.####.##",
              "##########",
              "##########",
              "#.##..##.#",
              "##########",
              ".########.",
              "..........",
              ".########.",
              ".........."],
 "ancre": ["....##....",
           "...#..#...",
           "....##....",
           ".########.",
           "....##....",
           "....##....",
           "....##....",
           "#...##...#",
           "##..##..##",
           ".##.##.##.",
           "..######..",
           "....##...."],
 "eclair": [".....####.",
            "....####..",
            "...####...",
            "..####....",
            ".########.",
            "..#######.",
            "....####..",
            "...####...",
            "...###....",
            "..###.....",
            "..##......",
            ".#........"],
 "etoile": ["..........",
            "....##....",
            "....##....",
            "...####...",
            "##########",
            "##########",
            ".########.",
            "..######..",
            "..######..",
            ".###..###.",
            ".##....##.",
            ".........."],
 "rouage_brise": ["..........",
            ".....#....",
            ".#.##.#.#.",
            "..##.###..",
            ".####.###.",
            "####..####",
            "####..####",
            ".###.####.",
            "..###.##..",
            ".#.#.##.#.",
            "....#.....",
            ".........."],
 "cristal": ["....MM....",
            "...MLLM...",
            "...MLLM...",
            "..MMLLMM..",
            ".MMMLLMMM.",
            ".DDDMMMLL.",
            "..DDMMLL..",
            "..DDMMLL..",
            "...DMML...",
            "...DMML...",
            "....DL....",
            "....DL...."],
 "fiole": ["...####...",
            "...####...",
            "....##....",
            "....##....",
            "...####...",
            "..##..##..",
            ".##....##.",
            ".#.####.#.",
            ".#.####.#.",
            ".##.##.##.",
            "..######..",
            "...####..."],
}

def motif(nom):
    im = Image.new("RGBA", (W, H)); px = im.load()
    g = MOTIFS[nom]
    for j, l in enumerate(g):
        for i, c in enumerate(l):
            if c == "#":
                bord = any((0 <= j + dj < len(g) and 0 <= i + di < len(l) and g[j + dj][i + di] != "#")
                           for di, dj in ((1, 0), (0, 1)))
                v = 200 if bord else 255
                px[3 + i, 8 + j] = (v, v, v, 255)
            elif c in "LMD":                            # facettes : clair, moyen, sombre
                v = {"L": 255, "M": 200, "D": 140}[c]
                px[3 + i, 8 + j] = (v, v, v, 255)
    return im

if __name__ == "__main__":
    for f in FORMES:
        fond(f).save(f"{OUT}/fond_{f}.png"); ornement(f).save(f"{OUT}/ornement_{f}.png")
    for m in MOTIFS: motif(m).save(f"{OUT}/motif_{m}.png")
    print("ok")
