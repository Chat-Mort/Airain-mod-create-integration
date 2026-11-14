src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
import shutil,os
MOD='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
tmp='racine_meca/'; os.makedirs(tmp+'textures/block',exist_ok=True)
for f in os.listdir(MOD+'textures/block'):
    if f.endswith('.png'): shutil.copyfile(MOD+'textures/block/'+f,tmp+'textures/block/'+f)
ims=[]
for k in 'AB':
    for p in ('','oxidized_'): shutil.copyfile(f'airain_tex/block/{p}airain_catwalk_meca{k}.png',tmp+f'textures/block/{p}airain_catwalk_mecaX.png')
    rm.RAC['t']=os.path.abspath(tmp)+'/'; rm._cache.clear()
    E=[]
    for x in range(4):
        meca = x==1
        for p,z in (('',0),('oxidized_',2)):
            es=charge(f'{p}airain_catwalk_floor_bottom',(x,0,z))
            if meca:
                for e in es:
                    for f in e['faces'].values():
                        if 'airain_catwalk' in f['texture'] and 'band' not in f['texture']: f['texture']=f'airain:block/{p}airain_catwalk_mecaX'.replace('airain:','t:')
            E+=es+charge(f'{p}airain_catwalk_railing_bottom',(x,0,z),0)+charge(f'{p}airain_catwalk_railing_bottom',(x,0,z),180)
    ims.append(vue(E+sol(range(0,4),range(-1,4)),[-0.5,1.1,0.9],700))
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22)
W=Image.new('RGBA',(max(i.width for i in ims)+40,sum(i.height+50 for i in ims)+20),(34,30,38,255)); d=ImageDraw.Draw(W); y=10
N={'A':'A : caillebotis cerclé de bandes de danger','B':'B : plaque pleine rivetée cerclée de bandes de danger'}
for k,i in zip('AB',ims):
    d.text((20,y),N[k]+" (2e bloc de chaque ligne)",font=fo,fill=(235,215,170)); W.alpha_composite(i,(20,y+40)); y+=i.height+50
# textures seules, en grand
T2=Image.new('RGBA',(2*200+40,220),(34,30,38,255))
for j,k in enumerate('AB'):
    T2.alpha_composite(Image.open(f'airain_tex/block/airain_catwalk_meca{k}.png').convert('RGBA').resize((192,192),0),(20+j*200,14))
W2=Image.new('RGBA',(max(W.width,T2.width),W.height+T2.height),(34,30,38,255)); W2.alpha_composite(W,(0,0)); W2.alpha_composite(T2,(0,W.height)); W2.save('rendu_fusion/sol_meca.png')
