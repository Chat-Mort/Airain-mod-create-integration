# Marteau-pilon d'airain (objet 32 x 32, même famille que la pioche impériale) : manche noir à viroles d'or en diagonale,
# tête d'airain massive posée en travers, faces de frappe en acier, cylindre à vapeur et manomètre sur le dessus.
# Dessin au pixel sur deux axes à 45° : a = x + y (le long de la tête), t = x - y (épaisseur, le haut à droite est éclairé).
from PIL import Image
def hx(s, a=255): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (a,)
CONT = hx('100c14')
AIR_OR = [hx('fff0c0'), hx('f0d088'), hx('e1ba6e'), hx('c99b52'), hx('a8763c'), hx('704425')]   # airain : reflet -> ombre
AIR_ROUGE = [hx('d9645c'), hx('c04343'), hx('af1d25'), hx('8b0018'), hx('7e0019'), hx('520019')]  # airain rouge impérial (palette du bloc d'airain rouge impérial)
ACIER = [hx('f0faff'), hx('c8ccdc'), hx('9ea4b8'), hx('6e7488')]
MANCHE = [hx('4a4258'), hx('302936'), hx('1a151e')]
OR = [hx('ffe496'), hx('e4bc60'), hx('a8763c')]

def teinte(pal, t, t0, t1):
    """Ombre selon l'épaisseur : le côté haut-droit (t grand) est éclairé."""
    f = (t - t0) / max(1, t1 - t0)
    return pal[0] if f > 0.82 else pal[1] if f > 0.55 else pal[2] if f > 0.25 else pal[3]

def marteau(rouge=False):
    """rouge : mode 5 × 5, la tête passe à l'airain rouge impérial (les viroles restent en or)."""
    AIR = AIR_ROUGE if rouge else AIR_OR
    im = Image.new('RGBA', (32, 32)); px = im.load()
    for y in range(32):
        for x in range(32):
            a, t = x + y, x - y
            m = None
            if 18 <= a <= 46 and 3 <= t <= 12:                                   # tête, centrée sur le manche (a = 32)                                   # tête
                if a <= 21 or a >= 43:                                           # faces de frappe en acier
                    m = teinte(ACIER, t, 3, 12)
                elif a in (22, 42):                                              # joint acier / airain
                    m = AIR[5]
                elif a in (25, 26, 38, 39):                                      # cerclages
                    m = AIR[3] if t >= 9 else AIR[4] if t >= 6 else AIR[5]
                else:
                    m = teinte(AIR[1:5], t, 3, 12)
            elif 29 <= a <= 35 and 13 <= t <= 15:                                # cylindre à vapeur sur le dessus
                m = AIR[1] if t >= 15 else AIR[3] if a <= 31 else AIR[4]
                if a in (29, 35): m = AIR[4]
            elif 31 <= a <= 33 and 16 <= t <= 18:                                # tige de piston
                m = ACIER[0] if a <= 32 else ACIER[2]
            elif 31 <= a <= 33 and -25 <= t <= 2:                                # manche
                m = MANCHE[0] if a == 31 else MANCHE[1] if a == 32 else MANCHE[2]
                if -1 <= t <= 1 or -25 <= t <= -22: m = OR[0] if a == 31 else OR[1] if a == 32 else OR[2]   # viroles
            if m: px[x, y] = m
    for (x, y) in ((18, 7), (25, 14)):                                             # rivets des cerclages, côté éclairé
        px[x, y] = AIR[0]
    m = [[px[x, y][3] > 0 for x in range(32)] for y in range(32)]                   # contour sombre
    for y in range(32):
        for x in range(32):
            if not m[y][x] and any(0 <= x + i < 32 and 0 <= y + j < 32 and m[y + j][x + i] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = CONT
    return im

if __name__ == '__main__':
    im = marteau(); bg = Image.new('RGBA', (32 * 12, 32 * 12), (139, 139, 139, 255)); bg.alpha_composite(im.resize((32 * 12, 32 * 12), Image.NEAREST)); bg.save('/tmp/nv/marteau.png')
