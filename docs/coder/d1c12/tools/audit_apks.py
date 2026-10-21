from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,zipfile,struct
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c12';e=base/'evidence';art=base/'artifacts/D1-20261016-C12';sdk=Path('D:/Android/SDK/build-tools/36.0.0');ndk=Path('D:/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin');environment=dict(os.environ,JAVA_HOME='D:/Android/Android Studio/jbr')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources={'app-debug.apk':root/'app/build/outputs/apk/debug/app-debug.apk','app-debug-androidTest.apk':root/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk','app-release-unsigned.apk':root/'app/build/outputs/apk/release/app-release-unsigned.apk','worker-debug.apk':base/'worker_app/build/outputs/apk/debug/d1worker-debug.apk'}
expected={p.name:sha(p) for p in (base/'native-libs/arm64-v8a').glob('*.so')};rows=[];temp=base/'outputs/apk-native';temp.mkdir(exist_ok=True)
for name,source in sources.items():
 baseline_apk=root/'docs/coder/d1c07/artifacts/D1-20261005-C07'/name
 with zipfile.ZipFile(baseline_apk) as prior:
  inherited={n:hashlib.sha256(prior.read(n)).hexdigest() for n in prior.namelist() if n.endswith('.so') and Path(n).name!='libvideokit_d1_lease.so'}
 dest=art/name;shutil.copy2(source,dest);row={'file':name,'path':dest.relative_to(root).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size,'scope':'static packaging only; Android/device NOT_RUN'}
 with zipfile.ZipFile(dest) as z:
  names=z.namelist();dex=b''.join(z.read(n) for n in names if n.endswith('.dex'));libs=[]
  for entry in names:
   if not entry.endswith('.so'):continue
   info=z.getinfo(entry);data=z.read(entry);p=temp/(name+'-'+Path(entry).name);p.write_bytes(data)
   dump=subprocess.check_output([str(ndk/'llvm-readelf.exe'),'-h','-lW','-d',str(p)]).decode('utf-8');(e/(name+'-'+Path(entry).name+'.elf.txt')).write_text(dump,encoding='utf-8')
   loads=[line for line in dump.splitlines() if re.match(r'\s*LOAD\s',line)];assert loads;alignment=min(int(line.split()[-1],16) for line in loads)
   with dest.open('rb') as f:f.seek(info.header_offset);header=f.read(30);name_len,extra_len=struct.unpack_from('<HH',header,26);offset=info.header_offset+30+name_len+extra_len
   digest=hashlib.sha256(data).hexdigest();owned=Path(entry).name in expected
   if owned:assert digest==expected[Path(entry).name] and alignment>=16384
   else:assert digest==inherited[entry],entry
   assert info.compress_type==zipfile.ZIP_STORED and offset%16384==0
   libs.append({'path':entry,'sha256':digest,'bytes':len(data),'zip_offset':offset,'uncompressed':True,'zip_alignment':16384,'elf_load_alignment_min':alignment,'provenance':'C12 audited native' if owned else 'byte-identical inherited C07 AndroidX native library','needed':re.findall(r'\(NEEDED\).*?\[(.*?)\]',dump),'soname':re.findall(r'\(SONAME\).*?\[(.*?)\]',dump)})
  row['native_libraries']=libs;row['c12_classes']=b'Lcom/videokit/spike/c12/' in dex
  assert not any(n.lower().endswith(('.mp4','.avi','.mkv','.srt','.onnx','.tflite','.pth')) for n in names)
  if name=='app-debug.apk':
   assert {Path(n['path']).name for n in libs if n['provenance']=='C12 audited native'}==set(expected)
   for cls in ['CpuIsolatedService','CpuTaskClient','CpuProtocol','NativeCpu','RegistrationProtocol','BindingRevocation','ExitRecordRules','AndroidOutputValidator','OutputValidationRules']:assert ('Lcom/videokit/spike/c12/'+cls+';').encode() in dex,cls
   assert 'assets/licenses/NOTICE-C12.txt' in names
   for entry in names:
    if entry.startswith('assets/licenses/'):assert z.read(entry)==(base/'notice-assets'/entry.removeprefix('assets/')).read_bytes()
  elif name=='worker-debug.apk':
   assert {Path(n['path']).name for n in libs if n['provenance']=='C12 audited native'}=={'libvideokit_d1_lease.so'}
   assert b'Lcom/videokit/spike/c12/CpuIsolatedService;' not in dex
  elif name=='app-release-unsigned.apk':
   assert not row['c12_classes'] and not any(n['provenance']=='C12 audited native' for n in libs) and not any('NOTICE-C12' in n for n in names)
   row['unchanged_release_vs_C07']=row['sha256']=='71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e'
   assert row['unchanged_release_vs_C07']
  elif name=='app-debug-androidTest.apk':
   methods=re.findall(r'@Test public void (\w+)\(', (base/'device/com/videokit/spike/c12/C12CpuDeviceTests.java').read_text(encoding='utf-8'))
   assert all(method.encode() in dex for method in methods);row['cpu_test_methods']=methods
 manifest=subprocess.check_output([str(sdk/'aapt.exe'),'dump','xmltree',str(dest),'AndroidManifest.xml']).decode('utf-8',errors='replace');(e/(name+'.manifest.txt')).write_text(manifest,encoding='utf-8')
 badging=subprocess.check_output([str(sdk/'aapt.exe'),'dump','badging',str(dest)]).decode('utf-8',errors='replace');(e/(name+'.badging.txt')).write_text(badging,encoding='utf-8');assert 'android.permission.INTERNET' not in badging
 if name=='app-debug.apk':
  block=next(b for b in re.split(r'E: (?:service|activity|receiver|provider)',manifest) if 'com.videokit.spike.c12.CpuIsolatedService' in b)
  assert 'android:exported' in block and 'android:isolatedProcess' in block
  assert re.search(r'android:isolatedProcess.*0xffffffff',block)
  assert re.search(r'android:exported.*0x0',block)
 if 'unsigned' not in name:
  signing=subprocess.check_output([str(sdk/'apksigner.bat'),'verify','--verbose','--print-certs',str(dest)],env=environment).decode('utf-8',errors='replace');(e/(name+'.signing.txt')).write_text(signing,encoding='utf-8');row['certificate_sha256']=re.search(r'Signer #1 certificate SHA-256 digest: (\S+)',signing)[1]
  aligned=subprocess.run([str(sdk/'zipalign.exe'),'-c','-P','16','-v','4',str(dest)],capture_output=True,text=True,encoding='utf-8');(e/(name+'.zipalign.txt')).write_text(aligned.stdout+aligned.stderr,encoding='utf-8');assert aligned.returncode==0
 rows.append(row)
assert len({r['certificate_sha256'] for r in rows if 'certificate_sha256' in r})==1
(e/'apk-audit.json').write_text(json.dumps({'candidateId':'D1-20261016-C12','apks':rows,'android_loading':'NOT_RUN','16KiB_page_device_execution':'NOT_RUN'},indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
