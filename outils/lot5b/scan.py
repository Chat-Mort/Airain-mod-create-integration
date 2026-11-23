import sys
from PIL import Image
O = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/'
im = Image.open(O + sys.argv[1] + '.png').convert('RGBA'); p = im.load()
for a in sys.argv[2:]:
    k, v = a[0], a[1:]; v, rng = (v.split(':') + [''])[:2]
    v = int(v); r0, r1 = (map(int, rng.split('-')) if rng else (0, 256))
    out = []; prev = None
    for t in range(r0, r1):
        c = p[t, v] if k == 'y' else p[v, t]
        if c != prev: out.append('%d:%02x%02x%02x%s' % (t, c[0], c[1], c[2], '' if c[3] == 255 else '/%d' % c[3])); prev = c
    print(a, ' '.join(out))
