src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'; rm._cache.clear()
exec(open('maquette_fourneau5.py').read().split('def elems')[0].split('def chargel')[1].join(['def chargel','']) if False else '')
def chargel(m,pos,r=0):
    es=charge(m,(0,0,0),r)
    for e in es:
        (x1,y1,z1),(x2,y2,z2)=e['from'],e['to']
        D={'north':[16-x2,16-y2,16-x1,16-y1],'south':[x1,16-y2,x2,16-y1],'west':[z1,16-y2,z2,16-y1],'east':[16-z2,16-y2,16-z1,16-y1],'up':[x1,z1,x2,z2],'down':[x1,16-z2,x2,16-z1]}
        for k,f in e['faces'].items(): f.setdefault('uv',D[k])
        for i in range(3): e['from'][i]+=pos[i]*16; e['to'][i]+=pos[i]*16
        if e.get('rotation'): e['rotation']['origin']=[e['rotation']['origin'][i]+pos[i]*16 for i in range(3)]
    return es
def scene():
    E=[]
    # mât au sud (z=2), cabine z=1 portail au nord, passerelle z=0
    E+=chargel('airain_lift_winch',(1,0,2))
    for y in (1,2,3): E+=chargel('airain_lift_mast',(1,y,2),180)
    E+=chargel('airain_lift_cabin',(1,1,1),0)+chargel('airain_lift_cabin_top',(1,2,1),0)
    E+=chargel('airain_catwalk_floor_bottom',(1,1,0))+chargel('airain_catwalk_railing_bottom',(1,1,0),270)+chargel('airain_catwalk_railing_bottom',(1,1,0),90)
    for x in range(3):
        for z in range(3): E+=cube((x,0,z))
    return E
A=vue(scene(),[-0.7,0.5,-1],700); B=vue(scene(),[1,0.5,1],700)
W=Image.new('RGBA',(A.width+B.width+60,max(A.height,B.height)+40),(34,30,38,255)); W.alpha_composite(A,(20,20)); W.alpha_composite(B,(A.width+40,20)); W.save('rendu_fusion/cabine2.png')
