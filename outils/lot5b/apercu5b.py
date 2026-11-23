# Maquette du lot 5b (première partie) : écrans recomposés comme en jeu, titre en airain (le mod recolore les titres sombres)
from PIL import Image, ImageDraw, ImageFont
import ecrans, reglages, sim_reglages
S = 3
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 8 * S - 2)
def morceau(sheet, u, v, w, h): return sheet.crop((u * S, v * S, (u + w) * S, (v + h) * S))
def ecran(sheet, u, v, w, h, titre, extra=(), coul=(0xF3, 0xD6, 0x94), fond=(24, 26, 30, 255)):
    out = Image.new('RGBA', ((w + 20) * S, (h + 20) * S), fond)
    out.alpha_composite(morceau(sheet, u, v, w, h), (10 * S, 10 * S))
    for (uu, vv, ww, hh, x, y) in extra: out.alpha_composite(morceau(sheet, uu, vv, ww, hh), ((10 + x) * S, (10 + y) * S))
    d = ImageDraw.Draw(out); tw = d.textlength(titre, font=FT)
    d.text(((10 + w / 2) * S - tw / 2, (10 + 3) * S), titre, font=FT, fill=coul)
    return out
def paire(nom, fn, u, v, w, h, titre, extra=()):
    a = ecrans.original(nom); a = a.resize((a.width * S, a.height * S), Image.NEAREST); b = fn()
    A = ecran(a, u, v, w, h, titre, extra, coul=(0x59, 0x24, 0x24)); B = ecran(b, u, v, w, h, titre, extra)
    return A, B
if __name__ == '__main__':
    rangs = [
        paire('display_link', ecrans.lien_affichage, 0, 0, 235, 162, 'Display Link'),
        paire('threshold_switch', ecrans.interrupteur_seuil, 0, 0, 182, 103, 'Threshold Switch', extra=((0, 105, 115, 22, 48, 23), (0, 129, 115, 22, 48, 47))),
    ]
    O = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/value_settings.png'
    va = Image.open(O).convert('RGBA'); va = va.resize((va.width * S, va.height * S), Image.NEAREST)
    rangs.append((sim_reglages.scene(va, (24, 26, 30, 255)), sim_reglages.scene(reglages.reglages(), (24, 26, 30, 255))))
    W = 110 + sum(max(a.width, b.width) + 20 for a, b in rangs); H = 60 + 2 * max(max(a.height, b.height) for a, b in rangs) + 30
    out = Image.new('RGBA', (W, H), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
    d.text((10, 10), 'Lot 5b — écrans de Create : lien d\'affichage, interrupteur à seuil, réglage de valeur (taille réelle à l\'échelle 3)', font=F, fill=(240, 220, 160))
    hmax = max(max(a.height, b.height) for a, b in rangs)
    for r, lab in enumerate(('AVANT', 'APRÈS')): d.text((10, 50 + r * (hmax + 30) + hmax // 2), lab, font=F, fill=(220, 220, 220))
    x = 110
    for a, b in rangs:
        out.alpha_composite(a, (x, 50)); out.alpha_composite(b, (x, 50 + hmax + 30)); x += max(a.width, b.width) + 20
    out.convert('RGB').save('/mnt/user-data/outputs/lot5b_mockup.png'); print(out.size)
