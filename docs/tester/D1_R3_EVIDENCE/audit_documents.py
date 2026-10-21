"""Static R3 document review. No harness, JVM, media or device operations."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
expected={
 'D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md':'c91743c74bab78ea854c4e5f6dbe7bd2c09da6e3428641f3b31db158323ebb44',
 'D1_R3_BRANCH_MANIFEST_V1.0.md':'6b5cb83a9e67fc7de69cac0817f53e29e6ee82b69e9defc781504e0a148e569b',
 'D1_R3_DELIVERY_V1.0.md':'ee8086792298abd31a99bd4ed627ce2adcabddf3b0dec94372b38a9101a6a605'}
inputs=[];links=[];anchors={}
for name,digest in expected.items():
 p=ROOT/'docs/coder'/name;data=p.read_bytes();txt=data.decode('utf-8-sig')
 assert sha(data)==digest,name
 (OUT/name).write_bytes(data)
 inputs.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(data),bytes=len(data),matchesHandoff=True))
 anchors[name]=[dict(line=i,text=s) for i,s in enumerate(txt.splitlines(),1) if re.search(r'S17|P10-[CD]|Q07-TAKEFIRST|最多6|CLAIMED|UNKNOWN|正常退出|515|544|Qr|32个|180|覆盖|F03',s)]
 for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',txt):
  target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
  if lm:target=target[:lm.start()]
  t=Path(target);exists=t.is_file();valid=exists and (line is None or 1<=line<=len(t.read_text(encoding='utf-8-sig').splitlines()))
  links.append(dict(source=name,sourceLine=txt[:m.start()].count('\n')+1,target=target,line=line,exists=exists,valid=valid))
assert all(r['valid'] for r in links)
old=json.loads((ROOT/'docs/tester/D1_R2_EVIDENCE/input-and-link-audit.json').read_text(encoding='utf-8'))
r2=[dict(path=r['path'],expected=r['sha256'],actual=sha((ROOT/r['path']).read_bytes())) for r in old['inputs']]
assert all(r['expected']==r['actual'] for r in r2)
save('input-and-link-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Offline static review only',inputs=inputs,links=links,linkOccurrences=len(links),uniqueTargets=len({r['target'] for r in links}),r2Unchanged=r2))
save('reference-anchors.json',anchors)
txt=(ROOT/'docs/coder/D1_R3_BRANCH_MANIFEST_V1.0.md').read_text(encoding='utf-8-sig')
rows=[]
for i,line in enumerate(txt.splitlines(),1):
 if not re.match(r'^\| [PQ]\d\d-',line):continue
 cells=[s.strip() for s in line.split('|')[1:-1]]
 assert len(cells)==9,(i,cells)
 ident,task,terminal,ic,v,gmo,hb,qq,sec=cells[0],cells[1],cells[2],cells[3],cells[4],cells[5],cells[6],cells[7],cells[8]
 iby,icalls=map(int,ic.split('/'));g,m,o=map(int,gmo.split('/'));h,b=map(int,hb.split('/'));qr,qn=map(int,qq.split('/'))
 rows.append(dict(branch=ident,line=i,task=re.search(r'[ST]\d\d',task).group(),precondition=task,terminal=terminal,inputBytes=iby,inputCalls=icalls,validationBytes=int(v),targets=g,records=m,writeBytes=o,handles=h,buffers=b,queryReplay=qr,queryNew=qn,seconds=int(sec),nonQueryAllocated=8 if ident=='P10-D' else 4 if ident=='P10-C' else 6))
assert len(rows)==61 and len({r['branch'] for r in rows})==61
def total(rs):return {k:sum(r[k] for r in rs) for k in ['inputBytes','inputCalls','validationBytes','targets','records','writeBytes','queryReplay','queryNew','seconds','nonQueryAllocated']}
p=[r for r in rows if r['branch'].startswith('P')];q=[r for r in rows if r['branch'].startswith('Q')]
tot=total(rows)
tot['inputBytes']+=32;tot['inputCalls']+=2;tot['records']+=1
tot['seconds']+=20+20+10+18
tot['nonQueryAllocated']+=16+32
tot['allControlAllocated']=tot['nonQueryAllocated']+tot['queryReplay']+tot['queryNew']
tot['logBytes']=61*32768+131072+32*16384+524288
tot['maxRowHandles']=max(r['handles'] for r in rows)
tot['maxRowBuffers']=max(r['buffers'] for r in rows)
tasks={task:[r['branch'] for r in rows if r['task']==task] for task in sorted({r['task'] for r in rows})}
save('branch-and-budget-audit.json',dict(scope='Independent Markdown parsing and static arithmetic; allocations are not proof of necessary control-command count or actual runtime',rows=rows,pCount=len(p),qCount=len(q),p=total(p),q=total(q),totalsIncludingPFAndGlobal=tot,tasks=tasks,shortReadCharge=sum(65536-i for i in range(4))+4,shortReadNextRequest=65532,claim='All published aggregate numeric totals checked against parsed rows; execution feasibility reviewed separately.'))
print(json.dumps(dict(inputHashesMatch=True,links=len(links),uniqueTargets=len({r['target'] for r in links}),P=len(p),Q=len(q),totals=tot),ensure_ascii=False))
