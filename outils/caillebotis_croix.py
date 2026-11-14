# Caillebotis en croisillons (comme la grille d'airain) pour le sol des passerelles, escaliers, rampes.
import sys
src=open('ferronnerie.py').read(); exec(src[:src.index('OUT=')])
def epais(lignes):
    """Version plus robuste : chaque barreau diagonal gagne un pixel d'épaisseur ombré (en bas à droite)."""
    g=[list(l) for l in lignes]
    for y in range(1,15):
        for x in range(1,15):
            if lignes[y][x] in 'hW' and g[y+1][x]=='.' and 0<y+1<15: g[y+1][x]='s'
    return [''.join(r) for r in g]
VAR={'A':GRILLE,'B':epais(GRILLE)}
if __name__=='__main__':
    D='airain_tex/block/'
    for k,lig in VAR.items():
        for s_,p in enumerate(['','exposed_','weathered_','oxidized_']):
            rendre_carte(carte(lig),T[s_]).save(D+f'{p}airain_catwalk_croix{k}.png')
    print('ok')

def marche():
    """Marches d'escalier (4 px de profondeur) : croisillons épais de période 4, un rang de losanges entier par marche."""
    L=[]
    for y in range(16):
        r=''
        for x in range(16):
            k=(x+y)%4==0 or (x-y)%4==0
            r+='h' if k else ('s' if ((x+y-1)%4==0 or (x-y+1)%4==0) and y%4!=3 else '.')
        L.append(r)
    return L
if __name__=='__main__':
    for s_,p in enumerate(['','exposed_','weathered_','oxidized_']):
        rendre_carte(carte(marche()),T[s_]).save(f'airain_tex/block/{p}airain_catwalk_step.png')
    print('marches ok')
