import random
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17); FB=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",19)
h=lambda v:((v>>16)&255,(v>>8)&255,v&255)
N=[("nether_wastes","Désolations du Nether","Terres calcinées","Scorched Wastes",0x330808,0x3A1806,"—"),
   ("crimson_forest","Forêt carmin","Bois de braise","Ember Woods",0x330303,0x3E1004,"spores carmin"),
   ("warped_forest","Forêt biscornue","Bois de vert-de-gris","Verdigris Woods",0x1A051A,0x0C3430,"spores bleues"),
   ("soul_sand_valley","Vallée des âmes","Vallée des transférés","Valley of the Transferred",0x1B4745,0x1E4A56,"cendres"),
   ("basalt_deltas","Deltas de basalte","Crassiers noirs","Black Slag Heaps",0x685F70,0x5A4E44,"cendres blanches")]
E=[("the_end","L'End","Île du Gardien","Guardian's Isle"),
   ("end_highlands","Hautes terres de l'End","Hauts de la Réserve","Reserve Highlands"),
   ("end_midlands","Terres moyennes de l'End","Terrasses de la Réserve","Reserve Terraces"),
   ("small_end_islands","Petites îles de l'End","Îlots à la dérive","Drifting Islets"),
   ("end_barrens","Terres stériles de l'End","Confins du Vide","Void Fringes")]
END_AV,END_AP=0xA080A0,0x9C8670
W,H=1400,820; im=Image.new("RGB",(W,H),(36,38,44)); d=ImageDraw.Draw(im)
d.text((30,18),"NETHER",fill=(230,170,110),font=FB)
d.text((380,18),"vanilla (FR)",fill=(150,150,150),font=F); d.text((640,18),"Empire (FR / EN)",fill=(235,225,200),font=F); d.text((1100,18),"brouillard : avant → après",fill=(150,150,150),font=F)
y=50
for k,av,fr,en,c0,c1,p in N:
    d.text((30,y+8),k,fill=(120,120,130),font=F); d.text((380,y+8),av,fill=(170,170,170),font=F)
    d.text((640,y),fr,fill=(240,230,205),font=FB); d.text((640,y+22),en,fill=(170,160,140),font=F)
    d.rectangle((1100,y,1180,y+40),fill=h(c0)); d.text((1192,y+10),"→",fill=(200,200,200),font=FB); d.rectangle((1220,y,1300,y+40),fill=h(c1))
    y+=58
y+=20; d.text((30,y),"END",fill=(190,160,230),font=FB); y+=32
for k,av,fr,en in E:
    d.text((30,y+8),k,fill=(120,120,130),font=F); d.text((380,y+8),av,fill=(170,170,170),font=F)
    d.text((640,y),fr,fill=(240,230,205),font=FB); d.text((640,y+22),en,fill=(170,160,140),font=F)
    y+=52
d.rectangle((1100,y-260,1180,y-220),fill=h(END_AV)); d.text((1192,y-250),"→",fill=(200,200,200),font=FB); d.rectangle((1220,y-260,1300,y-220),fill=h(END_AP))
d.text((1100,y-210),"brouillard (tous)",fill=(150,150,150),font=F)
im.save("ambiance/noms_couleurs.png")

# ciel de l'End : vanilla vs proposition
v=Image.open("mcmeta-assets/assets/minecraft/textures/environment/end_sky.png").convert("RGBA")
p=v.copy(); px=p.load(); rng=random.Random(4)
lo,hi=(34,30,40),(190,150,104)
for x in range(p.width):
    for yy in range(p.height):
        r,g,b,a=px[x,yy]; t=(r+g+b)/765
        px[x,yy]=tuple(int(lo[i]+(hi[i]-lo[i])*t) for i in range(3))+(a,)
for _ in range(60):
    x,yy=rng.randrange(p.width),rng.randrange(p.height); px[x,yy]=(255,226,140,255)
for _ in range(25):
    x,yy=rng.randrange(p.width),rng.randrange(p.height); px[x,yy]=(150,255,240,255)
p.save("ambiance/end_sky.png")
def tuile(t): 
    c=Image.new("RGBA",(t.width*3,t.height*2))
    for i in range(3):
        for j in range(2): c.paste(t,(i*t.width,j*t.height))
    return c.resize((c.width*2,c.height*2),Image.NEAREST)
a,b=tuile(v),tuile(p)
c=Image.new("RGB",(a.width*2+60,a.height+60),(36,38,44)); dd=ImageDraw.Draw(c)
c.paste(a,(20,50)); c.paste(b,(a.width+40,50))
dd.text((20,15),"Ciel de l'End vanilla",fill=(200,200,200),font=FB); dd.text((a.width+40,15),"Proposition : bronze, poussière de laiton et d\x27écho",fill=(235,225,200),font=FB)
c.save("ambiance/ciel_end.png")
