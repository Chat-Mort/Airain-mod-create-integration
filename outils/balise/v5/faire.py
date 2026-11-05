"""Balise de défense, version 16 pixels : textures dessinées pixel par pixel et forme du bloc."""
import json, os
from PIL import Image
OUT = os.path.dirname(os.path.abspath(__file__))
PAL = {
  "1": (248, 214, 140), "2": (224, 176, 86), "3": (196, 142, 58), "4": (146, 98, 36), "5": (90, 56, 22), "r": (255, 242, 200),
  "o": (232, 150, 100), "O": (186, 98, 60), "q": (120, 52, 30),                       # cuivre
  "C": (238, 230, 208), "c": (196, 186, 164), "N": (40, 32, 28), "R": (206, 34, 24), "S": (150, 20, 14),   # cadran, rouge
  "g": (150, 144, 136), "G": (90, 86, 82),                                           # acier du volant
  "k": (46, 32, 18), "K": (70, 50, 28), "Y": (240, 196, 100), "y": (160, 114, 46),  # plaque sombre, emblème
  "L": (255, 236, 210), "H": (255, 132, 84), "M": (220, 44, 28), "B": (140, 16, 12), # verre de la lampe
  "f": (92, 90, 100), "F": (62, 61, 70), "e": (44, 43, 51), "E": (26, 25, 31), "b": (176, 168, 150)}      # fonte, boulon

def poser(img, x0, y0, grille):
    p = img.load()
    for y, ligne in enumerate(grille):
        for x, ch in enumerate(ligne):
            if ch != ".": p[x0+x, y0+y] = PAL[ch] + (255,)

def plaque12x8():
    return ["122222222221",
            "2r3333333r34",
            "233333333334",
            "233333333334",
            "233333333334",
            "233333333334",
            "2r3333333r34",
            "455555555555"]
MOTIFS = {
  "nord": ["..4444..",       # manomètre
           ".4CCCR4.",
           ".4CCRC4.",
           ".4CNCC4.",
           ".4cCCc4.",
           "..4444.."],
  "sud":  ["44oO4444",       # engrenage de cuivre dans son logement
           "4ooooOq4",
           "44oqqO44",
           "44OqqO44",
           "4oOOOqq4",
           "444Oq444"],
  "est":  ["..RRRR..",       # vanne : volant rouge
           ".R.RS.S.",
           ".RRggSS.",
           ".RRGGSS.",
           ".S.SS.S.",
           "..SSSS.."],
  "ouest":[".kkkkkk.",       # plaque sombre : la roue couronnée de l'Empire
           ".kYkkYk.",
           ".kYYYYk.",
           ".kkyykk.",
           ".kyKKyk.",
           ".kkyykk."]}
for face, motif in MOTIFS.items():
    t = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    poser(t, 0, 0, plaque12x8())
    poser(t, 2, 1, motif)
    t.save(f"{OUT}/balise_corps_{face}.png")

t = Image.new("RGBA", (16, 16), (0, 0, 0, 0))          # dessus du corps 12 x 12
poser(t, 0, 0, ["122222222221",
                "2r3333333r34",
                "233444444334",
                "234333333234",
                "234335533234",
                "234354453234",
                "234354453234",
                "234335533234",
                "234333333234",
                "233222222334",
                "2r3333333r34",
                "455555555555"])
t.save(f"{OUT}/balise_corps_dessus.png")

t = Image.new("RGBA", (16, 16), (0, 0, 0, 0))          # lampe, chapeau, col
poser(t, 0, 0, ["122221",            # côté de la lampe 6 x 4 : verre rouge entre deux bagues de laiton
                "3HLLH4",
                "3MHHM4",
                "455554"])
poser(t, 0, 4, ["122221",            # dessus de la lampe 6 x 6 : chapeau de laiton, évent, verre visible autour
                "2HMMH4",
                "2M55M4",
                "2M55M4",
                "2HMMH4",
                "455554"])
poser(t, 0, 10, ["455554", "5BMMB5", "5MHHM5", "5MHHM5", "5BMMB5", "555555"])   # dessous
poser(t, 8, 0, ["oq", "Oq", "1y"])   # côté de la tige de cuivre 2 x 3, collier de laiton en bas
poser(t, 8, 3, ["oO", "Oq"])         # dessus de la tige
t.save(f"{OUT}/balise_lampe.png")

t = Image.new("RGBA", (16, 16), (0, 0, 0, 0))          # socle de fonte : côté 14 x 1, dessus 14 x 14
poser(t, 0, 0, ["ffffffffffffff", "FbFFFFFFFFFFbE"])
poser(t, 0, 2, ["ffffffffffffff",
                "fbFFFFFFFFFFbe",
                "fFeeeeeeeeeeFE",
                "fFeFFFFFFFFfFE",
                "fFeFFFFFFFFfFE",
                "fFeFFFFFFFFfFE",
                "fFeFFFFFFFFfFE",
                "fFeFFFFFFFFfFE",
                "fFeFFFFFFFFfFE",
                "fFeFFFFFFFFfFE",
                "fFeFFFFFFFFfFE",
                "fFfffffffffffE",
                "fbFFFFFFFFFFbE",
                "eEEEEEEEEEEEEE"])
t.save(f"{OUT}/balise_socle.png")

def cotes(uv, tex=None, par_face=None, dessus=None, dessous=None):
    f = {d: {"texture": (par_face or {}).get(d, tex), "uv": uv} for d in ("north", "south", "east", "west")}
    if dessus: f["up"] = {"texture": dessus[0], "uv": dessus[1]}
    if dessous: f["down"] = {"texture": dessous[0], "uv": dessous[1]}
    return f
modele = {"parent": "minecraft:block/block",
  "textures": {"particle": "kubejs:block/balise_corps_nord", "socle": "kubejs:block/balise_socle",
               "nord": "kubejs:block/balise_corps_nord", "sud": "kubejs:block/balise_corps_sud",
               "est": "kubejs:block/balise_corps_est", "ouest": "kubejs:block/balise_corps_ouest",
               "dessus": "kubejs:block/balise_corps_dessus", "lampe": "kubejs:block/balise_lampe"},
  "elements": [
    {"from": [1, 0, 1], "to": [15, 1, 15], "faces": cotes([0, 1, 14, 2], "#socle", dessus=("#socle", [0, 2, 14, 16]), dessous=("#socle", [0, 2, 14, 16]))},
    {"from": [2, 1, 2], "to": [14, 9, 14], "faces": cotes([0, 0, 12, 8], par_face={"north": "#nord", "south": "#sud", "east": "#est", "west": "#ouest"},
                                                         dessus=("#dessus", [0, 0, 12, 12]))},
    {"from": [7, 9, 7], "to": [9, 12, 9], "faces": cotes([8, 0, 10, 3], "#lampe", dessus=("#lampe", [8, 3, 10, 5]))},
    {"from": [5, 12, 5], "to": [11, 16, 11], "faces": cotes([0, 0, 6, 4], "#lampe", dessus=("#lampe", [0, 4, 6, 10]), dessous=("#lampe", [0, 10, 6, 16]))}]}
json.dump(modele, open(f"{OUT}/balise_defense_forme.json", "w"), indent=2)
