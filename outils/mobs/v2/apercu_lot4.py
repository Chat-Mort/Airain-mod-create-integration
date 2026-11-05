import sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs")
from PIL import Image, ImageDraw, ImageFont
from rendu_mob import rendre, boite
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
P="/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"; O="v2/out/"
PH=[boite(-2.5,0,-4.5,5,3,9,0,8),boite(-3.5,0,-8.5,7,3,5,0,0),boite(-1.5,0.5,4.5,3,2,6,3,20),boite(-0.5,1,10.5,1,1,6,4,29),
    boite(2.5,1,-4.5,6,2,9,23,12),boite(8.5,1.5,-4.5,13,1,9,16,24),boite(-8.5,1,-4.5,6,2,9,23,12),boite(-21.5,1.5,-4.5,13,1,9,16,24)]
SL=[boite(-3,1,-3,6,6,6,0,16),boite(-3.25,4,-3.5,2,2,2,32,0),boite(1.25,4,-3.5,2,2,2,32,4),boite(0,2,-3.5,1,1,1,32,8),boite(-4,0,-4,8,8,8,0,0)]
GU=[boite(-6,0,-8,12,12,16,0,0),boite(-1,5,-8.25,2,2,1,8,0),boite(-2,2,8,4,4,8,40,0),boite(-1.5,2.5,16,3,3,7,0,54),boite(-1,3,23,2,2,6,41,32),boite(0,-0.5,25,1,9,9,25,19)]+\
   [boite(x,y,z,2,9,2,0,0) for (x,y,z) in ((-1,12,-1),(-1,-9,-1),(-9,5,-1),(7,5,-1))]
def oeil(b,y):
    b=b.convert("RGBA").copy(); b.alpha_composite(y.convert("RGBA")); return b
def items(D,E):
    return [(oeil(Image.open(D+"phantom.png"),Image.open(E+"phantom_eyes.png")),"Âme sans repos",PH,52,(0,2,0)),
            (Image.open(D+"slime/slime.png"),"Graisse vivante",SL,14,(0,4,0)),
            (Image.open(D+"guardian.png"),"Torpilleur",GU,40,(0,6,6)),(Image.open(D+"guardian_elder.png"),"Gardien des marées",GU,40,(0,6,6))]
def planche(Ls,sortie,N):
    out=Image.new("RGB",(N*len(Ls),2*N+30),(40,42,48)); d=ImageDraw.Draw(out)
    for i,(t,n,m,tz,c) in enumerate(Ls):
        out.paste(rendre(t,m,N=N,taille=tz,centre=c),(i*N,30)); out.paste(rendre(t,m,N=N,taille=tz,centre=c,dos=True),(i*N,30+N)); d.text((i*N+8,5),n,fill=(235,225,200),font=F)
    out.save(sortie)
V="/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/entity/"
planche(items(P,V),"v2/lot4_avant.png",300)
planche(items(O,O),"v2/lot4_v2.png",360)
