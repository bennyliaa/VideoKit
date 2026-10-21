"""Independent design-package identity and archived-metadata reconstruction only.
Does not execute candidate tooling, product models, builds, migrations, ADB, or media reads.
"""
from pathlib import Path
import json,hashlib,zipfile,re,struct
R=Path(__file__).resolve().parents[3];B='docs/coder/d1e8/'
def sha(b):return hashlib.sha256(b).hexdigest()
def raw(p):
    assert not str(p).lower().endswith(('.mp4','.avi','.mkv')),'MEDIA_FORBIDDEN'
    return (R/p).read_bytes()
def obj(p):return json.loads(raw(p))
def check(x):
    b=raw(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
seal=B+'evidence/e8-design-seal.json';sealHash='bba077cd93cdaf1e6b2c172c213f236834ce218e0ea7b0447dd361b020b30b4f'
assert sha(raw(seal))==sealHash
f=obj(seal);assert len(f['immutableFiles'])==30
for x in f['immutableFiles']:check(x)
manifest=obj(f['manifest']['path']);assert len(manifest['files'])==28
with zipfile.ZipFile(R/f['designZip']['path']) as z:
    assert z.namelist()==[x['path'] for x in manifest['files']] and len(set(z.namelist()))==28
    for x in manifest['files']:
        assert not x['path'].lower().endswith(('.mp4','.avi','.mkv'))
        b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
for x in f['documents']:check(x)
analysis=obj(B+'evidence/existing-evidence-analysis.json')
for x in analysis['sources']:
    check(x['original']);check(x['copy']);assert raw(x['original']['path'])==raw(x['copy']['path'])
for x in analysis['productionSources']:check(x)
oldSeal='docs/coder/d1e7a/evidence/e7a-freeze.json'
assert sha(raw(oldSeal))=='1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'
old=obj(oldSeal);assert len(old['immutableFiles'])==200
for x in old['immutableFiles']:check(x)
text=raw(B+'reference/normalMp4SixRealFrames-post-state-stdout.txt').decode()
segment=text.split('HEX_BEGIN|files/e4a_output_budget/ledger.bin',1)[1].split('HEX_END',1)[0]
ledger=bytes.fromhex(segment);assert len(ledger)==1011 and sha(ledger)=='f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba'
lines=ledger.decode('ascii').splitlines();assert len(lines)==7 and lines[0]=='E4A1 730a73e1-50e1-4198-a515-047104f00e31 4194304 2097152 128'
chain=sha((lines[0]+'\n').encode());records={};events=[]
for line in lines[1:]:
    payload,want=line.rsplit(' ',1);assert sha((chain+' '+payload).encode())==want;chain=want;parts=payload.split()
    if parts[0]=='R':assert len(parts)==3 and parts[1] not in records;records[parts[1]]=dict(batch=parts[2],state=None,bytes=None)
    else:
        assert parts[0]=='S' and len(parts)==5 and parts[1] in records and records[parts[1]]['bytes'] is None
        records[parts[1]].update(state=parts[2],bytes=int(parts[3]),sha256=parts[4])
    events.append(dict(payload=payload,chain=chain))
expected={'86cafdb3-0fc4-447d-920b-b19c884bf494':('ABORTED',0),'0ee15550-8952-4639-91ac-83ab9d14d36c':('ABORTED',53651),'fbe4330b-111b-4b05-a93c-467413eb8d34':('READY',53567)}
assert {k:(v['state'],v['bytes']) for k,v in records.items()}==expected
assert sum(v['bytes'] for v in records.values())==107218 and all(v['bytes'] is not None for v in records.values())
proof=raw(B+'reference/archive-proof.txt.bin').decode();assert 'originalCloseACK=false' in proof and 'fence=662e9ecd-bede-42e6-bb58-ce81d668ff44' in proof
assert lines[2] in proof and '1747c406b45987a8f4a3e8194bb170dfac92eb938d94ad2950bbb1f303ad4055' in lines[2]
guard=raw(B+'reference/archive-guard.identity.bin');assert len(guard)==82 and guard[:4]==b'E5B1' and guard[6:42].decode()=='86cafdb3-0fc4-447d-920b-b19c884bf494'
assert [struct.unpack('>qqi',guard[42:62]),struct.unpack('>qqi',guard[62:82])]==[(64522,20304,10221),(64522,20385,10221)]
owner=raw(B+'reference/archive-recovery.owner.bin');assert len(owner)==104 and owner==b'E5A_N2_RECOVERY_OWNER_V1 8c6673b7-38a5-4a24-838d-ca8466d8b75f 4869 10221 com.videokit.app 1792224193301\n'
current=obj(B+'reference/control-01-snapshot.json')['fields']
assert all(current[k]==v for k,v in dict(history='AVAILABLE',returned='0',matches='0',proc='NOT_REQUESTED',holder='CLOSED',originalOperationsReturned='true',grant='NONE',birthGeneration='NOT_RECORDED').items())
historical=raw(B+'reference/normalMp4SixRealFrames-instrumentation-stdout.txt').decode()
assert 'exitTimestamp=1792224193337 reason=10 status=0 absent=true' in historical
assert 'ABORTED_SETTLED' in raw(B+'reference/02-original-abort-stdout.txt').decode()
matrix=obj(B+'evidence/requirements-evidence-matrix.json');assert len(matrix['requirements'])==14 and matrix['implementation']=='NOT_STARTED' and matrix['productionTests']=='NOT_RUN'
for x in matrix['requirements']:check(x['document'])
design=raw('docs/coder/D1_E8_TEST_DESIGN_V1.0.md').decode();groups=re.findall(r'^\|(L\d+|V\d+|S\d+|C\d+) ',design,re.M);assert len(groups)==len(set(groups))==22
checks=obj(B+'evidence/design-check-results.json');assert checks['scenarioGroups']==groups and checks['productionOrAndroidTestCasesExecuted']==0
budgetSource=raw('docs/coder/d1e7a/src/com/videokit/spike/e4/E4OutputBudget.java').decode();assert 'Persistent cooperative execution budget' in budgetSource
guardSource=raw('docs/coder/d1e7a/src/com/videokit/spike/e4/E5BGuard.java').decode();assert guardSource.index('io.unlock(descriptor)')<guardSource.index('io.close(descriptor)')
oldObserver=raw('docs/coder/d1e7a/src/com/videokit/spike/e4/E5AFinalObservation.java').decode();assert 'legacy-acceptance' not in oldObserver and 'requireRecoveryWriterDead(writer)' in oldObserver
findings=[dict(id='E8-F01',priority='P1',issue='MIGRATION_ACTOR_IDENTITY_AND_CROSS_HOST_COMPLETION_OR_UNKNOWN_ADMISSION_CONTRACT_NOT_CLOSED',basis='Migration plan lines17-36 require returned owner but pin only legacy task/policy and two policy files; new actor binding, status authority and completion prerequisite need explicit specification, not just an available lock.'),dict(id='E8-F02',priority='P2',issue='UNAWARE_LEGACY_BINARY_AUTOMATIC_FAIL_CLOSED_ROLLBACK_CLAIM_HAS_NO_ENFORCEMENT',basis='Migration plan line21 and L11 require old unaware code to block; frozen legacy observer has no acceptance/revocation/version gate. Need explicit supported rollback floor/deployment restriction or compatible reader, not reliance on currently empty history.')]
result=dict(packageIntegrity='PASS',manifestFiles=28,immutableFiles=30,sealSha256=sealHash,designZip=f['designZip'],priorE7AImmutableFilesVerified=200,independentArchivedLedger=dict(bytes=1011,sha256=sha(ledger),records=records,events=events,consumed=107218,reserved=0),oldCloseACK=False,legacyBirth='NOT_RECORDED',oldAviCause='UNKNOWN',designScenarioGroups=groups,productionTestsExecuted=0,testerAdbCalls=0,testerMediaOrExportReadBytes=0,testerBuildModelMigrationRuns=0,recommendation='PRECISE_ONE_TIME_LEGACY_TERMINAL_ACCEPTANCE_WITH_FRESH_CURRENT_GATES',designDecision='DIRECTION_SUPPORTED_CONTRACT_CHANGES_REQUIRED_BEFORE_IMPLEMENTATION_ACCEPTANCE_BASELINE',findings=findings,deviceMigrationAdmission=False,longTermE6B_OBS_F01='OPEN',D1='NOT_PASSED',M0='NOT_STARTED')
Path(__file__).with_name('identity-and-design-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['packageIntegrity','manifestFiles','immutableFiles','priorE7AImmutableFilesVerified','productionTestsExecuted','designDecision','findings']}))
