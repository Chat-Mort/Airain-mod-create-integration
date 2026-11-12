# Exporte les modèles v2 des machines d'Écho vers le mod (modèles statiques + pièces animées)
import json, copy
src=open('design_v2.py').read(); exec(src[:src.index('cases=[')])
M='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/'
import os
def ecrire(nom, els):
    used=set()
    for e in els:
        for f in e['faces'].values(): used.add(f['texture'].lstrip('#'))
    els=copy.deepcopy(els)
    for e in els:
        for f in e['faces'].values():
            t=f['texture'].lstrip('#'); f['texture']='#'+t
    tex={k:T[k] for k in used}; tex['particle']=T[sorted(used)[0]] if 'laiton' not in used else T['laiton']
    os.makedirs(os.path.dirname(M+nom),exist_ok=True)
    json.dump({"parent":"minecraft:block/block","textures":tex,"elements":els},open(M+nom+'.json','w'),indent=1)
# Turbine : tout sauf les pales (pièce animée) et l'arbre (rendu par Create)
ecrire('echo_turbine', [e for e in turbine if e is not SHAFT_N])
ecrire('echo_turbine/rotor', ROTOR_TURBINE)   # les pales de la cheminée, à plat
# Sourcelink : socle à fenêtre (on voit l'Écho liquide qu'il produit) ; engrenage + gemme = pièce animée
# socle bas (8 de haut) : chaque bande lit le bon morceau du boîtier, pour garder son bord tout autour
base=[bande(box([0,0,0],[16,2,16],"andesite"),14,16),bande(box([0,6,0],[16,8,16],"andesite"),0,2),
      bande(box([0,2,0],[2,6,2],"andesite"),2,6),bande(box([14,2,0],[16,6,2],"andesite"),2,6),bande(box([0,2,14],[2,6,16],"andesite"),2,6),bande(box([14,2,14],[16,6,16],"andesite"),2,6),
      box([1,2,1],[15,6,15],"source",lum=True),box([0.5,2,0.5],[15.5,6,15.5],"fenetre",faces=("north","south","east","west")),
      bande(box([0,4,-0.01],[16,8,0],"laiton",faces=("north",)),0,4),bande(box([0,0,-0.01],[16,4,0],"laiton",faces=("north",)),12,16)]   # plaque de l'arbre : bords haut et bas
ecrire('mechanical_sourcelink', base)
ecrire('mechanical_sourcelink/rotor', [*deplace(COG,0,2,0), box([5,11.5,5],[11,13,11],"pierre"),box([4,13,4],[12,14,12],"dore"),
      box([6,15,6],[10,19,10],"gemme",lum=True,rot=G45([8,17,8]))])
ecrire('echo_diffuser_off', diffuseur(False)); ecrire('echo_diffuser_on', diffuseur(True))
ecrire('echo_condenser_condense', condenseur(False)); ecrire('echo_condenser_evaporate', condenseur(True))
for n in ['echo_turbine','echo_turbine/rotor','mechanical_sourcelink','mechanical_sourcelink/rotor','echo_diffuser_off','echo_diffuser_on','echo_condenser_condense','echo_condenser_evaporate']:
    d=json.load(open(M+n+'.json')); d['render_type']='minecraft:cutout'; json.dump(d,open(M+n+'.json','w'),indent=1)
print('ok')
