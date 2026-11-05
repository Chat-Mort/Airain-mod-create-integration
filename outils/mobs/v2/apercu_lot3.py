import sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs")
from PIL import Image, ImageDraw, ImageFont
from rendu_mob import rendre, boite
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
P="/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"; O="v2/out/"
PIG=[boite(-4,0,-2,4,12,4,0,16),boite(0,0,-2,4,12,4,16,48),boite(-4,12,-2,8,12,4,16,16),boite(-8,12,-2,4,12,4,40,16),boite(4,12,-2,4,12,4,32,48),
     boite(-5,24,-4,10,8,8,0,0),boite(-2,25,-5,4,4,1,31,1),boite(-6,27,-2,1,5,4,39,6),boite(5,27,-2,1,5,4,51,6)]
HOG=[boite(-8,10,-13,16,14,26,1,1),boite(-7,6,-32,14,6,19,61,1),boite(-8,9,-30,2,11,2,10,13),boite(6,9,-30,2,11,2,1,13),
     boite(-7,0,-12,6,14,6,66,42),boite(1,0,-12,6,14,6,41,42),boite(-6,0,7,5,11,5,21,45),boite(1,0,7,5,11,5,0,45),boite(0,24,-10,0,10,19,90,33)]
BLZ=[boite(-4,20,-4,8,8,8,0,0)]+[boite(x,y,z,2,8,2,0,16) for (x,y,z) in ((-7,10,-1),(5,10,-1),(-1,10,-7),(-1,10,5),(-5,4,-5),(3,4,3),(3,4,-5),(-5,4,3))]
GHA=[boite(-8,16,-8,16,16,16,0,0)]+[boite(x,16-L,z,2,L,2,0,0) for (x,z,L) in ((-6,-5,12),(-1,-5,9),(4,-5,14),(-6,0,10),(-1,0,13),(4,0,8),(-6,5,11),(-1,5,12),(4,5,9))]
WIT=[boite(-10,20,-1.5,20,3,3,0,16),boite(-1.5,10,-1.5,3,10,3,0,22),boite(-4,23,-4,8,8,8,0,0),boite(-14,20,-3,6,6,6,32,0),boite(8,20,-3,6,6,6,32,0),boite(-1.5,4,-1.5,3,6,3,12,22)]
def items(D):
    return [(Image.open(D+"piglin/piglin.png"),"Forgeron de l'abîme",PIG,40,(0,16,0)),(Image.open(D+"piglin/piglin_brute.png"),"Garde de la forge",PIG,40,(0,16,0)),
            (Image.open(D+"piglin/zombified_piglin.png"),"Forgeron calciné",PIG,40,(0,16,0)),(Image.open(D+"hoglin/hoglin.png"),"Bélier-locomotive",HOG,64,(0,12,-8)),
            (Image.open(D+"hoglin/zoglin.png"),"Épave",HOG,64,(0,12,-8)),(Image.open(D+"blaze.png"),"Lanterne de forge",BLZ,34,(0,16,0)),
            (Image.open(D+"ghast/ghast.png"),"Dirigeable fantôme",GHA,44,(0,14,0)),(Image.open(D+"ghast/ghast_shooting.png"),"(en tir)",GHA,44,(0,14,0)),
            (Image.open(D+"wither/wither.png"),"Gardien des enfers",WIT,36,(0,20,0))]
def planche(Ls,sortie,N):
    out=Image.new("RGB",(N*len(Ls),2*N+30),(40,42,48)); d=ImageDraw.Draw(out)
    for i,(t,n,m,tz,c) in enumerate(Ls):
        out.paste(rendre(t,m,N=N,taille=tz,centre=c),(i*N,30)); out.paste(rendre(t,m,N=N,taille=tz,centre=c,dos=True),(i*N,30+N)); d.text((i*N+8,5),n,fill=(235,225,200),font=F)
    out.save(sortie)
if __name__=="__main__":
    planche(items(P),"v2/lot3_avant.png",240)
    planche(items(O),"v2/lot3_v2.png",300)
