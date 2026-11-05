import sys
from PIL import Image, ImageDraw, ImageFont
from rendu_mob import MODELES, rendre
T="/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
L=[("skeleton/skeleton.png","Arbalétrier",MODELES["humanoide"](2,2)),("skeleton/stray.png","Veilleur des glaces",MODELES["humanoide"](2,2)),
   ("skeleton/bogged.png","Drainier",MODELES["humanoide"](2,2)),("skeleton/wither_skeleton.png","Fondeur",MODELES["humanoide"](2,2)),
   ("zombie/zombie.png","Chauffeur",MODELES["humanoide"]()),("zombie/husk.png","Prospecteur",MODELES["humanoide"]()),
   ("creeper/creeper.png","Chaudière instable",MODELES["creeper"]()),("spider/spider.png","Rampeuse mécanique",MODELES["araignee"]())]
N=300; out=Image.new("RGB",(N*len(L),2*N+30),(40,42,48)); d=ImageDraw.Draw(out)
for i,(f,n,m) in enumerate(L):
    t=Image.open(T+f)
    tz=40 if "spider" not in f else 52
    out.paste(rendre(t,m,N=N,taille=tz),(i*N,30)); out.paste(rendre(t,m,N=N,taille=tz,dos=True),(i*N,30+N))
    d.text((i*N+8,5),n,fill=(235,225,200),font=F)
out.save(sys.argv[1])
