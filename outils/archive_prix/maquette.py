# Maquette : prix sur les boutons de lot de l'Archive résonante (équivalent réfractaire des volets de gare de l'Empire).
from PIL import Image, ImageDraw, ImageFont, ImageFilter
G='/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/airain/textures/gui/'
E=Image.open(G+'difference_engine.png').convert('RGBA'); A=Image.open(G+'resonant_archive.png').convert('RGBA')
S=3
def piece(im,u,v,w,h): return im.crop((u*S,v*S,(u+w)*S,(v+h)*S))
def hx(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))
# masques des chiffres, tirés des volets de l'Empire (même dessin, autre matière)
MASQ=[]
for k in range(10):
    c=piece(E,398+8*k,20,8,10); p=c.load(); m=Image.new('L',c.size,0); q=m.load()
    for y in range(c.height):
        for x in range(c.width):
            r,g,b,a=p[x,y]
            if a>0 and r>190 and g>180 and b>150 and r-b<70: q[x,y]=255
    MASQ.append(m)
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
# --- A : cellules de verre violet, chiffres lumineux (lueur de résonance)
def cellule_A(k):
    w,h=8*S,10*S; im=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(im)
    for y in range(h): d.line([(0,y),(w-1,y)],fill=mix(hx('2a1d40'),hx('130c20'),y/h)+(255,))
    d.rectangle([0,0,w-1,h-1],outline=hx('0c0814')+(255,))
    d.line([(1,1),(w-2,1)],fill=hx('4a3a68')+(255,))            # reflet du verre en haut
    if k is None:   # cristal à la place de la pièce
        cx=w//2; pts=[(cx,3),(cx+7,h//2-1),(cx,h-4),(cx-7,h//2-1)]
        d.polygon(pts,fill=hx('9b6ae0')+(255,)); d.polygon([(cx,3),(cx+7,h//2-1),(cx,h//2-1)],fill=hx('c9a8ff')+(255,))
        d.polygon([(cx,h//2-1),(cx-7,h//2-1),(cx,h-4)],fill=hx('6a3fb0')+(255,)); d.line([(cx,4),(cx,h-5)],fill=hx('e8dcff')+(255,))
        return im
    m=MASQ[k]; halo=m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    im.alpha_composite(Image.composite(Image.new('RGBA',(w,h),hx('8f5ee0')+(255,)),Image.new('RGBA',(w,h),(0,0,0,0)),halo.point(lambda v:int(v*.75))))
    im.alpha_composite(Image.composite(Image.new('RGBA',(w,h),hx('efe6ff')+(255,)),Image.new('RGBA',(w,h),(0,0,0,0)),m))
    return im
# --- B : plaque d'argent continue, chiffres gravés (creux violet, arête claire en bas)
def plaque_B(t):
    w,h=(8+8*len(t))*S,10*S; im=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(im)
    for y in range(h): d.line([(0,y),(w-1,y)],fill=mix(hx('d8d4e6'),hx('a9a3bd'),y/h)+(255,))
    d.rectangle([0,0,w-1,h-1],outline=hx('5a5470')+(255,)); d.line([(1,1),(w-2,1)],fill=hx('f2f0f8')+(255,))
    # cristal serti à gauche
    cx=4*S; d.polygon([(cx,4),(cx+6,h//2),(cx,h-5),(cx-6,h//2)],fill=hx('8a55d8')+(255,)); d.polygon([(cx,4),(cx+6,h//2),(cx,h//2)],fill=hx('c9a8ff')+(255,))
    for i,ch in enumerate(t):
        m=MASQ[int(ch)]; ox=(8+8*i)*S
        bas=Image.new('RGBA',m.size,hx('fbfaff')+(255,)); creux=Image.new('RGBA',m.size,hx('3b2458')+(255,))
        im.alpha_composite(Image.composite(bas,Image.new('RGBA',m.size,(0,0,0,0)),m),(ox,1))   # arête claire décalée
        im.alpha_composite(Image.composite(creux,Image.new('RGBA',m.size,(0,0,0,0)),m),(ox,0))
    return im
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
def lot(im_src,etat_v,q,prix,mode):
    b=piece(im_src,330,etat_v,52,30).copy(); d=ImageDraw.Draw(b)
    t='x'+str(q); tw=d.textlength(t,font=F); d.text((26*S-tw/2+2,4*S+2),t,font=F,fill=(40,30,50)); d.text((26*S-tw/2,4*S),t,font=F,fill=(255,255,255))
    s='%04d'%prix
    if mode=='empire':
        x=(26-20)*S; b.alpha_composite(piece(im_src,390,20,8,10),(x,15*S))
        for k,ch in enumerate(s): b.alpha_composite(piece(im_src,398+8*int(ch),20,8,10),(x+(8+8*k)*S,15*S))
    elif mode=='actuel':
        p=str(prix); fw=d.textlength(p,font=F); w=7*S+2*S+fw; x=int(26*S-w/2)
        b.alpha_composite(piece(im_src,390,32,7,7),(x,17*S)); d.text((x+9*S,17*S-4),p,font=F,fill=hx('ece4ff'))
    elif mode=='A':
        x=(26-20)*S; b.alpha_composite(cellule_A(None),(x,15*S))
        for k,ch in enumerate(s): b.alpha_composite(cellule_A(int(ch)),(x+(8+8*k)*S,15*S))
    elif mode=='B':
        pl=plaque_B(s); b.alpha_composite(pl,((26-20)*S,15*S))
    return b
PRIX=[3,90,176]
T=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
out=Image.new('RGBA',(4*560+60,330),(24,22,30,255)); d=ImageDraw.Draw(out)
for c,(titre,src,mode) in enumerate((("Empire (aujourd'hui)",E,'empire'),("Archive (aujourd'hui)",A,'actuel'),("Archive : proposition A",A,'A'),("Archive : proposition B",A,'B'))):
    ox=20+c*560
    d.text((ox,10),titre,font=T,fill=(235,235,235))
    fond=piece(src,0,150,180,72).copy(); out.alpha_composite(fond,(ox,60))
    for i in range(3): out.alpha_composite(lot(src,20,[1,32,64][i],PRIX[i],mode),(ox+(8+i*56)*S,60+(30)*S))
out.convert('RGB').save('/mnt/user-data/outputs/archive_price_mockup.png')
