import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
rm.RAC['t']='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_root/'
def box(fr,to,tex,faces=("north","south","east","west","up","down"),uvfull=False):
    f={k:{"texture":tex}|({"uv":[0,0,16,16]} if uvfull else {}) for k in faces}
    return {"from":fr,"to":to,"faces":f}
def deplace(e,p):
    for i in range(3): e['from'][i]+=p[i]*16; e['to'][i]+=p[i]*16
    for f in e['faces'].values():
        if 'uv' not in f:
            # uv selon la position dans le bloc d'origine
            pass
    return e
E=[]
S=['','exposed_','weathered_','oxidized_']
import copy
def bloc_at(p,tex):
    return {"from":[p[0]*16,p[1]*16,p[2]*16],"to":[p[0]*16+16,p[1]*16+16,p[2]*16+16],"faces":{k:{"texture":tex,"uv":[0,0,16,16]} for k in ("north","south","east","west","up","down")}}
def escalier(p,tex):
    x,y,z=[v*16 for v in p]
    return [{"from":[x,y,z],"to":[x+16,y+8,z+16],"faces":{k:{"texture":tex,"uv":uv} for k,uv in (("north",[0,8,16,16]),("south",[0,8,16,16]),("east",[0,8,16,16]),("west",[0,8,16,16]),("up",[0,0,16,16]),("down",[0,0,16,16]))}},
            {"from":[x,y+8,z+8],"to":[x+16,y+16,z+16],"faces":{k:{"texture":tex,"uv":uv} for k,uv in (("north",[0,0,16,8]),("south",[0,0,16,8]),("east",[0,0,8,8]),("west",[8,0,16,8]),("up",[0,8,16,16]))}}]
def dalle(p,tex):
    x,y,z=[v*16 for v in p]
    return [{"from":[x,y,z],"to":[x+16,y+8,z+16],"faces":{k:{"texture":tex,"uv":uv} for k,uv in (("north",[0,8,16,16]),("south",[0,8,16,16]),("east",[0,8,16,16]),("west",[0,8,16,16]),("up",[0,0,16,16]),("down",[0,0,16,16]))}}]
def muret(p,tex):
    x,y,z=[v*16 for v in p]
    return [{"from":[x+4,y,z+4],"to":[x+12,y+16,z+12],"faces":{k:{"texture":tex,"uv":uv} for k,uv in (("north",[4,0,12,16]),("south",[4,0,12,16]),("east",[4,0,12,16]),("west",[4,0,12,16]),("up",[4,4,12,12]))}}]
def barreaux(p,tex):
    x,y,z=[v*16 for v in p]
    return [{"from":[x,y,z+7],"to":[x+16,y+16,z+9],"faces":{k:{"texture":tex,"uv":[0,0,16,16]} for k in ("north","south")}}]
for i,pre in enumerate(S):
    x=i*2
    t='t:block/'+pre+'airain_bricks'
    E.append(bloc_at((x,0,0),t)); E.append(bloc_at((x,1,0),t)); E+=escalier((x,0,-1),t); E+=dalle((x+1,0,0),t); E+=muret((x,2,0),t)
    E+=barreaux((x+1,0,1),'t:block/'+pre+'airain_bars'); E+=barreaux((x+1,1,1),'t:block/'+pre+'airain_bars')
rm.EYE=norm([-0.6,0.6,-1]); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
im=rendre(E,{},900); W=Image.new('RGBA',im.size,(34,30,38,255)); W.alpha_composite(im); W.crop((0,150,900,750)).save(sys.argv[1])
