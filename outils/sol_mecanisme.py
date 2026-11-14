# Sol des pièces-mécanismes (pont-levis, passerelle rétractable) : bandes de danger en deux teintes d'airain.
import math
src=open('ferronnerie.py').read(); exec(src[:src.index('OUT=')])
def bande(x,y): return x<3 or y<3 or x>12 or y>12
def raye(x,y): return ((x+y)//3)%2==0      # rayures diagonales nettes de 3 px
def relief_bande(x,y):
    # le bord extérieur de la bande : clair en haut à gauche, sombre en bas à droite ; le bord intérieur à l'inverse
    if x==0 or y==0: return 5.2
    if x==15 or y==15: return 0.9
    if (x==12 and 3<=y<=12) or (y==12 and 3<=x<=12): return 4.6   # arête intérieure éclairée (la bande est plus haute)
    if (x==3 and 3<=y<=12) or (y==3 and 3<=x<=12): return 1.6
    return None
def composer(centre, t_or, t_rouge):
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            v=relief_bande(x,y)
            if bande(x,y) or v is not None and (x in (3,12) or y in (3,12)) and 3<=x<=12 and 3<=y<=12:
                if v is None: v=3.6 if (x+y)%3 else 3.9   # aplat, un liseré clair par rayure
                t=t_rouge if (bande(x,y) and raye(x,y) and 0<x<15 and 0<y<15) else t_or
                a=int(v); f=v-a; p[x,y]=melange(teinte(a,t),teinte(a+1,t),f)+(255,)
            else:
                c=centre[y][x]
                if c is None: p[x,y]=(0,0,0,0)
                else: a=int(c); f=c-a; p[x,y]=melange(teinte(a,t_or),teinte(a+1,t_or),f)+(255,)
    return im
GRILLE_C=carte(GRILLE)
PLEIN=[[3.0+eclat(x,y)*1.0-(y/16)*0.4 for x in range(16)] for y in range(16)]
for (x,y) in ((5,5),(10,5),(5,10),(10,10)): PLEIN[y][x]=5.3; PLEIN[y+1][x+1]=1.7      # rivets
D='airain_tex/block/'
for s_,p in enumerate(['','exposed_','weathered_','oxidized_']):
    rouge=T[3] if s_<2 else T[0]
    composer(GRILLE_C,T[s_],rouge).save(D+f'{p}airain_catwalk_mecaA.png')
    composer(PLEIN,T[s_],rouge).save(D+f'{p}airain_catwalk_mecaB.png')
print('ok')
