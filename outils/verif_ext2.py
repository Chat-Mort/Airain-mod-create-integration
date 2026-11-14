src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
MOD='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
rm.RAC['t']=MOD; rm._cache.clear()
E=charge('airain_catwalk_floor_bottom',(0,0,0))+charge('airain_catwalk_railing_bottom',(0,0,0),0)+charge('airain_catwalk_railing_bottom',(0,0,0),90)
E+=charge('airain_catwalk_stairs',(1,0,0),90)+charge('airain_catwalk_stairs_left',(1,0,0),90)+charge('airain_catwalk_stairs_right',(1,0,0),90)
a=vue(E+sol(range(-1,3),range(-1,2)),[-0.6,1.2,1],700)
a.save('rendu_fusion/ext_zoom.png')
