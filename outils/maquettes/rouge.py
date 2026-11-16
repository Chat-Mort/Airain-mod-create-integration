# Nouveau rouge impérial : décalage de teinte et de saturation par stade, appliqué pixel par pixel (les motifs ne bougent pas).
import colorsys
from PIL import Image
# (décalage de teinte en degrés, saturation ×, valeur ×) pour terni, vieilli, rouge impérial
VARIANTES={'A':[(-4,1.06,1.0),(-11,1.15,0.97),(-16,1.32,0.94)],
           'B':[(-5,1.08,0.98),(-14,1.2,0.92),(-21,1.4,0.82)]}
def recolorer(im,stade,v):
    if stade==0: return im.copy()
    dh,ks,kv=VARIANTES[v][stade-1]
    im=im.convert('RGBA'); out=im.copy(); p=im.load(); q=out.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=p[x,y]
            if a==0: continue
            h,s,vv=colorsys.rgb_to_hsv(r/255,g/255,b/255)
            if s<0.08: q[x,y]=(r,g,b,a); continue      # gris/blanc purs (verre, reflets neutres) : laissés tels quels
            h=(h+dh/360)%1; s=min(1,s*ks); vv=min(1,vv*kv)
            R,G,B=colorsys.hsv_to_rgb(h,s,vv); q[x,y]=(int(R*255+.5),int(G*255+.5),int(B*255+.5),a)
    return out
