"""Read only existing E3 results, independently hash/decode/archive; never reads media."""
from pathlib import Path
import hashlib,json,struct,zlib,stat
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e3'
RUN='e3-11a896d3c2c34483ba2dff60fa63f5c8';PREFIX='runs/'+RUN+'/'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Prior reads in this review: original driver10917B and readonly verify143 files719649B.
usage={'bytes':730566,'files':144,'byteCap':6291456,'fileCap':512};cache={}
def read_result(path):
    rel=path.relative_to(BASE).as_posix()
    assert rel.startswith('execution/') or rel.startswith(PREFIX)
    assert not path.is_symlink() and not path.is_junction() and stat.S_ISREG(path.stat().st_mode)
    size=path.stat().st_size;assert usage['bytes']+size<=usage['byteCap'] and usage['files']<usage['fileCap']
    usage['files']+=1;parts=[];count=0
    with path.open('rb',buffering=0) as stream:
        while count<size:
            b=stream.read(min(65536,size-count));assert b
            usage['bytes']+=len(b);count+=len(b);parts.append(b)
    cache[rel]=b''.join(parts);return cache[rel]
files=sorted(p for folder in (BASE/'execution',BASE/'runs'/RUN) for p in folder.rglob('*') if p.is_file())
assert len(files)==143
for p in files:read_result(p)
def get(rel):return json.loads(cache[rel])
manifest=get('execution/result-manifest.json');driver=get('execution/driver-result.json');launcher=get('execution/launcher-result.json')
pre=get(PREFIX+'result-before-close.json')
assert {r['path'] for r in manifest['files']}==set(cache)-{'execution/result-manifest.json'} and len(manifest['files'])==142
for r in manifest['files']:
    b=cache[r['path']];assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
assert manifest['batchPassProven'] and manifest['complete'] and manifest['resultHashComplete']
assert manifest['status']==driver['status']==launcher['status']==pre['status']=='PASS'
assert sha(cache[PREFIX+'result-before-close.json'])==driver['driverWitness']['precloseSummarySha']
states={};slots=[]
for rel,b in cache.items():
    if not rel.endswith(('/state0.slot','/state1.slot')):continue
    assert len(b)==8192
    seq,n,reserved=struct.unpack('<qiI',b[:16]);assert seq>0 and reserved==0 and 0<=n<=8144
    assert seq%2==int(rel[-6])
    payload=b[48:48+n];assert sha(b[:16]+payload)==b[16:48].hex()
    d=zlib.decompressobj();raw=d.decompress(payload,65537);assert len(raw)<=65536 and d.eof and not d.unused_data
    obj=json.loads(raw);task=rel.split('/')[-2];assert obj['task']==task and obj['batch']==RUN and obj['schema']==3
    slots.append(dict(path=rel,seq=seq,sha256=sha(b)))
    if task not in states or seq>states[task][0]:states[task]=(seq,obj)
states={k:v[1] for k,v in states.items()};assert len(states)==32
commands={key:dict(value,task=task) for task,state in states.items() for key,value in state['commands'].items()}
for rel,b in cache.items():
    dest=OUT/'original-output-archive'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
window_commands={key:value for key,value in commands.items() if key.startswith(('P01-','Q01-SEQ')) and value['label'] in ('readJ','readRef','readV')}
save('decoded-original-states.json',states)
save('decoded-window-commands.json',window_commands)
save('collection-integrity.json',dict(at=datetime.now().astimezone().isoformat(),scope='Original E3 output only, no media stat/read/hash; no candidate imports',resultManifestSha256=sha(cache['execution/result-manifest.json']),precloseSha256=sha(cache[PREFIX+'result-before-close.json']),originalOutputFiles=143,decodedTasks=len(states),decodedSlots=slots,resultReadUsageIncludingPriorDriverAndVerify=usage,outputHashes=[dict(path=k,bytes=len(v),sha256=sha(v)) for k,v in cache.items()],originalG=launcher['originalChild'],originalGExitCode=launcher['originalChildExitCode'],originalLauncher=driver['claim']['launcher'],noInFlight=manifest['noInFlight']))
print(json.dumps(dict(resultManifestSha256=sha(cache['execution/result-manifest.json']),precloseSha256=sha(cache[PREFIX+'result-before-close.json']),resultReadUsage=usage,slotCount=len(slots),sampleWindowCommand=list(window_commands.items())[:3],Q01ReadCommands={k:v for k,v in window_commands.items() if k.startswith('Q01-SEQ')}),ensure_ascii=False))
