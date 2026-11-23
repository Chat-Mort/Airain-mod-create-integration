# Maquette du lot : recettes de Create dans EMI, table de décoration de Sophisticated Storage (avant / après, échelle 3)
from PIL import Image, ImageDraw, ImageFont
import jei_create, deco_table
from kit import *
import apercu_numis as A
F, FT = A.F, A.FT
ORIG = Image.open(jei_create.O).convert('RGBA').resize((768, 768), Image.NEAREST)
NEUF = jei_create.widgets()

def panneau(w, h):
    """Fond d'une recette EMI du pack (ardoise, filet d'or) — dessiné ici pour la maquette."""
    im = Image.new('RGBA', (w * S, h * S), hx('363a44')); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w * S - 1, h * S - 1], outline=OR['trait']); d.rectangle([1, 1, w * S - 2, h * S - 2], outline=OR['clair'])
    d.rectangle([2, 2, w * S - 3, h * S - 3], outline=OR['base']); d.rectangle([3, 3, w * S - 4, h * S - 4], outline=OR['base'])
    return im

def recette(sheet, nom):
    def m(u, v, w, h): return sheet.crop((u * S, v * S, (u + w) * S, (v + h) * S))
    P = {'press': (177, 70), 'mix': (177, 103), 'mill': (177, 53), 'seq': (180, 30)}
    w, h = P[nom]; im = panneau(w + 6, h + 6); o = 3
    def pose(c, x, y): im.alpha_composite(c, ((x + o) * S, (y + o) * S))
    slot = m(0, 0, 18, 18); d = ImageDraw.Draw(im)
    def texte(x, y, t, c=(150, 155, 165)): d.text(((x + o) * S, (y + o) * S - 4), t, font=FT, fill=c)
    if nom == 'press':
        pose(m(0, 56, 52, 11), 61, 41); pose(m(19, 0, 71, 10), 52, 54); pose(slot, 26, 50); pose(slot, 130, 49)
        texte(66, 8, 'press (3D)')
    if nom == 'mix':
        for i in range(3): pose(slot, 16 + i * 19, 50)
        pose(slot, 141, 50); pose(m(0, 21, 18, 14), 136, 32); pose(m(0, 42, 52, 11), 81, 88); pose(m(0, 201, 169, 19), 4, 80)
        d.text(((9 + o) * S, (86 + o) * S - 4), 'Heated', font=FT, fill=(0xE8, 0x83, 0x00)); pose(m(0, 156, 18, 18), 152, 80)
        texte(70, 30, 'mixer (3D)')
    if nom == 'mill':
        pose(slot, 14, 8); pose(m(19, 10, 42, 10), 85, 32); pose(m(0, 21, 18, 14), 43, 4); pose(slot, 138, 26); texte(48, 30, 'millstone')
    if nom == 'seq':
        pose(m(19, 0, 71, 10), 52, 10); pose(slot, 20, 6); pose(m(20, 156, 18, 18), 150, 6); pose(m(0, 178, 12, 16), 104, 0)
    return im

def colonne(sheet):
    rs = [recette(sheet, n) for n in ('press', 'mix', 'mill', 'seq')]
    W = max(r.width for r in rs); H = sum(r.height + 24 for r in rs); out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y = 0
    for r in rs: out.alpha_composite(r, (0, y)); y += r.height + 24
    return out

if __name__ == '__main__':
    a, b = colonne(ORIG), colonne(NEUF)
    out = Image.new('RGBA', (110 + a.width * 2 + 60, a.height + 80), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
    d.text((10, 12), 'Recettes de Create dans EMI : avant / après (fond de recette EMI du pack, échelle 3)', font=F, fill=(240, 220, 160))
    out.alpha_composite(a, (110, 60)); out.alpha_composite(b, (150 + a.width, 60))
    d.text((110, 40), 'AVANT', font=F, fill=(200, 200, 200)); d.text((150 + a.width, 40), 'APRÈS', font=F, fill=(200, 200, 200))
    out.convert('RGB').save('/mnt/user-data/outputs/create_recipes_emi_mockup.png'); print(out.size)
    # table de décoration
    o = Image.open(deco_table.O + 'decoration_table.png').convert('RGBA'); o = o.resize((768, 768), Image.NEAREST); n = deco_table.table_decoration()
    el = Image.open(deco_table.O + 'decoration_table_elements.png').convert('RGBA')
    def scene(sheet, coul):
        s = Image.new('RGBA', (270 * S, 245 * S), (24, 26, 30, 255)); s.alpha_composite(sheet.crop((0, 0, 250 * S, 226 * S)), (10 * S, 10 * S)); d = ImageDraw.Draw(s)
        def ic(u, v, x, y, w=16, h=16): s.alpha_composite(el.crop((u, v, u + w, v + h)).resize((w * S, h * S), Image.NEAREST), ((10 + x) * S, (10 + y) * S))
        for (u, v, x, y) in ((0, 16, 26, 17), (0, 0, 26, 47), (0, 32, 26, 77), (0, 48, 26, 107), (16, 16, 74, 47), (16, 32, 74, 77), (16, 48, 74, 107), (48, 48, 137, 47), (32, 48, 137, 77)): ic(u, v, x, y)
        for (y, c) in ((46, (200, 60, 60)), (76, (60, 90, 200))):
            d.rectangle([(10 + 117) * S, (10 + y) * S, (10 + 135) * S - 1, (10 + y + 18) * S - 1], fill=(20, 20, 20)); d.rectangle([(10 + 118) * S, (10 + y + 1) * S, (10 + 134) * S - 1, (10 + y + 17) * S - 1], fill=c)
        d.text(((10 + 8) * S, (10 + 6) * S - 4), 'Decoration Table', font=FT, fill=coul)
        d.text(((10 + 45) * S, (10 + 127) * S - 4), 'Inventory', font=FT, fill=coul)
        return s
    A_, B_ = scene(o, (0x40, 0x40, 0x40)), scene(n, (0xF3, 0xD6, 0x94))
    out = Image.new('RGBA', (A_.width * 2 + 40, A_.height + 50), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
    d.text((10, 12), 'Table de décoration (Sophisticated Storage) : avant / après — icônes des pièces et boutons de couleur posés par le jeu', font=F, fill=(240, 220, 160))
    out.alpha_composite(A_, (0, 45)); out.alpha_composite(B_, (A_.width + 40, 45))
    out.convert('RGB').save('/mnt/user-data/outputs/decoration_table_mockup.png'); print(out.size)
