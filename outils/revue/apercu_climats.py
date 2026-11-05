import sys, os, importlib
SP="/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad"; sys.path.insert(0, SP)
from PIL import Image, ImageDraw, ImageFont
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EXTRA=[("apercu:toile_or",(215,170,60)),("apercu:toile",(165,30,28)),("grand_etendard",(205,165,75)),("banniere_murale",(165,30,28)),
       ("exposed_",(170,118,88)),("snow",(242,246,250))]
VEC={"north":(0,-1),"south":(0,1),"east":(1,0),"west":(-1,0)}
def habiller(W):
    for (x,y,z),s in list(W.items()):
        if "grand_etendard" in s and "partie=6" in s:
            f=s.split("facing=")[1].split(",")[0].split("]")[0]
            # potence : bras vers la droite de la face, toile qui pend sur 4 blocs
            dx,dz={"north":(1,0),"south":(-1,0),"east":(0,1),"west":(0,-1)}[f]
            for k in (1,2): W[(x+dx*k,y,z+dz*k)]="apercu:toile_or"
            for k in (1,2):
                for h in range(0,4): W[(x+dx*k,y-1-h,z+dz*k)]="apercu:toile"
        if "banniere_murale" in s:
            for h in (1,2): W[(x,y-h,z)]="apercu:toile"
out=[]
for clim in ("tempere","desert","froid","savane"):
    sys.argv=["a","2","/tmp",clim]
    if "apercu_avant_poste" in sys.modules: del sys.modules["apercu_avant_poste"]
    A=importlib.import_module("apercu_avant_poste")
    A.TABLE[:0]=EXTRA
    places=A.assembler(2); W=A.blocs_monde(places); habiller(W)
    im=A.iso(W,7)
    ImageDraw.Draw(im).text((14,10),"Avant-poste "+A.NOMS_CLIMAT[clim],font=ImageFont.truetype(FB,20),fill=(240,240,240))
    out.append(im)
    if clim=="tempere":
        # gros plan de la place
        c=[p for p in places if p.nom=="centre_fontaine"]
        if c:
            Wc=A.blocs_monde(c); habiller(Wc); A.iso(Wc,16,marge=1).save("/home/claude/apercus/place_etendards.png")
w=max(i.width for i in out); h=max(i.height for i in out)
g=Image.new("RGB",(w*2,h*2),(30,31,36))
for i,im in enumerate(out): g.paste(im,((i%2)*w,(i//2)*h))
g.save("/home/claude/apercus/avant_postes_climats_v2.png"); print(g.size)
