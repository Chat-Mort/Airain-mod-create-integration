#!/usr/bin/env python3
"""Nuancier avant/après de l'atmosphère des biomes (couleurs vanilla 1.21.1 -> Empire d'Airain)."""
import colorsys, json, sys
from PIL import Image, ImageDraw, ImageFont
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
h=lambda v:((v>>16)&255,(v>>8)&255,v&255)
# biome : ciel, brouillard, eau, herbe, feuillage  (valeurs vanilla ; herbe/feuillage = colormap au climat du biome)
V={
 "Plaines désertées|plains":(0x78A7FF,0xC0D8FF,0x3F76E4,0x91BD59,0x77AB2F),
 "Désert de rouille|desert":(0x6EB1FF,0xC0D8FF,0x3F76E4,0xBFB755,0xAEA42A),
 "Savane brûlée|savanna":(0x6EB1FF,0xC0D8FF,0x3F76E4,0xBFB755,0xAEA42A),
 "Taïga silencieuse|taiga":(0x7BA5FF,0xC0D8FF,0x3F76E4,0x86B783,0x68A464),
 "Toundra muette|snowy_plains":(0x7FA1FF,0xC0D8FF,0x3F76E4,0x80B497,0x60A17B),
 "Forêt reprise|forest":(0x79A6FF,0xC0D8FF,0x3F76E4,0x79C05A,0x59AE30),
 "Marais des égouts|swamp":(0x78A7FF,0xC0D8FF,0x617B64,0x6A7039,0x6A7039),
 "Jungle envahissante|jungle":(0x77A8FF,0xC0D8FF,0x3F76E4,0x59C93C,0x30BB0B),
 "Vergers du Conseil|cherry_grove":(0x78A7FF,0xC0D8FF,0x5DB7EF,0xB6DB61,0xB6DB61),
 "Terres rouillées|badlands":(0x6EB1FF,0xC0D8FF,0x3F76E4,0x90814D,0x9E814D),
}
def hls(c): r,g,b=[x/255 for x in c]; return colorsys.rgb_to_hls(r,g,b)
def rgb(H,L,S): return tuple(round(x*255) for x in colorsys.hls_to_rgb(H%1,max(0,min(1,L)),max(0,min(1,S))))
def mix(a,b,t): return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
AMBRE=(214,170,110); OLIVE=(128,128,70); VDG=(46,92,84)
def ciel(c):  H,L,S=hls(c); return mix(rgb(H,L*0.95,S*0.45),AMBRE,0.22)
def brume(c): H,L,S=hls(c); return mix(rgb(H,L*0.92,S*0.35),AMBRE,0.30)
def eau(c):   return mix(c,VDG,0.65)
def vert(c):  H,L,S=hls(c); return mix(rgb(H,L*0.92,S*0.70),OLIVE,0.25)
T=[ciel,brume,eau,vert,vert]
COL=["Ciel","Brouillard","Eau","Herbe","Feuillage"]
out={}
SW,SH=78,46; X0=250; W=X0+len(COL)*(2*SW+26)+20; H=110+len(V)*(SH+18)+60
im=Image.new("RGB",(W,H),(30,31,36)); d=ImageDraw.Draw(im)
fT,fL,fS=ImageFont.truetype(FB,22),ImageFont.truetype(FB,14),ImageFont.truetype(F,12)
d.text((20,18),"Atmosphère des biomes · avant (Minecraft) / après (Empire d'Airain)",font=fT,fill=(240,240,240))
for j,c in enumerate(COL):
    x=X0+j*(2*SW+26); d.text((x,64),c,font=fL,fill=(250,220,140))
    d.text((x,84),"avant",font=fS,fill=(170,170,170)); d.text((x+SW+4,84),"après",font=fS,fill=(170,170,170))
for i,(k,vals) in enumerate(V.items()):
    nom,bid=k.split("|"); y=110+i*(SH+18)
    d.text((20,y+6),nom,font=fL,fill=(235,235,235)); d.text((20,y+25),"minecraft:"+bid,font=fS,fill=(150,150,150))
    out[bid]={}
    for j,(v,f) in enumerate(zip(vals,T)):
        a=h(v); b=f(a); x=X0+j*(2*SW+26)
        d.rectangle([x,y,x+SW,y+SH],fill=a); d.rectangle([x+SW+4,y,x+2*SW+4,y+SH],fill=b)
        out[bid][COL[j]]="#%02X%02X%02X"%b
d.text((20,H-40),"Principe : ciel et brume ternis vers l'ambre (poussière), herbe et feuilles vers l'olive, eau assombrie vert-de-gris.",font=fS,fill=(200,200,200))
im.save(sys.argv[1]); json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
