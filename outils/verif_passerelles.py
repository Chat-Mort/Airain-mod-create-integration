# Rend les vrais modèles JSON générés (blockstates multipart simulés) pour vérifier orientation et raccords.
import sys, json, math, copy; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
MD='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/'
def charge(nom, pos, y=0):
    d=json.load(open(MD+nom+'.json')); E=copy.deepcopy(d['elements']); T=d['textures']
    out=[]
    for e in E:
        r=e.get('rotation')
        if r and r.get('rescale'):
            c=1/math.cos(math.radians(abs(r['angle'])))
            ax={'x':(1,2),'y':(0,2),'z':(0,1)}[r['axis']]
            for i in ax:
                o=r['origin'][i]; e['from'][i]=o+(e['from'][i]-o)*c; e['to'][i]=o+(e['to'][i]-o)*c
        # rotation y du blockstate (autour du centre), par pas de 90°
        for _ in range(y//90):
            fr,to=e['from'],e['to']
            nf=[16-to[2],fr[1],fr[0]]; nt=[16-fr[2],to[1],to[0]]
            e['from'],e['to']=nf,nt
            if r:
                o=r['origin']; r['origin']=[16-o[2],o[1],o[0]]
                if r['axis']=='x': r['axis']='z'
                elif r['axis']=='z': r['axis']='x'; r['angle']=-r['angle']
            fc={}
            m={'north':'east','east':'south','south':'west','west':'north','up':'up','down':'down'}
            for k,v in e['faces'].items(): fc[m[k]]=v
            e['faces']=fc
        for i in range(3): e['from'][i]+=pos[i]*16; e['to'][i]+=pos[i]*16
        if r: r['origin']=[r['origin'][i]+pos[i]*16 for i in range(3)]
        for f in e['faces'].values():
            t=f['texture'].lstrip('#'); f['texture']=T.get(t,t).replace('airain:','t:')
        out.append(e)
    return out
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
E=[]
# passerelle basse (rambardes ouest, sud) → escalier vers le nord → passerelle en haut (rambardes nord, est, ouest)
E+=charge('airain_catwalk_floor_bottom',(0,0,2))+charge('airain_catwalk_railing_bottom',(0,0,2),270)+charge('airain_catwalk_railing_bottom',(0,0,2),180)+charge('airain_catwalk_railing_bottom',(0,0,2),90)
E+=charge('airain_catwalk_stairs',(0,0,1))+charge('airain_catwalk_stairs_left',(0,0,1))+charge('airain_catwalk_stairs_right',(0,0,1))
E+=charge('airain_catwalk_floor_bottom',(0,1,0))+charge('airain_catwalk_railing_bottom',(0,1,0),0)+charge('airain_catwalk_railing_bottom',(0,1,0),90)+charge('airain_catwalk_railing_bottom',(0,1,0),270)
E+=charge('airain_support',(0,0,0))+charge('airain_support_bottom',(0,0,0))+charge('airain_support_top',(0,0,0))
# rampe vers l'est + portillon
E+=charge('airain_catwalk_floor_bottom',(2,0,2))+charge('airain_catwalk_gate_bottom',(2,0,2),180)+charge('airain_catwalk_gate_open_bottom',(2,0,2),0)
E+=charge('airain_catwalk_ramp_bottom',(3,0,2),90)+charge('airain_catwalk_ramp_left_bottom',(3,0,2),90)+charge('airain_catwalk_ramp_right_bottom',(3,0,2),90)
E+=charge('airain_catwalk_floor_top',(4,0,2))+charge('airain_catwalk_railing_top',(4,0,2),0)+charge('airain_catwalk_railing_top',(4,0,2),180)
E+=charge('airain_ladder',(2,0,0))+charge('airain_ladder',(2,1,0))+charge('airain_ladder',(2,2,0))+charge('airain_ladder_cage',(2,2,0))
rm.EYE=norm([-0.7,0.7,1]); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
im=rendre(E,{},1400); im=im.crop(im.getbbox()); W=Image.new('RGBA',(im.width+40,im.height+40),(34,30,38,255)); W.alpha_composite(im,(20,20)); W.save(sys.argv[1])
