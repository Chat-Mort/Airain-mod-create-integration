# 1.64 : schémas des scènes Ponder du mod (structures NBT de Minecraft, couche 0 = plateau de base).
import os
from nbtlib import File, Compound, List, Int, String, Long, Byte, Short
from nbtlib.tag import IntArray
D='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/ponder/'
os.makedirs(D,exist_ok=True)
BASE='minecraft:smooth_stone'
class Schema:
    def __init__(s,nom,tx,ty,tz,base=BASE):
        s.nom=nom; s.t=(tx,ty,tz); s.blocs={}
        for x in range(tx):
            for z in range(tz): s.mettre(x,0,z,base)
    def mettre(s,x,y,z,bloc,props=None,nbt=None): s.blocs[(x,y,z)]=(bloc,props or {},nbt)
    def ecrire(s):
        pal=[]; idx={}; blocs=[]
        for (x,y,z),(b,p,n) in sorted(s.blocs.items(),key=lambda k:(k[0][1],k[0][2],k[0][0])):
            cle=(b,tuple(sorted(p.items())))
            if cle not in idx:
                idx[cle]=len(pal)
                e=Compound({'Name':String(b)})
                if p: e['Properties']=Compound({k:String(str(v).lower()) for k,v in p.items()})
                pal.append(e)
            e=Compound({'state':Int(idx[cle]),'pos':List[Int]([Int(x),Int(y),Int(z)])})
            if n is not None: e['nbt']=n
            blocs.append(e)
        f=File({'DataVersion':Int(3955),'size':List[Int]([Int(v) for v in s.t]),'palette':List[Compound](pal),'blocks':List[Compound](blocs),'entities':List[Compound]([])},gzipped=True)
        f.save(D+s.nom+'.nbt')
def pos(x,y,z): return Long((((x & 0x3FFFFFF) << 38) | ((z & 0x3FFFFFF) << 12) | (y & 0xFFF)) - (1<<64 if ((x & 0x3FFFFFF) >> 25) else 0))
def item(i,n=1): return Compound({'id':String(i),'count':Int(n)})

# ---------------------------------------------------------------- 1. haut-fourneau (face avant au nord)
s=Schema('haut_fourneau',9,7,9)
cx,tz=4,2
s.mettre(cx,0,tz+2,'create:blaze_burner',{'blaze':'seething','facing':'north'})
def local(lx,ly,lz): return (cx-lx,1+ly,tz+lz)      # gauche (lx +) vers l'ouest
def emprise(lx,ly,lz):
    if ly<=1: return abs(lx)<=2 and 0<=lz<=4 and not (abs(lx)==2 and lz in (0,4))
    return abs(lx)<=1 and 1<=lz<=3
for ly in range(5):
    for lx in range(-2,3):
        for lz in range(5):
            if not emprise(lx,ly,lz): continue
            interieur=abs(lx)<=1 and 1<=lz<=3
            p=local(lx,ly,lz)
            if ly==0 and lx==0 and lz==0: s.mettre(*p,'airain:blast_furnace_taphole',{'facing':'north'})
            elif ly==0 and lx==0 and lz==2: s.mettre(*p,'airain:airain_grate')
            elif ly==1 and interieur: pass
            elif ly==1 and lx==-2 and lz==2: s.mettre(*p,'airain:blast_furnace_tuyere',{'facing':'east'})
            elif ly in (2,3) and lx==0 and lz==2: pass
            elif ly==4 and lx==0 and lz==2: s.mettre(*p,'airain:blast_furnace_hopper')
            else: s.mettre(*p,'airain:fire_bricks')
tx,ty,tzz=local(-2,1,2)
s.mettre(tx+1,ty,tzz,'create:encased_fan',{'facing':'west'})
s.mettre(tx+2,ty,tzz,'create:creative_motor',{'facing':'west'})
s.mettre(cx,1,1,'create:fluid_pipe',{'north':'true','south':'true'})
s.mettre(cx,1,0,'create:basin')
s.ecrire()

# ---------------------------------------------------------------- 2. laminoir
s=Schema('laminoir',5,3,5)
s.mettre(2,1,2,'airain:airain_rolling_mill',{'facing':'north'})
s.mettre(3,1,2,'create:shaft',{'axis':'x'}); s.mettre(4,1,2,'create:creative_motor',{'facing':'west'})
s.mettre(2,1,1,'create:depot')
s.ecrire()

# ---------------------------------------------------------------- 3. téléphérique : gare, pylône, gare
s=Schema('telepherique',15,7,5)
A,P,B=(1,1,2),(7,1,2),(13,1,2)
H=(7,5,2)
s.mettre(*A,'airain:airain_cable_station',{'facing':'east','upper':'false'},Compound({'id':String('airain:airain_cable_station'),'suivant':pos(*H),'tourne':Byte(0)}))
s.mettre(A[0],2,A[2],'airain:airain_cable_station',{'facing':'east','upper':'true'})
for y in range(1,5): s.mettre(7,y,2,'airain:airain_pylon')
s.mettre(*H,'airain:airain_pylon_head',{'facing':'east'},Compound({'id':String('airain:airain_pylon_head'),'precedent':pos(*A),'suivant':pos(*B)}))
s.mettre(*B,'airain:airain_cable_station',{'facing':'west','upper':'false'},Compound({'id':String('airain:airain_cable_station'),'precedent':pos(*H),'tourne':Byte(0)}))
s.mettre(B[0],2,B[2],'airain:airain_cable_station',{'facing':'west','upper':'true'})
s.mettre(1,0,2,'create:shaft',{'axis':'y'})
s.ecrire()

# ---------------------------------------------------------------- 4. monte-charge : treuil, mât, cabine, deux étages
s=Schema('monte_charge',7,8,7)
s.mettre(3,1,2,'airain:airain_lift_winch',{'axis':'x'})
for y in range(2,7): s.mettre(3,y,2,'airain:airain_lift_mast',{'facing':'south'})
s.mettre(3,2,3,'airain:airain_lift_cabin',{'facing':'south','top':'false'})
s.mettre(3,3,3,'airain:airain_lift_cabin',{'facing':'south','top':'true'})
s.mettre(4,1,2,'create:shaft',{'axis':'x'}); s.mettre(5,1,2,'create:creative_motor',{'facing':'west'})
for x in (2,3,4): s.mettre(x,4,4,'airain:airain_catwalk',{'top':'false','north':'none','south':'railing','east':'railing' if x==4 else 'none','west':'railing' if x==2 else 'none'})
s.mettre(3,1,4,'airain:airain_catwalk',{'top':'false','south':'railing'})
s.mettre(2,2,4,'airain:airain_lift_call_box',{'face':'wall','facing':'south'})
s.ecrire()

# ---------------------------------------------------------------- 5. passages mobiles : deux quais, un pont-levis, une passerelle rétractable
s=Schema('passages_mobiles',9,3,7)
def plancher(x,z,cotes): s.mettre(x,1,z,'airain:airain_catwalk',{'top':'false',**cotes})
for z in (1,5):
    plancher(1,z,{'west':'railing'}); plancher(7,z,{'east':'railing'})
s.mettre(2,1,1,'airain:airain_catwalk_drawbridge',{'top':'false'})
for x in (3,4,5,6): plancher(x,1,{'north':'railing','south':'railing'})
s.mettre(2,1,5,'airain:airain_catwalk_telescopic',{'top':'false'})
for x in (3,4,5,6): plancher(x,5,{'north':'railing','south':'railing'})
s.mettre(2,0,1,'create:shaft',{'axis':'y'}); s.mettre(2,0,5,'create:shaft',{'axis':'y'})
s.ecrire()

# ---------------------------------------------------------------- 6. conduite d'air : ventilateur, conduits, bouche
s=Schema('conduite_air',9,4,5)
s.mettre(1,1,2,'create:creative_motor',{'facing':'east'}); s.mettre(2,1,2,'create:encased_fan',{'facing':'east'})
for x in range(3,7): s.mettre(x,1,2,'airain:airain_air_duct',{'east':'true','west':'true'})
s.mettre(7,1,2,'airain:airain_air_vent',{'facing':'east'})
s.ecrire()

# ---------------------------------------------------------------- 7. rayonnage : 3 × 2 casiers garnis, un entonnoir
s=Schema('rayonnage',7,4,5)
STOCK={(0,0):('minecraft:cobblestone',1856),(1,0):('minecraft:iron_ingot',6120),(2,0):('minecraft:oak_log',412),(0,1):('minecraft:redstone',905),(2,1):('minecraft:coal',1210)}
for i in range(3):
    for j in range(2):
        props={'facing':'north','left_end':'true' if i==2 else 'false','right_end':'true' if i==0 else 'false','top':'true' if j==1 else 'false'}
        c=Compound({'quantite':Long(0),'renforts':Byte(1 if (i,j)==(1,0) else 0),'reserve':Byte(0)})
        if (i,j) in STOCK: c['modele']=item(STOCK[(i,j)][0]); c['quantite']=Long(STOCK[(i,j)][1])
        s.mettre(4-i,1+j,2,'airain:airain_rack',props,Compound({'id':String('airain:airain_rack'),'casier':c}))
s.mettre(5,1,2,'create:andesite_funnel',{'facing':'east','extracting':'false'})
s.ecrire()

# ---------------------------------------------------------------- 8. tableau émaillé : 3 × 2 au mur, une liaison d'affichage sur un stressomètre
s=Schema('tableau_emaille',7,5,5)
for x in range(1,6):
    for y in range(1,4): s.mettre(x,y,3,'minecraft:bricks')
def ligne(t,x,a=0,taille=1,c=0): return Compound({'t':Byte(t),'x':String(x),'a':Byte(a),'s':Byte(taille),'c':Byte(c)})
reg=Compound({'avant':List[Compound]([ligne(0,'FONDERIE',1,2,2),ligne(3,'Stress'),ligne(4,'Cuve'),ligne(3,'Arbres')]),'arriere':List[Compound]([]),
  'email':Byte(15),'cadre':Byte(0),'airain':Byte(0),'mat':Byte(0),'ecusson':Byte(1),'rosaces':Byte(1),'baguettes':Byte(1),
  'police':Byte(1),'coulTexte':Byte(0),'coulValeur':Byte(1),'eclairage':Byte(0),'intensite':Byte(10),'allumage':Byte(0),
  'alerteLigne':Byte(0),'seuil':Int(90),'alerteAction':Byte(0),'alerteCouleur':Byte(2),'accrochage':Byte(0),'memeFace':Byte(1)})
ctl=(4,3,2)
for i in range(3):
    for j in range(2):
        p=(4-i,3-j,2)
        n=Compound({'id':String('airain:enamel_board'),'ctl':pos(*ctl),'w':Byte(3 if p==ctl else 1),'h':Byte(2 if p==ctl else 1)})
        if p==ctl: n['reglages']=reg; n['valeurs']=List[String]([String(''),String('68%'),String('█████▒▒▒'),String('128 RPM')])
        s.mettre(*p,'airain:enamel_board',{'facing':'north','mount':'wall'},n)
s.mettre(5,1,1,'create:stressometer',{'facing':'west'}); s.mettre(4,1,1,'create:shaft',{'axis':'x'}); s.mettre(6,1,1,'create:shaft',{'axis':'x'})
s.mettre(5,2,1,'create:display_link',{'facing':'up'})
s.ecrire()
print('schémas ok :', sorted(os.listdir(D)))
