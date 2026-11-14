import sys, json, math, copy
src=open('verif_passerelles.py').read(); exec(src[:src.index('E=[]')])
_charge=charge
def charge(nom,pos,y=0,x=0):
    d=json.load(open(MD+nom+'.json'))
    while 'elements' not in d: d=json.load(open(MD+d['parent'].split('block/')[1]+'.json')) | {'textures':dict(json.load(open(MD+d['parent'].split('block/')[1]+'.json'))['textures'],**d.get('textures',{}))}
    E=copy.deepcopy(d['elements']); T=d['textures']
    out=[]
    for e in E:
        r=e.get('rotation')
        if r and r.get('rescale'):
            c=1/math.cos(math.radians(abs(r['angle']))); ax={'x':(1,2),'y':(0,2),'z':(0,1)}[r['axis']]
            for i in ax:
                o=r['origin'][i]; e['from'][i]=o+(e['from'][i]-o)*c; e['to'][i]=o+(e['to'][i]-o)*c
        for _ in range(x//90):
            fr,to=e['from'],e['to']
            e['from'],e['to']=[fr[0],min(fr[2],to[2]),16-max(fr[1],to[1])],[to[0],max(fr[2],to[2]),16-min(fr[1],to[1])]
            e['from'][1],e['to'][1]=fr[2],to[2]; e['from'][2],e['to'][2]=16-to[1],16-fr[1]
            if r: o=r['origin']; r['origin']=[o[0],o[2],16-o[1]]
            m={'north':'down','up':'north','south':'up','down':'south','east':'east','west':'west'}
            e['faces']={m[k]:v for k,v in e['faces'].items()}
        for _ in range(y//90):
            fr,to=e['from'],e['to']
            e['from'],e['to']=[16-to[2],fr[1],fr[0]],[16-fr[2],to[1],to[0]]
            if r:
                o=r['origin']; r['origin']=[16-o[2],o[1],o[0]]
                if r['axis']=='x': r['axis']='z'
                elif r['axis']=='z': r['axis']='x'; r['angle']=-r['angle']
            m={'north':'east','east':'south','south':'west','west':'north','up':'up','down':'down'}
            e['faces']={m[k]:v for k,v in e['faces'].items()}
        for i in range(3): e['from'][i]+=pos[i]*16; e['to'][i]+=pos[i]*16
        if r: r['origin']=[r['origin'][i]+pos[i]*16 for i in range(3)]
        for f in e['faces'].values():
            t=f['texture'].lstrip('#'); f['texture']=T.get(t,t).replace('airain:','t:')
        out.append(e)
    return out
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
def cube(pos,t='t:block/fire_bricks'):
    return [{'from':[pos[0]*16,pos[1]*16,pos[2]*16],'to':[pos[0]*16+16,pos[1]*16+16,pos[2]*16+16],'faces':{k:{'texture':t,'uv':[0,0,16,16]} for k in ("north","south","east","west","up","down")}}]
def sol(xs,zs): return sum([[{'from':[x*16,-1,z*16],'to':[x*16+16,0,z*16+16],'faces':{'up':{'texture':'t:block/fire_bricks','uv':[0,0,16,16]}}}] for x in xs for z in zs],[])
def vue(E,eye,taille=900):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(E,{},taille); return im.crop(im.getbbox())
def tuyau(pos,bras):
    E=[]
    core='x' if ('east' in bras or 'west' in bras) else ('z' if ('north' in bras or 'south' in bras) else 'y')
    E+=charge('airain_pipe_core_'+core,pos)
    D6={'north':(0,0),'east':(0,90),'south':(0,180),'west':(0,270),'up':(270,0),'down':(90,0)}
    for b_ in bras: x,y=D6[b_]; E+=charge('airain_pipe_arm',pos,y,x)
    return E
# 1. tuyauterie
E=tuyau((0,0,0),['east','west'])+charge('airain_pipe_valve_open',(1,0,0),90)+tuyau((2,0,0),['west','up'])+tuyau((2,1,0),['down','up'])+charge('airain_pipe_valve_closed',(2,2,0),0,90)
E+=charge('airain_gauge_floor',(0,1,0),180)+tuyau((-1,0,0),['east','west'])+charge('airain_gauge_wall',(1,1,0),0)+cube((1,1,1))
A=vue(E+sol(range(-1,3),range(0,2)),[-0.6,0.5,-1])
# 2. lampes
E=cube((0,2,0))+charge('airain_pendant_lamp',(0,1,0))+cube((2,1,1))+charge('airain_wall_lamp',(2,1,0))+charge('airain_beacon_light_frame',(4,0,0))+charge('airain_beacon_light_glass_on',(4,0,0))+charge('airain_beacon_light/reflector',(4,0,0))
B=vue(E+sol(range(0,5),range(0,2)),[-0.6,0.35,-1])
# 3. plancher technique + toboggan
E=[]
for x in range(3): E+=charge('airain_raised_floor_legs',(x,0,0))+charge('airain_raised_floor_duct',(x,0,0),90)
E+=charge('airain_raised_floor_plate',(0,0,0))+charge('airain_raised_floor_lid',(1,0,0))+charge('airain_raised_floor_plate',(2,0,0))
E+=charge('airain_chute',(1,1,2),90)+charge('airain_chute',(2,0,2),90)+charge('airain_chute_flat',(3,0,2),90)+cube((0,0,2))+cube((0,1,2))
C=vue(E+sol(range(0,4),range(0,3)),[-0.6,0.6,1])
# 4. réverbères, plaques, borne, établi
E=charge('airain_lamppost_base',(0,0,0))+charge('airain_lamppost_mast',(0,0,0))+charge('airain_lamppost_mast',(0,1,0))+charge('airain_lamppost_head',(0,2,0))
E+=charge('airain_lamppost_base',(2,0,0))+charge('airain_lamppost_mast',(2,0,0))+charge('airain_lamppost_mast',(2,1,0))+charge('airain_lamppost_head_double',(2,2,0))
E+=charge('airain_workbench',(4,0,0),180)
E+=charge('airain_signpost_base',(6,0,0))+charge('airain_signpost_post',(6,0,0))+charge('airain_signpost_post',(6,1,0))+charge('airain_signpost_cap',(6,1,0))
for e in charge('airain_signpost/arrow',(6,1,0),90):
    e['from'][1]+=9.5; e['to'][1]+=9.5; E.append(e)
for e in charge('airain_signpost/board',(6,1,0),0):
    e['from'][1]+=2.5; e['to'][1]+=2.5; E.append(e)
D_=vue(E+sol(range(-1,8),range(0,2)),[-0.6,0.4,1])
# 5. passerelle à garde-corps vitré + plaques
E=[]
for x in range(3):
    E+=charge('airain_catwalk_floor_bottom',(x,0,0))+charge('airain_catwalk_glass_frame_bottom',(x,0,0),180)+charge('airain_catwalk_glass_pane_bottom',(x,0,0),180)+charge('airain_catwalk_railing_bottom',(x,0,0),0)
for x,pk in ((0,'arrow_right'),(1,'danger'),(2,'exit')): E+=charge(f'airain_sign_plate_catwalk_low_{pk}',(x,0,1),180)
F=vue(E+sol(range(0,3),range(0,2)),[-0.5,0.5,1])
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",26)
V=[("Tuyauterie, vannes, manomètres",A),("Lampes et gyrophare",B),("Plancher technique (conduit logé) et toboggan",C),("Réverbères, établi, borne",D_),("Garde-corps vitré et plaques",F)]
ims=[]
for t,i in V:
    s=min(1,700/i.width,520/i.height); ims.append((t,i.resize((int(i.width*s),int(i.height*s)))))
W=Image.new('RGBA',(2*760,3*600),(34,30,38,255)); d=ImageDraw.Draw(W)
for k,(t,i) in enumerate(ims):
    x0=(k%2)*760; y0=(k//2)*600
    d.text((x0+20,y0+15),t,font=fo,fill=(235,215,170)); W.alpha_composite(i,(x0+30+(700-i.width)//2,y0+60+(520-i.height)//2))
W.save('rendu_fusion/atelier_vrais.png')
