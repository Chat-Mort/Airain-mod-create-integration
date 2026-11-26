# Table du carreleur : textures du bloc (16 x 16) — dessus en damier de marbre serti d'airain, flancs d'ardoise à tiroirs
import sys; sys.path.insert(0, '/home/claude/travail/lot12')
from px import hx, neuf
from PIL import Image
B = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
A = dict(h=hx('fff0c4'), c=hx('f3d694'), b=hx('e1ba6e'), m=hx('c99b52'), s=hx('a8763c'), d=hx('704425'))
ARD = [hx('3f4350'), hx('363a44'), hx('2f333c'), hx('2a2e37'), hx('1b1e24')]
BL = [hx('f2efe8'), hx('e2ded4'), hx('cfc9bc')]; NO = [hx('3a3840'), hx('2c2a30'), hx('1f1d22')]
def dessus():
    """Plateau : damier de marbre de 4 x 4 carreaux de 3 texels, serti d'un cadre d'airain de 2 texels."""
    im = neuf(); px = im.load()
    for y in range(16):
        for x in range(16):
            e = min(x, y, 15 - x, 15 - y)
            if e == 0: px[x, y] = A['c'] if (x == 0 or y == 0) and not (x == 15 or y == 15) else A['d']; continue
            if e == 1: px[x, y] = A['m'] if (x == 1 or y == 1) and not (x == 14 or y == 14) else A['s']; continue
            i, j = (x - 2) // 3, (y - 2) // 3; u, v = (x - 2) % 3, (y - 2) % 3
            p = BL if (i + j) % 2 == 0 else NO
            px[x, y] = p[0] if u + v == 0 else p[2] if u + v == 4 else p[1]
    return im
def flanc(face=False):
    im = neuf(); px = im.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = ARD[1] if (x + y * 3) % 7 else ARD[2]
    for x in range(16): px[x, 0] = A['c']; px[x, 1] = A['m']; px[x, 2] = A['d']           # bord de plateau en airain
    for y in range(3, 16): px[0, y] = A['m']; px[15, y] = A['d']                           # montants
    if face:
        for (y0, y1) in ((4, 8), (10, 14)):                                                # deux tiroirs à cartons
            for y in range(y0, y1 + 1):
                for x in range(2, 14):
                    px[x, y] = ARD[0] if y == y0 or x == 2 else ARD[4] if y == y1 or x == 13 else ARD[3]
            px[7, y0 + 2] = A['c']; px[8, y0 + 2] = A['s']                                 # poignées
            for x in (4, 5, 10, 11): px[x, y0 + 1] = hx('efdfb6')                          # bords de cartons qui dépassent
    else:
        for y in range(5, 13):
            for x in range(3, 13):
                if x in (3, 12) or y in (5, 12): px[x, y] = ARD[3]
    return im
def dessous():
    im = neuf(); px = im.load()
    for y in range(16):
        for x in range(16): px[x, y] = A['m'] if (x + y) % 5 else A['s']
    return im
if __name__ == '__main__':
    dessus().save(B + 'tilers_table_top.png'); flanc().save(B + 'tilers_table_side.png'); flanc(True).save(B + 'tilers_table_front.png'); dessous().save(B + 'tilers_table_bottom.png')
    W = Image.new('RGBA', (4 * 140, 140), (139, 139, 139, 255))
    for i, f in enumerate((dessus(), flanc(True), flanc(), dessous())): W.alpha_composite(f.resize((128, 128), Image.NEAREST), (i * 140 + 6, 6))
    W.save('/tmp/nv/table_tex.png')
