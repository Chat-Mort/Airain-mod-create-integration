import shutil
src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
MOD='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
import os, tempfile
ims=[]
for k in ('actuel','A','B'):
    tmp='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/racine_croix/'
    os.makedirs(tmp+'textures/block',exist_ok=True)
    for f in os.listdir(MOD): shutil.copyfile(MOD+f,tmp+'textures/block/'+f) if f.endswith('.png') else None
    if k!='actuel':
        for p in ('','oxidized_'): shutil.copyfile(f'airain_tex/block/{p}airain_catwalk_croix{k}.png',tmp+f'textures/block/{p}airain_catwalk.png')
    rm.RAC['t']=tmp; rm._cache.clear()
    E=[]
    for x in range(2): E+=charge('airain_catwalk_floor_bottom',(x,0,1))+charge('airain_catwalk_railing_bottom',(x,0,1),180)
    E+=charge('airain_catwalk_stairs',(2,0,1),90)+charge('airain_catwalk_stairs_left',(2,0,1),90)
    E+=charge('oxidized_airain_catwalk_floor_bottom',(3,1,1))+charge('oxidized_airain_catwalk_railing_bottom',(3,1,1),180)+charge('oxidized_airain_catwalk_ramp_bottom',(4,1,1),90)
    E+=cube((3,0,1))+cube((4,0,1))
    ims.append((k,vue(E+sol(range(0,5),range(1,2)),[-0.5,0.8,1],700)))
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
W=Image.new('RGBA',(max(i.width for _,i in ims)+40,sum(i.height+50 for _,i in ims)+20),(34,30,38,255)); y=10; d=ImageDraw.Draw(W)
N={'actuel':'Actuel (lignes droites)','A':'A : croisillons fins, comme la grille','B':'B : croisillons épaissis (barreau + ombre)'}
for k,i in ims:
    d.text((20,y),N[k],font=fo,fill=(235,215,170)); W.alpha_composite(i,(20,y+40)); y+=i.height+50
W.save('rendu_fusion/croix.png')
