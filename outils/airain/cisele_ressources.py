# Airain ciselé d'après la retouche de Liam (stade vieilli) : on retrouve la « carte » de teintes de chaque pixel,
# puis on la rend aux quatre stades par la même chaîne que les autres textures (teinte de l'airain, puis rouge cramoisi).
import colorsys, sys, json, os
import numpy as np
from PIL import Image
S='/home/claude/maquettes/outils/'
os.chdir(S)
exec(open(S+'airain_luxe.py').read().split("STADES=['','exposed_'")[0])
T_=[0.0,0.28,0.58,0.92]
CRAMOISI={1:(-5,1.08,0.98),2:(-14,1.2,0.92),3:(-21,1.4,0.82)}
def chaine(v,s):
    a=int(min(5,max(0,np.floor(v)))); f=v-a
    c=melange(teinte(a,T_[s]),teinte(a+1,T_[s]),f)
    if s==0: return c
    dh,ks,kv=CRAMOISI[s]
    h,sa,vv=colorsys.rgb_to_hsv(c[0]/255,c[1]/255,c[2]/255)
    if sa<0.08: return c
    h=(h+dh/360)%1; sa=min(1,sa*ks); vv=min(1,vv*kv)
    R,G,B=colorsys.hsv_to_rgb(h,sa,vv); return (int(R*255+.5),int(G*255+.5),int(B*255+.5))
V=np.arange(0,6.001,0.01)
LUT=np.array([chaine(v,2) for v in V],float)
src=Image.open('/home/claude/airain-mod-create-integration/outils/retouches_liam/block/weathered_chiseled_airain.png').convert('RGBA'); px=src.load()
GEAR=(0x61,0x0f,0x13)
carte=[[0.0]*16 for _ in range(16)]; err=0; masque=[[False]*16 for _ in range(16)]
for y in range(16):
    for x in range(16):
        c=np.array(px[x,y][:3],float); k=int(np.argmin(((LUT-c)**2).sum(1))); carte[y][x]=float(V[k]); err=max(err,np.sqrt(((LUT[k]-c)**2).sum()))
        masque[y][x]=(0<x<15 and 0<y<15 and px[x,y][:3]==GEAR)
print('écart max', round(err,1))
json.dump({'carte':carte,'masque':masque},open('/home/claude/maquettes/cisele/carte.json','w'))

# ---------------------------------------------------------------- rendu des quatre stades, engrenage creusé d'un pixel
import hashlib
M='/home/claude/airain-mod-create-integration/'
TB=M+'src/main/resources/assets/airain/textures/block/'; MD=M+'src/main/resources/assets/airain/models/block/'
PRE=['','exposed_','weathered_','oxidized_']
def borne(v): return max(0,min(255,int(round(v))))
manif_p=M+'outils/rouge_imperial.json'; manif=json.load(open(manif_p))
for s,p in enumerate(PRE):
    plein=Image.new('RGBA',(16,16)); relief=Image.new('RGBA',(16,16),(0,0,0,0)); fond=Image.new('RGBA',(16,16))
    q=plein.load(); r=relief.load(); f=fond.load()
    for y in range(16):
        for x in range(16):
            base=np.array(chaine(carte[y][x],2),float); ici=np.array(chaine(carte[y][x],s),float)
            c=tuple(borne(v) for v in ici+(np.array(px[x,y][:3],float)-base))      # l'écart de Liam au ton de base est gardé
            if s==2: c=px[x,y][:3]                                                  # son stade : ses pixels tels quels
            q[x,y]=c+(255,)
            if not masque[y][x]: r[x,y]=c+(255,)
    eng=q[3,4][:3]                                                                  # couleur unie de l'engrenage
    for y in range(16):
        for x in range(16):
            f[x,y]=(eng+(255,)) if masque[y][x] else tuple(int(v*0.62) for v in eng)+(255,)   # fond du creux : ombre plus sombre
    if s!=2: plein.save(TB+p+'chiseled_airain.png')
    else: import shutil; shutil.copyfile(M+'outils/retouches_liam/block/weathered_chiseled_airain.png',TB+p+'chiseled_airain.png')   # la retouche de Liam, telle quelle
    relief.save(TB+p+'chiseled_airain_relief.png'); fond.save(TB+p+'chiseled_airain_inner.png')
    for n in ('chiseled_airain','chiseled_airain_relief','chiseled_airain_inner'):
        if p: manif['block/'+p+n+'.png']=hashlib.sha1(open(TB+p+n+'.png','rb').read()).hexdigest()   # déjà au rouge cramoisi
    # modèle : faces percées à l'engrenage, et un cube intérieur un pixel en retrait
    T=f'airain:block/{p}chiseled_airain'
    # fond du creux : six plans pleine largeur, un pixel sous chaque face (rien ne se voit au travers, même de biais)
    PL={'north':([0,0,1],[16,16,1]),'south':([0,0,15],[16,16,15]),'west':([1,0,0],[1,16,16]),'east':([15,0,0],[15,16,16]),'down':([0,1,0],[16,1,16]),'up':([0,15,0],[16,15,16])}
    fonds=[{"from":a,"to":b,"faces":{k:{"texture":"#creux","uv":[0,0,16,16]}}} for k,(a,b) in PL.items()]
    faces=lambda t,cull,uv: {k:{"texture":t,"uv":uv}|({"cullface":k} if cull else {}) for k in ("north","south","east","west","up","down")}
    json.dump({"parent":"minecraft:block/block","render_type":"minecraft:cutout","textures":{"particle":T,"relief":T+'_relief',"creux":T+'_inner'},
               "elements":[{"from":[0,0,0],"to":[16,16,16],"faces":faces('#relief',True,[0,0,16,16])},]+fonds},
              open(MD+p+'chiseled_airain.json','w'),indent=1)
json.dump(manif,open(manif_p,'w'),indent=1,sort_keys=True)
print('ciselé : 4 stades, engrenage en creux')
