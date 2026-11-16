# 1.60 : ressources du tableau émaillé (textures, police impériale, modèles, butin, recette, noms, menu, livre).
import json, os, shutil
from PIL import Image
R='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=R+'assets/airain/'; Dd=R+'data/'
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
# ---- émail : blanc, teinté par la couleur choisie ; brillant = reflet doux en haut à gauche, mat = aplat (pas de bruit)
def email(brillant):
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            v=0.90
            if brillant:
                d=(x+y)/30.0
                v=0.86+0.14*max(0,1-d*1.6)
                if x+y in (3,4): v=1.0
            g=int(255*min(1,v)); p[x,y]=(g,g,g,255)
    return im
email(True).save(AS+'textures/block/enamel.png'); email(False).save(AS+'textures/block/enamel_matte.png')
# icône du bloc (objet) : émail noir, deux lignes crème et une barre d'or
ic=Image.new('RGBA',(16,16),(29,29,33,255)); q=ic.load()
for x in range(2,14): q[x,4]=(236,228,206,255)
for x in range(2,9): q[x,7]=(236,228,206,255)
for x in range(10,14): q[x,7]=(232,196,110,255)
for x in range(2,12): q[x,10]=(232,196,110,255)
for x in range(12,14): q[x,10]=(62,58,52,255)
for x in range(0,16): q[x,0]=(44,44,50,255)
ic.save(AS+'textures/block/enamel_board_item.png')
# ---- police impériale (Caladea Bold tramée, 2× la résolution de la police de Minecraft)
os.makedirs(AS+'textures/font',exist_ok=True); os.makedirs(AS+'font',exist_ok=True)
shutil.copy('/home/claude/maquettes/police/imperiale.png',AS+'textures/font/imperiale.png')
shutil.copy('/home/claude/maquettes/police/imperiale.json',AS+'font/imperiale.json')
# ---- modèles et blockstate (le dessin est fait par le rendu du bloc-entité)
w(AS+'blockstates/enamel_board.json',{"variants":{"":{"model":"airain:block/enamel_board"}}})
w(AS+'models/block/enamel_board.json',{"textures":{"particle":"airain:block/cut_airain"},"elements":[]})
def el(fr,to,t,faces=("north","south","east","west","up","down"),uv=None):
    f={}
    for k in faces:
        dx,dy,dz=[abs(to[i]-fr[i]) for i in range(3)]
        a,b={"north":(dx,dy),"south":(dx,dy),"east":(dz,dy),"west":(dz,dy),"up":(dx,dz),"down":(dx,dz)}[k]
        u0=(16-a)/2; v0=(16-b)/2
        f[k]={"texture":t,"uv":(uv or {}).get(k,[u0,v0,u0+a,v0+b])}
    return {"from":fr,"to":to,"faces":f}
E=[el([0,0,14],[16,16,16],'#c'),el([3,3,13],[13,13,14],'#e',("north",),{"north":[3,3,13,13]}),
   el([0,13,10.5],[16,16,14],'#p'),el([0,0,10.5],[16,3,14],'#p'),el([0,3,10.5],[3,13,14],'#p'),el([13,3,10.5],[16,13,14],'#p')]
w(AS+'models/item/enamel_board.json',{"parent":"minecraft:block/block","textures":{"particle":"airain:block/cut_airain","c":"airain:block/cut_airain","p":"airain:block/airain_beam_plate","e":"airain:block/enamel_board_item"},
  "elements":E,"display":{"gui":{"rotation":[30,225,0],"scale":[0.625,0.625,0.625]},"fixed":{"rotation":[0,180,0],"scale":[0.5,0.5,0.5]}}})
# ---- butin, outil, recette
w(Dd+'airain/loot_table/blocks/enamel_board.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:enamel_board"}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
p=Dd+'minecraft/tags/block/mineable/pickaxe.json'; d=json.load(open(p))
if 'airain:enamel_board' not in d['values']: d['values'].append('airain:enamel_board')
w(p,d)
w(Dd+'airain/recipe/affichage/enamel_board.json',{"type":"minecraft:crafting_shaped","category":"redstone","pattern":["NSN","SDS","NSN"],
  "key":{"N":{"item":"airain:airain_nugget"},"S":{"item":"airain:airain_sheet"},"D":{"item":"minecraft:black_dye"}},"result":{"id":"airain:enamel_board","count":4}})
# ---- noms, menu, liaison d'affichage, livre
FR={"block.airain.enamel_board":"Tableau émaillé","airain.display_source.cannon_casting":"Moulage de canon",
 "airain.email.ligne":"Ligne %s","airain.email.apercu":"Aperçu","airain.email.taille_tableau":"%s × %s blocs",
 "airain.email.onglet.contenu":"Contenu","airain.email.onglet.style":"Style","airain.email.onglet.police":"Police","airain.email.onglet.lumiere":"Lumière","airain.email.onglet.pose":"Pose",
 "airain.email.lignes":"Lignes","airain.email.lignes_avant":"Lignes (face avant)","airain.email.lignes_arriere":"Lignes (face arrière)",
 "airain.email.type.0":"Titre","airain.email.type.1":"Section","airain.email.type.2":"Texte","airain.email.type.3":"Valeur","airain.email.type.4":"Barre","airain.email.type.5":"Filet","airain.email.type.6":"Vide","airain.email.type.7":"Colonne →",
 "airain.email.type":"Type","airain.email.taille":"Taille","airain.email.taille.0":"P","airain.email.taille.1":"M","airain.email.taille.2":"G",
 "airain.email.texte":"Texte","airain.email.aligner":"Aligner","airain.email.align.0":"G","airain.email.align.1":"C","airain.email.align.2":"D",
 "airain.email.liaison":"Liaison","airain.email.liaison.aucune":"aucune liaison d'affichage",
 "airain.email.email":"Émail","airain.email.cadre":"Cadre","airain.email.cadre.0":"Riveté","airain.email.cadre.1":"Lisse","airain.email.cadre.2":"Marbre","airain.email.cadre.3":"Aucun",
 "airain.email.airain":"Airain","airain.email.airain.0":"Neuf","airain.email.airain.1":"Terni","airain.email.airain.2":"Vieilli","airain.email.airain.3":"Rouge",
 "airain.email.finition":"Finition et ornements","airain.email.brillant":"Brillant","airain.email.mat":"Mat","airain.email.ecusson":"Écusson","airain.email.rosaces":"Rosaces","airain.email.baguettes":"Baguettes",
 "airain.email.police":"Police","airain.email.police.0":"Minecraft","airain.email.police.1":"Impériale","airain.email.police.2":"Gravée",
 "airain.email.couleurs":"Couleurs","airain.email.couleur_lignes":"Toutes les lignes","airain.email.couleur_valeurs":"Valeurs",
 "airain.email.eclairage":"Éclairage","airain.email.eclairage.0":"Éteint","airain.email.eclairage.1":"Rétroéclairé","airain.email.eclairage.2":"Lettres",
 "airain.email.intensite":"Intensité","airain.email.allumage":"Allumage","airain.email.allumage.0":"Toujours","airain.email.allumage.1":"Signal redstone","airain.email.allumage.2":"En alerte seulement",
 "airain.email.alerte":"Alerte","airain.email.alerte.si":"Si la ligne","airain.email.alerte.depasse":"dépasse","airain.email.alerte.alors":"alors",
 "airain.email.alerte.action.0":"clignote","airain.email.alerte.action.1":"s'allume",
 "airain.email.accrochage":"Accrochage","airain.email.accrochage.0":"Automatique","airain.email.accrochage.1":"Au mur","airain.email.accrochage.2":"Pendu","airain.email.accrochage.3":"Sur pied",
 "airain.email.ici":"Ici : %s","airain.email.montage.0":"au mur","airain.email.montage.1":"pendu","airain.email.montage.2":"sur pied",
 "airain.email.double":"Double face","airain.email.double.meme":"Même contenu","airain.email.double.different":"Différent",
 "airain.email.editer":"Éditer","airain.email.face.avant":"Face avant","airain.email.face.arriere":"Face arrière",
 "airain.email.copier":"Copier","airain.email.copier.aide":"Presse-papiers de Create : clic droit\npour copier les réglages, accroupi\npour les coller sur un autre tableau",
 "airain.ingenieur.tableau_emaille.titre":"Le tableau émaillé","airain.ingenieur.tableau_emaille.court":"Tableau émaillé",
 "airain.ingenieur.tableau_emaille.histoire":"Chaque atelier avait son tableau, chaque quai sa plaque.",
 "airain.ingenieur.tableau_emaille.usage":"@airain:enamel_board Côte à côte : un seul tableau\n- Clic droit main nue : le menu\n- Lignes : titre, texte, valeur, barre\n- Une liaison d'affichage par ligne\n- Émail, cadre, police, lumière\n- Au mur, pendu ou sur pied\n- Presse-papiers : copier les réglages"}
EN={"block.airain.enamel_board":"Enamel Board","airain.display_source.cannon_casting":"Cannon casting",
 "airain.email.ligne":"Line %s","airain.email.apercu":"Preview","airain.email.taille_tableau":"%s × %s blocks",
 "airain.email.onglet.contenu":"Content","airain.email.onglet.style":"Style","airain.email.onglet.police":"Font","airain.email.onglet.lumiere":"Light","airain.email.onglet.pose":"Mount",
 "airain.email.lignes":"Lines","airain.email.lignes_avant":"Lines (front)","airain.email.lignes_arriere":"Lines (back)",
 "airain.email.type.0":"Title","airain.email.type.1":"Section","airain.email.type.2":"Text","airain.email.type.3":"Value","airain.email.type.4":"Bar","airain.email.type.5":"Rule","airain.email.type.6":"Blank","airain.email.type.7":"Column →",
 "airain.email.type":"Type","airain.email.taille":"Size","airain.email.taille.0":"S","airain.email.taille.1":"M","airain.email.taille.2":"L",
 "airain.email.texte":"Text","airain.email.aligner":"Align","airain.email.align.0":"L","airain.email.align.1":"C","airain.email.align.2":"R",
 "airain.email.liaison":"Link","airain.email.liaison.aucune":"no display link",
 "airain.email.email":"Enamel","airain.email.cadre":"Frame","airain.email.cadre.0":"Riveted","airain.email.cadre.1":"Smooth","airain.email.cadre.2":"Marble","airain.email.cadre.3":"None",
 "airain.email.airain":"Airain","airain.email.airain.0":"New","airain.email.airain.1":"Tarnished","airain.email.airain.2":"Aged","airain.email.airain.3":"Red",
 "airain.email.finition":"Finish and ornaments","airain.email.brillant":"Glossy","airain.email.mat":"Matte","airain.email.ecusson":"Crest","airain.email.rosaces":"Rosettes","airain.email.baguettes":"Mouldings",
 "airain.email.police":"Font","airain.email.police.0":"Minecraft","airain.email.police.1":"Imperial","airain.email.police.2":"Engraved",
 "airain.email.couleurs":"Colours","airain.email.couleur_lignes":"All lines","airain.email.couleur_valeurs":"Values",
 "airain.email.eclairage":"Lighting","airain.email.eclairage.0":"Off","airain.email.eclairage.1":"Backlit","airain.email.eclairage.2":"Letters",
 "airain.email.intensite":"Intensity","airain.email.allumage":"Switching","airain.email.allumage.0":"Always","airain.email.allumage.1":"Redstone signal","airain.email.allumage.2":"Only on alert",
 "airain.email.alerte":"Alert","airain.email.alerte.si":"If line","airain.email.alerte.depasse":"exceeds","airain.email.alerte.alors":"then",
 "airain.email.alerte.action.0":"blinks","airain.email.alerte.action.1":"lights up",
 "airain.email.accrochage":"Mounting","airain.email.accrochage.0":"Automatic","airain.email.accrochage.1":"On a wall","airain.email.accrochage.2":"Hanging","airain.email.accrochage.3":"On a post",
 "airain.email.ici":"Here: %s","airain.email.montage.0":"on a wall","airain.email.montage.1":"hanging","airain.email.montage.2":"on a post",
 "airain.email.double":"Two-sided","airain.email.double.meme":"Same content","airain.email.double.different":"Different",
 "airain.email.editer":"Edit","airain.email.face.avant":"Front","airain.email.face.arriere":"Back",
 "airain.email.copier":"Copy","airain.email.copier.aide":"Create clipboard: right-click\nto copy the settings, sneak\nto paste them on another board",
 "airain.ingenieur.tableau_emaille.titre":"The Enamel Board","airain.ingenieur.tableau_emaille.court":"Enamel board",
 "airain.ingenieur.tableau_emaille.histoire":"Every workshop had its board, every platform its sign.",
 "airain.ingenieur.tableau_emaille.usage":"@airain:enamel_board Side by side: one board\n- Bare hand right-click: the menu\n- Lines: title, text, value, bar\n- One display link per line\n- Enamel, frame, font, light\n- On a wall, hanging or on a post\n- Clipboard: copy the settings"}
for f,D in (('fr_fr.json',FR),('en_us.json',EN)):
    pth=AS+'lang/'+f; d=json.load(open(pth)); d.update(D); json.dump(d,open(pth,'w'),ensure_ascii=False,indent=1)
print('affichage ok')
