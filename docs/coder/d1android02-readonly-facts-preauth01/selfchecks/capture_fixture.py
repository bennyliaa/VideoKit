"""Exact bounded local producer only. No SDK/network/product/media calls."""
from pathlib import Path
import hashlib,json,sys,time
mode=sys.argv[1];gate=Path(sys.argv[2]);assert len(sys.argv)==3
if mode=='identity':
 print('ANDROID02_ID_BEGIN\nTB138FC\n31\nSYNTHETIC_FIXTURE_FIRMWARE_API31\n0\narm64-v8a\nANDROID02_ID_COMPLETE')
elif mode in ['global_idle','global_busy','global_unknown']:
 if mode=='global_unknown':print('UNPROVEN_GLOBAL_FORMAT')
 else:
  print('ANDROID02_GLOBAL_BEGIN\nACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)')
  if mode=='global_busy':print('  *APP* UID 10223 ProcessRecord{abcdef 123:com.example.otherproject/u0a223}\n    curProcState=4 cached=false\n    mInstr=ActiveInstrumentation{abc {com.example.otherproject.test/Runner} 1 procs}')
  else:print('  *APP* UID 10012 ProcessRecord{abcdef 124:com.zui.launcher/u0a12}\n    user #0 uid=10012\n    packageList={com.zui.launcher}\n    curProcState=2 cached=false\n    mInstr=null')
  print('ANDROID02_GLOBAL_ACTIVITIES\nACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)\nDisplay #0 (activities from top to bottom):\n  mResumedActivity: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n  mFocusedApp=ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n      * Hist #0: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n          packageName=com.zui.launcher processName=com.zui.launcher\n          app=ProcessRecord{abcdef 124:com.zui.launcher/u0a12}\n          mActivityComponent=com.zui.launcher/.Launcher\n          state=RESUMED stopped=false delayedResume=false finishing=false\n          mVisibleRequested=true mVisible=true\nANDROID02_GLOBAL_COMPLETE')
elif mode in ['app_absence','test_absence','app_present']:
 kind='TEST' if mode=='test_absence' else 'APP';print('ANDROID02_'+kind+'_BEGIN')
 if mode=='app_present':print('package:com.videokit.d1media3.android02')
 print('ANDROID02_'+kind+'_COMPLETE')
elif mode in ['payload_app','payload_test']:
 expected=4096 if mode=='payload_app' else 2048;data=sys.stdin.buffer.read(65537);assert len(data)==expected
 print('LOCAL_PAYLOAD '+json.dumps({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'fixtureOnly':True},separators=(',',':')))
elif mode=='instrument':
 receipt={'firstFailure':None,'fixtureOnly':True,'scopeEntry':'scopeAll','candidate':'D1-MEDIA3-ANDROID02-FIX02','status':'OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY','completedCaseCount':10,'expectedCaseCount':10,'originalResourcesReturned':True,'workerActuallyJoined':True,'timelyOriginalBody':True,'lastControlledReturnSignalBeforeMarker':True,'sourceKeepers':0,'outputKeepers':0,'runnerFinalizerOwnerAtReceipt':1,'runnerFinishReturn':'EXTERNAL_ORIGINAL_CAPTURE_REQUIRED'}
 print('INSTRUMENTATION_STATUS: receipt='+json.dumps({'fixtureOnly':True,'status':'LOCAL_PARTIAL_HISTORY','caseReceipts':[{'case':'preopenAdmission'}]},separators=(',',':')))
 print('INSTRUMENTATION_RESULT: receipt='+json.dumps(receipt,separators=(',',':'))+'\nINSTRUMENTATION_CODE: -1')
elif mode=='late':
 end=time.monotonic()+3
 while not gate.exists() and time.monotonic()<end:time.sleep(.01)
 print('ORIGINAL_LOCAL_LATE_RETURN')
elif mode=='overrun':
 for value in [b'A'*64,b'B'*64,b'C'*64]:sys.stdout.buffer.write(value);sys.stdout.buffer.flush();time.sleep(.01)
elif mode=='stderr':print('LOCAL_CAPTURE_OUTPUT');print('LOCAL_CONTROLLED_DIAGNOSTIC',file=sys.stderr)
elif mode=='invalid_utf8':sys.stdout.buffer.write(b'\xff\xfe')
elif mode=='nonzero':print('LOCAL_CONTROLLED_FAILURE',file=sys.stderr);raise SystemExit(7)
else:raise ValueError('EXACT_LOCAL_MODE_ONLY')
