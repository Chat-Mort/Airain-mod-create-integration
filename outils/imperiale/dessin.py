from PIL import Image, ImageDraw, ImageFont
import random, math
SAC='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/plaque_netherite_sacree.png'
PN='/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/plaque_netherite.png'
forme = Image.open(PN).convert('RGBA')
def dans(x, y): return forme.getpixel((x, y))[3] > 0
def bord(x, y): return dans(x, y) and any(not (0 <= x+dx < 16 and 0 <= y+dy < 16) or not dans(x+dx, y+dy) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)))

def imperiale():
    im = Image.new('RGBA', (16, 16), (0,0,0,0)); px = im.load()
    for x in range(16):
        for y in range(16):
            if not dans(x, y): continue
            if bord(x, y): px[x,y] = (40,34,44,255) if x < 5 or x > 10 else ((110,110,128,255) if y < 8 else (88,88,104,255)); continue
            if x in (3, 12):                                   # bandes de netherite à gauche et à droite
                px[x,y] = (40,34,44,255) if x == 3 else (58,50,62,255)
                if y in (4, 11): px[x,y] = (226,186,96,255)    # rivets d'or
                continue
            t = x + y                                          # reflets en diagonale, ombre en bas à droite
            if t in (9, 10): base = (255,255,255)
            elif t in (8, 11): base = (244,246,252)
            elif t == 17: base = (250,252,255)
            elif t >= 19: base = (196,200,216)
            elif t <= 6: base = (236,238,246)
            else: base = (224,227,238)
            if (x * 7 + y * 3) % 23 == 0: base = (236,226,246)   # irisation
            elif (x * 5 + y * 11) % 29 == 0: base = (222,240,250)
            n = random.Random(x * 31 + y).randint(-3, 3)
            px[x,y] = tuple(min(255, max(0, c + n)) for c in base) + (255,)
    # sceau central : l'étoile sertie dans un filet d'or
    for (x, y) in ((7,5),(8,5),(6,6),(9,6),(6,9),(9,9),(7,10),(8,10),(5,7),(5,8),(10,7),(10,8)):
        px[x,y] = (226,186,96,255)
    for (x, y, c) in ((7,6,(210,236,255)),(8,6,(255,255,255)),(6,7,(190,226,255)),(7,7,(255,255,255)),(8,7,(240,250,255)),(9,7,(200,230,255)),
                      (6,8,(200,230,255)),(7,8,(240,250,255)),(8,8,(255,255,255)),(9,8,(190,226,255)),(7,9,(255,255,255)),(8,9,(210,236,255))):
        px[x,y] = c + (255,)
    return im

def inachevee():
    im = Image.open(SAC).convert('RGBA'); px = im.load(); fin = imperiale().load()
    r = random.Random(4)
    for x in range(16):
        for y in range(16):
            if dans(x, y) and not bord(x, y) and (x < 6 or r.random() < 0.35) and x not in (3, 12): px[x,y] = fin[x,y]
    return im

def bloc():
    im = Image.new('RGBA', (16, 16)); px = im.load(); r = random.Random(9)
    for x in range(16):
        for y in range(16):
            v = 222 + r.randint(-10, 10)
            px[x,y] = (v - 6, v + 2, min(255, v + 18), 255)
            if x in (0, 15) or y in (0, 15): px[x,y] = (226,186,96,255) if (x + y) % 3 else (176,138,58,255)
    for (cx, cy) in ((4,4),(11,5),(5,11),(11,11),(8,8)):
        for (dx, dy, c) in ((0,0,(255,255,255)),(1,0,(250,250,220)),(-1,0,(250,250,220)),(0,1,(230,245,255)),(0,-1,(230,245,255))):
            px[cx+dx, cy+dy] = c + (255,)
    return im

if __name__ == '__main__':
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; f = ImageFont.truetype(FB, 16)
    Z = 10
    items = [("Plaque sacrée", Image.open(SAC).convert('RGBA')), ("En cours (×5)", inachevee()), ("Bloc d'étoile", bloc()), ("Plaque impériale", imperiale())]
    W = len(items) * (16 * Z + 60) + 40
    out = Image.new('RGB', (W, 16 * Z + 80), (32,33,38)); d = ImageDraw.Draw(out); x = 30
    for i, (n, im) in enumerate(items):
        g = im.resize((16 * Z, 16 * Z), Image.NEAREST); out.paste(g, (x, 20), g)
        d.text((x + 80 - d.textlength(n, font=f) / 2, 16 * Z + 35), n, fill=(240,205,120), font=f)
        if i < 3: d.text((x + 16 * Z + 14, 16 * Z // 2 + 10), "→" if i != 1 else "+", fill=(200,200,200), font=ImageFont.truetype(FB, 26))
        x += 16 * Z + 60
    out.save('apercu_imperiale.png'); print(out.size)
