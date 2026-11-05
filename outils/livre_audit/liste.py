import runpy, sys, io, contextlib
S = '/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad'
sys.argv = ['gen_v2.py', S + '/livre_audit/out']
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(S + '/gen_v2.py', run_name='__main__')
inv = {v: k for k, v in g['QUESTS'].items()}
chap = {q['id']: c['key'] for c in g['chapters'] for q in c['quests']}
for c in g['chapters']:
    if c['key'] not in sys.argv[1:] if False else c['key'] not in WANT: continue
