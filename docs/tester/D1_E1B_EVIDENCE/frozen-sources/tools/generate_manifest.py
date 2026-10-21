"""Update copied accepted allocations to the implemented E1B entry points."""
import argparse, hashlib, json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ENTRIES={'res':'res','g+':'guard','h+':'open_j','r+':'ref','seal':'seal','end':'end','cancel':'cancel_source','cancelO':'cancel_output','ch':'close_j','cr':'close_r','cg':'close_guard','retry':'close_j','gate':'gate','version':'version','grant':'grant','allocA':'alloc','dupB':'dup','sendB':'send','takeB':'take','claim':'claim','flushB':'flush','ca':'close_a','cb':'close_b','v+':'vopen','cv':'vclose','takeover':'takeover','ready':'ready','abort':'cancel_output'}
def generate():
    manifest=json.loads((BASE/'upstream-e1/branches.json').read_text(encoding='utf-8-sig'))
    manifest.update(schema=2,scope='E1B_IMPLEMENTATION_PENDING_INDEPENDENT_REVIEW',missingFullDriver=False,experimentEnabled=False)
    for row in manifest['branches']:
        row.update(entry='src/scenarios.py:Scenarios.run',implementation='CONCRETE_SYNTHETIC_DRIVER',executionStatus='REAL_MEDIA_NOT_RUN',blockers=['Independent review and separate media-experiment authorization required'])
        for op in row['operations']:
            name=next((x for x in sorted(ENTRIES,key=len,reverse=True) if op['token'].startswith(x)),None)
            op['entry']='src/gengine.py:Ops.'+ENTRIES[name] if name else 'src/gengine.py:Flow.n + src/scenarios.py:Scenarios.run'
            op['binding']='ADMISSION_JOURNAL_THEN_NATIVE_OR_AUTHORITY'
    manifest['executionOrder']=[r['id'] for r in manifest['branches'] if r['id'] not in ('P10-D','P10-C')]+['P10-D','P10-C']
    for phase,rows in manifest['phases'].items():
        for row in rows:row.update(implementation='src/phases.py:'+('preflight' if phase=='PF' else 'Cleanup.finish' if row['id']=='GC/n32' else 'Cleanup.run'))
    manifest['dataBinding']='src/scenarios.py -> Ops.read_j/read_r/write/seek_write -> Flow.data -> Engine.remote -> JavaHelper/RHost'
    manifest['recoveryBinding']='J independent bounded record read + Engine.recovery_callback; src/recovery.py whole-authority read-only reconstruction'
    manifest['profile']={'synthetic':{'L':131072,'C':4096,'Z':0,'boundary':65536},'realMedia':'DISABLED; no physical version/durability/media-boundary claim'}
    assert len(manifest['branches'])==61 and sum(r['nonquery'] for r in manifest['branches'])+48==351
    (BASE/'manifest/branches.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'branches':61,'controls':452,'mode':'IMPLEMENTATION_MAPPING_ONLY'}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--generate',action='store_true');args=parser.parse_args()
    if args.generate:generate()
    else:print('INSPECT_ONLY: explicit --generate required')
