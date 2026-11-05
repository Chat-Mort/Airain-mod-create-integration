"""Fond de l'écran du banc d'entretien (176 x 186) : réservoir en verre, cases, conduite de progression, modules."""
from gui import *
ROUAGE = ["................", "......####......", "...#.######.#...", "...##########...", "..####....####..", ".####......####.",
          ".###........###.", ".###........###.", ".###........###.", ".###........###.", ".####......####.", "..####....####..",
          "...##########...", "...#.######.#...", "......####......", "................"]
LINGOT = ["................", "................", "................", "................", "................", "......######....",
          ".....#......#...", "....#......##...", "...########.#...", "...#......#.#...", "...#......##....", "...########.....",
          "................", "................", "................", "................"]
def banc():
    w, h = 176, 186
    g, a = panneau(w, h); px = g.load()
    for (x, y) in ((36, 24), (36, 52), (110, 38), (150, 18), (150, 38), (150, 58)): creux(px, x - 1, y - 1, 18, 18)
    for l in range(3):
        for c in range(9): creux(px, 8 + c * 18 - 1, 104 + l * 18 - 1, 18, 18)
    for c in range(9): creux(px, 8 + c * 18 - 1, 162 - 1, 18, 18)
    creux(px, 10, 19, 16, 62, fond=40)                                  # réservoir d huile
    creux(px, 58, 40, 46, 8, fond=40)                                   # conduite de progression
    im = metalliser(g, a, 7)
    fantome(im, 36, 24, PIOCHE); fantome(im, 36, 52, LINGOT)
    for y in (18, 38, 58): fantome(im, 150, y, ROUAGE)
    for (x, y) in ((11, 20), (23, 20), (11, 78), (23, 78)): rivet(im, x, y)
    pv = im.load()
    for yy in range(24, 80, 10):                                        # graduations du réservoir
        for xx in (12, 13): pv[xx, yy] = LA[1] + (255,)
    tuyau(im, 26, 30, 33, 30); tuyau(im, 26, 58, 33, 58)                  # le réservoir alimente les deux cases
    roue(im, 130.5, 70.5, 8, dents=10, trou=2); roue(im, 139.5, 80.5, 4.5, CU, dents=7, trou=1)
    plaque(im, 5, 4, 120, 12)
    return im
if __name__ == "__main__":
    banc().save(RES + "banc.png"); print("ok")
