# Schéma vu de dessus : la nacelle fait le tour de la boucle (brin de droite dans le sens de marche).
import math
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20); f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def panneau(titre, park):
    W,H=1000,380; im=Image.new('RGB',(W,H),(28,29,34)); d=ImageDraw.Draw(im)
    d.text((20,12),titre,font=F,fill=(235,235,235))
    ax,bx,y,r=180,820,200,55
    cab=(201,154,62); fl=(120,200,255)
    d.line([(ax,y-r),(bx,y-r)],fill=cab,width=4); d.line([(ax,y+r),(bx,y+r)],fill=cab,width=4)
    d.arc([ax-r,y-r,ax+r,y+r],90,270,fill=cab,width=4); d.arc([bx-r,y-r,bx+r,y+r],270,90,fill=cab,width=4)
    for x,n in ((ax,'Gare A'),(bx,'Gare B')):
        d.ellipse([x-r+10,y-r+10,x+r-10,y+r-10],outline=(150,120,70),width=3); d.rectangle([x-10,y-10,x+10,y+10],fill=(110,90,60))
        d.text((x-35,y+r+30),n,font=f,fill=(220,220,220))
    for x in range(300,760,120):
        d.polygon([(x,y+r-9),(x+18,y+r),(x,y+r+9)],fill=fl)       # aller : brin du bas, vers B
        d.polygon([(x+18,y-r-9),(x,y-r),(x+18,y-r+9)],fill=fl)   # retour : brin du haut, vers A
    d.text((380,y+r+12),"aller A → B (à droite dans le sens de marche)",font=f,fill=fl)
    d.text((380,y-r-34),"retour B → A",font=f,fill=fl)
    for (px,py) in park:
        d.rectangle([px-18,py-18,px+18,py+18],outline=(240,90,90),width=3)
    return im
# la nacelle s'arrête du côté où elle arrive ; au départ, elle fait le demi-tour de la roue
a=panneau("Option 1 : arrêt à l'arrivée, demi-tour de la roue au départ",[(180,255),(820,255)])
a2=panneau("",[])
d=ImageDraw.Draw(a)
d.rectangle([180-18,145-18,180+18,145+18],fill=None)
im=Image.new('RGB',(1000,760),(28,29,34))
o1=panneau("Option 1 : arrêt du côté d'arrivée (le demi-tour de la roue se fait au départ)",[(180,145),(820,255)])
o2=panneau("Option 2 : arrêt du côté de départ (le demi-tour de la roue se fait à l'arrivée)",[(180,255),(820,145)])
im.paste(o1,(0,0)); im.paste(o2,(0,380))
d=ImageDraw.Draw(im); d.text((20,350),"carré rouge : où la nacelle attend (on y monte et on en descend)",font=f,fill=(240,130,130))
d.text((20,730),"carré rouge : où la nacelle attend (on y monte et on en descend)",font=f,fill=(240,130,130))
im.save('/mnt/user-data/outputs/gondola_loop_plan.png')
