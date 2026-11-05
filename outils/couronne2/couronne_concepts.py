import sys, math
sys.path.insert(0, '../balise7')
from concepts import boite, cyl, cylx, rendu, LA, LA2, LA3, FER, FONTE, CU, OX, ROUGE, OR
from PIL import Image, ImageDraw, ImageFont
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PEAU=(150,120,100); CHEV=(70,50,35); AMBRE=(255,180,60,1); VERRE=(150,200,215); VAP=(225,225,230)
def tete(V):
    boite(V,(0,0,0),(8,8,8),PEAU); boite(V,(0,6,0),(8,8,8),CHEV); boite(V,(0,0,0),(1,8,8),CHEV)
    boite(V,(8,3,2),(8+0,4,3),PEAU)
def bandeau(V, y=6, h=2):
    # anneau 10x10 autour de la tête (de -1 à 9)
    for x in range(-1,9+1):
        for z in range(-1,9+1):
            if x in(-1,9) or z in(-1,9):
                for yy in range(y,y+h): V[(x,yy,z)]=LA2 if yy==y else LA
    for (x,z) in ((-1,-1),(9,-1),(-1,9),(9,9)): V[(x,y+h,z)]=LA3
def A():   # Couronne-engrenage
    V={}; tete(V); bandeau(V)
    for i in range(-1,10):
        for (x,z) in ((i,-1),(i,9),(-1,i),(9,i)):
            if i%2==0: V[(x,8,z)]=LA; V[(x,9,z)]=LA3 if i in (0,8) else LA
    # grand rouage frontal (face x=9) qui tourne
    for dy in range(-3,4):
        for dz in range(-3,4):
            r=math.hypot(dy,dz)
            if r<=3.2 and r>=1.2: V[(10,10+dy,4+dz)]=OR
            if 3.2<r<=3.9 and (math.atan2(dy,dz)*8/math.pi)%2<1: V[(10,10+dy,4+dz)]=LA2
    V[(10,10,4)]=(200,40,30); V[(11,10,4)]=FER
    for dz in (3,4,5): V[(10,7,dz)]=CU
    return V
def B():   # Couronne des lampes
    V={}; tete(V); bandeau(V)
    for (x,z) in ((-1,-1),(9,-1),(-1,9),(9,9),(4,-1),(4,9),(9,4)):
        for y in range(8,11): V[(x,y,z)]=LA2 if y<10 else LA
        V[(x,11,z)]=AMBRE; V[(x,12,z)]=LA3
    for x in range(-1,10): V[(x,10,-1)]=CU; V[(x,10,9)]=CU
    for z in range(-1,10): V[(9,10,z)]=CU
    # évent de vapeur à l'arrière
    boite(V,(-2,6,3),(-1,10,5),FER); 
    for k,(y) in enumerate(range(11,15)): V[(-2-k%2,y,4)]=VAP
    return V
def C():   # Diadème de commandement
    V={}; tete(V); bandeau(V,y=5,h=2)
    # loupe sur l'oeil droit (face x=8, z=1..2)
    for dy in (-1,0,1):
        for dz in (-1,0,1):
            V[(9,4+dy,2+dz)]=VERRE if (dy,dz)==(0,0) else LA3
    V[(9,5,4)]=LA2; V[(9,6,5)]=LA2
    # rouages latéraux
    for side in (-2,10):
        for dy in range(-2,3):
            for dx in range(-2,3):
                if 1<=math.hypot(dy,dx)<=2.4: V[(4+dx,6+dy,side)]=OR
        V[(4,6,side)]=FER
    # antenne de commandement au sommet
    for y in range(8,14): V[(4,y,4)]=FER
    V[(4,14,4)]=AMBRE
    for (dx,dz) in ((1,0),(-1,0),(0,1),(0,-1)): V[(4+dx,11,4+dz)]=CU
    for (dx,dz) in ((1,0),(-1,0),(0,1),(0,-1)): V[(4+2*dx,9,4+2*dz)]=LA2; V[(4+dx,9,4+dz)]=LA2
    return V
noms=[("A — Couronne-engrenage","Bandeau à dents d'engrenage,\ngrand rouage frontal qui tourne"),
      ("B — Couronne des lampes","Sept flèches à ampoules ambrées,\ntuyaux de cuivre, évent de vapeur"),
      ("C — Diadème de commandement","Loupe sur l'œil, rouages latéraux,\nantenne lumineuse qui « parle » aux automates")]
ims=[rendu(f(),T=14) for f in (A,B,C)]
W=sum(i.width for i in ims)+80; H=max(i.height for i in ims)+130
out=Image.new("RGB",(W,H),(24,25,29)); d=ImageDraw.Draw(out)
x=20
for im,(t,s) in zip(ims,noms):
    out.paste(im,(x,20)); d.text((x,H-100),t,fill=(240,205,120),font=ImageFont.truetype(FB,20)); d.multiline_text((x,H-70),s,fill=(200,200,200),font=ImageFont.truetype(F,15))
    x+=im.width+20
out.save("/home/claude/apercus/couronne_concepts.png"); print(out.size)
