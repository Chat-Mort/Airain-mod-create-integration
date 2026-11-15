# Rend les vrais modèles générés de la charpente et des marquages (blockstates simulés).
src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
rm._cache.clear()
P=''
def poteau(x,y,z,base=False,cap=False):
    E=charge(P+'airain_beam_post',(x,y,z))
    if base: E+=charge(P+'airain_beam_post_base',(x,y,z))
    if cap: E+=charge(P+'airain_beam_post_cap',(x,y,z))
    return E
def poutre(x,y,z,ax,deb=False,fin=False):
    r=0 if ax=='x' else 90
    E=charge(P+'airain_beam',(x,y,z),r)
    if deb: E+=charge(P+'airain_beam_start',(x,y,z),r)
    if fin: E+=charge(P+'airain_beam_end',(x,y,z),r)
    return E
FACE={'north':270,'east':0,'south':90,'west':180}
def incl(nom,x,y,z,f): return charge(P+nom,(x,y,z),FACE[f])
def treillis(x,y,z,ax):
    k=(x if ax=='x' else z)%2; n=P+'airain_lattice_girder'+('_alt' if k else '')
    return charge(n,(x,y,z),0 if ax=='x' else 90)
E=[]
for (x,z) in ((0,0),(0,4),(6,0),(6,4)):
    for y in range(4): E+=poteau(x,y,z,y==0,y==3)
for x in (0,6):
    for z in (1,2,3): E+=poutre(x,3,z,'z',z==1,z==3)
    E+=incl('airain_knee_brace',x,2,1,'south')+incl('airain_knee_brace',x,2,3,'north')
for z in (0,4):
    for x in range(7): E+=treillis(x,4,z,'x')
for z in (0,4):
    for k in range(3): E+=incl('airain_rafter',k,5+k,z,'east')+incl('airain_rafter',6-k,5+k,z,'west')
for z in (1,2,3):
    for k in range(3): E+=charge(P+'airain_glass_roof_frame',(k,5+k,z),0)+charge(P+'airain_glass_roof_glass',(k,5+k,z),0)
for z in range(5): E+=poutre(3,8,z,'z',False,False)
for z in range(5): E+=charge(P+'airain_gutter',(-1,5,z),90)+(charge(P+'airain_gutter_start',(-1,5,z),90) if z==0 else [])+(charge(P+'airain_gutter_end',(-1,5,z),90) if z==4 else [])
E+=charge(P+'airain_gutter_outlet',(-1,5,0))
for y in range(5): E+=charge(P+'airain_downpipe',(-1,y,0))+(charge(P+'airain_downpipe_shoe',(-1,y,0)) if y==0 else [])
# lanterneaux sur le côté est
for z in (1,2,3):
    for k in range(3): E+=charge('slate_dummy',(0,0,0)) if False else []
FL='minecraft:block/polished_andesite'
def fl(x,z): return {'from':[x*16,-1,z*16],'to':[x*16+16,0,z*16+16],'faces':{'up':{'texture':FL,'uv':[0,0,16,16]}}}
for x in range(-3,10):
    for z in range(-4,8): E.append(fl(x,z))
def ligne(x,z,c,bras):
    L=charge(f'{c}_floor_line_dot',(x,0,z))
    for b_ in bras: L+=charge(f'{c}_floor_line_'+{'n':'north','s':'south','e':'east','w':'west'}[b_],(x,0,z))
    return L
for x in (2,3,4):
    for z in (1,2,3):
        if (x,z)!=(3,2): E+=charge('yellow_hazard_stripes',(x,0,z))
for x in range(-2,9):
    E+=ligne(x,-2,'yellow','ew' if x not in (-2,8) else ('es' if x==-2 else 'ws'))
    E+=ligne(x,6,'yellow','ew' if x not in (-2,8) else ('en' if x==-2 else 'wn'))
for z in range(-1,6): E+=ligne(-2,z,'yellow','ns'); E+=ligne(8,z,'yellow','ns' if z!=2 else 'nse')
E+=ligne(9,2,'white','we')
for x in (0,3,6): E+=charge('white_floor_arrow',(x,0,-3),90)
E+=charge('white_floor_crossing',(7,0,-3),90)
E+=cube((3,0,2),'create:block/andesite_casing')
A=vue(E,[-0.75,0.55,-1],1500)
# détails rapprochés : pied, about, jambe, poutrelle tournée, treillis en colonne, lanterneau, gouttière
Q=poteau(0,0,0,True)+poteau(0,1,0,False,True)+poutre(0,1,1,'z',True,False)+incl('airain_knee_brace',0,0,1,'south')
Q+=charge('airain_beam_post_turned',(2,0,0))+charge('airain_beam_post_base',(2,0,0))+charge('airain_beam_turned',(2,1,0),0)+charge('airain_beam_start_turned',(2,1,0),0)
Q+=charge('airain_lattice_girder_column',(4,0,0))+charge('airain_lattice_girder_column_alt',(4,1,0))
Q+=charge('airain_skylight_frame',(6,0,0))+charge('airain_skylight_glass',(6,0,0))+charge('airain_skylight_frame',(7,0,0))+charge('airain_skylight_glass',(7,0,0))
for k,pre in enumerate(['','exposed_','weathered_','oxidized_']): Q+=charge(pre+'airain_beam',(k*1,0,3),0)+charge(pre+'airain_beam_start',(k,0,3),0) if k==0 else charge(pre+'airain_beam',(k,0,3),0)
Q+=[fl(x,z) for x in range(-1,9) for z in range(-1,5)]
B=vue(Q,[-0.7,0.6,-1],1100)
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
W=Image.new('RGBA',(max(A.width,B.width)+40,A.height+B.height+60),(34,30,38,255))
W.alpha_composite(A,(20,10)); W.alpha_composite(B,(20,A.height+40))
W.save('rendu_fusion/charpente_vrai.png'); print(W.size)
