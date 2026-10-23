"""Static exact-byte recovery of an accidental report destination. No rerun."""
from pathlib import Path
import json,hashlib,zipfile
H=Path(__file__).resolve().parent;C=H.parent/'d1android02-readonly-facts-preauth01'
def sha(raw):return hashlib.sha256(raw).hexdigest()
rel='evidence/result.json';target=C/rel
assert target.resolve()==Path('D:/CodexProjects/VideoKit/docs/coder/d1android02-readonly-facts-preauth01/evidence/result.json').resolve()
manifest=json.loads((C/'reference/full-manifest.json').read_bytes());row=next(x for x in manifest['files'] if x['path']==rel)
raw=target.read_bytes();result=json.loads(raw);assert result['schema']=='PREAUTH01_SELFCHECK02_BATCH_RESULT_V1' and result['allPassed'] and len(result['results'])==7
snapshot=H/'evidence/result.json';snapshot.parent.mkdir(parents=True,exist_ok=True);assert not snapshot.exists();snapshot.write_bytes(raw)
archive=C/'readonly-facts-preauth01-blocked-frozen.zip';assert sha(archive.read_bytes())=='e563573ca4d51c428ae7c56d79f4b5b7e03bd6e106157f95286c849a91afed52'
with zipfile.ZipFile(archive) as z:
 assert z.namelist().count(rel)==1;original=z.read(rel)
assert len(original)==row['bytes'] and sha(original)==row['sha256'] and json.loads(original)['schema']=='PREAUTH01_BATCH_RESULT_V1'
assert sha(raw)!=row['sha256'];target.write_bytes(original);assert target.read_bytes()==original
bad=[x['path'] for x in manifest['files'] if sha((C/x['path']).read_bytes())!=x['sha256']]
assert not bad
receipt=dict(schema='SELFCHECK02_ARTIFACT_DESTINATION_RECOVERY_V1',failure='DERIVED_FINAL_RESULT_WRITER_STILL_TARGETED_ORIGINAL_EVIDENCE_RESULT',newExecutionResultPreserved=str(snapshot),newExecutionResultSha256=sha(raw),originalRelativePath=rel,originalWasOverwrittenDuringFinalReport=True,postRunOriginalBadBeforeRecovery=[rel],restorationSourceArchiveSha256=sha(archive.read_bytes()),restoredExactOriginalSha256=sha(original),original56BadAfterRecovery=bad,dynamicRerun=False,driverRuntimeSourcesNotChanged=True,qualificationAndSixFunctionalGroups='PASS_IN_ORIGINAL_NEW_RESULT',wholeDelivery='LIMITED_FUNCTIONAL_PASS_WITH_AUXILIARY_ARTIFACT_ROUTING_FAILURE',newResourceUnknown=False)
(H/'evidence/artifact-destination-recovery.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(receipt))
