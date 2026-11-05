exec(open('v4.py').read().split('L = [("A')[0])
# --- Écho 1 : sanctuaire-lutrin (même cadre que A : piliers + linteau, lutrin incliné, grimoire, anneau flottant)
def echo_sanctuaire():
    V = {}
    bx(V, 1, 0, 3, 15, 2, 13, NOIR2)
    for x in (1, 14):
        for z in (3, 12): bx(V, x, 2, z, x + 1, 26, z + 1, NOIR)
        bx(V, x, 9, 2.5, x + 1, 10, 3, LAV, 0); bx(V, x, 17, 2.5, x + 1, 18, 3, LAV, 0)
    bx(V, 1, 26, 3, 15, 28, 13, VIO); bx(V, 3, 25, 4, 13, 26, 12, NOIR2)
    bx(V, 5.5, 2, 6, 10.5, 10, 10, NOIR); bx(V, 5, 10, 5.5, 11, 11, 10.5, VIO)
    incline(V, 3, 13, 11, 4, 8, 1, 30, NOIR2)
    incline(V, 3.8, 7.7, 12, 4.6, 6.5, 0.5, 30, PALE); incline(V, 8.3, 12.2, 12, 4.6, 6.5, 0.5, 30, PALE)
    incline(V, 7.7, 8.3, 11.8, 4.6, 6.5, 0.6, 30, VIO)
    anneau(V, 8, 20, 7.5, 8.5, 3, 4, LAV); bx(V, 7.3, 19.3, 7.3, 8.7, 20.7, 8.7, PALE)
    for k in range(5): bx(V, 3.5 + k * 2.2, 22.5 - (k % 2) * 1.5, 9, 4.5 + k * 2.2, 23.5 - (k % 2) * 1.5, 10, LAV, 0)   # runes en suspension
    return V
# --- Écho 2 : archive résonante (pendant direct de A : colonnes de tomes/cristaux en lévitation + lutrin devant)
def echo_archive():
    V = {}
    bx(V, 1, 0, 3, 15, 2, 13, NOIR2)
    for x in (1, 14):
        bx(V, x, 2, 3, x + 1, 26, 4, VIO); bx(V, x, 2, 12, x + 1, 26, 13, VIO)
    bx(V, 1, 2, 12, 15, 26, 13, NOIR); bx(V, 1, 26, 3, 15, 28, 13, VIO)
    for c, x in enumerate((4.5, 8, 11.5)):
        for k in range(5):
            y = 6 + k * 4
            bx(V, x - 1.2, y, 7, x + 1.2, y + 2, 10, PALE if (k + c) % 2 else NOIR2, 3)       # tomes flottants
            bx(V, x - 0.3, y + 2.6, 8.2, x + 0.3, y + 3.2, 8.8, LAV, 0)                        # éclat
    incline(V, 3, 13, 4, 1, 4, 1, 30, NOIR2); incline(V, 4, 12, 5, 1.6, 3, 0.5, 30, PALE)   # petit lutrin à l'avant
    bx(V, 6, 2, 1.5, 10, 4, 3, NOIR)
    return V
L = [("Empire · A Machine différentielle", babbage), ("Écho 1 · Sanctuaire-lutrin", echo_sanctuaire), ("Écho 2 · Archive résonante", echo_archive)]
out = Image.new('RGB', (3 * 320, 380), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
for i, (t, fn) in enumerate(L):
    im = rendu(F(fn()), T=4); im.thumbnail((300, 330)); x = i * 320 + 10
    out.paste(im, (x + (300 - im.width) // 2, 40 + (330 - im.height))); d.text((x, 8), t, fill=(230, 220, 200), font=f)
out.save('apercu_bornes_v5.png'); print('ok')
