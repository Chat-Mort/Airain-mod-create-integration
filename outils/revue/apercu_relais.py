import sys
sys.argv=[sys.argv[0]]
exec(open("/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/revue/apercu_ruines.py").read().split("L=[")[0])
from PIL import Image
a=A.iso(charger("ruines/relais_brise.nbt"),18,marge=1)
b=A.iso(charger("ruines/atelier_effondre.nbt",ymin=4),18,marge=1)
c=A.iso(charger("ruines/atelier_effondre.nbt",ymax=3,coupe=lambda x,y,z: z<8 and x<6),22,sol=False,marge=0)
d=A.iso(charger("station/station_capsules.nbt",ymax=4,coupe=lambda x,y,z: z<13 and x<17),16,sol=False,marge=0)
W=a.width+b.width; H=max(a.height,b.height)+max(c.height,d.height)
o=Image.new("RGB",(W,H),(30,31,36)); o.paste(a,(0,0)); o.paste(b,(a.width,0)); o.paste(c,(0,max(a.height,b.height))); o.paste(d,(c.width,max(a.height,b.height)))
o.save("/home/claude/apercus/revue_ruines_zoom.png"); print(o.size)
