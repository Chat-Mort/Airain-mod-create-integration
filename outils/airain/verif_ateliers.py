import sys
src=open('verif_passerelles.py').read(); exec(src[:src.index('E=[]')])
def cube(pos,t,faces=("north","south","east","west","up","down")):
    return [{'from':[pos[0]*16,pos[1]*16,pos[2]*16],'to':[pos[0]*16+16,pos[1]*16+16,pos[2]*16+16],'faces':{k:{'texture':t,'uv':[0,0,16,16]} for k in faces}}]
def vue(E,eye,nom='',taille=1100):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(E,{},taille); return im.crop(im.getbbox())
def sol(xs,zs): return sum([[{'from':[x*16,-1,z*16],'to':[x*16+16,0,z*16+16],'faces':{'up':{'texture':'t:block/fire_bricks','uv':[0,0,16,16]}}}] for x in xs for z in zs],[])
P='oxidized_'
# 1. escalier à palier : arrivée sud, palier (passerelle haute à l'ouest), sortie est
E=charge(P+'airain_catwalk_landing_right',(0,0,0))+charge(P+'airain_catwalk_railing_top',(0,0,0),0)
E+=charge(P+'airain_catwalk_floor_bottom',(0,0,1))+charge(P+'airain_catwalk_railing_bottom',(0,0,1),90)+charge(P+'airain_catwalk_railing_bottom',(0,0,1),270)+charge(P+'airain_catwalk_railing_bottom',(0,0,1),180)
E+=charge(P+'airain_catwalk_floor_top',(-1,0,0))+charge(P+'airain_catwalk_railing_top',(-1,0,0),0)+charge(P+'airain_catwalk_railing_top',(-1,0,0),180)
E+=charge(P+'airain_catwalk_floor_bottom',(1,1,0))+charge(P+'airain_catwalk_railing_bottom',(1,1,0),0)+charge(P+'airain_catwalk_railing_bottom',(1,1,0),180)
E+=charge(P+'airain_support',(1,0,0))+charge(P+'airain_support_bottom',(1,0,0))+charge(P+'airain_support_top',(1,0,0))
E+=sol(range(-1,2),range(0,2))
A=vue(E,[-0.6,0.8,1],'a'); B=vue(E,[0.8,0.6,-0.6],'b')
# 2. suspentes
E=[]
for x in range(3):
    E+=charge(P+'airain_catwalk_floor_bottom',(x,0,0))+charge(P+'airain_catwalk_railing_bottom',(x,0,0),0)+charge(P+'airain_catwalk_railing_bottom',(x,0,0),180)
    E+=cube((x,2,0),'t:block/fire_bricks')
for x in (0,2): E+=charge(P+'airain_hanger',(x,1,0))+charge(P+'airain_hanger_plate',(x,1,0))+charge(P+'airain_hanger_low',(x,1,0))
C=vue(E,[-0.6,0.35,1])
# 3. rambardes seules au bord d'une dalle
E=[]
for x in range(3):
    for z in range(2): E+=cube((x,0,z),'t:block/fire_bricks')
    E+=charge('airain_railing',(x,1,1),180)
E+=charge('airain_railing',(2,1,1),90)+charge('airain_railing',(2,1,0),90)
D=vue(E,[-0.6,0.8,1])
# 4. ventilateur → conduit → coude → bouche (souffle au sud)
E=cube((0,0,0),'create:block/fan_side')+cube((0,0,0),'create:block/fan_casing',faces=("up",))
E+=charge('airain_air_duct_core',(1,0,0))+charge('airain_air_duct_arm',(1,0,0),270)+charge('airain_air_duct_arm',(1,0,0),90)
E+=charge('airain_air_duct_core',(2,0,0))+charge('airain_air_duct_arm',(2,0,0),270)+charge('airain_air_duct_arm',(2,0,0),180)
E+=charge('airain_air_duct_core',(2,0,1))+charge('airain_air_duct_arm',(2,0,1),0)+charge('airain_air_duct_arm',(2,0,1),180)
E+=charge('airain_air_vent',(2,0,2),180)+sol(range(0,3),range(0,3))
F=vue(E,[-0.6,0.8,1])
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",26)
rows=[("Escalier à palier (palier raccordé à une passerelle haute)",[A,B]),("Suspentes",[C]),("Rambardes seules",[D]),("Conduite d'air",[F])]
H=sum(max(i.height for i in r[1])+70 for r in rows); Wd=max(sum(i.width+20 for i in r[1]) for r in rows)+40
W=Image.new('RGBA',(Wd,H),(34,30,38,255)); y=0; d=ImageDraw.Draw(W)
for t,ims in rows:
    d.text((20,y+15),t,font=fo,fill=(235,215,170)); x=20
    for i in ims: W.alpha_composite(i,(x,y+55)); x+=i.width+20
    y+=max(i.height for i in ims)+70
W.save('rendu_fusion/ateliers_vrais.png')
