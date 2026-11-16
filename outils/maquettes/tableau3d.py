# Maquette du tableau émaillé, seul afficheur retenu : mur de salle de contrôle, plaque pendue double face,
# panneau sur pied pour baliser une zone, et les cinq émaux.
exec(open('base3d.py').read())
EMAUX={'noir':((26,26,32,255),CR),'bleu':((30,62,120,255),CR),'rouge':((128,30,26,255),CR),'vert':((26,80,50,255),CR),'creme':((230,220,192,255),(70,40,24,255))}
def panneau(nom,w,h,email,dessin,k=8):
    """Texture de l'émail : w × h pixels de modèle, k pixels de texture par pixel de modèle ; reflet en haut à gauche."""
    fond,enc=EMAUX[email]
    im=Image.new('RGBA',(int(w*k),int(h*k)),fond); d=ImageDraw.Draw(im)
    cl=tuple(min(255,c+28) for c in fond[:3])+(255,)
    d.rectangle([0,0,im.width-1,2],fill=cl); d.rectangle([0,0,2,im.height-1],fill=cl)
    dessin(im,d,enc); im.save(D+nom+'.png'); return hd(nom)
def plaque_murale(X,Y,w,h,tex,ep=3):
    """Au mur : contre-plaque, cadre riveté en saillie (ep px), émail en retrait. X, Y, w, h en pixels de modèle."""
    E=[b((X,Y,14),(X+w,Y+h,16),SOMBRE)]
    E.append(b((X+ep,Y+ep,13),(X+w-ep,Y+h-ep,14),tex,("north",),{'north':FULL}))
    E+=[b((X,Y+h-ep,10.5),(X+w,Y+h,14),PL),b((X,Y,10.5),(X+w,Y+ep,14),PL),b((X,Y+ep,10.5),(X+ep,Y+h-ep,14),PL),b((X+w-ep,Y+ep,10.5),(X+w,Y+h-ep,14),PL)]
    E+=[b((X+ep,Y+h-ep-0.5,12.5),(X+w-ep,Y+h-ep,13),BD),b((X+ep,Y+ep,12.5),(X+ep+0.5,Y+h-ep,13),BD)]     # ombre intérieure
    for (cx,cy) in ((X+0.5,Y+0.5),(X+w-2.5,Y+0.5),(X+0.5,Y+h-2.5),(X+w-2.5,Y+h-2.5)): E.append(b((cx,cy,9.5),(cx+2,cy+2,10.5),CH))
    return E
def plaque_double(X,Y,Z,w,h,tex,ep=2):
    """Double face (pendue ou sur pied) : épaisseur 6 px, émail des deux côtés."""
    E=[b((X,Y,Z+5),(X+w,Y+h,Z+11),PL,("up","down","east","west")),
       b((X,Y,Z+5),(X+w,Y+ep,Z+11),PL,("north","south")),b((X,Y+h-ep,Z+5),(X+w,Y+h,Z+11),PL,("north","south")),
       b((X,Y+ep,Z+5),(X+ep,Y+h-ep,Z+11),PL,("north","south")),b((X+w-ep,Y+ep,Z+5),(X+w,Y+h-ep,Z+11),PL,("north","south")),
       b((X+ep,Y+ep,Z+5.8),(X+w-ep,Y+h-ep,Z+6),tex,("north",),{'north':FULL}),b((X+ep,Y+ep,Z+10),(X+w-ep,Y+h-ep,Z+10.2),tex,("south",),{'south':FULL})]
    for (cx,cy) in ((X+0.5,Y+0.5),(X+w-2.5,Y+0.5),(X+0.5,Y+h-2.5),(X+w-2.5,Y+h-2.5)): E+=[b((cx,cy,Z+4.5),(cx+2,cy+2,Z+5),CH),b((cx,cy,Z+11),(cx+2,cy+2,Z+11.5),CH)]
    return E
def ligne_val(im,d,x0,x1,y,nom,val,enc,barre=None):
    poser(im,nom,x0,y,enc,2)
    if barre:
        bx=x0+largeur(nom)*2+12
        for i in range(barre[0]): d.rectangle([bx+i*9,y+4,bx+i*9+6,y+13],fill=OR if i<barre[1] else (62,58,52))
    poser(im,val,x1,y,OR,2,False,'d')
# =============================================================== 1. salle de contrôle : 5 × 3 blocs, séparateurs en relief
W5,H3=96,48
def salle(im,d,enc):
    K=8; w=im.width
    poser(im,'SALLE DE CONTRÔLE · FONDERIE',w/2,14,RO,3,True,'c')
    G=[("PRODUCTION",[("Lingots d'airain",'1 284',None),("Débit tapis nord",'312 /min',None),("Haut-fourneau",'76 %',(6,5)),("Moulage du canon",'41 %',(6,2)),("Réservoir d'Écho",'90 %',(6,5))]),
       ("ÉNERGIE",[("Stress",'68 %',(6,4)),("Arbres principaux",'128 tr/min',None),("Turbine d'Écho",'64 tr/min',None)]),
       ("TRAINS",[("Port-Impérial",'2 min',None),("Mine du Nord",'7 min',None)])]
    col=[(14,w//2-14),(w//2+14,w-14)]
    y=[64,64]
    for i,(titre,L) in enumerate(G):
        c=0 if i==0 else 1
        x0,x1=col[c]
        poser(im,titre,x0,y[c],(200,160,90,255),2,True); y[c]+=28
        for nom,val,bar in L: ligne_val(im,d,x0,x1,y[c],nom,val,enc,bar); y[c]+=30
        y[c]+=10
def salle_relief(X,Y):
    # filet sous le titre et séparateur central : des baguettes d'airain sur l'émail
    return [b((X+3,Y+H3-10,12),(X+W5-3,Y+H3-9,13),BAR),b((X+W5/2-0.75,Y+3,12),(X+W5/2+0.75,Y+H3-10,13),BAR)]
t_salle=panneau('salle',W5-6,H3-6,'noir',salle)
def alerte(im,d,enc): poser(im,'RÉSERVOIR PLEIN',im.width/2,40,enc,2,True,'c')
t_alerte=panneau('alerte',32-4,16-4,'rouge',alerte)
E=mur(-4,8,0,5)+sol(-4,8,-3,1)
E+=plaque_murale(0,16,W5,H3,t_salle)+salle_relief(0,16)
E+=plaque_murale(-44,40,32,16,t_alerte,2)
E+=[b((X,0,-18),(X+16,10,-6),'minecraft:block/dark_oak_planks') for X in (16,32,48)]    # pupitre devant
SA=vue(E,[-0.25,0.3,-1],1300); SA=SA.crop(SA.getbbox())
# =============================================================== 2. plaque pendue sous une poutrelle (double face)
def gare(im,d,enc): poser(im,'GARE DE LA FONDERIE',im.width/2,26,enc,3,True,'c')
t_gare=panneau('gare',64-4,14-4,'bleu',gare)
def poutrelle_x(X0,X1,Y,Z): return [b((X0,Y,Z+3),(X1,Y+2,Z+13),FL),b((X0,Y+12,Z+3),(X1,Y+14,Z+13),FL),b((X0,Y+2,Z+7),(X1,Y+12,Z+9),WB,("north","south"))]
E=poutrelle_x(-8,72,30,0)
for cx in (8,54):
    E+=[b((cx,14,7.5),(cx+1,30,8.5),'airain:block/airain_rod'),b((cx+2,14,7.5),(cx+3,30,8.5),'airain:block/airain_rod'),b((cx-0.5,13,6.5),(cx+3.5,14,9.5),PL)]
E+=plaque_double(0,0,0,64,14,t_gare)
PE=vue(E,[-0.4,0.15,-1],800); PE=PE.crop(PE.getbbox())
# =============================================================== 3. panneau sur pied, au milieu d'une zone hachurée
def stock(im,d,enc):
    poser(im,'STOCKAGE',im.width/2,14,enc,4,True,'c'); poser(im,'Zone B',im.width/2,62,(200,190,160,255),2,False,'c')
t_stock=panneau('stock',32-4,14-4,'vert',stock)
E=sol(-2,4,-2,3)
for x in range(-1,3):
    for z in range(-1,2):
        if not (x in (0,1) and z==0): E.append(b((x*16,0.05,z*16),(x*16+16,0.1,z*16+16),'airain:block/yellow_hazard_stripes',("up",),{'up':FULL}))
# pied : poteau en I sur platine, puis la plaque
E+=[b((14,0,1),(18,1,15),PL),b((11,1,4),(21,26,6),FL),b((11,1,10),(21,26,12),FL),b((15,1,6),(17,26,10),WB,("east","west"))]
E+=[b((11,26,3),(21,27,13),PL)]
E+=plaque_double(0,27,0,32,14,t_stock)
PI=vue(E,[-0.5,0.4,-1],800); PI=PI.crop(PI.getbbox())
# =============================================================== 4. les cinq émaux (1 bloc chacun)
E=mur(-1,11,0,2)+sol(-1,11,-2,1)
for i,(em,mot) in enumerate(reversed((('noir','FORGE'),('bleu','GARE'),('rouge','DANGER'),('vert','STOCK'),('creme','BUREAU')))):
    def f(im,d,enc,mot=mot): poser(im,mot,im.width/2,im.height/2-12,enc,3,True,'c')
    t=panneau('email_'+em,12,12,em,f,12)
    E+=plaque_murale(i*32+8,8,16,16,t,2)
EM_=vue(E,[-0.2,0.2,-1],1300); EM_=EM_.crop(EM_.getbbox())
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22)
Wd=max(SA.width,PE.width+PI.width+60,EM_.width)+40
Ht=SA.height+max(PE.height,PI.height)+EM_.height+200
out=Image.new('RGBA',(Wd,Ht),(34,30,38,255)); dd=ImageDraw.Draw(out); y=10
dd.text((20,y),"1. Salle de contrôle : un tableau 6 × 3, baguettes en relief, et une alerte 2 × 1 en émail rouge",font=fo,fill=(235,215,170)); out.alpha_composite(SA,(20,y+36)); y+=SA.height+50
dd.text((20,y),"2. Pendu sous une poutrelle (double face)",font=fo,fill=(235,215,170)); dd.text((PE.width+80,y),"3. Sur pied, pour baliser une zone",font=fo,fill=(235,215,170))
out.alpha_composite(PE,(20,y+40)); out.alpha_composite(PI,(PE.width+80,y+36)); y+=max(PE.height,PI.height)+50
dd.text((20,y),"4. Les cinq émaux (colorant) : noir, bleu, rouge, vert, crème",font=fo,fill=(235,215,170)); out.alpha_composite(EM_,(20,y+36))
out.save('tableau3d.png'); print(out.size)
