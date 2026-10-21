"""Static design/source/inventory verification only; no product or model execution, build, device or media."""
from pathlib import Path
import hashlib,json,zipfile,re
R=Path(__file__).resolve().parents[3];B='docs/coder/d1e8a/'
def sha(b):return hashlib.sha256(b).hexdigest()
def raw(p):
    assert not str(p).lower().endswith(('.mp4','.avi','.mkv')),'MEDIA_FORBIDDEN'
    return (R/p).read_bytes()
def obj(p):return json.loads(raw(p))
def check(x):
    b=raw(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
seal=B+'evidence/e8a-design-seal.json';sealHash='dfbb91fcc193d65b599d88e9399f66edb115e0331e85a656f1b83d0ba54d1e86'
assert sha(raw(seal))==sealHash
f=obj(seal);assert len(f['immutableFiles'])==42
for x in f['immutableFiles']:check(x)
manifest=obj(f['manifest']['path']);assert len(manifest['files'])==40
with zipfile.ZipFile(R/f['designZip']['path']) as z:
    assert z.namelist()==[x['path'] for x in manifest['files']] and len(set(z.namelist()))==40
    for x in manifest['files']:
        assert not x['path'].lower().endswith(('.mp4','.avi','.mkv'))
        b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
for x in f['documents']:check(x)
baselines={}
for key,path,want in [('E8','docs/coder/d1e8/evidence/e8-design-seal.json','bba077cd93cdaf1e6b2c172c213f236834ce218e0ea7b0447dd361b020b30b4f'),('E7A','docs/coder/d1e7a/evidence/e7a-freeze.json','1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76')]:
    assert sha(raw(path))==want;old=obj(path)
    for x in old['immutableFiles']:check(x)
    baselines[key]=dict(sealSha256=want,immutableFiles=len(old['immutableFiles']))
for original in raw(B+'reference/original-paths.txt').decode().splitlines():
    copy=B+'reference/'+Path(original).name;assert raw(original)==raw(copy),(original,copy)
derivation=obj(B+'evidence/document-derivation.json');assert len(derivation['documents'])==4
for d in derivation['documents']:
    for key in ['previous','current','diff']:check(d[key])
inventory=obj(B+'evidence/proposed-write-and-approval-inventory.json')
deviceFiles=sum(x['maxFiles'] for x in inventory['device']);deviceBytes=sum(x['maxFiles']*x['maxBytes'] for x in inventory['device'])
externalFiles=sum(x['maxFiles'] for x in inventory['external']);externalBytes=sum(x['maxFiles']*x['maxBytes'] for x in inventory['external'])
assert deviceFiles==inventory['deviceMaxFiles']==4 and deviceBytes==inventory['deviceMaxBytes']==8448
assert inventory['deviceNewDirectories']==3
assert externalFiles==inventory['externalMaxFiles']==20 and externalBytes==inventory['externalFileContentMax']==155648
assert inventory['externalMetadataHardLimit']==196608 and externalBytes<196608 and inventory['rawLogHardLimit']==1048576
assert inventory['actorMax']==2 and inventory['commandsPerActorMax']==8 and inventory['statusPerActorMax']==3
assert inventory['qualificationPhasesPerActor']==2 and inventory['qualificationNsPerPhase']==10000000000 and inventory['holderDesignMax']==48
assert inventory['activationAssetMax']==24576 and not inventory['approvalTokenGenerated']
states=obj(B+'evidence/state-transition-contract.json');assert len(states['states'])==16
byState={x['state']:x for x in states['states']};assert len(byState)==16
for name in ['COMMITTED_UNRETURNED','RETURN_OBSERVED','NORMAL_FINISH_CONFIRMED','FINAL_ACCEPTED','QUARANTINED','REGISTRY_UNCERTAIN','RETURNED_LATE_NONQUALIFIED','TERMINATED_WITHOUT_RETURN_RECOVERY_REQUIRED']:assert byState[name]['activation']=='NO'
assert byState['ACTIVATION_PACKAGE_APPROVED']['activation']=='ONLY_WITH_CURRENT_HOST_PROOF'
binding=obj(B+'evidence/actor-binding-contract.json');assert not binding['valuesAssigned'] and binding['implementation']=='NOT_STARTED'
for name in ['registryID','migrationID','actorOrdinal','attemptUUID','handleUUID','commandSeq','stateSeq','prepareAppSHA','prepareTestSHA','actualUID','actualPID','bootSourceKind','bootValue','starttime','participants','reserveSHA','originalOperationReturns','normalFinishEvidence']:assert name in binding['requiredFields']
reader=obj(B+'evidence/real-old-reader-inspection.json')
for name in ['observer','admission']:check(reader[name])
observer=raw(reader['observer']['path']).decode();assert 'requireRecoveryWriterDead(writer)' in observer
for marker in reader['newMarkersNotRead']:assert marker not in observer
assert not reader['actualReaderExecuted'] and reader['currentHistory0IsNotCompatibilityGate']
guard=obj(B+'evidence/guard-unlock-close-counterexample.json');check(guard['guardClose']['source'])
guardText=raw(guard['guardClose']['source']['path']).decode();assert guardText.index('io.unlock(descriptor)')<guardText.index('io.close(descriptor)') and guard['runtimeCasesExecuted']==0
deployment=obj(B+'evidence/existing-deployment-boundary-inspection.json');check(deployment['source']);assert deployment['newE8AAllowlistGate']=='NOT_IMPLEMENTED'
matrix=obj(B+'evidence/requirements-evidence-matrix.json');assert len(matrix['requirements'])==16
for row in matrix['requirements']:check(row['document'])
design=raw('docs/coder/D1_E8A_TEST_DESIGN_V1.0.md').decode();groups=re.findall(r'^\|([AD]\d{2})\|',design,re.M)
assert len(groups)==len(set(groups))==32 and groups==['A'+str(i).zfill(2) for i in range(1,24)]+['D'+str(i).zfill(2) for i in range(1,10)]
checks=obj(B+'evidence/design-check-results.json');assert checks['scenarioGroupsDesigned']==groups and checks['productionOrAndroidCasesExecuted']==0
ledger=obj('docs/coder/d1e8/evidence/existing-evidence-analysis.json')['ledger'];assert ledger['consumed']==107218 and ledger['reserved']==0 and ledger['reservations']==ledger['settlements']==3
result=dict(packageIntegrity='PASS',manifestFiles=40,immutableFiles=42,sealSha256=sealHash,designZip=f['designZip'],priorBaselines=baselines,costs=dict(deviceFiles=deviceFiles,deviceContentBytes=deviceBytes,newDeviceDirectories=3,externalNamedFiles=externalFiles,externalContentBytes=externalBytes,externalMetadataHardLimit=196608,rawLogHardLimit=1048576,activationAssetBytes=24576,maxActors=2,maxCommandsPerActor=8,maxStatusesPerActor=3,phaseQualificationNs=10000000000,phasesPerActor=2,holderDesignMax=48),oldFindings=dict(E8_F01='CLOSED_IN_REVISED_DESIGN_ONLY',E8_F02='CLOSED_IN_REVISED_DESIGN_ONLY'),newBlockingFindings=[],implementationAdmission='SUPPORTED_FOR_SEPARATE_CONSOLIDATED_IMPLEMENTATION_DISPATCH',migrationAdmission=False,buildAssessment='TWO_TRUSTED_PUBLICATIONS_JUSTIFIED_FOR_PINNED_FINAL_CATALOG; TWO_FULL_SOURCE_NATIVE_RECOMPILES_NOT_REQUIRED; SHARE_VERIFIED_CODE_AND_LIMIT_ACTIVATION_TO_CATALOG_ROLE_PACKAGING_AND_NEEDED_VALIDATION',scenarioGroupsDesigned=groups,productionTestsExecuted=0,testerAdbCalls=0,testerMediaOrExportReadBytes=0,testerBuildModelMigrationRuns=0,oldConsumption=107218,reserved=0,longTermE6B_OBS_F01='OPEN',D1='NOT_PASSED',M0='NOT_STARTED')
Path(__file__).with_name('identity-and-design-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['packageIntegrity','manifestFiles','immutableFiles','oldFindings','newBlockingFindings','implementationAdmission','costs']}))
