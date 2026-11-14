exec(open('livre_maquette.py').read())
IND=[('airain:airain_ingot','Airain'),('kubejs:ferraille','Récupération'),('airain:blast_furnace_taphole','Haut-fourneau'),('airain:chiseled_airain','Style impérial'),
     ('airain:airain_catwalk','Passerelles'),('airain:airain_air_vent',"Conduite d'air"),('airain:airain_workbench','Atelier'),('airain:airain_lift_winch','Mécanismes'),
     ('airain:airain_load_reliever','Mécanique'),('airain:echo_turbine',"Turbine d'Écho"),('airain:mechanical_sourcelink','Sourcelink méca.'),('airain:echo_diffuser',"Diffuseur d'Écho"),
     ('airain:echo_condenser',"Condenseur"),('airain:glyph_gear','Glyphe-engrenage')]
A=sommaire("Livre de l'ingénieur","L'industrie impériale",['Blocs','Objets','Empire','Écho','Industrie'],4,IND,5,60)
air=chapitre('airain:airain_ingot','Airain',"L'alliage secret de l'Empire.",
"Ne se fabrique qu'au §lhaut-fourneau impérial§r.\n## Alliage · surchauffé\n@minecraft:copper_ingot 3 cuivre\n@create:zinc_ingot 1 zinc\n@minecraft:calcite 1 fondant\n@airain:airain_ingot → 4 lingots\n## Refonte · chauffé\n@kubejs:ferraille 6 ferrailles → 1\n@kubejs:rouage_brise 2 rouages → 1",6,60)
pas=chapitre('airain:airain_catwalk','Passerelles',"On traversait les usines par le haut.",
"## Pièces\n@airain:airain_catwalk Passerelle\n@airain:airain_catwalk_stairs Escalier : +1\n@airain:airain_catwalk_ramp Rampe : +½\n@airain:airain_catwalk_landing Palier : virage\n@airain:airain_support Poteau, suspente, échelle\n## Clé de Create\n- Sol : grille, plein\n- Côté : rambarde, vitre, vide\n- Échelle : cage, tunnel\n- Accroupi : ramasser\n## Pose\n- Pièce sur un bord : au bout (accroupi : descend)\n- Portillon : main nue = ouvrir",8,60)
hf=chapitre('airain:blast_furnace_taphole','Haut-fourneau',"Le seul feu assez chaud pour l'airain.",
"## Structure\n- Creuset 5×5, 2 de haut\n- Cuve 3×3 creuse, 3 de haut\n@airain:fire_bricks 54 briques\n@airain:blast_furnace_taphole Trou de coulée\n@airain:airain_grate Grille + brûleur\n@airain:blast_furnace_tuyere 1 à 3 tuyères\n@airain:blast_furnace_hopper Gueulard\n## Montage\n- Main nue sur le trou : hologramme\n- Bloc en main : posé\n## Coulée\n- Métal : bassin + presse\n- Laitier : entonnoir",9,60)
planche([A]+air+pas+hf,'livre_maquette.png',2)
print(len(air),len(pas),len(hf))
