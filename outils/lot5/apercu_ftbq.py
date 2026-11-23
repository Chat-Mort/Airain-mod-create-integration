# Maquette du lot 5a : les quêtes telles que FTB Quests les dessine (forme grise, fond à 60 %, anneau teinté selon l'état)
import os, sys, glob
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/claude/travail/lot5'); import ftbq
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
HDP = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/'
A = '/tmp/l5/apres/'
ITEMS = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'

def charge(base, k):
    for b in base:
        if os.path.exists(b + k): return Image.open(b + k).convert('RGBA')
AVANT = [HDP + 'ftbquests/textures/', ftbq.SRC]; APRES = [A, HDP + 'ftbquests/textures/', ftbq.SRC]

def teinte(im, c, a=255):
    r, g, b, al = im.split()
    r = r.point(lambda v: v * c[0] // 255); g = g.point(lambda v: v * c[1] // 255); b = b.point(lambda v: v * c[2] // 255)
    al = al.point(lambda v: v * a // 255); return Image.merge('RGBA', (r, g, b, al))

ETATS = [('terminée', (0xF3, 0xD6, 0x94), 0xE8, False), ('commencée', (0xE1, 0xBA, 0x6E), 0xE8, False),
         ('à faire', (0xB4, 0x82, 0x42), 0xC8, False), ('verrouillée', (0x6A, 0x6E, 0x78), 0xFF, True)]

def quete(src, nom, etat, icone, taille=96):
    lab, c, a, lock = etat
    sh = charge(src, f'shapes/{nom}/shape.png'); bg = charge(src, f'shapes/{nom}/background.png'); ol = charge(src, f'shapes/{nom}/outline.png')
    im = Image.new('RGBA', (128, 128))
    im.alpha_composite(teinte(sh, (85, 85, 85))); im.alpha_composite(teinte(bg, (255, 255, 255), 150)); im.alpha_composite(teinte(ol, c, a))
    im = im.resize((taille, taille), Image.NEAREST)          # le jeu réduit la texture sans lissage
    s = int(taille * 2 / 3); ic = icone.resize((s, s), Image.NEAREST); im.alpha_composite(ic, ((taille - s) // 2, (taille - s) // 2))
    if lock: im.alpha_composite(teinte(sh, (0, 0, 0), 100).resize((taille, taille), Image.NEAREST))
    return im

def scene(src, titre):
    fond = Image.open(HDP + 'airain/textures/ftbq/ardoise.png').convert('RGBA')
    W, H = 110 + 5 * 4 * 112, 150
    out = Image.new('RGBA', (W, H))
    for y in range(0, H, 96):
        for x in range(0, W, 96): out.alpha_composite(fond, (x, y))
    d = ImageDraw.Draw(out); d.text((10, 60), titre, font=F, fill=(243, 214, 148))
    icones = [Image.open(p).convert('RGBA') for p in sorted(glob.glob(ITEMS + '*.png'))[3:200:9]]
    x = 110; k = 0
    for nom in ('circle', 'square', 'rsquare', 'hexagon', 'gear'):
        for e in ETATS:
            out.alpha_composite(quete(src, nom, e, icones[k % len(icones)]), (x, 18)); k += 1
            if nom == 'circle': d.text((x + 10, 122), e[0], font=f, fill=(220, 220, 220))
            x += 112
    return out

def icones_planche():
    noms = ftbq.TRAITS + ftbq.TEXTURES
    S = 2; cw = 48 * S + 14
    out = Image.new('RGBA', (110 + len(noms) // 2 * cw + cw, 2 * 2 * (48 * S + 34) + 20), (42, 46, 55, 255)); d = ImageDraw.Draw(out)
    for half in range(2):
        part = noms[half * 12:(half + 1) * 12]
        for r, lab in enumerate(('AVANT', 'APRÈS')):
            y = 10 + (half * 2 + r) * (48 * S + 34)
            d.text((10, y + 48), lab, font=F, fill=(220, 220, 220))
            for i, n in enumerate(part):
                im = Image.open(f'{ftbq.SRC}gui/{n}.png').convert('RGBA')
                im = im.resize((48 * S, 48 * S), Image.NEAREST) if r == 0 else Image.open(f'{A}gui/{n}.png').resize((48 * S, 48 * S), Image.NEAREST)
                out.alpha_composite(im, (110 + i * cw, y + 16))
                if r == 0: d.text((110 + i * cw, y), n[:14], font=f, fill=(170, 170, 180))
    return out

if __name__ == '__main__':
    os.system(f'python3 /home/claude/travail/lot5/ftbq.py {A} > /dev/null')
    a = scene(AVANT, 'AVANT'); b = scene(APRES, 'APRÈS'); c = icones_planche()
    W = max(a.width, c.width)
    out = Image.new('RGBA', (W, 40 + a.height + b.height + 40 + c.height), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
    d.text((10, 10), 'Lot 5a — formes des quêtes en jeu (rond = forme par défaut du pack), quatre états', font=F, fill=(240, 220, 160))
    out.alpha_composite(a, (0, 40)); out.alpha_composite(b, (0, 40 + a.height))
    d.text((10, 50 + a.height + b.height), 'Icônes du livre de quêtes (x2 de la taille HD)', font=F, fill=(240, 220, 160))
    out.alpha_composite(c, (0, 80 + a.height + b.height))
    out.convert('RGB').save('/mnt/user-data/outputs/lot5a_mockup.png'); print(out.size)
