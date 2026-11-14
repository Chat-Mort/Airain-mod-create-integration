# Ressources 1.51 : pièces d'atelier (tuyauterie, vanne, manomètre, lampes, gyrophare, plancher technique, toboggan,
# réverbère, plaques, bornes, établi) et garde-corps vitré des passerelles.
# Règle des textures : un motif n'est jamais étiré ni tassé. Motifs périodiques → uv automatique (positionnel) ;
# panneau → seulement sur des faces de 16 × 16 ; le reste → uv « crop » (pixel pour pixel, centré).
import json, os, shutil
R='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=R+'assets/airain/'; Dd=R+'data/'
SCR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
PRE=['','exposed_','weathered_','oxidized_']
ALL=("north","south","east","west","up","down")
DIMS={"north":(0,1),"south":(0,1),"east":(2,1),"west":(2,1),"up":(0,2),"down":(0,2)}
LUM={"block_light":15,"sky_light":15}
def el(fr,to,t='#m',faces=ALL,uv=None,rot=None,lum=False):
    """uv=None : automatique (positionnel) ; 'full' : toute la texture ; 'crop' : pixel pour pixel, centré ; ou une liste."""
    f={}
    for k in faces:
        d={"texture":t}
        a,b=DIMS[k]; wa=abs(to[a]-fr[a]); hb=abs(to[b]-fr[b])
        if uv=='full': d["uv"]=[0,0,16,16]
        elif uv=='crop':
            wa=min(16,wa); hb=min(16,hb); u=(16-wa)/2; v=(16-hb)/2; d["uv"]=[round(u,3),round(v,3),round(u+wa,3),round(v+hb,3)]
        elif isinstance(uv,dict) and k in uv: d["uv"]=uv[k]
        elif isinstance(uv,list): d["uv"]=uv
        if lum: d["neoforge_data"]=LUM
        f[k]=d
    e={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":f}
    if rot: e["rotation"]={"origin":rot[0],"axis":rot[1],"angle":rot[2]}|({"rescale":True} if len(rot)>3 and rot[3] else {})
    return e
def modele(nom,E,tex,rt="cutout",parent="minecraft:block/block"):
    w(AS+f'models/block/{nom}.json',{"parent":parent,"render_type":"minecraft:"+rt,"ambientocclusion":False,"textures":dict(tex,particle=tex.get('m',list(tex.values())[0])),"elements":E})
def tex(p): return {'m':f'airain:block/{p}airain_block','pn':f'airain:block/{p}airain_panel','fz':f'airain:block/{p}airain_frieze','bd':f'airain:block/{p}airain_band',
                    'fl':f'airain:block/{p}airain_fluted','tu':f'airain:block/{p}airain_pipe','tv':f'airain:block/{p}airain_pipe_vertical','ro':f'airain:block/{p}airain_rod',
                    'rg':'airain:block/oxidized_airain_block','g':f'airain:block/{p}airain_catwalk'}
# ---------------------------------------------------------------- textures : copiées depuis l'atelier de textures (noms neufs uniquement)
TB=SCR+'/airain_tex/block/'; DT=AS+'textures/block/'
NOUV_TEX=[p+n for p in PRE for n in ('airain_panel','airain_frieze','airain_band','airain_fluted','airain_pipe','airain_pipe_vertical','airain_rod')]+\
  ['sign_'+n for n in ('fleche','fleche_gauche','fleche_haut','forge','danger','sortie','stock','engrenage','plain')]+['airain_glass','gauge_face','lamp_red_glass','lamp_warm','beacon_glass_on','beacon_glass_off']
for n in NOUV_TEX: shutil.copyfile(TB+n+'.png',DT+n+'.png')
# ---------------------------------------------------------------- géométrie
def bras_nord():          # bras de tuyau vers le nord (z-) : flancs « tuyau », dessus/dessous « tuyau vertical », bride au bout
    return [el([5,5,0],[11,11,5],'#tu',faces=("east","west")),el([5,5,0],[11,11,5],'#tv',faces=("up","down")),
            el([4,4,0],[12,12,1],'#bd',faces=("north","east","west","up","down"))]
def coeur(axe):
    if axe=='x': return [el([5,5,5],[11,11,11],'#tu',faces=("north","south","up","down")),el([5,5,5],[11,11,11],'#bd',faces=("east","west"))]
    if axe=='z': return [el([5,5,5],[11,11,11],'#tu',faces=("east","west")),el([5,5,5],[11,11,11],'#tv',faces=("up","down")),el([5,5,5],[11,11,11],'#bd',faces=("north","south"))]
    return [el([5,5,5],[11,11,11],'#tv',faces=("north","south","east","west")),el([5,5,5],[11,11,11],'#bd',faces=("up","down"))]
def tuyau_z():            # tuyau droit nord-sud complet (vanne, plancher technique)
    return [el([5,5,0],[11,11,16],'#tu',faces=("east","west")),el([5,5,0],[11,11,16],'#tv',faces=("up","down")),
            el([4,4,0],[12,12,1],'#bd'),el([4,4,15],[12,12,16],'#bd')]
def vanne(ferme):
    E=tuyau_z()+[el([4,4,4],[12,12,12],'#bd'),el([7,12,7],[9,14,9],'#m')]
    r=([8,14.5,8],'y',45) if ferme else None
    for a,b in (([3,14,3],[13,15,4]),([3,14,12],[13,15,13]),([3,14,4],[4,15,12]),([12,14,4],[13,15,12]),([4,14.2,7.5],[12,14.8,8.5]),([7.5,14.2,4],[8.5,14.8,12])):
        E.append(el(a,b,'#rg',rot=r))
    E.append(el([7,15,7],[9,15.5,9],'#m'))
    return E
def mano(face):
    if face=='wall': y0,z0,z1,cz=5,12.5,16,12.4
    else: y0,z0,z1,cz=(3 if face=='floor' else 7),6.5,9.5,6.4
    E=[el([5,y0,z0],[11,y0+6,z1],'#m'),el([5,y0,z0],[11,y0+6,z1],'#m',rot=([8,y0+3,(z0+z1)/2],'z',45)),
       el([5.6,y0+0.6,cz],[10.4,y0+5.4,cz+0.1],'#cad',faces=("north",),uv='full')]
    if face=='floor': E.append(el([7.5,-5,7.5],[8.5,3,8.5],'#m'))     # la tige descend jusqu'au tuyau du dessous
    if face=='ceiling': E.append(el([7.5,13,7.5],[8.5,16,8.5],'#m'))
    return E
AIGUILLE=[el([7.75,8,7.9],[8.25,10.4,8.0],'#n',faces=("north","south")),el([7.5,7.5,7.85],[8.5,8.5,8.0],'#m')]
def suspension():
    return [el([7.5,12,7.5],[8.5,16,8.5]),el([6,11,6],[10,12,10],'#bd'),el([5,10,5],[11,11,11]),el([4,8,4],[12,10,12]),
            el([3,6,3],[13,8,13],'#bd'),el([2,5,2],[14,6,14]),el([5.5,3.5,5.5],[10.5,6,10.5],'#lw',uv='crop',lum=True)]
def applique():
    E=[el([4,3,15],[12,13,16],'#pn',uv='crop'),el([5,4,10],[11,5,15]),el([5,11,10],[11,12,15]),el([6.5,5,11.5],[9.5,11,14.5],'#lr',uv='crop',lum=True)]
    for x in (5,7.25,8.75,10.5): E.append(el([x,5,10],[x+0.5,11,10.5]))
    E.append(el([5,7.75,10],[11,8.25,10.5]))
    return E
def gyro_cadre():
    E=[el([4,0,4],[12,2,12],'#bd'),el([5,8,5],[11,9,11])]
    for (a,b) in (([5,2,5],[5.5,8,5.5]),([10.5,2,5],[11,8,5.5]),([5,2,10.5],[5.5,8,11]),([10.5,2,10.5],[11,8,11])): E.append(el(a,b))
    return E
def gyro_verre(on): return [el([5.25,2,5.25],[10.75,8,10.75],'#gl',faces=("north","south","east","west"),uv='crop',lum=on)]
REFLECTEUR=[el([6.5,2.5,6.5],[9.5,6.5,9.5],'#lw',uv='crop',lum=True),el([5.5,2.2,6],[6.2,7.2,10],'#rg')]
def pieds():
    E=[]
    for (x,z) in ((1,1),(13,1),(1,13),(13,13)):
        E+=[el([x,1,z],[x+2,13,z+2],'#ro',faces=("north","south","east","west"),uv={k:[7,3,9,15] for k in ("north","south","east","west")}),el([x-0.5,0,z-0.5],[x+2.5,1,z+2.5])]
    return E
def dalle(): return [el([0,13,0],[16,16,16],'#pn',faces=("up","down"),uv='full'),el([0,13,0],[16,16,16],'#bd',faces=("north","south","east","west"))]
def trappe(): return [el([0,13,-3],[16,29,0],'#pn',faces=("north","south"),uv='full'),el([0,13,-3],[16,29,0],'#bd',faces=("east","west","up","down"))]
def conduit_z():
    return [el([3,3,0],[13,13,16],'#cd',faces=("east","west","up","down")),el([2,2,0],[14,14,1],'#cr'),el([2,2,15],[14,14,16],'#cr')]
def tob_pente():   # descend vers le nord : rotation de -45° autour de x (étirée par Minecraft pour couvrir la diagonale)
    r=([8,8,8],'x',-45,True)
    return [el([2,7.5,0],[14,8.5,16],rot=r),el([1,7.5,0],[2,13.5,16],rot=r),el([14,7.5,0],[15,13.5,16],rot=r)]
def tob_plat(): return [el([0,0,0],[16,1,16]),el([1,1,0],[2,4,16]),el([14,1,0],[15,4,16]),el([2,1,0],[14,4,1])]
FUT3={k:[6,0,9,16] for k in ("north","south","east","west")}
def fut(y0=0,y1=16): return [el([6.5,y0,6.5],[9.5,y1,9.5],'#fl',faces=("north","south","east","west"),uv={k:[6,16-y1,9,16-y0] for k in ("north","south","east","west")})]
def socle(): return [el([3,0,3],[13,2,13]),el([4.5,2,4.5],[11.5,5,11.5],'#bd')]
def lanterne(x,y,z):
    return [el([x-2,y+6,z-2],[x+2,y+7,z+2]),el([x-1,y+7,z-1],[x+1,y+8,z+1]),el([x-1.5,y+1,z-1.5],[x+1.5,y+6,z+1.5],'#lr',uv='crop',lum=True),el([x-2,y,z-2],[x+2,y+1,z+2])]
def tete_simple(): return fut(0,10)+lanterne(8,10,8)
def tete_double():  # traverse est-ouest (axe x)
    return fut(0,11)+[el([-1,9,7],[17,10.5,9],'#bd'),el([6,10.5,7.5],[10,12,8.5])]+[el([-0.5,6,7.5],[0.5,9,8.5]),el([15.5,6,7.5],[16.5,9,8.5])]+lanterne(0,-1,8)+lanterne(16,-1,8)
NIV={'middle':(3,4,13,12),'catwalk_low':(3,7,13,13),'catwalk_high':(3,15,13,21)}
def plaque(niv):
    x0,y0,x1,y1=NIV[niv]; z0=15.5 if niv=='middle' else 13.5      # contre une rambarde : sur sa face extérieure
    return [el([x0,y0,z0],[x1,y1,z0+0.5],'#sign',faces=("north",),uv='full'),el([x0,y0,z0],[x1,y1,z0+0.5],'#m',faces=("south","east","west","up","down"))]
def borne_fut(): return fut()
def borne_socle(): return [el([4,0,4],[12,2,12],'#bd')]
def borne_chapeau(): return [el([5.5,14,5.5],[10.5,15,10.5],'#bd'),el([6.5,15,6.5],[9.5,16,9.5])]
def planchette(t):   # flèche pointée vers le nord : face est (on lit vers le nord), face ouest en miroir
    return [el([7.5,0,-6],[8.5,6,8],t,faces=("east",),uv='full'),el([7.5,0,-6],[8.5,6,8],t,faces=("west",),uv=[16,0,0,16]),
            el([7.5,0,-6],[8.5,6,8],'#m',faces=("north","up","down"))]
def etabli():
    E=dalle()
    for (x,z) in ((0.5,0.5),(13.5,0.5),(0.5,13.5),(13.5,13.5)): E.append(el([x,0,z],[x+2,13,z+2]))
    E+=[el([1,3,1],[15,4,15],'#rg'),el([2,9,0],[14,12.5,1],'#bd'),el([7,10,-0.5],[9,11,0]),
        el([1,16,2],[6,19,5],'#bd'),el([1.5,16,0.5],[5.5,19,1.5],'#bd'),el([3,17,1.5],[4,18,2],'#rg'),el([1,17.5,0],[6,18,0.5],'#rg'),
        el([9,16,6],[13,17.5,7.5],'#rg'),el([10.5,16,7.5],[11.5,17,13])]
    return E
def vitre_cadre(h):   # dehors, comme les rambardes
    return [el([-2,h,-2],[0,h+13,0]),el([0,h+11,-2],[16,h+13,0]),el([0,h,-1.5],[16,h+1.5,-0.5])]
def vitre_verre(h): return [el([0,h+1.5,-1.25],[16,h+11,-0.75],'#gl',faces=("north","south"),uv='crop')]
# ---------------------------------------------------------------- modèles
TC={'m':'airain:block/airain_block','cr':'airain:block/riveted_airain','cd':'airain:block/airain_block'}
for p in PRE:
    t=tex(p); tt=dict(t,lw='airain:block/lamp_warm',lr='airain:block/lamp_red_glass',cd='airain:block/'+p+'airain_block',cr='airain:block/'+p+'riveted_airain')
    for a in 'xyz': modele(f'{p}airain_pipe_core_{a}',coeur(a),t)
    modele(f'{p}airain_pipe_arm',bras_nord(),t); modele(f'{p}airain_pipe_item',coeur('z')+bras_nord()+[dict(e,**{"from":[e['from'][0],e['from'][1],16-e['to'][2]],"to":[e['to'][0],e['to'][1],16-e['from'][2]]}) for e in bras_nord()],t)
    modele(f'{p}airain_pipe_valve_open',vanne(False),t); modele(f'{p}airain_pipe_valve_closed',vanne(True),t)
    modele(f'{p}airain_pendant_lamp',suspension(),tt); modele(f'{p}airain_wall_lamp',applique(),tt)
    modele(f'{p}airain_raised_floor_legs',pieds(),t); modele(f'{p}airain_raised_floor_plate',dalle(),t); modele(f'{p}airain_raised_floor_lid',trappe(),t)
    modele(f'{p}airain_raised_floor_pipe',tuyau_z(),t); modele(f'{p}airain_raised_floor_duct',conduit_z(),tt)
    modele(f'{p}airain_raised_floor_item',pieds()+dalle(),t)
    modele(f'{p}airain_chute',tob_pente(),t); modele(f'{p}airain_chute_flat',tob_plat(),t)
    modele(f'{p}airain_lamppost_mast',fut(),t); modele(f'{p}airain_lamppost_base',socle(),t)
    modele(f'{p}airain_lamppost_head',tete_simple(),tt); modele(f'{p}airain_lamppost_head_double',tete_double(),tt)
    modele(f'{p}airain_lamppost_item',socle()+fut(5,16)+lanterne(8,6,8),tt)
# pièces non patinables
tp=dict(tex(''),lw='airain:block/lamp_warm',lr='airain:block/lamp_red_glass',cad='airain:block/gauge_face',n='airain:block/oxidized_airain_block')
for f in ('wall','floor','ceiling'): modele(f'airain_gauge_{f}',mano(f),tp)
modele('airain_gauge/needle',AIGUILLE,tp)
modele('airain_beacon_light_frame',gyro_cadre(),tp)
modele('airain_beacon_light_glass_on',gyro_verre(True),dict(tp,gl='airain:block/beacon_glass_on'),rt='translucent')
modele('airain_beacon_light_glass_off',gyro_verre(False),dict(tp,gl='airain:block/beacon_glass_off'),rt='translucent')
modele('airain_beacon_light/reflector',REFLECTEUR,tp)
modele('airain_beacon_light_item',gyro_cadre()+gyro_verre(False),dict(tp,gl='airain:block/beacon_glass_off'),rt='translucent')
for n in NIV: modele(f'airain_sign_plate_{n}',plaque(n),dict(tp,sign='airain:block/sign_fleche'))
PICTOS={'arrow_right':'fleche','arrow_left':'fleche_gauche','arrow_up':'fleche_haut','forge':'forge','danger':'danger','exit':'sortie','storage':'stock','gear':'engrenage'}
for pk,tx in PICTOS.items():
    for n in NIV: w(AS+f'models/block/airain_sign_plate_{n}_{pk}.json',{"parent":f"airain:block/airain_sign_plate_{n}","textures":{"sign":"airain:block/sign_"+tx}})
modele('airain_signpost_post',borne_fut(),tp); modele('airain_signpost_base',borne_socle(),tp); modele('airain_signpost_cap',borne_chapeau(),tp)
modele('airain_signpost/arrow',planchette('#s'),dict(tp,s='airain:block/sign_fleche'))
modele('airain_signpost/board',planchette('#s'),dict(tp,s='airain:block/sign_plain'))
modele('airain_signpost_item',borne_socle()+borne_fut()+borne_chapeau()+[dict(e,**{"from":[e['from'][0],e['from'][1]+9,e['from'][2]],"to":[e['to'][0],e['to'][1]+9,e['to'][2]]}) for e in planchette('#s')],dict(tp,s='airain:block/sign_fleche'))
modele('airain_workbench',etabli(),tp)
for p in PRE:
    t=tex(p)
    for hh,h in (('bottom',3),('top',11)):
        modele(f'{p}airain_catwalk_glass_frame_{hh}',vitre_cadre(h),t)
        modele(f'{p}airain_catwalk_glass_pane_{hh}',vitre_verre(h),dict(t,gl='airain:block/airain_glass'),rt='translucent')
# ---------------------------------------------------------------- blockstates, objets, butin
ROT={'north':0,'east':90,'south':180,'west':270}
DIR6={'north':(0,0),'east':(0,90),'south':(0,180),'west':(0,270),'up':(270,0),'down':(90,0)}
def mp(model,when=None,y=0,x=0):
    d={"apply":{"model":model}|({"y":y} if y else {})|({"x":x} if x else {})}
    if when is not None: d["when"]=when
    return d
def butin(i):
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
FAMS=['airain_pipe','airain_pipe_valve','airain_pendant_lamp','airain_wall_lamp','airain_raised_floor','airain_chute','airain_lamppost']
TOUS=[]
for f in FAMS:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f; TOUS.append(i); M=lambda n,p=p: f'airain:block/{p}{n}'
            if f=='airain_pipe':
                bs={"multipart":[mp(M('airain_pipe_core_x'),{"OR":[{"east":"true"},{"west":"true"}]}),
                                 mp(M('airain_pipe_core_z'),{"AND":[{"east":"false","west":"false"},{"OR":[{"north":"true"},{"south":"true"}]}]}),
                                 mp(M('airain_pipe_core_y'),{"east":"false","west":"false","north":"false","south":"false"})]+
                               [mp(M('airain_pipe_arm'),{d:"true"},y,x) for d,(x,y) in DIR6.items()]}
                item=M('airain_pipe_item')
            elif f=='airain_pipe_valve':
                v={}
                for o,mo in (('true','open'),('false','closed')):
                    v[f"axis=z,open={o}"]={"model":M('airain_pipe_valve_'+mo)}
                    v[f"axis=x,open={o}"]={"model":M('airain_pipe_valve_'+mo),"y":90}
                    v[f"axis=y,open={o}"]={"model":M('airain_pipe_valve_'+mo),"x":90}
                bs={"variants":v}; item=M('airain_pipe_valve_open')
            elif f=='airain_pendant_lamp': bs={"variants":{"":{"model":M('airain_pendant_lamp')}}}; item=M('airain_pendant_lamp')
            elif f=='airain_wall_lamp': bs={"variants":{f"facing={d}":{"model":M('airain_wall_lamp')}|({"y":r} if r else {}) for d,r in ROT.items()}}; item=M('airain_wall_lamp')
            elif f=='airain_raised_floor':
                parts=[mp(M('airain_raised_floor_legs')),mp(M('airain_raised_floor_plate'),{"open":"false"})]
                for ax,r in (('z',0),('x',90)):
                    parts+=[mp(M('airain_raised_floor_pipe'),{"content":"pipe","axis":ax},r),mp(M('airain_raised_floor_duct'),{"content":"duct","axis":ax},r)]
                for d,r in ROT.items(): pass
                parts.append(mp(M('airain_raised_floor_lid'),{"open":"true"}))
                bs={"multipart":parts}; item=M('airain_raised_floor_item')
            elif f=='airain_chute':
                bs={"variants":{f"facing={d},flat={fl}":{"model":M('airain_chute'+('_flat' if fl=='true' else ''))}|({"y":r} if r else {}) for d,r in ROT.items() for fl in ('false','true')}}; item=M('airain_chute')
            else:
                bs={"multipart":[mp(M('airain_lamppost_mast'),{"top":"false"}),mp(M('airain_lamppost_base'),{"bottom":"true"}),
                                 mp(M('airain_lamppost_head'),{"top":"true","double":"false"}),
                                 mp(M('airain_lamppost_head_double'),{"top":"true","double":"true","axis":"x"}),mp(M('airain_lamppost_head_double'),{"top":"true","double":"true","axis":"z"},90)]}
                item=M('airain_lamppost_item')
            w(AS+f'blockstates/{i}.json',bs); w(AS+f'models/item/{i}.json',{"parent":item}); butin(i)
# non patinables
g={}
for fc in ('wall','floor','ceiling'):
    for d,r in ROT.items():
        rr=r if fc=='wall' else ROT[{'north':'south','south':'north','east':'west','west':'east'}[d]]
        g[f"face={fc},facing={d}"]={"model":f"airain:block/airain_gauge_{fc}"}|({"y":rr} if rr else {})
w(AS+'blockstates/airain_gauge.json',{"variants":g}); w(AS+'models/item/airain_gauge.json',{"parent":"airain:block/airain_gauge_wall"})
w(AS+'blockstates/airain_beacon_light.json',{"multipart":[mp('airain:block/airain_beacon_light_frame'),mp('airain:block/airain_beacon_light_glass_on',{"lit":"true"}),mp('airain:block/airain_beacon_light_glass_off',{"lit":"false"})]})
w(AS+'models/item/airain_beacon_light.json',{"parent":"airain:block/airain_beacon_light_item"})
w(AS+'blockstates/airain_sign_plate.json',{"variants":{f"facing={d},level={n},picto={pk}":{"model":f"airain:block/airain_sign_plate_{n}_{pk}"}|({"y":r} if r else {}) for d,r in ROT.items() for n in NIV for pk in PICTOS}})
w(AS+'models/item/airain_sign_plate.json',{"parent":"airain:block/airain_sign_plate_middle_arrow_right"})
w(AS+'blockstates/airain_signpost.json',{"multipart":[mp('airain:block/airain_signpost_post'),mp('airain:block/airain_signpost_base',{"bottom":"true"}),mp('airain:block/airain_signpost_cap',{"top":"true"})]})
w(AS+'models/item/airain_signpost.json',{"parent":"airain:block/airain_signpost_item"})
w(AS+'blockstates/airain_workbench.json',{"variants":{f"facing={d}":{"model":"airain:block/airain_workbench"}|({"y":r} if r else {}) for d,r in ROT.items()}})
w(AS+'models/item/airain_workbench.json',{"parent":"airain:block/airain_workbench"})
for i in ('airain_gauge','airain_beacon_light','airain_sign_plate','airain_signpost','airain_workbench'): butin(i)
# garde-corps vitré : ajouté aux blockstates des passerelles et des paliers
for f in ('airain_catwalk','airain_catwalk_landing'):
    for p in PRE:
        for c in (0,1):
            i=('waxed_' if c else '')+p+f; c_=AS+f'blockstates/{i}.json'; bs=json.load(open(c_))
            bs['multipart']=[x for x in bs['multipart'] if 'glass' not in json.dumps(x)]
            if f=='airain_catwalk':
                for d,r in ROT.items():
                    for hh,cond in (('bottom',{"top":"false"}),('top',{"top":"true"})):
                        for part in ('frame','pane'): bs['multipart'].append(mp(f'airain:block/{p}airain_catwalk_glass_{part}_{hh}',dict(cond,**{d:"glass"}),r))
            else:      # palier : côtés « back » et « side » (1.55.3)
                CW={'north':'east','east':'south','south':'west','west':'north'}; CCW={v:k for k,v in CW.items()}
                for d in ROT:
                    for g in ('false','true'):
                        for prop,dw in (('back',d),('side',CW[d] if g=='true' else CCW[d])):
                            for part in ('frame','pane'): bs['multipart'].append(mp(f'airain:block/{p}airain_catwalk_glass_{part}_top',{"facing":d,"turn_left":g,prop:"glass"},ROT[dw]))
            w(c_,bs)
# ---------------------------------------------------------------- patine, étiquettes, recettes, noms
ox={}; wx={}
for f in FAMS:
    for s,p in enumerate(PRE):
        if s<3: ox['airain:'+p+f]={"next_oxidation_stage":'airain:'+PRE[s+1]+f}
        wx['airain:'+p+f]={"waxed":'airain:waxed_'+p+f}
for nom,ajout in (('oxidizables',ox),('waxables',wx)):
    c=Dd+f'neoforge/data_maps/block/{nom}.json'; d=json.load(open(c)); d['values'].update(ajout); w(c,d)
def tag(chemin, valeurs):
    c=Dd+chemin; old=json.load(open(c))['values'] if os.path.exists(c) else []
    w(c,{"replace":False,"values":list(dict.fromkeys(old+valeurs))})
ids=['airain:'+i for i in TOUS]+['airain:'+i for i in ('airain_gauge','airain_beacon_light','airain_sign_plate','airain_signpost','airain_workbench')]
tag('minecraft/tags/block/mineable/pickaxe.json',ids); tag('minecraft/tags/block/needs_stone_tool.json',ids)
RC=R+'data/airain/recipe/airain/'
it=lambda i:{"item":"airain:"+i}; mc=lambda i:{"item":"minecraft:"+i}
def sh(n,pat,key,res,cnt=1): w(RC+n+'.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":pat,"key":key,"result":{"id":"airain:"+res,"count":cnt}})
def sl(n,ing,res,cnt=1): w(RC+n+'.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":ing,"result":{"id":"airain:"+res,"count":cnt}})
sh('pipe',["SSS"],{"S":it('airain_sheet')},'airain_pipe',6)
sl('pipe_valve',[it('airain_pipe'),it('airain_ingot')],'airain_pipe_valve')
sl('gauge',[it('airain_sheet'),mc('glass_pane'),mc('redstone')],'airain_gauge')
sh('pendant_lamp',[" C ","SGS"],{"C":it('airain_chain'),"S":it('airain_sheet'),"G":mc('glowstone_dust')},'airain_pendant_lamp',2)
sh('wall_lamp',["B","G","S"],{"B":it('airain_bars'),"G":mc('glowstone_dust'),"S":it('airain_sheet')},'airain_wall_lamp',2)
sh('beacon_light',["G","R","S"],{"G":mc('red_stained_glass'),"R":mc('redstone_lamp'),"S":it('airain_sheet')},'airain_beacon_light')
sh('raised_floor',["SSS","N N"],{"S":it('airain_sheet'),"N":it('airain_nugget')},'airain_raised_floor',4)
sh('chute',["S ","SS"],{"S":it('airain_sheet')},'airain_chute',4)
sh('lamppost',["L","I","S"],{"L":it('airain_lantern'),"I":it('airain_ingot'),"S":it('airain_sheet')},'airain_lamppost',3)
sl('sign_plate',[it('airain_sheet'),mc('red_dye'),mc('gold_nugget')],'airain_sign_plate',3)
sl('signpost',[it('airain_ingot'),it('airain_sheet'),mc('red_dye')],'airain_signpost',2)
sh('workbench',["SSS","ICI","I I"],{"S":it('airain_sheet'),"I":it('airain_ingot'),"C":mc('crafting_table')},'airain_workbench')
for p in PRE:
    for f in FAMS:
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing",
          "ingredients":[it(p+f),{"item":"minecraft:honeycomb"}],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
NFR={'airain_pipe':"Tuyau d'airain",'airain_pipe_valve':"Vanne d'airain",'airain_pendant_lamp':"Suspension d'atelier",'airain_wall_lamp':"Applique d'atelier",
     'airain_raised_floor':"Plancher technique",'airain_chute':"Toboggan d'airain",'airain_lamppost':"Réverbère impérial"}
NEN={'airain_pipe':"Airain Pipe",'airain_pipe_valve':"Airain Valve",'airain_pendant_lamp':"Workshop Pendant Lamp",'airain_wall_lamp':"Workshop Wall Lamp",
     'airain_raised_floor':"Raised Floor",'airain_chute':"Airain Chute",'airain_lamppost':"Imperial Lamppost"}
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
fr={"block.airain.airain_gauge":"Manomètre","block.airain.airain_beacon_light":"Gyrophare","block.airain.airain_sign_plate":"Plaque émaillée",
    "block.airain.airain_signpost":"Borne de carrefour","block.airain.airain_workbench":"Établi d'atelier"}
en={"block.airain.airain_gauge":"Gauge","block.airain.airain_beacon_light":"Beacon Light","block.airain.airain_sign_plate":"Enamel Sign",
    "block.airain.airain_signpost":"Crossroads Signpost","block.airain.airain_workbench":"Workshop Bench"}
for f in FAMS:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f
            fr['block.airain.'+i]=NFR[f]+SFR[s]+(' (ciré)' if c else ''); en['block.airain.'+i]=('Waxed ' if c else '')+SEN[s]+NEN[f]
L=AS+'lang/'
for fn,d in (('fr_fr.json',fr),('en_us.json',en)):
    j=json.load(open(L+fn)); j.update(d); json.dump(j,open(L+fn,'w'),ensure_ascii=False,indent=1)
print('atelier ok',len(TOUS)+5)
