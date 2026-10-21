from pathlib import Path
import sys,json,subprocess,hashlib,shutil,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];assert not (B/'evidence/media3-container01-freeze.json').exists(),'FROZEN_SELFTEST_USE_NEW_EXTERNAL_OUTPUT'
D=B/'evidence/tool-output-gate-final';D.mkdir(exist_ok=False);script=B/'tools/local_check.py';P=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe');root=R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args,code):
 argv=[str(P),'-X','utf8','-B',str(script)]+list(map(str,args));start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(D/(name+'.stdout')).write_bytes(p.stdout);(D/(name+'.stderr')).write_bytes(p.stderr);(D/(name+'.json')).write_text(json.dumps({'argv':argv,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':p.returncode,'originalProcessReturned':True,'toolSha256':sha(script),'expectedExit':code},indent=2),encoding='utf-8');assert p.returncode==code,(name,p.stderr.decode('utf8','replace'));return p
shown=run('derived-root',['--print-review-root'],0);assert Path(shown.stdout.decode().strip())==root
positive=root/'coder-tool-positive-002';assert not positive.exists();run('positive',['--review-output',positive],0)
assert 'groups=20' in (positive/'checks.stdout').read_text();context=json.loads((positive/'review-context.json').read_text());assert context['allowedReviewRoot']==str(root) and context['reviewMode'] and not context['candidateFrozen']
assert json.loads((positive/'source-pins.json').read_text())==json.loads((B/'evidence/local-007/source-pins.json').read_text())
shutil.copytree(positive,D/'positive-output',ignore=shutil.ignore_patterns('classes'))
negatives={'old04':R/'docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/coder-tool-negative-04','old03':R/'docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/coder-tool-negative-04','candidate':B/'evidence/tool-negative-denied','prefix-sibling':R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE_extra/coder-negative','traversal':root/'..'/'D1_INPUT_SINK04_REVIEW_EVIDENCE/coder-tool-traversal-negative-04','root-itself':root,'relative':Path('docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/coder-relative-negative')}
rows=[]
for name,target in negatives.items():
 before=target.exists();run(name,['--review-output',target],1);assert target.exists()==before,'DENIED_PATH_WAS_CREATED';rows.append({'case':name,'target':str(target),'expectedDenied':True,'targetCreated':False})
(D/'summary.json').write_text(json.dumps({'candidate':B.name,'toolSha256':sha(script),'positiveActualJdkCompileAnd20Groups':True,'positiveDirectory':str(positive),'positiveContext':'CODER_SELF_CHECK_UNFROZEN_NOT_INDEPENDENT_REVIEW','positivePinsMatchFinalLocal007':True,'derivedRoot':str(root),'negativeCases':rows,'oldEvidenceUnmodified':True,'noTemporaryOverride':True},indent=2),encoding='utf-8');print('C01 actual gate: correct root JDK compile+20 PASS; 7 wrong paths rejected without creation')
