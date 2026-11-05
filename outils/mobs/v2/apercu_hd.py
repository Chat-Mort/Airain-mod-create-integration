import sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mobs"); sys.path.insert(0,"v2")
from PIL import Image, ImageDraw, ImageFont
from rendu_mob import MODELES, rendre, boite
from apercu_lot3 import BLZ
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
def x4(bs): return [dict(b, uv=tuple(v*4 for v in b["uv"])) for b in bs]
L=[(Image.open("v2/out/creeper/creeper.png"),MODELES["creeper"](),"Chaudière instable — 16 px",34,(0,16,0)),
   (Image.open("v2/hd/creeper/creeper.png"),x4(MODELES["creeper"]()),"Chaudière instable — ×4",34,(0,16,0)),
   (Image.open("v2/out/blaze.png"),BLZ,"Lanterne de forge — 16 px",30,(0,16,0)),
   (Image.open("v2/hd/blaze.png"),x4(BLZ),"Lanterne de forge — ×4",30,(0,16,0))]
N=520; out=Image.new("RGB",(N*len(L),N+34),(40,42,48)); d=ImageDraw.Draw(out)
for i,(t,m,n,tz,c) in enumerate(L):
    out.paste(rendre(t,m,N=N,taille=tz,centre=c),(i*N,34)); d.text((i*N+10,6),n,fill=(235,225,200),font=F)
out.save("v2/hd_essai.png")
