# Carton de motif (objet 32 x 32) : carton vieilli, coins d'airain ; vierge (quadrillage pointillé) ou enregistré (motif imprimé)
import sys
sys.path.insert(0, '/home/claude/travail/lot8')
from marteau import hx, CONT, AIR_OR
from PIL import Image
PAP = [hx('fbf0d4'), hx('efdfb6'), hx('dcc596'), hx('b89c6a')]
ENC = [hx('3a2a1c'), hx('7a5a3a')]
def carton(motif=None):
    im = Image.new('RGBA', (32, 32)); px = im.load()
    x0, y0, x1, y1 = 4, 6, 27, 25                                   # carte légèrement en biais : on la dessine droite
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px[x, y] = PAP[1] if (x * 3 + y * 5) % 13 else PAP[2]
            if y == y0 or x == x0: px[x, y] = PAP[0]
            if y == y1 or x == x1: px[x, y] = PAP[3]
    gx, gy, c = 8, 8, 4                                             # grille 4 x 4 de cases de 4 texels
    for j in range(4):
        for i in range(4):
            for v in range(c):
                for u in range(c):
                    X, Y = gx + i * c + u, gy + j * c + v
                    if motif:
                        col = motif[(i + j) % len(motif)]
                        px[X, Y] = col if (u, v) != (0, 0) else tuple(int(k * 0.8) for k in col[:3]) + (255,)
                    elif (u == 0 or v == 0) and (X + Y) % 2 == 0:
                        px[X, Y] = PAP[3]
    if not motif:
        for X in range(gx, gx + 17, 2): px[X, gy + 16] = PAP[3]
        for Y in range(gy, gy + 17, 2): px[gx + 16, Y] = PAP[3]
    else:
        for k in range(17): px[gx + k, gy - 1] = ENC[0]; px[gx - 1, gy + k] = ENC[0]
    for (cx, cy) in ((x0, y0), (x1 - 2, y0), (x0, y1 - 2), (x1 - 2, y1 - 2)):     # coins d'airain
        for v in range(3):
            for u in range(3):
                if (cx == x0 and u == 2 and v == 2) or (cx != x0 and u == 0 and v == 2) and cy == y0: pass
                px[cx + u, cy + v] = AIR_OR[1] if u + v < 2 else AIR_OR[3] if u + v < 4 else AIR_OR[5]
    m = [[px[x, y][3] > 0 for x in range(32)] for y in range(32)]
    for y in range(32):
        for x in range(32):
            if not m[y][x] and any(0 <= x + i < 32 and 0 <= y + j < 32 and m[y + j][x + i] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = CONT
    return im
if __name__ == '__main__':
    W = Image.new('RGBA', (32 * 20, 32 * 10), (139, 139, 139, 255))
    W.alpha_composite(carton().resize((288, 288), Image.NEAREST), (10, 16))
    W.alpha_composite(carton([hx('e8e4dc'), hx('2c2a30')]).resize((288, 288), Image.NEAREST), (330, 16))
    W.save('/tmp/nv/carton.png')
