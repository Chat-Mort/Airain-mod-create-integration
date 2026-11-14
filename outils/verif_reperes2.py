src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'; rm._cache.clear()
ims=[]
for nom in ('drawbridge','telescopic'):
    E=[]
    for x in range(3):
        E+=charge('airain_catwalk_floor_bottom',(x,0,0))
        if x==1: E+=charge(f'airain_catwalk_mechanism/{nom}_bottom',(x,0,0),90)
    for x in range(3):
        E+=charge('oxidized_airain_catwalk_floor_solid_bottom',(x,0,2))
        if x==1: E+=charge(f'airain_catwalk_mechanism/oxidized_{nom}_bottom',(x,0,2),90)
    ims.append(vue(E,[-0.35,1.4,0.6],700))
W=Image.new('RGBA',(sum(i.width for i in ims)+60,max(i.height for i in ims)+40),(34,30,38,255)); x=20
for i in ims: W.alpha_composite(i,(x,20)); x+=i.width+20
W.save('rendu_fusion/reperes.png')
