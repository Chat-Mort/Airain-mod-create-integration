exec(open('v5.py').read().split('L = [("Empire · A')[0])
def disque(V, cx, cz, y0, y1, r0, r1, c):
    for X in range(round((cx - r1 - 1) * R), round((cx + r1 + 1) * R)):
        for Z in range(round((cz - r1 - 1) * R), round((cz + r1 + 1) * R)):
            d = math.hypot(X / R + .25 - cx, Z / R + .25 - cz)
            if r0 <= d <= r1:
                for Y in range(round(y0 * R), round(y1 * R)): V[(X, Y, Z)] = c
def eclat(V, cx, cy, cz, h, c):
    for k in range(int(h * 2)):
        t = k / 2; w = 1.2 * (1 - abs(t - h / 2) / (h / 2 + .01))
        if w > 0.2: bx(V, cx - w, cy + t, cz - w, cx + w, cy + t + .5, cz + w, c, 0)
# zone 3x3 : x -16..32, z -48..0 (devant la borne qui occupe x 0..16, z 0..16)
def scene_empire():
    V = babbage()
    bx(V, -16, 0, -48, 32, 1, 0, WH)
    for (a, b, c_, d) in ((-16, -48, 32, -46), (-16, -2, 32, 0), (-16, -48, -14, 0), (30, -48, 32, 0)): bx(V, a, 1, b, c_, 1.5, d, RED, 0)
    for (a, b, c_, d) in ((-16, -48, 32, -47), (-16, -1, 32, 0), (-16, -48, -15, 0), (31, -48, 32, 0)): bx(V, a, 1, b, c_, 1.6, d, GOLD, 0)
    disque(V, 8, -24, 1, 1.5, 9, 11, RED); disque(V, 8, -24, 1, 1.5, 3, 4.5, GOLD)            # cible de largage
    bx(V, 7, 1, -33, 9, 1.5, -15, GOLD, 0); bx(V, -1, 1, -25, 17, 1.5, -23, GOLD, 0)
    # dents de rouage sur les 4 bords
    for k in range(-14, 30, 3): bx(V, k, 1, -3, k + 1.5, 2.2, -1.5, BRASS, 0); bx(V, k, 1, -46.5, k + 1.5, 2.2, -45, BRASS, 0)
    for k in range(-44, -3, 3): bx(V, -14.5, 1, k, -13, 2.2, k + 1.5, BRASS, 0); bx(V, 29, 1, k, 30.5, 2.2, k + 1.5, BRASS, 0)
    # gauche : chaudière + cheminée + manomètre
    cylY(V, -8, 8, 6, 0, 14, IRON2); cylY(V, -8, 8, 6.4, 3, 4, BRASS); cylY(V, -8, 8, 6.4, 10, 11, BRASS)
    cylY(V, -8, 8, 1.6, 14, 34, IRON); cylY(V, -8, 8, 2.2, 33, 35, BRASS)
    anneau(V, -8, 8, 1.4, 2, 0, 2.2, WH); anneau(V, -8, 8, 1.4, 2, 1.8, 2.6, GOLD2)
    bx(V, -2, 9, 7, 1, 11, 9, BRASS)                                                            # tuyau vers la machine
    # droite : lanterne impériale + étendard
    bx(V, 21, 0, 4, 27, 2, 10, WH); bx(V, 23, 2, 6, 25, 30, 8, IRON2)
    bx(V, 21.5, 30, 4.5, 26.5, 35, 9.5, GOLD2); bx(V, 22, 30.5, 5, 26, 34.5, 9, (255, 220, 120, 1)); bx(V, 21, 35, 4, 27, 36, 10, GOLD)
    bx(V, 25, 14, 7, 31, 27, 7.6, RED); bx(V, 25, 14, 6.9, 31, 15, 7.7, GOLD); bx(V, 27.5, 18, 6.8, 28.5, 23, 7.8, GOLD, 0)
    return V
def scene_echo():
    V = echo_archive()
    bx(V, -16, 0, -48, 32, 1, 0, NOIR2)
    for (a, b, c_, d) in ((-16, -48, 32, -47), (-16, -1, 32, 0), (-16, -48, -15, 0), (31, -48, 32, 0)): bx(V, a, 1, b, c_, 1.4, d, VIO, 0)
    disque(V, 8, -24, 1, 1.3, 16, 17, LAV); disque(V, 8, -24, 1, 1.3, 10, 10.8, LAV); disque(V, 8, -24, 1, 1.3, 3, 3.8, PALE)
    for k in range(8):
        a = k * math.pi / 4; bx(V, 8 + 13.4 * math.cos(a) - .6, 1, -24 + 13.4 * math.sin(a) - .6, 8 + 13.4 * math.cos(a) + .6, 1.3, -24 + 13.4 * math.sin(a) + .6, PALE, 0)
    for (x, z) in ((-13, -45), (29, -45), (-13, -3), (29, -3)):                                 # éclats flottants aux 4 coins
        bx(V, x - 1.5, 1, z - 1.5, x + 1.5, 2.5, z + 1.5, NOIR, 0); eclat(V, x, 7, z, 7, LAV); eclat(V, x, 15.5, z, 2, PALE)
    for x in (-8, 24):                                                                          # obélisques latéraux
        bx(V, x - 3, 0, 5, x + 3, 2, 11, NOIR); bx(V, x - 2, 2, 6, x + 2, 22, 10, NOIR2); bx(V, x - 1.5, 22, 6.5, x + 1.5, 25, 9.5, NOIR2)
        bx(V, x - 0.5, 6, 5.8, x + 0.5, 18, 6.2, LAV, 0); eclat(V, x, 27, 8, 5, LAV)
    return V
L = [("Empire · Machine différentielle + zone de largage", scene_empire), ("Écho · Archive résonante + cercle d'arrivée", scene_echo)]
out = Image.new('RGB', (2 * 520, 520), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
for i, (t, fn) in enumerate(L):
    im = rendu(F(fn()), T=3); im.thumbnail((500, 470)); x = i * 520 + 10
    out.paste(im, (x + (500 - im.width) // 2, 40 + (470 - im.height))); d.text((x, 8), t, fill=(230, 220, 200), font=f)
out.save('apercu_zone_v6.png'); print('ok')
