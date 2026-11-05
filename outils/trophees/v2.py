from PIL import Image, ImageDraw, ImageFont
import sys
def grille(lignes, pal):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, l in enumerate(lignes):
        for x, ch in enumerate(l):
            if ch != '.': im.putpixel((x, y), pal[ch] + (255,))
    return im
# Visière du Colosse : heaume de fer à cornes, fente rouge lumineuse
VISIERE = [
 "................",
 ".K............K.",
 ".KH..........HK.",
 "..KH.KKKKKK.HK..",
 "...KKLLLLLLKK...",
 "...KLLWWLLLMK...",
 "..KLLWLLLLLMMK..",
 "..KLLLLLLLLMMK..",
 "..KRRRRRRRRRRK..",
 "..KDOOYYYYOODK..",
 "..KLLLLLLLLMMK..",
 "..KLMLKLLKLMMK..",
 "..KLMLKLLKLMDK..",
 "...KLLKLLKMDK...",
 "....KKKKKKKK....",
 "................"]
PV = {'K': (22, 20, 26), 'H': (205, 195, 170), 'L': (160, 162, 172), 'W': (225, 228, 236), 'M': (105, 106, 118), 'D': (70, 70, 80),
      'R': (60, 20, 18), 'O': (200, 40, 25), 'Y': (255, 120, 60)}
# Cœur de magma : un cœur en netherite, veines de lave, artères de laiton
COEUR = [
 "....BB....BB....",
 "...KCCK..KCCK...",
 "..KNNNNKKNNNNK..",
 ".KNSSNNNNNNNNNK.",
 ".KNSNNOONNNNNNK.",
 ".KNNNOYYONNONNK.",
 ".KNNNNOYYOOONNK.",
 ".KNNONNOYONNNNK.",
 "..KNOONNONNNNK..",
 "...KNNNOONNNK...",
 "....KNNNNNNK....",
 ".....KNNONK.....",
 "......KNNK......",
 ".......KK.......",
 "................",
 "................"]
PC = {'K': (18, 14, 18), 'N': (62, 52, 58), 'S': (110, 98, 104), 'O': (255, 110, 20), 'Y': (255, 215, 90), 'B': (215, 165, 70), 'C': (150, 105, 40)}
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    v, c = grille(VISIERE, PV), grille(COEUR, PC)
    v.save(f'{out}/visiere_colosse.png'); c.save(f'{out}/coeur_magma.png')
    f = Image.new('RGBA', (420, 230), (36, 37, 42, 255))
    f.alpha_composite(v.resize((192, 192), 0), (10, 10)); f.alpha_composite(c.resize((192, 192), 0), (215, 10))
    d = ImageDraw.Draw(f); ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    d.text((10, 206), "Visière du Colosse", fill=(230, 220, 200), font=ft); d.text((215, 206), "Cœur de magma", fill=(230, 220, 200), font=ft)
    f.save('apercu_v2.png')
