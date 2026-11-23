# Maquette de l'engrenage séquencé étoffé : écran recomposé comme en jeu (rangées posées par Create, bouton, textes)
from PIL import Image, ImageDraw, ImageFont
import ecrans, apercu_numis as A
S = 3
def scene(sheet, coul_titre):
    out = Image.new('RGBA', ((173 + 20) * S, (161 + 20) * S), (24, 26, 30, 255)); o = 10 * S
    out.alpha_composite(sheet.crop((0, 0, 173 * S, 161 * S)), (o, o))
    for k, v in enumerate((16, 60, 82, 162, 104)):                        # rotation, attente, fin, signal, vide
        out.alpha_composite(sheet.crop((0, v * S, 162 * S, (v + 22) * S)), (o, o + (16 + 22 * k) * S))
    d = ImageDraw.Draw(out); FT = A.FT
    def t(x, y, s, c=(255, 255, 238)):
        d.text((o + x * S + 3, o + y * S - 1), s, font=FT, fill=(60, 60, 50)); d.text((o + x * S, o + y * S - 4), s, font=FT, fill=c)
    for k, (a, b, c) in enumerate((('Turn', '90°', '>'), ('Delay', '20t', ''), ('End', '', ''), ('Await', '', ''), ('', '', ''))):
        y = 16 + 22 * k + 9
        if a: t(33, y, a)
        if b: t(91, y, b)
        if c: t(121, y, c)
    tw = d.textlength('Sequenced Gearshift', font=FT); d.text((o + (165 * S) / 2 - tw / 2, o + 4 * S - 4), 'Sequenced Gearshift', font=FT, fill=coul_titre)
    out.alpha_composite(A.W.crop((0, 0, 54, 54)), (o + 140 * S, o + 137 * S)); out.alpha_composite(A.icone('I_CONFIRM'), (o + 141 * S, o + 138 * S))
    return out
avant = Image.open('/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/create/textures/gui/sequencer.png').convert('RGBA')
apres = ecrans.engrenage_sequence()
a, b = scene(avant, (0xF3, 0xD6, 0x94)), scene(apres, (0xF3, 0xD6, 0x94))
out = Image.new('RGBA', (a.width * 2 + 140, a.height + 60), (30, 32, 38, 255)); d = ImageDraw.Draw(out)
d.text((10, 12), "Engrenage séquencé — version actuelle (1.68.16) puis version étoffée", font=A.F, fill=(240, 220, 160))
out.alpha_composite(a, (110, 50)); out.alpha_composite(b, (130 + a.width, 50))
d.text((10, 50 + a.height // 2), 'ACTUEL', font=A.F, fill=(200, 200, 200))
out.convert('RGB').save('/tmp/nv/seq_cmp.png'); print(out.size)
