from pathlib import Path
import subprocess,json,hashlib,sys,os
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c14';out=base/'outputs/allocator';out.mkdir(exist_ok=True);tmp=base/'outputs/native-temp';tmp.mkdir(exist_ok=True)
tool=Path('D:/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin');source=base/'native/quota.c';library=out/'libvideokit_alloc.so';env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp))
command=[str(tool/'clang.exe'),'--target=aarch64-linux-android31','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-Wl,--no-undefined','-Wl,-z,max-page-size=16384','-Wl,-soname,libvideokit_alloc.so',str(source),'-o',str(library)]
result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',env=env);(base/'evidence/quota-compile.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
(base/'evidence/quota-build.json').write_text(json.dumps({'command':command,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'contract':'64MiB aggregate FFmpeg allocator requested bytes, 4096 records, realloc charges old+new, unknown free aborts own worker; not a process RSS claim','execution':'NDK compilation only; device quota probe NOT_RUN'},indent=2),encoding='utf-8');print('Quota glue compile PASS')
