"""Frozen C06 tablet methods, bounded execution and explicit dependencies."""
import datetime, json, pathlib, subprocess, re
BASE = pathlib.Path(__file__).resolve().parent
ADB = r'D:\Android\SDK\platform-tools\adb.exe'
SERIAL = 'HA1Q6WXR'
def adb(args, timeout=30):
    return subprocess.run([ADB,'-s',SERIAL]+args,capture_output=True,timeout=timeout)
def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
results=[]
normal='realEncoderOutput'
companion='isolatedActualEncodeAndReadyRecovery'
plan=[('C06DeviceTests',normal,180,None),('C06DeviceTests','videoFrameCaptureMp4Control',180,None),('C06IsolatedDeviceTests',companion,240,None),
 ('C06DeviceTests','outputValidationCounterexamples',180,None)]
plan += [('C06DeviceTests',m,180,normal) for m in ['exportReadyResponseLoss','exportWriteFault','exportFlushFault','exportValidationFault']]
plan += [('C06DeviceTests',m,180,None) for m in ['realPipelineImmediateCancel','writingJournalRecovery','isolatedWorkerDeathAndTimeout','isolatedBrokerSigsegvIndependently','isolatedBrokerHangIndependently']]
plan += [('C06IsolatedDeviceTests',m,240,None) for m in ['ordinaryIsolatedCodecOutcomeDoesNotReady','nativeLeaseSurvivesDuplicateDescriptorClose']]
plan += [('C06IsolatedDeviceTests',m,360 if m=='secondCodecTaskSurvivesFirstNativeCrash' else 240,companion) for m in ['cancelAfterActualVideoSample','workerExitDuringActualEncoding','workerSigsegvDuringActualEncoding','secondCodecTaskSurvivesFirstNativeCrash','actualHostDeathDuringEncodingAndCrossOwnerAbort','actualHostDeathAfterReadyAndSameTaskQuery']]
plan += [('C06DeviceTests',m,180,None) for m in ['playbackMp4','playbackAviWithoutSrt','playbackAviSrt','playbackMkvAss']]
plan += [('C06DeviceTests','offlinePlatformFaceFeasibility',180,'videoFrameCaptureMp4Control')]
assert len(plan)==26
for cls,method,limit,dependency in plan:
    start=now()
    device_start=adb(['shell','date '+chr(34)+'+%m-%d %H:%M:%S.000'+chr(34)]).stdout.decode().strip()
    print('START '+method+' '+start,flush=True)
    command=['shell','am','instrument','-w','-e','class','com.videokit.spike.c06.'+cls+'#'+method,'com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner']
    reason=None
    if dependency and not any(r['method']==dependency and r['result']=='PASS' for r in results):
        status,code,output='BLOCKED',None,'Precondition did not pass: '+dependency
        reason=output
    else:
        try:
            p=adb(command,limit)
            output=(p.stdout+p.stderr).decode('utf-8',errors='replace')
            code=p.returncode
            status='PASS' if code==0 and 'OK (1 test)' in output and 'FAILURES!!!' not in output else 'FAIL'
        except subprocess.TimeoutExpired as e:
            output=((e.stdout or b'')+(e.stderr or b'')).decode('utf-8',errors='replace')
            output+='\nTESTER_TIMEOUT_'+str(limit)+'_SECONDS\n'
            status,code='BLOCKED',None
            reason='External bounded timeout; release not proven'
            for uid in ['10221','10220']:
                p=adb(['logcat','-d','--uid='+uid,'-v','threadtime','-T',device_start])
                (BASE/(method+'-timeout-uid'+uid+'.log')).write_bytes(p.stdout+p.stderr)
            for package in ['com.videokit.app','com.videokit.worker.spike']:
                p=adb(['shell','am','force-stop',package])
                output+='\nTARGETED_STOP '+package+' '+(p.stdout+p.stderr).decode(errors='replace')
    (BASE/(method+'.log')).write_text(output,encoding='utf-8')
    for uid in ['10221','10220']:
        p=adb(['logcat','-d','--uid='+uid,'-v','threadtime','-T',device_start])
        (BASE/(method+'-uid'+uid+'.log')).write_bytes(p.stdout+p.stderr)
        if uid=='10221':
            for isolated_pid in sorted(set(re.findall(r'pid=(\d+)',p.stdout.decode(errors='replace')))):
                if int(isolated_pid)>0:
                    cp=adb(['logcat','-b','crash','-d','--pid='+isolated_pid,'-v','threadtime','-T',device_start])
                    (BASE/(method+'-crash-pid'+isolated_pid+'.log')).write_bytes(cp.stdout+cp.stderr)
                    crash=adb(['logcat','-b','crash','-d','-v','threadtime','-T',device_start]).stdout.decode(errors='replace')
                    blocks=re.split(r'(?=^.*\*\*\* \*\*\* \*\*\*)',crash,flags=re.MULTILINE)
                    own=[block for block in blocks if re.search(r'pid:\s*'+isolated_pid+r'\s*,',block) and 'com.videokit.' in block]
                    (BASE/(method+'-tombstone-pid'+isolated_pid+'.log')).write_text('\n'.join(own),encoding='utf-8')
    results.append(dict(candidateId='D1-20261005-C06',serial=SERIAL,method=method,className=cls,start=start,end=now(),result=status,processExitCode=code,timeoutSeconds=limit,dependency=dependency,reason=reason,log=method+'.log',command=[ADB,'-s',SERIAL]+command))
    (BASE/'tablet-batch-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('END '+method+' '+status+' '+now(),flush=True)
for uid in ['10221','10220']:
    p=adb(['logcat','-d','--uid='+uid,'-v','threadtime','-T',device_start])
    (BASE/('tablet-uid'+uid+'-logcat.txt')).write_bytes(p.stdout+p.stderr)
print('BATCH_FINISHED '+now(),flush=True)




