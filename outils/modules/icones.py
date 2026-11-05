import math
from PIL import Image, ImageDraw, ImageFont
P = dict(k=(40,26,12), b=(150,108,40), B=(205,160,70), L=(240,205,120), a=(255,196,90), A=(255,236,170), e=(255,110,40),
         c=(196,116,78), C=(140,74,46), s=(104,106,116), S=(76,78,86), f=(48,50,56), g=(120,180,200), G=(220,245,255),
         t=(140,230,255), w=(235,235,230), r=(200,50,40), m=(110,72,40), M=(80,50,28))
# niveau 2 : laiton -> netherite noirci, reflets d'or (comme le casque couronné)
P2 = dict(P, k=(16,12,18), b=(46,40,50), B=(76,66,80), L=(255,214,110), c=(92,80,96), C=(58,50,62), s=(104,92,110), S=(58,50,62), m=(60,40,30), M=(40,28,22))

def grille(rows):
    assert len(rows) == 16 and all(len(r) == 16 for r in rows), [len(r) for r in rows]
    return rows

LANTERNE = grille([
"................",
"......kkkk......",
".....kLLLLk.....",
"....kbBBBBbk....",
"..kkkkkkkkkkkk..",
"..kLLLLLLLkLLk..",
"..kBBBBBBBkaak..",
"..kBeeBeeBkAak..",
"..kBeeBeeBkaak..",
"..kBBBBBBBkLLk..",
"..kBBBkBBBkaak..",
"..kBBkkkBBkaAk..",
"..kBBBBBBBkAak..",
"..kbbbbbbbkLLk..",
"..kkkkkkkkkkkk..",
"................"])
LUNETTE = grille([
"................",
"......kkkk......",
"....kkLLLLkk....",
"...kLBBBBBBbk...",
"..kLBkkkkkkBbk..",
"..kLkgGGggfkBkk.",
".kLBkGGgggfkBkLk",
".kLBkGgggffkBkBk",
".kBBkggggffkbkLk",
".kBBkgggfffkbkk.",
"..kBbkffffkbbk..",
"..kmbbkkkkbbk...",
".kmMkbbbbbbkk...",
"kmMk.kkkkkk.....",
"kMk.............",
".k.............."])
CANON = grille([
"................",
"................",
"..........kkk...",
".........kLBbk..",
"........kLkfbk..",
".......kcLffbk..",
"......kcCkLBk...",
".....kcCcckk....",
"....kcCcCk......",
"...kccCcCk......",
"..kLkcCck.......",
".kLBbkck........",
".kBbbkkSk.......",
"..kkkSSSSk......",
"...kSsLsSSk.....",
"...kkkkkkkk....."])
TESLA = grille([
".t.............t",
"..t...kkkk...tt.",
".t..kkLLLLkk..t.",
"...kLBBBBBBbk...",
"...kbbbBBbbbk...",
"....kkkLLkkk....",
".....kccccck....",
".....kCCCCCk....",
".....kccccck....",
".....kCCCCCk....",
".....kccccck....",
".....kCCCCCk....",
"....kkccccckk...",
"...kkSSSSSSSkk..",
"..kSsLssssLsSk..",
"..kkkkkkkkkkkk.."])
BLINDAGE = grille([
"................",
".kkkk......kkkk.",
"kLBBbk....kbBBLk",
"kBBBbbkkkkbbBBBk",
"kbbkLkLLLLkLkbbk",
".kkkSLSSSSLSkkk.",
"...kLsssssssLk..",
"...kSSSSSSSSSk..",
"...kLsssssssLk..",
"...kSSSSSSSSSk..",
"...kLsssssssLk..",
"...kSSSSSSSSSk..",
"....kLsssssLk...",
".....kSSSSSk....",
"......kLLLk.....",
".......kkk......"])
CHAUDIERE = grille([
"..........w.....",
"........ww.w....",
"..........kk....",
"..........ff....",
"....kkkkkkffk...",
"...kLLLLLLffLk..",
"...kcccccccccCk.",
"...kLLLLLLLLLbk.",
"...kccckkkccCCk.",
"...kcckwrwkcCCkk",
"...kcckrkrkcCCkL",
"...kccckkkccCCkk",
"...kLLLLLLLLLbk.",
"...kcccccccccCk.",
"...kbbbbbbbbbbk.",
"....kkkkkkkkkk.."])

def dessine(rows, pal, etoile=False):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.': im.putpixel((x, y), pal[ch] + (255,))
    if etoile:   # éclat d'étoile du Nether, en haut à gauche
        for (x, y, c) in ((1, 1, (255, 255, 255)), (0, 1, (190, 240, 255)), (2, 1, (190, 240, 255)), (1, 0, (255, 240, 180)), (1, 2, (255, 240, 180))):
            im.putpixel((x, y), c + (255,))
    return im

def plaque_sacree():
    im = Image.open('/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/plaque_netherite.png').convert('RGBA')
    # serti d'or et étoile du Nether au centre
    for (x, y) in ((6,5),(7,5),(8,5),(9,5),(5,6),(10,6),(5,7),(10,7),(5,8),(10,8),(5,9),(10,9),(6,10),(7,10),(8,10),(9,10)):
        im.putpixel((x, y), (210, 170, 90, 255))
    for x in range(6, 10):
        for y in range(6, 10): im.putpixel((x, y), (22, 18, 24, 255))
    star = {(7,6):(220,235,255),(8,6):(200,225,250),(6,7):(200,225,250),(7,7):(255,255,255),(8,7):(255,255,240),(9,7):(170,210,240),
            (6,8):(170,210,240),(7,8):(255,250,220),(8,8):(255,255,255),(9,8):(200,225,250),(7,9):(200,225,250),(8,9):(170,210,240),
            (7,4):(255,240,200),(8,11):(255,240,200),(4,8):(255,240,200),(11,7):(255,240,200)}
    for p, c in star.items(): im.putpixel(p, c + (255,))
    return im

ICONES = [("Tête-lanterne", LANTERNE), ("Longue-vue", LUNETTE), ("Canon d'épaule", CANON),
          ("Bobine Tesla", TESLA), ("Blindage riveté", BLINDAGE), ("Chaudière de secours", CHAUDIERE)]
if __name__ == '__main__':
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; font = ImageFont.truetype(FB, 15); fs = ImageFont.truetype(FB, 17)
    Z = 8; cw = 16 * Z + 40
    out = Image.new('RGB', (cw * 6 + 20, 2 * (16 * Z + 50) + 220), (32, 33, 38)); d = ImageDraw.Draw(out)
    for n, (nom, g) in enumerate(ICONES):
        for t, (pal, et) in enumerate(((P, False), (P2, True))):
            im = dessine(g, pal, et).resize((16 * Z, 16 * Z), Image.NEAREST)
            X, Y = 20 + n * cw, 40 + t * (16 * Z + 50)
            out.paste(im, (X, Y), im)
            if t == 0: d.text((X + 64 - d.textlength(nom, font=font) / 2, Y + 16 * Z + 6), nom, fill=(240, 205, 120), font=font)
    d.text((20, 10), "Niveau 1", fill=(240, 205, 120), font=fs)
    d.text((20, 40 + 16 * Z + 26), "Niveau 2 (table de forgeron)", fill=(240, 205, 120), font=fs)
    pl = plaque_sacree().resize((16 * Z, 16 * Z), Image.NEAREST); Y = 2 * (16 * Z + 50) + 50
    pn = Image.open('/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/plaque_netherite.png').convert('RGBA').resize((16 * Z, 16 * Z), Image.NEAREST)
    out.paste(pn, (20, Y), pn); out.paste(pl, (20 + cw, Y), pl)
    d.text((20, Y - 30), "Plaque de netherite  →  Plaque de netherite sacrée", fill=(240, 205, 120), font=fs)
    out.save('apercu_icones.png'); print(out.size)
