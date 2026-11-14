import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
rm.RAC['t']='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_root/'
def cube(pos,side,top=None):
    x,y,z=[v*16 for v in pos]
    f={k:{"texture":'t:block/'+side,"uv":[0,0,16,16]} for k in ("north","south","east","west")}
    f["up"]={"texture":'t:block/'+(top or side),"uv":[0,0,16,16]}; f["down"]=f["up"]
    return {"from":[x,y,z],"to":[x+16,y+16,z+16],"faces":f}
E=[]
S=['','exposed_','weathered_','oxidized_']
# un petit portique : socle taillé, piliers, frise ciselée, mur riveté, grille
for i,p in enumerate(S):
    x=i*2
    E.append(cube((x,0,0),p+'cut_airain'))
    E.append(cube((x,1,0),p+'airain_pillar',p+'airain_pillar_top')); E.append(cube((x,2,0),p+'airain_pillar',p+'airain_pillar_top'))
    E.append(cube((x,3,0),p+'chiseled_airain'))
    E.append(cube((x+1,0,1),p+'riveted_airain')); E.append(cube((x+1,1,1),p+'airain_block')); E.append(cube((x+1,2,1),p+'airain_grate')); E.append(cube((x+1,3,1),p+'riveted_airain'))
rm.EYE=norm([-0.55,0.5,-1]); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
im=rendre(E,{},900)
W=Image.new('RGBA',(900,700),(34,30,38,255)); W.alpha_composite(im.crop((0,100,900,800)),(0,0))
W.save(sys.argv[1])
