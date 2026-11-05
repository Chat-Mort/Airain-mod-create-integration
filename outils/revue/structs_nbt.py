import sys, nbtlib
sys.argv=[sys.argv[0],"0","/tmp"]
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad")
import apercu_avant_poste as A
from PIL import Image, ImageDraw, ImageFont
D="/home/claude/empire-airain-pack/kubejs/data/kubejs/structure/"
L=[("ruines/atelier_effondre.nbt","Ruine : atelier effondré"),("ruines/reservoir_tombe.nbt","Ruine : réservoir tombé"),("refractaires/cache.nbt","Cache réfractaire"),("laboratoire.nbt","Laboratoire (départ)"),("ruines/relais_brise.nbt","Relais brisé")]
imgs=[]
for f,t in L:
    n=nbtlib.load(D+f); pal=[str(p["Name"])+("["+",".join(f"{k}={v}" for k,v in p["Properties"].items())+"]" if "Properties" in p else "") for p in n["palette"]]
    W={}
    for b in n["blocks"]:
        s=pal[int(b["state"])]
        if A.couleur(s) is None: continue
        x,y,z=[int(v) for v in b["pos"]]
        if f=="laboratoire.nbt" and y>=int(n["size"][1])-3: continue
        W[(x,y+1,z)]=s
    imgs.append((t,A.iso(W,9,marge=1)))
w=max(i.width for _,i in imgs); h=sum(i.height+30 for _,i in imgs)
out=Image.new("RGB",(w,h),(30,31,36)); d=ImageDraw.Draw(out); y=0
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",16)
for t,i in imgs:
    d.text((10,y+6),t,fill=(240,210,140),font=F); out.paste(i,(0,y+30)); y+=i.height+30
out.save("/home/claude/apercus/revue_structures_petites.png"); print(out.size)
