"""Static post-run seal. No JVM, test, old transaction read, SDK or device call."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,time,zipfile,struct
H=Path(__file__).resolve().parent;P=Path('D:/CodexProjects/VideoKit');O=P/'docs/coder/d1-host-transaction01'
prep=json.loads((H/'evidence/preparation.json').read_bytes());deadline=prep['monotonicDeadline'];read_reserved=prep['readReserved']+1048576;write_reserved=prep['copyBytes'];reads=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def guard():
 if time.monotonic()>=deadline:raise RuntimeError('FIRST_READ_45_MINUTE_DEADLINE')
def read(p,expected=None,cap=33554432):
 global read_reserved
 guard();p=Path(p);n=p.stat().st_size
 if n>cap or read_reserved+n+1>536870912:raise ValueError('READ_BUDGET_BEFORE_OPEN')
 read_reserved+=n+1
 with p.open('rb') as f:b=f.read(n+1)
 if len(b)!=n or expected is not None and sha(b)!=expected:raise ValueError('SOURCE_OR_DELIVERY_PIN:'+str(p))
 reads.append(dict(path=str(p),bytes=n,reserved=n+1,sha256=sha(b),originalCloseReturned=True));return b
def save(name,d):
 global write_reserved
 guard();p=H/name;b=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
 if p.exists() or write_reserved+len(b)>33554432:raise ValueError('NO_OVERWRITE_OR_SAVED_BUDGET')
 write_reserved+=len(b)
 with p.open('xb') as f:
  if f.write(b)!=len(b):raise IOError('SHORT_WRITE')
attempts=sorted(p for p in (H/'evidence').glob('attempt*') if p.is_dir());assert len(attempts)==1
D=attempts[0];result=json.loads(read(D/'result.json'));summary=json.loads(read(D/'work/summary.json'));assert result['status']=='PASS'
assert summary['passed']==12 and summary['originalRealFileCases']==8 and summary['sourceBindingMatrixGroups']==4 and summary['affectedFrozenAuthorityScenarios']==3
assert summary['hostOwners']==summary['SDKOwners']==summary['sourceOwners']==0
read_reserved+=result['readReserved']
result_bytes=(D/'result.json').stat().st_size
final_runner_saved=result['permanentSavedReservation']+result_bytes
assert final_runner_saved==4513778
write_reserved+=final_runner_saved
attempt_tree_bytes=sum(p.stat().st_size for p in D.rglob('*') if p.is_file());write_reserved+=attempt_tree_bytes
for r in result['processes']:
 assert r['exitCode']==0 and r['waitReturned'] and r['handleCloseReturned'] and r['stdoutCloseReturned'] and r['stderrCloseReturned'] and not r.get('observationExpired')
order=json.loads(read(D/'order.json'));assert order['beforeAnyPopen']
assert order['specs']['compile']['envSha256']==order['specs']['checks']['envSha256']
inputs=json.loads(read(D/'source-input-pins.json'))
for r in inputs:read(Path(r['path']),r['sha256'])
originals=[]
manifest=json.loads(read(O/'manifest.json','4350de4c1296c221508ea2cba23e5dc20b628d7536add1ca736462cdcc30bffe'));old={r['path']:r for r in manifest['files']}
for r in prep['copyInputs']:
 original=Path(r['original']);read(original,r['sha256']);read(H/r['relative'],r['sha256']);originals.append(dict(path=str(original),sha256=r['sha256'],unchanged=True))
source_diffs=[]
for p in sorted((H/'src').rglob('*.java'))+sorted((H/'checks').rglob('*.java')):
 rel=p.relative_to(H).as_posix();r=old[rel];a=read(O/rel,r['sha256']);b=read(p)
 source_diffs.append(dict(path=rel,old=r['sha256'],new=sha(b),changed=a!=b))
assert len([r for r in source_diffs if r['changed']])==4
jar_rows=[]
for name in ('host-transaction02.jar','host-transaction02-tests.jar'):
 p=D/name;b=read(p)
 with zipfile.ZipFile(p) as z:
  names=z.namelist()
  for name_in_zip in names:
   raw=z.read(name_in_zip);assert raw[:4]==b'\xca\xfe\xba\xbe' and struct.unpack('>H',raw[6:8])[0]==55
  if name=='host-transaction02.jar':assert all(n.startswith('com/videokit/d1hosttx/') for n in names)
 jar_rows.append(dict(path=str(p),bytes=len(b),sha256=sha(b),classEntries=len(names),classMajor=55))
sourcezip=D/'exact-new-and-regression-sources.zip'
with zipfile.ZipFile(sourcezip) as z:
 for name in z.namelist():assert z.read(name)==read(H/name)
witnesses=[p for p in (D/'work').rglob('*') if p.is_file() and '.hosttx-identity-' in p.name]
matrix=[r for r in summary['cases'] if r['case'] in ('source_task_matrix','source_authority_matrix','private_encoding_matrix','original_task_snapshot')]
assert len(matrix)==4 and all(r['pass'] for r in matrix)
save('source-and-artifact-audit.json',dict(currentSourceEqualsExecutedInputs=True,sourceDifferences=source_diffs,original01CopiesUnchanged=originals,old01ManifestHashUnchanged=True,oldTransactionFilesRead=0,oldTransactionMigration=False,jars=jar_rows,sourceArchiveEntriesExact=True,matrix=matrix,sourceBindingGroups=4,realFileGroups=8,originalAuthorityGroups=3,privateHardlinkWitnesses=len(witnesses),R03='NOT_RUN_NOT_CLOSED',oldDevelopmentFailuresAndIndependentBStaticFailurePreserved=True,independentB='NOT_RUN_CURRENT_CANDIDATE',D1='NOT_PASSED',M0='NOT_STARTED'))
# Files created by authoring tools are measured once; payload/class output is
# additionally covered by the full attempt-tree bound, not refunded/deduped.
authored=[p for p in H.iterdir() if p.is_file()]+[p for folder in ('src','checks') for p in (H/folder).rglob('*') if p.is_file()]
write_reserved+=sum(p.stat().st_size for p in authored)
save('batch-ledger.json',dict(status='ONE_STRICT_BUILD_ONE_SERIAL_WORKER_LIMITED_PASS',firstReadClock=json.loads((H/'first-read-clock.json').read_bytes()),deadlineUtc=prep['deadlineUtc'],snapshotUtc=datetime.now(timezone.utc).isoformat(),preparationReadReserved=prep['readReserved'],preparationCopyBytes=prep['copyBytes'],earlyNamedConsoleReadReservationIncludedInPreparation=8388608,postRunConsoleReadReservation=1048576,consoleActualBytes='UNKNOWN_PARTIAL_READS; conservative reservations retained',runnerReadReserved=result['readReserved'],runnerSavedBeforeFinalResult=result['permanentSavedReservation'],runnerResultBytes=result_bytes,runnerSavedAfterFinalResult=final_runner_saved,additionalCompileClassAndSampleTreeBound=attempt_tree_bytes,staticReadRows=reads,readReservedBeforeLedger=read_reserved,permanentSavedReservedBeforeLedger=write_reserved,readCap=536870912,savedCap=33554432,sampleMaximum=8388608,sourcesMaximum=2,blockMaximum=65536,outputPayloadMaximum=16777216,metadataAndCommunicationReadTailReservation=262144,metadataAndReceiptWriteTailReservation=131072,budgetMeaning='Named material/copy/compile/test/static fees, not all JVM/OS implicit page IO. No refunds or hardlink byte deduplication.',D1='NOT_PASSED',M0='NOT_STARTED'))
save('completion.json',dict(status='DEVELOPER_LIMITED_PASS_PENDING_INDEPENDENT_B',completedUtc=datetime.now(timezone.utc).isoformat(),completedMonotonic=time.monotonic(),firstReadBeforeMonotonic=prep['firstReadBeforeMonotonic'],deadlineMonotonic=deadline,elapsedSeconds=time.monotonic()-prep['firstReadBeforeMonotonic'],compileProcesses=1,serialTestWorkers=1,repairRoundsUsed=0,caseGroups=dict(realFile=8,sourceBindingMatrix=4,originalAuthority=3),originalOwners=dict(SDK=0,host=0,source=0),oldTransactionFilesRead=0,oldTransactionsMigrated=0,sourceUnchangedAfterActual=True,Android='NOT_RUN',SDK=0,ADB=0,network=0,device=0,Gradle=0,Git=0,D1='NOT_PASSED',M0='NOT_STARTED'))
excluded={'manifest.json','seal.json','delivery-receipt.json','notification-receipt.json'};rows=[]
for p in sorted(H.rglob('*')):
 if p.is_file() and p.relative_to(H).as_posix() not in excluded:
  b=read(p);rows.append(dict(path=p.relative_to(H).as_posix(),bytes=len(b),sha256=sha(b)))
save('manifest.json',dict(schema='D1_HOST_TRANSACTION02_SOURCE_BINDING_FROZEN_MANIFEST_V1',files=rows,fileCount=len(rows),bytes=sum(x['bytes'] for x in rows),excluded=sorted(excluded),developerStatus='LIMITED_PASS_PENDING_INDEPENDENT_B',approvedForDeviceExecution=False,D1='NOT_PASSED',M0='NOT_STARTED'))
for r in rows:read(H/r['path'],r['sha256'])
m=read(H/'manifest.json');report=next(r for r in rows if r['path']=='REPORT.md')
seal=dict(status='DEVELOPER_LIMITED_PASS_FROZEN',manifestSha256=sha(m),reportSha256=report['sha256'],fileCount=len(rows),bytes=sum(x['bytes'] for x in rows),bad=0,sourceBindingFix='DEVELOPER_VERIFIED_NOT_INDEPENDENTLY_ACCEPTED',independentB='PENDING',R03='NOT_RUN_NOT_CLOSED',D1='NOT_PASSED',M0='NOT_STARTED')
save('seal.json',seal);s=read(H/'seal.json')
save('delivery-receipt.json',dict(**seal,sealSha256=sha(s),readReservedAtReceipt=read_reserved,permanentSavedReservedBeforeReceipt=write_reserved,tailReservation=dict(read=262144,write=131072),completedUtc=datetime.now(timezone.utc).isoformat(),elapsedSinceFirstReadSeconds=time.monotonic()-prep['firstReadBeforeMonotonic'],deadlineUtc=prep['deadlineUtc']))
assert read_reserved+262144<536870912 and write_reserved+131072<33554432
assert sum(p.stat().st_size for p in H.rglob('*') if p.is_file())<33554432
print(json.dumps(dict(**seal,sealSha256=sha(s),readReserved=read_reserved,permanentSavedReserved=write_reserved,completedUtc=datetime.now(timezone.utc).isoformat(),elapsedSeconds=time.monotonic()-prep['firstReadBeforeMonotonic'])))
