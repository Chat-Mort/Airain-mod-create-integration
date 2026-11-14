src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
import shutil,os
MOD='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
tmp=os.path.abspath('racine_mat')+'/'; os.makedirs(tmp+'textures/block',exist_ok=True); os.makedirs(tmp+'models',exist_ok=True)
for f in os.listdir(MOD+'textures/block'):
    if f.endswith('.png'): shutil.copyfile(MOD+'textures/block/'+f,tmp+'textures/block/'+f)
for f in os.listdir('materiaux'): shutil.copyfile('materiaux/'+f,tmp+'textures/block/'+f)
rm.RAC['t']=tmp; rm._cache.clear()
def cu(pos,t,top=None):
    c=cube(pos,'t:block/'+t)
    if top:
        for e in c: e['faces']['up']['texture']='t:block/'+top; e['faces']['down']['texture']='t:block/'+top
    return c
E=[]
# sol en carrelage, socle de marbre noir, murs de marbre blanc en briques, colonnes, frise ciselée, toit d'ardoise
for x in range(7):
    for z in range(4): E+=cu((x,0,z),'carrelage')
for x in range(7):
    E+=cu((x,1,4),'marbre_noir_dalles')
    for y in (2,3):
        if x in (0,3,6): E+=cu((x,y,4),'marbre_blanc_colonne','marbre_blanc_dalles')
        else: E+=cu((x,y,4),'marbre_blanc_briques' if y==2 else 'marbre_blanc')
    E+=cu((x,4,4),'marbre_blanc_cisele' if x%2 else 'marbre_noir_cisele')
    E+=cu((x,5,5),'ardoise_tuiles','ardoise_tuiles')
    E+=cu((x,5,4),'ardoise_polie')
# un pan de bois laqué et une porte d'airain pour l'échelle des couleurs
E+=cu((7,1,4),'laque_panneau')+cu((7,2,4),'laque')+cu((7,3,4),'laque_panneau')
E+=cu((1,1,1),'chiseled_airain')+cu((5,1,2),'airain_block')+cu((5,2,2),'oxidized_airain_block')
A=vue(E,[-0.55,0.55,-1],1000)
A.save('rendu_fusion/scene_materiaux.png')
