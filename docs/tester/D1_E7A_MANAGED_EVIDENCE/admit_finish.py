"""Independent review of the already archived safe snapshot; no device operations."""
from pathlib import Path
import json,hashlib,re
E=Path(__file__).resolve().parent
raw=(E/'control-01-response-stdout.txt').read_bytes();snapshot=(E/'control-01-snapshot.json').read_bytes();x=json.loads(snapshot);f=x['fields']
assert x['rawResponseSha256']==hashlib.sha256(raw).hexdigest()
assert f['handle']=='9f19bfb5-60e0-4bcc-9666-852409cfe3b4' and f['sequence']=='9'
for k,v in dict(phase='RETURNED',verdict='QUALIFIED_DIAGNOSTIC',reason='ACTUAL_RETURNED',holder='CLOSED',originalOperationsReturned='true',safeToFinish='true',finishClaimed='false',admission='NONE',code='NO_UNIQUE_MATCH_MISSING',history='AVAILABLE',returned='0',matches='0',proc='NOT_REQUESTED').items():assert f[k]==v,(k,f[k])
assert 'BLOCKED_CURRENT_GATE' in x['rawSnapshot'] and 'grant=NONE' in x['rawSnapshot']
with (E/'finish-admission.json').open('x',encoding='utf-8') as out:
    json.dump(dict(admitted=True,snapshotFile='control-01-snapshot.json',snapshotFileSha256=hashlib.sha256(snapshot).hexdigest(),handle=f['handle'],archivedSequence=9,reason='ORIGINAL_OPERATIONS_RETURNED_AND_ORIGINAL_HOLDER_CLOSED_EXACT_ARCHIVED_SNAPSHOT',deathGate='BLOCKED_NO_HISTORY_ROWS',productAdmission=False,controlUsed=1,remainingBeforeAck=5),out,ensure_ascii=False,indent=2);out.write('\n')
print('ACK_FINISH_ADMITTED_EXACT_ARCHIVED_SEQUENCE_9; diagnostic collection qualified, death gate blocked, product admission none')
