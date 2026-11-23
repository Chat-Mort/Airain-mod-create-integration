# Maquette du lot Numismatics : chaque écran recomposé comme en jeu (boutons de Create, icônes, textes), avant / après, échelle 3
import sys, json
from PIL import Image, ImageDraw, ImageFont
import numis
S = 3
HDC = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/'
W = Image.open(HDC + 'create/textures/gui/widgets.png').convert('RGBA')
IC = Image.open('/tmp/src5/create/src/main/resources/assets/create/textures/gui/icons.png').convert('RGBA')
NI = Image.open(HDC + 'numismatics/textures/gui/icons.png').convert('RGBA')
POS = json.load(open('/home/claude/sauvegarde/outils/icones_create/icons_pos.json'))
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 8 * S - 2)
BLANC, SOMBRE = (255, 255, 255), (0x59, 0x24, 0x24)

def icone(nom):
    if nom.startswith('N:'):
        c, r = {'HOPPER': (0, 2), 'OPEN_SUB_LIST': (1, 2), 'SALE_GO': (2, 2), 'COG': (3, 0), 'SPUR': (0, 0), 'SUN': (5, 0)}[nom[2:]]
        return NI.crop((c * 48, r * 48, c * 48 + 48, r * 48 + 48))
    c, r = POS[nom]; return IC.crop((c * 16, r * 16, c * 16 + 16, r * 16 + 16)).resize((48, 48), Image.NEAREST)

def scene(sheet, w, h, el, marge=10, airain=False):
    out = Image.new('RGBA', ((w + 2 * marge) * S, (h + 2 * marge) * S), (24, 26, 30, 255))
    o = marge * S
    out.alpha_composite(sheet.crop((0, 0, w * S, h * S)), (o, o)); d = ImageDraw.Draw(out)
    def ombre_txt(x, y, t, c, centre=False, droite=False, ombre=True):
        tw = d.textlength(t, font=FT); X = o + x * S - (tw / 2 if centre else tw if droite else 0); Y = o + y * S - 4
        if ombre: d.text((X + 3, Y + 3), t, font=FT, fill=tuple(v // 4 for v in c))
        d.text((X, Y), t, font=FT, fill=c)
    for e in el:
        k = e[0]
        if k == 'btn':
            _, x, y, ic = e; out.alpha_composite(W.crop((0, 0, 54, 54)), (o + x * S, o + y * S)); out.alpha_composite(icone(ic), (o + (x + 1) * S, o + (y + 1) * S))
        elif k == 'ico': _, x, y, ic = e; out.alpha_composite(icone(ic), (o + x * S, o + y * S))
        elif k == 'img': _, x, y, im = e; out.alpha_composite(im, (o + x * S, o + y * S))
        elif k == 'txt':
            _, x, y, t, c = e[:5]
            if airain and y == 3 and c == BLANC: c = (0xF3, 0xD6, 0x94)          # titre passé en airain par le mod
            ombre_txt(x, y, t, c, centre=True, ombre=c != SOMBRE and c != (0x20, 0x20, 0x20))
        elif k == 'txtd': _, x, y, t, c = e; ombre_txt(x, y, t, c, droite=True, ombre=False)
        elif k == 'txtg': _, x, y, t, c = e; ombre_txt(x, y, t, c, ombre=c == BLANC)
    return out

def jauge(sheet, frac):
    c = sheet.crop((53 * S, 137 * S, 183 * S, 155 * S)); return c.crop((0, 0, int(130 * frac) * S, 18 * S))

DEF = {
 'andesite_depositor': (182, 79, lambda s: [('txt', 87, 3, 'Andesite Depositor', BLANC), ('btn', 19, 23, 'I_VIEW_SCHEDULE'), ('btn', 149, 55, 'I_CONFIRM'), ('txtg', 87, 28, 'Cog', BLANC)]),
 'brass_depositor': (208, 145, lambda s: [('txt', 100, 3, 'Brass Depositor', BLANC), ('txt', 100, 21, 'Price: 1 cog, 4 spurs', BLANC), ('btn', 7, 121, 'I_VIEW_SCHEDULE'), ('btn', 175, 121, 'I_CONFIRM')]
     + [('txt', bx + 18, 50 + 22 * k, '0', BLANC) for bx in (49, 135) for k in range(3)] + [('ico', sx, 46 + 22 * k, 'N:SPUR') for sx in (25, 111) for k in range(3)]),
 'bank_terminal': (200, 132, lambda s: [('txt', 96, 3, 'Bank Terminal', BLANC), ('txt', 96, 21, 'Balance: 1,024 spurs', BLANC), ('btn', 139, 108, 'N:OPEN_SUB_LIST'), ('btn', 167, 108, 'I_CONFIRM')]),
 'bank_terminal_sub_account_list': (234, 220, lambda s: [('txt', 113, 3, 'Sub Accounts', BLANC), ('txtg', 13, 201, 'New account', BLANC), ('img', 9, 20, carte(s)), ('txt', 113, 26, 'Workshop', BLANC), ('txtg', 18, 65, 'Spur', (0x44, 0x20, 0x00)), ('btn', 173, 196, 'I_ADD'), ('btn', 201, 196, 'I_CONFIRM')]),
 'bank_terminal_sub_account_list_popup': (250, 133, lambda s: [('txt', 125, 4, 'Sub Account', SOMBRE), ('btn', 223, 92, 'I_CONFIRM'), ('img', 43, 90, s.crop((0, 240 * S, 48, 256 * S))), ('txtg', 70, 94, 'Trusted Players', BLANC)]),
 'trust_list': (200, 110, lambda s: [('txt', 96, 3, 'Trust List', BLANC), ('btn', 167, 86, 'I_CONFIRM')]),
 'blaze_banker': (200, 110, lambda s: [('txt', 96, 4, 'Blaze Banker', SOMBRE), ('btn', 167, 86, 'I_CONFIRM')]),
 'salepoint_config': (238, 145, lambda s: [('txt', 115, 3, 'Salepoint', BLANC), ('txt', 115, 21, 'Price: 2 cogs, 0 spurs', BLANC), ('btn', 16, 121, 'I_VIEW_SCHEDULE'), ('btn', 205, 121, 'I_CONFIRM')]
     + [('txt', bx + 18, 50 + 22 * k, '0', BLANC) for bx in (38, 176) for k in range(3)] + [('ico', sx, 46 + 22 * k, 'N:SPUR') for sx in (14, 152) for k in range(3)]),
 'salepoint': (226, 137, lambda s: [('txt', 109, 3, 'Salepoint', BLANC), ('txt', 109, 21, 'Price: 2 cogs, 0 spurs', BLANC), ('btn', 31, 113, 'N:SALE_GO'), ('btn', 193, 113, 'I_CONFIRM'),
     ('img', 53, 113, jauge(s, 0.6)), ('txt', 118, 119, '3 / 5', BLANC), ('ico', 133, 45, 'N:COG'), ('ico', 133, 63, 'N:SPUR'), ('txtd', 133, 49, '4', (0x20, 0x20, 0x20)), ('txtd', 133, 67, '0', (0x20, 0x20, 0x20)), ('txtg', 107, 86, 'x2', BLANC)]),
 'vendor': (254, 151, lambda s: [('txt', 123, 3, 'Vendor', BLANC), ('txt', 123, 21, 'Price: 1 cog, 0 spurs', BLANC), ('btn', 7, 127, 'I_VIEW_SCHEDULE'), ('btn', 29, 127, 'N:HOPPER'), ('btn', 221, 127, 'I_CONFIRM'), ('txtg', 102, 45, 'Sell', BLANC)]
     + [('txt', bx + 18, 50 + 22 * k, '0', BLANC) for bx in (42, 188) for k in range(3)] + [('ico', sx, 46 + 22 * k, 'N:SPUR') for sx in (18, 164) for k in range(3)]),
}
def carte(sheet):
    # carte de sous-compte telle que le jeu la dessine (couleurs des cartes de l'horaire de Create, déjà en HD)
    hd = Image.open(HDC + 'create/textures/gui/schedule.png').convert('RGBA'); c = lambda x: hd.getpixel((x * S + 1, 233 * S + 1))
    dark, med, light = c(5), c(6), c(7); w, h = 208, 88; im = Image.new('RGBA', (w * S, h * S)); d = ImageDraw.Draw(im)
    R = lambda x, y, ww, hh, col: d.rectangle([x * S, y * S, (x + ww) * S - 1, (y + hh) * S - 1], fill=col)
    R(0, 1, w, h - 2, light); R(1, 0, w - 2, h, light); R(1, 1, w - 2, h - 2, dark); R(2, 2, w - 4, h - 4, med); R(8, 22, w - 16, 1, light); R(9, 23, w - 16, 1, dark)
    for (u, v, x, y) in ((12, 220, 2, 2), (0, 244, w - 14, 2), (0, 232, w - 15, 26)): im.alpha_composite(sheet.crop((u * S, v * S, (u + 12) * S, (v + 12) * S)), (x * S, y * S))
    im.alpha_composite(sheet.crop((12 * S, 242 * S, 52 * S, 256 * S)), (5 * S, 42 * S))
    return im
def paire(nom):
    w, h, el = DEF[nom]
    a = numis.original(nom); a = a.resize((a.width * S, a.height * S), Image.NEAREST); b = numis.ECRANS[nom]()
    return scene(a, w, h, el(a)), scene(b, w, h, el(b), airain=True)
def planche(noms, fichier, titre):
    rangs = [paire(n) for n in noms]
    Wd = 110 + max(a.width + b.width + 40 for a, b in rangs); Hd = 50 + sum(a.height + 20 for a, b in rangs)
    out = Image.new('RGBA', (Wd, Hd), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
    d.text((10, 12), titre, font=F, fill=(240, 220, 160)); y = 50
    for (a, b), n in zip(rangs, noms):
        d.text((10, y + a.height // 2 - 20), 'AVANT', font=F, fill=(200, 200, 200)); d.text((10, y + a.height // 2 + 4), '→ APRÈS', font=F, fill=(200, 200, 200))
        out.alpha_composite(a, (110, y)); out.alpha_composite(b, (110 + a.width + 20, y)); y += a.height + 20
    out.convert('RGB').save(fichier); print(fichier, out.size)
if __name__ == '__main__':
    G = [['andesite_depositor', 'brass_depositor', 'bank_terminal'], ['bank_terminal_sub_account_list', 'bank_terminal_sub_account_list_popup'],
         ['trust_list', 'blaze_banker', 'salepoint_config'], ['salepoint', 'vendor']]
    for i, g in enumerate(G): planche(g, f'/tmp/nv/numis_{i + 1}.png', f'Numismatics ({i + 1}/4)')
