import json,re
FR={"airain.fourneau.incomplet":"Haut-fourneau incomplet",
 "airain.fourneau.manque.bricks":"des briques réfractaires (creuset 5 × 5 à coins coupés sur 2 rangs, cuve 3 × 3 sur 3 rangs)",
 "airain.fourneau.manque.hollow":"de la place vide : l'intérieur du creuset au rang 2, le centre de la cuve aux rangs 3 et 4",
 "airain.fourneau.manque.hopper":"le gueulard au centre du sommet de la cuve",
 "airain.fourneau.manque.tuyere":"au moins une tuyère au milieu d'un côté ou de l'arrière du creuset, au rang 2",
 "airain.fourneau.manque.tuyeres":"trois tuyères au plus",
 "airain.fourneau.etat":"Haut-fourneau : %s · souffle %s tr/min · %s lingots en cuve",
 "airain.fourneau.lunettes.air":"Souffle : %s tr/min (tous les ventilateurs)",
 "airain.fourneau.hologramme":"Haut-fourneau incomplet : %s blocs à poser ou corriger. Hologramme affiché 30 s : clic droit avec le bon bloc pour le poser.",
 "airain.fourneau.hologramme_off":"Hologramme masqué",
 "airain.fourneau.lunettes.briques":"Briques réfractaires : %s","airain.fourneau.lunettes.tuyere":"Tuyère : au moins %s",
 "airain.fourneau.lunettes.grille":"Grille d'airain : %s","airain.fourneau.lunettes.gueulard":"Gueulard : %s",
 "airain.fourneau.lunettes.vide":"Blocs à retirer de l'intérieur : %s","airain.fourneau.lunettes.astuce":"Clic droit main nue sur le trou de coulée : hologramme",
 "airain.ingenieur.haut_fourneau.usage":"En briques réfractaires, sur 5 de haut. Le creuset (rangs 1 et 2) : 5 × 5 aux quatre coins coupés, le trou de coulée au milieu de la face avant, en bas ; au centre du sol, une grille d'airain (ou de cuivre) avec un brûleur à blaze dessous ; au rang 2, l'intérieur 3 × 3 reste vide. La cuve (rangs 3 à 5) : 3 × 3 posée au centre, creuse, avec le gueulard au centre du sommet. Une à trois tuyères au milieu des côtés ou de l'arrière du creuset, au rang 2, chacune avec un ventilateur de Create qui souffle dedans : chaque ventilateur ajoute son débit. Clic droit main nue sur le trou de coulée : les blocs manquants apparaissent en hologramme (les mauvais blocs en rouge) ; un clic droit avec le bon bloc le pose dans la case visée, même en l'air. Brûleur chauffé : refonte (6 ferrailles ou 2 rouages brisés = un lingot). Surchauffé : alliage aussi (3 cuivres, 1 zinc, 1 fondant = 4 lingots). L'airain en fusion sort au tuyau par le trou de coulée (bassin + presse : 90 mB = un lingot), le laitier à l'entonnoir. Lunettes d'ingénieur : ce qui manque, puis chaleur, souffle, cuve."}
EN={"airain.fourneau.incomplet":"Blast furnace incomplete",
 "airain.fourneau.manque.bricks":"fire bricks (5 × 5 hearth with cut corners on 2 rows, 3 × 3 shaft on 3 rows)",
 "airain.fourneau.manque.hollow":"empty space: inside the hearth on row 2, the middle of the shaft on rows 3 and 4",
 "airain.fourneau.manque.hopper":"the throat in the middle of the top of the shaft",
 "airain.fourneau.manque.tuyere":"at least one tuyere in the middle of a side or of the back of the hearth, on row 2",
 "airain.fourneau.manque.tuyeres":"three tuyeres at most",
 "airain.fourneau.etat":"Blast furnace: %s · blast %s RPM · %s ingots in the tank",
 "airain.fourneau.lunettes.air":"Blast: %s RPM (all fans)",
 "airain.fourneau.hologramme":"Blast furnace incomplete: %s blocks to place or fix. Hologram shown for 30 s: right-click with the right block to place it.",
 "airain.fourneau.hologramme_off":"Hologram hidden",
 "airain.fourneau.lunettes.briques":"Fire bricks: %s","airain.fourneau.lunettes.tuyere":"Tuyere: at least %s",
 "airain.fourneau.lunettes.grille":"Airain grate: %s","airain.fourneau.lunettes.gueulard":"Throat: %s",
 "airain.fourneau.lunettes.vide":"Blocks to clear from inside: %s","airain.fourneau.lunettes.astuce":"Right-click the taphole bare-handed: hologram",
 "airain.ingenieur.haut_fourneau.usage":"Fire bricks, 5 high. The hearth (rows 1 and 2): 5 × 5 with the four corners cut, the taphole in the middle of the front face, at the bottom; in the middle of the floor, an airain (or copper) grate with a blaze burner below; on row 2, the 3 × 3 inside stays empty. The shaft (rows 3 to 5): 3 × 3 set in the middle, hollow, with the throat in the middle of the top. One to three tuyeres in the middle of the sides or of the back of the hearth, on row 2, each with a Create fan blowing into it: every fan adds its throughput. Right-click the taphole bare-handed: missing blocks appear as a hologram (wrong blocks in red); right-click with the right block to place it in the targeted spot, even mid-air. Heated burner: remelting (6 scrap or 2 broken cogs = one ingot). Superheated: alloying too (3 copper, 1 zinc, 1 flux = 4 ingots). Molten airain is piped out of the taphole (basin + press: 90 mB = one ingot), slag comes out with a funnel. Engineer's goggles: what is missing, then heat, blast, tank."}
L='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/lang/'
for f,D in (('fr_fr.json',FR),('en_us.json',EN)):
    d=json.load(open(L+f)); d.update(D); json.dump(d,open(L+f,'w'),ensure_ascii=False,indent=1)
# le générateur d'origine : mêmes textes (s'il est relancé un jour)
p='outils_airain/recettes_noms.py'; s=open(p).read()
for D in (FR,EN):
    for k,v in D.items():
        if k.startswith('airain.ingenieur'): continue
        s2=re.sub(r'("%s":)"[^"]*"'%re.escape(k), lambda m: m.group(1)+json.dumps(v,ensure_ascii=False), s, count=1)
        s=s2
open(p,'w').write(s)
print('ok')
