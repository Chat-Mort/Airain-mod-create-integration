exec(open('arcane2.py').read().split("def vue(")[0])
def redingote(V):
    """Option C avec la capuche de A : redingote arcanique ajustée, pans fendus jusqu'à mi-cuisse, fermoirs d'argent."""
    def capuche(x,y,z,w,h,d):
        if z == d-1 and 1 <= y <= 6 and 1 <= x <= w-2: return None if y in (2, 3) and x in (2, 3, 6, 7) else F1
        if z == d-1 and y == 7: return F1
        if y >= h-2 and (x + z) % 4 == 0: return V3
        return V1 if (x + y + z) % 5 else V2
    boite(V, -5, 23, -5, 5, 34, 5, capuche)
    for k in range(4): V[(-1 + (k % 2), 34 + k // 2, -5)] = V2
    diademe(V, sacre=True)
    # redingote : torse ajusté, revers, rangée de fermoirs d'argent, broderies lumineuses
    def torse(x,y,z,w,h,d):
        if z == d-1:
            if x in (w//2 - 1, w//2): return LV if y % 3 == 1 else F1            # fermoirs sur la fente
            if y >= h - 3 and x in (w//2 - 2, w//2 + 1): return V3                 # revers du col
            if x in (0, w-1): return (12,8,18)
            if (x + y) % 6 == 0: return LV
            return V1 if (x + y) % 3 else V2
        if z == 0: return V1 if (x + y) % 3 else V2
        return F2
    boite(V, -5, 11, -3, 5, 25, 3, torse)
    for x in range(-4, 4): V[(x, 25, 3)] = (12,8,18); V[(x, 26, 2)] = V2; V[(x, 26, -3)] = V2     # col haut
    for x in range(-5, 5): V[(x, 13, 3)] = (12,8,18); V[(x, 13, -3)] = (12,8,18)                          # ceinture d'argent
    V[(-1, 13, 4)] = LV2; V[(0, 13, 4)] = LV2                                                # boucle : l'Écho primordial
    # pans : derrière et sur les côtés, fendus devant, jusqu'à mi-cuisse
    for y in range(5, 13):
        e = 1 if y < 9 else 0
        for x in range(-5 - e, 5 + e):
            V[(x, y, -3 - e)] = (12,8,18) if y == 5 else (LV if (x + y) % 7 == 0 else (V2 if (x + y) % 3 else V1))
        for z in range(-3 - e, 3):
            for x in (-5 - e, 4 + e):
                V[(x, y, z)] = (12,8,18) if y == 5 else (V1 if (z + y) % 3 else V2)
        for x in (-5 - e, -4 - e, 3 + e, 4 + e):                                            # devant : seulement les bords
            V[(x, y, 3)] = (12,8,18) if y == 5 or x in (-5 - e, 4 + e) else V2
    for s in (1, -1):
        x0 = 4 if s == 1 else -9
        boite(V, x0, 11, -3, x0+5, 25, 3, lambda x,y,z,w,h,d: (12,8,18) if y in (1, 2) else (LV if y == 6 and (x + z) % 2 == 0 else (V1 if (x+y) % 4 else V2)))
        boite(V, x0 - (1 if s == -1 else 0), 23, -4, x0+5+(1 if s == 1 else 0), 26, 4, lambda x,y,z,w,h,d: (30,22,40) if y == h-1 else ((12,8,18) if (x+z) % 2 else F2))
    # chausses sombres et bottines à bout d'argent
    for x0 in (-5, 0):
        boite(V, x0, 3, -3, x0+5, 13, 3, lambda x,y,z,w,h,d: F2 if (x+y) % 4 else V1)
        boite(V, x0, -1, -3, x0+5, 4, 4, lambda x,y,z,w,h,d: (12,8,18) if y == h-1 else (F1 if y == 0 else ((30,22,40) if z == d-1 and y == 1 else F2)))

def vue(f, dos=False, T=7):
    V = {}; corps(V); f(V)
    if dos: V = {(-x, y, -z): c for (x, y, z), c in V.items()}
    return rendu(V, T=T)
cas = [("Redingote arcanique", redingote, False), ("… de dos", redingote, True)]
ims = [vue(f, d) for _, f, d in cas]
font = ImageFont.truetype(FB, 22)
cw = max(i.width for i in ims) + 80; ch = max(i.height for i in ims) + 50
out = Image.new('RGB', (cw * 2, ch), (32, 33, 38)); dr = ImageDraw.Draw(out)
for n, ((t, _, _), im) in enumerate(zip(cas, ims)):
    out.paste(im, (n * cw + (cw - im.width) // 2, 5))
    dr.text((n * cw + cw // 2 - dr.textlength(t, font=font) / 2, ch - 38), t, fill=(200, 180, 255), font=font)
out.save('apercu_redingote.png'); print(out.size)
