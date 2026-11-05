import sys
from PIL import Image
from plans7 import planche
import sujets_a as A
SUJ = {
 "COGWHEEL": ("COGWHEEL", 1, A.rouage, [], None), "VALVE": ("VALVE", 1, A.vanne, [], None), "GAUGE": ("GAUGE", 0.9, A.manometre, [], None),
 "BULB": ("BULB", 0.75, A.ampoule, [], None), "SPRING": ("SPRING", 0.75, A.ressort, [], None), "GOGGLES": ("GOGGLES", 1.6, A.lunettes, [], None),
 "KEY": ("KEY", 0.7, A.cle, [], None), "BOLT": ("BOLT", 0.7, A.boulon, [], None),
 "LAMP": ("LAMP POST", 0.4, A.reverbere, [], None), "TESLA": ("TESLA COIL", 0.42, A.tesla, [], None), "AUTO": ("AUTOMATON", 0.42, A.automate, [], None),
 "LOCO": ("LOCOMOTIVE", 2.2, A.locomotive, [], None), "CAR": ("STEAM CAR", 2.1, A.voiture, [], None), "SUB": ("SUBMARINE", 2.6, A.sousmarin, [], None),
 "VELO": ("VELOCIPEDE", 1.9, A.velocipede, [], None), "SCOPE": ("TELESCOPE", 2.0, A.lunette, [], None),
}
tailles = {"LAMP": (64, 128), "TESLA": (64, 128), "AUTO": (64, 128), "LOCO": (128, 64), "CAR": (128, 64), "SUB": (128, 64), "VELO": (128, 64), "SCOPE": (128, 64)}
ims = [planche(*tailles.get(n, (64, 64)), SUJ, n, i) for i, n in enumerate(SUJ)]
W = 1400; x = y = 8; rh = 0; c = Image.new("RGB", (W, 1200), (36, 34, 38))
for im in ims:
    im = im.resize((im.width*3, im.height*3), Image.NEAREST)
    if x + im.width > W: x = 8; y += rh + 8; rh = 0
    c.paste(im, (x, y)); x += im.width + 8; rh = max(rh, im.height)
c.crop((0, 0, W, y + rh + 8)).save("/home/claude/apercus/v7_test_a.png")
