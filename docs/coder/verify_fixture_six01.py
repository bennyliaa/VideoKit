from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[2];E=R/'docs/coder/d1fixture-six01-evidence';OUTPUT=R/'docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4';seal=E/'fixture-six01-freeze.json';reads=[]
def sha(p):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b);n+=len(b)
 if p==OUTPUT:reads.append({'kind':'ORIGINAL_MEDIA_HASH_READ','bytes':n,'originalDriverInputMeterChanged':False})
 return h.hexdigest()
assert sha(seal)=='ffd195f62f0fa0f6266ff2683053dd578b35cac8999acc0b747e0ec1c62c86c4';v=json.loads(seal.read_text());assert len(v['files'])==38
assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in v['files'])
assert bool(OUTPUT.stat().st_file_attributes&1)
with zipfile.ZipFile(R/v['archive']['path']) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==37
 reads.append({'kind':'ARCHIVE_MEDIA_CRC_READ','bytes':8849,'originalDriverInputMeterChanged':False})
 for x in v['files'][:-1]:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
 reads.append({'kind':'ARCHIVE_MEDIA_MEMBER_HASH_READ','bytes':8849,'originalDriverInputMeterChanged':False})
tool=R/'docs/coder/d1fixture-tool02/evidence/fixture-tool02-freeze.json';assert sha(tool)==v['tool02SealSha256'];t=json.loads(tool.read_text());assert len(t['files'])==2774 and all(sha(R/x['path'])==x['sha256'] for x in t['files'])
assert v['externalPreservationLedger']['originalMediaDirectBytes']==35396 and v['externalPreservationLedger']['archiveCopyMediaBytes']==17698
receipt={'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':'D1_FIXTURE_SIX01_GENERATE','status':'GENERATED_CANDIDATE_NOT_QUALIFIED_PRESERVED','sealSha256':sha(seal),'frozenRowsUnchanged':38,'zipMembersMatched':37,'tool02RowsUnchanged':2774,'mediaPath':OUTPUT.relative_to(R).as_posix(),'mediaBytes':8849,'mediaSha256':v['output']['sha256'],'readOnlyAttribute':True,'newGeneratorOrEncoderParserDecoderCalls':0,'newProcessOrDeviceOrOldSessionActions':0,'thisPostfreezePreservationReads':reads,'thisAdditionalOriginalMediaHashBytes':8849,'thisAdditionalArchiveMediaBytes':17698,'cumulativeExternalOriginalMediaReadBytesIncludingSealedLedger':35396+8849,'externalReadsAreLogicalApplicationPayloadNotPhysicalDiskTraffic':True,'driver8MiBOriginalInputLedgerUnchanged':340626,'independentContainerFormatOrMedia3Qualification':'NOT_RUN','controllerExecEvidence':{'toolChunk':'2913d7','originalPythonControllerExitCode':0,'generationPopenNaturalExitCode':0,'generationInvocations':1},'D1':'NOT_PASSED','M0':'NOT_STARTED'}
p=R/'docs/coder/D1_FIXTURE_SIX01_GENERATE_POST_FREEZE_RECEIPT.json';assert not p.exists();p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),**receipt},ensure_ascii=False,indent=2))
