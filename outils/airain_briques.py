# Briques d'airain (4 stades) et barreaux d'airain, même style poli que le reste.
import math
from PIL import Image
exec(open('airain_luxe.py').read().split("STADES=['','exposed_'")[0])
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex'
def briques():
    c=vide()
    for y in range(16):
        rang=y//4; ly=y%4; dec=0 if rang%2==0 else 4
        for x in range(16):
            lx=(x+dec)%8
            if ly==3 or lx==7: c[y][x]=0.9                              # joint creux
            else:
                v=3.0+(1.8 if ly==0 else 0)+(0.8 if lx==0 else 0)-(0.9 if ly==2 else 0)-(0.4 if lx==6 else 0)
                v+=reflet(lx,ly,0.5)*0.8
                c[y][x]=v
    return c
def barreaux():
    c=[[None]*16 for _ in range(16)]
    for y in range(16):
        for x in (1,2,7,8,13,14):
            c[y][x]=(4.6 if x in (1,7,13) else 2.0)
        if y in (0,15):
            for x in range(16): c[y][x]=4.8 if y==0 else 1.6
    for x in (1,7,13):
        for y in (4,11): c[y][x]=6.0
    return c
for s,pre in enumerate(['','exposed_','weathered_','oxidized_']):
    rendre_carte(briques(),T[s]).save(f'{OUT}/block/{pre}airain_bricks.png')
    rendre_carte(barreaux(),T[s]).save(f'{OUT}/block/{pre}airain_bars.png')
print('ok')
