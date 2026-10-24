"""Static bounded preparation from the complete frozen 01 candidate only."""
from pathlib import Path
from datetime import datetime,timezone
import time,json,hashlib,difflib
H=Path(__file__).resolve().parent;P=Path('D:/CodexProjects/VideoKit');O=P/'docs/coder/d1-host-transaction01'
clock=json.loads((H/'first-read-clock.json').read_bytes());deadline=clock['deadlineMonotonic'];rows=[];copies=[];read_reserved=8388608;copied=0
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p,expected=None):
 global read_reserved
 p=Path(p);n=p.stat().st_size
 if time.monotonic()>=deadline or read_reserved+n+1>536870912:raise RuntimeError('BATCH_TIME_OR_READ_BUDGET')
 read_reserved+=n+1
 with p.open('rb') as f:b=f.read(n+1)
 if len(b)!=n or expected is not None and sha(b)!=expected:raise ValueError('FROZEN_PIN_MISMATCH:'+str(p))
 rows.append(dict(path=str(p),bytes=n,sha256=sha(b),reserved=n+1,originalCloseReturned=True));return b
def write(p,b):
 global copied
 if p.exists():raise RuntimeError('NO_PREPARATION_OVERWRITE:'+str(p))
 copied+=len(b)
 if copied>33554432:raise RuntimeError('PERMANENT_SAVED_BUDGET')
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:
  if f.write(b)!=len(b):raise IOError('SHORT_COPY')
def save(p,d):write(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
manifest=json.loads(read(O/'manifest.json','4350de4c1296c221508ea2cba23e5dc20b628d7536add1ca736462cdcc30bffe'));pins={r['path']:r for r in manifest['files']}
for rel,r in pins.items():
 if rel.startswith(('lib/','reference/regression-sources/','reference/platform-fixtures/')) or rel=='reference/inherited-fix02-sbom.cdx.json':
  b=read(O/rel,r['sha256']);write(H/rel,b);copies.append(dict(path=str(H/rel),relative=rel,bytes=len(b),sha256=sha(b),original=str(O/rel)))
changes=[]
for rel,r in pins.items():
 if rel.startswith(('src/','checks/')) and rel.endswith('.java'):
  before=read(O/rel,r['sha256']);after=read(H/rel)
  if before!=after:
   changes.append(dict(path=rel,old=r['sha256'],new=sha(after)))
   write(H/'diffs'/(Path(rel).name+'.diff'),''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='HOST01/'+rel,tofile='HOST02/'+rel)).encode())
read(P/'docs/tester/D1_HOST_TRANSACTION01_INDEPENDENT_B_REPORT_V1.0.md','08781fabff3344242280f82050e46cb6e92a0abff5fb87e66111b672d0610380')
req=read(P/'docs/coder/D1_HOST_TRANSACTION02_SOURCE_BINDING_FIX_CODER_REQUIREMENTS_V1.0.md');write(H/'reference/requirements.md',req)
for name in ('java.exe','javac.exe'):read(Path('D:/Android/Android Studio/jbr/bin')/name)
read(Path('D:/Android/Android Studio/jbr/release'))
save(H/'evidence/preparation.json',dict(scope='New HOST02 source/task/authority fix; no product call in preparation',sourceReads=rows,copyInputs=copies,sourceDifferences=changes,readReserved=read_reserved,earlyNamedConsoleReadReservation=8388608,earlyConsoleActualBytes='UNKNOWN; conservative full reservation retained',copyBytes=copied,firstReadUtc=clock['startUtc'],firstReadBeforeMonotonic=clock['firstReadBeforeMonotonic'],monotonicDeadline=deadline,deadlineUtc=datetime.fromtimestamp(datetime.fromisoformat(clock['startUtc']).timestamp()+2700,timezone.utc).isoformat(),clockProvenance='Raw monotonic recorded immediately BEFORE first requirement read in same tool invocation',JDK='Pinned bundled JBR21.0.10 --release11; binaries rechecked',Media3='1.9.3 unchanged',dependencyChanges=0,readCap=536870912,savedCap=33554432))
save(H/'case-plan.json',dict(schema='HOST_TRANSACTION02_SOURCE_BINDING_CASE_PLAN_V1',originalRealFileCases=['normal','validation_rejected','cancel_before_ready','publish_fails','unknown_then_query','query_before_ack','dual_consumer_move','late_old_generation'],originalAuthorityEntry='IndependentAuthorityCheck.main',originalAuthorityScenarios=3,newMatrixGroups=['source_task_matrix: SRC_A/SRC_B same other fields, constructor/move/recovery and exact original positive','source_authority_matrix: identical fields/generation1 but different original group reference, constructor/move/recovery','private_encoding_matrix: separator-safe key, VKH1 and HTX1 header rejection, no old files/migration','original_task_snapshot: opaqueTask accessor relabel without redirecting captured original grant'],newMatrixGroupCount=4,javaWorkerPassGroups=12,totalGroupsIncludingOriginalAuthority=15,compileProcesses=1,serialWorkerProcesses=1,initialBuilds=1,repairRoundsMaximum=1,wholeSeconds=2700,buildObservationSeconds=300,testObservationSeconds=300,readCap=536870912,savedCap=33554432,sampleMaximum=8388608,sourcesMaximum=2,blockMaximum=65536,outputPayloadMaximum=16777216,executionContext='Exact local command eligible for require_escalated automatic review; no admin/ACL/protection modifications',R03PhysicalReplacementAndTOCTOU='NOT_RUN_NOT_CLOSED',Android=False,Gradle=False,network=False,device=False,Git=False))
print(json.dumps(dict(inputs=len(rows),copyInputs=len(copies),readReserved=read_reserved,copyBytes=copied,changedSources=changes,deadlineUtc=datetime.fromtimestamp(datetime.fromisoformat(clock['startUtc']).timestamp()+2700,timezone.utc).isoformat())))
