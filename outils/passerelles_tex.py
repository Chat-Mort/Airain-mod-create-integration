# Textures des passerelles : caillebotis (plancher ajouré) et échelle, dans l'airain poli.
from PIL import Image
exec(open('airain_luxe.py').read().split("STADES=['','exposed_'")[0])
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex/block/'
def caillebotis():
    c=[[None]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if x in (0,15) or y in (0,15): c[y][x]=4.8 if (x==0 or y==0) else 1.6
            elif x%3==0: c[y][x]=3.6+reflet(x,y,0.4)          # lames porteuses
            elif y%5==0: c[y][x]=2.6                           # entretoises
    return c
def echelle():
    c=[[None]*16 for _ in range(16)]
    for y in range(16):
        for x in (1,2,13,14): c[y][x]=4.6 if x in (1,13) else 2.2
        if y%4==1:
            for x in range(3,13): c[y][x]=4.8
            for x in range(3,13): c[y+1][x]=2.0
    return c
for s,pre in enumerate(['','exposed_','weathered_','oxidized_']):
    rendre_carte(caillebotis(),T[s]).save(OUT+pre+'airain_catwalk.png')
    rendre_carte(echelle(),T[s]).save(OUT+pre+'airain_ladder.png')
print('ok')
