import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
from rendu_modele import *
M='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/'
ARBRE={"from":[6,6,-0.01],"to":[10,10,8],"faces":{k:{"texture":"create:block/axis"} for k in ("east","west","up","down")}|{"north":{"texture":"create:block/axis_top"}}}
def avec_arbre(m):
    e,t=modele(M+m+'.json'); return e+[ARBRE],t
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
cases=[("Turbine d'Écho",*avec_arbre('echo_turbine')),("Sourcelink mécanique",*avec_arbre('mechanical_sourcelink')),
       ("Diffuseur d'Écho (éteint)",*modele(M+'echo_diffuser_off.json')),("Diffuseur d'Écho (allumé)",*modele(M+'echo_diffuser_on.json')),
       ("Condenseur (condense)",*modele(M+'echo_condenser_condense.json')),("Condenseur (évapore)",*modele(M+'echo_condenser_evaporate.json'))]
T=360; W=Image.new('RGBA',(T*3,(T+40)*2+260),(34,30,38,255)); d=ImageDraw.Draw(W)
f=ImageFont.truetype(FB,20); f2=ImageFont.truetype(FR,17)
# même échelle pour tous les blocs : on compare les tailles
for i,(nom,e,t) in enumerate(cases):
    im=rendre(e,t,T,echelle=13.5)
    x=(i%3)*T; y=(i//3)*(T+40)
    W.alpha_composite(im,(x,y+30)); d.text((x+T/2,y+14),nom,font=f,fill=(235,215,170),anchor='mm')
# objets et liquide
y=(T+40)*2+10
from PIL import Image as I
A='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
liq=I.fromarray((tex('ars_nouveau:block/source_still')*255).astype('uint8'),'RGBA').resize((16,16))
import numpy as np
a=np.asarray(liq).astype(float); a[...,0]*=0xB9/255; a[...,1]*=0x8A/255; a[...,2]*=0xFF/255; liq=I.fromarray(a.astype('uint8'),'RGBA')
for j,(nom,im) in enumerate((("Glyphe de l'engrenage",I.open(A+'glyph_gear.png')),("Seau d'Écho liquide",I.open(A+'liquid_echo_bucket.png')),("Écho liquide",liq))):
    x=j*T+T//2-96; W.alpha_composite(im.convert('RGBA').resize((192,192),0),(x,y+40)); d.text((j*T+T/2,y+18),nom,font=f,fill=(235,215,170),anchor='mm')
W.save(sys.argv[1])
