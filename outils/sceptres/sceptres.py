from PIL import Image
A = '/mnt/user-data/attachments/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/'
def propre(im):
    """Retire le halo : presque transparent -> transparent, le reste plein."""
    px = im.load()
    for x in range(im.width):
        for y in range(im.height):
            r, g, b, a = px[x, y]
            px[x, y] = (0, 0, 0, 0) if a < 128 else (r, g, b, 255)
    return im
def recolorer(im, table):
    px = im.load()
    for x in range(im.width):
        for y in range(im.height):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in table: px[x, y] = table[(r, g, b)] + (255,)
    return im
# ---- impérial : or et nacre (au lieu d'or et rouge), étoile au cœur du rouage
imp = propre(Image.open(A + 'b86600db-image.png').convert('RGBA'))
recolorer(imp, {(228,148,16): (226,184,84), (149,65,3): (150,110,38), (191,110,7): (190,148,60), (250,237,107): (255,238,176),
                (243,185,31): (248,212,118), (242,183,30): (248,212,118), (242,158,18): (226,184,84), (242,207,53): (255,228,150), (241,158,18): (226,184,84),
                (189,23,4): (232,235,244), (132,5,1): (190,194,212)})
px = imp.load()
for (x, y, c) in ((27, 4, (240,250,255)), (26, 4, (150,212,255)), (28, 4, (150,212,255)), (27, 3, (150,212,255)), (27, 5, (150,212,255))):
    px[x, y] = c + (255,)
imp.save('sceptre_imperial.png')
# ---- arcanique : palette de l'Écho (violet profond, lavande), Écho primordial au creux de la fourche
arc = propre(Image.open(A + 'e09184c1-image.png').convert('RGBA'))
recolorer(arc, {(0,0,0): (14,10,20), (180,81,181): (150,112,220), (86,39,87): (58,30,96), (200,90,201): (186,156,255), (163,73,164): (122,84,190)})
px = arc.load()
for (x, y, c) in ((24, 8, (246,240,255)), (25, 8, (214,196,255)), (23, 8, (58,30,96)), (26, 8, (58,30,96)), (24, 9, (58,30,96)), (25, 9, (58,30,96))):
    px[x, y] = c + (255,)
arc.save('sceptre_arcanique.png')
o = Image.new('RGBA', (1060, 340), (31, 32, 36, 255))
for i, im in enumerate((Image.open(A + 'b86600db-image.png').convert('RGBA'), imp, arc)):
    g = im.resize((320, 320), Image.NEAREST); o.paste(g, (10 + i * 350, 10), g)
o.save('sceptres_avant_apres.png')
