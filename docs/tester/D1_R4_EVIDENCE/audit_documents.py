"""Read-only R4 document parsing; no implementation or experimental execution."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
expected={'D1_R4_CONTROL_OPERATION_MANIFEST_V1.0.md':'6492f598b8b9f605239648277d08a56beae565c65de0f1dac5cee6db2ffa40bd','D1_R4_DELIVERY_V1.0.md':'ebca0ae145b162f29e19e5d0921fed99f3f0bd6118f16226f52e7ef93c227f88'}
identities=[];links=[];anchors={}
for name,h in expected.items():
 p=ROOT/'docs/coder'/name;assert sha(p)==h
 data=p.read_bytes();txt=data.decode('utf-8-sig');(OUT/name).write_bytes(data)
 identities.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=h,bytes=len(data),matchesHandoff=True))
 anchors[name]=[dict(line=i,text=s) for i,s in enumerate(txt.splitlines(),1) if re.search(r'P12-|P10-[CD]|Q07-TAKEFIRST|GC/n32|两次|每事务|元数据事务|512B|10ms|452|351|515|覆盖|544',s)]
 for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',txt):
  target=m.group(1);lm=re.search(r':(\d+)$',target);ln=int(lm.group(1)) if lm else None
  if lm:target=target[:lm.start()]
  p=Path(target);valid=p.is_file() and (ln is None or 1<=ln<=len(p.read_text(encoding='utf-8-sig').splitlines()))
  assert valid,target
  links.append(dict(source=name,line=txt[:m.start()].count('\n')+1,target=target,targetLine=ln,valid=valid))
old=[]
for batch in ['D1_R2','D1_R3']:
 audit=json.loads((ROOT/f'docs/tester/{batch}_EVIDENCE/input-and-link-audit.json').read_text(encoding='utf-8'))
 for r in audit['inputs']:
  actual=sha(ROOT/r['path']);assert actual==r['sha256']
  old.append(dict(path=r['path'],sha256=actual,unchanged=True))
save('input-and-link-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Offline documents only; no media/harness/runtime/device/build',inputs=identities,links=links,linkOccurrences=len(links),uniqueTargets=len({r['target'] for r in links}),oldInputsUnchanged=old))
save('reference-anchors.json',anchors)
prior=json.loads((ROOT/'docs/tester/D1_R3_EVIDENCE/branch-and-budget-audit.json').read_text(encoding='utf-8'))
prior_by={r['branch']:r for r in prior['rows']}
txt=(ROOT/'docs/coder/D1_R4_CONTROL_OPERATION_MANIFEST_V1.0.md').read_text(encoding='utf-8-sig')
def tokens(seq):
 if '无新控制' in seq:return []
 seq=seq.replace('{','').replace('}','');depth=0;out=[];start=0
 for i,c in enumerate(seq):
  if c=='(':depth+=1
  elif c==')':depth-=1
  elif c in ';,' and depth==0:
   out.append(seq[start:i].strip());start=i+1
 out.append(seq[start:].strip())
 assert depth==0
 return [s for s in out if s]
rows=[];pf=[];gc=[]
for i,line in enumerate(txt.splitlines(),1):
 if re.match(r'^\| [PQ]\d\d-',line):
  cells=[s.strip() for s in line.split('|')[1:-1]];assert len(cells)==6
  branch,seq,evidence,n,qq,seconds=cells;n=int(n);seconds=int(seconds);qr,qn=map(int,qq.split('/'))
  parsed=tokens(seq.split('→',1)[1]);assert len(parsed)==n,(branch,parsed,n)
  orig=prior_by[branch];assert (qr,qn,seconds)==(orig['queryReplay'],orig['queryNew'],orig['seconds'])
  rows.append(dict(branch=branch,line=i,task=orig['task'],controlTokens=parsed,N=n,queryReplay=qr,queryNew=qn,seconds=seconds,planningRemainderMs=seconds*1000-10*n-100*(qr+qn)))
 if re.match(r'^\| (PF|GC)/n\d\d \|',line):
  cells=[s.strip() for s in line.split('|')[1:-1]];ident=cells[0]
  (pf if ident.startswith('PF') else gc).append(dict(id=ident,line=i,request=cells[1],evidence=cells[2]))
assert len(rows)==61 and set(r['branch'] for r in rows)==set(prior_by)
assert [r['id'] for r in pf]==[f'PF/n{i:02}' for i in range(1,17)]
assert [r['id'] for r in gc]==[f'GC/n{i:02}' for i in range(1,33)]
p=sum(r['N'] for r in rows if r['branch'].startswith('P'));q=sum(r['N'] for r in rows if r['branch'].startswith('Q'))
qr=sum(r['queryReplay'] for r in rows);qn=sum(r['queryNew'] for r in rows)
assert (p,q,qr,qn)==(176,127,18,83)
assert all(r['planningRemainderMs']>0 for r in rows)
save('control-and-budget-audit.json',dict(scope='Independent token parsing and allocation arithmetic only; positive time remainder is conditional on a 10ms/N planning assumption, not real timing proof',rows=rows,PF=pf,GC=gc,pNonQuery=p,qNonQuery=q,nonQuery=p+q+len(pf)+len(gc),queries=dict(replay=qr,new=qn,total=qr+qn),allControl=p+q+len(pf)+len(gc)+qr+qn,limit=544,spareUnallocated=544-(p+q+len(pf)+len(gc)+qr+qn),same61BranchesAndQueryAndSecondsAsR3=True,minimumPlanningRemainderMs=min(r['planningRemainderMs'] for r in rows),inheritedDataBudgets=prior['totalsIncludingPFAndGlobal'],logFilePeakAllocated=61*32768+131072+32*16384+524288,largestExplicitRowEventCalculation=19*768+4*768+1024,note='Inherited R3 nonQuery/allControl values are superseded by R4; inherited media/time/file budgets remain unchanged.'))
print(json.dumps(dict(hashesMatch=True,links=len(links),uniqueTargets=len({r['target'] for r in links}),branches=len(rows),pNonQuery=p,qNonQuery=q,PF=len(pf),GC=len(gc),nonQuery=p+q+48,queries=qr+qn,control=p+q+48+qr+qn,minPlanningRemainderMs=min(r['planningRemainderMs'] for r in rows)),ensure_ascii=False))
