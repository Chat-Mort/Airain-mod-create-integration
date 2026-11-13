# Écrit toutes les textures finales de l'airain dans le mod (ordre : base → poli → fourneau → décor → ferronnerie).
import subprocess, shutil, os, sys
S='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/'
os.chdir(S)
for f in ('airain_textures.py','airain_luxe.py','fourneau_luxe.py','airain_deco.py'):
    subprocess.run([sys.executable,f],check=True,stdout=subprocess.DEVNULL)
from PIL import Image
sys.path.insert(0,S)
exec(open(S+'airain_luxe.py').read().split("STADES=['','exposed_'")[0])
import importlib.util
spec=importlib.util.spec_from_file_location('ferr',S+'ferronnerie.py'); fe=importlib.util.module_from_spec(spec); spec.loader.exec_module(fe)
T_=[0.0,0.28,0.58,0.92]; PRE=['','exposed_','weathered_','oxidized_']
TX=S+'airain_tex/'
MC=S+'mcmeta-assets/assets/minecraft/textures/'
ROUGE_FLAMME=[(110,16,14),(170,30,22),(220,60,40),(250,120,90),(255,190,170),(255,230,220)]
def flamme_rouge(im, metal_t):
    """Lanterne : le fer devient airain du stade, la flamme devient rouge."""
    px=im.load(); out=im.copy(); q=out.load()
    flamme=lambda c: c[3]>0 and c[0]>c[2]+40
    vals_m=sorted({sum(px[x,y][:3]) for y in range(im.height) for x in range(im.width) if px[x,y][3]>0 and not flamme(px[x,y])})
    vals_f=sorted({sum(px[x,y][:3]) for y in range(im.height) for x in range(im.width) if flamme(px[x,y])})
    for y in range(im.height):
        for x in range(im.width):
            c=px[x,y]
            if c[3]==0: continue
            if flamme(c):
                k=vals_f.index(sum(c[:3]))/max(1,len(vals_f)-1); q[x,y]=ROUGE_FLAMME[min(5,int(k*6))]+(c[3],)
            else:
                k=vals_m.index(sum(c[:3]))/max(1,len(vals_m)-1); q[x,y]=teinte(1+int(k*4.99),metal_t)+(c[3],)
    return out
for s,pre in enumerate(PRE):
    t=T_[s]; f=fe.textures(t)
    f['porte_haut'].save(f'{TX}block/{pre}airain_door_top.png'); f['porte_bas'].save(f'{TX}block/{pre}airain_door_bottom.png')
    f['trappe'].save(f'{TX}block/{pre}airain_trapdoor.png'); f['barreaux'].save(f'{TX}block/{pre}airain_bars.png')
    f['grille'].save(f'{TX}block/{pre}airain_grate.png')
    flamme_rouge(Image.open(MC+'block/lantern.png').convert('RGBA'),t).save(f'{TX}block/{pre}airain_lantern.png')
    flamme_rouge(Image.open(MC+'item/lantern.png').convert('RGBA'),t).save(f'{TX}item/{pre}airain_lantern.png')
    # chaîne (objet) : la chaîne vanilla, remontée vers les tons clairs
    im=Image.open(MC+'item/chain.png').convert('RGBA'); px=im.load(); out=im.copy(); q=out.load()
    vals=sorted({sum(px[x,y][:3]) for y in range(16) for x in range(16) if px[x,y][3]>0})
    for y in range(16):
        for x in range(16):
            if px[x,y][3]>0: q[x,y]=teinte(1+int(vals.index(sum(px[x,y][:3]))/max(1,len(vals)-1)*4.99),t)+(px[x,y][3],)
    out.save(f'{TX}item/{pre}airain_chain.png')
    # porte (objet) : les deux moitiés, réduites
    ic=Image.new('RGBA',(16,16)); ic.alpha_composite(f['porte_haut'].resize((8,8),Image.NEAREST),(4,0)); ic.alpha_composite(f['porte_bas'].resize((8,8),Image.NEAREST),(4,8))
    ic.save(f'{TX}item/{pre}airain_door.png')
# copie dans le mod (uniquement nos fichiers, jamais ceux retouchés par Liam)
DST='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/'
n=0
for sous in ('block','item'):
    for fn in os.listdir(TX+sous):
        if fn.startswith('airain_bricks') or 'airain_bricks' in fn: continue
        cible=DST+sous+'/'+fn
        shutil.copy(TX+sous+'/'+fn, cible); n+=1
print('textures copiées', n)
# seau d'airain en fusion (le seau de lave recoloré) et engrenage inachevé (l'engrenage, en partie terne)
im=Image.open(MC+'item/lava_bucket.png').convert('RGBA'); px=im.load()
for y in range(16):
    for x in range(16):
        r,g,b,a=px[x,y]
        if a and r>g+30: L=(r+g)/2; px[x,y]=(min(255,int(L*1.1+40)),min(255,int(L*0.75+20)),int(L*0.3),a)
im.save(DST+'item/molten_airain_bucket.png')
g=Image.open(DST+'item/airain_gear.png').convert('RGBA'); px=g.load()
for y in range(16):
    for x in range(16):
        r,gg,b,a=px[x,y]
        if a and (x+y)%3==0: px[x,y]=(int(r*0.55),int(gg*0.5),int(b*0.5),a)
g.save(DST+'item/incomplete_airain_gear.png')
print('seau et engrenage inachevé')
