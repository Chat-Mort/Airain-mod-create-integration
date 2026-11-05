import os, re, sys, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carte import *
from appliquer import traduire
P = '/home/claude/empire-airain-pack'
S = '/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad'
n = 0
for racine in (P + '/kubejs', P + '/config', P + '/defaultconfigs'):
    for d, _, fs in os.walk(racine):
        for f in fs:
            if not f.endswith(('.js', '.json', '.snbt', '.mcfunction', '.toml', '.json5', '.txt')): continue
            p = os.path.join(d, f)
            try: s = open(p, encoding='utf-8').read()
            except UnicodeDecodeError: continue
            t = traduire(s)
            if t != s: open(p, 'w', encoding='utf-8').write(t); n += 1
print('pack texte :', n)
os.rename(P + '/kubejs/data/kubejs/recipe/airain/encre_runique.json', P + '/kubejs/data/kubejs/recipe/airain/runic_ink.json')
# générateurs (quêtes, structures…)
m = 0
for p in glob.glob(S + '/*.py'):
    s = open(p, encoding='utf-8').read(); t = traduire(s)
    if t != s: open(p, 'w', encoding='utf-8').write(t); m += 1
print('générateurs :', m)
# structures NBT
import nbtlib
k = 0
def parcourt(x):
    ch = False
    if isinstance(x, nbtlib.tag.String):
        t = traduire(str(x)); return (nbtlib.tag.String(t), t != str(x))
    if isinstance(x, nbtlib.tag.Compound):
        for key in list(x.keys()):
            v, c = parcourt(x[key]); 
            if c: x[key] = v; ch = True
        return x, ch
    if isinstance(x, nbtlib.tag.List):
        for i in range(len(x)):
            v, c = parcourt(x[i])
            if c: x[i] = v; ch = True
        return x, ch
    return x, False
for p in glob.glob(P + '/**/*.nbt', recursive=True):
    f = nbtlib.load(p)
    _, c = parcourt(f)
    if c: f.save(); k += 1
print('structures :', k)
