# Recettes et noms de l'airain et du haut-fourneau.
import json, os
R='/home/claude/airain-mod-create-integration/src/main/resources/'
RC=R+'data/airain/recipe/airain/'
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
PRE=['','exposed_','weathered_','oxidized_']
FAM=['airain_block','cut_airain','riveted_airain','chiseled_airain','airain_pillar','airain_stairs','cut_airain_stairs','airain_slab','cut_airain_slab',
     'airain_grate','airain_bars','airain_door','airain_trapdoor','airain_chain','airain_lantern']
it=lambda i:{"item":"airain:"+i}
def sc(nom,src,res,n): w(RC+f'stonecutting/{nom}.json',{"type":"minecraft:stonecutting","ingredient":it(src),"result":{"id":"airain:"+res,"count":n}})
# ---- stockage
w(RC+'ingot_from_nuggets.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["NNN","NNN","NNN"],"key":{"N":it('airain_nugget')},"result":{"id":"airain:airain_ingot","count":1}})
w(RC+'nuggets.json',{"type":"minecraft:crafting_shapeless","category":"misc","ingredients":[it('airain_ingot')],"result":{"id":"airain:airain_nugget","count":9}})
w(RC+'block.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["III","III","III"],"key":{"I":it('airain_ingot')},"result":{"id":"airain:airain_block","count":1}})
w(RC+'ingots_from_block.json',{"type":"minecraft:crafting_shapeless","category":"misc","ingredients":[it('airain_block')],"result":{"id":"airain:airain_ingot","count":9}})
# ---- tailleur de pierre, pour chaque stade (et ciré)
for s,p in enumerate(PRE):
    for c in ('','waxed_'):
        q=c+p
        for res,n in (('cut_airain',4),('riveted_airain',4),('chiseled_airain',1),('airain_pillar',1),('airain_stairs',1),('airain_slab',2),('airain_grate',4),('cut_airain_stairs',4),('cut_airain_slab',8)):
            sc(f'{q}{res}_from_{q}airain_block',q+'airain_block',q+res,n)
        for res,n in (('cut_airain_stairs',1),('cut_airain_slab',2),('riveted_airain',1),('chiseled_airain',1)):
            sc(f'{q}{res}_from_{q}cut_airain',q+'cut_airain',q+res,n)
    # cire : rayon de miel + bloc
    for f in FAM:
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing",
          "ingredients":[it(p+f),{"item":"minecraft:honeycomb"}],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
# ---- objets de décor (airain neuf)
w(RC+'door.json',{"type":"minecraft:crafting_shaped","category":"redstone","pattern":["II","II","II"],"key":{"I":it('airain_ingot')},"result":{"id":"airain:airain_door","count":3}})
w(RC+'trapdoor.json',{"type":"minecraft:crafting_shaped","category":"redstone","pattern":["II","II"],"key":{"I":it('airain_ingot')},"result":{"id":"airain:airain_trapdoor","count":1}})
w(RC+'bars.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["III","III"],"key":{"I":it('airain_ingot')},"result":{"id":"airain:airain_bars","count":16}})
w(RC+'chain.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["N","I","N"],"key":{"N":it('airain_nugget'),"I":it('airain_ingot')},"result":{"id":"airain:airain_chain","count":1}})
w(RC+'lantern.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["NNN","NTN","NNN"],"key":{"N":it('airain_nugget'),"T":{"item":"minecraft:redstone_torch"}},"result":{"id":"airain:airain_lantern","count":1}})
# ---- métal : fusion → lingots (bassin + presse), plaques, engrenage
F=lambda n:{"type":"neoforge:single","amount":n,"fluid":"airain:molten_airain"}
w(RC+'compacting_ingot.json',{"type":"create:compacting","ingredients":[F(90)],"results":[{"id":"airain:airain_ingot"}]})
w(RC+'compacting_block.json',{"type":"create:compacting","ingredients":[F(810)],"results":[{"id":"airain:airain_block"}]})
w(RC+'pressing_sheet.json',{"type":"create:pressing","ingredients":[it('airain_ingot')],"results":[{"id":"airain:airain_sheet"}]})
w(RC+'crushing_slag.json',{"type":"create:crushing","ingredients":[it('slag')],"processing_time":150,"results":[{"id":"create:cinder_flour"},{"id":"minecraft:gravel","chance":0.25}]})
INC='airain:incomplete_airain_gear'
w(RC+'sequenced_airain_gear.json',{"type":"create:sequenced_assembly","ingredient":{"item":"create:cogwheel"},"loops":1,
  "results":[{"id":"airain:airain_gear"}],"transitional_item":{"id":INC},
  "sequence":[{"type":"create:deploying","ingredients":[{"item":INC},it('airain_sheet')],"results":[{"id":INC}]},
              {"type":"create:filling","ingredients":[{"item":INC},F(90)],"results":[{"id":INC}]},
              {"type":"create:pressing","ingredients":[{"item":INC}],"results":[{"id":INC}]}]})
# ---- haut-fourneau (sans airain : c'est lui qui le produit)
w(RC+'fire_brick.json',{"type":"create:mixing","heat_requirement":"heated","ingredients":[{"item":"minecraft:brick"},{"item":"minecraft:brick"},{"item":"minecraft:nether_brick"}],"results":[{"id":"airain:fire_brick","count":2}]})
w(RC+'fire_bricks.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["BB","BB"],"key":{"B":it('fire_brick')},"result":{"id":"airain:fire_bricks","count":1}})
w(RC+'tuyere.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":[" P ","SBS"],"key":{"P":{"item":"create:fluid_pipe"},"S":{"item":"create:copper_sheet"},"B":it('fire_bricks')},"result":{"id":"airain:blast_furnace_tuyere","count":1}})
w(RC+'hopper.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["I I","IHI"," B "],"key":{"I":{"item":"create:iron_sheet"},"H":{"item":"minecraft:hopper"},"B":it('fire_bricks')},"result":{"id":"airain:blast_furnace_hopper","count":1}})
w(RC+'taphole.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":["BSB","BPB","BBB"],"key":{"B":it('fire_bricks'),"S":{"item":"create:brass_sheet"},"P":{"item":"create:fluid_pipe"}},"result":{"id":"airain:blast_furnace_taphole","count":1}})
# ---- grilles acceptées au centre du fourneau : airain, et cuivre (pour le premier fourneau)
tg=R+'data/airain/tags/block/airain_grates.json'; d=json.load(open(tg))
d['values']+=[f'minecraft:{c}{p}copper_grate' for c in ('','waxed_') for p in PRE]; d['values']=list(dict.fromkeys(d['values'])); w(tg,d)
# ---------------------------------------------------------------- noms
NFR={'airain_block':"Bloc d'airain",'cut_airain':"Airain taillé",'riveted_airain':"Airain riveté",'chiseled_airain':"Airain ciselé",'airain_pillar':"Pilier d'airain",
     'airain_stairs':"Escalier en airain",'cut_airain_stairs':"Escalier en airain taillé",'airain_slab':"Dalle d'airain",'cut_airain_slab':"Dalle d'airain taillé",
     'airain_grate':"Grille d'airain",'airain_bars':"Barreaux d'airain",'airain_door':"Porte d'airain",'airain_trapdoor':"Trappe d'airain",'airain_chain':"Chaîne d'airain",'airain_lantern':"Lanterne d'airain"}
NEN={'airain_block':"Block of Airain",'cut_airain':"Cut Airain",'riveted_airain':"Riveted Airain",'chiseled_airain':"Chiseled Airain",'airain_pillar':"Airain Pillar",
     'airain_stairs':"Airain Stairs",'cut_airain_stairs':"Cut Airain Stairs",'airain_slab':"Airain Slab",'cut_airain_slab':"Cut Airain Slab",
     'airain_grate':"Airain Grate",'airain_bars':"Airain Bars",'airain_door':"Airain Door",'airain_trapdoor':"Airain Trapdoor",'airain_chain':"Airain Chain",'airain_lantern':"Airain Lantern"}
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
fr={}; en={}
for f in FAM:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f
            fr[f'block.airain.{i}']=NFR[f]+SFR[s]+(' (ciré)' if c else '')
            en[f'block.airain.{i}']=('Waxed ' if c else '')+SEN[s]+NEN[f]
fr.update({"item.airain.airain_ingot":"Lingot d'airain","item.airain.airain_nugget":"Pépite d'airain","item.airain.airain_sheet":"Plaque d'airain",
 "item.airain.airain_gear":"Engrenage d'airain","item.airain.incomplete_airain_gear":"Engrenage d'airain inachevé","item.airain.slag":"Laitier",
 "item.airain.fire_brick":"Brique réfractaire","item.airain.molten_airain_bucket":"Seau d'airain en fusion","fluid.airain.molten_airain":"Airain en fusion",
 "block.airain.molten_airain":"Airain en fusion","block.airain.fire_bricks":"Briques réfractaires","block.airain.blast_furnace_tuyere":"Tuyère",
 "block.airain.blast_furnace_hopper":"Gueulard","block.airain.blast_furnace_taphole":"Trou de coulée",
 "airain.fourneau.incomplet":"Le haut-fourneau n'est pas monté. Les places à remplir brillent en orange. Il manque :",
 "airain.fourneau.manque.bricks":"des briques réfractaires (3 × 3 au sol, 4 de haut, le trou de coulée au milieu de la face avant, en bas)",
 "airain.fourneau.manque.grate":"une grille d'airain (ou de cuivre) au centre du sol, avec un brûleur à blaze juste en dessous",
 "airain.fourneau.manque.hollow":"de la place vide au centre, aux rangs 2 et 3 (la cuve)",
 "airain.fourneau.manque.hopper":"le gueulard au centre du sommet",
 "airain.fourneau.manque.tuyere":"une tuyère au milieu d'un côté ou de l'arrière, au rang 2 ou 3",
 "airain.fourneau.manque.tuyeres":"une seule tuyère, pas plusieurs",
 "airain.fourneau.etat":"Haut-fourneau : %s · ventilateur %s tr/min · %s lingots en cuve",
 "airain.fourneau.chaleur.froid":"froid (brûleur éteint)","airain.fourneau.chaleur.chaud":"chaud, refonte","airain.fourneau.chaleur.surchauffe":"surchauffé, refonte et alliage",
 "airain.fourneau.lunettes.chaleur":"Chaleur : %s","airain.fourneau.lunettes.air":"Souffle : %s tr/min","airain.fourneau.lunettes.cuve":"Airain en fusion : %s / %s mB",
 "airain.fourneau.lunettes.progres":"Fonte : %s %%"})
en.update({"item.airain.airain_ingot":"Airain Ingot","item.airain.airain_nugget":"Airain Nugget","item.airain.airain_sheet":"Airain Sheet",
 "item.airain.airain_gear":"Airain Gear","item.airain.incomplete_airain_gear":"Incomplete Airain Gear","item.airain.slag":"Slag",
 "item.airain.fire_brick":"Fire Brick","item.airain.molten_airain_bucket":"Bucket of Molten Airain","fluid.airain.molten_airain":"Molten Airain",
 "block.airain.molten_airain":"Molten Airain","block.airain.fire_bricks":"Fire Bricks","block.airain.blast_furnace_tuyere":"Tuyere",
 "block.airain.blast_furnace_hopper":"Furnace Throat","block.airain.blast_furnace_taphole":"Taphole",
 "airain.fourneau.incomplet":"The blast furnace is not assembled. The spots to fill glow orange. Missing:",
 "airain.fourneau.manque.bricks":"fire bricks (3 × 3 footprint, 4 high, the taphole in the middle of the front face, at the bottom)",
 "airain.fourneau.manque.grate":"an airain (or copper) grate in the middle of the floor, with a blaze burner right below",
 "airain.fourneau.manque.hollow":"empty space in the middle, on rows 2 and 3 (the shaft)",
 "airain.fourneau.manque.hopper":"the throat in the middle of the top",
 "airain.fourneau.manque.tuyere":"a tuyere in the middle of a side or of the back, on row 2 or 3",
 "airain.fourneau.manque.tuyeres":"a single tuyere, not several",
 "airain.fourneau.etat":"Blast furnace: %s · fan %s RPM · %s ingots in the tank",
 "airain.fourneau.chaleur.froid":"cold (burner out)","airain.fourneau.chaleur.chaud":"hot, remelting","airain.fourneau.chaleur.surchauffe":"superheated, remelting and alloying",
 "airain.fourneau.lunettes.chaleur":"Heat: %s","airain.fourneau.lunettes.air":"Blast: %s RPM","airain.fourneau.lunettes.cuve":"Molten airain: %s / %s mB",
 "airain.fourneau.lunettes.progres":"Smelting: %s %%"})
L=R+'assets/airain/lang/'
for fn,d in (('fr_fr.json',fr),('en_us.json',en)):
    j=json.load(open(L+fn)); j.update(d); json.dump(j,open(L+fn,'w'),ensure_ascii=False,indent=1)
print('recettes et noms ok')
