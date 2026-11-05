import sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs")
from PIL import Image, ImageDraw, ImageFont
from rendu_mob import MODELES, rendre, boite
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
P="/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/entity/"; O="v2/out/"
def couche(boxes, du, g):
    out=[]
    for b in boxes:
        (x0,y0,z0),(x1,y1,z1)=b["f"],b["t"]; u,v,w,h,d=b["uv"]
        out.append({"f":(x0-g,y0-g,z0-g),"t":(x1+g,y1+g,z1+g),"uv":(u+du,v,w,h,d)})
    return out
def duo(a,b):
    c=Image.new("RGBA",(a.width*2,a.height)); c.paste(a.convert("RGBA"),(0,0)); c.paste(b.convert("RGBA"),(a.width,0)); return c
def squel():
    return MODELES["humanoide"](2,2)[:6]
def items(dossier, base):
    H=MODELES["humanoide"]()
    Ls=[]
    Ls.append((Image.open(dossier+"zombie/zombie.png"),"Chauffeur",H))
    Ls.append((Image.open(dossier+"zombie/husk.png"),"Prospecteur",H))
    t=duo(Image.open(dossier+"zombie/drowned.png"),Image.open(dossier+"zombie/drowned_outer_layer.png"))
    Ls.append((t,"Scaphandrier",couche(H[:6],64,0.25)+H))
    for k,n in (("stray","Veilleur des glaces"),("bogged","Drainier")):
        t=duo(Image.open(base+k+".png"),Image.open(dossier+"skeleton/"+k+"_overlay.png"))
        Ls.append((t,n,couche(squel(),64,0.25)+squel()))
    return Ls
def planche(Ls, sortie, N=300, tz=40):
    out=Image.new("RGB",(N*len(Ls),2*N+30),(40,42,48)); d=ImageDraw.Draw(out)
    for i,(t,n,m) in enumerate(Ls):
        out.paste(rendre(t,m,N=N,taille=tz),(i*N,30)); out.paste(rendre(t,m,N=N,taille=tz,dos=True),(i*N,30+N)); d.text((i*N+8,5),n,fill=(235,225,200),font=F)
    out.save(sortie)
planche(items(P,P+"skeleton/"),"v2/lot1_avant.png",N=260)
planche(items(O,O),"v2/lot1_v2.png",N=360,tz=36)
