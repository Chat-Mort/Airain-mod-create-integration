from PIL import Image
P = {".": None, "k": (34, 30, 30), "1": (70, 66, 66), "2": (104, 100, 98), "3": (140, 136, 130), "4": (182, 178, 170), "5": (220, 216, 206),
     "r": (110, 52, 28), "o": (156, 82, 40), "y": (196, 124, 58), "b": (120, 84, 30), "B": (176, 132, 52), "L": (220, 182, 92), "W": (250, 230, 160),
     "d": (24, 18, 12), "g": (52, 40, 24), "G": (84, 66, 38), "c": (150, 96, 60), "C": (196, 132, 84)}
def img(rows):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if P.get(ch): im.putpixel((x, y), P[ch] + (255,))
    return im
ferraille = [
"................",
"................",
"......kk........",
".....k34k.......",
"....k3451k..kk..",
"...k2r451k.k43k.",
"..k23o4k1kk452k.",
"..k2or2k..k3o2k.",
".k1kk2r1k.kro1k.",
".k45kk11kkk21k..",
"k3452kk2345k1k..",
"k2o432k1y4321kk.",
".k2r21kk2o33k45k",
"..kk11k.k1r2k21k",
"....kk...kkk.kk.",
"................"]
huile = [
"................",
".........kk.....",
"........kLWk....",
".......kLBk.....",
"......kLBk......",
"..kkkkkBbk......",
".kGBLLLBbk......",
"kgBLWWLBBbk.....",
"kgBLLLBBBbkkk...",
"kgBBBBBBBbk.kk..",
"kgbBBBBBbbk..k..",
"kgbbbbbbbbk.kk..",
"kgddgggdddkkk...",
"kgBBBBBBBbk.....",
".kkkkkkkkk......",
"................"]
rouage = [
"................",
"......kkk.......",
"..kk.kc Ck..k...",
".kCck kCck.kCk..",
".kccCkkcCCkCck..",
"..kCcCccCccCk...",
".kkcCck..kccCk..",
"kCcCck....kcCkk.",
"kccck......kk...",
".kkCck....k.....",
"..kcCck..kCk....",
".kccCcCccCcck...",
".kCk.kcCck.kCk..",
"..k..kCCk...k...",
"......kk........",
"................"]
rouage = [r.replace(" ", ".") for r in rouage]
base = "/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/"
for n, r in (("ferraille", ferraille), ("huile_machine", huile), ("rouage_brise", rouage)):
    im = img(r); im.save(base + n + ".png"); im.resize((160, 160), Image.NEAREST).save(f"butin/{n}_x10.png")
c = Image.new("RGBA", (500, 170), (60, 60, 64, 255))
for i, n in enumerate(("ferraille", "huile_machine", "rouage_brise")): c.paste(Image.open(f"butin/{n}_x10.png"), (5 + i*165, 5), Image.open(f"butin/{n}_x10.png"))
c.save("/home/claude/apercus/butin_items.png")
