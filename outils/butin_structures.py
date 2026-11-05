"""Butin des structures vanilla : un tirage EN PLUS du butin d'origine (modificateurs de butin NeoForge,
neoforge:add_table), qui fait de chaque structure une trace de l'Empire. usage : python3 butin_structures.py <pack>"""
import json, os, sys

P = sys.argv[1]
def w(rel, obj):
    f = os.path.join(P, "kubejs/data", rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)

def n(item, a, b, poids=1):
    return {"type": "minecraft:item", "name": item, "weight": poids,
            "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}}]}
def vide(poids): return {"type": "minecraft:empty", "weight": poids}
def ecrit(doc, pages):
    return {"type": "minecraft:item", "name": "minecraft:written_book", "functions": [
        {"function": "minecraft:set_written_book_pages", "mode": "replace_all",
         "pages": [{"translate": "airain.%s.p%d" % (doc, i)} for i in range(1, pages + 1)]},
        {"function": "minecraft:set_name", "name": {"translate": "airain.%s.titre" % doc, "italic": False}},
        {"function": "minecraft:set_custom_data", "tag": "{airain_doc:\"%s\"}" % doc}]}

# famille : (structures vanilla, objets, chance de l'écrit)
FAMILLES = {
  "mine": (["abandoned_mineshaft", "simple_dungeon"],
           [n("kubejs:ferraille", 2, 5, 4), n("kubejs:huile_machine", 1, 2, 3), n("kubejs:rouage_brise", 1, 1, 2),
            n("create:zinc_nugget", 2, 6, 3), vide(3)], 0.30),
  "prospecteur": (["desert_pyramid", "jungle_temple", "igloo_chest"],
           [n("numismatics:spur", 4, 12, 4), n("numismatics:bevel", 1, 3, 2), vide(2)], 0.35),
  "cargaison": (["shipwreck_supply", "shipwreck_treasure", "buried_treasure", "underwater_ruin_big", "underwater_ruin_small"],
           [n("numismatics:bevel", 2, 4, 3), n("numismatics:sprocket", 1, 2, 2), n("create:copper_sheet", 2, 5, 2), vide(3)], 0.30),
  "conseil": (["stronghold_library", "stronghold_corridor", "stronghold_crossing"],
           [n("minecraft:paper", 2, 6, 3), n("numismatics:sprocket", 1, 2, 1), vide(2)], 0.35),
  "profondeurs": (["ancient_city"],
           [n("kubejs:fragment_resonance", 1, 2, 3), n("numismatics:sprocket", 1, 2, 1), vide(2)], 0.35),
  "nether": (["nether_bridge", "bastion_bridge", "bastion_other", "bastion_treasure", "bastion_hoglin_stable"],
           [n("kubejs:ferraille", 2, 5, 4), n("kubejs:rouage_brise", 1, 2, 2), n("kubejs:huile_machine", 1, 1, 2),
            n("numismatics:cog", 1, 1, 1), vide(3)], 0.30),
  "ciel": (["end_city_treasure"],
           [n("numismatics:cog", 1, 2, 3), n("numismatics:crown", 1, 1, 1), vide(6)], 0.35),
}
PAGES = 3

entrees = []
for fam, (structs, objets, chance) in FAMILLES.items():
    w("kubejs/loot_table/chests/vanilla_%s.json" % fam, {"type": "minecraft:chest", "pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": objets},
        {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": chance}],
         "entries": [ecrit(fam, {"conseil": 4}.get(fam, PAGES))]}]})
    for s in structs:
        w("kubejs/loot_modifiers/vanilla_%s.json" % s, {
            "type": "neoforge:add_table",
            "conditions": [{"condition": "neoforge:loot_table_id", "loot_table_id": "minecraft:chests/" + s}],
            "table": "kubejs:chests/vanilla_" + fam})
        entrees.append("kubejs:vanilla_" + s)
w("neoforge/loot_modifiers/global_loot_modifiers.json", {"replace": False, "entries": entrees})

TX = {"fr_fr": {
  "airain.mine.titre": "Carnet de mineur",
  "airain.mine.p1": "Galerie 7, à quarante mètres sous la plaine.\n\nOn creuse pour le Cœur : du cuivre, du zinc, et encore du cuivre.\n\nLe contremaître dit qu'il en faudra plus que tout ce que la terre contient.",
  "airain.mine.p2": "Les rampeuses d'entretien descendent seules, maintenant. Elles graissent les rails et recousent les câbles.\n\nPersonne ne les a programmées pour ça.",
  "airain.mine.p3": "Dernier quart. On remonte tous demain pour le Transfert.\n\nJ'ai laissé ma lampe allumée au fond de la galerie. Si je ne redescends pas, qu'elle éclaire quelqu'un d'autre.",
  "airain.prospecteur.titre": "Lettre d'un prospecteur",
  "airain.prospecteur.p1": "À ma sœur, au comptoir de l'avant-poste sud.\n\nJ'ai trouvé un temple bien plus vieux que l'Empire. Ceux qui l'ont bâti aimaient déjà les pièges et les mécanismes.\n\nRien de nouveau sous le soleil.",
  "airain.prospecteur.p2": "Je cache ici ma paye. Le Conseil dit qu'on n'aura plus besoin d'argent après le Transfert.\n\nAlors pourquoi est-ce qu'il compte encore le nôtre ?",
  "airain.prospecteur.p3": "Si je ne reviens pas, prends les pièces.\n\nEt ne monte pas dans une capsule avant d'avoir eu de mes nouvelles.",
  "airain.cargaison.titre": "Manifeste de cargaison",
  "airain.cargaison.p1": "Cargo « Opiniâtre », port d'attache : le quai de l'Ouest.\n\nChargement : 40 tonnes de cuivre, 12 de zinc, 300 rouages.\n\nDestination : le chantier du Cœur.",
  "airain.cargaison.p2": "Note du capitaine.\n\nLe Conseil réquisitionne aussi les passagers. Tous, sans exception. Ils voyagent en cale, endormis, et on m'interdit de les réveiller.",
  "airain.cargaison.p3": "Nous avons viré vers le large cette nuit.\n\nSi le Cœur veut cette cargaison, qu'il vienne la chercher au fond.\n\n— Capitaine Morvan",
  "airain.conseil.titre": "Registre du Conseil",
  "airain.conseil.p1": "Registre du Conseil, séance 1.\n\nUn moteur unique alimentera toutes les cités. Plus de famine, plus d'hiver.\n\nLe projet prend le nom de Cœur.",
  "airain.conseil.p2": "Séance 88.\n\nLes ingénieurs signalent, sous cette forteresse, un anneau de pierre aux yeux vides, plus ancien que l'Empire. Ils disent qu'il mène ailleurs.\n\nLa chancelière Strass ordonne de le sceller.",
  "airain.conseil.p3": "Séance 140.\n\nLe Cœur demande plus que du métal.\n\nVote à l'unanimité : le Transfert commence au prochain cycle.",
  "airain.conseil.p4": "Séance 141, à huis clos.\n\nLa chancelière Strass rappelle que le fondateur a montré la voie. Auguste Ferrand dort dans sa première usine depuis quarante ans, et elle tourne encore.\n\nCet essai n'a pas de numéro. Il n'a jamais existé.",
  "airain.profondeurs.titre": "Rapport d'expédition des profondeurs",
  "airain.profondeurs.p1": "Expédition 3, sous la roche noire.\n\nUne cité entière, bien plus ancienne que nous. Ses habitants ont disparu. Ils ont laissé un grand portail qui ne mène nulle part.",
  "airain.profondeurs.p2": "Ici, l'Écho est plus fort que partout ailleurs. Les cristaux chantent quand on se tait.\n\nJe crois que ce peuple a fait la même erreur que nous, bien avant nous.",
  "airain.profondeurs.p3": "Le gardien des lieux entend tout.\n\nMarchez doucement. Et surtout, ne parlez pas du Cœur.",
  "airain.nether.titre": "Journal de l'expédition du Nether",
  "airain.nether.p1": "Expédition impériale vers l'autre monde, jour 3.\n\nLa chaleur fait fondre la soudure. On habille les machines de briques noires pour qu'elles tiennent.",
  "airain.nether.p2": "Jour 19.\n\nLes automates noircis gardent les forteresses. Ce sont les nôtres, envoyés avant nous.\n\nIls ne reconnaissent plus nos insignes.",
  "airain.nether.p3": "Jour 40.\n\nLe Gardien des enfers s'est éveillé. Le Conseil voulait son cœur pour nourrir le nôtre.\n\nNous ne rentrerons pas.",
  "airain.ciel.titre": "Dernier message",
  "airain.ciel.p1": "Chasseur de la flotte du Conseil, dernier journal.\n\nNous avons franchi l'anneau de pierre. De l'autre côté : des tours violettes qui chantent. Les fugitifs ne sont pas morts. Ils vivent ici.",
  "airain.ciel.p2": "Leur bête a abattu trois de nos navires. Ils l'ont appelée avec l'Écho, et l'ont liée aux tours noires.\n\nUn de leurs enfants m'a demandé où dormait ma mère. Dans le Cœur, ai-je dit. Il a pleuré.",
  "airain.ciel.p3": "Ils disent que le Cœur ne garde pas les âmes. Qu'il les brûle.\n\nJe n'ai plus d'encre, et je ne rentrerai pas.\n\nSi vous lisez ceci : ne lui donnez rien.",
}, "en_us": {
  "airain.mine.titre": "Miner's Notebook",
  "airain.mine.p1": "Gallery 7, forty metres under the plain.\n\nWe dig for the Core: copper, zinc, and more copper.\n\nThe foreman says it will need more than the whole earth holds.",
  "airain.mine.p2": "The maintenance crawlers go down on their own now. They grease the rails and stitch the cables.\n\nNobody programmed them to.",
  "airain.mine.p3": "Last shift. We all go up tomorrow for the Transfer.\n\nI left my lamp lit at the end of the gallery. If I don't come back down, let it light someone else's way.",
  "airain.prospecteur.titre": "A Prospector's Letter",
  "airain.prospecteur.p1": "To my sister, at the counter of the southern outpost.\n\nI found a temple far older than the Empire. Its builders already loved traps and mechanisms.\n\nNothing new under the sun.",
  "airain.prospecteur.p2": "I'm hiding my pay here. The Council says we won't need money after the Transfer.\n\nThen why does it still count ours?",
  "airain.prospecteur.p3": "If I don't come back, take the coins.\n\nAnd don't step into a capsule before you hear from me.",
  "airain.cargaison.titre": "Cargo Manifest",
  "airain.cargaison.p1": "Freighter \"Stubborn\", home port: the Western Quay.\n\nLoad: 40 tonnes of copper, 12 of zinc, 300 cogwheels.\n\nDestination: the Core worksite.",
  "airain.cargaison.p2": "Captain's note.\n\nThe Council requisitions the passengers too. All of them. They travel in the hold, asleep, and I am forbidden to wake them.",
  "airain.cargaison.p3": "We turned out to sea tonight.\n\nIf the Core wants this cargo, let it come and fetch it from the bottom.\n\n— Captain Morvan",
  "airain.conseil.titre": "Council Register",
  "airain.conseil.p1": "Council register, session 1.\n\nA single engine will power every city. No more famine, no more winter.\n\nThe project is named the Core.",
  "airain.conseil.p2": "Session 88.\n\nThe engineers report, beneath this fortress, a stone ring with empty eyes, older than the Empire. They say it leads elsewhere.\n\nChancellor Strass orders it sealed.",
  "airain.conseil.p3": "Session 140.\n\nThe Core asks for more than metal.\n\nUnanimous vote: the Transfer begins next cycle.",
  "airain.conseil.p4": "Session 141, behind closed doors.\n\nChancellor Strass recalls that the founder showed the way. Auguste Ferrand has slept inside his first factory for forty years, and it still runs.\n\nThis trial has no number. It never happened.",
  "airain.profondeurs.titre": "Deep Expedition Report",
  "airain.profondeurs.p1": "Expedition 3, beneath the black rock.\n\nA whole city, far older than us. Its people are gone. They left a great portal that leads nowhere.",
  "airain.profondeurs.p2": "Here the Echo is stronger than anywhere else. The crystals sing when we fall silent.\n\nI think these people made the same mistake as us, long before us.",
  "airain.profondeurs.p3": "The keeper of this place hears everything.\n\nWalk softly. And above all, do not speak of the Core.",
  "airain.nether.titre": "Nether Expedition Log",
  "airain.nether.p1": "Imperial expedition to the other world, day 3.\n\nThe heat melts the solder. We clad the machines in black bricks so they hold.",
  "airain.nether.p2": "Day 19.\n\nThe blackened automatons guard the fortresses. They are ours, sent before us.\n\nThey no longer recognize our insignia.",
  "airain.nether.p3": "Day 40.\n\nThe Infernal Guardian has woken. The Council wanted its core to feed ours.\n\nWe will not return.",
  "airain.ciel.titre": "Last Message",
  "airain.ciel.p1": "Hunter of the Council fleet, last log.\n\nWe crossed the stone ring. On the other side: purple towers that sing. The fugitives are not dead. They live here.",
  "airain.ciel.p2": "Their beast brought down three of our ships. They called it with the Echo, and bound it to the black towers.\n\nOne of their children asked me where my mother sleeps. In the Core, I said. He cried.",
  "airain.ciel.p3": "They say the Core does not keep souls. That it burns them.\n\nI am out of ink, and I will not go home.\n\nIf you are reading this: give it nothing.",
}}
L = os.path.join(P, "kubejs/assets/kubejs/lang")
for code, t in TX.items():
    f = os.path.join(L, code + ".json"); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("butin des structures vanilla :", len(entrees), "modificateurs")
