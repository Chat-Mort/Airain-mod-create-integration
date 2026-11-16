#!/usr/bin/env python3
"""1.61 : rouge impérial « cramoisi » pour la patine de l'airain.

Décale teinte, saturation et luminosité des textures terni, vieilli et rouge impérial, pixel par pixel : les motifs ne
bougent pas, le stade neuf ne change pas. Les pixels déjà rouges dans la texture neuve (flamme des lanternes, voyants)
restent tels quels. À relancer après les générateurs de textures ; un fichier déjà traité est reconnu à son empreinte
(outils/rouge_imperial.json) et n'est pas décalé deux fois.
Usage : python3 outils/rouge_imperial.py
"""
import colorsys, hashlib, json, os, glob
from PIL import Image

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src/main/resources/assets/airain/textures')
MANIFESTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rouge_imperial.json')
# (décalage de teinte en degrés, saturation ×, valeur ×) : terni, vieilli, rouge impérial
STADES = {'exposed_': (-5, 1.08, 0.98), 'weathered_': (-14, 1.2, 0.92), 'oxidized_': (-21, 1.4, 0.82)}

def empreinte(p): return hashlib.sha1(open(p, 'rb').read()).hexdigest()
def rouge_voulu(c):
    r, g, b, a = c
    if a == 0: return False
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return s > 0.4 and (h < 15 / 360 or h > 340 / 360)

faits = json.load(open(MANIFESTE)) if os.path.exists(MANIFESTE) else {}
n = 0
for p in sorted(glob.glob(os.path.join(RACINE, '**/*.png'), recursive=True)):
    nom = os.path.basename(p)
    pre = next((k for k in STADES if nom.startswith(k)), None)
    if pre is None: continue
    cle = os.path.relpath(p, RACINE)
    if faits.get(cle) == empreinte(p): continue          # déjà au nouveau rouge
    dh, ks, kv = STADES[pre]
    neuf_p = os.path.join(os.path.dirname(p), nom[len(pre):])
    neuf = Image.open(neuf_p).convert('RGBA') if os.path.exists(neuf_p) else None
    im = Image.open(p).convert('RGBA'); px = im.load()
    nx = neuf.load() if neuf is not None and neuf.size == im.size else None
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0: continue
            if nx is not None and rouge_voulu(nx[x, y]): continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s < 0.08: continue                           # gris et blancs neutres (verre, reflets)
            h = (h + dh / 360) % 1; s = min(1, s * ks); v = min(1, v * kv)
            R, G, B = colorsys.hsv_to_rgb(h, s, v)
            px[x, y] = (int(R * 255 + .5), int(G * 255 + .5), int(B * 255 + .5), a)
    im.save(p)
    faits[cle] = empreinte(p); n += 1
json.dump(faits, open(MANIFESTE, 'w'), indent=1, sort_keys=True)
print('rouge impérial :', n, 'textures recolorées')
