# Pagination de tous les chapitres (mêmes règles que l'écran) et planche de contrôle.
import sys, json
exec(open('livre_maquette.py').read())
exec(open('livre_textes.py').read())
lang=sys.argv[1] if len(sys.argv)>1 else 'fr'
T=FR if lang=='fr' else EN
L=json.load(open(AIR+'lang/'+('fr_fr' if lang=='fr' else 'en_us')+'.json'))
src=open('/home/claude/airain-mod-create-integration/src/main/java/fr/chatmort/airain/ingenieur/LivreIngenieurScreen.java').read()
import re
ch=re.findall(r'\{"(\w+)", "([\w:]+)"\}',src)
vus=set(); ims=[]; tot=0; num=6
for k,ic in ch:
    if k in vus: continue
    vus.add(k)
    h,u=T[k]; court=L.get(f'airain.ingenieur.{k}.court',k)
    P=chapitre(ic,court,h,u,num,0); num+=len(P); tot+=len(P)
    if len(P)>1: print('2 pages :',k,len(P))
    ims+=P
print('doubles pages de chapitres :',tot,'/',len(vus))
if len(sys.argv)>2:
    for i in range(0,len(ims),8): planche(ims[i:i+8],f'livre_{lang}_{i//8}.png',2)
