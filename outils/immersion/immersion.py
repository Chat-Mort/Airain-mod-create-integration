"""Immersion : noms des boss des mods, messages de mort de l'Empire, titres des tableaux, objets renommés, tableaux.
usage : immersion.py <dossier du pack>"""
import json, os, sys, shutil
from tableaux import TABLEAUX, AUTEURS, AUTEURS_EN
P = sys.argv[1]
A = os.path.join(P, "kubejs/assets")

BOSS = {  # espace de noms -> {entité: (fr, en)}
 "cataclysm": {"the_harbinger": ("L'Empereur d'Airain", "The Airain Emperor"),
               "netherite_monstrosity": ("Monstruosité de la forge des âmes", "Soul Forge Monstrosity"),
               "ender_guardian": ("Gardien du vide", "Void Guardian"),
               "the_prowler": ("La Sentinelle", "The Sentinel"),
               "the_watcher": ("Drone de surveillance", "Surveillance Drone"),
               "ender_golem": ("Golem du vide", "Void Golem")},
 "mowziesmobs": {"ferrous_wroughtnaut": ("Le Colosse de fer", "The Iron Colossus")},
 "mebahelcreaturesdwarven": {"dwarven_spider": ("Araignée de bronze", "Bronze Spider"),
                             "dwarven_sphere": ("Sphère de bronze", "Bronze Sphere"),
                             "dwarven_spider_guardian": ("Araignée gardienne", "Guardian Spider"),
                             "dwarven_centurion": ("Centurion à vapeur", "Steam Centurion")},
}

MORTS = {  # clé : (fr, en)
 "mob": ("%1$s a été mis en pièces par %2$s", "%1$s was taken apart by %2$s"),
 "player": ("%1$s a été démonté par %2$s", "%1$s was dismantled by %2$s"),
 "arrow": ("%1$s a reçu un carreau de %2$s", "%1$s caught a bolt from %2$s"),
 "trident": ("%1$s a été harponné par %2$s", "%1$s was harpooned by %2$s"),
 "fireball": ("%1$s a reçu un boulet incandescent de %2$s", "%1$s was hit by a glowing shot from %2$s"),
 "explosion": ("%1$s a sauté avec la chaudière", "%1$s went up with the boiler"),
 "explosion.player": ("%1$s a été soufflé par %2$s", "%1$s was blasted apart by %2$s"),
 "sonic_boom": ("%1$s a été pulvérisé par un rayon d'Écho", "%1$s was shattered by an Echo beam"),
 "sonic_boom.player": ("%1$s a été pulvérisé par un rayon d'Écho en fuyant %2$s", "%1$s was shattered by an Echo beam while fleeing %2$s"),
 "inFire": ("%1$s est tombé dans le foyer", "%1$s fell into the firebox"),
 "onFire": ("%1$s a fini calciné comme une vieille bielle", "%1$s was burnt like an old piston rod"),
 "lava": ("%1$s a voulu nager dans la fonte en fusion", "%1$s tried to swim in molten iron"),
 "lava.player": ("%1$s a plongé dans la fonte en fusion pour fuir %2$s", "%1$s dove into molten iron to escape %2$s"),
 "fall": ("%1$s a raté son atterrissage", "%1$s botched the landing"),
 "fall.player": ("%1$s a raté son atterrissage en fuyant %2$s", "%1$s botched the landing while fleeing %2$s"),
 "flyIntoWall": ("%1$s a percuté le décor à pleine vapeur", "%1$s hit the scenery at full steam"),
 "drown": ("%1$s a pris l'eau comme une chaudière percée", "%1$s took on water like a leaky boiler"),
 "starve": ("%1$s a oublié de remettre du charbon", "%1$s forgot to add more coal"),
 "inWall": ("%1$s s'est fait coincer dans les engrenages", "%1$s got caught in the gears"),
 "cramming": ("%1$s a été compressé comme une plaque de laiton", "%1$s was pressed like a brass sheet"),
 "outOfWorld": ("%1$s est tombé hors de l'Empire", "%1$s fell out of the Empire"),
 "witherSkull": ("%1$s a reçu un crâne brûlant du %2$s", "%1$s took a burning skull from the %2$s"),
 "wither": ("%1$s s'est désagrégé", "%1$s crumbled away"),
 "magic": ("%1$s a été emporté par l'Écho", "%1$s was taken by the Echo"),
 "indirectMagic": ("%1$s a été emporté par l'Écho de %2$s", "%1$s was taken by the Echo of %2$s"),
 "dragonBreath": ("%1$s a été dissous par le souffle du Gardien des Cieux", "%1$s was dissolved by the Sky Guardian's breath"),
 "lightningBolt": ("%1$s a servi de paratonnerre", "%1$s served as a lightning rod"),
 "freeze": ("%1$s a gelé comme un tuyau en hiver", "%1$s froze like a pipe in winter"),
 "generic": ("%1$s s'est arrêté", "%1$s stopped working"),
}


# Butins renommés (le nom vanilla reste visible en gris dans l'infobulle : kubejs/server_scripts/airain_paliers.js)
BUTINS = {
 "item.minecraft.phantom_membrane": ("Toile étrange", "Strange Fabric", "Membrane de phantom", "Phantom Membrane"),
 "item.minecraft.ghast_tear": ("Goutte d'âme", "Soul Droplet", "Larme de ghast", "Ghast Tear"),
 "item.minecraft.magma_cream": ("Scorie en fusion", "Molten Slag", "Crème de magma", "Magma Cream"),
 "block.minecraft.wither_skeleton_skull": ("Masque des enfers", "Infernal Mask", "Crâne de wither squelette", "Wither Skeleton Skull"),
 "item.minecraft.nether_star": ("Cœur du Gardien des enfers", "Infernal Guardian Core", "Étoile du Nether", "Nether Star"),
 "block.minecraft.dragon_egg": ("Œuf du Gardien des Cieux", "Sky Guardian's Egg", "Œuf de dragon", "Dragon Egg"),
}

def fusion(chemin, d):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    j = json.load(open(chemin)) if os.path.exists(chemin) else {}
    j.update(d); json.dump(j, open(chemin, "w"), ensure_ascii=False, indent=2)

for code, k in (("fr_fr", 0), ("en_us", 1)):
    for ns, ents in BOSS.items():
        fusion(f"{A}/{ns}/lang/{code}.json", {f"entity.{ns}.{e}": n[k] for e, n in ents.items()})
    L = {f"death.attack.{c}": v[k] for c, v in MORTS.items()}
    auteurs = AUTEURS if k == 0 else AUTEURS_EN
    from plans_final import PLANCHES, AUTEURS_PLANS
    for i, (nom, (_, fr, en)) in enumerate(TABLEAUX.items()):
        if nom in PLANCHES:                                   # plans d'ingénieur (v6)
            _, fr, en = PLANCHES[nom]; aut = AUTEURS_PLANS[k]
            L[f"painting.minecraft.{nom}.title"] = fr if k == 0 else en
            L[f"painting.minecraft.{nom}.author"] = aut[i % len(aut)]
            continue
        L[f"painting.minecraft.{nom}.title"] = fr if k == 0 else en
        L[f"painting.minecraft.{nom}.author"] = auteurs[i % len(auteurs)]
    L["item.minecraft.totem_of_undying"] = "Cœur de secours" if k == 0 else "Spare Heart"
    for cle, (fr, en, vfr, ven) in BUTINS.items():
        L[cle] = fr if k == 0 else en
    fusion(f"{A}/kubejs/lang/{code}.json", {f"tooltip.kubejs.vanilla.{cle.split('.')[-1]}": (vfr if k == 0 else ven) for cle, (fr, en, vfr, ven) in BUTINS.items()})
    fusion(f"{A}/minecraft/lang/{code}.json", L)

dst = f"{A}/minecraft/textures/painting"; os.makedirs(dst, exist_ok=True)
for nom in TABLEAUX: shutil.copy(f"painting7/{nom}.png", f"{dst}/{nom}.png")
print(len(BOSS), "espaces de noms,", len(MORTS), "messages de mort,", len(TABLEAUX), "tableaux")
