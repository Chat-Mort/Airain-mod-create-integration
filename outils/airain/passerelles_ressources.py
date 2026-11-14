# Modèles, blockstates et données des passerelles d'airain (style industriel).
import json, os
R='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=R+'assets/airain/'; Dd=R+'data/'
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
PRE=['','exposed_','weathered_','oxidized_']
ALL=("north","south","east","west","up","down")
def el(fr,to,t='#m',faces=ALL,rot=None,full=False):
    """Un élément de modèle ; uv : un morceau poli de la texture, à l'échelle de la pièce."""
    f={}
    for k in faces:
        if full: uv=[0,0,16,16]
        else:
            dx,dy,dz=[abs(to[i]-fr[i]) for i in range(3)]
            a,b={"north":(dx,dy),"south":(dx,dy),"east":(dz,dy),"west":(dz,dy),"up":(dx,dz),"down":(dx,dz)}[k]
            # pixel pour pixel, centré : jamais tassé (jusqu'à 16 px)
            a=max(0.5,min(16,a)); b=max(0.5,min(16,b)); u=(16-a)/2; v=(16-b)/2
            uv=[round(u,3),round(v,3),round(u+a,3),round(v+b,3)]
        f[k]={"texture":t,"uv":uv}
    e={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":f}
    if rot: e["rotation"]={"origin":rot[0],"axis":rot[1],"angle":rot[2],"rescale":True}
    return e
def uv_position(E):
    for e in E:
        x0,_,z0=e['from']; x1,_,z1=e['to']
        for k in ('up','down'):
            f=e['faces'].get(k)
            if f and f['texture'] in ('#g','#m') and 'rotation' not in e and abs(e['to'][1]-e['from'][1])<=2.01 and (x1-x0)>=1.99 and (z1-z0)>=1.99:
                # hors du bloc (rambardes dehors) : on décale de 16 au lieu de rogner, sinon la face devient une ligne
                def ram(a,b):
                    a,b=sorted((a,b))
                    if b-a>16: return 0,16
                    if a<0: a,b=a+16,b+16
                    if b>16: a,b=a-16,b-16
                    return a,b
                u0,u1=ram(x0,x1); v0,v1=ram(z0,z1)
                f['uv']=[u0,v0,u1,v1] if k=='up' else [u0,16-v1,u1,16-v0]
    return E
def modele(nom, elements, tex):
    elements=uv_position(elements)
    w(AS+f'models/block/{nom}.json',{"parent":"minecraft:block/block","render_type":"minecraft:cutout","ambientocclusion":False,
       "textures":dict(tex,particle=tex['m']),"elements":elements})
# ---------------------------------------------------------------- géométrie (pièces décrites côté nord / montant vers le nord)
def plancher(h):
    return [el([0,h-2,0],[16,h,16],'#g',faces=("up","down"),full=True),
            el([0,h-2,0],[16,h,1]),el([0,h-2,15],[16,h,16]),el([0,h-2,1],[1,h,15]),el([15,h-2,1],[16,h,15])]
def plein(E):
    out=[]
    for e in E:
        e=json.loads(json.dumps(e))
        for f in e['faces'].values():
            if f['texture'] in ('#g','#gs'): f['texture']='#m'
        out.append(e)
    return out
def tunnel():
    # tunnel plein autour de l'échelle : trois parois de tôle, ouvertes côté mur
    return [el([1,0,1],[15,16,2],'#m',faces=("north","south"),full=True),el([1,0,2],[2,16,13],'#m',faces=("east","west"),full=True),
            el([14,0,2],[15,16,13],'#m',faces=("east","west"),full=True)]
def rambarde_nord(h):
    # à l'extérieur du bloc (sur le bord du voisin) : le plancher garde toute sa largeur ; poteau à l'angle extérieur
    return [el([0,h+11,-2],[16,h+13,0]),el([0,h+6,-1.5],[16,h+7,-0.5]),el([0,h,-1.5],[16,h+3,-1]),el([-2,h,-2],[0,h+13,0])]
def rambarde_int(h):   # rambarde dans le bloc (cage du monte-charge, segment mobile relevé) : poteaux aux deux bouts
    return [el([0,h+11,0],[16,h+13,2]),el([0,h+6,0.5],[16,h+7,1.5]),el([0,h,0.5],[16,h+3,1]),el([0,h,0],[2,h+13,2]),el([14,h,0],[16,h+13,2])]
def portillon_nord(h, ouvert):
    # dehors, comme les rambardes (z décalé de -2)
    E=[el([0,h,-2.0],[2,h+13,0.0]),el([14,h,-2.0],[16,h+13,0.0])]            # poteaux du portillon
    if not ouvert:
        E+=[el([2,h+1,-2.0],[3,h+12,-1.0]),el([13,h+1,-2.0],[14,h+12,-1.0]),el([2,h+11,-2.0],[14,h+12,-1.0]),el([2,h+1,-2.0],[14,h+2,-1.0]),
            el([3,h+6,-1.8],[13,h+7,-1.2]),
            el([3,h+3.5,-1.7],[13,h+4.5,-1.3],rot=([8,h+4,-1.5],'z',22.5)),el([3,h+8.5,-1.7],[13,h+9.5,-1.3],rot=([8,h+9,-1.5],'z',22.5)),
            el([14,h+7,-2.5],[15,h+9,-0.5])]
    else:   # ouvert : le battant pivote sur son poteau ouest et rentre dans la passerelle
        E+=[el([2,h+1,-1.0],[3,h+12,0.0]),el([2,h+1,10.0],[3,h+12,11.0]),el([2,h+11,0.0],[3,h+12,10.0]),el([2,h+1,0.0],[3,h+2,10.0]),
            el([2.2,h+6,0.0],[2.8,h+7,10.0]),
            el([2.3,h+3.5,0],[2.7,h+4.5,10],rot=([2.5,h+4,5.0],'x',-22.5)),el([2.3,h+8.5,0],[2.7,h+9.5,10],rot=([2.5,h+9,5.0],'x',-22.5))]
    return E
def m2n(fr,to):
    """Passe une boîte décrite « monte vers +x, côtés en z » à « monte vers le nord, côtés en x » : (x,z) → (z, 16-x)."""
    return [fr[2],fr[1],16-to[0]],[to[2],to[1],16-fr[0]]
def eln(fr,to,t='#m',faces=ALL,rot=None,full=False):
    a,b=m2n(fr,to)
    r=None
    if rot: o=rot[0]; r=([o[2],o[1],16-o[0]],'x' if rot[1]=='z' else rot[1],rot[2])
    return el(a,b,t,faces,r,full)
S=3
def escalier_base():
    E=[]
    for i in range(4):
        top=S+4*(i+1)
        # marche : la bande des croisillons (rangs 2 à 6 : une rangée de croix entières), pixel pour pixel
        e=eln([4*i,top-1,0],[4*i+4,top,16],'#gs',faces=("up","down")); e['faces']['up']['uv']=[0,2,16,6]; e['faces']['down']['uv']=[0,6,16,2]; E.append(e)
        E.append(eln([4*i+3,top-2,0],[4*i+4,top,16]))
        # nez de marche : bandeau à rivets sur l'avant (pixel pour pixel)
        n=eln([4*i,top-2,0],[4*i+1,top,16],'#bd')
        for k,f in n['faces'].items(): f['uv']=[0,1,16,3] if k in ('north','south') else ([7,1,8,3] if k in ('east','west') else [0,1,16,2])
        E.append(n)
    for z0 in (0,14): E.append(eln([0,S+5,z0+0.5],[16,S+8,z0+1.5],rot=([8,S+6.5,8],'z',45)))
    return E
def escalier_rampe(z0):
    return [eln([0,S+18.5,z0],[16,S+20.5,z0+2],rot=([8,S+19.5,8],'z',45)),eln([0,S+11.5,z0+0.5],[16,S+12.5,z0+1.5],rot=([8,S+12,8],'z',45)),
            eln([0,S,z0],[2,S+13,z0+2]),eln([14,S+16,z0],[16,S+29,z0+2])]
def rampe_base(h0):
    E=[]
    for i in range(8):
        E.append(eln([2*i,h0-2+i,0],[2*i+2,h0+i,16],'#g',faces=("up","down"),full=True))
        E.append(eln([2*i+1,h0-1+i,0],[2*i+2,h0+i+0.5,16]))
    return E
def rampe_cote(h0,z0):
    return [eln([0,h0+15,z0],[16,h0+17,z0+2],rot=([8,h0+16,8],'z',22.5)),eln([0,h0+10,z0+0.5],[16,h0+11,z0+1.5],rot=([8,h0+10.5,8],'z',22.5)),
            eln([0,h0+2,z0+0.5],[16,h0+4,z0+1],rot=([8,h0+3,8],'z',22.5)),eln([0,h0,z0],[2,h0+13,z0+2]),eln([14,h0+8,z0],[16,h0+21,z0+2])]
def poteau_fut(): return [el([6,0,6],[10,16,10],'#r',full=True)]
def poteau_bas(): return [el([2,0,2],[14,1,14]),el([4,1,4],[12,2.5,12]),el([5,2.5,5],[11,4,11])]
def poteau_haut(): return [el([5,12,5],[11,13.5,11]),el([4,13.5,4],[12,15,12]),el([1,15,1],[15,16,15])]
def echelle():
    E=[el([2,0,13],[4,16,15]),el([12,0,13],[14,16,15])]
    for yy in (2,6,10,14): E.append(el([4,yy,13.5],[12,yy+1,14.5]))
    return E
def cage():
    E=[]
    for yy in (4,12): E+=[el([1,yy,1],[2,yy+1,13]),el([14,yy,1],[15,yy+1,13]),el([1,yy,1],[15,yy+1,2])]
    for xx in (1,7.5,14): E.append(el([xx,0,1],[xx+1,16,2]))
    return E
# ---------------------------------------------------------------- modèles par teinte
ROT={'north':0,'east':90,'south':180,'west':270}
for p in PRE:
    tex={'m':f'airain:block/{p}airain_block','g':f'airain:block/{p}airain_catwalk','gs':f'airain:block/{p}airain_catwalk','r':f'airain:block/{p}riveted_airain','bd':f'airain:block/{p}airain_band'}
    for haut,h in (('bottom',3),('top',11)):
        modele(f'{p}airain_catwalk_floor_{haut}',plancher(h),tex); modele(f'{p}airain_catwalk_floor_solid_{haut}',plein(plancher(h)),tex)
        modele(f'{p}airain_catwalk_railing_{haut}',rambarde_nord(h),tex)
        modele(f'{p}airain_catwalk_railing_inner_{haut}',rambarde_int(h),tex)
        modele(f'{p}airain_catwalk_gate_{haut}',portillon_nord(h,False),tex)
        modele(f'{p}airain_catwalk_gate_open_{haut}',portillon_nord(h,True),tex)
        modele(f'{p}airain_catwalk_ramp_{haut}',rampe_base(h),tex); modele(f'{p}airain_catwalk_ramp_solid_{haut}',plein(rampe_base(h)),tex)
        modele(f'{p}airain_catwalk_ramp_left_{haut}',rampe_cote(h,-2),tex)
        modele(f'{p}airain_catwalk_ramp_right_{haut}',rampe_cote(h,16),tex)
    modele(f'{p}airain_catwalk_stairs',escalier_base(),tex); modele(f'{p}airain_catwalk_stairs_solid',plein(escalier_base()),tex)
    modele(f'{p}airain_catwalk_stairs_left',escalier_rampe(-2),tex)
    modele(f'{p}airain_catwalk_stairs_right',escalier_rampe(16),tex)
    modele(f'{p}airain_support',poteau_fut(),tex); modele(f'{p}airain_support_bottom',poteau_bas(),tex); modele(f'{p}airain_support_top',poteau_haut(),tex)
    modele(f'{p}airain_ladder',echelle(),tex); modele(f'{p}airain_ladder_cage',cage(),tex); modele(f'{p}airain_ladder_tunnel',tunnel(),tex)
    # objets : une pièce complète
    modele(f'{p}airain_catwalk_item',plancher(3)+rambarde_nord(3),tex)
    modele(f'{p}airain_catwalk_stairs_item',escalier_base()+escalier_rampe(-2)+escalier_rampe(16),tex)
    modele(f'{p}airain_catwalk_ramp_item',rampe_base(3)+rampe_cote(3,-2)+rampe_cote(3,16),tex)
    modele(f'{p}airain_support_item',poteau_fut()+poteau_bas()+poteau_haut(),tex)
    modele(f'{p}airain_ladder_item',echelle(),tex)
def mp(model,when=None,y=0):
    d={"apply":{"model":model}|({"y":y} if y else {})}
    if when: d["when"]=when
    return d
FAM=['airain_catwalk','airain_catwalk_stairs','airain_catwalk_ramp','airain_support','airain_ladder']
TOUS=[]
for f in FAM:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f; TOUS.append(i); M=lambda n: f'airain:block/{p}{n}'
            if f=='airain_catwalk':
                parts=[mp(M('airain_catwalk_floor_bottom'),{"top":"false","solid":"false"}),mp(M('airain_catwalk_floor_top'),{"top":"true","solid":"false"}),
                       mp(M('airain_catwalk_floor_solid_bottom'),{"top":"false","solid":"true"}),mp(M('airain_catwalk_floor_solid_top'),{"top":"true","solid":"true"})]
                for d,r in ROT.items():
                    for etat,modl in (('railing','railing'),('gate','gate'),('gate_open','gate_open'),('inner','railing_inner')):
                        for haut in ('false','true'):
                            parts.append(mp(M(f'airain_catwalk_{modl}_'+('top' if haut=='true' else 'bottom')),{d:etat,"top":haut},r))
                bs={"multipart":parts}
            elif f=='airain_catwalk_stairs':
                parts=[]
                for d,r in ROT.items():
                    parts+=[mp(M('airain_catwalk_stairs'),{"facing":d,"solid":"false"},r),mp(M('airain_catwalk_stairs_solid'),{"facing":d,"solid":"true"},r),mp(M('airain_catwalk_stairs_left'),{"facing":d,"left":"true"},r),mp(M('airain_catwalk_stairs_right'),{"facing":d,"right":"true"},r)]
                bs={"multipart":parts}
            elif f=='airain_catwalk_ramp':
                parts=[]
                for d,r in ROT.items():
                    for haut in ('false','true'):
                        hh='top' if haut=='true' else 'bottom'
                        parts+=[mp(M('airain_catwalk_ramp_'+hh),{"facing":d,"top":haut,"solid":"false"},r),mp(M('airain_catwalk_ramp_solid_'+hh),{"facing":d,"top":haut,"solid":"true"},r),mp(M('airain_catwalk_ramp_left_'+hh),{"facing":d,"top":haut,"left":"true"},r),
                                mp(M('airain_catwalk_ramp_right_'+hh),{"facing":d,"top":haut,"right":"true"},r)]
                bs={"multipart":parts}
            elif f=='airain_support':
                bs={"multipart":[mp(M('airain_support')),mp(M('airain_support_bottom'),{"bottom":"true"}),mp(M('airain_support_top'),{"top":"true"})]}
            else:
                parts=[]
                for d,r in ROT.items(): parts+=[mp(M('airain_ladder'),{"facing":d},r),mp(M('airain_ladder_cage'),{"facing":d,"cage":"cage"},r),mp(M('airain_ladder_tunnel'),{"facing":d,"cage":"full"},r)]
                bs={"multipart":parts}
            w(AS+f'blockstates/{i}.json',bs)
            w(AS+f'models/item/{i}.json',{"parent":M(f+'_item')})
            w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
w(AS+'models/item/airain_catwalk_gate.json',{"parent":"minecraft:item/generated","textures":{"layer0":"airain:item/airain_catwalk_gate"}})
# ---------------------------------------------------------------- data maps, tags
def maj(c, cle, ajout):
    d=json.load(open(c)) if os.path.exists(c) else {cle:{}}
    d.setdefault(cle,{}).update(ajout) if cle=='values' else None
    w(c,d)
ox={}; wx={}
for f in FAM:
    for s,p in enumerate(PRE):
        if s<3: ox['airain:'+p+f]={"next_oxidation_stage":'airain:'+PRE[s+1]+f}
        wx['airain:'+p+f]={"waxed":'airain:waxed_'+p+f}
for nom,ajout in (('oxidizables',ox),('waxables',wx)):
    c=Dd+f'neoforge/data_maps/block/{nom}.json'; d=json.load(open(c)); d['values'].update(ajout); w(c,d)
def tag(chemin, valeurs):
    c=Dd+chemin; old=json.load(open(c))['values'] if os.path.exists(c) else []
    w(c,{"replace":False,"values":list(dict.fromkeys(old+valeurs))})
ids=['airain:'+i for i in TOUS]
tag('minecraft/tags/block/mineable/pickaxe.json',ids); tag('minecraft/tags/block/needs_stone_tool.json',ids)
tag('minecraft/tags/block/climbable.json',[x for x in ids if 'ladder' in x])
# ---------------------------------------------------------------- recettes
RC=R+'data/airain/recipe/airain/'
it=lambda i:{"item":"airain:"+i}
w(RC+'catwalk.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["I I","GGG"],"key":{"I":it('airain_ingot'),"G":it('airain_grate')},"result":{"id":"airain:airain_catwalk","count":6}})
w(RC+'catwalk_stairs.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["C ","CC"],"key":{"C":it('airain_catwalk')},"result":{"id":"airain:airain_catwalk_stairs","count":2}})
w(RC+'catwalk_ramp.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":[it('airain_catwalk'),it('airain_catwalk'),it('airain_sheet')],"result":{"id":"airain:airain_catwalk_ramp","count":2}})
w(RC+'support.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["I","I","S"],"key":{"I":it('airain_ingot'),"S":it('airain_sheet')},"result":{"id":"airain:airain_support","count":2}})
w(RC+'ladder.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["N N","NIN","N N"],"key":{"N":it('airain_nugget'),"I":it('airain_ingot')},"result":{"id":"airain:airain_ladder","count":4}})
w(RC+'catwalk_gate.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":[it('airain_bars'),it('airain_bars'),it('airain_ingot')],"result":{"id":"airain:airain_catwalk_gate","count":1}})
for p in PRE:
    for f in FAM:
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing",
          "ingredients":[it(p+f),{"item":"minecraft:honeycomb"}],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
# ---------------------------------------------------------------- noms
NFR={'airain_catwalk':"Passerelle d'airain",'airain_catwalk_stairs':"Escalier de passerelle",'airain_catwalk_ramp':"Rampe de passerelle",'airain_support':"Poteau de soutien",'airain_ladder':"Échelle d'airain"}
NEN={'airain_catwalk':"Airain Catwalk",'airain_catwalk_stairs':"Catwalk Stairs",'airain_catwalk_ramp':"Catwalk Ramp",'airain_support':"Airain Support",'airain_ladder':"Airain Ladder"}
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
fr={"item.airain.airain_catwalk_gate":"Portillon de passerelle"}; en={"item.airain.airain_catwalk_gate":"Catwalk Gate"}
for f in FAM:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f
            fr['block.airain.'+i]=NFR[f]+SFR[s]+(' (ciré)' if c else ''); en['block.airain.'+i]=('Waxed ' if c else '')+SEN[s]+NEN[f]
L=R+'assets/airain/lang/'
for fn,d in (('fr_fr.json',fr),('en_us.json',en)):
    j=json.load(open(L+fn)); j.update(d); json.dump(j,open(L+fn,'w'),ensure_ascii=False,indent=1)
print('passerelles ok', len(TOUS))
