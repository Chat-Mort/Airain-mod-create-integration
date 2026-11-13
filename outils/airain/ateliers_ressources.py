# Ressources 1.50 : escalier à palier, suspente, rambarde seule, conduite d'air (conduit + bouche).
import json, os
_s=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'passerelles_ressources.py')).read()
exec(_s[:_s.index('# ---------------------------------------------------------------- modèles par teinte')])
def tag(chemin, valeurs):
    c=Dd+chemin; old=json.load(open(c))['values'] if os.path.exists(c) else []
    w(c,{"replace":False,"values":list(dict.fromkeys(old+valeurs))})
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
ROT={'north':0,'east':90,'south':180,'west':270}
def mp(model,when=None,y=0,x=0):
    d={"apply":{"model":model}|({"y":y} if y else {})|({"x":x} if x else {})}
    if when: d["when"]=when
    return d
def miroir(E):
    """Miroir est-ouest (x → 16-x) d'une liste d'éléments sans rotation."""
    out=[]
    for e in E:
        e=json.loads(json.dumps(e)); a,b=e['from'][0],e['to'][0]
        e['from'][0],e['to'][0]=round(16-b,3),round(16-a,3)
        f=e['faces']; f['east'],f['west']=f.get('west'),f.get('east')
        e['faces']={k:v for k,v in f.items() if v}
        out.append(e)
    return out
# ---------------------------------------------------------------- géométrie
def dalle(x0,z0,x1,z1,h):
    """Un morceau de caillebotis encadré, dessus à h."""
    return [el([x0,h-2,z0],[x1,h,z1],'#g',faces=("up","down"),full=True),
            el([x0,h-2,z0],[x1,h,z0+1]),el([x0,h-2,z1-1],[x1,h,z1]),el([x0,h-2,z0+1],[x0+1,h,z1-1]),el([x1-1,h-2,z0+1],[x1,h,z1-1])]
def palier():
    # entrée au sud (3 px), palier à 11 px, sortie à l'est (19 px) ; poteau d'angle au sud-est
    E=dalle(1,12,12,16,7)+dalle(0,0,12,12,11)+dalle(12,1,16,12,15)
    E+=[el([12,0,12],[16,1,16]),el([12.5,1,12.5],[15.5,24,15.5],'#r'),el([12,24,12],[16,25,16]),
        el([12.5,9,11.5],[15.5,10,12.5]),el([11.5,5,12.5],[12.5,6,15.5])]          # poteau, chapeau et goussets sous les marches
    return E
def rambarde_ouest(h):
    return [el([0,h+11,0],[2,h+13,16]),el([0.5,h+6,0],[1.5,h+7,16]),el([0.5,h,0],[1,h+3,16]),el([0,h,14],[2,h+13,16])]
def suspente_tiges():
    E=[]
    for z0 in (2.5,12.5):
        E+=[el([7.5,0,z0],[8.5,16,z0+1]),el([7,6,z0-0.5],[9,9,z0+1.5])]      # tirant et ridoir
    return E
def suspente_plaque():
    return [el([5,15,1],[11,16,15],'#r'),el([7,14,2],[9,15,4]),el([7,14,12],[9,15,14])]
def suspente_etrier(h):
    """h : dessus de la traverse (sous le plancher du bloc du dessous), en coordonnées de la suspente."""
    E=[el([7,h-1,1.5],[9,h,14.5])]
    for z0 in (2.5,12.5): E+=[el([7.5,h,z0],[8.5,0,z0+1]),el([7.25,h-1.5,z0-0.25],[8.75,h-1,z0+1.25])]
    return E
def rambarde_seule():
    return rambarde_nord(0)+[el([14,0,0],[16,13,2])]
SANS_BOUTS=("east","west","up","down")
def conduit_coeur(): return [el([3,3,3],[13,13,13])]
def conduit_bras(): return [el([3,3,0],[13,13,3],faces=SANS_BOUTS),el([2,2,0],[14,14,1],'#r')]
def bouche():
    E=[el([2,2,14],[14,14,16],'#r'),el([3,3,6],[13,13,14],faces=SANS_BOUTS),
       el([1,13,0],[15,15,6]),el([1,1,0],[15,3,6]),el([1,3,0],[3,13,6]),el([13,3,0],[15,13,6]),
       el([3,3,5],[13,13,6],'#d',faces=("north",))]
    for yy in (4,6.5,9,11.5): E.append(el([3,yy,1],[13,yy+1,4],rot=([8,yy+0.5,2.5],'x',-22.5)))
    return E
# ---------------------------------------------------------------- modèles
for p in PRE:
    tex={'m':f'airain:block/{p}airain_block','g':f'airain:block/{p}airain_catwalk','r':f'airain:block/{p}riveted_airain'}
    modele(f'{p}airain_catwalk_landing_right',palier(),tex); modele(f'{p}airain_catwalk_landing_right_solid',plein(palier()),tex)
    modele(f'{p}airain_catwalk_landing_left',miroir(palier()),tex); modele(f'{p}airain_catwalk_landing_left_solid',plein(miroir(palier())),tex)
    modele(f'{p}airain_catwalk_landing_item',palier()+rambarde_nord(11)+rambarde_ouest(11),tex)
    modele(f'{p}airain_hanger',suspente_tiges(),tex); modele(f'{p}airain_hanger_plate',suspente_plaque(),tex)
    modele(f'{p}airain_hanger_low',suspente_etrier(-15),tex); modele(f'{p}airain_hanger_high',suspente_etrier(-7),tex)
    modele(f'{p}airain_hanger_item',suspente_tiges()+suspente_plaque(),tex)
    modele(f'{p}airain_railing',rambarde_seule(),tex); modele(f'{p}airain_railing_item',rambarde_seule(),tex)
texc={'m':'airain:block/airain_block','r':'airain:block/riveted_airain','d':'airain:block/oxidized_airain_block'}
modele('airain_air_duct_core',conduit_coeur(),texc); modele('airain_air_duct_arm',conduit_bras(),texc)
modele('airain_air_duct_item',conduit_coeur()+conduit_bras()+[dict(e,**{"from":[e['from'][0],e['from'][1],16-e['to'][2]],"to":[e['to'][0],e['to'][1],16-e['from'][2]]}) for e in conduit_bras()],texc)
modele('airain_air_vent',bouche(),texc)
# ---------------------------------------------------------------- blockstates, objets, butin
DIR6={'north':(0,0),'east':(0,90),'south':(0,180),'west':(0,270),'up':(270,0),'down':(90,0)}
NFAM=['airain_catwalk_landing','airain_hanger','airain_railing']
NOUV=[]
def butin(i,pools=None):
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":pools or [{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
for f in NFAM:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f; NOUV.append(i); M=lambda n: f'airain:block/{p}{n}'
            parts=[]
            if f=='airain_catwalk_landing':
                for d,r in ROT.items():
                    for g,cote in (('false','right'),('true','left')):
                        parts+=[mp(M(f'airain_catwalk_landing_{cote}'),{"facing":d,"turn_left":g,"solid":"false"},r),mp(M(f'airain_catwalk_landing_{cote}_solid'),{"facing":d,"turn_left":g,"solid":"true"},r)]
                    for etat in ('railing','gate','gate_open'): parts.append(mp(M(f'airain_catwalk_{etat}_top'),{d:etat},r))
                butin(i)
            elif f=='airain_hanger':
                for ax,r in (('x',0),('z',90)):
                    parts+=[mp(M('airain_hanger'),{"axis":ax},r),mp(M('airain_hanger_plate'),{"axis":ax,"plate":"true"},r),
                            mp(M('airain_hanger_low'),{"axis":ax,"stirrup":"low"},r),mp(M('airain_hanger_high'),{"axis":ax,"stirrup":"high"},r)]
                butin(i)
            else:
                for d,r in ROT.items(): parts.append(mp(M('airain_railing'),{d:"true"},r))
                butin(i,[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],
                          "conditions":[{"condition":"minecraft:survives_explosion"},{"condition":"minecraft:block_state_property","block":"airain:"+i,"properties":{d:"true"}}]} for d in ROT])
            w(AS+f'blockstates/{i}.json',{"multipart":parts})
            w(AS+f'models/item/{i}.json',{"parent":M(f+'_item')})
w(AS+'blockstates/airain_air_duct.json',{"multipart":[mp('airain:block/airain_air_duct_core')]+[mp('airain:block/airain_air_duct_arm',{d:"true"},y,x) for d,(x,y) in DIR6.items()]})
w(AS+'blockstates/airain_air_vent.json',{"variants":{f"facing={d}":{"model":"airain:block/airain_air_vent"}|({"x":x} if x else {})|({"y":y} if y else {}) for d,(x,y) in DIR6.items()}})
w(AS+'models/item/airain_air_duct.json',{"parent":"airain:block/airain_air_duct_item"}); w(AS+'models/item/airain_air_vent.json',{"parent":"airain:block/airain_air_vent"})
butin('airain_air_duct'); butin('airain_air_vent')
# ---------------------------------------------------------------- data maps, tags, recettes
ox={}; wx={}
for f in NFAM:
    for s,p in enumerate(PRE):
        if s<3: ox['airain:'+p+f]={"next_oxidation_stage":'airain:'+PRE[s+1]+f}
        wx['airain:'+p+f]={"waxed":'airain:waxed_'+p+f}
for nom,ajout in (('oxidizables',ox),('waxables',wx)):
    c=Dd+f'neoforge/data_maps/block/{nom}.json'; d=json.load(open(c)); d['values'].update(ajout); w(c,d)
ids=['airain:'+i for i in NOUV]+['airain:airain_air_duct','airain:airain_air_vent']
tag('minecraft/tags/block/mineable/pickaxe.json',ids); tag('minecraft/tags/block/needs_stone_tool.json',ids)
RC=R+'data/airain/recipe/airain/'
it=lambda i:{"item":"airain:"+i}
w(RC+'catwalk_landing.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":[it('airain_catwalk_stairs'),it('airain_catwalk'),it('airain_support')],"result":{"id":"airain:airain_catwalk_landing","count":1}})
w(RC+'hanger.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["SSS","N N","N N"],"key":{"S":it('airain_sheet'),"N":it('airain_nugget')},"result":{"id":"airain:airain_hanger","count":4}})
w(RC+'railing.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["NNN","I I"],"key":{"N":it('airain_nugget'),"I":it('airain_ingot')},"result":{"id":"airain:airain_railing","count":6}})
w(RC+'air_duct.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["SSS","   ","SSS"],"key":{"S":it('airain_sheet')},"result":{"id":"airain:airain_air_duct","count":8}})
w(RC+'air_vent.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["SBS"," D "],"key":{"S":it('airain_sheet'),"B":it('airain_bars'),"D":it('airain_air_duct')},"result":{"id":"airain:airain_air_vent","count":1}})
for p in PRE:
    for f in NFAM:
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing",
          "ingredients":[it(p+f),{"item":"minecraft:honeycomb"}],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
# ---------------------------------------------------------------- noms
NFR={'airain_catwalk_landing':"Escalier à palier",'airain_hanger':"Suspente d'airain",'airain_railing':"Rambarde d'airain"}
NEN={'airain_catwalk_landing':"Catwalk Landing Stairs",'airain_hanger':"Airain Hanger",'airain_railing':"Airain Railing"}
fr={"block.airain.airain_air_duct":"Conduit d'air","block.airain.airain_air_vent":"Bouche d'air",
    "airain.conduit.trop_long":"Réseau trop long (plus de %s conduits)","airain.conduit.muet":"Aucun ventilateur ne souffle dans le conduit",
    "airain.conduit.souffle":"Soufflage : %s tr/min, comme le ventilateur","airain.conduit.aspire":"Aspiration : %s tr/min, comme le ventilateur","airain.conduit.portee":"Portée : %s blocs"}
en={"block.airain.airain_air_duct":"Air Duct","block.airain.airain_air_vent":"Air Vent",
    "airain.conduit.trop_long":"Network too long (over %s ducts)","airain.conduit.muet":"No fan is blowing into the duct",
    "airain.conduit.souffle":"Pushing: %s RPM, same as the fan","airain.conduit.aspire":"Pulling: %s RPM, same as the fan","airain.conduit.portee":"Range: %s blocks"}
for f in NFAM:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f
            fr['block.airain.'+i]=NFR[f]+SFR[s]+(' (ciré)' if c else ''); en['block.airain.'+i]=('Waxed ' if c else '')+SEN[s]+NEN[f]
L=R+'assets/airain/lang/'
for fn,d in (('fr_fr.json',fr),('en_us.json',en)):
    j=json.load(open(L+fn)); j.update(d); json.dump(j,open(L+fn,'w'),ensure_ascii=False,indent=1)
print('ateliers ok', len(NOUV)+2)
