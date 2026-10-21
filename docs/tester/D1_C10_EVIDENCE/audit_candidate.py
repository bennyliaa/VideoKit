import hashlib,json,pathlib,shutil,struct,zipfile
R=pathlib.Path(r'D:\CodexProjects\VideoKit');B=pathlib.Path(__file__).resolve().parent;E=R/'docs/coder/d1c10/evidence';C=B/'candidate';C.mkdir(exist_ok=True)
def sha(data):return hashlib.sha256(data).hexdigest()
summary=json.loads((E/'freeze-summary.json').read_text());assert sha((E/'freeze-summary.json').read_bytes())=='4b728a9b5694e096e0374cd8d2e5bb77ce53afb173e512d0308d8f9ca4e0deec'
for r in summary['artifacts']:
 dst=C/pathlib.Path(r['path']).name;assert not dst.exists(),'COPY_MUST_BE_EXCLUSIVE';shutil.copyfile(R/r['path'],dst);assert dst.stat().st_size==r['bytes'] and sha(dst.read_bytes())==r['sha256']
assert sha((C/'D1-20261016-C10-source.zip').read_bytes())=='7ab367f61f0e185d9ae4f70dbcbb6c2502e4cb03fdf46441e145c93fb5ea7a70'
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
with zipfile.ZipFile(C/'D1-20261016-C10-source.zip') as z:
 for name in z.namelist():
  if name.endswith(('/C10CpuDeviceTests.java','/C10DeviceTests.java','/C10IsolatedDeviceTests.java','/CpuTaskClient.java','/CpuIsolatedService.java','/CpuEnvironment.java','/CpuLifecycle.java','/CpuDiagnostics.java','/DeviceFixtures.java')):
   (B/pathlib.Path(name).name).write_bytes(z.read(name))
result=dict(result='DEBUG_G01_PASS',candidate='D1-20261016-C10',copiedArtifacts=len(summary['artifacts']),nativeEntriesVerified=natives,unchangedFfmpegAndAllocator=unchanged,localAssertions=321,productAdmission='NOT_APPROVED',scope='C10 lifecycle/glue changes; unchanged C09 FFmpeg/allocator license/security review retained; no build or device execution')
(B/'admission-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
