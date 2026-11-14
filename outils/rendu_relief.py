import sys, copy; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
from airain_relief import *
rm.RAC['t']='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_root/'
F=("north","south","east","west","up","down")
def bloc(nom, pos, pre=''):
    if nom=='airain_pillar':
        E=modele({**{f:masque_cannelures() for f in F[:4]},"up":masque_pilier_dessus(),"down":masque_pilier_dessus()},
                 {**{f:'#'+pre+'airain_pillar' for f in F[:4]},"up":'#'+pre+'airain_pillar_top',"down":'#'+pre+'airain_pillar_top'})
    else:
        m={'chiseled_airain':masque_cisele,'cut_airain':masque_taille,'riveted_airain':masque_rivete}.get(nom,plat)
        E=modele({f:m() for f in F},{f:'#'+pre+nom for f in F})
    E=copy.deepcopy(E)
    for e in E:
        for i in range(3): e['from'][i]+=pos[i]*16; e['to'][i]+=pos[i]*16
        for f in e['faces'].values():
            f.setdefault('uv',[0,0,16,16])
    return E
T={}
for pre in ('','exposed_','weathered_','oxidized_'):
    for n in ('chiseled_airain','cut_airain','riveted_airain','airain_pillar','airain_pillar_top','airain_block'): T[pre+n]='t:block/'+pre+n
E=[]
for i,pre in enumerate(('','weathered_')):
    z=i*3
    E+=bloc('cut_airain',(0,0,z),pre)+bloc('airain_pillar',(0,1,z),pre)+bloc('airain_pillar',(0,2,z),pre)+bloc('chiseled_airain',(0,3,z),pre)
    E+=bloc('riveted_airain',(1,0,z+1),pre)+bloc('riveted_airain',(1,1,z+1),pre)+bloc('chiseled_airain',(1,2,z+1),pre)+bloc('cut_airain',(1,3,z+1),pre)
rm.EYE=norm([-1,0.55,-0.75]); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
rendre(E,T,900).save(sys.argv[1])
