import math
import sys; sys.path.insert(0,"../balise7")
from concepts import boite, cyl, rendu, LA, LA2, LA3, FER, CU, OR
from PIL import Image, ImageDraw, ImageFont
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PEAU=(150,120,100); CHEV=(70,50,35); VERRE=(150,200,215)
def tete(V):
    boite(V,(0,0,0),(8,8,8),PEAU); boite(V,(0,6,0),(8,8,8),CHEV); boite(V,(0,0,0),(1,8,8),CHEV)
RUBIS=(190,30,35); RUB2=(240,80,70)
def D():
    V={}; tete(V)
    # bandeau : 3 rangs, rivets
    for x in range(-1,10):
        for z in range(-1,10):
            if x in(-1,9) or z in(-1,9):
                V[(x,5,z)]=LA2; V[(x,6,z)]=LA; V[(x,7,z)]=LA3 if (x+z)%3==0 else LA
    # fleurons : coins et milieu de chaque face ; créneaux d'engrenage entre
    def pointe(x,z,h,top=LA3):
        for k in range(h): V[(x,8+k,z)]=LA if k<h-1 else top
    for i in range(-1,10):
        for (x,z) in ((i,-1),(i,9),(-1,i),(9,i)):
            if i in (-1,9): pointe(x,z,3)
            elif i in (3,5): pointe(x,z,2,LA)
            elif i==4: pointe(x,z,5)
            elif i in (1,7): pointe(x,z,1)
    V[(10,9,4)]=RUBIS; V[(10,10,4)]=RUB2
    for (x,z) in ((4,-2),(4,10),(-2,4)): V[(x,9,z)]=(58,150,130)
    # rouages sur les oreilles (côtés z), qui tournent
    for side,zz in ((-1,-2),(1,10)):
        for dy in range(-4,5):
            for dx in range(-4,5):
                r=math.hypot(dy,dx); a=math.atan2(dy,dx)
                if 1.3<=r<=3.0: V[(4+dx,3+dy,zz)]=OR
                elif 3.0<r<=4.2 and (a*10/math.pi)%2<1: V[(4+dx,3+dy,zz)]=LA2
        V[(4,3,zz)]=FER; V[(4,3,zz+side)]=LA3
        for y in (4,5): V[(4,y,zz-side if False else zz)]=V.get((4,y,zz),OR)
    # loupe sur l'oeil droit (face x=8, z=2), bras depuis le rouage
    for dy in (-1,0,1):
        for dz in (-1,0,1):
            V[(9,3+dy,2+dz)]=VERRE if (dy,dz)==(0,0) else LA3
    V[(9,3,0)]=LA2; V[(8,3,-1)]=LA2
    return V
ims=[rendu(D(),T=16)]
# vue de l'autre côté (miroir z)
V=D(); W={(z,y,8-x):c for (x,y,z),c in V.items()}; ims.append(rendu(W,T=16))
out=Image.new("RGB",(sum(i.width for i in ims)+60,max(i.height for i in ims)+90),(24,25,29)); d=ImageDraw.Draw(out)
x=20
for im,t in zip(ims,("Face (loupe sur l'œil droit)","Côté : le rouage couvre l'oreille")):
    out.paste(im,(x,20)); d.text((x,out.height-55),t,fill=(240,205,120),font=ImageFont.truetype(FB,18)); x+=im.width+20
out.save("/home/claude/apercus/couronne_finale_v1.png"); print(out.size)
