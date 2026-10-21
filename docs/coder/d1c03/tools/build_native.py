"""Build only independently-authored ARM64 Android API31 JNI flock adapter using installed NDK."""
from pathlib import Path
import subprocess,json,hashlib,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c03';ndk=Path('D:/Android/SDK/ndk/30.0.16248370');bin=ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin';source=base/'native/lease.c';output=base/'native-libs/arm64-v8a/libvideokit_d1_lease.so';output.parent.mkdir(parents=True,exist_ok=True)
command=[str(bin/'clang.exe'),'--target=aarch64-linux-android31','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-Wl,--no-undefined','-Wl,-z,max-page-size=16384','-Wl,-soname,libvideokit_d1_lease.so',str(source),'-o',str(output)]
subprocess.run(command,check=True)
readelf=subprocess.check_output([str(bin/'llvm-readelf.exe'),'-h','-l','-d',str(output)]).decode('utf-8',errors='replace');symbols=subprocess.check_output([str(bin/'llvm-nm.exe'),'-D',str(output)]).decode('utf-8',errors='replace')
(base/'evidence/native-readelf.txt').write_text(readelf,encoding='utf-8');(base/'evidence/native-symbols.txt').write_text(symbols,encoding='utf-8')
if 'Java_com_videokit_spike_c03_AndroidLease_tryLock' not in symbols or 'Java_com_videokit_spike_c03_AndroidLease_unlock' not in symbols:raise RuntimeError('JNI symbols missing')
result={'candidateId':'D1-20261005-C03','ndk_properties':(ndk/'source.properties').read_text(),'compiler_version':subprocess.check_output([str(bin/'clang.exe'),'--version']).decode(),'command':command,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,'abi':'arm64-v8a','api':31,'page_alignment':16384,'scope':'native compilation/static ELF only; actual Android syscall/Binder descriptor behavior NOT_RUN','authorship':'Independent project JNI adapter; no external algorithm/model code'}
(base/'evidence/native-build.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
