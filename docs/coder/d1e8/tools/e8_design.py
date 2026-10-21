"""E8 design evidence only: decode existing metadata, bind citations, seal/verify design package.
No migration/V2 implementation, Android/device, media, compilation, or dependency actions.
"""
from pathlib import Path
import argparse,hashlib,json,re,struct,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2]
DOCS=[R/('docs/coder/D1_E8_'+n+'_V1.0.md') for n in ['ARCHITECTURE_DECISION','LEGACY_MIGRATION_PLAN','WRITER_V2_CONTRACT','TEST_DESIGN']]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=sha(raw))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def check(x):assert row(R/x['path'])==x,x['path']
def analyze():
 assert not (B/'evidence/e8-design-seal.json').exists()
 originals=(B/'reference/original-paths.txt').read_text(encoding='utf-8').splitlines();sources=[]
 for original in originals:
  a=R/original;b=B/'reference'/a.name;assert a.read_bytes()==b.read_bytes();sources.append(dict(original=row(a),copy=row(b)))
 text=(B/'reference/normalMp4SixRealFrames-post-state-stdout.txt').read_text(encoding='utf-8')
 segment=text.split('HEX_BEGIN|files/e4a_output_budget/ledger.bin',1)[1].split('HEX_END',1)[0]
 raw=bytes.fromhex(segment);assert len(raw)==1011 and sha(raw)=='f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba'
 lines=raw.decode('ascii').splitlines();assert lines[0]=='E4A1 730a73e1-50e1-4198-a515-047104f00e31 4194304 2097152 128';assert len(lines)==7
 chain=sha((lines[0]+'\n').encode('ascii'));entries={};events=[]
 for line in lines[1:]:
  payload,actual=line.rsplit(' ',1);assert actual==sha((chain+' '+payload).encode('ascii'));chain=actual;p=payload.split(' ')
  if p[0]=='R':assert len(p)==3 and p[1] not in entries;entries[p[1]]=dict(batch=p[2],length=None)
  else:
   assert len(p)==5 and p[0]=='S' and p[1] in entries and entries[p[1]]['length'] is None
   entries[p[1]].update(state=p[2],length=int(p[3]),sha256=p[4]);assert p[2] in ['READY','ABORTED']
  events.append(dict(payload=payload,chain=chain))
 expected={'86cafdb3-0fc4-447d-920b-b19c884bf494':0,'0ee15550-8952-4639-91ac-83ab9d14d36c':53651,'fbe4330b-111b-4b05-a93c-467413eb8d34':53567}
 assert {k:v['length'] for k,v in entries.items()}==expected
 assert sum(v['length'] for v in entries.values())==107218
 proof=(B/'reference/archive-proof.txt.bin').read_bytes().decode('ascii').splitlines();assert proof[3]=='originalCloseACK=false' and proof[4]=='fence=662e9ecd-bede-42e6-bb58-ce81d668ff44' and proof[5]==lines[2]
 owner=(B/'reference/archive-recovery.owner.bin').read_bytes().decode('ascii');assert owner=='E5A_N2_RECOVERY_OWNER_V1 8c6673b7-38a5-4a24-838d-ca8466d8b75f 4869 10221 com.videokit.app 1792224193301\n'
 guard=(B/'reference/archive-guard.identity.bin').read_bytes();assert len(guard)==82 and guard[:4]==b'E5B1' and struct.unpack('>H',guard[4:6])[0]==36
 assert guard[6:42].decode('ascii') in expected
 ids=[struct.unpack('>qqi',guard[42:62]),struct.unpack('>qqi',guard[62:82])];assert ids==[(64522,20304,10221),(64522,20385,10221)]
 current=json.loads((B/'reference/control-01-snapshot.json').read_text(encoding='utf-8'))['fields']
 for k,v in dict(sequence='9',holder='CLOSED',originalOperationsReturned='true',safeToFinish='true',history='AVAILABLE',returned='0',matches='0',proc='NOT_REQUESTED',birthGeneration='NOT_RECORDED',grant='NONE').items():assert current[k]==v
 historic=(B/'reference/normalMp4SixRealFrames-instrumentation-stdout.txt').read_text(encoding='utf-8');assert 'exitTimestamp=1792224193337 reason=10 status=0 absent=true' in historic
 sourceFiles=['src/com/videokit/spike/e4/E5N2Recovery.java','src/com/videokit/spike/e4/E5AFinalObservation.java','src/com/videokit/spike/e4/E5AAdmission.java','src/com/videokit/spike/e4/E5BGuard.java','src/com/videokit/spike/e4/E4OutputBudget.java','android/com/videokit/spike/e4/E4Session.java','upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java']
 production=[row(R/'docs/coder/d1e7a'/n) for n in sourceFiles]
 old=R/'docs/coder/d1e7a/evidence/e7a-freeze.json';assert sha(old.read_bytes())=='1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76';f=json.loads(old.read_text(encoding='utf-8'))
 for x in f['immutableFiles']:check(x)
 write(B/'evidence/existing-evidence-analysis.json',dict(schema=1,status='PASS_EXISTING_METADATA_ONLY',ledger=dict(bytes=1011,sha256=sha(raw),events=events,entries=entries,consumed=107218,reserved=0,reservations=3,settlements=3),legacyGuardIds=ids,legacyFence=proof[4][6:],legacyOwnerBytes=104,originalCloseACK=False,currentManagedDiagnostic=current,legacyBirth='NOT_RECORDED',oldAVIExactPredicate='UNKNOWN',scope='Independent reconstruction of already archived metadata and source binding, NOT migration/V2 tests or new device observations',sources=sources,productionSources=production,frozenE7A=dict(seal=row(old),immutableFilesVerified=len(f['immutableFiles']),mutation=False),androidTests=0,builds=0,mediaReads=0,migrationExecutions=0))
 requirements=[
 ('E8-R01','历史当前分离','ARCHITECTURE_DECISION','SUPPORTED','E5C_N2_ABORT/E6B_NORMAL/E7A_MANAGED'),
 ('E8-R02','合作与主动同UID不同模型','ARCHITECTURE_DECISION','PROPOSED_SCOPE','E4OutputBudget cooperative contract'),
 ('E8-R03','精确一次性终局验收而非盲查旧PID','ARCHITECTURE_DECISION','PROPOSED','actual closed terminal source + external accepted reports'),
 ('E8-R04','原账户三R三S/消费107218/产物保留','LEGACY_MIGRATION_PLAN','SUPPORTED_BASELINE_PROPOSED_ACTION','existing ledger HEX'),
 ('E8-R05','不可逆对象/变化/保留/风险/验证/批准','LEGACY_MIGRATION_PLAN','PROPOSED_UNAPPROVED','exact policy scope and noncircular proposal/approval manifest'),
 ('E8-R06','当前guard fence ledger pending资源实际返回','LEGACY_MIGRATION_PLAN','PROPOSED_RETAINS_ORIGINAL_BOUNDARIES','E5BGuard/E5AFinalObservation/E4OutputBudget'),
 ('E8-R07','不补旧birth不补old closeACK','ARCHITECTURE_DECISION','SUPPORTED_LIMIT','104B original owner, proof originalCloseACK=false'),
 ('E8-R08','V2事前boot/start/Binder参与者','WRITER_V2_CONTRACT','PROPOSED_PLATFORM_VALIDATION_REQUIRED','existing linkToDeath source; local SDK symbol only'),
 ('E8-R09','部分提交实际close UNKNOWN与发布自证循环','WRITER_V2_CONTRACT','PROPOSED_FAIL_CLOSED','existing guard unlock precedes close; no self-certifying receipt'),
 ('E8-R10','原host跨进程重启PID复用淘汰','TEST_DESIGN','DESIGNED_NOT_EXECUTED','L03-L05/V01-V06'),
 ('E8-R11','幂等重放兼容回滚篡改成本','TEST_DESIGN','DESIGNED_NOT_EXECUTED','L07-L11/V07/S01-S02/C01'),
 ('E8-R12','证据不足外证或原账户隔离','LEGACY_MIGRATION_PLAN','PROPOSED','no deletion/budget reset; no approval replaces live unknown'),
 ('E8-R13','无设备APK媒体迁移执行/旧冻结/P0','TEST_DESIGN','ACTUAL_THIS_BATCH','E7A200 immutable verified; design-only tools'),
 ('E8-R14','完整交付后暂停不自动下一批','TEST_DESIGN','REQUIRED_FINAL_STATE','human instruction relayed by coordinator')]
 rows=[]
 for id,requirement,doc,status,basis in requirements:
  path=R/('docs/coder/D1_E8_'+doc+'_V1.0.md');assert path.exists();rows.append(dict(id=id,requirement=requirement,status=status,document=row(path),basis=basis))
 write(B/'evidence/requirements-evidence-matrix.json',dict(schema=1,requirements=rows,implementation='NOT_STARTED',productionTests='NOT_RUN',designScenarioGroups=22,approval='NOT_GRANTED_BY_E8',D1='NOT_PASSED',M0='NOT_STARTED',afterDelivery='PAUSED_WAIT_HUMAN'))
 tests=DOCS[3].read_text(encoding='utf-8');groups=re.findall(r'^\|(L\d+|V\d+|S\d+|C\d+) ',tests,re.M);assert len(groups)==22 and len(set(groups))==22
 write(B/'evidence/design-check-results.json',dict(schema=1,status='PASS_DESIGN_AND_EXISTING_METADATA_CONSISTENCY_ONLY',requirements=14,scenarioGroups=groups,ledgerEventsVerified=6,reservations=3,settlements=3,consumption=107218,reserved=0,productionOrAndroidTestCasesExecuted=0,newAPKs=0,builds=0,deviceCalls=0,mediaReads=0,migrationExecutions=0,V2Implemented=False,afterDelivery='PAUSED_WAIT_HUMAN'))
 print('PASS existing metadata: six chain events/three R+S/107218+reserved0; 14 requirements/22 DESIGNED groups; production tests0')
def freeze():
 assert not (B/'evidence/e8-design-seal.json').exists()
 assert json.loads((B/'evidence/design-check-results.json').read_text())['productionOrAndroidTestCasesExecuted']==0
 paths=sorted([p for folder in ['reference','tools','evidence'] for p in (B/folder).rglob('*') if p.is_file()]+DOCS+[R/'docs/milestones/D1_E8_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E8_TESTER_REQUIREMENTS_V1.0.md'])
 entries=[row(p) for p in paths];assert sum(x['bytes'] for x in entries)<4*1024*1024
 manifest=B/'evidence/design-manifest.json';write(manifest,dict(schema=1,files=entries))
 z=B/'artifacts/D1-20261017-E8-design.zip';z.parent.mkdir()
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED) as out:
  for p in paths:out.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 seal=dict(schema=1,candidateId='D1-20261017-E8-DESIGN',state='FROZEN_DESIGN_COMPLETE_DEVELOPMENT_PAUSED',documents=[row(p) for p in DOCS],manifest=row(manifest),designZip=row(z),immutableFiles=entries+[row(manifest),row(z)],implementation='NOT_STARTED',approval='NOT_GRANTED',builds=0,deviceCalls=0,mediaReads=0,migrationExecutions=0,E6B_OBS_F01='OPEN_DESIGN_PROPOSED',D1='NOT_PASSED',M0='NOT_STARTED',next='WAIT_HUMAN_NO_AUTO_IMPLEMENTATION')
 write(B/'evidence/e8-design-seal.json',seal);print(json.dumps(dict(seal=row(B/'evidence/e8-design-seal.json'),designZip=seal['designZip'],files=len(entries),immutableFiles=len(seal['immutableFiles']))))
def verify():
 p=B/'evidence/e8-design-seal.json';seal=json.loads(p.read_text(encoding='utf-8'))
 for x in seal['immutableFiles']:check(x)
 m=json.loads((R/seal['manifest']['path']).read_text(encoding='utf-8'))
 with zipfile.ZipFile(R/seal['designZip']['path']) as z:
  assert z.namelist()==[x['path'] for x in m['files']]
  for x in m['files']:raw=z.read(x['path']);assert len(raw)==x['bytes'] and sha(raw)==x['sha256']
 print(json.dumps(dict(status='PASS',mode='READ_ONLY',seal=row(p),files=len(m['files']),immutableFiles=len(seal['immutableFiles']),implementation='NOT_STARTED',afterDelivery='PAUSED_WAIT_HUMAN')))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['analyze','freeze','verify']);a=p.parse_args();{'analyze':analyze,'freeze':freeze,'verify':verify}[a.mode]()
