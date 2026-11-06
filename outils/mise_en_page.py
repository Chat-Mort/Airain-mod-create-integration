# Mise en page du livre de quêtes : chapitres regroupés, positions (x, y) par quête, lignes masquées.
# Exécuté par gen_v2.py juste avant l'écriture. Les identifiants des quêtes ne changent pas.
POS = {}
CACHER = set()          # quêtes dont les traits de dépendance sont masqués (lien trop long ; la dépendance reste)
def ligne(y, *paires):
    for k, x in paires: POS[k] = (x, y)
import math
def cercle(cx, cy, r, cles, debut=-90):
    for i, k in enumerate(cles):
        a = math.radians(debut + 360 * i / len(cles))
        POS[k] = (round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2))

# ============================================================ chapitres : regroupements
_par_cle = {c["key"]: c for c in chapters}
_CLE = {v: k for k, v in QUESTS.items()}
def _deplacer(cles, vers):
    pris = []
    for c in chapters:
        if c is vers: continue
        pris += [q for q in c["quests"] if _CLE[q["id"]] in cles]
        c["quests"] = [q for q in c["quests"] if _CLE[q["id"]] not in cles]
    vers["quests"] += pris
# les Échos perdus rejoignent la voie de l'Écho
_deplacer({"l_vael", "l_essai", "l_resonance", "l_diapason", "l_grand_relais", "l_choeur", "l_primordial"}, _par_cle["arcanes"])
# ingénierie et trains : une seule annexe
_deplacer({q for q in ("t_horaire", "t_portes", "t_observateur", "t_fret", "t_fluides", "t_triage", "t_long", "t_pneumatique", "t_tube", "t_ligne")}, _par_cle["ingenierie"])
# bases et capitales : la nouvelle annexe
cBa = chapter("bases", "13_bases", ("&3Annexe&r · Bases et capitales", "&3Side&r · Bases and Capitals"),
              ("Fonder, pavoiser, exposer : faire d'un abri une base de l'Empire.", "Found, decorate, display: turn a shelter into an Empire base."),
              "airain:foundation_stone", 15)
_deplacer({"e_fondation", "h_grand", "h_murale", "h_gabarit", "h_hissage", "h_pavoise", "b_socle", "b_trophees", "c_agrandissement", "c_infirmerie", "c_meteo", "c_forge"}, cBa)
# exploration et bestiaire
_deplacer({_CLE[q["id"]] for q in _par_cle["bestiaire"]["quests"]}, _par_cle["exploration"])
chapters[:] = [c for c in chapters if c["key"] not in ("echos", "trains", "bestiaire")]
tr(f"chapter.{_par_cle['ingenierie']['id']}.title", ("&3Annexe&r · Ingénierie et logistique", "&3Side&r · Engineering and Logistics"))
tr(f"chapter.{_par_cle['arsenal']['id']}.title", ("&3Annexe&r · Arsenal", "&3Side&r · Arsenal"))
tr(f"chapter.{_par_cle['exploration']['id']}.title", ("&3Annexe&r · Exploration et bestiaire", "&3Side&r · Exploration and Bestiary"))
_ordre = {"sacs": 10, "commandes": 11, "ingenierie": 12, "arsenal": 13, "bases": 14, "exploration": 15}
for c in chapters:
    if c["key"] in _ordre: c["order"] = _ordre[c["key"]]
GROUPES = [("empire", ("L'Empire", "The Empire"), ("reveil", "andesite", "cuivre", "laiton", "ciel", "coeur", "reconquete")),
           ("echo", ("La voie de l'Écho", "The Echo Path"), ("arcanes",)),
           ("annexes", ("Annexes", "Side Chapters"), tuple(_ordre))]
for _g, _t, _cles in GROUPES:
    tr(f"chapter_group.{hid('grp:' + _g)}.title", _t)
    for c in chapters:
        if c["key"] in _cles: c["group"] = hid("grp:" + _g)

# ============================================================ I · le Réveil
ligne(-1.5, ("bienvenue", 0), ("surface", 4))
ligne(0, ("comprendre", 0), ("outils", 2), ("alliage", 4), ("roue", 6), ("engrenages", 8), ("q_alliage", 10), ("atelier", 14))
ligne(1.5, ("boitiers1", 6), ("meule", 8), ("tapis", 10), ("moulin", 12))
ligne(3, ("cuir", 4), ("village", 6), ("ruines_piste", 8))
# ============================================================ II · l'âge de l'Andésite
ligne(-3.5, ("mixeur", 4))
ligne(-2, ("bureau_etudes", 0), ("ventilateur", 4), ("minerai", 6), ("q_plaques", 8))
ligne(0, ("presse", 0), ("plaques", 2), ("armure_fer", 4), ("arme_fer", 6), ("ruines_propres", 8), ("salles", 10), ("presage", 12), ("gardien_vent", 14), ("masse", 16))
ligne(2, ("ars", 0), ("banque", 2), ("outils_meca", 4), ("goulottes", 6), ("ferme", 8), ("prepa2", 12))
# ============================================================ III · l'âge du Cuivre
ligne(-2, ("tuyaux", 2), ("pompe", 4), ("q_cuivre", 6), ("forge", 8), ("armure_diamant", 10))
ligne(0, ("boitier_cuivre", 0), ("inscriptions", 10), ("monument", 12), ("prepa3", 14), ("gardien_marees", 16))
ligne(2, ("reservoirs", 2), ("bec", 4), ("vapeur", 6), ("plongee", 8))
ligne(3.5, ("banc", 4), ("affutage", 6))
# ============================================================ IV · l'âge du Laiton : une ligne par thème
ligne(-6, ("bastion", 2), ("armure_netherite", 15), ("canons", 17), ("obus", 19))
ligne(-4, ("banc_modules", 6), ("table_empire", 9), ("desenchanteur", 10.75), ("purge", 12.5))
ligne(-2, ("blaze", 2), ("laiton", 4), ("boitier_laiton", 6), ("q_laiton", 8), ("q_precision", 10), ("netherite", 12))
ligne(0, ("nether", 0), ("quartz", 2), ("deployeur", 6), ("precision", 8), ("bras", 10), ("capsules", 12), ("prepa4", 21), ("forge_ames", 23))
ligne(1, ("waystones", 12))
ligne(2, ("crafter", 8), ("broyage", 10), ("rails", 12), ("train", 14), ("reseau", 16), ("gare", 18))
ligne(4, ("gardien_debout", 6), ("garnison", 8), ("netherite_sacree", 10), ("gardien_elite", 12))
ligne(6, ("l_refractaires", 2), ("a_ars_source", 10), ("a_ars_livre", 19))
CACHER |= {"netherite_sacree"}
# ============================================================ V · l'âge du Ciel
ligne(-2, ("helices", 2), ("station", 6), ("naval", 8), ("jetpack", 14))
ligne(0, ("assembleur", 0), ("envol", 4), ("navire", 6), ("end", 8), ("dragon", 10), ("cites", 12), ("bientot", 16), ("citadelle", 18))
ligne(2, ("ballon", 2), ("q_enveloppes", 4), ("atelier_ench", 6), ("mage", 8), ("prepa5", 14), ("l_relais", 16))
ligne(3.5, ("fret", 6))
# ============================================================ VI · le Cœur d'Airain
ligne(-2, ("salle", 2), ("memoires", 4))
ligne(0, ("crafters21", 0), ("l_sanctuaire", 4), ("forger", 6), ("reactiver", 8), ("remparts", 12))
ligne(-1.5, ("siege", 10)); ligne(1.5, ("soins", 10))
ligne(2, ("mat_coeur", 2), ("mer", 4))
# ============================================================ VII · la Reconquête : symétrique
ligne(-3.5, ("assaut", 2))
ligne(-2, ("vague1", 2), ("vague2", 4), ("vague3", 6))
ligne(0, ("eveil", 0), ("flotte", 2), ("berceau", 8), ("empereur", 12), ("coeur_eteint", 14), ("deux_voix", 16), ("epilogue", 20), ("defi", 22))
ligne(-1, ("sentinelle", 10)); ligne(1, ("etincelle", 10))
ligne(2, ("cite1", 2), ("cite2", 4), ("cite3", 6))
ligne(4, ("wither", 2))
ligne(-2, ("f_empire", 18), ("capitaine", 20)); ligne(-3.5, ("trone", 20)); ligne(-5, ("borne_empire", 20))
ligne(-6.5, ("r1", 20), ("r3", 22), ("r5", 24), ("r10", 26))
ligne(2, ("f_echo", 18), ("gardien_echo", 20)); ligne(3.5, ("solium", 20)); ligne(5, ("borne_echo", 20))
ligne(6.5, ("a1", 20), ("a3", 22), ("a5", 24), ("a10", 26))
# ============================================================ la voie de l'Écho : les Arcanes, puis les Échos perdus (à droite)
ligne(-7.5, ("ar_magebloom", 2))
ligne(-6, ("ar_archebois", 0), ("ar_bocal", 2), ("ar_sourcelinks", 4), ("ar_relais", 6))
ligne(-3, ("ar_glyphes", 2), ("ar_chasseur", 4), ("ar_rodeur", 6), ("ar_gardien", 8))
ligne(-1.5, ("ar_brasero", 4), ("ar_rituel", 6))
ligne(0, ("a_ars_table", 0), ("a_ars_appareil", 2))
POS["ar_starbuncle"] = (4, 1.5)
cercle(4, 1.5, 2.3, ["ar_drygmy", "ar_whirlisprig", "ar_wixie", "ar_golem"], debut=-48)
for _k, _a in zip(["ar_drygmy", "ar_whirlisprig", "ar_wixie", "ar_golem"], (-48, -16, 16, 48)):
    POS[_k] = (round(4 + 2.3 * math.cos(math.radians(_a)), 2), round(1.5 + 2.3 * math.sin(math.radians(_a)), 2))
ligne(4.5, ("a_ars_apprenti", 4), ("ar_robe", 6), ("ar_fil", 8)); ligne(6, ("a_ars_archimage", 6))
ligne(-2, ("l_vael", 10), ("l_essai", 12))
ligne(0, ("l_resonance", 10), ("l_diapason", 12), ("l_grand_relais", 14), ("l_choeur", 16), ("l_primordial", 18))
# ============================================================ annexes
ligne(-1, ("sac_cuivre", 2), ("sac_fer", 4), ("sac_or", 6), ("sac_diamant", 8), ("sac_netherite", 10), ("sac_eternel", 12))
ligne(0, ("sac1", 0))
ligne(1, ("stock1", 2), ("stock2", 4), ("stock3", 6), ("controleur", 8))
POS["boutique"] = (0, 0)
cercle(0, 0, 4.5, ["o_pain", "o_alliage", "o_plaques", "o_tuyaux", "o_cuivre", "o_laiton", "o_precision", "o_rails", "o_tubes", "o_obus", "o_netherite", "o_enveloppes"])
ligne(-3, ("i_scierie", 0), ("i_cuisine", 2), ("i_tri", 4), ("i_vapeur", 6), ("i_coffres", 8))
ligne(-1.5, ("i_arbres", 0), ("i_canne", 2), ("i_pierre", 4), ("i_entonnoirs", 6), ("i_gisement", 8))
ligne(1, ("t_portes", 2), ("t_fluides", 6))
ligne(2, ("t_horaire", 0), ("t_fret", 4))
ligne(3, ("t_observateur", 2), ("t_triage", 6), ("t_long", 8))
ligne(5, ("t_ligne", 0), ("t_pneumatique", 2), ("t_tube", 4))
ligne(-4, ("a_reglement", 0), ("a_traite", 2))
ligne(-2, ("a_lance", 0), ("a_katana", 2), ("a_claymore", 4), ("a_netherite", 6), ("a_unique", 8))
ligne(0, ("a_obus", 0), ("a_mortier", 2))
ligne(2, ("a_silex", 0), ("a_revolver", 2), ("a_fusil", 4), ("a_gatling", 6)); ligne(3.5, ("a_blazegun", 4))
ligne(0, ("e_fondation", 0), ("h_grand", 2), ("h_murale", 4), ("h_pavoise", 8))
ligne(-1, ("h_gabarit", 6)); ligne(1, ("h_hissage", 6))
ligne(3, ("b_socle", 0), ("b_trophees", 2))
ligne(5, ("c_agrandissement", 0), ("c_infirmerie", 2), ("c_meteo", 4), ("c_forge", 6))
ligne(-3, ("e_pyramide", 0), ("e_fortin", 2), ("e_traces", 4))
ligne(-2, ("e_archiviste", 6))
ligne(-1, ("e_avantposte", 0), ("e_archives", 4))
ligne(-1, ("e_front", 0))
ligne(1.5, ("e_epave", 0), ("e_cite", 2), ("e_cite_meca", 4))
ligne(3, ("e_fuite", 0), ("e_forteresse", 2), ("e_donjons", 6))
ligne(5, ("r_ciel", 0), ("r_abysses", 2), ("r_toit", 4), ("r_vitesse", 6), ("r_voyage", 8))
ligne(7, ("b_araignee", 0), ("b_sphere", 2), ("b_gardienne", 4), ("b_centurion", 6))
ligne(8.5, ("b_wroughtnaut", 0), ("b_golem", 2), ("b_rodeur", 4), ("b_veilleur", 6))

for _ch in chapters:
    for _q in _ch["quests"]:
        _k = _CLE[_q["id"]]
        if _k in POS: _q["x"], _q["y"] = POS[_k]
        _q["hide_lines"] = _k in CACHER

# ============================================================ petits titres de section (images de chapitre)
import sys as _sys, unicodedata as _ud, re as _re
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "titres"))
from plaques import plaque as _plaque
H_TITRE = 0.75
# (chapitre, texte FR, texte EN, ancre x, ancre y, côté, style) ; côté « g » : à gauche de l'ancre, « d » : à droite, « h » : au-dessus
TITRES = [
 ("laiton", "Le bastion et l'arsenal", "The Bastion and the Arsenal", 0, -6, "g", "empire"),
 ("laiton", "L'atelier impérial", "The Imperial Workshop", 0, -4, "g", "empire"),
 ("laiton", "Le laiton", "Brass", 0, -2, "g", "empire"),
 ("laiton", "Usines et trains", "Factories and Trains", 0, 2, "g", "empire"),
 ("laiton", "Les gardiens", "The Guardians", 0, 4, "g", "empire"),
 ("laiton", "L'appel de l'Écho", "The Call of the Echo", 0, 6, "g", "echo"),
 ("reconquete", "Les assauts", "The Assaults", 0, -2, "g", "empire"),
 ("reconquete", "Les cités", "The Cities", 0, 2, "g", "empire"),
 ("reconquete", "Le choix", "The Choice", 16, 0, "h", "empire"),
 ("reconquete", "Fin de l'Empire", "Empire Ending", 20, -6.5, "g", "empire"),
 ("reconquete", "Fin de l'Écho", "Echo Ending", 20, 6.5, "g", "echo"),
 ("arcanes", "Les premiers murmures", "The First Whispers", 0, -6, "g", "echo"),
 ("arcanes", "Le grimoire", "The Spell Book", 0, -3, "g", "echo"),
 ("arcanes", "L'atelier réfractaire", "The Refractory Workshop", 0, -1.5, "g", "echo"),
 ("arcanes", "Les petits Échos", "The Little Echoes", 0, 1.5, "g", "echo"),
 ("arcanes", "La robe des Arcanes", "The Robe of the Arcana", 0, 4.5, "g", "echo"),
 ("arcanes", "Les Échos perdus", "The Lost Echoes", 13, -2, "h", "echo"),
 ("ingenierie", "L'ingénierie", "Engineering", 0, -3, "g", "empire"),
 ("ingenierie", "Trains et logistique", "Trains and Logistics", 0, 2, "g", "empire"),
 ("arsenal", "Les manuels", "The Manuals", 0, -4, "g", "empire"),
 ("arsenal", "Les lames", "Blades", 0, -2, "g", "empire"),
 ("arsenal", "L'artillerie", "Artillery", 0, 0, "g", "empire"),
 ("arsenal", "Les armes à feu", "Firearms", 0, 2, "g", "empire"),
 ("bases", "Fonder et pavoiser", "Found and Decorate", 0, 0, "g", "empire"),
 ("bases", "Les trophées", "Trophies", 0, 3, "g", "empire"),
 ("bases", "La capitale", "The Capital", 0, 5, "g", "empire"),
 ("exploration", "Ruines et vestiges", "Ruins and Remains", 0, -3, "g", "empire"),
 ("exploration", "Les cités perdues", "The Lost Cities", 0, 1.5, "g", "empire"),
 ("exploration", "Records d'ingénieur", "Engineer's Records", 0, 5, "g", "empire"),
 ("exploration", "Bestiaire", "Bestiary", 0, 7, "g", "empire"),
]
POS["l_vael"], POS["l_essai"] = (12, -2), (14, -2)
for _ch in chapters:
    for _q in _ch["quests"]:
        _k = _CLE[_q["id"]]
        if _k in POS: _q["x"], _q["y"] = POS[_k]
def _nom(t):
    t = _ud.normalize("NFD", t.lower()); t = "".join(c for c in t if not _ud.combining(c))
    return _re.sub(r"[^a-z0-9]+", "_", t).strip("_")
_TEX = os.path.join(sys.argv[1], "kubejs/assets/kubejs/textures/quests")
os.makedirs(_TEX, exist_ok=True)
for _f in os.listdir(_TEX):
    if _f.startswith("title_"): os.remove(os.path.join(_TEX, _f))
for _cle, _fr, _en, _x, _y, _cote, _st in TITRES:
    _ch = _par_cle.get(_cle) or next(c for c in chapters if c["key"] == _cle)
    _im = _plaque(_fr, _st)
    _fn = "title_" + _cle + "_" + _nom(_en) + ".png"
    _im.save(os.path.join(_TEX, _fn))
    _w = H_TITRE * _im.width / _im.height
    _cx = _x - 0.75 - _w / 2 if _cote == "g" else _x + 0.75 + _w / 2 if _cote == "d" else _x
    _cy = _y - 1.0 if _cote == "h" else _y
    _ch.setdefault("images", []).append({"image": "kubejs:textures/quests/" + _fn, "x": round(_cx, 3), "y": round(_cy, 3),
                                         "w": round(_w, 3), "h": H_TITRE})
