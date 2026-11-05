import sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs")
from PIL import Image, ImageDraw, ImageFont
from rendu_mob import MODELES, rendre
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
def planche(items, sortie, N=300):
    out=Image.new("RGB",(N*len(items),2*N+30),(40,42,48)); d=ImageDraw.Draw(out)
    for i,(t,n,m,tz) in enumerate(items):
        out.paste(rendre(t,m,N=N,taille=tz),(i*N,30)); out.paste(rendre(t,m,N=N,taille=tz,dos=True),(i*N,30+N))
        d.text((i*N+8,5),n,fill=(235,225,200),font=F)
    out.save(sortie)
if __name__=="__main__":
    T="/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/skeleton/"
    O="v2/out/"; m=MODELES["humanoide"](2,2)
    items=[]
    for k,n in (("skeleton","Arbalétrier"),("stray","Veilleur des glaces"),("bogged","Drainier"),("wither_skeleton","Fondeur")):
        items.append((Image.open(T+k+".png"),n+" (avant)",m,40)); items.append((Image.open(O+k+".png"),n+" (v2)",m,40))
    planche(items,"v2/squelettes_v2.png",N=260)
