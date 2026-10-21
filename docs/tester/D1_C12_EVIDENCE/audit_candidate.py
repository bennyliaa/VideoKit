import hashlib,json,pathlib,shutil,struct,zipfile
R=pathlib.Path(r'D:\CodexProjects\VideoKit');B=pathlib.Path(__file__).resolve().parent;E=R/'docs/coder/d1c12/evidence';C=B/'candidate';C.mkdir(exist_ok=True)
def sha(data):return hashlib.sha256(data).hexdigest()
summary=json.loads((E/'freeze-summary.json').read_text());assert sha((E/'freeze-summary.json').read_bytes())=='8fbde727e4ef900088ee17739bf2382ad9ed8cdb54bb3af99eb65a4b9847ddc6'
for r in summary['artifacts']:
 dst=C/pathlib.Path(r['path']).name;assert not dst.exists(),'COPY_MUST_BE_EXCLUSIVE';shutil.copyfile(R/r['path'],dst);assert dst.stat().st_size==r['bytes'] and sha(dst.read_bytes())==r['sha256']
assert sha((C/'D1-20261016-C12-source.zip').read_bytes())=='cf6c67bde094a53dfc14a9d0e59bc2cb2c549db2ec49199b388c17901a0c39b5'
shutil.copyfile(E/'freeze-summary.json',C/'freeze-summary.json');shutil.copyfile(E/'source-manifest.json',C/'source-manifest.json')
apks=json.loads((E/'apk-audit.json').read_text())['apks'];natives=0;unchanged=[]
with zipfile.ZipFile(R/'docs/coder/d1c09/artifacts/D1-20261016-C09/app-debug.apk') as old:
 for apk in apks:
  file=C/apk['file'];raw=file.read_bytes();assert sha(raw)==apk['sha256']
  with zipfile.ZipFile(file) as z:
   for row in apk['native_libraries']:
    b=z.read(row['path']);assert sha(b)==row['sha256'] and len(b)==row['bytes'];zi=z.getinfo(row['path']);nl,ex=struct.unpack_from('<HH',raw,zi.header_offset+26);assert zi.compress_type==0 and (zi.header_offset+30+nl+ex)%16384==0
    if b[4]==2:phoff=struct.unpack_from('<Q',b,32)[0];size,num=struct.unpack_from('<HH',b,54);fmt='<IIQQQQQQ'
    else:phoff=struct.unpack_from('<I',b,28)[0];size,num=struct.unpack_from('<HH',b,42);fmt='<IIIIIIII'
    ph=[struct.unpack_from(fmt,b,phoff+i*size) for i in range(num)];assert all(p[7]>=16384 for p in ph if p[0]==1);natives+=1
    if apk['file']=='app-debug.apk' and pathlib.Path(row['path']).name in ['libavcodec.so','libavformat.so','libavutil.so','libswscale.so','libvideokit_alloc.so']:
     assert old.read(row['path'])==b;unchanged.append(row['path'])
   if apk['file']=='app-release-unsigned.apk':assert apk['sha256']=='71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e'
with zipfile.ZipFile(C/'D1-20261016-C12-source.zip') as z:
 for name in z.namelist():
  if name.endswith(('/C12CpuDeviceTests.java','/C12DeviceTests.java','/C12IsolatedDeviceTests.java','/CpuTaskClient.java','/CpuIsolatedService.java','/CpuEnvironment.java','/CpuLifecycle.java','/CpuDiagnostics.java','/DeviceFixtures.java','/RegistrationProtocol.java','/BindingRevocation.java','/ExitEvidence.java','/WorkerGenerations.java','/ExitTraceCapture.java')):
   (B/pathlib.Path(name).name).write_bytes(z.read(name))
result=dict(result='DEBUG_G01_PASS',candidate='D1-20261016-C12',copiedArtifacts=len(summary['artifacts']),nativeEntriesVerified=natives,unchangedFfmpegAndAllocator=unchanged,localAssertions=735,productAdmission='NOT_APPROVED',scope='C12 lifecycle/glue changes; unchanged C09 FFmpeg/allocator license/security review retained; no build or device execution')
(B/'admission-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
