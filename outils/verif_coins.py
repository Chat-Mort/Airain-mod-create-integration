src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'; rm._cache.clear()
import json
BS=json.load(open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/blockstates/airain_catwalk.json'))
CELLS={(0,0),(1,0),(2,0),(0,1),(0,2),(1,2)}
D={'north':(0,-1),'south':(0,1),'east':(1,0),'west':(-1,0)}
def etat(c,glass=False):
    s={"top":"false","solid":"false","retracted":"false"}
    for d,(dx,dz) in D.items(): s[d]='none' if (c[0]+dx,c[1]+dz) in CELLS else ('glass' if glass and d=='north' else 'railing')
    return s
def ok(when,s):
    return all(s.get(k) in v.split('|') for k,v in when.items())
E=[]
for c in CELLS:
    s=etat(c, glass=c==(2,0))
    for part in BS['multipart']:
        if ok(part.get('when',{}),s):
            a=part['apply']; E+=charge(a['model'].split('block/')[1],(c[0]+1,0,c[1]+1),a.get('y',0))
A=vue(E+sol(range(0,5),range(0,5)),[-0.7,0.9,-1],800); B=vue(E+sol(range(0,5),range(0,5)),[0.8,0.8,1],800)
W=Image.new('RGBA',(A.width+B.width+60,max(A.height,B.height)+40),(34,30,38,255)); W.alpha_composite(A,(20,20)); W.alpha_composite(B,(A.width+40,20)); W.save('rendu_fusion/coins.png')
