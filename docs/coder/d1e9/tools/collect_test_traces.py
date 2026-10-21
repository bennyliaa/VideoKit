"""Copy only actual plain-text platform traces/response files into the review package; never media/fixtures."""
import hashlib,json,pathlib,shutil
B=pathlib.Path(__file__).resolve().parents[1];rows=[];total=0
for work in sorted((B/'.selfcheck').iterdir()):
 evidence=B/'evidence/selfcheck-attempts'/work.name
 if not evidence.is_dir():continue
 files=sorted((work/'cases').glob('*-platform-trace-*.txt')) if (work/'cases').is_dir() else []
 files+=list(work.glob('compile*.args'))
 for p in files:
  raw=p.read_bytes();assert len(raw)<=262144;total+=len(raw);assert total<=16777216
  target=evidence/'platform-traces'/p.name;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():assert target.read_bytes()==raw
  else:shutil.copyfile(p,target)
  rows.append(dict(path=str(target.relative_to(B)).replace('\\','/'),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/test-trace-inventory.json').write_text(json.dumps(dict(schema=1,status='PASS',files=rows,bytes=total,fixtureMediaIncluded=False,actualDeviceCalls=0),indent=2)+'\n',encoding='utf-8')
print('trace files',len(rows),'bytes',total)
