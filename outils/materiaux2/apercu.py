import random
from PIL import Image, ImageDraw, ImageFont
T='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'; N='tex/'
f1=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22); f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
Z=4
def mur(fichiers,c,l,seed=1):
    r=random.Random(seed); im=Image.new('RGB',(c*16,l*16))
    for j in range(l):
        for i in range(c): im.paste(Image.open(r.choice(fichiers)).convert('RGB'),(i*16,j*16))
    return im.resize((im.width*Z,im.height*Z),Image.NEAREST)
def colonne(fichiers_par_rang):
    im=Image.new('RGB',(16,16*len(fichiers_par_rang)))
    for j,f in enumerate(fichiers_par_rang): im.paste(Image.open(f).convert('RGB'),(0,j*16))
    return im.resize((im.width*Z,im.height*Z),Image.NEAREST)
o=Image.new('RGB',(1860,1720),(27,29,34)); d=ImageDraw.Draw(o); y=14
def titre(t,x,yy,f=f1): d.text((x,yy),t,font=f,fill=(240,236,228))
titre("Marbre : aujourd'hui (à gauche) et proposé (à droite)",20,y); y+=36
for n,en in (('blanc','white'),('noir','black')):
    a=mur([T+f'{en}_marble_{v}.png' for v in range(6)],6,4); b=mur([N+f'marbre_{n}_{v}.png' for v in range(6)],6,4)
    o.paste(a,(20,y)); o.paste(b,(20+a.width+40,y))
    p=mur([N+f'marbre_{n}_poli.png'],3,4); o.paste(p,(20+2*a.width+80,y)); d.text((20+2*a.width+80,y+p.height+4),'poli',font=f2,fill=(200,200,208))
    y+=a.height+34
titre("Piliers empilés : aujourd'hui (une bande d'or par bloc) et proposé (bandes aux bouts de la colonne)",20,y); y+=36
x=20
for n,en in (('blanc','white'),('noir','black')):
    a=colonne([T+f'{en}_marble_pillar.png']*3); b=colonne([N+f'pilier_{n}_10.png',N+f'pilier_{n}_00.png',N+f'pilier_{n}_01.png'])
    o.paste(a,(x,y)); o.paste(b,(x+a.width+20,y)); x+=2*a.width+80
yp=y
titre("Nouvelles ardoises",x+40,yp)
xs=x+40; ys=yp+36
for k,(nom,lib) in enumerate((('ardoise_briques','Briques'),('ardoise_dalles','Petites dalles'),('ardoise_taillee','Taillée'),('ardoise_chevrons','Chevrons'),('ardoise_ciselee','Ciselée'),('ardoise_pilier','Pilier cannelé'))):
    m=mur([N+nom+'.png'],2,2); xx=xs+(k%3)*(m.width+30); yy=ys+(k//3)*(m.height+40)
    o.paste(m,(xx,yy)); d.text((xx,yy+m.height+4),lib,font=f2,fill=(200,200,208))
o.save('/home/claude/travail/materiaux2/apercu_materiaux.png'); print(o.size)
