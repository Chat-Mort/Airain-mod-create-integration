import sys, nbtlib
sys.argv=[sys.argv[0],"0","/tmp"]
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad")
import apercu_avant_poste as A
from PIL import Image, ImageDraw, ImageFont
A.TABLE[:0]=[("vine",(60,120,40)),("sculk",(20,60,70)),("soul_fire",(90,210,230)),("soul_soil",(75,58,45)),("lightning_rod",(200,120,80)),
 ("fluid_tank",(170,140,90)),("mechanical_pump",(160,150,120)),("lever",(120,110,100)),("iron_trapdoor",(200,200,205)),("spruce_trapdoor",(110,80,50)),
 ("lootr",(220,170,40)),("amethyst",(155,100,210)),("waxed_copper_block",(200,110,70)),("exposed_",(170,118,88)),("calcite",(225,225,220)),("smooth_basalt",(70,70,75))]
D="/tmp/ptest/kubejs/data/kubejs/structure/"
def charger(f, ymax=None, ymin=None, coupe=None):
    n=nbtlib.load(D+f); pal=[str(p["Name"])+("["+",".join(f"{k}={v}" for k,v in p["Properties"].items())+"]" if "Properties" in p else "") for p in n["palette"]]
    W={}
    for b in n["blocks"]:
        s=pal[int(b["state"])]
        if A.couleur(s) is None or "air" in s.split("[")[0]: continue
        x,y,z=[int(v) for v in b["pos"]]
        if ymax is not None and y>ymax: continue
        if ymin is not None and y<ymin: continue
        if coupe and not coupe(x,y,z): continue
        W[(x,y+1,z)]=s
    return W
L=[("ruines/atelier_effondre.nbt","Atelier effondré",dict(ymin=4)),("ruines/atelier_effondre.nbt","Atelier : la cave (coupe)",dict(ymax=4,coupe=lambda x,y,z: y<4 or (x,z)==(4,5))),
   ("ruines/reservoir_tombe.nbt","Château d'eau effondré",dict(ymin=4)),("ruines/reservoir_tombe.nbt","Château d'eau : salle des pompes (coupe)",dict(ymax=3)),
   ("ruines/conduite_rompue.nbt","Conduite rompue (retouchée par toi, ajouts autour)",{}),("ruines/relais_brise.nbt","Relais brisé",{}),
   ("station/station_capsules.nbt","Station : le collecteur (coupe sous le hall)",dict(ymax=5,coupe=lambda x,y,z: not (y==5)))]
imgs=[]
for f,t,kw in L:
    W=charger(f,**kw); imgs.append((t,A.iso(W,11,sol=not kw.get("ymax"),marge=1)))
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",17)
cols=2; rows=(len(imgs)+1)//2
cw=max(i.width for _,i in imgs); 
rh=[max(i.height for _,i in imgs[r*2:r*2+2])+34 for r in range(rows)]
out=Image.new("RGB",(cw*2,sum(rh)),(30,31,36)); d=ImageDraw.Draw(out)
y=0
for r in range(rows):
    for c in range(2):
        k=r*2+c
        if k>=len(imgs): break
        t,im=imgs[k]; d.text((c*cw+12,y+8),t,fill=(240,210,140),font=F); out.paste(im,(c*cw,y+34))
    y+=rh[r]
out.save("/home/claude/apercus/revue_ruines_v2.png"); print(out.size)
