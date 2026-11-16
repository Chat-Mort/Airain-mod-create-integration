# Maquette des afficheurs impériaux, vue de face sur un mur d'usine : tableau émaillé, plaque de gare, cadran,
# totaliseur à rouleaux, enseigne en lettres d'airain.
import math, numpy as np
from PIL import Image, ImageDraw, ImageFont
exec(open('livre_maquette.py').read().split('def couper')[0])
B=96; TX=B//16                      # 96 px par bloc, un texel = 6 px
W,H=20*B,9*B
img=Image.new('RGBA',(W,H),(0,0,0,255))
def tex(ns,p):
    base={'mc':MC,'air':AIR}[ns]
    return Image.open(base+'textures/'+p+'.png').convert('RGBA').crop((0,0,16,16)).resize((B,B),Image.NEAREST)
mur=tex('mc','block/bricks'); sol=tex('mc','block/polished_andesite')
for x in range(0,W,B):
    for y in range(0,H,B): img.alpha_composite(mur if y<8*B else sol,(x,y))
A=dict(c=(252,233,183),l=(243,214,148),m=(201,154,81),d=(168,118,60),s=(112,68,37),ss=(87,51,29),rv=(255,240,196))
d=ImageDraw.Draw(img)
def cadre(x0,y0,x1,y1,ep=2):
    """Cadre d'airain riveté (ep en texels), biseau clair en haut/à gauche."""
    e=ep*TX
    d.rectangle([x0,y0,x1-1,y1-1],fill=A['m'])
    d.rectangle([x0,y0,x1-1,y0+TX-1],fill=A['l']); d.rectangle([x0,y0,x0+TX-1,y1-1],fill=A['l'])
    d.rectangle([x0,y1-TX,x1-1,y1-1],fill=A['s']); d.rectangle([x1-TX,y0,x1-1,y1-1],fill=A['s'])
    d.rectangle([x0+e-TX,y0+e-TX,x1-e+TX-1,y0+e-1],fill=A['s']); d.rectangle([x0+e-TX,y0+e-TX,x0+e-1,y1-e+TX-1],fill=A['s'])
    for cx in (x0+TX*1, x1-TX*2):
        for cy in (y0+TX*0.5, y1-TX*1.5):
            pass
    # rivets tous les 8 texels sur le cadre
    for x in range(x0+TX*4,x1-TX*3,TX*8):
        for y in (y0+int(TX*0.5),y1-int(TX*1.5)):
            d.rectangle([x,y,x+TX//2,y+TX//2],fill=A['rv']); d.rectangle([x+TX//2,y+TX//2,x+TX-1,y+TX-1],fill=A['ss'])
    return x0+e,y0+e,x1-e,y1-e
def texte(t,x,y,col,ech=2,gras=False):
    """Police de Minecraft agrandie (ech px par pixel de police)."""
    tmp=Image.new('RGBA',(largeur(t)+len(t)+4,12),(0,0,0,0)); ecrire(tmp,t,0,1,col,gras)
    tmp=tmp.resize((tmp.width*ech,tmp.height*ech),Image.NEAREST); img.alpha_composite(tmp,(int(x),int(y))); return tmp.width
def centre(t,x0,x1,y,col,ech=2,gras=False): texte(t,(x0+x1)/2-largeur(t)*ech/2,y,col,ech,gras)
def barre(x,y,n,plein,ech=2,col=(232,196,110)):
    for i in range(n):
        c=col if i<plein else (70,62,52)
        d.rectangle([x+i*5*ech,y+ech,x+i*5*ech+4*ech-1,y+7*ech-1],fill=c)
    return n*5*ech
CR=(236,228,206); RO=(214,64,48); OR=(232,196,110)
# ---------------------------------------------------------------- 1. tableau émaillé (5 × 3 blocs)
x0,y0,x1,y1=cadre(1*B,1*B,6*B,4*B)
d.rectangle([x0,y0,x1-1,y1-1],fill=(24,24,30))
centre('GARE DE LA FONDERIE',x0,x1,y0+12,RO,3,True)
d.rectangle([x0+20,y0+48,x1-21,y0+49],fill=(110,90,60))
L=[("Lingots d'airain",'1 284',None),("Débit tapis nord",'312 /min',None),("Stress du réseau",'68 %',(10,7)),
   ("Moulage du canon",'41 %',(10,4)),("Arbres principaux",'128 tr/min',None),("Prochain train","Port-Impérial · 2 min",None)]
y=y0+64
for nom,val,b in L:
    texte(nom,x0+20,y,CR,2)
    if b: barre(x0+20+largeur(nom)*2+16,y,b[0],b[1])
    w=largeur(val)*2; texte(val,x1-20-w,y,OR,2)
    y+=34
# ---------------------------------------------------------------- 2. plaque de gare (émail bleu, une ligne en grand)
x0,y0,x1,y1=cadre(1*B,5*B,6*B,6*B,1)
d.rectangle([x0,y0,x1-1,y1-1],fill=(30,62,120)); d.rectangle([x0+6,y0+6,x1-7,y1-7],outline=CR,width=3)
centre('PORT-IMPÉRIAL',x0,x1,y0+18,CR,4,True)
# ---------------------------------------------------------------- 3. cadran (2 × 2 blocs)
cx,cy,R=8*B,2.5*B,int(0.92*B)
d.ellipse([cx-R-3*TX,cy-R-3*TX,cx+R+3*TX,cy+R+3*TX],fill=A['s']); d.ellipse([cx-R-2*TX,cy-R-2*TX,cx+R+2*TX,cy+R+TX],fill=A['l'])
d.ellipse([cx-R-TX,cy-R-TX,cx+R+TX,cy+R+TX],fill=A['m']); d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(238,228,200))
for a0,a1,c in ((-225,-90,(120,160,90)),(-90,-18,(225,190,80)),(-18,45,(200,70,50))):
    d.arc([cx-R+14,cy-R+14,cx+R-14,cy+R-14],a0,a1,fill=c,width=12)
for k in range(11):
    a=math.radians(-225+k*27); r0=R-30 if k%5 else R-40
    d.line([cx+math.cos(a)*r0,cy+math.sin(a)*r0,cx+math.cos(a)*(R-14),cy+math.sin(a)*(R-14)],fill=(40,30,25),width=3 if k%5==0 else 2)
a=math.radians(-225+0.68*270)
d.line([cx,cy,cx+math.cos(a)*(R-24),cy+math.sin(a)*(R-24)],fill=(150,30,24),width=6)
d.ellipse([cx-10,cy-10,cx+10,cy+10],fill=A['d']); d.ellipse([cx-5,cy-6,cx+3,cy+2],fill=A['l'])
centre('STRESS',cx-R,cx+R,cy-44,(60,45,35),2,True); centre('68 %',cx-R,cx+R,cy+30,(150,30,24),3,True)
for ang in (45,135,225,315):
    rx,ry=cx+math.cos(math.radians(ang))*(R+TX*1.5),cy+math.sin(math.radians(ang))*(R+TX*1.5)
    d.rectangle([rx-3,ry-3,rx+2,ry+2],fill=A['rv']); d.rectangle([rx,ry,rx+3,ry+3],fill=A['ss'])
# ---------------------------------------------------------------- 4. totaliseur à rouleaux (3 × 1 blocs)
x0,y0,x1,y1=cadre(10*B,1*B+48,13*B,2*B+48,2)
d.rectangle([x0,y0,x1-1,y1-1],fill=A['d'])
chiffres='001284'; n=len(chiffres); lw=(x1-x0-40)//n
for i,ch in enumerate(chiffres):
    rx=x0+20+i*lw
    d.rectangle([rx,y0+6,rx+lw-6,y1-7],fill=(26,22,20))
    for gy in range(y0+6,y1-6,2):    # galbe du rouleau : plus sombre en haut et en bas
        t=abs((gy-(y0+y1)/2)/((y1-y0)/2));
        if t>0.6: d.line([rx,gy,rx+lw-6,gy],fill=(14,12,11))
    if i==n-1:   # le dernier rouleau est en train de tourner : 4 qui s'en va par le haut, 5 qui arrive par le bas
        f=Image.new('RGBA',(lw-6,y1-y0-13),(26,22,20,255)); fd=ImageDraw.Draw(f)
        for k,(c,yy) in enumerate((('4',-12),('5',26))):
            g=Image.new('RGBA',(12,12),(0,0,0,0)); ecrire(g,c,0,1,CR,True); g=g.resize((36,36),Image.NEAREST); f.alpha_composite(g,(int((lw-6)/2-9),yy))
        fd.rectangle([0,0,lw,3],fill=(14,12,11)); fd.rectangle([0,f.height-4,lw,f.height],fill=(14,12,11))
        img.alpha_composite(f,(rx,y0+6))
    else: texte(ch,rx+lw/2-9,y0+18,CR,3,True)
    if i==n-4: d.rectangle([rx+lw-4,y0+6,rx+lw-3,y1-7],fill=A['s'])
d.rectangle([x0+20,y0+4,x1-21,y0+6],fill=(255,255,255,40))
# plaque gravée sous le totaliseur
x0,y0,x1,y1=cadre(10*B+70,2*B+60,13*B-70,2*B+108,1)
d.rectangle([x0,y0,x1-1,y1-1],fill=A['l']); centre('LINGOTS',x0,x1,y0+6,A['ss'],2,True)
# colonne à voyants (bargraphe)
x0,y0,x1,y1=cadre(14*B+24,1*B,14*B+72,4*B,1)
d.rectangle([x0,y0,x1-1,y1-1],fill=(30,26,24))
for k in range(10):
    yy=y1-14-k*((y1-y0-14)//10); on=k<7
    c=(230,80,50) if on and k>=6 else ((240,200,90) if on else (70,40,35))
    d.ellipse([x0+8,yy-18,x1-9,yy-4],fill=c)
    if on: d.ellipse([x0+12,yy-16,x0+18,yy-12],fill=(255,240,210))
# ---------------------------------------------------------------- 5. enseigne en lettres d'airain (relief, éclairage rouge)
mot='FONDERIE'; ech=11
x=8*B; y=5*B+10
lumiere=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lumiere)
for car in mot:
    w=adv(car,True)*ech
    # halo rouge sur le mur, dessous et derrière
    dl.rectangle([x-10,y-6,x+w-ech+10,y+8*ech+12],fill=(220,40,20,70))
    x+=w+6
lumiere=lumiere.resize((W//8,H//8),Image.BILINEAR).resize((W,H),Image.BILINEAR)
img.alpha_composite(lumiere)
x=8*B
for car in mot:
    texte(car,x+ech,y+ech,A['ss'],ech,True)          # ombre portée en bas à droite
    texte(car,x,y,A['m'],ech,True)
    # reflet en haut à gauche : la même lettre décalée et masquée
    tmp=Image.new('RGBA',(30,12),(0,0,0,0)); ecrire(tmp,car,0,0,A['l'],True)
    tmp2=Image.new('RGBA',(30,12),(0,0,0,0)); ecrire(tmp2,car,1,1,(0,0,0),True)
    a=np.asarray(tmp).copy(); b=np.asarray(tmp2)
    a[...,3]=np.where(b[...,3]>0,0,a[...,3])
    hl=Image.fromarray(a).resize((30*ech,12*ech),Image.NEAREST); img.alpha_composite(hl,(x,y))
    x+=adv(car,True)*ech+6
# étiquettes
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22)
out=Image.new('RGBA',(W,H+70),(34,30,38,255)); out.alpha_composite(img,(0,70)); dd=ImageDraw.Draw(out)
for t,x in (("1. Tableau émaillé (5×3)",1*B),("3. Cadran (2×2)",7*B),("4. Totaliseur + plaque",10*B),("5. Voyants",14*B-20)):
    dd.text((x,10),t,font=fo,fill=(235,215,170))
dd.text((1*B,40),"2. Plaque de gare (même bloc, une ligne)",font=fo,fill=(235,215,170)); dd.text((8*B,40),"6. Enseigne en lettres d'airain, éclairée",font=fo,fill=(235,215,170))
out.save('afficheurs.png'); print(out.size)
