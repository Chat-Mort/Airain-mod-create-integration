import re,sys,math
sys.path.insert(0,'../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
NT=Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/models/armor/casque_couronne_layer_1.png').convert('RGBA').crop((64,0,128,32))
src=open('/home/claude/airain-mod-create-integration/src/main/java/fr/chatmort/airain/gardien/CouronneGeo.java').read()
F=[tuple(float(v.rstrip('f')) for v in m.split(',')) for m in re.findall(r'\{([-\d.f, ]+)\},',src.split('CASQUE = {')[1].split('ROUAGE')[0])]
Rg=[tuple(int(v) for v in m.split(',')) for m in re.findall(r'\{([-\d, ]+)\},',src.split('ROUAGE = {')[1])]
COL=[(74,66,68),(40,34,36),(106,96,106),(84,78,84),(30,24,24),(190,30,35),(58,150,130),(150,205,220),(184,104,70),(56,48,50)]
fl=math.floor
def apercu(S, DY, GX, sortie):
    V={}
    def put(x,y,z,c): V[(fl(-z*2),fl(-y*2),fl(x*2))]=c
    # casque : boîte [-5,5]x[-9,1]x[-5,5], texture de tête netherite (UV vanilla)
    N=20
    for i in range(N):
        for j in range(N):
            a=(i+.5)/N; b=(j+.5)/N
            faces={ # (point 3D, (u,v) texture)
              'avant':((-5+10*a, -9+10*b, -5), (8+8*(1-a), 8+8*b)),
              'arriere':((-5+10*a, -9+10*b, 5), (24+8*a, 8+8*b)),
              'droite':((-5, -9+10*b, -5+10*a), (0+8*a, 8+8*b)),
              'gauche':((5, -9+10*b, -5+10*a), (16+8*(1-a), 8+8*b)),
              'dessus':((-5+10*a, -9, -5+10*b), (8+8*(1-a), 0+8*b))}
            for f,((x,y,z),(u,v)) in faces.items():
                c=NT.getpixel((min(63,int(u)),min(31,int(v))))
                if c[3]: put(x+(0.25 if f!='gauche' else -0.25),y+(0.25 if f!='dessus' else 0.25),z+(0.25 if f!='arriere' else -0.25),c[:3])
    for X in range(-8,8):
        for Y in range(-16,0):
            for Z in range(-8,8):
                if X in(-8,7) or Y in(-16,-1) or Z in(-8,7): put(X/2+0.25,Y/2+0.25,Z/2+0.25,(150,120,100) if Y>-13 else (70,50,35))
    for (x,y,z,w,h,d,m) in F:
        for i in range(int(w*2)):
            for j in range(int(h*2)):
                for k in range(int(d*2)):
                    px,py,pz=x+i/2+0.25,y+j/2+0.25+DY,z+k/2+0.25
                    put(px*S,py,pz*S,COL[int(m)])
    for s in (-1,1):
        for (y,z,m) in Rg:
            for i in range(2):
                for j in range(2):
                    for k in range(2): put(s*GX-0.5+i/2+0.25, -3.5+y-0.5+j/2+0.25, (-1+z-0.5+k/2+0.25), COL[m])
    iso=rendu(V,T=6)
    def plan(axe):   # vue de face (axe 0 : +rx) ou de profil (axe 2 : +rz)
        best={}
        for (a,b,c),col in V.items():
            k=(c if axe==0 else a, b); d=a if axe==0 else c
            if k not in best or d>best[k][0]: best[k]=(d,col)
        xs=[k[0] for k in best]; ys=[k[1] for k in best]
        im=Image.new('RGB',((max(xs)-min(xs)+3)*8,(max(ys)-min(ys)+3)*8),(32,33,38)); dr=ImageDraw.Draw(im)
        for (u,v),(d,col) in best.items():
            f=1.0 if axe==0 else 0.85
            X=(u-min(xs)+1)*8; Y=(max(ys)-v+1)*8
            dr.rectangle([X,Y,X+7,Y+7],fill=tuple(int(q*f) for q in col[:3]))
        return im
    a,b,c=iso,plan(0),plan(2)
    out=Image.new('RGB',(a.width+b.width+c.width+40,max(a.height,b.height,c.height)),(32,33,38))
    out.paste(a,(0,0)); out.paste(b,(a.width+20,20)); out.paste(c,(a.width+b.width+40,20))
    return out
im=apercu(1.0,0.0,7.0,None)
out=Image.new("RGB",(im.width+20,im.height+60),(24,25,29)); out.paste(im,(10,10))
ImageDraw.Draw(out).text((10,im.height+20),"Casque couronné : la couronne prend la couleur de la netherite",fill=(240,205,120),font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",16))
out.save('/home/claude/apercus/casque_couronne_v2.png')
