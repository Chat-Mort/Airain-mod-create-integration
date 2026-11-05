import sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs")
from PIL import Image, ImageDraw, ImageFont
from rendu_mob import MODELES, rendre, boite
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
P="/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"; O="v2/out/"
V="/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/entity/"
ENDER=[boite(-3,0,-1,2,30,2,56,0),boite(1,0,-1,2,30,2,56,0),boite(-4,30,-2,8,12,4,32,16),
       boite(-6,12,-1,2,30,2,56,0),boite(4,12,-1,2,30,2,56,0),boite(-4,42,-4,8,8,8,0,0),boite(-4,42,-4,8,8,8,0,16,gonfle=-0.5)]
MITE=[boite(-2,0,-6,4,3,2,0,0),boite(-3,0,-4,6,4,5,0,5),boite(-1.5,0,1,3,3,1,0,14),boite(-0.5,0,2,1,2,1,0,18)]
SB=[(3,2,2),(4,3,2),(6,4,3),(3,3,3),(2,2,3),(2,1,2),(1,1,2)]; SU=[(0,0),(0,4),(0,9),(0,16),(0,22),(11,0),(13,4)]
VER=[]; z=-8
for (w,h,d),(u,v) in zip(SB,SU):
    VER.append(boite(-w/2,0,z,w,h,d,u,v)); z+=d
VER+= [boite(-5,0,-3,10,8,3,20,0), boite(-3,0,2,6,4,3,20,11), boite(-3,0,-6.5,6,5,2,20,18)]
def oeil(base, yeux):
    b=base.convert("RGBA").copy(); b.alpha_composite(yeux.convert("RGBA")); return b
def items(D, E):
    return [(Image.open(D+"creeper/creeper.png"),"Chaudière instable",MODELES["creeper"](),40),
            (oeil(Image.open(D+"spider/spider.png"),Image.open(E+"spider_eyes.png")),"Rampeuse mécanique",MODELES["araignee"](),52),
            (oeil(Image.open(D+"spider/cave_spider.png"),Image.open(E+"spider_eyes.png")),"Rampeuse de réparation",MODELES["araignee"](),52),
            (oeil(Image.open(D+"enderman/enderman.png"),Image.open(E+"enderman/enderman_eyes.png")),"Égaré du Vide",ENDER,64),
            (Image.open(D+"endermite.png"),"Puce du vide",MITE,14),(Image.open(D+"silverfish.png"),"Ver de forage",VER,20)]
def planche(Ls,sortie,N):
    out=Image.new("RGB",(N*len(Ls),2*N+30),(40,42,48)); d=ImageDraw.Draw(out)
    for i,(t,n,m,tz) in enumerate(Ls):
        c=(0,16,0) if tz<=40 else (0,26,0)
        if tz<30: c=(0,2,-1)
        out.paste(rendre(t,m,N=N,taille=tz,centre=c),(i*N,30)); out.paste(rendre(t,m,N=N,taille=tz,centre=c,dos=True),(i*N,30+N)); d.text((i*N+8,5),n,fill=(235,225,200),font=F)
    out.save(sortie)
planche(items(P,V),"v2/lot2_avant.png",260)
planche(items(O,O),"v2/lot2_v2.png",330)
