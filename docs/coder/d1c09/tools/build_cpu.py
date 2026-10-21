from pathlib import Path
import subprocess,hashlib,json,sys,shutil,os
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c09';build=base/'outputs/ffmpeg-build';src=base/'upstream/source/ffmpeg-8.0.3';out=base/'native-libs/arm64-v8a'
admission=json.loads((base/'evidence/ffmpeg-admission.json').read_text(encoding='utf-8'));assert admission['admission']=='DEBUG_LOCAL_EXPERIMENT_ONLY'
tool=Path('D:/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin');source=base/'native/cpu.c';library=out/'libvideokit_cpu.so'
command=[str(tool/'clang.exe'),'--target=aarch64-linux-android31','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-Wl,--no-undefined','-Wl,-z,max-page-size=16384','-Wl,-soname,libvideokit_cpu.so','-I'+str(src),'-I'+str(build),str(source)]
for lib in ['avformat','avcodec','swscale','avutil']:command+=['-L'+str(build/('lib'+lib)),'-l'+lib]
command+=['-L'+str(base/'outputs/allocator'),'-lvideokit_alloc','-MMD','-MF',str(base/'outputs/cpu-native.d'),'-o',str(library)]
temp=base/'outputs/native-temp';temp.mkdir(exist_ok=True);environment=os.environ.copy();environment['TMP']=str(temp);environment['TEMP']=str(temp)
log=base/'evidence/cpu-native-compile.log'
if log.exists():shutil.copyfile(log,base/'evidence/cpu-native-compile-attempt1.log')
result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',env=environment);log.write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for lib in admission['libraries']:
 p=root/lib['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==lib['sha256'];shutil.copyfile(p,out/lib['soname'][0])
shutil.copyfile(base/'outputs/allocator/libvideokit_alloc.so',out/'libvideokit_alloc.so')
dump=subprocess.check_output([str(tool/'llvm-readelf.exe'),'-h','-lW','-d',str(library)]).decode('utf-8');(base/'evidence/cpu-native-readelf.txt').write_text(dump,encoding='utf-8')
symbols=subprocess.check_output([str(tool/'llvm-nm.exe'),'-D',str(library)]).decode('utf-8');(base/'evidence/cpu-native-symbols.txt').write_text(symbols,encoding='utf-8')
assert 'Java_com_videokit_spike_c09_NativeCpu_decode' in symbols
(base/'evidence/cpu-native-build.json').write_text(json.dumps({'command':command,'source':row(source),'library':row(library),'libraries':[row(p) for p in sorted(out.glob('*.so'))],'scope':'local NDK compile/static only; Android isolated loading NOT_RUN'},indent=2),encoding='utf-8');print('CPU JNI compile PASS; debug-only libraries copied after audit')
