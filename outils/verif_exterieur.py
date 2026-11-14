src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
MOD='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
rm.RAC['t']=MOD; rm._cache.clear()
E=[]
# ligne de passerelles : rambardes dehors, sol pleine largeur
for x in range(3):
    E+=charge('airain_catwalk_floor_bottom',(x,0,1))
    E+=charge('airain_catwalk_railing_bottom' if x!=1 else 'airain_catwalk_gate_bottom',(x,0,1),0)
    E+=charge('airain_catwalk_railing_bottom' if x!=2 else 'airain_catwalk_glass_frame_bottom',(x,0,1),180)
    if x==2: E+=charge('airain_catwalk_glass_pane_bottom',(x,0,1),180)
E+=charge('airain_catwalk_railing_bottom',(0,0,1),270)
# escalier montant vers l'est
E+=charge('airain_catwalk_stairs',(3,0,1),90)+charge('airain_catwalk_stairs_left',(3,0,1),90)+charge('airain_catwalk_stairs_right',(3,0,1),90)
E+=charge('airain_catwalk_floor_bottom',(4,1,1))+charge('airain_catwalk_railing_bottom',(4,1,1),0)+charge('airain_catwalk_railing_bottom',(4,1,1),180)
E+=cube((4,0,1))
# rampe
E+=charge('oxidized_airain_catwalk_ramp_bottom',(5,1,1),90)+charge('oxidized_airain_catwalk_ramp_left_bottom',(5,1,1),90)+charge('oxidized_airain_catwalk_ramp_right_bottom',(5,1,1),90)
# palier
E+=charge('airain_catwalk_landing_left',(7,0,1),0)
a=vue(E+sol(range(0,8),range(-1,4)),[-0.5,0.8,1],900)
b=vue(E+sol(range(0,8),range(-1,4)),[0.6,0.7,-1],900)
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
W=Image.new('RGBA',(max(a.width,b.width)+40,a.height+b.height+120),(34,30,38,255)); d=ImageDraw.Draw(W)
d.text((20,10),"Rambardes à l'extérieur : sol pleine largeur (avant)",font=fo,fill=(235,215,170)); W.alpha_composite(a,(20,50))
d.text((20,a.height+60),"Vue arrière",font=fo,fill=(235,215,170)); W.alpha_composite(b,(20,a.height+100))
W.save('rendu_fusion/exterieur.png')
