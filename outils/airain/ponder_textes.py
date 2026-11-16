# 1.64 : textes des scènes Ponder, en anglais (texte de base, dans le code) et en français (fichiers de langue).
# Génère PonderTextes.java (un tableau de textes par scène, dans l'ordre d'apparition) et les clés airain.ponder.*.
import json
S={
 'haut_fourneau':(("The Imperial Blast Furnace","Le haut-fourneau impérial"),[
  ("The furnace sits on a Blaze Burner, under the grate in the middle of the hearth.","Le haut-fourneau repose sur un brûleur à blaze, sous la grille au milieu du creuset."),
  ("The hearth: 5 × 5 with cut corners, two rows of fire bricks. The taphole sits in the middle of the front face.","Le creuset : 5 × 5 aux coins coupés, deux rangs de briques réfractaires. Le trou de coulée au milieu de la face avant."),
  ("One to three tuyeres on the sides and at the back, each blown by a Create fan. The faster the fan, the faster the furnace.","Une à trois tuyères sur les côtés et à l'arrière, chacune soufflée par un ventilateur de Create. Plus il tourne vite, plus le fourneau produit."),
  ("The shaft: 3 × 3, three rows, hollow. The throat goes in the middle of the top.","La cuve : 3 × 3 sur trois rangs, creuse. Le gueulard au milieu du sommet."),
  ("Bare-hand right-click on the taphole: missing blocks appear as a hologram, and you can place them right into it.","Clic droit main nue sur le trou de coulée : les blocs manquants apparaissent en hologramme, et se posent directement dedans."),
  ("Pour the charge into the throat. Superheated burner: 3 copper, 1 zinc and 1 flux give molten airain. Heated burner: automaton scrap is remelted.","Versez la charge par le gueulard. Brûleur surchauffé : 3 cuivres, 1 zinc et 1 fondant donnent de l'airain en fusion. Brûleur chauffé : la ferraille des automates se refond."),
  ("Molten airain comes out of the taphole into pipes; slag comes out through a funnel.","L'airain fondu sort du trou de coulée dans les tuyaux ; le laitier, par un entonnoir.")]),
 'laminoir':(("Rolling Airain into Wire","Le laminoir"),[
  ("The Rolling Mill is driven by a shaft on its side.","Le laminoir est entraîné par un arbre sur le côté."),
  ("Airain ingots go in by right-click, funnel or belt. Each ingot becomes 2 wires.","Les lingots d'airain entrent par clic droit, entonnoir ou tapis. Chaque lingot donne 2 fils."),
  ("Bare hand: take the wire back. 8 wires around an airain sheet make 2 cables.","Main nue : reprendre le fil. 8 fils autour d'une plaque d'airain donnent 2 câbles.")]),
 'telepherique':(("The Imperial Cable Car","Le téléphérique impérial"),[
  ("A line needs a station at each end. Stations are two blocks high.","Une ligne a besoin d'une gare à chaque bout. Les gares font deux blocs de haut."),
  ("In between, stacked pylons topped with their head. At most 32 blocks per span, 8 pylons per line.","Entre les deux, des pylônes empilés coiffés de leur tête. 32 blocs au plus par travée, 8 pylônes par ligne."),
  ("Cable in hand: right-click a node, then the next one. The heads turn to follow the line.","Câble en main : clic droit sur un nœud, puis sur le suivant. Les têtes s'orientent seules dans l'axe."),
  ("Place the gondola on a station and drive a station with a shaft from below: its speed sets the gondola's speed.","Posez la nacelle sur une gare, et entraînez une gare par un arbre en dessous : sa vitesse règle celle de la nacelle."),
  ("Right-click inside the gondola: it leaves two seconds later. Right-click a station: the gondola comes.","Clic droit dans la nacelle : départ deux secondes plus tard. Clic droit sur une gare : la nacelle vient.")]),
 'monte_charge':(("The Lift","Le monte-charge"),[
  ("A winch, driven by Create rotation, at the foot of a rack mast.","Un treuil, entraîné par la rotation de Create, au pied d'un mât à crémaillère."),
  ("The cabin runs on the side where the mast was placed.","La cabine circule du côté où le mât a été posé."),
  ("Every catwalk placed opposite the mast, beyond the cabin, becomes a floor.","Chaque passerelle posée en face du mât, de l'autre côté de la cabine, devient un étage."),
  ("In the cabin: right-click to go up a floor, sneak to go down. The call box brings the cabin.","Dans la cabine : clic droit pour monter d'un étage, accroupi pour descendre. Le boîtier d'appel fait venir la cabine.")]),
 'passages_mobiles':(("Moving Crossings","Les passages mobiles"),[
  ("The drawbridge and the telescopic catwalk slip into a catwalk line, facing the gap.","Le pont-levis et la passerelle rétractable se glissent dans une ligne de passerelles, face au vide."),
  ("They drive the 1 to 4 catwalks that follow. Wrench in the middle of the floor: change the length.","Ils entraînent les 1 à 4 passerelles qui suivent. Clé au milieu du sol : changer la longueur."),
  ("A shaft from below: one direction deploys, the other raises or retracts. A redstone signal raises them too.","Un arbre par-dessous : un sens déploie, l'autre relève ou rentre. Un signal de redstone les relève aussi."),
  ("While the crossing is open, railings close both ends.","Tant que le passage est ouvert, des rambardes ferment les deux bouts.")]),
 'conduite_air':(("Carrying the Wind","La conduite d'air"),[
  ("A Create fan blows into an air duct. Ducts connect on their own.","Un ventilateur de Create souffle dans un conduit d'air. Les conduits se raccordent seuls."),
  ("At the far end, the air vent gives back the same current: same force, same range, same processing.","À l'autre bout, la bouche d'air rend le même courant : même force, même portée, mêmes traitements."),
  ("Up to 64 ducts. Engineer's goggles show the transmitted current.","Jusqu'à 64 conduits. Les lunettes d'ingénieur montrent le courant transmis.")]),
 'rayonnage':(("The Imperial Racking","Le rayonnage impérial"),[
  ("Rack bays side by side and stacked form a single inventory. One item per bay, 32 stacks.","Les casiers côte à côte et empilés forment un seul inventaire. Un objet par casier, 32 piles."),
  ("A funnel on any bay is enough: each item goes to the bay that already holds it, otherwise to an empty bay.","Un entonnoir sur n'importe quel casier suffit : chaque objet va dans le casier qui le contient déjà, sinon dans un casier libre."),
  ("The stock is visible on the pallet, and the label shows the exact count.","Le stock se voit sur la palette, et l'étiquette donne la quantité exacte."),
  ("Right-click to deposit, twice quickly for everything you carry. Left-click: take a stack; sneak: a single one.","Clic droit pour déposer, deux fois vite pour tout ce que vous portez. Clic gauche : une pile ; accroupi : un seul."),
  ("Wrench: reserve a bay for its item. Reinforcements I to IV: up to 512 stacks.","Clé : réserver un casier à son objet. Renforts I à IV : jusqu'à 512 piles.")]),
 'tableau_emaille':(("The Enamel Board","Le tableau émaillé"),[
  ("Enamel boards side by side form a single board, up to 16 × 8.","Les tableaux émaillés posés côte à côte n'en forment qu'un, jusqu'à 16 × 8."),
  ("Bare-hand right-click opens the menu: lines, enamel, frame, font, light, mounting.","Clic droit main nue : le menu. Lignes, émail, cadre, police, lumière, accrochage."),
  ("One Create Display Link per line: stress, speed, stock, trains… Value and bar lines read numbers and percentages.","Une liaison d'affichage de Create par ligne : stress, vitesse, stock, trains… Les lignes valeur et barre lisent nombres et pourcentages."),
  ("Against a wall, hanging under a block or on a post: the board finds its mounting by itself.","Contre un mur, pendu sous un bloc ou sur un pied : le tableau trouve seul son accrochage.")]),
}
J='''package fr.chatmort.airain.ponder;

/** Textes de base (anglais) des scènes Ponder, dans l'ordre d'apparition ; généré par ponder_textes.py. */
final class PonderTextes {
	private PonderTextes() {}
'''
for k,((he,hf),T) in S.items():
    J+=f'\tstatic final String {k.upper()}_TITRE = {json.dumps(he,ensure_ascii=False)};\n'
    J+=f'\tstatic final String[] {k.upper()} = {{'+', '.join(json.dumps(e,ensure_ascii=False) for e,_ in T)+'};\n'
J+='}\n'
open('/home/claude/airain-mod-create-integration/src/main/java/fr/chatmort/airain/ponder/PonderTextes.java','w').write(J)
L='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/lang/'
for f,i in (('en_us.json',0),('fr_fr.json',1)):
    d=json.load(open(L+f))
    for k,(h,T) in S.items():
        d[f'airain.ponder.{k}.header']=h[i]
        for n,t in enumerate(T): d[f'airain.ponder.{k}.text_{n+1}']=t[i]
    json.dump(d,open(L+f,'w'),ensure_ascii=False,indent=1)
print('textes ponder ok')
