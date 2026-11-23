# Pense-bête : lire un sceau de l'Écho (même tracé que le livre de l'ingénieur).
from PIL import Image, ImageDraw, ImageFont
Z=6   # agrandissement d'un tiers de pixel
def sceau(n, col=(94,46,140)):
    im=Image.new('RGBA',(24*Z,34*Z)); d=ImageDraw.Draw(im)
    def trait(x0,y0,x1,y1):
        m=max(abs(x1-x0),abs(y1-y0),1)
        for i in range(m+1):
            px=x0+round((x1-x0)*i/m); py=y0+round((y1-y0)*i/m)
            d.rectangle([(px-1)*Z,(py-1)*Z,(px+1)*Z-1,(py+1)*Z-1],fill=col)
    trait(12,4,12,30)
    for rang in range(4):
        c=n%10; n//=10; sx=1 if rang%2==0 else -1; haut=rang<2
        x0,x8,y0,y9=12,12+8*sx,(4 if haut else 30),(13 if haut else 21)
        if c in (1,5,7,9): trait(x0,y0,x8,y0)
        if c in (2,8,9): trait(x0,y9,x8,y9)
        if c==3: trait(x0,y0,x8,y9)
        if c in (4,5): trait(x0,y9,x8,y0)
        if c>=6: trait(x8,y0,x8,y9)
    return im
B=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30); R=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
W,H=1500,1250; im=Image.new('RGB',(W,H),(240,232,214)); d=ImageDraw.Draw(im)
d.text((40,30),"Lire un sceau de l'Écho",font=B,fill=(122,32,36))
d.text((40,80),"Une hampe, et un trait par chiffre. Un coin vide vaut zéro.",font=R,fill=(58,42,26))
for i,(n,t) in enumerate(((1,"Unités\nhaut droite"),(10,"Dizaines\nhaut gauche"),(100,"Centaines\nbas droite"),(1000,"Milliers\nbas gauche"))):
    x=60+i*360; im.paste(sceau(n),(x,130),sceau(n)); d.multiline_text((x+170,180),t,font=R,fill=(58,42,26),spacing=6)
d.text((40,360),"Les neuf traits (en unités ; aux autres coins, en miroir)",font=B,fill=(122,32,36))
for c in range(1,10):
    x=40+(c-1)*160; s=sceau(c); im.paste(s,(x,420),s); d.text((x+60,640),str(c),font=B,fill=(58,42,26))
d.text((40,700),"Exemples",font=B,fill=(122,32,36))
for i,(n,t) in enumerate(((3,"3"),(90,"90"),(176,"176"),(1024,"1 024"),(8192,"8 192"))):
    x=40+i*290; s=sceau(n); im.paste(s,(x,760),s); d.text((x+10,980),t,font=B,fill=(58,42,26))
d.text((40,1060),"176 = 1 centaine (bas droite) + 7 dizaines (haut gauche) + 6 unités (haut droite)",font=R,fill=(58,42,26))
d.text((40,1100),"En jeu : au survol d'un lot, la valeur s'affiche en éperons. Le mémo est aussi",font=R,fill=(58,42,26))
d.text((40,1135),"dans le livre de l'ingénieur, page « Archive résonante ».",font=R,fill=(58,42,26))
im.save('/mnt/user-data/outputs/echo_seal_cheatsheet.png')
