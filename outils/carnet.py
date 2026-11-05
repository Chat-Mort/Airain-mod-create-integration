import json, os, sys
P = sys.argv[1]
ROM = ["I", "II", "III", "IV", "V", "VI", "VII"]
FR = [
 "Morgana m'a mis un cristal dans la main et m'a dit de me taire.\n\nAu bout d'une heure, il a fait froid. Elle a souri : « Tu viens de rencontrer quelqu'un. »",
 "On ne prend pas l'Écho, on le nourrit. Les fleurs, la lave, les bêtes qui naissent.\n\nCe qui vit lui rend un peu de ce que l'Empire lui a volé.",
 "Ma première volonté était une lumière. Elle a tremblé, puis elle a tenu toute la nuit.\n\nQuelqu'un, là-dedans, avait accepté de m'aider.",
 "Pour le départ vers le Vide, Morgana a ouvert le ciel. Elle n'avait jamais lancé un rituel aussi grand.\n\nElle a saigné du nez pendant trois jours.",
 "Le petit être jaune refuse de me quitter. Morgana dit qu'il était peut-être un enfant, avant.\n\nJe ne veux pas savoir. Je l'ai appelé Pépin.",
 "On ne porte pas la robe pour se protéger. On la porte pour que les égarés nous reconnaissent.",
 "La nuit où Morgana a appelé le Gardien des Cieux, j'étais à côté d'elle.\n\nLa bête a ouvert les yeux, et pendant un instant, elle ne savait pas qui elle devait servir.\n\nMorgana non plus, je crois.\n\n— une apprentie"]
EN = [
 "Morgana put a crystal in my hand and told me to be quiet.\n\nAfter an hour, it turned cold. She smiled: \"You've just met someone.\"",
 "You don't take the Echo, you feed it. Flowers, lava, newborn beasts.\n\nWhat lives gives back a little of what the Empire stole from it.",
 "My first will was a light. It trembled, then it held all night.\n\nSomeone in there had agreed to help me.",
 "For the departure to the Void, Morgana opened the sky. She had never cast a ritual so great.\n\nHer nose bled for three days.",
 "The little yellow one refuses to leave me. Morgana says it may have been a child, before.\n\nI don't want to know. I named it Pip.",
 "You don't wear the robe to protect yourself. You wear it so the lost recognise you.",
 "The night Morgana called the Sky Guardian, I was beside her.\n\nThe beast opened its eyes, and for a moment it did not know whom it should serve.\n\nNeither did Morgana, I think.\n\n— an apprentice"]
for i in range(7):
    n = i + 1
    lt = {"type": "minecraft:chest", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:written_book", "functions": [
        {"function": "minecraft:set_written_book_pages", "mode": "replace_all", "pages": [{"translate": f"airain.apprentie{n}.p1"}]},
        {"function": "minecraft:set_name", "name": {"translate": f"airain.apprentie{n}.titre", "italic": False}},
        {"function": "minecraft:set_custom_data", "tag": "{airain_doc:\"apprentie%d\"}" % n}]}]}]}
    d = f"{P}/kubejs/data/kubejs/loot_table/carnet"; os.makedirs(d, exist_ok=True)
    json.dump(lt, open(f"{d}/apprentie_{n}.json", "w"), indent=1, ensure_ascii=False)
for lang, T, titre in (("fr_fr", FR, "Carnet de l'apprentie, %s"), ("en_us", EN, "The Apprentice's Notebook, %s")):
    f = f"{P}/kubejs/assets/kubejs/lang/{lang}.json"
    j = json.load(open(f))
    for i in range(7):
        j[f"airain.apprentie{i+1}.titre"] = titre % ROM[i]; j[f"airain.apprentie{i+1}.p1"] = T[i]
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("ok")
