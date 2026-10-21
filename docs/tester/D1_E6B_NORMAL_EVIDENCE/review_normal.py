"""Independent review of saved raw evidence only; never calls ADB or reads media."""
from pathlib import Path
import json,hashlib,re,sys,struct
E=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def load(n):return json.loads((E/n).read_bytes())
def text(n):return (E/n).read_text(encoding='utf-8').replace('\r\n','\n')
def save(n,x):
    with (E/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def fields(s):return dict(re.findall(r'([a-zA-Z_]+)=([^\s]+)',s))
def blocks(s):return {p:bytes.fromhex(h) for p,h in re.findall(r'HEX_BEGIN\|([^\n]+)\n(.*?)HEX_END',s,re.S)}
method=sys.argv[1];assert method in ['normalMp4SixRealFrames','normalAviSixRealFrames']
s=text(method+'-instrumentation-stdout.txt');logs=text(method+'-logcat-stdout.txt');post=text(method+'-post-state-stdout.txt')
assert 'OK (1 test)' in s and 'FAILURES!!!' not in s and 'INSTRUMENTATION_CODE: -1' in s
assert 'test='+method in s and 'E4 FINAL_OBSERVATION FRESH_OBSERVATION_ADMITTED' in s
assert 'oldCloseACK=false' in s and 'absent=true;' in s
report_lines=re.findall(r'E4 REPORT ([^\n]+)',s);assert len(report_lines)==2 and report_lines[0]==report_lines[1];r=fields(report_lines[0])
assert all(r[k]==v for k,v in dict(status='READY',error='null',received='6',inputs='6',outputs='6',controlInFlight='0',released='true',workerDied='false').items())
assert r['task']==r['outputTask'].replace('-','') and 0<int(r['outputBytes'])<=2097152
host_lines=re.findall(r'E4 HOST_DIAGNOSTICS ([^\n]+)',s);assert len(host_lines)==2 and host_lines[0]==host_lines[1];host=host_lines[0]
for part in ['terminalReason=ACTUAL_OWNERS_RETURNED','originalOwnerReturned=true','ownerFinishEntries=1','cleanupContinuations=0','callbackFlags=18','startedSignal=true startProven=true','cleanupError= hostStage=FINAL_ORIGINAL_OWNER_RETURN']:
    assert part in host,part
hd=fields(host.split(' validatorNativeDiagnostic=')[0])
vtext=host.split('validatorNativeDiagnostic=')[1].split(' sourceNativeDiagnostic=')[0];v=fields(vtext)
srcdiag=fields(host.split('sourceNativeDiagnostic=')[1])
assert all(v[k]==val for k,val in dict(scope='VALIDATOR',mode='11',phase='VERIFIED',code='E6_NATIVE_OK',site='0',stage='5',av_error='0',packets='6',decoded='6',accepted='6',demux_eof='1',decoder_eof='1',drain='1').items())
assert srcdiag['scope']=='SOURCE' and srcdiag['mode']=='10' and srcdiag['phase']=='FRAME_ACCEPTED' and v['task']!=srcdiag['task']
for part in ['callbackInFlight=0 callbackEntered=8 callbackReturned=8 callbackAckFailed=false callbackUnknown=false','nativeCalls=0 liveResources=0 unknownResources=0 creating=false imageHeld=false encoderReleased=true sinkReleased=true leaseReleased=true framesReleased=true']:
    assert part in s
events={}
for line in logs.splitlines():
    m=re.search(r'\bstage=([A-Z0-9_]+) thread=\d+ (.*)',line)
    if m:events.setdefault(m[1],[]).append(fields(m[2]))
sources=events['E4_SOURCE_FRAME'];starts=events['CPU_TASK_STARTED'];verified=events['CPU_OUTPUT_FRAME_VERIFIED'];diags=events['E6_NATIVE_DIAGNOSTIC']
assert len(sources)==len(verified)==6 and [int(x['sequence']) for x in sources]==list(range(1,7)) and [int(x['sequence']) for x in verified]==list(range(1,7))
assert len(starts)==len(diags)==7 and sum(x['mode']=='10' for x in starts)==6 and sum(x['mode']=='11' for x in starts)==1
assert len({x['task'] for x in starts})==7 and all(int(x['uid'])%100000>=90000 and x['uid']!='10221' and x['pid'] not in [hd['hostPid'],hd['codecPid']] for x in starts)
assert hd['hostPid']!=hd['codecPid']
bytask={x['task']:x for x in starts};assert bytask[v['task']]['mode']=='11' and srcdiag['task']==sources[-1]['task']
for x in sources:
    assert bytask[x['task']]['mode']=='10' and x['pid']==bytask[x['task']]['pid'] and x['uid']==bytask[x['task']]['uid']
    assert abs(int(x['pts_us'])-round(int(x['raw'])*int(x['num'])/int(x['den'])*1000000))<=1
timeline=[int(x['pts_us'])-int(sources[0]['pts_us']) for x in sources];outpts=[int(x['pts_us']) for x in verified]
assert all(0<=x<=2000000 for x in timeline) and all(timeline[i]>timeline[i-1] for i in range(1,6))
deviation=max(abs(a-b) for a,b in zip(timeline,outpts));assert deviation<=1000
assert all(x['task']==v['task'] and x['pid']==bytask[v['task']]['pid'] and x['uid']==bytask[v['task']]['uid'] for x in verified)
assert int(v['last_pts_us'])==outpts[-1]
assert len(events['CPU_OUTPUT_FULL_EOF_VERIFIED'])==1 and events['CPU_OUTPUT_FULL_EOF_VERIFIED'][0]['task']==v['task'] and events['CPU_OUTPUT_FULL_EOF_VERIFIED'][0]['frames']=='6'
content=events['PIPE_CONTENT_FRAME'];visual=events['PIPE_VISUAL_CHECK'];assert len(content)==6 and len(visual)==1
assert [int(x['sequence']) for x in content]==list(range(1,7)) and all(x['verifier_task']==v['task'] and float(x['luma_mae'])<=24 for x in content)
assert visual[0]['frames']=='6' and visual[0]['full_eof']=='true' and float(visual[0]['max_luma_mae'])<=24 and float(visual[0]['source_distinction'])>=4 and float(visual[0]['output_distinction'])>=2
ledgers={x['task']:x for x in events['CPU_LEDGER']};assert set(ledgers)==set(bytask)
for x in ledgers.values():
    for k,val in dict(stop_pending='false',pending_calls='0',actual_death='true',source_released='true',slot_released='true',operations='0',consumers='0',failed_closes='0',source_close='CLOSED',first_code='NONE').items():assert x[k]==val,(k,x)
for x in diags:
    assert x['code']=='E6_NATIVE_OK' and x['site']=='0' and int(x['read_at_calls'])<=8192 and int(x['compressed_bytes'])<=67108864
    assert x['read_at_calls']==x['broker_read_at_requests'] and x['compressed_bytes']==x['broker_compressed_bytes']
    assert x['task'] in bytask
assert next(x for x in diags if x['task']==v['task'])['compressed_bytes']==v['compressed_bytes']==r['outputBytes']
data=blocks(post);pre=blocks(text('05-after-install-stdout.txt'))
for path,b in pre.items():
    if path!='files/e4a_output_budget/ledger.bin':assert data[path]==b,path
ledger_bytes=data['files/e4a_output_budget/ledger.bin'];assert ledger_bytes.startswith(pre['files/e4a_output_budget/ledger.bin'])
lines=ledger_bytes.decode().splitlines();h=sha((lines[0]+'\n').encode());records={}
for line in lines[1:]:
    p,want=line.rsplit(' ',1);assert sha((h+' '+p).encode())==want;h=want;tokens=p.split()
    if tokens[0]=='R':assert tokens[1] not in records;records[tokens[1]]=dict(batch=tokens[2],state=None,bytes=None)
    else:
        assert tokens[0]=='S' and tokens[1] in records and records[tokens[1]]['bytes'] is None
        records[tokens[1]].update(state=tokens[2],bytes=int(tokens[3]),sha256=tokens[4])
assert all(x['bytes'] is not None for x in records.values()) and 'ABSENT|files/e4a_output_budget/operation.pending\n' in post
current=records[r['outputTask']];assert current==dict(batch='D1-E4A-E6B-NORMAL-TABLET-20261017',state='READY',bytes=int(r['outputBytes']),sha256=r['outputSha'])
budget=dict(records=records,consumed=sum(x['bytes'] for x in records.values()),reserved=0,pending=False,sha256=sha(ledger_bytes))
assert budget['consumed']<=4194304
prefix='files/e4a_outputs/'+r['outputTask'];journal=data[prefix+'.journal'];assert struct.unpack_from('>i',journal,42)[0]==3
stat=re.search(r'OUTPUT_STAT\|'+re.escape(prefix)+r'\.mp4\|(\d+),(\d+),(\d+),10221,8180,(\d+)',post);assert stat and int(stat[3])==int(r['outputBytes'])
assert all(load(method+'-'+n+'-receipt.json')['exitCode']==0 and not load(method+'-'+n+'-receipt.json')['overflow'] for n in ['clock','instrumentation','logcat','post-state'])
seconds=float(re.search(r'\nTime: ([0-9.]+)',s)[1]);assert seconds<60
result=dict(method=method,result='PASS',dependentMethodsAdmitted=True,report=r,host=hd,validator=v,sourceDiagnostic=srcdiag,sourceFrames=sources,sourceRelativePtsUs=timeline,outputPtsUs=outpts,maxPtsDeviationUs=deviation,content=content,visual=visual[0],cpuJobs=starts,cpuLedgers=list(ledgers.values()),nativeCounters=diags,cpuReadCalls=sum(int(x['read_at_calls']) for x in diags),cpuCompressedBytes=sum(int(x['compressed_bytes']) for x in diags),allSevenCpuOwnersReturned=True,globalOwnerReturned=True,controlInFlight=0,ledger=budget,outputInode=int(stat[2]),junitSeconds=seconds,rawSha256=sha((E/(method+'-instrumentation-stdout.txt')).read_bytes()),logcatSha256=sha((E/(method+'-logcat-stdout.txt')).read_bytes()),postStateSha256=sha((E/(method+'-post-state-stdout.txt')).read_bytes()),extraMediaReads=0)
save(method+'-independent-review.json',result)
print(json.dumps({k:result[k] for k in ['method','result','maxPtsDeviationUs','cpuReadCalls','cpuCompressedBytes','junitSeconds','ledger']}))
