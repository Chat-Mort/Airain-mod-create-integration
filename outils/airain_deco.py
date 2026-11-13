# Porte, trappe, chaîne et lanterne d'airain, aux quatre stades.
import math
from PIL import Image
exec(open('airain_luxe.py').read().split("STADES=['','exposed_'")[0])
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex'
MC='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/'
def cadre(c,x0,y0,x1,y1,base=3.0):
    plaque(x0,y0,x1,y1,c,base,0.6)
def porte_haut():
    c=vide(); cadre(c,0,0,15,15,3.2)
    # fenêtre à barreaux en haut
    for y in range(3,10):
        for x in range(3,13):
            c[y][x]=None if x not in (5,8,10) or y in () else (4.6 if x in (5,8) else 2.0)
    for x in range(3,13): c[2][x]=1.2; c[10][x]=5.0
    for y in range(2,11): c[y][2]=1.2; c[y][13]=5.0
    cadre(c,3,11,12,15,3.0)
    for x in (2,3): c[15][x]=1.2
    return c
def porte_bas():
    c=vide(); cadre(c,0,0,15,15,3.2)
    cadre(c,3,1,12,7,3.0); cadre(c,3,9,12,14,3.0)
    c[2][12]=6.0; c[3][12]=4.0; c[2][11]=5.0; c[3][11]=1.4      # poignée
    return c
def trappe():
    c=vide(); cadre(c,0,0,15,15,3.2)
    for y in range(3,13):
        for x in range(3,13):
            if (x-3)%3==2 or (y-3)%3==2: c[y][x]=None          # ajours
            else: c[y][x]=3.4+reflet(x,y,0.4)
    for (x,y) in [(1,1),(14,1),(1,14),(14,14)]: c[y][x]=6.0
    return c
def recolore(src, t, garder_flamme=False):
    im=Image.open(src).convert('RGBA'); px=im.load(); out=im.copy(); q=out.load()
    metal=lambda c: c[3]>0 and (not garder_flamme or not (c[0]>c[2]+40))
    vals=sorted({sum(px[x,y][:3]) for y in range(im.height) for x in range(im.width) if metal(px[x,y])})
    for y in range(im.height):
        for x in range(im.width):
            if metal(px[x,y]):
                k=vals.index(sum(px[x,y][:3]))/max(1,len(vals)-1)
                q[x,y]=teinte(int(k*5.99)+ (1 if k>0.85 else 0),t)+(px[x,y][3],)
    return out
def recolore_clair(src,t):
    # la chaîne vanilla est très sombre : on la remonte vers les tons moyens et clairs
    im=Image.open(src).convert('RGBA'); px=im.load(); out=im.copy(); q=out.load()
    vals=sorted({sum(px[x,y][:3]) for y in range(im.height) for x in range(im.width) if px[x,y][3]>0})
    for y in range(im.height):
        for x in range(im.width):
            if px[x,y][3]>0:
                k=vals.index(sum(px[x,y][:3]))/max(1,len(vals)-1)
                q[x,y]=teinte(1+int(k*4.99),t)+(px[x,y][3],)
    return out
for s,pre in enumerate(['','exposed_','weathered_','oxidized_']):
    t=T[s]
    rendre_carte(porte_haut(),t).save(f'{OUT}/block/{pre}airain_door_top.png')
    rendre_carte(porte_bas(),t).save(f'{OUT}/block/{pre}airain_door_bottom.png')
    rendre_carte(trappe(),t).save(f'{OUT}/block/{pre}airain_trapdoor.png')
    recolore_clair(MC+'block/chain.png',t).save(f'{OUT}/block/{pre}airain_chain.png')
    recolore(MC+'block/lantern.png',t,True).save(f'{OUT}/block/{pre}airain_lantern.png')
    # icône de la porte (objet) : les deux moitiés réduites, comme les portes de Minecraft
    h=rendre_carte(porte_haut(),t); b=rendre_carte(porte_bas(),t)
    ic=Image.new('RGBA',(16,16)); ic.alpha_composite(h.resize((8,8),Image.NEAREST),(4,0)); ic.alpha_composite(b.resize((8,8),Image.NEAREST),(4,8))
    ic.save(f'{OUT}/item/{pre}airain_door.png')
print('ok')
