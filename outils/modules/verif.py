import sys, math
sys.argv=['x']
exec(open('geo_modules.py').read().split('# ---------------- Java')[0])
import apercu as A
from PIL import Image
ANC = {'lanterne': (0,-7,-2), 'lunette': (0,-7,-2)}
def rend(parts, dos, niv=1):
    V = A.golem()
    for p in parts:
        for k in (p, p + '_lum'):
            for (x,y,z,w,h,d,m) in P.get(k, []):
                ax, ay, az = ANC.get(p, (0,-7,0))
                c = MAT[m][niv-1] + ((1,) if MAT[m][2] else ())
                X = x + ax; Y = y + ay; Z = z + az
                for i in range(max(1, int(round(w*2)))):
                    for j in range(max(1, int(round(h*2)))):
                        for kk in range(max(1, int(round(d*2)))):
                            A.put(V, X + i/2, Y + j/2, Z + kk/2, c)
    if dos: V = {(-x, y, -z): c for (x, y, z), c in V.items()}
    return A.rendu(V, T=4)
ims = [rend(['lanterne','canon','canon_fut','blindage','blindage_brasD','blindage_brasG'], False),
       rend(['lunette','tesla','tesla_eclairs','chaudiere'], False),
       rend(['lunette','tesla','tesla_eclairs','chaudiere'], True, 2),
       rend(['lanterne','canon','canon_fut','blindage','blindage_brasD','blindage_brasG'], True, 2)]
W = sum(i.width for i in ims); out = Image.new('RGB', (W, max(i.height for i in ims)), (32,33,38)); x = 0
for i in ims: out.paste(i, (x, 0)); x += i.width
out.save('verif.png'); print(out.size)
