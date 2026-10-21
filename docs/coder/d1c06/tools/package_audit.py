"""Read-only local audit of four completed C06 APK outputs; no devices."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile,os,re
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c06';out=base/'evidence';artifacts=base/'artifacts/D1-20261005-C06';artifacts.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sdk=Path('D:/Android/SDK/build-tools/36.0.0');env=dict(os.environ,JAVA_HOME='D:/Android/Android Studio/jbr')
sources={'app-debug.apk':root/'app/build/outputs/apk/debug/app-debug.apk','app-debug-androidTest.apk':root/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk','app-release-unsigned.apk':root/'app/build/outputs/apk/release/app-release-unsigned.apk','worker-debug.apk':base/'worker_app/build/outputs/apk/debug/d1worker-debug.apk'}
rows=[];media_names={p.name for p in (root/'test_media').rglob('*') if p.is_file()}
for name,source in sources.items():
 dest=artifacts/name;shutil.copy2(source,dest)
 with zipfile.ZipFile(dest) as z:
  names=z.namelist();dex=b''.join(z.read(n) for n in names if n.endswith('.dex'))
  row={'path':dest.relative_to(root).as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest),'sample_named_entries':[n for n in names if Path(n).name in media_names],'c06_dex':b'Lcom/videokit/spike/c06/' in dex,'native_libraries':[{'path':n,'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in names if n.endswith('.so')],'model_entries':[n for n in names if n.lower().endswith(('.onnx','.tflite','.pth'))]}
  assert not row['sample_named_entries'] and not row['model_entries']
  if name in ('app-debug.apk','worker-debug.apk'):
   row['output_validator_in_dex']=all(('Lcom/videokit/spike/c06/'+c+';').encode() in dex for c in ['AndroidOutputValidator','OutputValidationRules'])
   assert row['output_validator_in_dex']
  if name=='app-debug.apk':
   assert b'D1_INJECTED_OUTPUT_WRITE' in dex and b'D1_INJECTED_OUTPUT_FLUSH' in dex
   row['c06_diagnostic_classes']=all(('Lcom/videokit/spike/c06/'+c+';').encode() in dex for c in ['NativeFault','ExitEvidence','TombstoneWitness','CodecProbeState','VideoFrameSink','VideoCaptureOutputValidator','FrameCaptureRules','CaptureInputKind'])
   assert row['c06_diagnostic_classes']
  if name=='app-debug-androidTest.apk':
   assert b'correct injected error chain' in dex and b'outputValidationCounterexamples' in dex
   assert all(x.encode() in dex for x in ['isolatedBrokerHangIndependently','isolatedBrokerSigsegvIndependently','ordinaryIsolatedCodecOutcomeDoesNotReady','frameViaCapturePipeline','transformer_cancel_returned=','videoFrameCaptureMp4Control','VIDEO_CAPTURE_ONLY'])
  if name=='app-release-unsigned.apk':assert not row['c06_dex']
  if name=='worker-debug.apk':
   assert b'Landroidx/media3/transformer/Transformer;' in dex
   row['host_classes_absent']=all(('Lcom/videokit/spike/c06/'+c+';').encode() not in dex for c in ['HostFixtures','TaskInputBroker','RecoveryHostService','C06ProbeActivity','AuthorizedSink','VideoFrameSink','VideoCaptureOutputValidator']);assert row['host_classes_absent']
 badging=subprocess.check_output([str(sdk/'aapt.exe'),'dump','badging',str(dest)]).decode(errors='replace');manifest=subprocess.check_output([str(sdk/'aapt.exe'),'dump','xmltree',str(dest),'AndroidManifest.xml']).decode(errors='replace')
 (out/(name+'.badging.txt')).write_text(badging,encoding='utf-8');(out/(name+'.manifest.txt')).write_text(manifest,encoding='utf-8')
 row['internet_permission']='android.permission.INTERNET' in badging;assert not row['internet_permission']
 if name=='worker-debug.apk':assert 'com.videokit.worker.spike.BIND_MEDIA_WORKER' in manifest and 'android:isolatedProcess' not in manifest
 if name=='app-debug.apk':assert 'android:isolatedProcess' in manifest
 if 'unsigned' not in name:
  cert=subprocess.check_output([str(sdk/'apksigner.bat'),'verify','--verbose','--print-certs',str(dest)],env=env).decode(errors='replace');(out/(name+'.signing.txt')).write_text(cert,encoding='utf-8');row['certificate_sha256']=re.search(r'Signer #1 certificate SHA-256 digest: (\S+)',cert)[1]
 rows.append(row)
assert len({r['certificate_sha256'] for r in rows if 'certificate_sha256' in r})==1
(out/'apk-audit.json').write_text(json.dumps({'scope':'static package/manifest/signatures only; no Android execution','apks':rows},indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))

