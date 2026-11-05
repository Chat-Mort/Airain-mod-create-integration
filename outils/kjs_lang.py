import json, os
p='server_scripts/airain_paliers.js'; t=open(p,encoding='utf-8').read()
s=t.index("// Infobulles")
t=t[:s]+'''// Infobulles (texte d'ambiance, traduit dans kubejs/assets/kubejs/lang/)
ItemEvents.modifyTooltips(event => {
  const lignes = {
    schema_cuivre: 2, schema_laiton: 2, schema_ciel: 2,
    fragment_rouages: 1, fragment_marees: 1, fragment_forge: 1, fragment_vide: 1,
    coeur_d_airain: 2
  }
  for (const [id, n] of Object.entries(lignes)) {
    const texte = []
    for (let i = 1; i <= n; i++) texte.push(Text.translate(`tooltip.kubejs.${id}.${i}`).gray().italic())
    event.add('kubejs:' + id, texte)
  }
})
'''
open(p,'w',encoding='utf-8').write(t)
os.makedirs('assets/kubejs/lang',exist_ok=True)
fr={
 "item.kubejs.schema_cuivre":"Schéma du Cuivre","item.kubejs.schema_laiton":"Schéma du Laiton","item.kubejs.schema_ciel":"Schéma du Ciel",
 "item.kubejs.fragment_rouages":"Fragment de mémoire : les Rouages","item.kubejs.fragment_marees":"Fragment de mémoire : les Marées",
 "item.kubejs.fragment_forge":"Fragment de mémoire : la Forge","item.kubejs.fragment_vide":"Fragment de mémoire : le Vide",
 "item.kubejs.coeur_d_airain":"Cœur d'Airain",
 "tooltip.kubejs.schema_cuivre.1":"Les plans des machines à fluides de l'Empire.","tooltip.kubejs.schema_cuivre.2":"Reste dans la grille de craft : il n'est jamais consommé.",
 "tooltip.kubejs.schema_laiton.1":"Le secret de l'alliage d'Airain.","tooltip.kubejs.schema_laiton.2":"Permet de fabriquer le brûleur à blaze. Jamais consommé.",
 "tooltip.kubejs.schema_ciel.1":"Les plans des navires du ciel.","tooltip.kubejs.schema_ciel.2":"Jamais consommé.",
 "tooltip.kubejs.fragment_rouages.1":"« Nous ne partons pas. Nous attendons. »","tooltip.kubejs.fragment_marees.1":"« Nous dormons dans le métal. »",
 "tooltip.kubejs.fragment_forge.1":"« Le grand transfert est achevé. »","tooltip.kubejs.fragment_vide.1":"« Bientôt. »",
 "tooltip.kubejs.coeur_d_airain.1":"Il est chaud. Il bat.","tooltip.kubejs.coeur_d_airain.2":"Quelque chose, très loin sous terre, bat avec lui."}
en={
 "item.kubejs.schema_cuivre":"Copper Schematic","item.kubejs.schema_laiton":"Brass Schematic","item.kubejs.schema_ciel":"Sky Schematic",
 "item.kubejs.fragment_rouages":"Memory Fragment: Gears","item.kubejs.fragment_marees":"Memory Fragment: Tides",
 "item.kubejs.fragment_forge":"Memory Fragment: Forge","item.kubejs.fragment_vide":"Memory Fragment: Void",
 "item.kubejs.coeur_d_airain":"Brass Heart",
 "tooltip.kubejs.schema_cuivre.1":"Blueprints for the Empire's fluid machines.","tooltip.kubejs.schema_cuivre.2":"Stays in the crafting grid: never consumed.",
 "tooltip.kubejs.schema_laiton.1":"The secret of the imperial alloy.","tooltip.kubejs.schema_laiton.2":"Lets you craft the blaze burner. Never consumed.",
 "tooltip.kubejs.schema_ciel.1":"Blueprints for the sky ships.","tooltip.kubejs.schema_ciel.2":"Never consumed.",
 "tooltip.kubejs.fragment_rouages.1":'"We are not leaving. We are waiting."',"tooltip.kubejs.fragment_marees.1":'"We sleep in the metal."',
 "tooltip.kubejs.fragment_forge.1":'"The great transfer is complete."',"tooltip.kubejs.fragment_vide.1":'"Soon."',
 "tooltip.kubejs.coeur_d_airain.1":"It is warm. It pulses.","tooltip.kubejs.coeur_d_airain.2":"Something far beneath the ground pulses with it."}
assert set(fr)==set(en)
json.dump(fr,open('assets/kubejs/lang/fr_fr.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
json.dump(en,open('assets/kubejs/lang/en_us.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
