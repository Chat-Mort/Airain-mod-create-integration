# Maquette du menu du tableau émaillé : cinq onglets (Contenu, Style, Police, Lumière, Pose) et l'aperçu en direct.
from PIL import Image, ImageDraw, ImageFont
exec(open('livre_maquette.py').read().split('def couper')[0])
G='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/gui/'
FOND=Image.open(G+'standard.png').convert('RGBA').crop((0,0,310,226))
ENCRE=(58,26,10); SEPIA=(110,80,52); ROUGE=(138,26,20); VERT=(40,100,40); CLAIR=(250,236,200)
LAITON=dict(l=(250,226,160),m=(214,170,90),d=(150,104,48),s=(96,62,30))
DYES=[(249,255,254),(157,157,151),(71,79,82),(29,29,33),(176,46,38),(249,128,29),(254,216,61),(128,199,31),(94,124,22),(22,156,156),(58,179,218),(60,68,170),(137,50,184),(199,78,189),(243,139,170),(131,84,50)]
def t(d,im,s,x,y,col=ENCRE,gras=False): return ecrire(im,s,x,y,col,gras)
def bouton(d,im,x,y,w,h,txt,actif=False,petit=False):
    c=LAITON
    d.rectangle([x,y,x+w-1,y+h-1],fill=c['s'])
    d.rectangle([x,y,x+w-2,y+h-2],fill=c['d'] if actif else c['l'])
    d.rectangle([x+1,y+1,x+w-2,y+h-2],fill=(c['d'] if actif else c['m']))
    if actif: d.rectangle([x+1,y+1,x+w-2,y+1],fill=c['s'])
    if txt: ecrire(im,txt,x+(w-largeur(txt))//2,y+(h-8)//2+(1 if actif else 0),CLAIR if actif else ENCRE)
def case(d,im,x,y,coche,txt):
    d.rectangle([x,y,x+8,y+8],fill=LAITON['s']); d.rectangle([x+1,y+1,x+7,y+7],fill=LAITON['l'])
    if coche: d.line([x+2,y+4,x+3,y+6],fill=ROUGE,width=2); d.line([x+3,y+6,x+7,y+1],fill=ROUGE,width=2)
    ecrire(im,txt,x+12,y,ENCRE)
def radio(d,im,x,y,on,txt):
    d.ellipse([x,y,x+8,y+8],fill=LAITON['s']); d.ellipse([x+1,y+1,x+7,y+7],fill=LAITON['l'])
    if on: d.ellipse([x+2,y+2,x+6,y+6],fill=ROUGE)
    ecrire(im,txt,x+12,y,ENCRE)
def champ(d,im,x,y,w,txt,curseur=False):
    d.rectangle([x,y,x+w-1,y+11],fill=LAITON['s']); d.rectangle([x+1,y+1,x+w-1,y+11],fill=(40,28,18))
    ecrire(im,txt,x+3,y+2,CLAIR)
    if curseur: d.rectangle([x+4+largeur(txt),y+2,x+4+largeur(txt),y+9],fill=CLAIR)
def pastille(d,x,y,c,sel=False,tl=9):
    d.rectangle([x,y,x+tl,y+tl],fill=LAITON['s']); d.rectangle([x+1,y+1,x+tl-1,y+tl-1],fill=c)
    if sel: d.rectangle([x-2,y-2,x+tl+2,y+tl+2],outline=ROUGE,width=1)
def titre_section(d,im,s,x,y): ecrire(im,s,x,y,ROUGE,True); d.line([x,y+10,x+200,y+10],fill=LAITON['d'])
# aperçu : la texture de la salle de contrôle, encadrée, réduite dans le panneau sombre
APER=Image.open('tex/salle.png').convert('RGBA')
def apercu(im,d,email=None,lumineux=False):
    x0,y0,x1,y1=225,19,299,161
    ecrire(im,'Aperçu',x0+18,y0+2,LAITON['l'])
    a=APER.copy()
    if email:
        px=a.load()
        for yy in range(a.height):
            for xx in range(a.width):
                if px[xx,yy][:3]==(26,26,32): px[xx,yy]=email+(255,)
    w=70; h=int(a.height*w/a.width); a=a.resize((w,h),Image.LANCZOS)
    fx,fy=x0+2,y0+40
    d.rectangle([fx-3,fy-3,fx+w+2,fy+h+2],fill=LAITON['m']); d.rectangle([fx-3,fy-3,fx+w+2,fy-3],fill=LAITON['l']); d.rectangle([fx+w+2,fy-3,fx+w+2,fy+h+2],fill=LAITON['s'])
    if lumineux:
        g=Image.new('RGBA',im.size,(0,0,0,0)); dg=ImageDraw.Draw(g); dg.rectangle([fx-8,fy-8,fx+w+8,fy+h+8],fill=(255,200,120,60)); im.alpha_composite(g)
    im.alpha_composite(a,(fx,fy))
    ecrire(im,'6 × 3 blocs',x0+10,fy+h+12,LAITON['l'])
ONGLETS=['Contenu','Style','Police','Lumière','Pose']
def ecran(onglet,contenu):
    im=FOND.copy(); d=ImageDraw.Draw(im)
    ecrire(im,'Tableau émaillé',14,6,ENCRE,True)
    x=10
    for o in ONGLETS:
        w=largeur(o)+12; bouton(d,im,x,22,w,14,o,o==onglet); x+=w+3
    contenu(im,d)
    bouton(d,im,226,196,74,16,'Terminé')
    return im
# --------------------------------------------------------------- 1. Contenu
def contenu(im,d):
    titre_section(d,im,'Lignes (face avant)',12,42)
    L=[('Titre','SALLE DE CONTRÔLE',None),('Section','PRODUCTION',None),('Valeur',"Lingots d'airain",'liaison 1'),('Barre','Haut-fourneau','liaison 2'),
       ('Filet','',None),('Valeur','Stress','liaison 3'),('Texte','Train pour Port-Impérial',None)]
    y=54
    for i,(ty,tx,src) in enumerate(L):
        sel=i==5
        if sel: d.rectangle([11,y-2,214,y+9],fill=(232,196,120))
        ecrire(im,ty,14,y,SEPIA if not sel else ENCRE); ecrire(im,tx[:20],66,y,ENCRE,sel)
        if src: ecrire(im,'●',200,y,VERT)
        y+=11
    bouton(d,im,12,y+1,14,12,'+'); bouton(d,im,28,y+1,14,12,'−'); bouton(d,im,44,y+1,14,12,'↑'); bouton(d,im,60,y+1,14,12,'↓')
    y+=16; titre_section(d,im,'Ligne 6',12,y); y+=13
    ecrire(im,'Type',14,y+2,ENCRE); bouton(d,im,52,y,12,12,'◀'); ecrire(im,'Valeur',70,y+2,ENCRE,True); bouton(d,im,114,y,12,12,'▶')
    ecrire(im,'Taille',132,y+2,ENCRE); [bouton(d,im,162+i*16,y,14,12,s,s=='M') for i,s in enumerate('PMG')]; y+=14
    ecrire(im,'Texte',14,y+2,ENCRE); champ(d,im,52,y,162,'Stress',True); y+=14
    ecrire(im,'Aligner',14,y+2,ENCRE); [bouton(d,im,52+i*16,y,14,12,s,s=='G') for i,s in enumerate('GCD')]
    ecrire(im,'Couleur',110,y+2,ENCRE)
    for i,c in enumerate([(236,228,206),(232,196,110),(214,64,48),(120,200,120)]): pastille(d,152+i*13,y+1,c,i==0)
    y+=14
    ecrire(im,'Source',14,y+1,ENCRE); ecrire(im,'Liaison 3 · stressomètre',52,y+1,VERT)
apercu_args={}
# --------------------------------------------------------------- 2. Style
def style(im,d):
    titre_section(d,im,'Émail',12,42)
    for i,c in enumerate(DYES): pastille(d,14+(i%8)*14,56+(i//8)*14,c,i==11)
    ecrire(im,'Bleu',134,62,ENCRE,True)
    titre_section(d,im,'Cadre',12,90)
    for i,s in enumerate(['Riveté','Lisse','Marbre','Aucun']): bouton(d,im,12+i*50,104,48,14,s,i==0)
    titre_section(d,im,'Airain',12,126)
    for i,(c,s) in enumerate([((214,170,90),'Neuf'),((190,130,80),'Terni'),((168,88,60),'Vieilli'),((150,30,26),'Rouge')]):
        pastille(d,14+i*50,140,c,i==0); ecrire(im,s,26+i*50,141,ENCRE)
    titre_section(d,im,'Finition et ornements',12,158)
    radio(d,im,14,172,True,'Brillant'); radio(d,im,74,172,False,'Mat')
    case(d,im,14,186,True,'Écusson'); case(d,im,74,186,True,'Rosaces'); case(d,im,134,186,True,'Baguettes')
# --------------------------------------------------------------- 3. Police
def police(im,d):
    titre_section(d,im,'Police',12,42)
    fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',10)
    for i,(nom,sel) in enumerate((('Minecraft',False),('Impériale',True),('Gravée',False))):
        y=56+i*28
        radio(d,im,14,y,sel,nom)
        d.rectangle([90,y-4,214,y+14],fill=(26,26,32))
        if nom=='Minecraft': ecrire(im,'Lingots 1 284',96,y+1,(236,228,206))
        elif nom=='Impériale':
            tmp=Image.new('L',(140,16),0); ImageDraw.Draw(tmp).text((0,0),'Lingots 1 284',font=fs,fill=255)
            tmp=tmp.point(lambda v: 255 if v>110 else 0); im.paste((236,228,206),(96,y-1),tmp)
        else:
            ecrire(im,'Lingots 1 284',96,y+2,(120,120,135)); ecrire(im,'Lingots 1 284',96,y+1,(8,8,10))
    titre_section(d,im,'Couleurs',12,142)
    ecrire(im,'Texte',14,158,ENCRE)
    for i,c in enumerate([(236,228,206),(232,196,110),(214,64,48),(120,200,120),(140,190,240)]): pastille(d,60+i*13,157,c,i==0)
    ecrire(im,'Valeurs',14,176,ENCRE)
    for i,c in enumerate([(236,228,206),(232,196,110),(214,64,48),(120,200,120),(140,190,240)]): pastille(d,60+i*13,175,c,i==1)
# --------------------------------------------------------------- 4. Lumière
def lumiere(im,d):
    titre_section(d,im,'Éclairage',12,42)
    radio(d,im,14,56,False,'Éteint'); radio(d,im,66,56,True,'Rétroéclairé'); radio(d,im,150,56,False,'Lettres')
    ecrire(im,'Intensité',14,76,ENCRE)
    d.rectangle([70,79,200,81],fill=LAITON['s']); d.rectangle([70,79,70+int(130*11/15),81],fill=LAITON['l'])
    k=70+int(130*11/15); d.rectangle([k-3,74,k+3,86],fill=LAITON['d']); d.rectangle([k-2,75,k+2,85],fill=LAITON['l']); ecrire(im,'11',204,76,ENCRE,True)
    titre_section(d,im,'Allumage',12,98)
    radio(d,im,14,112,False,'Toujours'); radio(d,im,84,112,False,'Signal redstone'); radio(d,im,14,126,True,'Alerte')
    titre_section(d,im,'Alerte',12,146)
    ecrire(im,'Si la ligne',14,162,ENCRE); champ(d,im,64,160,18,'5'); ecrire(im,'dépasse',88,162,ENCRE); champ(d,im,128,160,26,'90'); ecrire(im,'%',158,162,ENCRE)
    ecrire(im,'alors',14,180,ENCRE); bouton(d,im,42,177,60,14,'clignote',True); bouton(d,im,106,177,50,14,'s\'allume')
    pastille(d,166,179,(214,64,48),True)
# --------------------------------------------------------------- 5. Pose
def pose(im,d):
    titre_section(d,im,'Accrochage',12,42)
    for i,(s,on) in enumerate((('Automatique',True),('Au mur',False),('Pendu',False),('Sur pied',False))): radio(d,im,14+(i%2)*100,56+(i//2)*14,on,s)
    ecrire(im,'Ici : pendu sous une poutrelle',14,88,VERT)
    titre_section(d,im,'Double face',12,106)
    radio(d,im,14,120,True,'Même contenu'); radio(d,im,114,120,False,'Différent')
    ecrire(im,'Éditer',14,138,ENCRE); bouton(d,im,48,135,64,14,'Face avant',True); bouton(d,im,116,135,70,14,'Face arrière')
    titre_section(d,im,'Copier',12,158)
    ecrire(im,'Presse-papiers de Create :',14,172,SEPIA); ecrire(im,'clic droit pour copier, accroupi',14,182,SEPIA); ecrire(im,'pour coller sur un autre tableau',14,192,SEPIA)
E=[]
for o,f,kw in (('Contenu',contenu,{}),('Style',style,{'email':(30,62,120)}),('Police',police,{}),('Lumière',lumiere,{'lumineux':True}),('Pose',pose,{})):
    im=ecran(o,f); d=ImageDraw.Draw(im); apercu(im,d,**kw); E.append(im.resize((im.width*2,im.height*2),Image.NEAREST))
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22)
w,h=E[0].size
out=Image.new('RGBA',(3*w+80,2*h+120),(34,30,38,255)); dd=ImageDraw.Draw(out)
for i,im in enumerate(E):
    x=20+(i%3)*(w+20); y=50+(i//3)*(h+50)
    dd.text((x,y-34),f"{i+1}. {ONGLETS[i]}",font=fo,fill=(235,215,170)); out.alpha_composite(im,(x,y))
out.save('menu_tableau.png'); print(out.size)
