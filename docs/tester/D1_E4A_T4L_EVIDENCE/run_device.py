from pathlib import Path
import sys,json,hashlib,os,time,shlex,datetime
E=Path(__file__).resolve().parent;B=E.parents[2]/'docs/coder/d1e4at4/tools'
review=json.loads((E/'local-review.json').read_text());assert review['status']=='PASS'
for row in review['scripts']:assert hashlib.sha256((E/row['file']).read_bytes()).hexdigest()==row['sha256']
sys.path.insert(0,str(B));import exact_process as ep
assert hashlib.sha256((B/'exact_process.py').read_bytes()).hexdigest()=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'
def new(name,obj):
    assert sum(p.stat().st_size for p in E.iterdir() if p.is_file())+131072<1048576
    raw=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode();assert len(raw)<65536
    with (E/name).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
new('attempt.json',dict(batch='D1-E4A-T4L-TABLET-20261017',at=datetime.datetime.now().astimezone().isoformat(),metadataCap=6,planned=2,deviceWrites=0,contentReads=0))
result=dict(status='NOT_COMPLETED',records=[],priorRemoteOwnership='UNKNOWN_NOT_CLEARED',nextBatchAuthorized=False)
try:
    for app in (False,True):
        name='app' if app else 'shell';script=(E/(name+'-checklist.sh')).read_text()
        argv=['D:/Android/SDK/platform-tools/adb.exe','-s','HA1Q6WXR','shell','-n','-T','-e','none']+(['run-as','com.videokit.app'] if app else [])+['sh','-c',shlex.quote(script)]
        r=ep.collect(argv,ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=16384));new(name+'-original.json',r);result['records'].append(name+'-original.json')
        assert r['ownership']=='RETURNED' and r['originalExitObserved'] and r['originalExitCode']==0 and not r['creationUnknown'] and not r['errors']
        assert all(r[k] for k in ('stdinCloseReturned','sourceCloseReturned','writerReturned','flushReturned')) and r['stdinCloseError'] is None and r['submittedBytes']==0
        for stream in ('stdout','stderr'):
            s=r[stream];raw=bytes.fromhex(s['prefixHex'])
            assert s['closeReturned'] and s['error'] is None and not s['prefixTruncated'] and len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256']
            result[name+'_'+stream]=raw.decode('utf-8','strict')
        assert result[name+'_stdout'].endswith('CHECKLIST_END\n') and 'CONTEXT_REJECT' not in result[name+'_stdout']
    result['status']='READONLY_CHECKLIST_RECORDED'
except Exception as ex:result['failure']=str(ex)
result.update(metadataCommands=len(result['records']),retainedLocalOwners=ep.retained_owners())
new('result.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if ep.retained_owners():
    print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED',flush=True)
    while ep.retained_owners():time.sleep(1)
