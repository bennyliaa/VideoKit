"""Independent event/expected-error/WAITING audit over tester copies only."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;ARCH=OUT/'original-output-archive';RUN='e3-11a896d3c2c34483ba2dff60fa63f5c8';P='runs/'+RUN+'/'
sem=json.loads((OUT/'semantic-audit.json').read_bytes());cost=dict(sem['resultReadUsage']);cost['bytes']+=(OUT/'semantic-audit.json').stat().st_size;cost['files']+=1
def load(p,json_value=True):
    size=p.stat().st_size;assert cost['files']<512 and cost['bytes']+size<=6291456
    cost['files']+=1;cost['bytes']+=size;b=p.read_bytes();return json.loads(b) if json_value else b
pre=load(ARCH/P/'result-before-close.json');raw=load(ARCH/P/'global.log',False);states=load(OUT/'decoded-original-states.json')
manifest=json.loads((ROOT/'docs/coder/d1e3/manifest/branches.json').read_bytes())
events=[json.loads(b) for b in raw.splitlines()[1:] if b.startswith(b'{')]
events=[e for e in events if 'id' in e]
error={'P06-ZERO/d01':'INVALID_PROVIDER_RESULT','P07-EARLY/d01':'EARLY_EOF','P10-B/n08':'STALE_REVISION','P11-SEALED/n09':'SESSION_RELEASED','P12-OLDOPEN/n19':'SESSION_RELEASED','Q09-SECOND/n01':'CLAIM_CONFLICT','Q09-SECOND/n02':'CLAIM_CONFLICT','Q09-PLAN/n01':'INTENT_CONFLICT','Q09-SOURCE/n01':'INTENT_CONFLICT','Q09-PRESET/n01':'INTENT_CONFLICT','Q05-SPACEFAIL/d02':'OUTPUT_SPACE_INSUFFICIENT','Q07-TAKEFIRST/n13':'STALE_OWNER','Q03-RANDOM/n01':'RANDOM_REQUIRED','Q03-VERIFY/n01':'VALIDATION_REQUIRED','Q09-ALIAS/n01':'INPUT_ALIAS','P10-D/n11':'EXHAUSTED','P10-C/n02':'CLOSE_NOT_RETRYABLE','P10-C/n04':'CLOSE_NOT_RETRYABLE'}
waiting={'P08-LATEOPEN/n03':'CANCELLED','P09-CANCEL/d01':'CANCELLED','P09-TIMEOUT/d01':'SOURCE_TIMEOUT'}
data={'P02-ZERO':1,'Q01-SEQ':4,'Q04-DUP':1,'Q02-RANDOM':7,'Q08-VALIDATOR':1,'Q04-CLOSEACK':1,'Q05-SPACEFAIL':2,'Q07-TAKEFIRST':2}
specs={'PF':dict(nonquery=16,inputCalls=2)};specs.update({r['id']:r for r in manifest['branches']})
expected=set();race=[];completed=[]
for row in ['PF']+manifest['executionOrder']:
    spec=specs[row]
    for prefix,total,kind in [('n',spec['nonquery'],'N'),('d',data.get(row,spec['inputCalls']),'D')]:
        for i in range(1,total+1):
            op=f'{row}/{prefix}{i:02}';expected.add(op);entries=[e for e in events if e['id']==op]
            terminal='WAITING_COMPLETION' if op in waiting else 'DONE'
            assert [e['phase'] for e in entries]==([terminal] if op=='PF/n01' else ['ADMITTED',terminal]),op
            assert all(e['kind']==kind for e in entries)
            last=entries[-1];assert len(last['resultDigest'])==64
            if op in ('P10-A/n06','P10-A/n07'):
                assert last['error'] in ('','STALE_REVISION');race.append(last['error'])
            else:assert last['error']==error.get(op,''),(op,last['error'])
            if op in waiting:
                cells=[c for c in pre['cellHistory'] if c['operation']==op];assert len(cells)==1;c=cells[0]
                assert c['discarded'] and c['deliveries']==0 and c['error_message']==waiting[op] and c['error_type']=='Refused'
                assert all(c[k] for k in ('native_done','gated','released','notification_done','notifier_quiescent','archived'))
                assert c['callbacks_finished']==c['callbacks_registered'] and c['callback_errors']==[]
            completed.append(dict(operation=op,kind=kind,terminal=terminal,error=last['error']))
assert race.count('STALE_REVISION')==1 and race.count('')==1
assert {e['id'] for e in events if not e['id'].startswith('GC/')}==expected
for c in pre['cellHistory']:
    state=states[c['binding']['task']];op=state['ops'][c['operation']]
    assert op['done'] and op['nativeReturned']
order={name:i for i,name in enumerate(['PF']+manifest['executionOrder']+['GC'])}
observed=[order[e['id'].split('/')[0]] for e in events]
assert all(a<=b for a,b in zip(observed,observed[1:]))
out=dict(status='PASS',scope='Independent original event semantics, no candidate modules or media',operationChecks=completed,approvedExpectedErrors=error,threeWaitingAudits=waiting,all64SourceOpsReturned=True,exactOperationSet=True,approvedRowOrder=True,resultReadUsageIncludingEarlierReview=cost,newActualRuns=0,mediaStatCalls=0,mediaBytesRead=0)
(OUT/'control-and-waiting-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='PASS',operations=len(completed),expectedRefusedSlots=len(error),waitingSlots=len(waiting),readUsage=cost)))
