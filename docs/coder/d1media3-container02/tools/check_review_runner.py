from pathlib import Path
import json,subprocess,hashlib,shutil,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];assert not (B/'evidence/media3-container02-freeze.json').exists();E=B/'evidence/review-runner-gate-final';E.mkdir(exist_ok=False);root=R/'docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE';positive=root/'coder-documented-entry-prefreeze-001';script=B/'tools/review_all.py';P='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
summary=json.loads((positive/'summary.json').read_text());assert not summary['frozenCandidate'] and len(summary['runs'])==60 and all(x['exitCode']==0 for x in summary['runs']) and summary['toolSha256']==sha(script)
assert json.loads((positive/'source/source-pins.json').read_text())==json.loads((B/'evidence/local-002/source-pins.json').read_text())
shutil.copyfile(positive/'summary.json',E/'positive-summary.json')
targets={'old04':R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/coder-runner-negative-04','old03':R/'docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/coder-runner-negative-04','candidate':B/'evidence/runner-negative-denied','prefix-sibling':R/'docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE_extra/coder-runner-negative','traversal':root/'..'/'D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/coder-runner-traversal-negative-04','root-itself':root,'relative':Path('docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/coder-runner-relative-negative')}
targets['existing-child']=positive
rows=[]
for name,target in targets.items():
 before=target.exists();argv=[P,'-X','utf8','-B',str(script),'--output',str(target)];p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(E/(name+'.stdout')).write_bytes(p.stdout);(E/(name+'.stderr')).write_bytes(p.stderr);record={'argv':argv,'exitCode':p.returncode,'originalProcessReturned':True,'toolSha256':sha(script),'deniedTargetCreated':False};(E/(name+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8');assert p.returncode==1 and target.exists()==before;rows.append(record)
(E/'summary.json').write_text(json.dumps({'runnerSha256':sha(script),'positiveFullDocumentedExecution':str(positive),'positiveFrozen':False,'positiveCoderSelfCheckNotIndependentReview':True,'positiveOriginalReturnedRuns':60,'negativePaths':8,'allDeniedWithoutTargetCreation':True,'negativeReceipts':rows},indent=2),encoding='utf-8');print('Documented runner positive full source/JAR execution + 8 rejected roots verified')
