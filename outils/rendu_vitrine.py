import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
rm.RAC['t']='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_root/'
ALL=("north","south","east","west","up","down")
def el(p,fr,to,tex,uvs=None,faces=ALL,rot=None):
    o=[v*16 for v in p]
    f={}
    for k in faces:
        t=tex[k] if isinstance(tex,dict) else tex
        f[k]={"texture":t,"uv":(uvs[k] if isinstance(uvs,dict) else uvs) if uvs else None}
        if f[k]["uv"] is None:
            x1,y1,z1=fr; x2,y2,z2=to
            f[k]["uv"]={"north":[16-x2,16-y2,16-x1,16-y1],"south":[x1,16-y2,x2,16-y1],"west":[z1,16-y2,z2,16-y1],"east":[16-z2,16-y2,16-z1,16-y1],"up":[x1,z1,x2,z2],"down":[x1,16-z2,x2,16-z1]}[k]
    e={"from":[fr[i]+o[i] for i in range(3)],"to":[to[i]+o[i] for i in range(3)],"faces":f}
    if rot: e["rotation"]={"origin":[rot[0][i]+o[i] for i in range(3)],"axis":rot[1],"angle":rot[2]}
    return e
def cube(p,side,top=None): return el(p,[0,0,0],[16,16,16],{**{k:side for k in ALL[:4]},"up":top or side,"down":top or side})
def vitrine(pre,z):
    b=lambda n:'t:block/'+pre+n
    E=[cube((0,0,z),b('airain_block')),cube((1,0,z),b('cut_airain')),cube((2,0,z),b('riveted_airain')),cube((3,0,z),b('chiseled_airain')),
       cube((4,0,z),b('airain_pillar'),b('airain_pillar_top')),cube((4,1,z),b('airain_pillar'),b('airain_pillar_top')),
       cube((5,0,z),b('airain_grate'))]
    # escaliers (airain lisse) et dalle (taillé)
    E+=[el((6,0,z),[0,0,0],[16,8,16],b('airain_block')),el((6,0,z),[0,8,8],[16,16,16],b('airain_block')),
        el((7,0,z),[0,0,0],[16,8,16],b('cut_airain'))]
    # porte (deux blocs), barreaux, trappe, lanterne et chaîne
    E+=[el((8,0,z),[0,0,13],[16,16,16],b('airain_door_bottom'),uvs=[0,0,16,16]),el((8,1,z),[0,0,13],[16,16,16],b('airain_door_top'),uvs=[0,0,16,16])]
    for y in (0,1): E.append(el((9,y,z),[0,0,7],[16,16,9],b('airain_bars'),faces=("north","south"),uvs=[0,0,16,16]))
    E.append(el((10,0,z),[0,0,0],[16,3,16],b('airain_trapdoor'),uvs={"up":[0,0,16,16],"down":[0,0,16,16],"north":[0,0,16,3],"south":[0,0,16,3],"east":[0,0,16,3],"west":[0,0,16,3]}))
    L=b('airain_lantern')
    E+=[el((11,0,z),[5,0,5],[11,7,11],L,uvs={"north":[0,2,6,9],"south":[0,2,6,9],"east":[0,2,6,9],"west":[0,2,6,9],"up":[0,9,6,15],"down":[0,9,6,15]}),
        el((11,0,z),[6,7,6],[10,9,10],L,uvs={"north":[1,0,5,2],"south":[1,0,5,2],"east":[1,0,5,2],"west":[1,0,5,2],"up":[1,10,5,14],"down":[1,10,5,14]})]
    C=b('airain_chain')
    for y in (0,1,2):
        E+=[el((12,y,z),[6.5,0,8],[9.5,16,8],C,faces=("north","south"),uvs=[0,0,3,16],rot=([8,8,8],'y',45)),
            el((12,y,z),[8,0,6.5],[8,16,9.5],C,faces=("east","west"),uvs=[3,0,6,16],rot=([8,8,8],'y',45))]
    return E
E=[]
MODE=sys.argv[2] if len(sys.argv)>2 else 'tous'
if MODE=='tous':
    for s,pre in enumerate(['','exposed_','weathered_','oxidized_']): E+=vitrine(pre,s*2)
else:
    E=vitrine(MODE if MODE!='neuf' else '',0)
    # espacer les objets : chaque colonne x devient x*1.6
    for e in E:
        cx=(e['from'][0]//16)
        for k in ('from','to'): e[k][0]+=cx*16*0.6
        if 'rotation' in e: e['rotation']['origin'][0]+=cx*16*0.6
rm.EYE=norm([-0.45,0.55,-1]); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
im=rendre(E,{},1600); W=Image.new('RGBA',im.size,(34,30,38,255)); W.alpha_composite(im); W=W.crop((0,350,1600,1250)) if MODE=='tous' else W.crop((0,450,1600,1150))
d=ImageDraw.Draw(W); f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
W.save(sys.argv[1])
