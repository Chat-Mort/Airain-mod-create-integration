import sys,re,glob,os
class P:
    def __init__(s,t): s.t=t; s.i=0
    def ws(s):
        while s.i<len(s.t) and s.t[s.i] in ' \t\r\n,': s.i+=1
    def val(s):
        s.ws(); c=s.t[s.i]
        if c=='{':
            s.i+=1; d={}
            while True:
                s.ws()
                if s.t[s.i]=='}': s.i+=1; return d
                k=s.key(); s.ws(); assert s.t[s.i]==':', f"':' attendu à {s.i}"; s.i+=1
                d[k]=s.val()
        if c=='[':
            s.i+=1; l=[]
            m=re.compile(r'\s*[IiLlBb];').match(s.t,s.i)
            if m: s.i=m.end()
            while True:
                s.ws()
                if s.t[s.i]==']': s.i+=1; return l
                l.append(s.val())
        if c=='"': return s.string()
        m=re.compile(r'[-0-9.a-zA-Z_]+').match(s.t,s.i); assert m, f"valeur invalide à {s.i}: {s.t[s.i:s.i+20]!r}"
        s.i=m.end(); return m.group()
    def key(s):
        if s.t[s.i]=='"': return s.string()
        m=re.compile(r'[A-Za-z0-9_.\-]+').match(s.t,s.i); assert m, f"clé invalide à {s.i}"; s.i=m.end(); return m.group()
    def string(s):
        s.i+=1; out=[]
        while s.t[s.i]!='"':
            if s.t[s.i]=='\\': s.i+=1
            out.append(s.t[s.i]); s.i+=1
        s.i+=1; return ''.join(out)
root=sys.argv[1];
def okid(i): return i[0] in '1234567' and len(i)==16
ids={}; deps=[]; ok=True
for f in sorted(glob.glob(root+'/**/*.snbt',recursive=True)):
    t=open(f,encoding='utf-8').read(); p=P(t)
    try:
        d=p.val(); p.ws(); assert p.i==len(t), "contenu après la fin"
    except Exception as e:
        ok=False; print("ERREUR",f,e); continue
    if 'quests' in d:
        ids[d['id']]='chapter'
        for q in d['quests']:
            assert q['id'] not in ids, "id dupliqué "+q['id']; ids[q['id']]='quest'
            for x in q.get('tasks',[])+q.get('rewards',[]):
                assert x['id'] not in ids, "id dupliqué"; ids[x['id']]='sub'
            deps+=[(f,q['id'],dd) for dd in q.get('dependencies',[])]
lang=P(open(root+'/lang/fr_fr.snbt',encoding='utf-8').read()).val()
missing=[d for _,_,d in deps if ids.get(d)!='quest']
badids=[i for i in ids if not okid(i)]
nolang=[i for i,k in ids.items() if k in('quest','chapter') and not any(key.split('.')[1]==i and key.endswith('.title') for key in lang)]
print("fichiers OK" if ok else "ERREURS", "| objets:",len(ids),"| dépendances:",len(deps),"| manquantes:",missing,"| sans titre:",nolang,"| IDs invalides:",badids)
