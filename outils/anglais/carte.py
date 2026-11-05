# Correspondances français → anglais
IDS = {
 "affiche_vierge": "blank_poster", "atlas": "atlas", "balise_defense": "defense_beacon", "balise_partie": "defense_beacon_part",
 "banc_entretien": "maintenance_bench", "banniere_murale": "foundation_wall_banner", "bloc_echo_primordial": "primordial_echo_block",
 "bloc_etoile": "star_block", "borne_arcanique": "resonant_archive", "borne_imperiale": "difference_engine",
 "borne_partie_arcanique": "resonant_archive_part", "borne_partie_imperiale": "difference_engine_part",
 "bottes_arcaniques": "arcane_boots", "bottes_imperiales": "imperial_boots", "bottes_runiques": "runic_boots", "bottes_sacrees": "sacred_boots",
 "caisse_arcanique": "arcane_delivery_crate", "caisse_imperiale": "imperial_delivery_crate", "carte_empire": "empire_map",
 "casque_arcanique": "arcane_helmet", "casque_couronne": "crowned_helmet", "casque_couronne_sacree": "sacred_crown",
 "casque_diademe": "diadem_helmet", "casque_imperial": "imperial_helmet", "casque_runique": "runic_helmet",
 "charte": "imperial_charter", "chroniques": "chronicles", "codex": "codex", "coeur_magma": "magma_heart",
 "couronne_airain": "airain_crown", "couronne_airain_sacree": "airain_crown_sacred", "demultiplicateur": "reduction_gear",
 "desenchanteur": "disenchanter", "diademe_echo": "echo_diadem", "encre_runique": "runic_ink", "engrenage_rodeur": "prowler_gear",
 "epee_arcanique": "arcane_sword", "epee_imperiale": "imperial_sword", "epee_runique": "runic_sword", "epee_sacree": "sacred_sword",
 "espadon_arcanique": "arcane_greatsword", "espadon_imperial": "imperial_greatsword", "espadon_runique": "runic_greatsword", "espadon_sacre": "sacred_greatsword",
 "gabarit_banniere": "banner_template", "gardien_spawn_egg": "guardian_spawn_egg", "graisseur": "grease_gun", "grand_etendard": "great_standard",
 "jambieres_arcaniques": "arcane_leggings", "jambieres_imperiales": "imperial_leggings", "jambieres_runiques": "runic_leggings", "jambieres_sacrees": "sacred_leggings",
 "katana_arcanique": "arcane_katana", "katana_imperial": "imperial_katana", "katana_runique": "runic_katana", "katana_sacre": "sacred_katana",
 "lingot_arcanium": "arcanium_ingot", "livre_ingenieur": "engineers_manual", "meule_fine": "fine_grindstone",
 "module_blindage": "armor_module", "module_blindage_2": "armor_module_2", "module_canon": "cannon_module", "module_canon_2": "cannon_module_2",
 "module_chaudiere": "boiler_module", "module_chaudiere_2": "boiler_module_2", "module_lanterne": "lantern_module", "module_lanterne_2": "lantern_module_2",
 "module_lunette": "scope_module", "module_lunette_2": "scope_module_2", "module_tesla": "tesla_module", "module_tesla_2": "tesla_module_2",
 "oeil_gardien": "guardian_eye", "parachute": "parachute", "pierre_fondation": "foundation_stone",
 "pioche_arcanique": "arcane_pickaxe", "pioche_imperiale": "imperial_pickaxe", "pioche_runique": "runic_pickaxe", "pioche_sacree": "sacred_pickaxe",
 "plan": "blueprint", "plaque_imperiale": "imperial_plate", "plaque_imperiale_inachevee": "incomplete_imperial_plate", "plaque_netherite_sacree": "sacred_netherite_plate",
 "plastron_arcanique": "arcane_chestplate", "plastron_imperial": "imperial_chestplate", "plastron_runique": "runic_chestplate", "plastron_sacre": "sacred_chestplate",
 "registre_fondations": "foundation_registry", "reliure": "binder", "sceau_centurion": "centurion_seal",
 "sceptre_arcanique": "arcane_scepter", "sceptre_imperial": "imperial_scepter", "socle_trophee": "trophy_pedestal", "solium": "solium",
 "table_enchantement": "imperial_enchanting_table", "tableau_service": "duty_board", "trone_imperial": "imperial_throne",
 "twinblade_arcanique": "arcane_twinblade", "twinblade_imperiale": "imperial_twinblade", "twinblade_runique": "runic_twinblade", "twinblade_sacree": "sacred_twinblade",
 "visiere_colosse": "colossus_visor",
 # entités, block entities, sérialiseur
 "assise": "seat", "caisse_livraison": "delivery_crate", "gardien": "guardian", "borne": "order_terminal", "monture": "mount",
}
IDS = {k: v for k, v in IDS.items() if k != v}
MATERIAUX = {"sacree": "sacred", "imperiale": "imperial", "runique": "runic", "arcanique": "arcane", "couronne": "crown",
             "casque_couronne": "crowned_helmet", "diademe": "diadem"}
# textures / modèles qui ne sont pas des identifiants
TEX_BLOC = {"balise_particule": "beacon_particle", "balise_tour": "beacon_tower", "banc_cuivre": "bench_copper", "banc_laiton": "bench_brass",
 "banc_plan": "bench_blueprint", "desench_cristal": "disenchanter_crystal", "desench_plan": "disenchanter_blueprint", "etendard_objet": "standard_item",
 "fondation_plaque": "foundation_plate", "fondation_plaque_arcanique": "foundation_plate_arcane", "fondation_plaque_imperiale": "foundation_plate_imperial",
 "huile_jauge": "oil_gauge", "jauge_fond": "gauge_background", "meule_pierre": "grindstone_stone", "meule_tranche": "grindstone_edge",
 "socle_colonne": "pedestal_column", "socle_cote": "pedestal_side", "socle_dessus": "pedestal_top", "socle_garni_losange": "pedestal_trim_diamond",
 "socle_garni_simple": "pedestal_trim_plain", "socle_garniture": "pedestal_trim", "socle_halo": "pedestal_halo", "socle_marbre": "pedestal_marble",
 "socle_velours": "pedestal_velvet", "socle_velours_losange": "pedestal_velvet_diamond", "socle_velours_simple": "pedestal_velvet_plain",
 "socle_verre": "pedestal_glass", "table_cote": "table_side", "table_dessous": "table_bottom", "table_dessus": "table_top",
 "zone_arcanique": "arcane_arrival_pad", "zone_imperiale": "imperial_arrival_pad"}
MODELE_BLOC = {"balise_vide": "defense_beacon_empty", "etendard_mat_ceremonie": "standard_pole_ceremony", "etendard_mat_potence": "standard_pole_gallows",
 "etendard_mat_vexillum": "standard_pole_vexillum", "etendard_socle": "standard_base", "etendard_socle_arcanique": "standard_base_arcane",
 "etendard_socle_imperial": "standard_base_imperial", "grand_mat": "great_mast", "grand_mat_bague": "great_mast_ring", "grand_mat_haut": "great_mast_top",
 "grand_mat_pied": "great_mast_foot", "borne_partie_arcanique_vide": "resonant_archive_part_empty", "borne_partie_imperiale_vide": "difference_engine_part_empty",
 "zone_arcanique": "arcane_arrival_pad", "zone_imperiale": "imperial_arrival_pad", "huile": "oil", "meule": "grindstone", "cristal": "crystal"}
TEX_ENTITE = {"gardien": "guardian", "gardien_capitaine": "guardian_captain", "gardien_echo": "guardian_echo", "gardien_elite": "guardian_elite",
 "gardien_modules": "guardian_modules", "gardien_modules_2": "guardian_modules_2", "gardien_mousse": "guardian_moss", "table_livre": "table_book", "etendard": "standard"}
TEX_ETENDARD = {"fond_aronde": "field_swallowtail", "fond_droit": "field_straight", "fond_pointe": "field_pointed", "frange": "fringe",
 "motif_ancre": "emblem_anchor", "motif_cle": "emblem_key", "motif_couronne": "emblem_crown", "motif_cristal": "emblem_crystal", "motif_eclair": "emblem_lightning",
 "motif_etoile": "emblem_star", "motif_fiole": "emblem_vial", "motif_flamme": "emblem_flame", "motif_rouage": "emblem_cog", "motif_rouage_brise": "emblem_broken_cog",
 "ornement_aronde": "trim_swallowtail", "ornement_droit": "trim_straight", "ornement_pointe": "trim_pointed"}
TEX_GUI = {"banc": "bench", "elements": "widgets", "etendard": "standard", "registre": "registry", "table_empire": "imperial_table", "tableau": "duty_board"}
TEX_ARMURE = {"arcanique": "arcane", "casque_couronne_layer_1": "crowned_helmet_layer_1", "casque_couronne_sacree_layer_1": "crowned_helmet_sacred_layer_1",
 "coiffes_echo": "echo_headpieces", "couronne_layer_1": "crown_layer_1", "couronne_sacree_layer_1": "crown_sacred_layer_1", "diademe_layer_1": "diadem_layer_1",
 "imperiale": "imperial", "runique_layer_1": "runic_layer_1", "runique_layer_2": "runic_layer_2", "sacree_layer_1": "sacred_layer_1", "sacree_layer_2": "sacred_layer_2"}
TEX_TABLEAU = {"affiche_capsule": "poster_capsule", "affiche_coeur_attend": "poster_heart_waits", "affiche_diapason": "poster_tuning_fork",
 "affiche_echo_interdit": "poster_echo_forbidden", "affiche_fondateur": "poster_founder", "affiche_libres": "poster_free", "affiche_reveillez": "poster_wake_up",
 "affiche_un_moteur": "poster_one_engine", "embleme_echo": "emblem_echo", "embleme_empire": "emblem_empire", "embleme_refractaires": "emblem_refractories"}
