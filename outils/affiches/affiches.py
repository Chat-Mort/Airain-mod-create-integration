import math, random
from PIL import Image, ImageDraw
W,H=32,48
CREME=(226,206,160); CREME2=(200,176,128); ROUGE=(150,34,30); ROUGE2=(190,58,44); NOIR=(34,24,20); LAITON=(204,150,58); LAITON2=(140,96,36); OR=(244,210,120)
VIOLET=(120,70,160); VIOLET2=(170,120,210); BLEU=(60,80,110); GRIS=(90,84,80)
def base(fond=CREME):
    im=Image.new('RGB',(W,H),fond); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W-1,H-1],outline=NOIR)
    d.rectangle([1,1,W-2,H-2],outline=CREME2)
    return im,d
def bandeau(d,y,coul=ROUGE,lignes=2):
    d.rectangle([2,y,W-3,y+8],fill=coul)
    for k in range(lignes):
        yy=y+2+k*3
        x=4
        r=random.Random(y*7+k)
        while x<W-5:
            l=r.randint(2,5); d.line([x,yy,min(x+l,W-5),yy],fill=CREME); x+=l+2
def engrenage(d,cx,cy,r,dents,coul,coul2,trou=None):
    for k in range(dents):
        a=2*math.pi*k/dents
        d.polygon([(cx+math.cos(a-0.12)*r*0.9,cy+math.sin(a-0.12)*r*0.9),(cx+math.cos(a-0.1)*(r+2),cy+math.sin(a-0.1)*(r+2)),
                   (cx+math.cos(a+0.1)*(r+2),cy+math.sin(a+0.1)*(r+2)),(cx+math.cos(a+0.12)*r*0.9,cy+math.sin(a+0.12)*r*0.9)],fill=coul)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=coul,outline=coul2)
    if trou: d.ellipse([cx-trou,cy-trou,cx+trou,cy+trou],fill=coul2)
def rayons(d,cx,cy,coul,n=16,r0=6,r1=40):
    for k in range(n):
        if k%2: continue
        a=2*math.pi*k/n; b=2*math.pi*(k+1)/n
        d.polygon([(cx,cy),(cx+math.cos(a)*r1,cy+math.sin(a)*r1),(cx+math.cos(b)*r1,cy+math.sin(b)*r1)],fill=coul)
A={}
# 1. Le Cœur vous attend : cœur-engrenage rayonnant, file de silhouettes
im,d=base(); rayons(d,16,18,CREME2); engrenage(d,16,18,8,10,LAITON,LAITON2)
d.polygon([(16,23),(11,17),(11,14),(13,12),(16,14),(19,12),(21,14),(21,17)],fill=ROUGE2,outline=ROUGE)
for i,x in enumerate((5,11,17,23,29)):
    h=5+(i%2)
    d.polygon([(x-2,36),(x-2,36-h+1),(x-1,36-h),(x+1,36-h),(x+2,36-h+1),(x+2,36)],fill=NOIR)
    d.ellipse([x-2,36-h-5,x+1,36-h-2],fill=NOIR)
d.line([2,36,W-3,36],fill=NOIR)
bandeau(d,38); A['coeur_attend']=im
# 2. Un Empire, un moteur : grand engrenage, cheminées
im,d=base((200,90,60)); rayons(d,16,20,(220,120,80),n=20)
for x,h in ((4,14),(9,18),(23,16),(28,12)): d.rectangle([x-1,34-h,x+1,34],fill=NOIR); d.ellipse([x-2,34-h-4,x+2,34-h-1],fill=GRIS)
def eng2(cx,cy,r,n):
    for k in range(n):
        a=2*math.pi*k/n
        d.rectangle([cx+math.cos(a)*(r+1)-1.5,cy+math.sin(a)*(r+1)-1.5,cx+math.cos(a)*(r+1)+1.5,cy+math.sin(a)*(r+1)+1.5],fill=LAITON)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=LAITON,outline=LAITON2); d.ellipse([cx-r+3,cy-r+3,cx+r-3,cy+r-3],fill=LAITON2)
    d.ellipse([cx-2,cy-2,cx+2,cy+2],fill=NOIR)
    for k in range(4):
        a=math.pi/4+math.pi/2*k; d.line([cx,cy,cx+math.cos(a)*(r-3),cy+math.sin(a)*(r-3)],fill=LAITON)
eng2(16,21,8,10)
d.rectangle([2,34,W-3,36],fill=NOIR); bandeau(d,38,NOIR); A['un_moteur']=im
# 3. L'Écho n'existe pas : volutes violettes barrées
im,d=base()
for k in range(3):
    r=9-k*3; d.arc([16-r,18-r,16+r,18+r],start=30+k*60,end=300+k*60,fill=VIOLET if k%2==0 else VIOLET2,width=2)
d.ellipse([3,5,29,31],outline=ROUGE,width=3); d.line([7,27,25,9],fill=ROUGE,width=3)
bandeau(d,36); A['echo_interdit']=im
# 4. Le fondateur veille : buste de profil dans un halo d'engrenage
im,d=base((40,48,70)); engrenage(d,16,18,11,14,LAITON,LAITON2,trou=8)
d.ellipse([9,10,23,26],fill=(40,48,70))
d.polygon([(13,26),(12,20),(13,14),(17,11),(21,13),(22,17),(21,19),(22,21),(20,22),(19,26)],fill=NOIR)  # tête de profil
d.rectangle([17,15,21,17],fill=LAITON); d.point((20,16),fill=OR)   # lunettes
d.polygon([(8,34),(10,27),(22,27),(24,34)],fill=NOIR)               # épaules
bandeau(d,37,LAITON2); A['fondateur']=im
# 5. Volontaires : la capsule
im,d=base(); rayons(d,16,20,(236,220,180),n=14)
d.rounded_rectangle([10,8,22,34],radius=5,fill=LAITON,outline=LAITON2)
d.rounded_rectangle([12,11,20,29],radius=3,fill=(150,190,200))
d.rectangle([15,17,17,26],fill=NOIR); d.ellipse([14,13,18,17],fill=NOIR)
for y in (31,33): d.line([10,y,22,y],fill=LAITON2)
d.line([16,34,16,36],fill=NOIR); d.line([4,36,28,36],fill=NOIR)
bandeau(d,38,BLEU); A['capsule']=im
out=Image.new('RGB',(5*(W*6+12)+12,H*6+24),(28,28,32))
for i,(k,im) in enumerate(A.items()):
    im.save(k+'.png'); out.paste(im.resize((W*6,H*6),Image.NEAREST),(12+i*(W*6+12),12))
out.save('/home/claude/apercus/affiches_v1.png')
