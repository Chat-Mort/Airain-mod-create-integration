import json, copy, sys
from PIL import Image, ImageDraw
import rendu_modele as R
M='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/'
def mod(n): d=json.load(open(M+n+'.json')); return d['elements'], d['textures']
def dec(els,dx=0,dy=0,dz=0):
    out=[]
    for e in els:
        e=copy.deepcopy(e); e['from']=[e['from'][0]+dx,e['from'][1]+dy,e['from'][2]+dz]; e['to']=[e['to'][0]+dx,e['to'][1]+dy,e['to'][2]+dz]; out.append(e)
    return out
def colonne(nom, ax, n=3):
    els=[]; tx={}
    for i in range(n):
        suf='' if n==1 else ('_bottom' if i==0 else '_top' if i==n-1 else '_middle')
        e,t=mod(f'{nom}{suf}_{ax}')
        # chaque bloc a ses propres textures : on les renomme
        k=f'b{i}'; e=copy.deepcopy(e)
        for el in e:
            for f in el['faces'].values(): f['texture']='#'+k+f['texture'][1:]
        for a,b in t.items(): tx[k+a]=b
        d={'y':(0,16*i,0),'x':(16*i,0,0),'z':(0,0,16*i)}[ax]
        els+=dec(e,*d)
    return els,tx
im=Image.new('RGB',(1500,1000),(28,29,34))
for j,nom in enumerate(('white_marble_pillar','black_marble_pillar','slate_pillar')):
    for i,ax in enumerate('yxz'):
        e,t=colonne(nom,ax); r=R.rendre(e,t,taille=320); im.paste(r,(i*330+10,j*330+10),r)
im.save('/tmp/verif_colonnes.png')
def rot180(els):
    sw={'north':'south','south':'north','east':'west','west':'east'}; out=[]
    for e in els:
        e=copy.deepcopy(e); a,b=e['from'],e['to']
        e['from']=[16-b[0],a[1],16-b[2]]; e['to']=[16-a[0],b[1],16-a[2]]
        e['faces']={sw.get(k,k):v for k,v in e['faces'].items()}; out.append(e)
    return out
im=Image.new('RGB',(1400,520),(28,29,34))
b,t=mod('airain_lamppost_base'); m,_=mod('airain_lamppost_mast'); h,th=mod('airain_lamppost_head'); hd,_=mod('weathered_airain_lamppost_head_double')
t=dict(th)
r=R.rendre(b+m+dec(h,dy=16),t,taille=480); im.paste(r,(0,20),r)
_,tw=mod('weathered_airain_lamppost_head_double')
r=R.rendre(b+m+dec(hd,dy=16),tw,taille=480); im.paste(r,(460,20),r)
# cloison + portail ouvert, montants réels
post,tf=mod('airain_mesh_fence_post'); side,_=mod('airain_mesh_fence_side'); st,_=mod('airain_mesh_fence_side_top'); sb,_=mod('airain_mesh_fence_side_bottom')
fr,_=mod('airain_mesh_fence_frame'); frm,_=mod('airain_mesh_fence_frame_mirror')
cn=side+st+sb; cs=rot180(cn)
els=dec(post+cn+cs+rot180(frm),dz=0)+dec(post+cn+cs+fr,dz=32)+dec(post+cn+cs,dz=-16)+dec(post+cn+cs,dz=48)
els+=dec([R and {'from':[9.75,0,0],'to':[10.25,16,16],'faces':{k:{'texture':'#g'} for k in ('east','west')}}],dz=48)
r=R.rendre(els,tf,taille=480); im.paste(r,(920,20),r)
im.save('/tmp/verif_lampe.png')
