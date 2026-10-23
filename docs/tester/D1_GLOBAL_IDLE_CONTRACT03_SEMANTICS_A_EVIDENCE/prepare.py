"""Bounded file-only preparation; no production body or child execution."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,sys,ast,uuid,zipfile,copy,subprocess
R=Path(__file__).resolve().parent;T=R.parent;B=T.parent/'coder/d1android02-global-idle-contract03-fix';P=T/'D1_DRIVER_CAPTURE_FIX01_PACKAGE';V=T/'D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE';READ=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def rd(p):
 p=Path(p)
 with p.open('rb') as f:b=f.read(10485761)
 assert len(b)<=10485760;READ.append({'path':str(p),'bytes':len(b)});assert sum(x['bytes'] for x in READ)<=33554432;return b
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:assert f.write(b)==len(b);f.flush()
def save(p,d):put(p,(json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode())
def main():
 assert not (R/'order.json').exists()
 for name,path in [('self_observer.py',V/'self_observer.py'),('native_identity.py',P/'native_identity.py'),('capture_policy.py',P/'capture_policy.py'),('independent_cases.py',V/'independent_cases.py')]:put(R/name,rd(path))
 io=rd(V/'self_io.py').decode().replace('4294967296','67108864').replace('8192','2048');put(R/'self_io.py',io.encode())
 assert sha(rd(P/'source-manifest.json'))=='b3cdd53b3527e39aac726d1014473e69f2c1a552fa7243a6be434adc5901c2e1'
 for x in json.loads(rd(P/'source-manifest.json'))['files']:assert sha(rd(P/x['path']))==x['sha256']
 pins=json.loads(rd(P/'runtime-pins.json'))
 for x in pins['files']:
  b=rd(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 full=rd(B/'reference/freeze-manifest.json');assert sha(full)=='55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81';rows=json.loads(full)['files'];assert len(rows)==98
 for x in rows:
  b=rd(B/x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 assert sha(rd(B/'reference/runner-source-seal.json'))=='4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93'
 source=json.loads(rd(B/'reference/runner-source-seal.json'))['sources']
 for p,h in source.items():assert sha(rd(B/p))==h
 sys.path[:0]=[str(R),str(B/'selfchecks')]
 from independent_cases import cases,text,record
 from contract_cases import make
 from contract03_cases import cases as extra73
 groups=[('independent175',cases(B)),('developer98-replay',make()),('developer73-map',extra73())];assert [len(x[1]) for x in groups]==[175,98,73]
 # New independently authored adjacent oracle cases, not a replay count.
 template=copy.deepcopy(groups[0][1][0]);adj=[]
 def add(label,t,why,status='BLOCKED_UNPROVEN'):
  q=copy.deepcopy(template);q.update(id=label,text=t,expected=status,expectedReason=why);q['context'].update(rawSha256=sha(t.encode()),rawBytes=len(t.encode()));adj.append(q)
 for kind in ('APP','PERS'):
  bad=record('com.independent.bad','com.independent.bad',10065,2,991,'bad991',kind).replace('ProcessRecord{','ProcessRecord {')
  for place in ('prefix','middle','tail'):
   bg=record('com.independent.bg','com.independent.bg',10066,16,992,'bad992');body=bad+record() if place=='prefix' else record()+bad+bg if place=='middle' else record()+bg+bad
   add('A_HEADER_'+kind+'_'+place,text(home=body),'GLOBAL_PROCESS_HEADERS_UNPROVEN')
 for value in ('2e0','2E0','2foo','02','2.00','2,0','+2','2\tcurProcState=16'):
  add('A_STATE_'+value.replace('\t','_'),text().replace('curProcState=2','curProcState='+value),'GLOBAL_OWN_FIELD_FORMAT_UNPROVEN' if value=='+2' else 'GLOBAL_PROCESS_STATE_UNPROVEN')
 for prefix in ('  *MYSTERY* UID 10065 ProcessRecord{bad991 991:x/u0a65}\n','    curProcState=2\n','  ProcessRecord{bad991 991:x/u0a65}\n','  UID 10065 ProcessRecord{bad991 991:x/u0a65}\n'):
  add('A_PREFIX_'+str(len(adj)),text(home=prefix+record()),'GLOBAL_PROCESS_HEADERS_UNPROVEN')
 add('A_INSTR_BEFORE_MALFORMED',text(home='Instrumentation #0: ActiveInstrumentation{abc}\n  *MYSTERY* UID 1 ProcessRecord{bad 1:x/1}\n'+record()),'ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED','BLOCKED_OCCUPIED')
 add('A_EMPTY_INSTR_KNOWN_GRAMMAR',text().replace('    mInstr=null\n',''),'GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY','PASS');assert len(adj)==20
 groups.append(('independent-adjacent20',adj));allrows=[];indices=[]
 for origin,items in groups:
  for row in items:
   row['origin']=origin;row['logicalIndex']=len(allrows);allrows.append(row)
 assert len(allrows)==366
 for i,row in enumerate(allrows):
  p=R/'inputs'/('case-'+str(i)+'.json');save(p,row);indices.append(str(p))
 save(R/'input-index.json',indices);save(R/'case-provenance.json',dict(groups=[dict(origin=n,count=len(v)) for n,v in groups],totalSemantic=366,originalIndependent17Positives=[r['id'] for r in groups[0][1] if r['expected']=='PASS'],original45Ids=[r['id'] for r in groups[0][1][:45]],currentPins=source,duplicatesReportedByOrigin=True))
 # Fixed exact production function host. No original capture/Runner/Gate/SDK.
 host="""param([string]$InputFile,[string]$OutputFile)
$ErrorActionPreference='Stop'
$u=[Text.UTF8Encoding]::new($false,$true)
. '%MODULE%'
$index=[IO.File]::ReadAllText($InputFile,$u)|ConvertFrom-Json -DateKind String
$out=@(foreach($p in $index){
 if(([IO.FileInfo]$p).Length -gt 1048576){throw 'CASE_INPUT_BOUND'}
 $r=[IO.File]::ReadAllText($p,$u)|ConvertFrom-Json -DateKind String
 $d=Get-GlobalIdleDecision $r.text $r.qualification $r.context
 $ok=($null -eq $r.expectedReason -or $d.reason -ceq $r.expectedReason)
 [ordered]@{id=$r.id;origin=$r.origin;logicalIndex=$r.logicalIndex;expected=$r.expected;expectedReason=$r.expectedReason;status=$d.status;reason=$d.reason;qualified=$d.qualified;stage=$d.stage;processCount=$d.processes.Count;processes=$d.processes;pass=($d.status -ceq $r.expected -and $d.qualified -eq ($r.expected -ceq 'PASS') -and $ok)}
})
[IO.File]::WriteAllText($OutputFile,($out|ConvertTo-Json -Depth 16),$u)
if(@($out|Where-Object {-not $_.pass}).Count){exit 2}
""".replace('%MODULE%',str(B/'tools/admission_checks.ps1').replace("'","''"));put(R/'host.ps1',host.encode())
 save(R/'budget.json',dict(wholeSeconds=300,stopNewAfterSeconds=240,concurrency=1,retry=0,maxPSHosts=2,perPSSeconds=90,auxProcesses=4,readBytes=67108864,artifactBytes=16777216,artifactFiles=512,stdoutBytes=1048576,stderrBytes=1048576,totalLogicalCases=400,semanticCases=366,argvCases=12,runtimeIdentityModels=4,rootPredicateCases=8,proposalBindings=6,entryReferences=3,externalStaticReview=1,estimatedDynamicSeconds=35,estimatedReadBytes=50331648,estimatedArtifactBytes=8388608,estimatedArtifactFiles=460,physicalIO='UNPROVEN'))
 from profile import preflight
 checked=preflight(R);save(R/'profile-preflight.json',checked)
 src=[]
 for p in sorted(R.glob('*.py')):
  b=rd(p);ast.parse(b.decode('utf-8-sig'));src.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 for p in [R/'host.ps1',R/'input-index.json',R/'budget.json',R/'profile-preflight.json',R/'case-provenance.json',*sorted((R/'inputs').glob('*.json'))]:
  b=rd(p);src.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 now=datetime.now(timezone.utc);order=dict(schema='CONTRACT03_SEMANTICS_A_ORDER_V1',batch=str(uuid.uuid4()),nonce=str(uuid.uuid4()),sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',requirement=str(T/'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_TESTER_REQUIREMENTS_V1.0.md'),candidate=str(B),candidateSourceSeal='4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93',candidateManifest='55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81',sources=src,notBeforeUtc=now.isoformat(),expiresUtc=(now+timedelta(seconds=900)).isoformat(),allowedStarts=1,scope='SEMANTICS_A_ONLY_NO_ORIGINAL_CAPTURE',readBytesPreparation=sum(x['bytes'] for x in READ));save(R/'order.json',order);print(json.dumps(dict(orderSha256=sha(rd(R/'order.json')),semanticCases=366,totalLogicalCases=400,preparationReadBytes=sum(x['bytes'] for x in READ),files=len(src))))
if __name__=='__main__':main()
