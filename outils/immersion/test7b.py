from PIL import Image
from plans7 import planche
import sujets_b as B
SUJ = {
 "b": ("BEAM ENGINE", 1.1, B.balancier, [(0.5, 0.22, "PIVOT"), (0.2, 0.68, "CYLINDER"), (0.8, 0.66, "FLYWHEEL"), (0.62, 0.42, "GOVERNOR")], None),
 "t": ("AUTOMATON HEAD", 1, B.tete, [(0.37, 0.44, "OPTIC"), (0.77, 0.48, "EAR GEAR"), (0.5, 0.66, "GRILLE"), (0.5, 0.9, "NECK")], None),
 "s": ("DIVING HELMET", 1, B.scaphandre, [(0.5, 0.44, "FACEPLATE"), (0.76, 0.42, "SIDE PORT"), (0.28, 0.88, "WING NUT"), (0.8, 0.27, "AIR INLET")], None),
 "c": ("BOILER", 1.15, B.chaudiere, [(0.24, 0.08, "STACK"), (0.84, 0.12, "GAUGE"), (0.84, 0.72, "FIREBOX"), (0.4, 0.58, "SHELL")], None),
 "d": ("AIRSHIP", 1.3, B.dirigeable, [(0.5, 0.36, "ENVELOPE"), (0.48, 0.8, "GONDOLA"), (0.81, 0.71, "ENGINE"), (0.92, 0.18, "FIN")], None),
 "m": ("POCKET WATCH", 0.85, B.montre, [(0.5, 0.13, "CROWN"), (0.47, 0.44, "MOVEMENT"), (0.5, 0.75, "SECONDS"), (0.82, 0.58, "CASE")], None),
 "a": ("MECHANICAL ARM", 1.1, B.bras, [(0.21, 0.68, "SHOULDER"), (0.47, 0.3, "ELBOW"), (0.92, 0.27, "CLAW"), (0.33, 0.75, "PISTON")], None),
 "p": ("CAPSULE", 0.85, B.capsule, [(0.5, 0.34, "WINDOW"), (0.5, 0.695, "PLATE"), (0.86, 0.75, "FEED"), (0.5, 0.92, "BASE")], None),
 "u": ("STEAM TURBINE", 1.2, B.turbine, [(0.33, 0.25, "INLET"), (0.55, 0.45, "BLADES"), (0.67, 0.92, "EXHAUST"), (0.92, 0.56, "BEARING")], None),
 "l": ("DIVING BELL", 0.95, B.cloche, [(0.5, 0.3, "PORTHOLE"), (0.5, 0.84, "SKIRT"), (0.5, 0.1, "LIFT EYE"), (0.16, 0.96, "BALLAST")], None),
 "w": ("WINDMILL", 0.95, B.moulin, [(0.42, 0.32, "HUB"), (0.2, 0.12, "SAIL"), (0.5, 0.73, "GALLERY"), (0.83, 0.4, "FANTAIL")], None),
 "x": ("TRIPLE ENGINE", 1, B.triple, [(0.5, 0.28, "BOILER"), (0.5, 0.78, "SPINE"), (0.5, 0.55, "BEAM"), (0.22, 0.34, "HEAD")], None),
}
ims = [planche(128, 128, SUJ, n, i) for i, n in enumerate(SUJ)]
W = 1600; x = y = 8; rh = 0; c = Image.new("RGB", (W, 1400), (36, 34, 38))
for im in ims:
    im = im.resize((im.width*2, im.height*2), Image.NEAREST)
    if x + im.width > W: x = 8; y += rh + 8; rh = 0
    c.paste(im, (x, y)); x += im.width + 8; rh = max(rh, im.height)
c.crop((0, 0, W, y + rh + 8)).save("/home/claude/apercus/v7_test_b.png")
