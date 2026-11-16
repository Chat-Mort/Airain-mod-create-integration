# Police « impériale » du tableau émaillé : sérif condensée, tramée à 2× la résolution de la police de Minecraft (16 px de haut).
import sys
from PIL import Image, ImageDraw, ImageFont
CH=''.join(chr(c) for c in range(32,127))+"àâäçéèêëîïôöùûüÿœæÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ«»°·—’…€×"
def rendre(fichier,taille,seuil=120,cell=16,base=12):
    f=ImageFont.truetype(fichier,taille)
    cols=16; rows=(len(CH)+cols-1)//cols
    W=cols*cell; im=Image.new('RGBA',(W,rows*cell),(0,0,0,0))
    lignes=[]
    for r in range(rows):
        lignes.append(CH[r*cols:(r+1)*cols].ljust(cols,'\u0000'))
    for i,c in enumerate(CH):
        if c==' ': continue
        g=Image.new('L',(cell*2,cell*2),0); d=ImageDraw.Draw(g)
        d.text((2,base),c,font=f,fill=255,anchor='ls')
        g=g.point(lambda v:255 if v>seuil else 0)
        bb=g.getbbox()
        if not bb: continue
        x0=bb[0]; gl=g.crop((x0,0,min(x0+cell,g.width),cell))
        X=(i%cols)*cell; Y=(i//cols)*cell
        im.paste((255,255,255,255),(X,Y),gl)
    return im,lignes
if __name__=='__main__':
    im,l=rendre(sys.argv[1],int(sys.argv[2]))
    im.save('imperiale.png')
