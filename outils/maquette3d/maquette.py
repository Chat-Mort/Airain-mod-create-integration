# Maquettes 3D : tête de réverbère élargie, contour de cloison grillagée à côté d'un portail coulissant.
import json, copy
from PIL import Image, ImageDraw, ImageFont
import rendu_modele as R
M='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/'
def mod(n): d=json.load(open(M+n+'.json')); return d['elements'], d['textures']
def boite(a,b,t,lum=False):
    f={}
    for k in ('north','south','east','west','up','down'):
        f[k]={'texture':t}
        if lum: f[k]['neoforge_data']={'block_light':15}
    return {'from':list(a),'to':list(b),'faces':f}
def dec(els,dx=0,dy=0,dz=0):
    out=[]
    for e in els:
        e=copy.deepcopy(e); e['from']=[e['from'][0]+dx,e['from'][1]+dy,e['from'][2]+dz]; e['to']=[e['to'][0]+dx,e['to'][1]+dy,e['to'][2]+dz]
        out.append(e)
    return out
def miroir_z(els):
    # rotation 180° autour de y : x -> 16-x, z -> 16-z, faces nord/sud et est/ouest échangées
    sw={'north':'south','south':'north','east':'west','west':'east'}; out=[]
    for e in els:
        e=copy.deepcopy(e); a,b=e['from'],e['to']
        e['from']=[16-b[0],a[1],16-b[2]]; e['to']=[16-a[0],b[1],16-a[2]]
        e['faces']={sw.get(k,k):v for k,v in e['faces'].items()}; out.append(e)
    return out
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)

# ---- réverbère
mat,tx=mod('airain_lamppost_mast'); base,_=mod('airain_lamppost_base'); tete,txh=mod('airain_lamppost_head')
tx=dict(txh); tx.update({'ro':'airain:block/airain_rod'})
col=dec(base)+dec(mat)
actuel=col+dec(tete,dy=16)
L=[ # nouvelle tête : lanterne de 8 px vitrée, toit à gradins et fleuron
 boite((6.5,0,6.5),(9.5,3,9.5),'#fl'),
 boite((5,3,5),(11,4,11),'#m'),
 boite((3.5,4,3.5),(12.5,5,12.5),'#m'),
 boite((4.5,5,4.5),(11.5,12,11.5),'#lw',True),
 *[boite((x,5,z),(x+1,12,z+1),'#m') for x in (4,11) for z in (4,11)],
 boite((3,12,3),(13,13,13),'#m'),
 boite((4.5,13,4.5),(11.5,14,11.5),'#m'),
 boite((6,14,6),(10,15,10),'#m'),
 boite((7.5,15,7.5),(8.5,17.5,8.5),'#m'),
]
neuf=col+dec(L,dy=16)
ia=R.rendre(actuel,tx,taille=520); ib=R.rendre(neuf,tx,taille=520,echelle=None)
# même échelle pour comparer
import numpy as np
im=Image.new('RGB',(1100,640),(28,29,34)); d=ImageDraw.Draw(im)
d.text((20,14),"Réverbère : tête actuelle (à gauche) et tête élargie proposée (à droite)",font=F,fill=(235,235,235))
im.paste(ia,(20,80),ia); im.paste(ib,(560,80),ib)
d.text((20,600),"Lumière : déjà au niveau 15 en haut du réverbère",font=f2,fill=(200,200,200))
im.save('apercu_reverbere.png')

# ---- cloison + portail
post,txf=mod('airain_mesh_fence_post'); side,_=mod('airain_mesh_fence_side'); st,_=mod('airain_mesh_fence_side_top'); sb,_=mod('airain_mesh_fence_side_bottom')
cote_n=side+st+sb; cote_s=miroir_z(cote_n)
# contour proposé : montant au bord de la cloison, côté portail
montant_s=[boite((7,0,14.5),(9,16,16),'#bd')]; montant_n=miroir_z(montant_s)
def scene(avec):
    els=[]
    els+=dec(post+cote_n+cote_s,dz=0)                    # cloison A (vers le sud = portail)
    els+=dec(post+cote_n+cote_s,dz=32)            # cloison B (portail au nord)
    els+=dec(post+cote_n+cote_s,dz=-16); els+=dec(post+cote_n,dz=48)
    if avec: els+=dec(montant_s,dz=0)+dec(montant_n,dz=32)
    # portail ouvert : vantail glissé devant la cloison B (bloc z 16..32 vide)
    els+=dec([boite((9.75,0,0),(10.25,16,16),'#g'),boite((9.4,14.5,0),(10.6,16,16),'#bd'),boite((9.4,0,0),(10.6,1.5,16),'#bd'),boite((9.3,0,0),(10.7,16,1.5),'#bd'),boite((9.3,0,14.5),(10.7,16,16),'#bd')],dz=32)
    return els
txf=dict(txf)
a=R.rendre(scene(False),txf,taille=560); b=R.rendre(scene(True),txf,taille=560)
im=Image.new('RGB',(1160,680),(28,29,34)); d=ImageDraw.Draw(im)
d.text((20,14),"Cloison grillagée autour d'un portail coulissant ouvert : aujourd'hui (à gauche) et proposé (à droite)",font=f2,fill=(235,235,235))
im.paste(a,(10,70),a); im.paste(b,(590,70),b)
d.text((20,640),"Proposé : un montant d'airain au bord de chaque cloison qui touche le portail, pour encadrer l'ouverture",font=f2,fill=(200,200,200))
im.save('apercu_cloison.png')
