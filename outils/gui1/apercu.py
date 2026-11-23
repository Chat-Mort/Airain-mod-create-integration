from PIL import Image, ImageDraw, ImageFont
from sprites import *
K='/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/gui/sprites/'
ITEMS=[('hud/crosshair',viseur()),
 ('widget/locked_button',verrou('',False)),('widget/unlocked_button_highlighted',verrou('survol',True)),('widget/locked_button_disabled',verrou('off',False)),
 ('widget/cross_button',croix_bouton('')),('widget/cross_button_highlighted',croix_bouton('survol')),
 ('notification/1',pastille('1')),('notification/3',pastille('3')),('notification/more',pastille('more')),
 ('server_list/ping_5',ping(5)),('server_list/ping_2',ping(2)),('server_list/pinging_3',ping(3,'mesure')),('server_list/unreachable',hors_ligne()),
 ('server_list/join',fleche_liste('droite',False)),('server_list/join_highlighted',fleche_liste('droite',True)),('server_list/move_up',fleche_liste('haut',False)),
 ('advancements/task_frame_obtained',cadre_progres('task',True)),('advancements/goal_frame_obtained',cadre_progres('goal',True)),('advancements/challenge_frame_obtained',cadre_progres('challenge',True)),('advancements/challenge_frame_unobtained',cadre_progres('challenge',False)),
 ('toast/advancement',toast()),
]
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14); B=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
fond=(58,62,72,255)
cases=[]
for nom,hd in ITEMS:
    av=Image.open(K+nom+'.png').convert('RGBA'); av=av.resize((av.width*3,av.height*3),Image.NEAREST)
    z=2 if hd.width<=120 else 1
    a=av.resize((av.width*z,av.height*z),Image.NEAREST); b=hd.resize((hd.width*z,hd.height*z),Image.NEAREST)
    w=a.width+b.width+40; h=max(a.height,b.height)+40
    c=Image.new('RGBA',(w,h),fond); c.alpha_composite(a,(10,10)); c.alpha_composite(b,(a.width+30,10))
    ImageDraw.Draw(c).text((10,h-22),nom.split('/')[1],font=F,fill=(220,220,220))
    cases.append(c)
# rangement en lignes de 1900 px
lignes=[];l=[];lw=0
for c in cases:
    if lw+c.width+12>1900: lignes.append(l); l=[]; lw=0
    l.append(c); lw+=c.width+12
lignes.append(l)
H=60+sum(max(c.height for c in l)+12 for l in lignes)
out=Image.new('RGBA',(1900,H),(28,29,34,255)); d=ImageDraw.Draw(out)
d.text((10,14),"Lot 1 — éléments encore en 1x : avant (à gauche, agrandi) / après en 3x (à droite), affichés comme en jeu en interface 3, puis x2",font=B,fill=(235,235,235))
y=56
for l in lignes:
    x=10
    for c in l: out.alpha_composite(c,(x,y)); x+=c.width+12
    y+=max(c.height for c in l)+12
out.convert('RGB').save('/mnt/user-data/outputs/gui_batch1_mockup.png'); print(out.size)
