import sys, runpy, io, contextlib
# exécuter gen_v2 sans écrire : on capture QUESTS/LANG
sys.argv=['gen_v2.py','/tmp/ptest_dump']
import os; os.makedirs('/tmp/ptest_dump',exist_ok=True)
with contextlib.redirect_stdout(io.StringIO()):
    g=runpy.run_path('gen_v2.py')
LANG=g['LANG']['fr']; chs=g['chapters']
for ch in chs:
    if ch['key'] not in ('reveil','andesite','cuivre','laiton','ciel','coeur','reconquete','echos'): continue
    print('\n#####', LANG[f"chapter.{ch['id']}.title"])
    for q in ch['quests']:
        t=LANG.get(f"quest.{q['id']}.title"); d=LANG.get(f"quest.{q['id']}.quest_desc",[])
        d=' '.join(x for x in d if x)[:260]
        print('-',t,'|',d)
