# Plaques émaillées, flèche de borne et cadran, dessinées à la taille exacte de leur face (posées pixel pour pixel).
import math
from PIL import Image, ImageDraw
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex/block/'
EM=(122,24,24); EM2=(140,32,28); ORf=(226,180,92); ORs=(160,104,48); ORc=(244,212,140)
def plaque(picto):
    """Plaque de 12 × 8 (colonnes 2 à 13, rangs 4 à 11) : liseré doré, émail rouge, pictogramme doré."""
    im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([2,4,13,11],fill=EM)
    d.line([(3,5),(12,5)],fill=EM2); d.line([(3,5),(3,10)],fill=EM2)
    d.line([(2,4),(13,4)],fill=ORc); d.line([(2,4),(2,11)],fill=ORc)          # liseré éclairé en haut à gauche
    d.line([(2,11),(13,11)],fill=ORs); d.line([(13,4),(13,11)],fill=ORs)
    G=ORf; O=ORs
    def px(pts,c=G):
        for p in pts: im.putpixel(p,c+(255,))
    if picto=='fleche':        # flèche pleine : fût sur 2 rangs, pointe triangulaire sur 6
        px([(x,y) for x in range(4,9) for y in (7,8)]); px([(9,y) for y in range(5,11)]); px([(10,y) for y in range(6,10)]); px([(11,7),(11,8)])
        px([(x,9) for x in range(4,9)],O)
    elif picto=='forge':       # marteau
        px([(x,y) for x in range(5,11) for y in (6,7)]); px([(7,y) for y in range(8,11)]+[(8,y) for y in range(8,11)]); px([(x,8) for x in (5,6,9,10)],O)
    elif picto=='danger':      # triangle plein, point d'exclamation en émail
        px([(7,5),(8,5)]+[(x,y) for y in (6,7) for x in range(6,10)]+[(x,y) for y in (8,9) for x in range(5,11)]+[(x,10) for x in range(4,12)])
        px([(7,6),(8,6),(7,7),(8,7),(7,8),(8,8),(7,10),(8,10)],EM)
    elif picto=='sortie':      # porte ouverte et flèche vers la sortie
        px([(4,y) for y in range(5,11)]+[(6,y) for y in range(5,11)]+[(5,5),(5,10)]); px([(5,y) for y in range(6,10)],O)
        px([(8,7),(9,7),(10,7),(8,8),(9,8),(10,8),(11,6),(11,7),(11,8),(11,9),(12,7),(12,8)])
    elif picto=='stock':       # caisse
        px([(x,5) for x in range(5,11)]+[(x,10) for x in range(5,11)]+[(5,y) for y in range(5,11)]+[(10,y) for y in range(5,11)]); px([(6,6),(7,7),(8,8),(9,9)],O)
    elif picto=='engrenage':   # engrenage à 8 dents
        px([(6,6),(7,6),(8,6),(9,6),(6,9),(7,9),(8,9),(9,9),(6,7),(6,8),(9,7),(9,8)]); px([(7,5),(8,5),(7,10),(8,10),(5,7),(5,8),(10,7),(10,8)],O)
    return im
for p in ('fleche','forge','danger','sortie','stock','engrenage'): plaque(p).save(OUT+'sign_'+p+'.png')
def planchette():
    """Flèche de borne : 12 × 4 (colonnes 2 à 13, rangs 6 à 9), pointe à droite."""
    im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([2,6,11,9],fill=EM); d.line([(2,6),(11,6)],fill=ORc); d.line([(2,9),(11,9)],fill=ORs); d.line([(2,6),(2,9)],fill=ORc)
    d.point((12,6),fill=ORc); d.point((12,7),fill=EM); d.point((12,8),fill=EM); d.point((12,9),fill=ORs); d.point((13,7),fill=ORf); d.point((13,8),fill=ORs)
    d.line([(4,7),(9,7)],fill=ORf); d.line([(4,8),(9,8)],fill=EM2)
    return im
planchette().save(OUT+'sign_board.png')
def cadran():
    """Cadran de 6 × 6 (colonnes et rangs 5 à 10) : fond ivoire, couronne dorée, zone rouge."""
    im=Image.new('RGBA',(16,16),(0,0,0,0)); px=im.load()
    IV=(236,226,200,255); C1=(226,180,92,255); C2=(160,104,48,255); RG=(170,44,32,255); TR=(90,60,40,255)
    for y in range(5,11):
        for x in range(5,11):
            r=math.hypot(x-7.5,y-7.5)
            if r<=3.2: px[x,y]=IV if r<=2.4 else (C1 if (x+y)<15 else C2)
    px[6,6]=TR; px[9,6]=TR; px[6,9]=TR; px[9,9]=RG; px[8,9]=RG
    return im
cadran().save(OUT+'gauge_face.png')
print('ok')
