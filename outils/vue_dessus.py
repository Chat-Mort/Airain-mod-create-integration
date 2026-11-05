import nbtlib, sys, json
from PIL import Image, ImageDraw, ImageFont
sys.argv=sys.argv
exec(open("apercu_avant_poste.py").read().split("TABLE = ")[1].split("\n")[0].join(["TABLE = ",""]) if False else "")
src=open("apercu_avant_poste.py").read(); i=src.index("TABLE = "); j=src.index("]\n",i)+1
exec(src[i:j])
def couleur(s):
    for k,c in TABLE:
        if k in s: return c
    return (220,0,220)
def vue(f, out, C=8):
    n=nbtlib.load(f); pal=n["palette"]; sx,sy,sz=[int(v) for v in n["size"]]
    top={}; J=[]
    for b in n["blocks"]:
        x,y,z=[int(v) for v in b["pos"]]; st=pal[int(b["state"])]; name=str(st["Name"])
        if name=="minecraft:jigsaw":
            J.append((x,y,z,str(b["nbt"]["name"]).split(":")[1],str(st["Properties"]["orientation"]).split("_")[0])); continue
        if name in ("minecraft:air","minecraft:structure_void"): continue
        if (x,z) not in top or y>=top[(x,z)][0]: top[(x,z)]=(y,name)
    im=Image.new("RGB",(sx*C+20,sz*C+20),(105,135,65)); d=ImageDraw.Draw(im)
    for (x,z),(y,s) in top.items():
        c=couleur(s); k=0.75+0.25*min(y,12)/12; c=tuple(int(v*k) for v in c)
        d.rectangle([10+x*C,10+z*C,10+x*C+C-1,10+z*C+C-1],fill=c)
    F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",10)
    for (x,y,z,nm,o) in J:
        d.rectangle([10+x*C,10+z*C,10+x*C+C-1,10+z*C+C-1],fill=(255,0,0)); d.text((12+x*C,10+z*C-11),nm[:5]+o[0],font=F,fill=(255,255,255))
    im.save(out)
for a in sys.argv[1:]:
    vue(a, "out/dessus_"+a.split("/")[-1].replace(".nbt",".png"))
