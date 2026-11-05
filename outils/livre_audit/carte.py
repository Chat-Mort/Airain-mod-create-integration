import runpy, sys, os, json, itertools
S = '/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad'
sys.argv = ['gen_v2.py', S + '/livre_audit/out']
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(S + '/gen_v2.py', run_name='__main__')
from PIL import Image, ImageDraw, ImageFont
chapters, QUESTS, LANG = g['chapters'], g['QUESTS'], g['LANG']
inv = {v: k for k, v in QUESTS.items()}
ou = {}
for c in chapters:
    for q in c['quests']: ou[q['id']] = (c['key'], q['x'], q['y'])
def titre(qid):
    t = LANG['fr'].get(f'quest.{qid}.title', '?')
    return t[0] if isinstance(t, list) else t
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
def seg_x(a, b, c, d):
    def o(p, q, r): return (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
    if len({a, b, c, d}) < 4: return False
    return o(a,b,c)*o(a,b,d) < 0 and o(c,d,a)*o(c,d,b) < 0
stats = []
for c in chapters:
    if c['key'] == 'secours': continue
    qs = c['quests']
    if not qs: continue
    xs = [q['x'] for q in qs] + [i['x'] - i['w'] / 2 for i in c.get('images', [])] + [i['x'] + i['w'] / 2 for i in c.get('images', [])]
    ys = [q['y'] for q in qs] + [i['y'] for i in c.get('images', [])]
    E, ext = 120, 70
    W = int((max(xs) - min(xs)) * ext + 2 * E + 120); H = int((max(ys) - min(ys)) * ext + 2 * E)
    im = Image.new('RGB', (W, H), (30, 31, 36)); d = ImageDraw.Draw(im)
    P = lambda x, y: (E + (x - min(xs)) * ext, E + (y - min(ys)) * ext)
    aretes, externes, cachees = [], 0, []
    for q in qs:
        for dep in q['deps']:
            if dep in ou and ou[dep][0] == c['key']:
                if q.get('hide_lines'): cachees.append((P(*ou[dep][1:]), P(q['x'], q['y']))); continue
                aretes.append((P(*ou[dep][1:]), P(q['x'], q['y'])))
            else: externes += 1
    croise = sum(1 for (a, b), (e, h) in itertools.combinations(aretes, 2) if seg_x(a, b, e, h))
    pos = {}
    for q in qs: pos.setdefault((q['x'], q['y']), []).append(q)
    sup = sum(len(v) - 1 for v in pos.values() if len(v) > 1)
    for a, b in aretes: d.line([a, b], fill=(120, 120, 135), width=2)
    for i in c.get('images', []):
        t = Image.open(S + '/livre_audit/out/kubejs/assets/kubejs/textures/quests/' + i['image'].split('/')[-1]).convert('RGBA')
        t = t.resize((int(i['w'] * ext), int(i['h'] * ext)), Image.NEAREST)
        cx, cy = P(i['x'], i['y']); im.paste(t, (int(cx - t.width / 2), int(cy - t.height / 2)), t)
    for a, b in cachees:
        n = int(((b[0]-a[0])**2 + (b[1]-a[1])**2) ** 0.5 // 12)
        for i in range(0, n, 2):
            t0, t1 = i / n, (i + 1) / n
            d.line([(a[0] + (b[0]-a[0]) * t0, a[1] + (b[1]-a[1]) * t0), (a[0] + (b[0]-a[0]) * t1, a[1] + (b[1]-a[1]) * t1)], fill=(90, 90, 100), width=1)
    import math
    traverse = 0
    for a, b in aretes:
        for q in qs:
            p = P(q['x'], q['y'])
            if p in (a, b): continue
            vx, vy = b[0]-a[0], b[1]-a[1]; L2 = vx*vx + vy*vy
            t = max(0, min(1, ((p[0]-a[0])*vx + (p[1]-a[1])*vy) / L2))
            if math.hypot(a[0] + t*vx - p[0], a[1] + t*vy - p[1]) < 18: traverse += 1
    for q in qs:
        x, y = P(q['x'], q['y'])
        ext_dep = any(not (dep in ou and ou[dep][0] == c['key']) for dep in q['deps'])
        col = (220, 170, 60) if not q['optional'] else (110, 160, 210)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=col, outline=(255, 80, 80) if ext_dep else (20, 20, 20), width=3)
        d.text((x, y + 16), titre(q['id'])[:22], fill=(230, 230, 230), font=f, anchor='mt')
    t = LANG['fr'].get(f"chapter.{c['id']}.title", c['key']); t = t[0] if isinstance(t, list) else t
    d.text((10, 10), f"{t}  —  {len(qs)} quêtes, {croise} croisements, {externes} liens externes, {traverse} traits sur une quête", fill=(255, 255, 255), font=fb)
    im.save(f"{S}/livre_audit/{c['order']:02d}_{c['key']}.png")
    stats.append((c['order'], c['key'], t, len(qs), croise, externes, traverse))
for s in sorted(stats): print(s)
