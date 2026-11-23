# Maquette 2 : prix de l'Archive résonante, à l'opposé de l'Empire (pas de cellules, pas de chiffres alignés).
#  A : « encre d'Écho » — le prix écrit à la main, en encre lumineuse qui ondule ;
#  B : « sceau de l'Écho » — le prix en un seul signe (numération cistercienne : un trait, jusqu'à 9 999), valeur au survol.
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
G='/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/airain/textures/gui/'
E=Image.open(G+'difference_engine.png').convert('RGBA'); A=Image.open(G+'resonant_archive.png').convert('RGBA')
S=3
def piece(im,u,v,w,h): return im.crop((u*S,v*S,(u+w)*S,(v+h)*S))
def hx(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
def lueur(masque, coeur, halo, force=.8, rayon=1.6):
    w,h=masque.size; im=Image.new('RGBA',(w,h))
    g=masque.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(rayon)).point(lambda v:int(min(255,v*force)))
    im.alpha_composite(Image.composite(Image.new('RGBA',(w,h),halo),Image.new('RGBA',(w,h)),g))
    im.alpha_composite(Image.composite(Image.new('RGBA',(w,h),coeur),Image.new('RGBA',(w,h)),masque))
    return im
# ---------------- A : encre d'Écho
POL=ImageFont.truetype('polices/uncial-antiqua-latin-400-normal.woff2',30)
def encre(prix, w=52*S, h=12*S, graine=0):
    r=random.Random(graine+prix); m=Image.new('L',(w,h)); t=str(prix)
    larg=sum(POL.getlength(c) for c in t)+2*(len(t)-1); x=(w-larg)/2+6
    for c in t:
        g=Image.new('L',(40,48)); ImageDraw.Draw(g).text((6,2),c,font=POL,fill=255)
        g=g.rotate(r.uniform(-9,9),resample=Image.BICUBIC).point(lambda v:255 if v>110 else 0)
        m.paste(g,(int(x)-6,int(-10+r.uniform(-2,2))),g); x+=POL.getlength(c)+2
    # petite rune « pièce » à gauche : un losange ouvert
    out=lueur(m,hx('f3ecff'),hx('9a5cf0'))
    return out
# ---------------- B : sceau cistercien
def sceau(prix, H=27, Wq=8, ep=2):
    """Un seul signe : hampe verticale ; unités en haut à droite, dizaines en haut à gauche, centaines en bas à droite, milliers en bas à gauche."""
    cw=2*Wq+ep+6; m=Image.new('L',(cw,H+4)); d=ImageDraw.Draw(m); cx=cw//2; y0=2; y1=y0+H
    d.rectangle([cx-ep//2,y0,cx-ep//2+ep-1,y1],fill=255)
    q=H//3
    def trait(a,b): d.line([a,b],fill=255,width=ep)
    def chiffre(n, sx, sy):
        if n==0: return
        X=lambda u: cx+sx*u; Y=lambda v: (y0+v) if sy>0 else (y1-v)
        segs=[]
        if n in (1,5,7,9): segs.append(((0,0),(Wq,0)))
        if n in (2,8,9): segs.append(((0,q),(Wq,q)))
        if n==3: segs.append(((0,0),(Wq,q)))
        if n in (4,5): segs.append(((0,q),(Wq,0)))
        if n in (6,7,8,9): segs.append(((Wq,0),(Wq,q)))
        for (a,b) in segs: trait((X(a[0]),Y(a[1])),(X(b[0]),Y(b[1])))
    s='%04d'%prix
    chiffre(int(s[3]),1,1); chiffre(int(s[2]),-1,1); chiffre(int(s[1]),1,-1); chiffre(int(s[0]),-1,-1)
    return lueur(m,hx('e6fbff'),hx('3fb8e0'),force=.9,rayon=1.8)
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
def sans_fenetre(b):
    # bouton sans la fenêtre sombre du prix : rien d'encadré, le prix flotte sur la plaque
    b=b.copy(); p=b.load()
    for y in range(40,82):
        for x in range(6,150):
            if 9<=x<=146 and 44<=y<=80: p[x,y]=(30,20,40,255)
    return b
def lot(src,q,prix,mode):
    b=piece(src,330,20,52,30).copy(); d=ImageDraw.Draw(b)
    t='x'+str(q); tw=d.textlength(t,font=F); d.text((26*S-tw/2+2,4*S+2),t,font=F,fill=(40,30,50)); d.text((26*S-tw/2,4*S),t,font=F,fill=(255,255,255))
    if mode=='empire':
        s='%04d'%prix; x=(26-20)*S; b.alpha_composite(piece(src,390,20,8,10),(x,15*S))
        for k,ch in enumerate(s): b.alpha_composite(piece(src,398+8*int(ch),20,8,10),(x+(8+8*k)*S,15*S))
    elif mode=='A':
        # on efface la fenêtre sombre du bouton : l'encre flotte sur la plaque
        b=sans_fenetre(piece(src,330,20,52,30))
        d=ImageDraw.Draw(b); d.text((26*S-tw/2+2,4*S+2),t,font=F,fill=(40,30,50)); d.text((26*S-tw/2,4*S),t,font=F,fill=(255,255,255))
        b.alpha_composite(encre(prix),(0,14*S))
    elif mode=='B':
        b=sans_fenetre(piece(src,330,20,52,30))
        # le signe prend la place du « x32 » ? non : quantité à gauche, sceau à droite
        d=ImageDraw.Draw(b); d.text((8*S,9*S),t,font=F,fill=(255,255,255))
        sg=sceau(prix); b.alpha_composite(sg,(52*S-sg.width-8*S,(30*S-sg.height)//2))
    return b
PRIX=[3,90,176]
T=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
pan=[]
for titre,src,mode in (("Empire (volets de gare)",E,'empire'),("A : encre d'Écho",A,'A'),("B : sceau de l'Écho",A,'B')):
    c=Image.new('RGBA',(540,330),(24,22,30,255)); d=ImageDraw.Draw(c); d.text((0,10),titre,font=T,fill=(235,235,235))
    c.alpha_composite(piece(src,0,150,180,72),(0,60))
    for i in range(3): c.alpha_composite(lot(src,[1,32,64][i],PRIX[i],mode),((8+i*56)*S,60+30*S))
    pan.append(c)
# grand format des sceaux, avec la lecture
leg=Image.new('RGBA',(540,330),(24,22,30,255)); d=ImageDraw.Draw(leg); d.text((0,10),"B : lire un sceau",font=T,fill=(235,235,235))
for i,p in enumerate((3,90,176,8192)):
    s=sceau(p); leg.alpha_composite(s.resize((s.width*3,s.height*3),Image.NEAREST),(20+i*130,70))
    d.text((20+i*130,190),str(p),font=T,fill=(200,200,220))
F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
d.text((0,240),"haut-droite : unités   haut-gauche : dizaines",font=F2,fill=(170,170,190))
d.text((0,264),"bas-droite : centaines   bas-gauche : milliers",font=F2,fill=(170,170,190))
d.text((0,288),"au survol du bouton : la valeur en pièces",font=F2,fill=(170,170,190))
pan.append(leg)
out=Image.new('RGB',(2*540*2+40,2*330*2),(24,22,30))
for i,p in enumerate(pan): out.paste(p.resize((1080,660),Image.NEAREST),((i%2)*(1080+40),(i//2)*660))
out.save('/mnt/user-data/outputs/archive_price_mockup.png')
