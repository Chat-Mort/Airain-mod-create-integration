import math, random
from PIL import Image, ImageDraw
exec(open('affiches.py').read().split("A={}")[0])   # palettes et outils
NUIT=(36,30,56); NUIT2=(54,44,84); AME=(200,230,240); AME2=(150,200,230)
B={}
# Réveillez-vous : une capsule fendue, une silhouette qui en sort, lumière violette
im,d=base(NUIT); rayons(d,16,20,NUIT2,n=14)
d.rounded_rectangle([9,8,23,34],radius=5,fill=LAITON2,outline=NOIR)
d.polygon([(16,8),(14,16),(18,22),(15,34),(23,34),(23,8)],fill=NUIT)     # la capsule fendue
d.ellipse([13,10,19,16],fill=VIOLET2); d.polygon([(12,30),(13,17),(19,17),(20,30)],fill=VIOLET2)
d.line([4,36,28,36],fill=VIOLET2); bandeau(d,38,VIOLET); B['reveillez']=im
# Le diapason d'Ada : diapason et ondes
im,d=base((226,214,190))
for r in (6,10,14):
    d.arc([16-r,16-r,16+r,16+r],start=200,end=340,fill=VIOLET2,width=1); d.arc([16-r,16-r,16+r,16+r],start=20,end=160,fill=VIOLET2,width=1)
d.rectangle([12,6,13,20],fill=LAITON); d.rectangle([19,6,20,20],fill=LAITON); d.rectangle([12,20,20,22],fill=LAITON); d.rectangle([15,22,17,33],fill=LAITON2)
d.ellipse([14,32,18,35],fill=LAITON2); bandeau(d,38,VIOLET); B['diapason']=im
# Libres : des âmes qui montent d'un cœur brisé
im,d=base(NUIT)
for k,(x,y) in enumerate(((8,8),(16,5),(24,9),(11,16),(21,15),(16,12))):
    d.ellipse([x-2,y-2,x+2,y+2],fill=AME); d.line([x,y+2,x+(k%3-1),y+7],fill=AME2)
d.polygon([(16,34),(10,27),(10,24),(12,22),(16,25),(20,22),(22,24),(22,27)],fill=LAITON2,outline=NOIR)
d.line([16,25,15,29,17,31],fill=NOIR); bandeau(d,38,VIOLET); B['libres']=im
out=Image.new('RGB',(3*(W*6+12)+12,H*6+24),(28,28,32))
for i,(k,im) in enumerate(B.items()):
    im.save(k+'.png'); out.paste(im.resize((W*6,H*6),Image.NEAREST),(12+i*(W*6+12),12))
out.save('/home/claude/apercus/affiches_refractaires.png')
