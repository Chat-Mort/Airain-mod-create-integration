#!/bin/sh
# Régénère toutes les structures du pack, dans l'ordre. usage : sh construire.sh <dossier du pack>
set -e
cd "$(dirname "$0")"
python3 labo.py "$1"
python3 ruine.py "$1" && python3 ruine_worldgen.py "$1"
python3 avant_poste.py "$1" && python3 avant_poste_worldgen.py "$1"
python3 structures_plus.py "$1" | grep retouches
python3 butin_structures.py "$1"
python3 cache_refractaire.py "$1"
python3 echo_structures.py "$1" | grep retouches && python3 echo_contenu.py "$1" > /dev/null
python3 echo_lang.py "$1" > /dev/null
python3 motifs_bannieres.py "$1" && python3 bannieres.py "$1" && python3 bannieres_airain.py "$1"
python3 fronts.py "$1" > /dev/null
python3 station.py "$1" > /dev/null
python3 dirigeable.py "$1" > /dev/null
python3 plans.py "$1" > /dev/null
python3 vanilla_retouches.py "$1"
python3 gardiens_structures.py "$1"
python3 affiches_structures.py "$1"
python3 musique.py "$1" > /dev/null
python3 gen_v2.py "$1" > /dev/null && python3 snbt_check.py "$1/config/ftbquests/quests" | tail -1
python3 diag_gen.py "$1"
python3 integrer_interface.py "$1"
(cd "$(dirname "$0")/immersion" && python3 immersion.py "$1" && python3 progres.py "$1")
