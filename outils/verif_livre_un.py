import sys, json
exec(open('livre_maquette.py').read())
L=json.load(open(AIR+'lang/fr_fr.json'))
ims=[]
for k,ic in (('charpente','airain:airain_beam'),('marquages','airain:yellow_hazard_stripes')):
    ims+=chapitre(ic,L[f'airain.ingenieur.{k}.court'],L[f'airain.ingenieur.{k}.histoire'],L[f'airain.ingenieur.{k}.usage'],10,0)
planche(ims,'livre_charpente.png',2)
