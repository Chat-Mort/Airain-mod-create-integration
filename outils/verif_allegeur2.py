src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'; rm._cache.clear()
def shaft(x,z):
    return [{'from':[x*16+6,6,z*16],'to':[x*16+10,10,z*16+16],'faces':{k:{'texture':'create:block/axis','uv':[6,0,10,16]} for k in ("east","west","up","down")}}]
E=[]
for i,p in enumerate(('','exposed_','weathered_','oxidized_')):
    E+=charge(f'{p}airain_load_reliever',(i,0,1),0)+charge(f'airain_load_reliever/{p}flywheel',(i,0,1),0)+charge('airain_load_reliever/lamps',(i,0,1),0)
    E+=shaft(i,0)+shaft(i,2)
A=vue(E+sol(range(0,4),range(0,3)),[-0.35,0.45,1],1100)
B=vue(E+sol(range(0,4),range(0,3)),[0.6,0.3,1],1100)
W=Image.new('RGBA',(max(A.width,B.width)+40,A.height+B.height+60),(34,30,38,255)); W.alpha_composite(A,(20,20)); W.alpha_composite(B,(20,A.height+40)); W.save('rendu_fusion/allegeur_creuse.png')
