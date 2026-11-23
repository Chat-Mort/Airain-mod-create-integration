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
    # disposition reprise de ValueSettingsScreen.renderWindow (Create 6.0.10)
    W, H = 260, 70; out = Image.new('RGBA', (W * S, H * S), fond); d = ImageDraw.Draw(out)
    F7 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 7 * S)
    labels = ('Speed', 'Direction'); x, y = 20, 20
    mlw = int(max(d.textlength(l, font=F7) for l in labels) / S) + 1; vbw = 140; rows = 2
    def cadre(fx, fy, fw, fh):
        rogne(out, sheet, 65, 9, fx, fy, 4, 4); rogne(out, sheet, 70, 9, fx + fw - 4, fy, 4, 4)
        rogne(out, sheet, 65, 19, fx, fy + fh - 4, 4, 4); rogne(out, sheet, 70, 19, fx + fw - 4, fy + fh - 4, 4, 4)
        etire(out, sheet, 65, 14, 3, 4, fx, fy + 4, 3, fh - 8); etire(out, sheet, 71, 14, 3, 4, fx + fw - 3, fy + 4, 3, fh - 8)
        rogne(out, sheet, 0, 24, fx + 4, fy, fw - 8, 3); rogne(out, sheet, 0, 27, fx + 4, fy + fh - 3, fw - 8, 3)
    cadre(x + mlw + 14, y - 3, vbw + 8, rows * 11 + 5)
    etire(out, sheet, 75, 9, 1, 1, x + mlw + 17, y, vbw + 2, rows * 11 - 1)
    for r, lab in enumerate(labels):
        ry = y + r * 11; vx = x + mlw + 18
        rogne(out, sheet, 0, 31, x - 4, ry, mlw + 8, 11)
        out.alpha_composite(piece(sheet, 162, 31, 3, 11), ((x + mlw + 1) * S, ry * S))       # embout posé par le mod
        for k in range(0, vbw, 248): rogne(out, sheet, 7, 0, vx + k, ry + 1, min(248, vbw - k), 8)
        for m in range(0, vbw - 6, 28): rogne(out, sheet, 0, 0, vx + m, ry + 1, 7, 8)
        rogne(out, sheet, 0, 0, vx + vbw - 7, ry + 1, 7, 8)
        d.text((x * S, (ry + 1) * S), lab, fill=(0x44, 0x20, 0), font=F7)
    cx, cy, cw = x + mlw + 18 + 60, y - 2, 22
    rogne(out, sheet, 0, 9, cx - 3, cy, 3, 14); rogne(out, sheet, 4, 9, cx, cy, cw, 14); rogne(out, sheet, 61, 9, cx + cw, cy, 3, 14)
    d.text(((cx + 2) * S, (cy + 3) * S), '64', fill=(0x44, 0x20, 0), font=F7)
    return out
if __name__ == '__main__':
    import reglages
    O = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/value_settings.png'
    a = Image.open(O).convert('RGBA'); a = a.resize((a.width * S, a.height * S), Image.NEAREST)
    b = reglages.reglages()
    A, B = scene(a), scene(b)
    out = Image.new('RGBA', (A.width, A.height * 2 + 10), (30, 32, 38, 255)); out.alpha_composite(A, (0, 0)); out.alpha_composite(B, (0, A.height + 10))
    out.save('/tmp/l5b/vs_sim.png')
