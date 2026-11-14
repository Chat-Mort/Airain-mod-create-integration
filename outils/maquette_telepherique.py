# Maquette du téléphérique impérial : gare motrice, pylône, câble, nacelle à plateforme ouverte, gare d'arrivée ; laminoir.
src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
import math
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'; rm._cache.clear()
M='t:block/airain_block'; BD='t:block/airain_band'; RG='t:block/oxidized_airain_block'; PN='t:block/airain_panel'
RO='t:block/airain_rod'; G='t:block/airain_catwalk'; RI='t:block/riveted_airain'
def b(f,t,tex=M,faces=("north","south","east","west","up","down")):
    """Boîte en pixels absolus (16 px = 1 bloc), uv positionnelles ramenées dans le bloc."""
    fc={}
    for k in faces:
        x0,y0,z0=f; x1,y1,z1=t
        dims={'north':(x1-x0,y1-y0),'south':(x1-x0,y1-y0),'east':(z1-z0,y1-y0),'west':(z1-z0,y1-y0),'up':(x1-x0,z1-z0),'down':(x1-x0,z1-z0)}[k]
        a,h=min(16,dims[0]),min(16,dims[1]); u=(16-a)/2; v=(16-h)/2
        fc[k]={'texture':tex,'uv':[u,v,u+a,v+h]}
    return {'from':list(f),'to':list(t),'faces':fc}
def gare(ox,oz,motrice=True):
    """Gare : socle riveté, fût, grande poulie horizontale (le câble s'enroule dessus), et la boîte du moteur de Create."""
    X,Z=ox*16,oz*16; E=[]
    E+=[b((X+0,0,Z+0),(X+16,6,Z+16),RI),b((X+1,6,Z+1),(X+15,8,Z+15),BD)]
    E+=[b((X+5,8,Z+5),(X+11,22,Z+11),M)]                      # fût
    E+=[b((X+1,22,Z+1),(X+15,24,Z+15),RG)]                    # poulie (jante)
    E+=[b((X+3,24,Z+3),(X+13,25,Z+13),M),b((X+6,25,Z+6),(X+10,27,Z+10),BD)]   # moyeu
    for k in range(4):                                          # rayons de la poulie
        a=k*math.pi/4
        E.append(b((X+7.5,24,Z+2),(X+8.5,24.6,Z+14),M))
    if motrice: E+=[b((X+16,0,Z+4),(X+24,10,Z+12),PN),b((X+16,10,Z+5),(X+23,11,Z+11),BD)]   # carter du moteur, l'arbre de Create arrive dessous
    return E
def pylone(ox,oz,h):
    """Pylône : treillis d'airain, puis une tête à bras et deux galets où passe le câble."""
    X,Z=ox*16,oz*16; E=[]
    for (x,z) in ((2,2),(12,2),(2,12),(12,12)): E.append(b((X+x,0,Z+z),(X+x+2,h*16,Z+z+2),RO))
    for y in range(0,h*16,8):
        E+=[b((X+2,y,Z+3),(X+14,y+1,Z+4),BD),b((X+2,y,Z+12),(X+14,y+1,Z+13),BD),b((X+3,y+4,Z+2),(X+4,y+5,Z+14),BD),b((X+12,y+4,Z+2),(X+13,y+5,Z+14),BD)]
    H=h*16
    E+=[b((X+0,H,Z+0),(X+16,H+3,Z+16),RI),b((X+-6,H+3,Z+6),(X+22,H+5,Z+10),M)]   # chapiteau et bras
    E+=[b((X+-5,H+5,Z+5),(X+-1,H+9,Z+11),RG),b((X+17,H+5,Z+5),(X+21,H+9,Z+11),RG)]   # galets
    return E
def cable(p0,p1,fl=10,n=24):
    """Câble en chaînette (léger affaissement), en petits tronçons."""
    E=[]
    for k in range(n):
        t0,t1=k/n,(k+1)/n
        def pt(t): return [p0[i]+(p1[i]-p0[i])*t for i in range(3)][:1]+[p0[1]+(p1[1]-p0[1])*t-fl*4*t*(1-t)]+[p0[2]+(p1[2]-p0[2])*t]
        a,c=pt(t0),pt(t1)
        x0,x1=min(a[0],c[0]),max(a[0],c[0]); y=(a[1]+c[1])/2
        E.append(b((x0,y-0.5,a[2]-0.5),(x1+0.2,y+0.5,a[2]+0.5),'t:block/airain_rod'))
    return E,pt
def nacelle(cx,cy,cz):
    """Nacelle : chariot à deux galets sur le câble, bras de suspente, plateforme ouverte 2×2 à rambardes et portillon."""
    E=[]
    E+=[b((cx-6,cy-3,cz-2),(cx+6,cy+1,cz+2),PN),b((cx-5,cy+0.5,cz-1.5),(cx-2,cy+3,cz+1.5),RG),b((cx+2,cy+0.5,cz-1.5),(cx+5,cy+3,cz+1.5),RG)]   # chariot
    E+=[b((cx-1,cy-30,cz-1),(cx+1,cy-3,cz+1),RO),b((cx-12,cy-31,cz-1),(cx+12,cy-29,cz+1),BD)]               # bras et palonnier
    for dx in (-12,11): E.append(b((cx+dx,cy-44,cz-1),(cx+dx+1,cy-30,cz+1),RO))                            # tirants
    fy=cy-46; x0,x1,z0,z1=cx-16,cx+16,cz-16,cz+16
    E+=[b((x0,fy,z0),(x1,fy+2,z1),G,("up","down")),b((x0,fy,z0),(x1,fy+2,z0+1),BD),b((x0,fy,z1-1),(x1,fy+2,z1),BD),b((x0,fy,z0),(x0+1,fy+2,z1),BD),b((x1-1,fy,z0),(x1,fy+2,z1),BD)]
    for (a0,a1,c0,c1) in ((x0,x1,z0,z0+1.5),(x0,x1,z1-1.5,z1),(x0,x0+1.5,z0,z1)):            # rambardes (portillon côté x1)
        E+=[b((a0,fy+13,c0),(a1,fy+15,c1),M),b((a0,fy+7,c0),(a1,fy+8,c1),M)]
    for (px,pz) in ((x0,z0),(x1-1.5,z0),(x0,z1-1.5),(x1-1.5,z1-1.5)): E.append(b((px,fy+2,pz),(px+1.5,fy+15,pz+1.5),M))
    E+=[b((x1-1.5,fy+2,z0+3),(x1,fy+12,z0+4),M),b((x1-1.5,fy+2,z1-4),(x1,fy+12,z1-3),M),b((x1-1.5,fy+11,z0+3),(x1,fy+12,z1-3),M),b((x1-1.5,fy+6,z0+3),(x1,fy+7,z1-3),RG)]   # portillon
    return E
E=[]
E+=gare(0,0,True)+gare(14,0,False)+pylone(7,0,3)
# câble : gare motrice → pylône → gare d'arrivée (deux brins, aller et retour, de part et d'autre)
for dz in (-5,21):
    pass
c1,pt1=cable((16,24,8-5),(7*16-5,3*16+7,8-5),fl=6); c2,pt2=cable((7*16+21,3*16+7,8-5),(14*16,24,8-5),fl=6)
c3,_=cable((16,24,8+5),(7*16-5,3*16+7,8+5),fl=6); c4,_=cable((7*16+21,3*16+7,8+5),(14*16,24,8+5),fl=6)
E+=c1+c2+c3+c4
p=pt2(0.45); E+=nacelle(p[0],p[1],3)
for x in range(16):
    for z in range(-2,3): E+=cube((x,-1,z),'t:block/fire_bricks')
A=vue(E,[-0.35,0.45,-1],1300)
# laminoir : bâti, deux rouleaux, entrée du lingot et sortie du fil enroulé
L=[]
L+=[b((0,0,0),(16,4,16),RI),b((1,4,1),(4,14,15),PN),b((12,4,1),(15,14,15),PN),b((1,14,1),(15,16,15),BD)]
L+=[b((4,8,2),(12,10.5,14),RG),b((4,10.5,2),(12,13,14),RG),b((3,9,1),(13,12,2),M),b((3,9,14),(13,12,15),M)]   # rouleaux et paliers
L+=[b((-3,9.5,6),(4,10.5,10),'t:block/airain_ingot' if False else M),b((12,9.8,7.5),(18,10.2,8.5),RO)]          # lingot qui entre, fil qui sort
L+=[b((18,4,4),(22,12,12),RO),b((17,7,5),(23,9,11),BD)]                                                          # bobine de fil
B=vue(L+[b((x*16,-1,z*16),(x*16+16,0,z*16+16),'t:block/fire_bricks',("up",)) for x in (-1,0,1) for z in (-1,0,1)],[-0.7,0.7,-1],600)
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
W=Image.new('RGBA',(max(A.width,B.width)+40,A.height+B.height+130),(34,30,38,255)); d=ImageDraw.Draw(W)
d.text((20,10),"Téléphérique : gare motrice (moteur de Create), pylône, câble aller-retour, nacelle, gare d'arrivée",font=fo,fill=(235,215,170))
W.alpha_composite(A,(20,50)); d.text((20,A.height+70),"Laminoir : lingot d'airain → fil (puis fil → câble)",font=fo,fill=(235,215,170)); W.alpha_composite(B,(20,A.height+110))
W.save('rendu_fusion/telepherique.png'); print(W.size)
