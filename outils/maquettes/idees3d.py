# Maquettes de quatre idées d'usine : cheminées, cloisons et portail coulissant, pont roulant, quai de chargement.
exec(open('base3d.py').read())
import random
BRI='minecraft:block/bricks'; FB='airain:block/fire_bricks'; BAND='airain:block/airain_band'; RIVA='airain:block/riveted_airain'
GR='airain:block/airain_grate'; ROD='airain:block/airain_rod'; FLV='airain:block/airain_beam_flange'; WEB='airain:block/airain_beam_web'
SMK=['minecraft:block/light_gray_wool','minecraft:block/white_wool','minecraft:block/gray_wool']
def poutrelle_x(x0,x1,y,z):
    return [b((x0,y,z+3),(x1,y+2,z+13),FLV),b((x0,y+12,z+3),(x1,y+14,z+13),FLV),b((x0,y+2,z+7),(x1,y+12,z+9),WEB,("north","south"))]
def poutrelle_z(z0,z1,y,x):
    return [b((x+3,y,z0),(x+13,y+2,z1),FLV),b((x+3,y+12,z0),(x+13,y+14,z1),FLV),b((x+7,y+2,z0),(x+9,y+12,z1),WEB,("east","west"))]
def poteau(x,z,h):
    return [b((x+3,0,z+1),(x+13,h,z+3),FLV),b((x+3,0,z+13),(x+13,h,z+15),FLV),b((x+7,0,z+3),(x+9,h,z+13),WEB,("east","west"))]
def fumee(cx,cy,cz,n,seed):
    random.seed(seed); E=[]
    for k in range(n):
        s=3+k*0.9; dx=k*1.8+random.uniform(-1,1); y=cy+k*5
        E.append(b((cx-s+dx,y,cz-s),(cx+s+dx,y+s*1.4,cz+s),SMK[k%3]))
    return E
# ================================================================ 1. cheminées
def cheminee_briques(X,Z,h):
    E=[b((X-2,0,Z-2),(X+18,10,Z+18),RIVA)]                                        # socle riveté
    E+=[b((X+1,10,Z+1),(X+15,16*h,Z+15),BRI)]                                     # fût
    for y in range(24,16*h-8,24): E.append(b((X+0.5,y,Z+0.5),(X+15.5,y+2,Z+15.5),BAND))   # bagues de cerclage
    E+=[b((X-0.5,16*h,Z-0.5),(X+16.5,16*h+3,Z+16.5),BAND),b((X+0.5,16*h+3,Z+0.5),(X+15.5,16*h+5,Z+15.5),RIVA)]   # couronnement
    return E
def cheminee_airain(X,Z,h):
    E=[b((X+2,0,Z+2),(X+14,6,Z+14),RIVA)]
    for y in range(6,16*h,16): E+=[b((X+4,y,Z+4),(X+12,y+16,Z+12),'airain:block/airain_pipe_vertical'),b((X+3,y,Z+3),(X+13,y+1.5,Z+13),BAND)]
    E+=[b((X+2.5,16*h,Z+2.5),(X+13.5,16*h+2,Z+13.5),BAND),b((X+1,16*h+5,Z+1),(X+15,16*h+6.5,Z+15),RIVA)]   # chapeau
    for (x,z) in ((X+3,Z+3),(X+12,Z+3),(X+3,Z+12),(X+12,Z+12)): E.append(b((x,16*h+2,z),(x+1,16*h+5,z+1),ROD))
    return E
E=sol(-3,5,-3,3)
E+=[b((x*16,y*16,z*16),(x*16+16,y*16+16,z*16+16),FB) for x in range(0,3) for y in range(0,2) for z in range(0,2)]   # bâtiment de la forge
E+=cheminee_briques(16,0,6)
E+=fumee(24,16*6+5,8,7,1)
E+=cheminee_airain(-40,0,3)
E+=fumee(-32,16*3+7,8,4,2)
CH=vue(E,[-0.5,0.35,-1],1100); CH=CH.crop(CH.getbbox())
# ================================================================ 2. cloisons grillagées et portail coulissant
def cloison(X,Z,h=2):
    E=[]
    for y in range(h):
        E+=[b((X,y*16,Z+7),(X+16,y*16+16,Z+9),'airain:block/airain_grate',("north","south")),
            b((X,y*16+15,Z+6.5),(X+16,y*16+16,Z+9.5),BAND),b((X,y*16,Z+6.5),(X+16,y*16+1,Z+9.5),BAND)]
    E+=[b((X,0,Z+6),(X+1.5,16*h,Z+10),FLV)]
    return E
E=sol(-2,9,-3,3)
for x in range(0,3): E+=cloison(x*16,0)
for x in range(6,8): E+=cloison(x*16,0)
E+=[b((128-1.5,0,6),(128,32,10),FLV)]
# portail : rail au sol et rail haut, un vantail grillagé à demi ouvert (glissé derrière la cloison de droite)
E+=[b((48,0,9.5),(96,1,11.5),'airain:block/airain_rod'),b((48,32,9),(128,34,12),FLV)]
ox=76
E+=[b((ox,1.5,9.8),(ox+40,31,11.2),'airain:block/airain_grate',("north","south")),b((ox,1.5,9.5),(ox+40,3,11.5),BAND),b((ox,29.5,9.5),(ox+40,31,11.5),BAND),
    b((ox,1.5,9.5),(ox+2,31,11.5),BAND),b((ox+38,1.5,9.5),(ox+40,31,11.5),BAND),b((ox+2,15,9.6),(ox+38,16.5,11.4),BAND)]
for wx in (ox+6,ox+32): E+=[b((wx,0.2,9.6),(wx+3,1.8,11.4),RIVA),b((wx,31,9.6),(wx+3,33,11.4),RIVA)]   # galets
E+=[b((ox+3,14,8.5),(ox+5,18,9.5),'minecraft:block/red_concrete')]   # poignée
# hachures de passage devant le portail
for x in range(3,6):
    E.append(b((x*16,0.05,-16),(x*16+16,0.1,0),'airain:block/yellow_hazard_stripes',("up",),{'up':FULL}))
CL=vue(E,[-0.3,0.35,-1],1100); CL=CL.crop(CL.getbbox())
# ================================================================ 3. pont roulant
E=sol(-1,7,-1,5)
for (x,z) in ((0,0),(0,4),(5,0),(5,4)): E+=poteau(x*16,z*16,64)
for x in (0,5): E+=poutrelle_z(0,80,64,x*16)                                          # chemins de roulement
E+=[b((x*16+5,78,0),(x*16+11,79,80),ROD) for x in (0,5)]                               # rails
zb=36
E+=poutrelle_x(0,96,80,zb-8)                                                           # pont (poutre roulante)
E+=[b((0,79,zb-10),(16,86,zb+10),RIVA),b((80,79,zb-10),(96,86,zb+10),RIVA)]            # sommiers à galets
xc=40
E+=[b((xc,94,zb-7),(xc+14,99,zb+7),RIVA),b((xc+2,90,zb-5),(xc+12,94,zb+5),'airain:block/airain_panel')]   # chariot et treuil
E+=[b((xc+6.3,40,zb-0.7),(xc+7.7,90,zb+0.7),ROD),b((xc+4,34,zb-2),(xc+10,40,zb+2),RIVA),b((xc+6,30,zb-1),(xc+8,34,zb+1),ROD)]   # câble et crochet
E+=[b((xc-6,10,zb-8),(xc+20,30,zb+8),'minecraft:block/spruce_planks'),b((xc-4,30,zb-0.5),(xc+18,31,zb+0.5),ROD),b((xc+6.5,31,zb-0.5),(xc+7.5,34,zb+0.5),ROD)]   # caisse levée
PR=vue(E,[-0.55,0.35,-1],1100); PR=PR.crop(PR.getbbox())
# ================================================================ 4. quai de chargement
E=sol(-2,6,-4,2)
# trois casiers (cadre simplifié) et le quai devant le casier du milieu
for x in range(3):
    E+=[b((x*16,0,0.5),(x*16+16,3,2.5),BAND),b((x*16+14.5,0,1),(x*16+16,16,2.5),FLV),b((x*16+2,3,3),(x*16+14,12,13),'minecraft:block/spruce_planks')]
E+=[b((0,0,1),(1.5,16,2.5),FLV)]
E+=[b((16,0,-16),(32,10,0),'create:block/andesite_casing'),b((18,10,-14),(30,12,-2),RIVA),b((17,4,-16.2),(31,8,-16),'airain:block/airain_panel',("north",))]   # quai
E+=[b((16+3,0.1,-64),(32-3,4,-16),'create:block/belt',("up","east","west"))]           # tapis qui arrive
for z in (-56,-38): E.append(b((16+5,4,z),(32-5,10,z+6),'minecraft:block/spruce_planks'))
QU=vue(E,[-0.6,0.45,-1],1000); QU=QU.crop(QU.getbbox())
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22)
Wd=max(CH.width+CL.width,PR.width+QU.width)+100; Ht=max(CH.height,CL.height)+max(PR.height,QU.height)+140
out=Image.new('RGBA',(Wd,Ht),(34,30,38,255)); dd=ImageDraw.Draw(out)
dd.text((20,10),"1. Cheminées : briques cerclées, ou conduit d'airain",font=fo,fill=(235,215,170))
dd.text((CH.width+60,10),"2. Cloisons grillagées, portail coulissant",font=fo,fill=(235,215,170))
out.alpha_composite(CH,(20,46)); out.alpha_composite(CL,(CH.width+60,46))
y=max(CH.height,CL.height)+70
dd.text((20,y),"3. Pont roulant : chariot et crochet",font=fo,fill=(235,215,170))
dd.text((PR.width+60,y),"4. Quai de chargement du rayonnage",font=fo,fill=(235,215,170))
out.alpha_composite(PR,(20,y+36)); out.alpha_composite(QU,(PR.width+60,y+36))
out.save('idees3d.png'); print(out.size)
