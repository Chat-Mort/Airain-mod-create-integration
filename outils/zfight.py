# Repère les faces coplanaires qui se chevauchent dans un même modèle (z-fighting), hors éléments tournés.
import json,glob,sys,collections
AX={'north':(2,0),'south':(2,1),'west':(0,0),'east':(0,1),'down':(1,0),'up':(1,1)}
def faces(e):
    f,t=e['from'],e['to']
    for k,fc in e.get('faces',{}).items():
        ax,side=AX[k]; pos=(t if side else f)[ax]
        o=[i for i in range(3) if i!=ax]
        yield k,ax,pos,(f[o[0]],t[o[0]],f[o[1]],t[o[1]])
def chevauche(a,b):
    return min(a[1],b[1])-max(a[0],b[0])>0.01 and min(a[3],b[3])-max(a[2],b[2])>0.01
res=collections.Counter(); ex={}
for p in glob.glob(sys.argv[1]+'/**/*.json',recursive=True):
    m=json.load(open(p)); E=[e for e in m.get('elements',[]) if 'rotation' not in e or e['rotation'].get('angle',0)==0]
    F=[(i,)+x for i,e in enumerate(E) for x in faces(e)]
    n=0
    for a in range(len(F)):
        for b in range(a+1,len(F)):
            ia,ka,axa,pa,ra=F[a]; ib,kb,axb,pb,rb=F[b]
            if ia==ib or ka!=kb or abs(pa-pb)>0.001: continue
            # même orientation (deux faces dans le même sens) ou opposées : les deux scintillent
            if chevauche(ra,rb): n+=1; ex.setdefault(p,(E[ia]['from'],E[ia]['to'],ka,E[ib]['from'],E[ib]['to'],kb))
    if n: res[p.split('models/block/')[-1]]=n
for k,v in sorted(res.items(),key=lambda x:-x[1])[:60]: print(v,k)
print(len(res))
