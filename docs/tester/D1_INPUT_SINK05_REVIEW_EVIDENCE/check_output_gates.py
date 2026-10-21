from pathlib import Path
import subprocess,json,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink05';E=Path(__file__).resolve().parent;P=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
cases=[('old-root',R/'docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/rejected-sink05-gate'),('candidate',B/'rejected-tester-gate'),('fake-prefix',R/'docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE_FAKE/rejected-tester-gate'),('escape',E/'..'/'rejected-tester-escape'),('relative',Path('relative-sink05-gate')),('root',E),('reuse',E/'independent-001')]
rows=[]
for tool,flag in [('review_all.py','--output'),('local_check.py','--review-output')]:
 for label,target in cases:
  before=target.exists();args=[str(P),'-X','utf8','-B',str(B/'tools'/tool),flag,str(target)];p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
  stem=tool.replace('.py','')+'-reject-'+label;(E/(stem+'.stderr')).write_bytes(p.stderr);(E/(stem+'.stdout')).write_bytes(p.stdout)
  assert p.returncode!=0 and before==target.exists(),(tool,label)
  rows.append(dict(tool=tool,case=label,argv=args,exitCode=p.returncode,originalProcessReturned=True,existedBefore=before,existsAfter=target.exists(),rejectedWithoutTargetCreation=True))
(E/'independent-output-gates.json').write_text(json.dumps(dict(result='PASS',negativeCasesPerTool=7,rows=rows),indent=2),encoding='utf8');print('PASS both documented tools reject7 roots without new targets; successful actual entry in independent-001')
