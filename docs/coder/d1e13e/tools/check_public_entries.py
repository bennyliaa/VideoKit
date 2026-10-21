from pathlib import Path
import subprocess,json,uuid,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];J=Path('D:/Android/Android Studio/jbr/bin');E=B/'evidence/public-004';E.mkdir(exist_ok=False);W=B/'.checks/public-004';W.mkdir(parents=True,exist_ok=False);C=B/'.checks/host-003'
def sha(b):return hashlib.sha256(b).hexdigest()
def record(f):return (json.dumps({'e9':1,'fields':dict(sorted(f.items()))},separators=(',',':'))+'\n').encode()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
location=E/'E13GuardLocation.java';location.write_text('package com.videokit.spike.e4; import java.nio.file.*; final class E13GuardLocation { static final Path ROOT=Paths.get("'+(E/'shared-slot').resolve().as_posix()+'"); static final String DISPOSITION_SHA="ABSENT";}\n')
p=subprocess.run([str(J/'javac.exe'),'-cp',str(C),'-d',str(W),str(location)],capture_output=True);assert p.returncode==0,p.stderr
methods=['ordinarySenderCannotBindCodec','authorizedHostSourceReadAndClose','oldGenerationNeverOpensSource','twoConsumersHoldSourceUntilLastReturn','cancelLateOpenRetainsOriginalOwner','lateReadAndCloseFailureDoNotReleaseEarly']
def scope():
 f={'kind':'e13DispatchScope','batch':'D1-E13E-LIFECYCLE-20261018','scopeId':str(uuid.uuid4()),'sourceAcceptance':'9cdc913d8a6c98e1aad4c4acddb0ab3ed3adc66dd39c2ee5d053139b678ace74','sourceApp':'962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad','sourceTest':'83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13','app':'a'*64,'test':'b'*64,'fixture':'c'*64,'fixtureSigner':'45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9','sourceReview':'d'*64,'methods':','.join(sorted(methods)),'budget':'source4096/read65536/open8/close16/process51/text2097152/output0'}
 path=E/('local-fixture-'+f['scopeId']+'.json');path.write_bytes(record(f));return path,sha(path.read_bytes())
cp=str(W)+';'+str(C);commands=[];active=[]
for n in range(2):
 path,digest=scope();args=[str(J/'java.exe'),'-cp',cp,'com.videokit.spike.e4.E13HostCase',str(path),digest,methods[0]];so=(E/('case'+str(n)+'.stdout.txt')).open('xb');se=(E/('case'+str(n)+'.stderr.txt')).open('xb');p=subprocess.Popen(args,stdout=so,stderr=se);active.append((p,so,se,'case'+str(n),args))
for n,entry in enumerate(['com.videokit.spike.e4.E13HostActivationSession','com.videokit.spike.e4.E9HostActivationSession']):
 args=[str(J/'java.exe'),'-cp',cp,entry,'--approved-e13-deploy' if n==0 else '--approved-deploy','UNUSED_CONFIG','a'*64,'UNUSED_RELEASE','b'*64,'UNUSED_APP','UNUSED_TEST']+(['UNUSED_FIXTURE'] if n==0 else []);name='deploy'+str(n);so=(E/(name+'.stdout.txt')).open('xb');se=(E/(name+'.stderr.txt')).open('xb');p=subprocess.Popen(args,stdout=so,stderr=se);active.append((p,so,se,name,args))
for p,so,se,name,args in active:
 code=p.wait(timeout=15);so.close();se.close();raw=(E/(name+'.stdout.txt')).read_bytes()+(E/(name+'.stderr.txt')).read_bytes();assert code==1 and b'E13_ORIGINAL_E13C_PENDING_NO_CHILD' in raw and b'E9_PC_SUPERVISOR_READY' not in raw,(name,raw)
 commands.append(dict(name=name,argv=args,pid=p.pid,exitCode=code,naturalReturn=True,sdkChild=0,install=0))
write(E/'commands-and-results.json',{'status':'PASS_REAL_PUBLIC_ENTRIES_PENDING','commands':commands,'concurrentCaseScopes':2,'locationOnlyShadow':str(location),'actualGuardAndEntryProduction':True,'originalDeviceChecked':False,'deviceCalls':0})
# Execute the ACTUAL outer observer on the same blocked public entry; no SDK child can start.
path,digest=scope();capture=E/'observer-capture';capture.mkdir();request={'id':'local_guard_case','scope':digest,'evidenceRoot':str(capture.resolve()),'pins':[],'argv':['D:/Android/Android Studio/jbr/bin/java.exe','-cp',cp,'com.videokit.spike.e4.E13HostCase',str(path),digest,methods[0]],'maxTextBytes':81920}
req=E/'local-observer-request.json';write(req,request)
# Existing stdout file produces a known NO_OPEN recording failure, preserving its bytes; stderr still drains.
(capture/'local_guard_case-stdout.txt').write_bytes(b'EXISTING_LOCAL_RECORD_DO_NOT_REPLACE')
argv=['pwsh','-NoProfile','-File',str(B/'tools/observe_original.ps1'),'-RequestPath',str(req)]
with (E/'observer.stdout.txt').open('xb') as so,(E/'observer.stderr.txt').open('xb') as se:
 p=subprocess.Popen(argv,stdout=so,stderr=se);code=p.wait(timeout=20)
assert code==0,(E/'observer.stderr.txt').read_text();raw=(E/'observer.stdout.txt').read_text();assert 'allOriginalResourcesReturned' in raw and 'stdout_EXISTING_RECORD_NOT_REPLACED' in raw
assert (capture/'local_guard_case-stdout.txt').read_bytes()==b'EXISTING_LOCAL_RECORD_DO_NOT_REPLACE'
receipt=json.loads((capture/'local_guard_case-receipt.json').read_text());assert receipt['originalWaitReturned'] and receipt['originalProcessDisposed'] and receipt['readers'][0]['recordFailed'] and receipt['readers'][0]['eof'] and receipt['readers'][1]['eof']
write(E/'outer-observer-result.json',{'status':'PASS_ACTUAL_OUTER_OBSERVER_KNOWN_RECORDING_FAILURE','pid':p.pid,'exitCode':code,'argv':argv,'actualPublicGuardRefusalChild':True,'rawRecordFailureDoesNotDropProcessReadersPipes':True,'deviceCalls':0})
print('PASS four actual public entries including concurrent new scopes; actual outer observer recording failure/empty stdout/natural original return')
