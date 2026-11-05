from PIL import Image, ImageDraw, ImageFont
T='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/'
V='../mcmeta-assets/assets/minecraft/textures/item/'
S=3
F=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
FB=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",n)
def ic(p): return Image.open(p).convert('RGBA')
LIVRES=[(ic(T+'item/chroniques.png'),"Chroniques oubliées"),(ic(T+'item/registre_fondations.png'),"Registre des fondations"),
        (ic(T+'item/codex.png'),"Codex de l'Empire"),(ic(T+'item/livre_ingenieur.png'),"Livre de l'ingénieur"),
        (ic(V+'book.png'),"Livre de quêtes"),(ic(V+'writable_book.png'),"Carnet d'Ars Nouveau")]
# icône de la reliure : porte-documents de cuir sombre, sangle et coins de laiton
R=[
"................",
"..KKKKKKKKKKKK..",
".KbOccccccccObK.",
".KbKKKKKKKKKKbK.",
".KbrRtTkKuUdbbK.",
".KbrRtTkKuUdbbK.",
".KbrRtTkKuUdbbK.",
"KKKKKKKKKKKKKKKK",
"KoooooKOOKoooooK",
"KKKKKKKOKKKKKKKK",
".KbrRtTkKuUdbbK.",
".KbrrttkkuuddbK.",
".KbKKKKKKKKKKbK.",
".KbOccccccccObK.",
"..KKKKKKKKKKKK..",
"................",
]
P={'.':(0,0,0,0),'K':(30,18,10,255),'b':(70,40,20,255),'c':(110,62,30,255),'o':(214,160,48,255),'O':(246,214,134,255),
   'r':(130,26,22,255),'R':(170,40,32,255),'t':(52,80,76,255),'T':(84,118,106,255),'k':(40,30,28,255),
   'u':(40,70,120,255),'U':(70,110,160,255),'d':(150,120,70,255)}
rel=Image.new('RGBA',(16,16))
for y,row in enumerate(R):
    for x,c in enumerate(row): rel.putpixel((x,y),P[c])
rel.save('reliure.png')
def item(im,dst,x,y,k=S*1):
    dst.paste(im.resize((16*k,16*k),Image.NEAREST),(x,y),im.resize((16*k,16*k),Image.NEAREST))

# --- 1. écran de la Reliure
fond=Image.open(T+'gui/registre.png').convert('RGBA').crop((0,0,300,196)).resize((300*S,196*S),Image.NEAREST)
A=Image.new('RGBA',(300*S+130*S,196*S+40),(32,33,38,255)); A.paste(fond,(110*S,20),fond); d=ImageDraw.Draw(A)
bx=110*S
for i,(im,n) in enumerate(LIVRES+[(None,None)]*2):
    y=20+(14+i*21)*S
    sel=(i==0)
    d.rounded_rectangle([bx-(28 if sel else 24)*S,y,bx+2*S,y+19*S],radius=3*S,fill=(150,30,30,255) if sel else (110,62,30,255),outline=(30,18,10,255),width=S)
    if im: item(im,A,bx-(24 if sel else 20)*S,y+1*S)
d.text((bx+20*S,20+16*S),"Reliure de l'ingénieur",fill=(138,26,20),font=FB(9*S))
for k,l in enumerate(["Huit livres, toujours sous la main.","","Un onglet par livre, à gauche :","un clic l'ouvre ici même.","","Accroupi + clic droit :","ranger ou retirer un livre."]):
    d.text((bx+20*S,20+(34+k*11)*S),l,fill=(58,26,10),font=F(7*S))
d.text((bx+162*S,20+16*S),"Chroniques oubliées",fill=(138,26,20),font=FB(8*S))
for k,l in enumerate(["Le livre s'ouvre comme d'habitude,","toujours à jour : registre, codex","et chroniques lisent le monde","au moment où on les ouvre.","","Échap : retour à la Reliure","(ou au sac)."]):
    d.text((bx+162*S,20+(34+k*11)*S),l,fill=(110,80,52),font=F(7*S))
d.text((10,6),"1. L'écran de la Reliure (clic droit ou touche B)",fill=(240,205,120),font=FB(16))
A.save('/home/claude/apercus/reliure_ecran.png')

# --- 2. le sac avec ses onglets
G=(198,198,198,255); GD=(85,85,85,255); GL=(255,255,255,255)
W,H=176,222
B=Image.new('RGBA',((W+90)*S,(H)*S+40),(32,33,38,255)); d=ImageDraw.Draw(B)
ox,oy=60*S,30
def cadre(x,y,w,h):
    d.rectangle([x,y,x+w,y+h],fill=G,outline=(0,0,0,255),width=S)
def case(x,y): d.rectangle([x,y,x+18*S,y+18*S],fill=(139,139,139,255)); d.line([x,y,x+18*S,y],fill=GD,width=S); d.line([x,y,x,y+18*S],fill=GD,width=S)
cadre(ox,oy,W*S,H*S)
d.text((ox+8*S,oy+5*S),"Sac à dos en fer",fill=(64,64,64),font=F(7*S))
for r in range(6):
    for c in range(9): case(ox+(7+c*18)*S,oy+(16+r*18)*S)
d.text((ox+8*S,oy+128*S),"Inventaire",fill=(64,64,64),font=F(7*S))
for r in range(3):
    for c in range(9): case(ox+(7+c*18)*S,oy+(138+r*18)*S)
for c in range(9): case(ox+(7+c*18)*S,oy+(196+0)*S)
# colonne des améliorations
ux=ox-26*S
cadre(ux,oy+4*S,26*S,4*18*S+8*S)
for k in range(4): case(ux+4*S,oy+(8+k*18)*S)
item(ic(V+'hopper.png') if False else rel,B,ux+5*S,oy+9*S)   # la reliure rangée dans le sac (exemple)
# onglets des livres sous les améliorations
ty=oy+(4*18+18)*S
d.text((ux-34*S,ty-12*S),"Livres",fill=(240,205,120),font=FB(6*S))
for i,(im,n) in enumerate(LIVRES):
    y=ty+i*20*S; hov=(i==1)
    d.rounded_rectangle([ux-2*S,y,ux+24*S,y+19*S],radius=3*S,fill=(255,236,190,255) if hov else (210,190,150,255),outline=(0,0,0,255),width=S)
    item(im,B,ux+3*S,y+1*S)
# info-bulle
tx,tyy=ux+28*S,ty+20*S
d.rectangle([tx,tyy,tx+92*S,tyy+24*S],fill=(16,0,16,240),outline=(80,0,255,255),width=S)
d.text((tx+4*S,tyy+3*S),"Registre des fondations",fill=(255,255,255),font=F(6*S)); d.text((tx+4*S,tyy+13*S),"Clic : lire",fill=(170,170,170),font=F(6*S))
item(rel,B,ox+(7+3*18+1)*S,oy+(16+1)*S)
d.text((10,6),"2. Le sac : la Reliure est rangée dedans, ses livres apparaissent à gauche",fill=(240,205,120),font=FB(16))
B.save('/home/claude/apercus/reliure_sac.png')
o=Image.new('RGBA',(40,20),(60,60,66,255)); o.paste(rel,(2,2),rel); b=ic(T+'item/chroniques.png'); o.paste(b,(22,2),b); o.resize((640,320),Image.NEAREST).save('/home/claude/apercus/reliure_icone.png')
