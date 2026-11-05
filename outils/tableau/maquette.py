import random, math
from PIL import Image, ImageDraw, ImageFont
S=3
F=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n*S)
FB=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",n*S)
FO=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",n*S)
R=random.Random(4)
# ===================== 1. tableau de service
W,H=276,190
im=Image.new('RGB',(W*S+40,H*S+80),(28,28,32)); d=ImageDraw.Draw(im)
ox,oy=20,50
d.text((ox,10),"Tableau de service : Fort-Rouage",fill=(240,205,120),font=FB(6))
# cadre de laiton
d.rectangle([ox,oy,ox+W*S,oy+H*S],fill=(150,100,36)); d.rectangle([ox+4*S,oy+4*S,ox+(W-4)*S,oy+(H-4)*S],fill=(214,160,48))
d.rectangle([ox+7*S,oy+7*S,ox+(W-7)*S,oy+(H-7)*S],fill=(176,130,82))
for _ in range(2600):   # liège
    x=R.randint(ox+7*S,ox+(W-7)*S); y=R.randint(oy+7*S,oy+(H-7)*S); c=R.choice([(150,104,62),(196,150,98),(166,118,72),(206,166,112)])
    d.rectangle([x,y,x+S,y+S],fill=c)
for (x,y) in ((5,5),(W-9,5),(5,H-9),(W-9,H-9)): d.ellipse([ox+x*S,oy+y*S,ox+(x+4)*S,oy+(y+4)*S],fill=(246,214,134))
notes=[("rouge","Il manque du zinc pour\nla fonderie de laiton.\nJe pars à la mine nord.","Liam · jour 58",False,-3),
       ("jaune","À faire : rallumer\nla Forge impériale\n(16 plaques de cuivre).","Liam · jour 58",False,2),
       ("vert","Train réparé, la ligne\nmine → base tourne.","Max · jour 55",True,-1),
       ("jaune","Le sac de cuivre est\ndans le coffre du\nhangar, prends-le !","Max · jour 57",False,3),
       ("rouge","Assaut prévu : balise\nposée, on la lance\nensemble.","Max · jour 57",False,-2)]
PIN={"rouge":(190,40,36),"jaune":(226,184,40),"vert":(70,150,70)}
for i,(c,t,a,fait,ang) in enumerate(notes):
    nx=ox+(16+(i%3)*84)*S; ny=oy+(18+(i//3)*78)*S
    n=Image.new('RGBA',(76*S,62*S),(0,0,0,0)); nd=ImageDraw.Draw(n)
    nd.rectangle([0,0,76*S,62*S],fill=(238,226,196) if not fait else (214,224,200),outline=(170,150,110))
    nd.multiline_text((5*S,9*S),t,fill=(50,30,16),font=FO(5),spacing=2*S)
    nd.text((5*S,51*S),a,fill=(120,95,70),font=F(4))
    if fait: nd.line([4*S,30*S,72*S,30*S],fill=(70,150,70),width=S)
    n=n.rotate(ang,expand=True,resample=Image.BICUBIC)
    im.paste(n,(nx,ny),n); d.ellipse([nx+34*S,ny+2*S,nx+40*S,ny+8*S],fill=PIN[c],outline=(40,20,10))
# emplacement libre + bouton
nx=ox+(16+2*84)*S; ny=oy+(18+78)*S
d.rectangle([nx,ny,nx+76*S,ny+62*S],outline=(120,84,50),width=S)
d.text((nx+12*S,ny+26*S),"+ Nouvelle note",fill=(90,60,30),font=FB(5))
im.save('/home/claude/apercus/tableau_service.png')

# ===================== 2. atlas impérial
W,H=300,196
im=Image.new('RGB',(W*S+40,H*S+80),(28,28,32)); d=ImageDraw.Draw(im)
d.text((ox,10),"Atlas impérial (livre, rangeable dans la Reliure)",fill=(240,205,120),font=FB(6))
fond=Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/gui/registre.png').convert('RGB').crop((0,0,300,196)).resize((W*S,H*S),Image.NEAREST)
im.paste(fond,(ox,oy))
# carte sur les deux pages : zone (20..280, 16..170)
mx0,my0,mx1,my1=ox+20*S,oy+16*S,ox+280*S,oy+168*S
carte=Image.new('RGB',(mx1-mx0,my1-my0),(228,206,160)); cd=ImageDraw.Draw(carte)
for _ in range(900):
    x=R.randint(0,carte.width-1); y=R.randint(0,carte.height-1); cd.point((x,y),fill=(214,190,142))
for k in range(0,carte.width,16*S): cd.line([k,0,k,carte.height],fill=(206,182,134))
for k in range(0,carte.height,16*S): cd.line([0,k,carte.width,k],fill=(206,182,134))
# rivière et chemins tracés à la main (traces de passage)
pts=[(0,90*S),(60*S,80*S),(120*S,100*S),(200*S,70*S),(260*S,85*S)]
cd.line(pts,fill=(120,150,170),width=2*S)
cd.line([(130*S,74*S),(70*S,40*S),(40*S,30*S)],fill=(170,130,90),width=S)
cd.line([(130*S,74*S),(190*S,120*S),(230*S,130*S)],fill=(170,130,90),width=S)
im.paste(carte,(mx0,my0)); d=ImageDraw.Draw(im)
# reliure au milieu
d.rectangle([ox+146*S,my0,ox+154*S,my1],fill=(110,40,32))
def ic(x,y,kind,label=None):
    X,Y=mx0+x*S,my0+y*S
    if kind=="fondation":
        d.line([X,Y-9*S,X,Y+4*S],fill=(60,40,20),width=S); d.polygon([(X,Y-9*S),(X+7*S,Y-9*S),(X+7*S,Y-2*S),(X+3*S,Y-4*S),(X,Y-2*S)],fill=(150,30,30))
    if kind=="poste":
        d.rectangle([X-4*S,Y-6*S,X+4*S,Y+3*S],fill=(150,100,40),outline=(60,40,20)); d.polygon([(X-5*S,Y-6*S),(X,Y-10*S),(X+5*S,Y-6*S)],fill=(90,140,110))
    if kind=="ruine":
        d.rectangle([X-4*S,Y-3*S,X-1*S,Y+3*S],fill=(120,110,100)); d.rectangle([X+1*S,Y-6*S,X+4*S,Y+3*S],fill=(120,110,100))
    if kind=="camp":
        d.polygon([(X-5*S,Y+3*S),(X,Y-5*S),(X+5*S,Y+3*S)],fill=(110,60,140),outline=(50,20,60))
    if kind=="relais":
        d.line([X-3*S,Y+4*S,X,Y-7*S,X+3*S,Y+4*S],fill=(80,80,90),width=S); d.ellipse([X-2*S,Y-9*S,X+2*S,Y-5*S],fill=(170,120,210))
    if kind=="station":
        d.pieslice([X-5*S,Y-5*S,X+5*S,Y+5*S],180,360,fill=(90,150,120)); d.rectangle([X-5*S,Y,X+5*S,Y+2*S],fill=(150,100,40))
    if kind=="mort":
        d.line([X-3*S,Y-3*S,X+3*S,Y+3*S],fill=(140,20,20),width=2*S); d.line([X-3*S,Y+3*S,X+3*S,Y-3*S],fill=(140,20,20),width=2*S)
    if kind=="joueur":
        d.polygon([(X,Y-6*S),(X+4*S,Y+4*S),(X,Y+2*S),(X-4*S,Y+4*S)],fill=(30,60,120),outline=(240,240,240))
    if label: d.text((X+7*S,Y-4*S),label,fill=(58,26,10),font=F(4))
ic(130,74,"fondation","Fort-Rouage"); ic(232,128,"fondation","Relais du Sud")
ic(42,30,"poste","Avant-poste"); ic(200,40,"poste"); ic(90,120,"ruine"); ic(170,145,"camp"); ic(250,20,"relais")
ic(20,140,"station"); ic(110,30,"mort","jour 31"); ic(136,82,"joueur")
# rose des vents
cx,cy=ox+262*S,oy+148*S
d.polygon([(cx,cy-12*S),(cx+3*S,cy),(cx,cy+12*S),(cx-3*S,cy)],fill=(150,100,40)); d.polygon([(cx-12*S,cy),(cx,cy-3*S),(cx+12*S,cy),(cx,cy+3*S)],fill=(214,160,48))
d.text((cx-2*S,cy-20*S),"N",fill=(58,26,10),font=FB(5))
# barre du bas : filtres et coordonnées
d.text((ox+24*S,oy+172*S),"Filtres :  ⚑ bases   ⌂ avant-postes   ▲ camps   ✕ morts      x 412  z −1180   zoom 1:4",fill=(110,80,52),font=F(5))
im.save('/home/claude/apercus/atlas_imperial.png')
