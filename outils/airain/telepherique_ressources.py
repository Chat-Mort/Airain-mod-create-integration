# Ressources 1.58 : téléphérique (gare, pylône, tête de pylône, nacelle, câble) et laminoir (fil d'airain).
import json, os, math
D=os.path.dirname(os.path.abspath(__file__))
_a=open(D+'/atelier_ressources.py').read()
exec(_a[:_a.index('# ---------------------------------------------------------------- textures')])
from PIL import Image
ROT={'north':0,'east':90,'south':180,'west':270}
T=dict(tex(''),r='airain:block/riveted_airain',g='airain:block/airain_catwalk',c='airain:block/airain_cable_strand')
def butin(i):
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
def tourne_y(e, centre, angle):
    """Rotation d'un élément autour de l'axe vertical passant par centre (angles de -45 à 45 seulement, par pas de 22,5)."""
    e["rotation"]={"origin":centre,"axis":"y","angle":angle}
    return e
# ---------------------------------------------------------------- textures nouvelles
TB='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/'
OR=[(0x6b,0x47,0x1c),(0x9a,0x6c,0x2c),(0xc8,0x98,0x48),(0xe8,0xc2,0x72),(0xf8,0xe2,0xa8)]
def toron():
    """Câble toronné : torons en biais, clair en haut à gauche de chaque brin."""
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            k=(x+y)%4
            p[x,y]=OR[[1,3,2,0][k]]+(255,)
    return im
toron().save(TB+'block/airain_cable_strand.png')
def bobine(epais, nom):
    """Bobine de fil (ou de câble) : spires d'airain sur un moyeu, vue de trois quarts."""
    im=Image.new('RGBA',(16,16)); p=im.load()
    cx,cy=7.5,8.5
    for y in range(16):
        for x in range(16):
            dx,dy=(x-cx)/6.6,(y-cy)/5.2
            r=math.hypot(dx,dy)
            if r<=1.0:
                if r<0.32: p[x,y]=(0x3a,0x26,0x12,255) if r<0.2 else OR[0]+(255,)
                else:
                    spire=int(r*(10 if epais else 14))%2
                    clair=(dx+dy)<-0.2
                    p[x,y]=OR[(3 if clair else 2) if spire==0 else (2 if clair else 1)]+(255,)
                    if r>0.92: p[x,y]=OR[0]+(255,)
    for x in range(12,16):                       # bout de fil qui pend
        y=9+(x-12)//1
        if y<16: p[x,y]=OR[3]+(255,);
        if y+1<16 and epais: p[x,y+1]=OR[1]+(255,)
    im.save(TB+f'item/{nom}.png')
bobine(False,'airain_wire'); bobine(True,'airain_cable')
def icone_nacelle():
    """Nacelle : plateforme à rambardes pendue à son chariot."""
    M=["......####......",
       ".....#oooo#.....",
       "......#..#......",
       ".......##.......",
       ".......##.......",
       ".......##.......",
       "..##########....",
       "..#........#....",
       "..#.##..##.#....",
       "..#........#....",
       ".##############.",
       ".#gggggggggggg#.",
       ".##############.",
       "................",
       "................",
       "................"]
    C={'#':OR[1],'o':(0x8a,0x2a,0x1c),'g':OR[3]}
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y,l in enumerate(M):
        for x,ch in enumerate(l):
            if ch in C: p[x,y]=C[ch]+(255,)
            if ch=='#' and (y in (0,6,10) or x in (2,1)): p[x,y]=OR[3]+(255,)
    im.save(TB+'item/airain_gondola.png')
icone_nacelle()
# ---------------------------------------------------------------- gare
def gare_bas():
    return [el([0,0,0],[16,6,16],'#r',uv='crop'),el([1,6,1],[15,8,15],'#bd'),el([5,8,5],[11,16,11],'#m'),
            el([4,8,4],[12,9,12],'#rg'),el([12,1,5],[16,5,11],'#pn',faces=("east","up","north","south"),uv='crop')]   # plaque du moteur
def gare_haut():
    return [el([5,0,5],[11,10,11],'#m'),el([4,9,4],[12,11,12],'#bd'),el([6,11,6],[10,12.5,10],'#rg')]
def poulie():
    """Grande poulie horizontale (diamètre 3 blocs), gorge rouge à hauteur du câble ; dessinée dans le bloc du haut."""
    E=[]; c=[8,13.5,8]
    R=22.5
    for k in range(16):
        a=k*22.5
        base=round(a/90)%4; reste=a-round(a/90)*90           # -45..45
        # segment de jante tangent, posé au nord du centre, puis tourné
        seg=[el([8-4.6,12.5,8-R-1.5],[8+4.6,16,8-R],'#bd',faces=("north","up","down")),
             el([8-4.6,13.6,8-R-0.2],[8+4.6,15.2,8-R],'#c',faces=("north",))]
        for e in seg:
            # rotation de base par quart de tour (exacte), puis le reste par l'élément
            for _ in range(base):
                f,t=e['from'],e['to']
                e['from'],e['to']=[16-t[2],f[1],f[0]],[16-f[2],t[1],t[0]]
                e['faces']={{'north':'east','east':'south','south':'west','west':'north'}.get(kk,kk):v for kk,v in e['faces'].items()}
            if reste: tourne_y(e,c,-reste)
            E.append(e)
    for a in (0,45):                                        # rayons
        E.append(tourne_y(el([8-R,13,7.25],[8+R,14,8.75],'#m'),c,a) if a else el([8-R,13,7.25],[8+R,14,8.75],'#m'))
        E.append(tourne_y(el([7.25,13,8-R],[8.75,14,8+R],'#m'),c,a) if a else el([7.25,13,8-R],[8.75,14,8+R],'#m'))
    E+=[el([5,12.5,5],[11,15,11],'#rg'),el([6,15,6],[10,16,10],'#bd')]   # moyeu
    return E
modele('airain_cable_station',gare_bas(),dict(T))
modele('airain_cable_station_upper',gare_haut(),dict(T))
modele('airain_cable_station/wheel',poulie(),dict(T))
modele('airain_cable_station_item',gare_bas()+[dict(e,**{"from":[e['from'][0],e['from'][1]-0,e['from'][2]],"to":e['to']}) for e in []],dict(T))
w(AS+'blockstates/airain_cable_station.json',{"variants":{f"facing={d},upper={u}":{"model":"airain:block/airain_cable_station"+("_upper" if u=="true" else "")}|({"y":r} if r else {}) for d,r in ROT.items() for u in ("false","true")}})
w(Dd+'airain/loot_table/blocks/airain_cable_station.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:airain_cable_station"}],
   "conditions":[{"condition":"minecraft:survives_explosion"}]}]})      # une seule moitié reste : l'autre part sans butin
# ---------------------------------------------------------------- pylône et tête
def pylone():
    E=[]
    for (x,z) in ((2,2),(12,2),(2,12),(12,12)): E.append(el([x,0,z],[x+2,16,z+2],'#ro',faces=("north","south","east","west"),uv={k:[7,0,9,16] for k in ("north","south","east","west")}))
    for y in (0,8):
        E+=[el([4,y,2.5],[12,y+1,3.5],'#bd'),el([4,y,12.5],[12,y+1,13.5],'#bd'),el([2.5,y,4],[3.5,y+1,12],'#bd'),el([12.5,y,4],[13.5,y+1,12],'#bd')]
    for (a,z) in ((22.5,3),(-22.5,13)):                    # contreventements en croix (faces avant et arrière)
        E.append(el([3,4,z-0.5],[13,5,z+0.5],'#bd',rot=([8,4.5,z],'z',a)))
        E.append(el([3,12,z-0.5],[13,13,z+0.5],'#bd',rot=([8,12.5,z],'z',-a)))
    return E
def tete():
    """Chapiteau riveté, bras transversal (de part et d'autre de la ligne) et deux galets où passe le câble."""
    E=[el([0,0,0],[16,3,16],'#r',uv='crop'),el([2,3,2],[14,6,14],'#m'),
       el([-16,6,6],[32,8,10],'#bd'),el([-16,5,6.5],[32,6,9.5],'#m')]
    for x0 in (-16,28.5):
        E+=[el([x0,8,4],[x0+3.5,11,12],'#rg'),el([x0+0.5,11,5],[x0+3,12,11],'#m')]       # galets (le câble roule dessus à 12 px)
    E+=[el([5,6,5],[11,8,11],'#bd'),el([-1,3,7],[2,6,9],'#bd'),el([14,3,7],[17,6,9],'#bd')]
    return E
modele('airain_pylon',pylone(),dict(T)); modele('airain_pylon_head',tete(),dict(T))
modele('airain_pylon_head_item',[e for e in tete() if e['from'][0]>=-3 and e['to'][0]<=19],dict(T))
w(AS+'blockstates/airain_pylon.json',{"variants":{"":{"model":"airain:block/airain_pylon"}}})
w(AS+'blockstates/airain_pylon_head.json',{"variants":{f"facing={d}":{"model":"airain:block/airain_pylon_head"}|({"y":r} if r else {}) for d,r in ROT.items()}})
# ---------------------------------------------------------------- laminoir (sortie au nord ; rouleaux sur l'axe est-ouest)
def laminoir():
    E=[el([0,0,0],[16,4,16],'#r',uv='crop'),el([1,4,2],[4,15,14],'#pn',uv='crop'),el([12,4,2],[15,15,14],'#pn',uv='crop'),
       el([1,15,1],[15,16,15],'#bd'),
       el([4,9,12],[12,10,16],'#m'),el([4,10,15],[12,11,16],'#bd'),                   # table d'entrée (au sud)
       el([4,8,0],[12,9,4],'#m'),el([4,7,0],[12,8,1],'#bd'),                          # goulotte de sortie (au nord)
       el([1,11,4],[4,13,12],'#rg'),el([12,11,4],[15,13,12],'#rg')]                   # vis de serrage
    return E
def rouleau(yc):
    return [el([4,yc-1.75,6.25],[12,yc+1.75,9.75],'#rg'),el([3.5,yc-1,7],[4,yc+1,9],'#m'),el([12,yc-1,7],[12.5,yc+1,9],'#m')]
modele('airain_rolling_mill',laminoir(),dict(T))
modele('airain_rolling_mill/roller_low',rouleau(9.25),dict(T)); modele('airain_rolling_mill/roller_high',rouleau(11.75),dict(T))
modele('airain_rolling_mill_item',laminoir()+rouleau(9.25)+rouleau(11.75),dict(T))
w(AS+'blockstates/airain_rolling_mill.json',{"variants":{f"facing={d}":{"model":"airain:block/airain_rolling_mill"}|({"y":r} if r else {}) for d,r in ROT.items()}})
# ---------------------------------------------------------------- nacelle (plateforme 2 × 2 centrée sur (8, 8) ; portillon côté +x)
def plateforme():
    x0,x1,z0,z1=-8,24,-8,24
    E=[el([x0,0,z0],[x1,2,z1],'#g',faces=("up","down"),uv='full'),
       el([x0,0,z0],[x1,2,z0+1],'#bd'),el([x0,0,z1-1],[x1,2,z1],'#bd'),el([x0,0,z0+1],[x0+1,2,z1-1],'#bd'),el([x1-1,0,z0+1],[x1,2,z1-1],'#bd')]
    for (px,pz) in ((x0,z0),(x1-1.5,z0),(x0,z1-1.5),(x1-1.5,z1-1.5),(x0,7.25),(x1-1.5,7.25)):
        E.append(el([px,2,pz],[px+1.5,15,pz+1.5],'#m'))
    for (a0,a1,c0,c1) in ((x0+1.5,x1-1.5,z0,z0+1.5),(x0+1.5,x1-1.5,z1-1.5,z1)):           # rambardes avant et arrière
        E+=[el([a0,13,c0],[a1,15,c1],'#m'),el([a0,7.5,c0+0.25],[a1,8.5,c1-0.25],'#m')]
    E+=[el([x0,13,z0+1.5],[x0+1.5,15,z1-1.5],'#m'),el([x0+0.25,7.5,z0+1.5],[x0+1.25,8.5,z1-1.5],'#m')]   # rambarde côté -x
    for (c0,c1) in ((z0+1.5,7.25),(8.75,z1-1.5)):                                           # deux battants de portillon côté +x
        E+=[el([x1-1.5,12,c0],[x1,13,c1],'#m'),el([x1-1.5,3,c0],[x1,4,c1],'#m'),el([x1-1.25,7.5,c0],[x1-0.25,8.5,c1],'#rg')]
    return E
def bras():
    """Suspente : mât central du plancher au chariot, entretoise en V."""
    return [el([7,2,7],[9,28,9],'#ro',faces=("north","south","east","west"),uv={k:[7,0,9,16] for k in ("north","south","east","west")}),
            el([6,2,6],[10,3,10],'#bd'),el([6.5,26,1],[9.5,28,15],'#bd'),
            el([7.5,9,7],[8.5,27,8],'#m',rot=([8,18,8],'x',22.5)),el([7.5,9,8],[8.5,27,9],'#m',rot=([8,18,8],'x',-22.5))]
def chariot():
    """Chariot : caisson sous le câble, deux galets dessus (le câble passe à y = 0)."""
    return [el([5.5,-4.5,1],[10.5,-0.5,15],'#pn',uv='crop'),el([6,-0.5,2.5],[10,0,13.5],'#bd'),
            el([6.5,-0.4,2.5],[9.5,2.6,5.5],'#rg'),el([6.5,-0.4,10.5],[9.5,2.6,13.5],'#rg'),
            el([7.25,0,2],[8.75,3,3],'#m'),el([7.25,0,13],[8.75,3,14],'#m')]
modele('airain_gondola/platform',plateforme(),dict(T)); modele('airain_gondola/arm',bras(),dict(T)); modele('airain_gondola/carriage',chariot(),dict(T))
# ---------------------------------------------------------------- objets
for i,m in (('airain_cable_station','airain_cable_station_item'),('airain_pylon','airain_pylon'),('airain_pylon_head','airain_pylon_head_item'),('airain_rolling_mill','airain_rolling_mill_item')):
    w(AS+f'models/item/{i}.json',{"parent":"airain:block/"+m})
for i in ('airain_wire','airain_cable','airain_gondola'):
    w(AS+f'models/item/{i}.json',{"parent":"minecraft:item/generated","textures":{"layer0":"airain:item/"+i}})
for i in ('airain_pylon','airain_pylon_head','airain_rolling_mill'): butin(i)
p=Dd+'minecraft/tags/block/mineable/pickaxe.json'; d=json.load(open(p))
for i in ('airain_cable_station','airain_pylon','airain_pylon_head','airain_rolling_mill'):
    if 'airain:'+i not in d['values']: d['values'].append('airain:'+i)
w(p,d)
# ---------------------------------------------------------------- recettes
R=Dd+'airain/recipe/telepherique/'
def it(i): return {"item":i if ':' in i else 'airain:'+i}
def forme(nom,pat,cle,res,n=1):
    w(R+nom+'.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":pat,"key":{k:it(v) for k,v in cle.items()},"result":{"id":"airain:"+res,"count":n}})
forme('rolling_mill',["PGP","SCS","PPP"],{"P":"airain_sheet","G":"airain_gear","S":"create:shaft","C":"create:andesite_casing"},'airain_rolling_mill')
forme('cable',["FFF","FPF","FFF"],{"F":"airain_wire","P":"airain_sheet"},'airain_cable',2)
forme('cable_station',["GAG","PCP","PSP"],{"G":"airain_gear","A":"airain_block","P":"airain_sheet","C":"create:brass_casing","S":"create:shaft"},'airain_cable_station')
forme('pylon',["B B","BSB","B B"],{"B":"airain_bars","S":"airain_sheet"},'airain_pylon',4)
forme('pylon_head',["PPP","WBW"," B "],{"P":"airain_sheet","W":"create:cogwheel","B":"airain_bars"},'airain_pylon_head')
forme('gondola',["BCB","BGB","WWW"],{"B":"airain_bars","C":"airain_chain","G":"airain_gear","W":"airain_catwalk"},'airain_gondola')
# ---------------------------------------------------------------- noms et messages
FR={"block.airain.airain_cable_station":"Gare de téléphérique","block.airain.airain_pylon":"Pylône d'airain","block.airain.airain_pylon_head":"Tête de pylône",
    "block.airain.airain_rolling_mill":"Laminoir","item.airain.airain_wire":"Fil d'airain","item.airain.airain_cable":"Câble d'airain","item.airain.airain_gondola":"Nacelle de téléphérique",
    "entity.airain.airain_gondola":"Nacelle",
    "airain.telepherique.cable_aide":"Clic droit sur une gare ou une tête de pylône, puis sur le nœud suivant (32 blocs au plus)",
    "airain.telepherique.nacelle_aide":"Clic droit sur une gare d'une ligne complète",
    "airain.telepherique.depart":"Câble accroché : clic droit sur le nœud suivant","airain.telepherique.annule":"Accroche annulée",
    "airain.telepherique.relie":"Travée posée","airain.telepherique.complete_ok":"Ligne complète : posez une nacelle sur une gare",
    "airain.telepherique.perdu":"Le premier nœud a disparu","airain.telepherique.loin":"Trop loin : 32 blocs au plus entre deux nœuds",
    "airain.telepherique.pres":"Trop près : 3 blocs au moins entre deux nœuds","airain.telepherique.plein":"Ces deux nœuds ne peuvent pas être reliés (déjà pris, ou une gare au milieu)",
    "airain.telepherique.long":"Ligne trop longue : 8 pylônes au plus","airain.telepherique.incomplete":"Ligne incomplète : il faut une gare à chaque bout",
    "airain.telepherique.ligne":"Ligne : %s pylône(s), %s blocs","airain.telepherique.sans_nacelle":"Pas de nacelle sur cette ligne",
    "airain.telepherique.deja":"Cette ligne a déjà sa nacelle","airain.telepherique.appel":"La nacelle arrive",
    "airain.telepherique.la":"La nacelle est déjà là","airain.telepherique.immobile":"Aucune gare n'est entraînée",
    "airain.telepherique.complet":"La nacelle est pleine","airain.telepherique.depart_proche":"Départ dans deux secondes",
    "airain.laminoir.etat":"Lingots : %s · fil : %s","airain.laminoir.progres":"Laminage : %s %%"}
EN={"block.airain.airain_cable_station":"Cable Car Station","block.airain.airain_pylon":"Airain Pylon","block.airain.airain_pylon_head":"Pylon Head",
    "block.airain.airain_rolling_mill":"Rolling Mill","item.airain.airain_wire":"Airain Wire","item.airain.airain_cable":"Airain Cable","item.airain.airain_gondola":"Cable Car Gondola",
    "entity.airain.airain_gondola":"Gondola",
    "airain.telepherique.cable_aide":"Right-click a station or pylon head, then the next node (32 blocks at most)",
    "airain.telepherique.nacelle_aide":"Right-click a station of a complete line",
    "airain.telepherique.depart":"Cable attached: right-click the next node","airain.telepherique.annule":"Attachment cancelled",
    "airain.telepherique.relie":"Span laid","airain.telepherique.complete_ok":"Line complete: place a gondola on a station",
    "airain.telepherique.perdu":"The first node is gone","airain.telepherique.loin":"Too far: 32 blocks at most between two nodes",
    "airain.telepherique.pres":"Too close: at least 3 blocks between two nodes","airain.telepherique.plein":"These two nodes cannot be linked (already taken, or a station in the middle)",
    "airain.telepherique.long":"Line too long: 8 pylons at most","airain.telepherique.incomplete":"Incomplete line: a station is needed at each end",
    "airain.telepherique.ligne":"Line: %s pylon(s), %s blocks","airain.telepherique.sans_nacelle":"No gondola on this line",
    "airain.telepherique.deja":"This line already has its gondola","airain.telepherique.appel":"The gondola is coming",
    "airain.telepherique.la":"The gondola is already here","airain.telepherique.immobile":"No station is powered",
    "airain.telepherique.complet":"The gondola is full","airain.telepherique.depart_proche":"Departing in two seconds",
    "airain.laminoir.etat":"Ingots: %s · wire: %s","airain.laminoir.progres":"Rolling: %s%%"}
for f,Dct in (('fr_fr.json',FR),('en_us.json',EN)):
    p=AS+'lang/'+f; d=json.load(open(p)); d.update(Dct); w(p,d)
print('téléphérique ok')
