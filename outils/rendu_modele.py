# Rendu isométrique (z-buffer) d'un modèle de bloc JSON Minecraft, textures comprises.
import json, math, numpy as np
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/'
RAC={'create':S+'create-src/src/main/resources/assets/create/','ars_nouveau':S+'ars_new/src/main/resources/assets/ars_nouveau/',
     'minecraft':S+'mcmeta-assets/assets/minecraft/','airain':'/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'}
_cache={}
def tex(rl):
    if rl in _cache: return _cache[rl]
    ns,p=rl.split(':') if ':' in rl else ('minecraft',rl)
    im=Image.open(RAC[ns]+'textures/'+p+'.png').convert('RGBA'); w=im.width
    im=im.crop((0,0,w,w)); a=np.asarray(im).astype(float)/255; _cache[rl]=a; return a
def norm(v): v=np.array(v,float); return v/np.linalg.norm(v)
EYE=norm([-1,0.82,-1.0])   # regard depuis le nord-ouest, au-dessus
F=-EYE; R=norm(np.cross(F,[0,1,0])); U=np.cross(R,F)
SH={'up':1,'down':.5,'north':.8,'south':.8,'east':.6,'west':.6}
def faces_el(e):
    x1,y1,z1=e['from']; x2,y2,z2=e['to']
    D={'north':((x2,y2,z1),(-1,0,0),(0,-1,0),(0,0,-1),[16-x2,16-y2,16-x1,16-y1],x2-x1,y2-y1),
       'south':((x1,y2,z2),(1,0,0),(0,-1,0),(0,0,1),[x1,16-y2,x2,16-y1],x2-x1,y2-y1),
       'west':((x1,y2,z1),(0,0,1),(0,-1,0),(-1,0,0),[z1,16-y2,z2,16-y1],z2-z1,y2-y1),
       'east':((x2,y2,z2),(0,0,-1),(0,-1,0),(1,0,0),[16-z2,16-y2,16-z1,16-y1],z2-z1,y2-y1),
       'up':((x1,y2,z1),(1,0,0),(0,0,1),(0,1,0),[x1,z1,x2,z2],x2-x1,z2-z1),
       'down':((x1,y1,z2),(1,0,0),(0,0,-1),(0,-1,0),[x1,16-z2,x2,16-z1],x2-x1,z2-z1)}
    rot=e.get('rotation')
    for k,f in e['faces'].items():
        o,du,dv,n,uv,lu,lv=D[k]; o=np.array(o,float); du=np.array(du,float)*lu; dv=np.array(dv,float)*lv; n=np.array(n,float)
        if rot:
            a=math.radians(rot['angle']); c,s=math.cos(a),math.sin(a); org=np.array(rot['origin'],float)
            ax=rot['axis']
            M={'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
            o=M@(o-org)+org; du=M@du; dv=M@dv; n=M@n
        yield o,du,dv,n,f.get('uv',uv),f['texture'],SH[k] if e.get('shade',True) else 1.0, 'neoforge_data' in f
def rendre(elements, textures, taille=360, echelle=None, decal=(0,0,0)):
    pts=[]
    faces=[]
    for e in elements:
        for o,du,dv,n,uv,t,sh,lum in faces_el(e):
            if np.dot(n,F)>=0: continue
            o=o+np.array(decal,float)
            t=t[1:] if t.startswith('#') else t
            while t in textures and not str(textures[t]).count(':') and t!=textures[t]: t=textures[t].lstrip('#')
            faces.append((o-8,du,dv,uv,textures.get(t,t),sh,lum))
            for q in (o,o+du,o+dv,o+du+dv): pts.append(q-8)
    P=np.array(pts); X=P@R; Y=-(P@U)
    if echelle is None: echelle=taille*0.78/max(X.max()-X.min(),Y.max()-Y.min())
    cx=(X.max()+X.min())/2; cy=(Y.max()+Y.min())/2
    img=np.zeros((taille,taille,4)); zb=np.full((taille,taille),1e9)
    yy,xx=np.mgrid[0:taille,0:taille]
    for o,du,dv,uv,t,sh,lum in faces:
        T=tex(t); h=T.shape[0]
        A=np.array([[du@R,dv@R],[-(du@U),-(dv@U)]])*echelle
        if abs(np.linalg.det(A))<1e-6: continue
        o2=np.array([(o@R-cx)*echelle+taille/2,(-(o@U)-cy)*echelle+taille/2])
        Ai=np.linalg.inv(A)
        cs=[o2,o2+A[:,0],o2+A[:,1],o2+A[:,0]+A[:,1]]
        x0=int(max(0,min(c[0] for c in cs)));x1=int(min(taille-1,max(c[0] for c in cs))+1)
        y0=int(max(0,min(c[1] for c in cs)));y1=int(min(taille-1,max(c[1] for c in cs))+1)
        sx=xx[y0:y1,x0:x1]+.5-o2[0]; sy=yy[y0:y1,x0:x1]+.5-o2[1]
        a=Ai[0,0]*sx+Ai[0,1]*sy; b=Ai[1,0]*sx+Ai[1,1]*sy
        m=(a>=0)&(a<1)&(b>=0)&(b<1)
        u=uv[0]+(uv[2]-uv[0])*a; v=uv[1]+(uv[3]-uv[1])*b
        tu=np.clip((u/16*h).astype(int),0,h-1); tv=np.clip((v/16*h).astype(int),0,h-1)
        col=T[tv,tu]
        p3=o[None,None,:]+a[...,None]*du+b[...,None]*dv
        z=p3@F
        m&=col[...,3]>.1
        zs=zb[y0:y1,x0:x1]; m&=z<zs
        c=col.copy(); c[...,:3]*= (1.0 if lum else sh)
        reg=img[y0:y1,x0:x1]; reg[m]=c[m]; zs[m]=z[m]
    out=Image.fromarray((np.clip(img,0,1)*255).astype('uint8'),'RGBA')
    return out
def modele(chemin):
    d=json.load(open(chemin)); return d['elements'],d['textures']
