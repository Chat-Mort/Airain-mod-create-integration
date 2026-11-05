import os, sys
from plans import *
from tableaux4 import SPEC
os.makedirs("painting6", exist_ok=True); ims = []
for nom in PLANCHES:
    w, h = SPEC[nom][:2]; im = generer(nom, w, h); assert im.size == (w*64, h*64), (nom, im.size); im.save(f"painting6/{nom}.png"); ims.append((w*h, w, nom, im))
for nom in CONSERVES:
    os.system(f"cp painting4/{nom}.png painting6/{nom}.png")
from PIL import Image
ims.sort(key=lambda t: (t[0], t[1]))
W = 1500; x = y = 10; rowh = 0; c = Image.new("RGB", (W, 5000), (36, 34, 38))
for _, _, n, im in ims:
    z = 2 if im.width <= 128 and im.height <= 128 else 1
    im = im.resize((im.width*z, im.height*z), Image.NEAREST)
    if x + im.width > W - 10: x = 10; y += rowh + 10; rowh = 0
    c.paste(im, (x, y)); x += im.width + 10; rowh = max(rowh, im.height)
c.crop((0, 0, W, y + rowh + 10)).save("/home/claude/apercus/plans_tous.png")
