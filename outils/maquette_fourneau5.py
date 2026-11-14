src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
import copy
from PIL import ImageChops
# ---- plan du fourneau B (local : lx -2..2, lz 0 avant..4, ly 0..4) ; ici avant = nord, x = lx+2, z = lz
def emprise(ly):
    if ly<=1: return {(x,z) for x in range(-2,3) for z in range(5) if not (abs(x)==2 and z in (0,4))}
    return {(x,z) for x in range(-1,2) for z in range(1,4)}
PART={0:'base',1:'crown',2:'base',3:'body',4:'crown'}
ROTC={('north','west'):0,('north','east'):90,('east','south'):180,('south','west'):270}
def plan():
    P=[]   # (lx,ly,lz, modele, rot)
    for ly in range(5):
        F=emprise(ly)
        for (x,z) in F:
            interieur = (ly<=1 and abs(x)<=1 and 1<=z<=3) or (ly>=2 and x==0 and z==2)
            if (x,ly,z)==(0,0,0): P.append((x,ly,z,'blast_furnace_taphole',0)); continue
            if (x,ly,z)==(0,0,2): P.append((x,ly,z,'airain_grate',0)); continue
            if (x,ly,z)==(0,4,2): P.append((x,ly,z,'blast_furnace_hopper',0)); continue
            if (x,ly,z)==(2,1,2): P.append((x,ly,z,'blast_furnace_tuyere',90)); continue
            if interieur:
                if ly==0: P.append((x,ly,z,'fire_bricks_none',0))
                continue
            ex=[d for d,(dx,dz) in (('north',(0,-1)),('south',(0,1)),('east',(1,0)),('west',(-1,0))) if (x+dx,z+dz) not in F]
            if (x,ly,z)==(0,3,1): P.append((x,ly,z,'fire_bricks_emblem',0)); continue
            if len(ex)==2:
                k=tuple(sorted(ex,key=lambda d:['north','east','south','west'].index(d)))
                k={('north','west'):('north','west'),('north','east'):('north','east'),('east','south'):('east','south'),('south','west'):('south','west')}[k]
                P.append((x,ly,z,f'fire_bricks_{PART[ly]}_corner',ROTC[k]))
            else: P.append((x,ly,z,f'fire_bricks_{PART[ly]}',0))
    return P
def chargel(m,pos,r):
    es=charge(m,(0,0,0),r)
    for e in es:
        (x1,y1,z1),(x2,y2,z2)=e['from'],e['to']
        D={'north':[16-x2,16-y2,16-x1,16-y1],'south':[x1,16-y2,x2,16-y1],'west':[z1,16-y2,z2,16-y1],'east':[16-z2,16-y2,16-z1,16-y1],'up':[x1,z1,x2,z2],'down':[x1,16-z2,x2,16-z1]}
        for k,f in e['faces'].items(): f.setdefault('uv',D[k])
        for i in range(3): e['from'][i]+=pos[i]*16; e['to'][i]+=pos[i]*16
        if e.get('rotation'): e['rotation']['origin']=[e['rotation']['origin'][i]+pos[i]*16 for i in range(3)]
    return es
def elems(P,fantome=False):
    E=[]
    for (x,ly,z,m,r) in P:
        es=cube((x+3,ly,z+1)) if m=='fire_bricks_none' else cube((x+3,ly,z+1),'t:block/airain_grate') if m=='airain_grate' else chargel(m,(x+3,ly,z+1),r)
        if fantome:
            for e in es:
                for f in e['faces'].values(): f['texture']='t:block/_vide_maquette'
        E+=es
    return E
P=plan(); print(len(P),'pièces', sum(1 for p in P if 'fire_bricks' in p[3]),'briques')
EYES=([-0.75,0.75,-1],[1,0.6,-0.55])
ims=[]
SOL=sol(range(0,7),range(0,7))
for eye in EYES: ims.append(vue(elems(P)+SOL,eye,900))
# ---- en construction : couche 0 + moitié de la couche 1 posées, le reste en hologramme
pose=[p for p in P if p[1]==0 or (p[1]==1 and p[0]<=0)]
reste=[p for p in P if p not in pose]
def rendu_fixe(E,eye,taille=1000):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    return rendre(E,{},taille)
eye=[-0.75,0.75,-1]
A=rendu_fixe(elems(pose)+elems(reste)+SOL,eye)           # tout opaque
B=rendu_fixe(elems(pose)+elems(reste,True)+SOL,eye)      # hologramme invisible (même échelle)
a=np.asarray(A).astype(float); b=np.asarray(B).astype(float)
diff=(np.abs(a-b).sum(-1)>3)
g=a.copy(); lum=a[...,:3].mean(-1,keepdims=True)
g[...,:3]=lum*np.array([0.55,0.85,1.15])+np.array([20,40,70])          # fantôme bleuté
o=b.copy(); al=0.42
o[diff,:3]=b[diff,:3]*(1-al)+g[diff,:3]*al; o[diff,3]=255
# liseré clair sur les arêtes du fantôme
C=Image.fromarray(np.clip(o,0,255).astype('uint8'),'RGBA'); C=C.crop(C.getbbox()); ims.append(C)
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
T=["Haut-fourneau B monté (5 × 5 × 5) : creuset 5 × 5 à coins coupés, cuve 3 × 3, gueulard","Vue de côté : la tuyère (ventilateur ici) au milieu d'une face du creuset","En construction : clic droit main nue sur le trou de coulée → hologramme des blocs manquants"]
W=Image.new('RGBA',(max(i.width for i in ims)+40,sum(i.height+60 for i in ims)+20),(34,30,38,255)); d=ImageDraw.Draw(W); y=10
for t,i in zip(T,ims): d.text((20,y),t,font=fo,fill=(235,215,170)); W.alpha_composite(i,(20,y+45)); y+=i.height+60
W.save('rendu_fusion/fourneau5.png'); print(W.size)
