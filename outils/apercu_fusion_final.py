import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
M='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/'
ARBRE={"from":[6,6,0],"to":[10,10,8],"faces":{k:{"texture":"#ax"} for k in ("east","west","up","down")}|{"north":{"texture":"#axt"}}}
def charge(parts, extra=[], niveau=None):
    E=[];Tx={"ax":"create:block/axis","axt":"create:block/axis_top","src":"ars_nouveau:block/source_still"}
    for p in parts:
        d=json.load(open(M+p+'.json'))
        for el in d['elements']:
            for f in el['faces'].values(): f['texture']='#'+p+f['texture'][1:]
        E+=d['elements']; Tx.update({p+k:v for k,v in d['textures'].items()})
    if niveau: E.append({"from":[2,3,2],"to":[14,3+11*niveau,14],"shade":False,"faces":{k:{"texture":"#src","neoforge_data":{}} for k in ("north","south","east","west","up")}})
    return E+extra,Tx
W=Image.new('RGBA',(1440,800),(34,30,38,255)); d=ImageDraw.Draw(W); f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
A=[-1,0.82,-1]; B=[1,0.82,1]
cas=(("Turbine (avant)",A,['echo_turbine','echo_turbine/rotor'],[ARBRE],None),("Turbine (arrière)",B,['echo_turbine','echo_turbine/rotor'],[ARBRE],None),
     ("Sourcelink (avant)",A,['mechanical_sourcelink','mechanical_sourcelink/rotor'],[ARBRE],None),("Sourcelink (arrière)",B,['mechanical_sourcelink','mechanical_sourcelink/rotor'],[],None),
     ("Condenseur : condense, 70 %",A,['echo_condenser_condense'],[],.7),("Condenseur : évapore, 30 %",A,['echo_condenser_evaporate'],[],.3),
     ("Diffuseur éteint",A,['echo_diffuser_off'],[],None),("Diffuseur allumé",A,['echo_diffuser_on'],[],None))
for i,(n,eye,p,x,nv) in enumerate(cas):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    X=(i%4)*360; Y=(i//4)*400
    W.alpha_composite(rendre(*charge(p,x,nv),360,echelle=12.5),(X,Y+36)); d.text((X+180,Y+18),n,font=f,fill=(235,215,170),anchor='mm')
W.save(sys.argv[1])
