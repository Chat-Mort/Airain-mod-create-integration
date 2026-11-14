src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'; rm._cache.clear()
E=[]
for z,(nom,p) in enumerate((('drawbridge',''),('telescopic',''),('drawbridge','oxidized_'),('telescopic','oxidized_'))):
    zz=z*2
    for x in range(4):
        so='airain_catwalk_floor_solid_bottom' if z>=2 and x==1 else 'airain_catwalk_floor_bottom'
        E+=charge(p+so,(x,0,zz))+charge(p+'airain_catwalk_railing_bottom',(x,0,zz),0)+charge(p+'airain_catwalk_railing_bottom',(x,0,zz),180)
        if x==1: E+=charge(f'airain_catwalk_mechanism/{p}{nom}_bottom',(x,0,zz),90)   # segments vers l'est
A=vue(E+sol(range(0,4),range(-1,8)),[-0.4,1.2,0.8],900)
A.save('rendu_fusion/reperes.png')
