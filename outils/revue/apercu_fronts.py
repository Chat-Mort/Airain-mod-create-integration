import sys
sys.argv=[sys.argv[0]]
src=open("/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/revue/apercu_ruines.py").read().split("L=[")[0]
src=src.replace('D="/tmp/ptest/kubejs/data/kubejs/structure/"','D="/home/claude/empire-airain-pack/kubejs/data/kubejs/structure/"')
exec(src)
A.TABLE[:0]=[("nether_brick",(70,30,34)),("netherrack",(110,40,40)),("blackstone",(40,36,40)),("basalt",(80,80,85)),("warped_stem",(60,110,110)),("warped",(40,140,130)),
 ("purple_wool",(120,50,160)),("black_wool",(30,30,34)),("purple_carpet",(120,50,160)),("soul_campfire",(90,210,230)),("mud_brick",(140,105,80)),("red_wool",(165,45,40)),("glass_pane",(190,225,235))]
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",17)
a=A.iso(charger("fronts/abri_nether.nbt"),16,sol=False,marge=1); b=A.iso(charger("fronts/champ_bataille.nbt"),13,marge=1)
o=Image.new("RGB",(a.width+b.width+20,max(a.height,b.height)+34),(30,31,36)); d=ImageDraw.Draw(o)
o.paste(a,(0,34)); o.paste(b,(a.width+20,34))
d.text((10,8),"Abri réfractaire du Nether (îlot du lac de lave)",font=F,fill=(240,210,140)); d.text((a.width+30,8),"Champ de bataille (le front)",font=F,fill=(240,210,140))
o.save("/home/claude/apercus/fronts_v1.png"); print(o.size)
