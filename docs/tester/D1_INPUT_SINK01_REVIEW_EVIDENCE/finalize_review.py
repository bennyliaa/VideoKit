from pathlib import Path
import json,hashlib,re,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1input-sink01';P=R/'docs/tester/D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cases=json.loads((R/'docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE/reusable-regression-cases.json').read_text())['cases']
for c in cases:
 c['phaseB']='NOT_RUN_PLATFORM' if c['id']=='S05' else 'FAIL_B02' if c['id']=='S06' else 'PARTIAL_FAIL_B01' if c['id']=='S03' else 'PASS_LIMITED_OFFLINE'
(E/'independent-case-results.json').write_text(json.dumps(dict(candidate='D1-20261021-INPUT-SINK01',cases=cases,total=19,allPlatformPass=False,newDependencies='PASS_IDENTITY_LICENSE_FOR_THIS_OFFLINE_CANDIDATE',overall='FAIL',findings=[dict(id='B02',priority='P1'),dict(id='B01',priority='P2')]),ensure_ascii=False,indent=2),encoding='utf8')
assert sha(E/'independent-001/generated-4b.tmp')=='e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6'
assert 'PASS_OFFLINE_ACTUAL_FRAMEWORK_ADAPTERS groups=20' in (E/'independent-001/checks.stdout').read_text()
assert 'scenarios=5 reproducedDefects=2 originalThreadsJoined=true retainedSources=0 retainedOutputs=0' in (E/'independent-boundaries-3.stdout').read_text()
for m in re.findall(r'\]\((D:/[^)]+)\)',P.read_text(encoding='utf8')):
 path=re.sub(r':\d+$','',m);assert Path(path).exists(),path
manifest=json.loads((B/'evidence/input-sink01-freeze.json').read_text())
for row in manifest['files']:assert sha(R/row['path'])==row['sha256']
records=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json']
out=dict(frozenAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=P.relative_to(R).as_posix(),reportBytes=P.stat().st_size,reportSha256=sha(P),overall='FAIL',evidenceFiles=records,candidateStillUnchanged=True,deviceOrSdkOrGradleCalls=0,allOriginalJdkProcessesReturned=True,controlledOriginalTailsJoined=True,scope='Independent offline phase B only; no next batch started')
(E/'review-evidence-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='evidenceFiles'},ensure_ascii=False,indent=2));print('evidenceFiles',len(records))
