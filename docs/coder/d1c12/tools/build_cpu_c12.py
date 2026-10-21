from pathlib import Path
import subprocess,json,hashlib,sys,os,shutil,tarfile
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c12';old=root/'docs/coder/d1c09';src=base/'outputs/headers/source';build=base/'outputs/headers/build';out=base/'native-libs/arm64-v8a';temp=base/'outputs/native-temp';temp.mkdir(exist_ok=True)
inherit=base/'evidence/inherited-c09';identity=json.loads((inherit/'ffmpeg-source-identity.json').read_text(encoding='utf-8'));expected={r['path']:r['sha256'] for r in identity['files']}
object_map=json.loads((inherit/'ffmpeg-object-source-license-map.json').read_text(encoding='utf-8'));expected.update({r['path']:r['sha256'] for r in object_map['files']})
extra=json.loads((inherit/'jni-source-dependency-map.json').read_text(encoding='utf-8'));expected.update({r['path']:r['sha256'] for r in extra['dependencies']})
with tarfile.open(base/'upstream/ffmpeg-8.0.3.tar.xz','r:xz') as archive:
 for token in (inherit/'cpu-native-dependencies.txt').read_text(encoding='utf-8').replace('\\\n',' ').split()[1:]:
  p=Path(token)
  if p==old/'native/cpu.c':continue
  if p.is_relative_to(old/'upstream/source/ffmpeg-8.0.3'):
   relative=p.relative_to(old/'upstream/source/ffmpeg-8.0.3');data=archive.extractfile('ffmpeg-8.0.3/'+relative.as_posix()).read();target=src/relative
  elif p.is_relative_to(old/'outputs/ffmpeg-build'):
   relative=p.relative_to(old/'outputs/ffmpeg-build');data=(inherit/'ffmpeg-generated/tree'/relative).read_bytes();target=build/relative
  else:raise ValueError('Unexpected JNI include source:'+str(p))
  assert hashlib.sha256(data).hexdigest()==expected[p.relative_to(root).as_posix()],p
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
admission=json.loads((base/'evidence/inherited-native-admission.json').read_text(encoding='utf-8'))
for row in admission['unchangedNative']:assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']
tool=Path('D:/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin');source=base/'native/cpu.c';library=out/'libvideokit_cpu.so'
command=[str(tool/'clang.exe'),'--target=aarch64-linux-android31','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-Wl,--no-undefined','-Wl,-z,max-page-size=16384','-Wl,-soname,libvideokit_cpu.so','-I'+str(src),'-I'+str(build),str(source),'-L'+str(out),'-lavformat','-lavcodec','-lswscale','-lavutil','-lvideokit_alloc','-MMD','-MF',str(base/'outputs/cpu-native.d'),'-o',str(library)]
env=dict(os.environ,TMP=str(temp),TEMP=str(temp));result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',env=env);(base/'evidence/cpu-native-compile.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
old_c=(inherit/'c09-cpu.c').read_text(encoding='utf-8');assert source.read_text(encoding='utf-8')==old_c.replace('com_videokit_spike_c09','com_videokit_spike_c12')
dump=subprocess.check_output([str(tool/'llvm-readelf.exe'),'-h','-lW','-d',str(library)]).decode('utf-8');(base/'evidence/cpu-native-readelf.txt').write_text(dump,encoding='utf-8');symbols=subprocess.check_output([str(tool/'llvm-nm.exe'),'-D',str(library)]).decode('utf-8');assert 'Java_com_videokit_spike_c12_NativeCpu_decode' in symbols
(base/'evidence/cpu-native-symbols.txt').write_text(symbols,encoding='utf-8')
(base/'evidence/cpu-native-build.json').write_text(json.dumps({'command':command,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'librarySha256':hashlib.sha256(library.read_bytes()).hexdigest(),'nativeAlgorithmChanges':'NONE; only JNI package identity c09 -> c12','usedHeaders':'C09 immutable signed 8.0.3 source/generated config; complete archive/config copied in C12','device':'NOT_RUN'},indent=2),encoding='utf-8');print('C12 CPU JNI compile PASS; codec and quota unchanged')
