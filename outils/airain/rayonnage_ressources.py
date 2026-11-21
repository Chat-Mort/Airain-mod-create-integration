# 1.62 : ressources du rayonnage impérial (modèles raccordés, renforts, butin qui garde le contenu, recettes, noms, livre).
import json, os
from PIL import Image, ImageDraw
R='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=R+'assets/airain/'; Dd=R+'data/'
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
ALL=("north","south","east","west","up","down")
def el(fr,to,t,faces=ALL):
    f={}
    for k in faces:
        dx,dy,dz=[abs(to[i]-fr[i]) for i in range(3)]
        a,b={"north":(dx,dy),"south":(dx,dy),"east":(dz,dy),"west":(dz,dy),"up":(dx,dz),"down":(dx,dz)}[k]
        tt=t+'v' if t in ('#f',) and b>a+0.01 else t
        a=min(16,a); b=min(16,b); u0=(16-a)/2; v0=(16-b)/2
        f[k]={"texture":tt,"uv":[round(u0,3),round(v0,3),round(u0+a,3),round(v0+b,3)]}
    return {"from":fr,"to":to,"faces":f}
TEX={'f':'airain:block/airain_beam_flange','fv':'airain:block/airain_beam_flange_vertical','bd':'airain:block/airain_band','g':'airain:block/airain_grate','r':'airain:block/airain_rod','particle':'airain:block/airain_band'}
def modele(nom,E): w(AS+f'models/block/{nom}.json',{"parent":"minecraft:block/block","render_type":"minecraft:cutout","ambientocclusion":False,"textures":TEX,"elements":E})
# dessiné tourné vers le nord (face avant à z = 0) : la gauche de celui qui regarde est du côté x = 16
def montants(x0): return [el([x0,0,1],[x0+1.5,16,2.5],'#f'),el([x0,0,13.5],[x0+1.5,16,15],'#f')]
def entretoises(x0): return [el([x0,6,2.5],[x0+1,7,13.5],'#r'),el([x0,12,2.5],[x0+1,13,13.5],'#r')]
base=[el([0,0,0.5],[16,3,2.5],'#bd'),el([0,0,13.5],[16,3,15.5],'#bd'),el([1,2.4,2.5],[15,2.9,13.5],'#g',("up","down"))]+montants(14.5)
modele('airain_rack',base)
modele('airain_rack_right_end',montants(0))
modele('airain_rack_left_end',entretoises(14.75))
modele('airain_rack_right_braces',entretoises(0.25))
modele('airain_rack_top',[el([0,14.5,0.5],[16,16,2.5],'#bd'),el([0,14.5,13.5],[16,16,15.5],'#bd')])
w(AS+'models/block/airain_rack_item.json',{"parent":"minecraft:block/block","render_type":"minecraft:cutout","ambientocclusion":False,"textures":TEX,
  "elements":base+montants(0)+entretoises(14.75)+entretoises(0.25)+[el([0,14.5,0.5],[16,16,2.5],'#bd'),el([0,14.5,13.5],[16,16,15.5],'#bd')]})
ROT={'north':0,'east':90,'south':180,'west':270}
def mp(m,when,y): d={"apply":{"model":m}|({"y":y} if y else {})}; d["when"]=when; return d
parts=[]
for f,y in ROT.items():
    parts+=[mp('airain:block/airain_rack',{"facing":f},y),mp('airain:block/airain_rack_right_end',{"facing":f,"right_end":"true"},y),
            mp('airain:block/airain_rack_right_braces',{"facing":f,"right_end":"true"},y),mp('airain:block/airain_rack_left_end',{"facing":f,"left_end":"true"},y),
            mp('airain:block/airain_rack_top',{"facing":f,"top":"true"},y)]
w(AS+'blockstates/airain_rack.json',{"multipart":parts})
w(AS+'models/item/airain_rack.json',{"parent":"airain:block/airain_rack_item"})
# renforts : plaque d'airain à 1, 2, 3 ou 4 tétons (or, or, bleu acier, rouge impérial)
COUL=[(232,196,110),(232,196,110),(140,190,240),(214,64,48)]
for n in range(1,5):
    im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([1,5,14,11],fill=(96,62,30,255)); d.rectangle([1,5,13,10],fill=(201,154,81,255)); d.rectangle([1,5,13,5],fill=(250,226,160,255)); d.rectangle([1,5,1,10],fill=(243,214,148,255))
    d.rectangle([2,11,14,11],fill=(87,51,29,255)); d.rectangle([14,6,14,11],fill=(112,68,37,255))
    x0=8-(n*3-1)//2
    for k in range(n):
        c=COUL[n-1]; x=x0+k*3
        d.rectangle([x,7,x+1,8],fill=c+(255,)); d.point((x,7),fill=(255,245,220,255)); d.point((x+1,8),fill=tuple(int(v*0.6) for v in c)+(255,))
    im.save(AS+f'textures/item/rack_reinforcement_{n}.png')
    w(AS+f'models/item/rack_reinforcement_{n}.json',{"parent":"minecraft:item/generated","textures":{"layer0":f"airain:item/rack_reinforcement_{n}"}})
# butin : le casier cassé garde son contenu
w(Dd+'airain/loot_table/blocks/airain_rack.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:airain_rack",
  "functions":[{"function":"minecraft:copy_components","source":"block_entity","include":["minecraft:custom_data"]}]}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
p=Dd+'minecraft/tags/block/mineable/pickaxe.json'; d=json.load(open(p))
if 'airain:airain_rack' not in d['values']: d['values'].append('airain:airain_rack')
w(p,d)
RC=Dd+'airain/recipe/rayonnage/'
it=lambda i:{"item":i if ':' in i else 'airain:'+i}
w(RC+'rack.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["BPB","BGB"],"key":{"B":it('airain_beam'),"P":{"tag":"minecraft:planks"},"G":it('airain_grate')},"result":{"id":"airain:airain_rack","count":2}})
w(RC+'reinforcement_1.json',{"type":"minecraft:crafting_shapeless","category":"misc","ingredients":[it('airain_sheet')]*4+[it('minecraft:iron_ingot')],"result":{"id":"airain:rack_reinforcement_1","count":1}})
w(RC+'reinforcement_2.json',{"type":"minecraft:crafting_shapeless","category":"misc","ingredients":[it('rack_reinforcement_1'),it('airain_block'),it('airain_sheet'),it('airain_sheet')],"result":{"id":"airain:rack_reinforcement_2","count":1}})
w(RC+'reinforcement_3.json',{"type":"minecraft:crafting_shapeless","category":"misc","ingredients":[it('rack_reinforcement_2'),it('airain_gear'),it('airain_gear'),it('minecraft:diamond')],"result":{"id":"airain:rack_reinforcement_3","count":1}})
w(RC+'reinforcement_4.json',{"type":"minecraft:crafting_shapeless","category":"misc","ingredients":[it('rack_reinforcement_3'),it('minecraft:netherite_ingot')],"result":{"id":"airain:rack_reinforcement_4","count":1}})
FR={"block.airain.airain_rack":"Casier de rayonnage","item.airain.rack_reinforcement_1":"Renfort de casier I","item.airain.rack_reinforcement_2":"Renfort de casier II",
 "item.airain.rack_reinforcement_3":"Renfort de casier III","item.airain.rack_reinforcement_4":"Renfort de casier IV","airain.display_source.rack_stock":"Stock du rayonnage",
 "airain.renfort.aide":"Clic droit sur un casier : %s piles","airain.casier.aide":"Un objet par casier, 32 piles ; les casiers voisins forment un seul inventaire trié",
 "airain.casier.objet":"%s × %s","airain.casier.renforts":"%s renfort(s) : %s piles",
 "airain.casier.vide":"Casier vide · %s piles","airain.casier.contenu":"%s : %s / %s","airain.casier.rien_a_reserver":"Rien à réserver : le casier est vide",
 "airain.casier.reserve":"Casier réservé à cet objet","airain.casier.libere":"Casier libéré","airain.casier.renforce_max":"Ce casier a déjà ses quatre renforts",
 "airain.casier.renfort_ordre":"Il faut d'abord le renfort %s","airain.casier.renforce":"Capacité : %s piles",
 "airain.ingenieur.rayonnage.titre":"Le rayonnage impérial","airain.ingenieur.rayonnage.court":"Rayonnage",
 "airain.ingenieur.rayonnage.histoire":"Les entrepôts de l'Empire se lisaient d'un regard.",
 "airain.ingenieur.rayonnage.usage":"@airain:airain_rack Un objet par casier, 32 piles\n- Voisins : un seul inventaire trié\n- Clic droit : déposer ; deux fois : tout\n- Clic gauche : une pile ; accroupi : une\n- Clé : réserver le casier\n@airain:rack_reinforcement_1 Renforts I à IV : jusqu'à 5 120 piles\n- Cassé, le casier garde son contenu"}
EN={"block.airain.airain_rack":"Rack Bay","item.airain.rack_reinforcement_1":"Rack Reinforcement I","item.airain.rack_reinforcement_2":"Rack Reinforcement II",
 "item.airain.rack_reinforcement_3":"Rack Reinforcement III","item.airain.rack_reinforcement_4":"Rack Reinforcement IV","airain.display_source.rack_stock":"Rack stock",
 "airain.renfort.aide":"Right-click a rack bay: %s stacks","airain.casier.aide":"One item per bay, 32 stacks; neighbouring bays form one sorted inventory",
 "airain.casier.objet":"%s × %s","airain.casier.renforts":"%s reinforcement(s): %s stacks",
 "airain.casier.vide":"Empty bay · %s stacks","airain.casier.contenu":"%s: %s / %s","airain.casier.rien_a_reserver":"Nothing to reserve: the bay is empty",
 "airain.casier.reserve":"Bay reserved for this item","airain.casier.libere":"Bay released","airain.casier.renforce_max":"This bay already has its four reinforcements",
 "airain.casier.renfort_ordre":"Reinforcement %s comes first","airain.casier.renforce":"Capacity: %s stacks",
 "airain.ingenieur.rayonnage.titre":"The Imperial Racking","airain.ingenieur.rayonnage.court":"Racking",
 "airain.ingenieur.rayonnage.histoire":"The Empire's warehouses could be read at a glance.",
 "airain.ingenieur.rayonnage.usage":"@airain:airain_rack One item per bay, 32 stacks\n- Neighbours: one sorted inventory\n- Right-click: deposit; twice: all\n- Left-click: a stack; sneak: one\n- Wrench: reserve the bay\n@airain:rack_reinforcement_1 Reinforcements I to IV: up to 5,120 stacks\n- Broken, the bay keeps its contents"}
for f,D in (('fr_fr.json',FR),('en_us.json',EN)):
    pth=AS+'lang/'+f; d=json.load(open(pth)); d.update(D); json.dump(d,open(pth,'w'),ensure_ascii=False,indent=1)
print('rayonnage ok')
