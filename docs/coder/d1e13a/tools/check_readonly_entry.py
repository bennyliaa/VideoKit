"""Check only CLI read-only behavior and original frozen bytes; never calls the old packager."""
from pathlib import Path
import hashlib,json,subprocess,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def row(p):b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def snapshot():return [row(p) for p in sorted(B.rglob('*')) if p.is_file() and not any(x in {'build','.gradle','.checks','__pycache__'} for x in p.relative_to(B).parts)]
old=R/'docs/coder/d1e13/evidence/e13-freeze.json';oldPin=row(old);assert oldPin['sha256']=='3b80d430aa7f859174ffae0a4b5ca948a01aa032d15c0666fb595e6a1bba5cc0'
frozen=json.loads(old.read_text(encoding='utf-8'))['immutableFiles']
for x in frozen:assert row(R/x['path'])==x
before=snapshot();commands=[]
for args,code in [([],2),(['verify'],2),(['--help'],0),(['pack','--help'],0)]:
 command=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py')]+args
 result=subprocess.run(command,capture_output=True,timeout=30);assert result.returncode==code,(args,result.stderr)
 commands.append({'argv':command,'exitCode':result.returncode,'stdout':result.stdout.decode('utf-8'),'stderr':result.stderr.decode('utf-8')})
assert before==snapshot(),'READ_ONLY_ENTRY_MUTATED_FILES'
for x in frozen:assert row(R/x['path'])==x
assert row(old)==oldPin
output={'status':'PASS_READONLY_DEFAULT_VERIFY_AND_HELP_PREFREEZE','commands':commands,'candidateFilesBeforeAfterIdentical':len(before),'oldE13FrozenRowsUnchanged':len(frozen),'oldSeal':oldPin,'oldMisusedPackagerReexecuted':False,'oldMisuseScope':'Existing JAR FileExistsError before completion was a packaging invocation problem; not a product functionality FAIL','deviceCalls':0}
(B/'evidence/readonly-entry-pre-freeze.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in output.items() if k!='commands'},ensure_ascii=False))
