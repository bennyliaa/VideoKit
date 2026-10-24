from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parent;ROOT=R.parents[2];GIT='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_bytes())
def git(*a):
 p=subprocess.run([GIT,*a],cwd=ROOT,capture_output=True);assert p.returncode==0,p.stderr.decode(errors='replace');return p.stdout
assert git('rev-parse','HEAD').decode().strip()=='09eae12e950d156e1e8fbbfa294ce9b06e6758b4';assert not git('diff','--cached','--name-only')
source=load(R/'source-whitelist.json')['files'];rows=[]
for x in source:
 b=(ROOT/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'];rows.append(x)
for n in ['source-whitelist.json','exclusions.json','review-checks.json','CHECKPOINT_SCOPE.md','freeze_stage.py']:
 p=R/n;b=p.read_bytes();rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b),origin='CHECKPOINT_BOOKKEEPING_OUTSIDE_SELF_HASH_CYCLE'))
paths=sorted(x['path'] for x in rows);assert len(paths)==len(set(paths))
p=subprocess.run([GIT,'check-ignore','--stdin','-z'],cwd=ROOT,input=b'\0'.join(x.encode() for x in paths)+b'\0',capture_output=True);assert p.returncode in (0,1);assert not p.stdout,p.stdout.decode()
out=dict(base='09eae12e950d156e1e8fbbfa294ce9b06e6758b4',branch='codex/d1-qualification07-offline-20261024-a78e',files=rows,count=len(rows),bytes=sum(x['bytes'] for x in rows),ignoreRejected=0,allSourceBytesVerified=True,secretReview='review-checks.json',excludedFromStage=['stage-freeze.json','stage-paths.nul','post-commit reports/ref/PR receipts'])
(R/'stage-freeze.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(R/'stage-paths.nul').write_bytes(b'\0'.join(x.encode() for x in paths)+b'\0');print(json.dumps(dict(count=out['count'],bytes=out['bytes'],branch=out['branch'],freezeSha256=sha((R/'stage-freeze.json').read_bytes()))))
