"""Textures du fluide huile (KubeJS attend kubejs:block/huile_still et huile_flow), en niveaux de gris : la teinte du fluide les colore."""
import json, math, random
from PIL import Image
B = "/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/block/"
def anim(taille, frames, nom, vitesse):
    im = Image.new("RGBA", (taille, taille * frames)); px = im.load(); rnd = random.Random(nom)
    bruit = [[rnd.random() for _ in range(taille)] for _ in range(taille)]
    for f in range(frames):
        for y in range(taille):
            for x in range(taille):
                yy = (y + f * vitesse) % taille
                v = 0.55 * bruit[int(yy)][x] + 0.45 * (0.5 + 0.5 * math.sin((x * 0.6 + yy * 0.9 + f * 0.5)))
                g = int(150 + 105 * v)
                if v > 0.86: g = 255                       # reflets
                px[x, y + f * taille] = (g, g, g, 255)
    im.save(B + nom + ".png")
    json.dump({"animation": {"frametime": 3}}, open(B + nom + ".png.mcmeta", "w"))
anim(16, 32, "huile_still", 0.5)
anim(32, 32, "huile_flow", 1)
print("ok")
