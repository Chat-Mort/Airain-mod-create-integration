# Maquette du rayonnage impérial : casiers d'un bloc qui se raccordent (montants, lisses), palettes, stock visible,
# étiquettes émaillées, renforts (capacité), entonnoir de Create sur le côté, allée marquée au sol.
exec(open('base3d.py').read())
MC_I='minecraft:item/'; MC_B='minecraft:block/'
PLANK='minecraft:block/spruce_planks'; PAL='minecraft:block/oak_planks'
BAND='airain:block/airain_band'; ROD='airain:block/airain_rod'; FLV='airain:block/airain_beam_flange'
K=8
def etiquette(nom,nombre,icone,niveau):
    """Plaque émaillée du casier : icône de l'objet, nom, quantité, et des barrettes de renfort (0 à 4)."""
    im=Image.new('RGBA',(12*K,4*K),(26,26,32,255)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,im.width-1,1],fill=(60,60,70))
    ic=Image.open(rm.RAC['minecraft']+'textures/'+icone.split(':')[1]+'.png').convert('RGBA').crop((0,0,16,16)).resize((24,24),Image.NEAREST)
    im.alpha_composite(ic,(4,4))
    poser(im,nom,32,2,CR,1)
    poser(im,nombre,32,13,OR,2,True)
    for k in range(4):
        c=(232,196,110,255) if k<niveau else (62,58,52,255)
        d.rectangle([im.width-8,im.height-6-k*6,im.width-4,im.height-3-k*6],fill=c)
    n='etiq_'+nom.replace(' ','_').replace("'",'')
    im.save(D+n+'.png'); return hd(n)
def casier(cx,cy,contenu=None,gauche=True,droite=True,haut=False):
    """Un casier d'un bloc. contenu = (type, texture, remplissage 0..1, étiquette)."""
    X,Y=cx*16,cy*16; E=[]
    # montants (avant et arrière) aux bords du casier, partagés avec le voisin : dessinés à gauche, et à droite en bout de rang
    for xx in ([0] if gauche else [])+([14.5] if droite else []):
        for zz in (1,13.5):
            E+=[b((X+xx,Y,zz),(X+xx+1.5,Y+16,zz+1.5),FLV)]
    if gauche: E+=[b((X+0.25,Y+6,2.5),(X+1.25,Y+7,13.5),ROD),b((X+0.25,Y+12,2.5),(X+1.25,Y+13,13.5),ROD)]   # entretoises de côté
    if droite: E+=[b((X+14.75,Y+6,2.5),(X+15.75,Y+7,13.5),ROD),b((X+14.75,Y+12,2.5),(X+15.75,Y+13,13.5),ROD)]
    # lisses avant et arrière, et le platelage
    E+=[b((X,Y,0.5),(X+16,Y+2.5,2.5),BAND),b((X,Y,13.5),(X+16,Y+2.5,15.5),BAND),b((X+1,Y+2,2.5),(X+15,Y+2.5,13.5),'airain:block/airain_grate',("up",))]
    if contenu:
        typ,tx,f,et=contenu
        # palette de bois
        for zz in (2.8,7.3,11.8): E.append(b((X+2,Y+2.5,zz),(X+14,Y+3.5,zz+1.4),PAL))
        E.append(b((X+2,Y+3.5,2.8),(X+14,Y+4.2,13.2),PAL,("up","north","south","east","west")))
        if typ=='bloc':          # cubes de 3,5 px, jusqu'à 3 couches de 3 × 3
            n=max(1,round(f*27)); k=0
            for ly in range(3):
                for zz in range(3):
                    for xx in range(3):
                        if k>=n: break
                        x0=X+2.4+xx*3.8; z0=3.2+zz*3.4; y0=Y+4.2+ly*3.5
                        E.append(b((x0,y0,z0),(x0+3.5,y0+3.5,z0+3.2),tx)); k+=1
        else:                    # caisses à claire-voie, l'objet peint sur le devant
            n=max(1,round(f*6)); k=0
            for ly in range(2):
                for xx in range(3):
                    if k>=n: break
                    x0=X+2.4+xx*3.8; y0=Y+4.2+ly*4.4
                    E+=[b((x0,y0,3.2),(x0+3.6,y0+4.2,13),PLANK),b((x0+0.5,y0+0.6,3.1),(x0+3.1,y0+3.6,3.2),tx,("north",),{'north':FULL})]
                    k+=1
        E+=[b((X+2,Y-1.8,0.0),(X+14,Y+2.4,0.3),et,("north",),{'north':FULL}),b((X+1.6,Y-2.2,0.3),(X+14.4,Y+2.8,0.6),PL)]     # étiquette émaillée accrochée à la lisse
    return E
R=[[('bloc',MC_B+'cobblestone',0.85,etiquette('Pierre','1 856',MC_B+'cobblestone',1)),('bloc',MC_B+'oak_log',0.45,etiquette('Bûches','412',MC_B+'oak_log',0)),
    ('objet',MC_I+'iron_ingot',0.9,etiquette('Fer','6 120',MC_I+'iron_ingot',3)),('objet',MC_I+'copper_ingot',0.3,etiquette('Cuivre','288',MC_I+'copper_ingot',0))],
   [('bloc',MC_B+'sand',1.0,etiquette('Sable','2 048',MC_B+'sand',1)),None,('objet',MC_I+'redstone',0.55,etiquette('Redstone','905',MC_I+'redstone',0)),('bloc',MC_B+'stone_bricks',0.2,etiquette('Briques','96',MC_B+'stone_bricks',0))],
   [('objet',MC_I+'coal',0.7,etiquette('Charbon','1 210',MC_I+'coal',2)),('bloc',MC_B+'andesite',0.6,etiquette('Andésite','830',MC_B+'andesite',0)),None,('objet',MC_I+'gold_ingot',0.15,etiquette('Or','64',MC_I+'gold_ingot',0))]]
E=sol(-3,6,-4,2)
for cy,ligne in enumerate(R):
    for cx,c in enumerate(ligne): E+=casier(cx,cy,c,True,cx==len(ligne)-1)
# couronnement en haut du rack
E+=[b((0,48,0.5),(64,49.5,15.5),BAND,("up","north","south","east","west"))]
# allée jaune devant
for x in range(-2,6): E.append(b((x*16,0.05,-3*16+7),(x*16+16,0.1,-3*16+9),'airain:block/yellow_floor_line',("up",),{'up':[0,7,16,9]}))
RA=vue(E,[-0.35,0.3,-1],1400); RA=RA.crop(RA.getbbox())
# gros plan sur deux casiers
E=sol(-1,3,-2,1)+casier(0,0,R[0][2],True,False)+casier(1,0,R[0][0],True,True)
GP=vue(E,[-0.3,0.3,-1],900); GP=GP.crop(GP.getbbox())
# les renforts : objets d'amélioration (icônes provisoires)
def renfort(n,c):
    im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([2,5,13,10],fill=(150,104,48,255)); d.rectangle([2,5,13,5],fill=(250,226,160,255)); d.rectangle([2,10,13,10],fill=(96,62,30,255))
    for k in range(n): d.rectangle([3+k*3,7,4+k*3,8],fill=c)
    return im.resize((96,96),Image.NEAREST)
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22); fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
Wd=max(RA.width,GP.width+620)+40; Ht=RA.height+GP.height+150
out=Image.new('RGBA',(Wd,Ht),(34,30,38,255)); dd=ImageDraw.Draw(out)
dd.text((20,10),"Rayonnage impérial : casiers d'un bloc raccordés, stock visible, étiquettes, un seul inventaire trié",font=fo,fill=(235,215,170))
out.alpha_composite(RA,(20,46)); y=RA.height+70
dd.text((20,y),"Gros plan : caisses et cubes, étiquette émaillée",font=fo,fill=(235,215,170)); out.alpha_composite(GP,(20,y+36))
x=GP.width+120
dd.text((x,y),"Renforts (capacité par casier)",font=fo,fill=(235,215,170))
for i,(cap,col) in enumerate(((64,(232,196,110,255)),(128,(232,196,110,255)),(256,(140,190,240,255)),(512,(214,64,48,255)))):
    out.alpha_composite(renfort(i+1,col),(x+i*140,y+50)); dd.text((x+i*140+10,y+152),f"{cap} piles",font=fs,fill=(235,215,170))
dd.text((x,y+190),"Base : 32 piles par casier, un seul objet",font=fs,fill=(200,185,150))
out.save('rayonnage3d.png'); print(out.size)
