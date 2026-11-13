src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
def shaft(pos,axis='x'):
    x,y,z=pos
    if axis=='x': return [{'from':[x*16,y*16+6,z*16+6],'to':[x*16+16,y*16+10,z*16+10],'faces':{k:{'texture':'create:block/axis','uv':[6,0,10,16]} for k in ("north","south","up","down")}}]
E=charge('airain_load_reliever',(1,0,0),90)+charge('airain_load_reliever/flywheel',(1,0,0),90)+charge('airain_load_reliever/lamps',(1,0,0),90)+shaft((0,0,0))+shaft((2,0,0))
A=vue(E+sol(range(0,3),range(0,1)),[-0.45,0.5,1],900)
E=charge('oxidized_airain_supercharger',(1,0,0),270)+charge('airain_supercharger/oxidized_piston',(1,0,0),270)+charge('airain_supercharger/lamp',(1,0,0),270)
P2=charge('airain_supercharger/oxidized_piston',(1,0,0),270)
for e in P2: e['from'][2]+=6; e['to'][2]+=6; e['from'][1]+=1.5; e['to'][1]+=1.5
E+=P2+cube((0,0,0),'t:block/oxidized_airain_block')
B=vue(E+sol(range(0,2),range(0,1)),[0.5,0.55,1],900)
W=Image.new('RGBA',(A.width+B.width+60,max(A.height,B.height)+40),(34,30,38,255)); W.alpha_composite(A,(20,20)); W.alpha_composite(B,(A.width+40,20)); W.save('rendu_fusion/mecanique_vrais.png')
