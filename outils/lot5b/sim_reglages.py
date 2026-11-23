# Simulation du réglage de valeur tel que Create le compose (morceaux étirés, rognés, répétés), pour juger le rendu
import sys
from PIL import Image, ImageDraw, ImageFont
S = 3
FT = ImageFont.truetype('/home/claude/sauvegarde/outils/polices/' + 'minecraft.ttf', 8 * S) if False else None
def piece(sheet, u, v, w, h): return sheet.crop((u * S, v * S, (u + w) * S, (v + h) * S))
def blit(dst, im, x, y): dst.alpha_composite(im, (x * S, y * S))
def etire(dst, sheet, u, v, w, h, x, y, W, H): blit(dst, piece(sheet, u, v, w, h).resize((W * S, H * S), Image.NEAREST), x, y)
def rogne(dst, sheet, u, v, x, y, W, H): blit(dst, piece(sheet, u, v, W, H), x, y)
def scene(sheet, fond=(96, 120, 80, 255)):
    W, H = 260, 90; out = Image.new('RGBA', (W * S, H * S), fond)
    x, y, w, h = 20, 18, 220, 58
    etire(out, sheet, 80, 9, 1, 1, x + 1, y + 1, w - 2, h - 2)                     # fond extérieur
    lab_w = 50; bar_x = x + 8 + lab_w + 6; bar_w = 140
    etire(out, sheet, 75, 9, 1, 1, bar_x - 1, y + 8, bar_w + 2, 2 * 11 - 1)        # fond des pistes
    d = ImageDraw.Draw(out)
    for r, lab in enumerate(('Speed', 'Direction')):
        ry = y + 8 + r * 11
        rogne(out, sheet, 0, 31, x + 4, ry, lab_w + 8, 11)
        d.text(((x + 8) * S, (ry + 1) * S), lab, fill=(0x44, 0x20, 0), font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 7 * S))
        for k in range(0, bar_w, 248): rogne(out, sheet, 7, 0, bar_x + k, ry + 1, min(248, bar_w - k), 8)
        for m in range(0, bar_w, 28): rogne(out, sheet, 0, 0, bar_x + m, ry + 1, 7, 8)
    cx, cy, cw = bar_x + 60, y + 8 - 2, 22                                         # curseur sur la 1re piste
    rogne(out, sheet, 0, 9, cx - 3, cy, 3, 14); rogne(out, sheet, 4, 9, cx, cy, cw, 14); rogne(out, sheet, 61, 9, cx + cw, cy, 3, 14)
    d.text(((cx + 2) * S, (cy + 3) * S), '64', fill=(0x44, 0x20, 0), font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 7 * S))
    # cadre
    rogne(out, sheet, 65, 9, x, y, 4, 4); rogne(out, sheet, 70, 9, x + w - 4, y, 4, 4)
    rogne(out, sheet, 65, 19, x, y + h - 4, 4, 4); rogne(out, sheet, 70, 19, x + w - 4, y + h - 4, 4, 4)
    etire(out, sheet, 65, 14, 3, 4, x, y + 4, 3, h - 8); etire(out, sheet, 71, 14, 3, 4, x + w - 3, y + 4, 3, h - 8)
    rogne(out, sheet, 0, 24, x + 4, y, w - 8, 3); rogne(out, sheet, 0, 27, x + 4, y + h - 3, w - 8, 3)
    return out
if __name__ == '__main__':
    import reglages
    O = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/value_settings.png'
    a = Image.open(O).convert('RGBA'); a = a.resize((a.width * S, a.height * S), Image.NEAREST)
    b = reglages.reglages()
    A, B = scene(a), scene(b)
    out = Image.new('RGBA', (A.width, A.height * 2 + 10), (30, 32, 38, 255)); out.alpha_composite(A, (0, 0)); out.alpha_composite(B, (0, A.height + 10))
    out.save('/tmp/l5b/vs_sim.png')
