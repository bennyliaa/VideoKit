"""Design/source inspection and immutable packaging only. Does not implement or execute the migration protocol."""
from pathlib import Path
import argparse,ast,difflib,hashlib,json,re,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2]
KINDS=['ARCHITECTURE_DECISION','LEGACY_MIGRATION_PLAN','WRITER_V2_CONTRACT','TEST_DESIGN']
DOCS=[R/('docs/coder/D1_E8A_'+x+'_V1.0.md') for x in KINDS]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=sha(raw))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def check(x):assert row(R/x['path'])==x,x['path']
def excerpt(p,first,last):
 lines=p.read_text(encoding='utf-8').splitlines();return dict(source=row(p),first=first,last=last,lines=lines[first-1:last])
def analyze():
 assert not (B/'evidence/e8a-design-seal.json').exists()
 sources=[]
 for original in (B/'reference/original-paths.txt').read_text(encoding='utf-8').splitlines():
  a=R/original;b=B/'reference'/a.name;assert a.read_bytes()==b.read_bytes();sources.append(dict(original=row(a),copy=row(b)))
 # Inspect the REAL frozen readers and guard source, not a new policy simulator.
 observer=B/'reference/E5AFinalObservation.java';admission=B/'reference/E5AAdmission.java';guard=B/'reference/E5BGuard.java'
 observerText=observer.read_text(encoding='utf-8');admissionText=admission.read_text(encoding='utf-8');guardText=guard.read_text(encoding='utf-8')
 newMarkers=['legacy-acceptance','n2-v2.acceptance','n2-v2.commit','LegacyRetirementGateABI','revoked.json']
 for marker in newMarkers:assert marker not in observerText and marker not in admissionText
 for enumeration in ['Files.walk(','Files.list(','Files.newDirectoryStream(']:assert enumeration not in observerText
 assert 'platform.requireRecoveryWriterDead(writer)' in observerText
 assert 'E5A_INDEPENDENT_FINAL_OBSERVATION_REQUIRED' in admissionText
 closeBody=guardText[guardText.index('public void close()'):guardText.index('public static final class Policy')]
 assert closeBody.index('io.unlock(descriptor)')<closeBody.index('io.close(descriptor)')
 oldreader=dict(status='SUPPORTED_STATIC_SOURCE_BOUNDARY_NOT_RUNTIME_EXECUTION',observer=row(observer),admission=row(admission),newMarkersNotRead=newMarkers,noDirectoryEnumeration=True,oldHistoryStillRequired=True,currentHistory0IsNotCompatibilityGate=True,conclusion='Old code does not automatically reject a new schema or marker. A managed compatible-version boundary is necessary.',actualReaderExecuted=False)
 write(B/'evidence/real-old-reader-inspection.json',oldreader)
 lines=guardText.splitlines();line=next(i+1 for i,s in enumerate(lines) if 'public void close()' in s)
 write(B/'evidence/guard-unlock-close-counterexample.json',dict(kind='FINITE_DESIGN_COUNTEREXAMPLE_BOUND_TO_REAL_SOURCE_NOT_INJECTION',guardClose=excerpt(guard,line,line+7),sameDeviceObservation=['identical acceptance bytes','identical commit bytes','guard lock can be acquired'],stateA='actual original guard close returned',stateB='unlock returned but original raw/dup close UNKNOWN',inference='Device content and obtainable lock cannot distinguish A/B; actor authority/return evidence is mandatory',runtimeCasesExecuted=0))
 deployment=B/'reference/execute_managed.py';s=deployment.read_text(encoding='utf-8');ast.parse(s)
 assert "['install','-r',a['path']]" in s and "sha(b)==a['sha256']" in s and "'/base.apk'" in s
 depLines=s.splitlines();selected=[dict(line=i+1,text=line) for i,line in enumerate(depLines) if any(t in line for t in ["sha(b)==a['sha256']","'/base.apk'","['install','-r'","versionCode=10 "])]
 write(B/'evidence/existing-deployment-boundary-inspection.json',dict(status='EXISTING_FLOW_SOURCE_AND_RECORDED_E7A_PRECEDENT_ONLY',source=row(deployment),lines=selected,newE8AAllowlistGate='NOT_IMPLEMENTED',highVersionOldCodeTest='DESIGNED_NOT_EXECUTED',conclusion='Existing process checks exact local APK and installed base.apk; E8A must add immutable allowlist/role/source-review checks, not rely only on version.'))
 baseline=R/'docs/coder/d1e8/evidence/e8-design-seal.json';assert sha(baseline.read_bytes())=='bba077cd93cdaf1e6b2c172c213f236834ce218e0ea7b0447dd361b020b30b4f'
 old=json.loads(baseline.read_text(encoding='utf-8'))
 for x in old['immutableFiles']:check(x)
 e7a=R/'docs/coder/d1e7a/evidence/e7a-freeze.json';assert sha(e7a.read_bytes())=='1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'
 old7=json.loads(e7a.read_text(encoding='utf-8'))
 for x in old7['immutableFiles']:check(x)
 write(B/'evidence/frozen-baseline-readonly.json',dict(status='PASS',E8=dict(seal=row(baseline),immutableFilesVerified=len(old['immutableFiles'])),E7A=dict(seal=row(e7a),immutableFilesVerified=len(old7['immutableFiles'])),mutation=False))
 inherited=json.loads((B/'reference/existing-evidence-analysis.json').read_text(encoding='utf-8'))
 assert inherited['ledger']['consumed']==107218 and inherited['ledger']['reserved']==0 and len(inherited['ledger']['events'])==6 and not inherited['originalCloseACK']
 stateRows=[
 ('ALLOTTED_UNBOUND','external reserve allocation','none','NO','read-only identify only'),
 ('IDENTITY_IO_ACTIVE','original identity handles still owned','none','NO','cannot finish while identity operation unresolved'),
 ('BOUND_IDLE','identity actual returned + external bound reserve','none','NO','one exact EXECUTE or safe closed-ingress abort'),
 ('EXECUTE_RESERVED','accepted command and original queue reservation','possibly none','NO','do not infer safe from EMPTY before worker starts'),
 ('INTENT_CREATING','actor identity file IO in flight','missing/partial/full intent','NO','retain original; partial is not returned'),
 ('PREPARED','payload may be complete','intent+payload','NO','no commit or return implication'),
 ('COMMIT_CREATING','commit IO may be partial','partial/full commit','NO','partial records isolated'),
 ('COMMITTED_UNRETURNED','commit complete, close/sync may be UNKNOWN','valid complete content','NO','obtainable lock is not return'),
 ('RETURN_OBSERVED','exact original all holder/calls returned','valid content','NO','archive exact actor/seq before finish ACK'),
 ('NORMAL_FINISH_CONFIRMED','actual normal finish for returned actor','valid content','NO','independent acceptance required'),
 ('FINAL_ACCEPTED','sealed actor-final catalog and H_actor','valid bound content','NO','prepare release remains unable to activate'),
 ('ACTIVATION_PACKAGE_APPROVED','trusted compatible code pins final catalog','exact bound intents/payload/commit','ONLY_WITH_CURRENT_HOST_PROOF','current guard/fence/ledger/pending/actual returns still required'),
 ('RETURNED_LATE_NONQUALIFIED','actual returned but deadline outcome remains PENDING','any known content','NO','qualified distinct recovery actor required'),
 ('TERMINATED_WITHOUT_RETURN_RECOVERY_REQUIRED','precise death and all participant capability disposition','any known content','NO','never change prior Java close to returned; distinct actor2 required'),
 ('QUARANTINED','live/unknown original actor','any content','NO','no new actor or product grant'),
 ('REGISTRY_UNCERTAIN','missing or unverified management authority','any content','NO','no content-based authority reconstruction')]
 write(B/'evidence/state-transition-contract.json',dict(schema=1,kind='NORMATIVE_DESIGN_NOT_EXECUTED_STATE_MACHINE',authority='LOCAL_TRUSTED_EXTERNAL_REGISTRY_THEN_FROZEN_ACTIVATION_PACKAGE',states=[dict(state=a,basis=b,device=c,activation=d,next=e) for a,b,c,d,e in stateRows],retirementHistory='Permanent accepted fact; no wall-clock expiry or repeated retired writer history',managerOffline='Blocks before final trusted catalog; accepted final catalog in trusted activation APK can be verified offline',runtimeTests=0))
 device=[('actors/0001.intent',1,2048),('actors/0002.intent',1,2048),('n2-v2.acceptance',1,4096),('n2-v2.commit',1,256)]
 external=[('descriptor.json',1,8192),('authorization-reference.json',1,4096),('prepare-deployment.json',1,8192),('activation-release.json',1,8192),('registry.events.jsonl',1,32768),('registry.checkpoint.json',1,4096),('final.acceptance.json',1,16384),('final.seal.json',1,8192)]+[('actors/<A>/'+n,2,size) for n,size in [('reserve.json',4096),('identify.json',4096),('returned.json',8192),('finish.json',4096),('termination.json',4096),('commands.jsonl',8192)]]
 assert sum(n for _,n,_ in device)==4 and sum(n*size for _,n,size in device)==8448
 assert sum(n for _,n,_ in external)==20 and sum(n*size for _,n,size in external)==155648
 write(B/'evidence/proposed-write-and-approval-inventory.json',dict(schema=1,state='PROPOSED_NO_ACTUAL_IDENTIFIERS_OR_APPROVAL',devicePrefix='files/e4a_output_budget/legacy-acceptance/<M>/',device=[dict(path=p,maxFiles=n,maxBytes=size) for p,n,size in device],deviceMaxFiles=4,deviceMaxBytes=8448,deviceNewDirectories=3,externalPrefix='D:/CodexProjects/VideoKit/docs/tester/D1_E8A_LEGACY_MIGRATION_REGISTRY/<M>/',external=[dict(path=p,maxFiles=n,maxBytes=size) for p,n,size in external],externalMaxFiles=20,externalFileContentMax=155648,externalMetadataHardLimit=196608,rawLogHardLimit=1048576,actorMax=2,commandsPerActorMax=8,statusPerActorMax=3,qualificationPhasesPerActor=2,qualificationNsPerPhase=10000000000,holderDesignMax=48,futureBuildStages=['one prepare dual-APK build','one later activation dual-APK build'],actualBuilds=0,actualWritesToDevice=0,approvalTokenGenerated=False,activationAssetMax=24576,approvalScope=['exact legacy terminal rule','new actor and external registry','bounded recovery/termination disposition','full new file and directory inventory','compatible-only deployment and rollback exclusion','actual implementation and descriptor scope match']))
 binding=['registryID','migrationID','actorOrdinal','attemptUUID','handleUUID','commandSeq','stateSeq','task','policyID','descriptorSHA','prepareAppSHA','prepareTestSHA','actualUID','actualPID','actualProcess','bootSourceKind','bootValue','starttime','participants','reserveSHA','originalOperationReturns','holderStates','normalFinishEvidence','terminationDispositionIfAny']
 write(B/'evidence/actor-binding-contract.json',dict(schema=1,requiredFields=binding,valuesAssigned=False,firstApplicationWriteRequires='external BOUND and returned identity phase',returnAuthority='actual source-bound managed response and externally stored evidence; never device completed bit',nextHostAuthority='trusted activation package exact final catalog; all actors fully accounted',noSelfCloseReceipt=True,lateReturnNeverPromoted=True,previousUnknownDeathDoesNotBecomeJavaClose=True,implementation='NOT_STARTED'))
 refs=[]
 for kind,doc in zip(KINDS,DOCS):
  previous=R/('docs/coder/D1_E8_'+kind+'_V1.0.md');before=previous.read_text(encoding='utf-8').splitlines(True);after=doc.read_text(encoding='utf-8').splitlines(True)
  out=B/'evidence/diffs'/(kind+'.diff');out.parent.mkdir(exist_ok=True)
  with out.open('x',encoding='utf-8',newline='\n') as f:f.write(''.join(difflib.unified_diff(before,after,fromfile=str(previous.relative_to(R)),tofile=str(doc.relative_to(R)))))
  refs.append(dict(previous=row(previous),current=row(doc),diff=row(out)))
 write(B/'evidence/document-derivation.json',dict(schema=1,status='PASS_EXACT_DOCUMENT_DELTA',documents=refs,productionSourceChanges=0))
 reqs=[
 ('E8A-R01','F01 首写前actor可靠绑定/实际身份phase返回','WRITER_V2_CONTRACT','A01-A04'),
 ('E8A-R02','F01 外部authority/精确handle序号/registry成本','LEGACY_MIGRATION_PLAN','A02-A06/A12-A13'),
 ('E8A-R03','F01 commit齐全/锁可取不是close','ARCHITECTURE_DECISION','A07-A11'),
 ('E8A-R04','F01 跨host缺旧未知回执与管理失联阻断','WRITER_V2_CONTRACT','A10/A13-A14/A21'),
 ('E8A-R05','F01 所有提交切点及无资源队列窗口','LEGACY_MIGRATION_PLAN','A04-A09/A23'),
 ('E8A-R06','F01 活actor与已可靠终止/迟到恢复分开','LEGACY_MIGRATION_PLAN','A15-A19'),
 ('E8A-R07','F01 新恢复actor自己的实际返回与保留旧未知','WRITER_V2_CONTRACT','A16-A19'),
 ('E8A-R08','F01 无自证自身close/无远端根/有限发布','ARCHITECTURE_DECISION','A11-A12/A20-A22'),
 ('E8A-R09','F01 新增4device/20external文件及审批scope','LEGACY_MIGRATION_PLAN','A05-A06/A19/cost audit'),
 ('E8A-R10','F02 真实旧reader不检查新schema','TEST_DESIGN','D01/real source inspection'),
 ('E8A-R11','F02 可执行兼容集合与精确SHA部署','WRITER_V2_CONTRACT','D02-D07'),
 ('E8A-R12','F02 同签名高version旧代码/回退恢复边界','WRITER_V2_CONTRACT','D02/D05/D08-D09'),
 ('E8A-R13','原账户107218/三R三S/档案/oldCloseACKfalse','ARCHITECTURE_DECISION','A19/A22 and inherited baseline'),
 ('E8A-R14','当前每host guards/fence/ledger/pending实际资源','LEGACY_MIGRATION_PLAN','A07-A11/A21-A22'),
 ('E8A-R15','四文档状态表矩阵来源ZIP外seal完整交付','TEST_DESIGN','package read-only verification'),
 ('E8A-R16','只设计无批准token/设备/构建/实现，后续另派','ARCHITECTURE_DECISION','actual current batch scope')]
 write(B/'evidence/requirements-evidence-matrix.json',dict(schema=1,requirements=[dict(id=a,requirement=b,document=row(R/('docs/coder/D1_E8A_'+c+'_V1.0.md')),directBoundaryTestDesign=d,status='DESIGN_REVISED_AWAIT_INDEPENDENT_REVIEW') for a,b,c,d in reqs],sourceEvidence=sources,F01='PROPOSED_CONTRACT_REVISION_NOT_IMPLEMENTED',F02='PROPOSED_COMPATIBLE_DEPLOYMENT_BOUNDARY_NOT_IMPLEMENTED',D1='NOT_PASSED',M0='NOT_STARTED'))
 tests=DOCS[3].read_text(encoding='utf-8');groups=re.findall(r'^\|(A\d+|D\d+)\|',tests,re.M);assert len(groups)==32 and len(set(groups))==32
 write(B/'evidence/design-check-results.json',dict(schema=1,status='PASS_DESIGN_SOURCE_AND_INVENTORY_CONSISTENCY_ONLY',requirements=16,states=len(stateRows),scenarioGroupsDesigned=groups,productionOrAndroidCasesExecuted=0,realOldReaderEvidence='DIRECT_FROZEN_SOURCE_INSPECTION_NOT_RUNTIME',existingDeploymentEvidence='FROZEN_REAL_FLOW_SOURCE_AND_RECORDED_FAST_PATH_NOT_NEW_GATE',inheritedConsumption=107218,inheritedReserved=0,newBuilds=0,newAPKs=0,deviceCalls=0,mediaReads=0,migrationExecutions=0,approvalTokens=0,implementation='NOT_STARTED',next='INDEPENDENT_COMPLETE_DESIGN_REVIEW_THEN_SEPARATE_IMPLEMENTATION_DISPATCH'))
 print('PASS design consistency:16 requirements/16 states/32 DESIGNED groups; device4files8448B; registry20files155648B; production executions0')
def freeze():
 assert not (B/'evidence/e8a-design-seal.json').exists()
 assert json.loads((B/'evidence/design-check-results.json').read_text(encoding='utf-8'))['productionOrAndroidCasesExecuted']==0
 paths=sorted([p for folder in ['reference','tools','evidence'] for p in (B/folder).rglob('*') if p.is_file()]+DOCS+[R/'docs/milestones/D1_E8A_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E8A_TESTER_REQUIREMENTS_V1.0.md'])
 files=[row(p) for p in paths];assert sum(x['bytes'] for x in files)<8*1024*1024
 manifest=B/'evidence/design-manifest.json';write(manifest,dict(schema=1,files=files))
 z=B/'artifacts/D1-20261018-E8A-design.zip';z.parent.mkdir()
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED) as out:
  for p in paths:out.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 write(B/'evidence/e8a-design-seal.json',dict(schema=1,candidateId='D1-20261018-E8A-DESIGN',state='FROZEN_DESIGN_WAIT_INDEPENDENT_REVIEW',documents=[row(p) for p in DOCS],manifest=row(manifest),designZip=row(z),immutableFiles=files+[row(manifest),row(z)],implementation='NOT_STARTED',approval='NOT_GRANTED',newAPKs=0,builds=0,deviceCalls=0,mediaReads=0,migrationExecutions=0,E8_F01='DESIGN_REVISED_PENDING_REVIEW',E8_F02='DESIGN_REVISED_PENDING_REVIEW',E6B_OBS_F01='OPEN',D1='NOT_PASSED',M0='NOT_STARTED',next='WAIT_COORDINATED_DESIGN_REVIEW_NO_AUTO_IMPLEMENTATION'))
 print(json.dumps(dict(seal=row(B/'evidence/e8a-design-seal.json'),designZip=row(z),files=len(files),immutableFiles=len(files)+2)))
def verify():
 p=B/'evidence/e8a-design-seal.json';f=json.loads(p.read_text(encoding='utf-8'))
 for x in f['immutableFiles']:check(x)
 m=json.loads((R/f['manifest']['path']).read_text(encoding='utf-8'))
 with zipfile.ZipFile(R/f['designZip']['path']) as z:
  assert z.namelist()==[x['path'] for x in m['files']]
  for x in m['files']:raw=z.read(x['path']);assert len(raw)==x['bytes'] and sha(raw)==x['sha256']
 print(json.dumps(dict(status='PASS',mode='READ_ONLY',seal=row(p),files=len(m['files']),immutableFiles=len(f['immutableFiles']),implementation='NOT_STARTED',next='WAIT_INDEPENDENT_REVIEW')))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['analyze','freeze','verify']);a=p.parse_args();{'analyze':analyze,'freeze':freeze,'verify':verify}[a.mode]()
