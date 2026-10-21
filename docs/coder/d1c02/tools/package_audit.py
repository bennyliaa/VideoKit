"""Local, read-only APK audit; copy only completed build outputs into candidate directory."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c02';out=base/'evidence';artifacts=base/'artifacts/D1-20261005-C02'
artifacts.mkdir(parents=True,exist_ok=True)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
rows=[];media_names={p.name for p in (root/'test_media').rglob('*') if p.is_file()}
aapt=Path('D:/Android/SDK/build-tools/36.1.0/aapt.exe')
if not aapt.exists():aapt=sorted(Path('D:/Android/SDK/build-tools').glob('*/aapt.exe'))[-1]
for source in sorted((root/'app/build/outputs/apk').rglob('*.apk')):
    dest=artifacts/source.name;shutil.copy2(source,dest)
    with zipfile.ZipFile(dest) as z:
        names=z.namelist();spike=[n for n in names if n.endswith('.dex') and b'Lcom/videokit/spike/c02/' in z.read(n)]
        row={'path':dest.relative_to(root).as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest),'sample_named_entries':[n for n in names if Path(n).name in media_names],'c02_dex':spike,'native_libraries':[n for n in names if n.endswith('.so')],'model_entries':[n for n in names if n.lower().endswith(('.onnx','.tflite','.pth'))]}
        if row['sample_named_entries'] or row['model_entries']:raise RuntimeError('Unexpected sample/model package entry')
        if 'release' in dest.name and spike:raise RuntimeError('Debug spike leaked into release')
        rows.append(row)
    badging=subprocess.check_output([str(aapt),'dump','badging',str(dest)],stderr=subprocess.STDOUT).decode(errors='replace')
    manifest=subprocess.check_output([str(aapt),'dump','xmltree',str(dest),'AndroidManifest.xml'],stderr=subprocess.STDOUT).decode(errors='replace')
    (out/(dest.name+'.badging.txt')).write_text(badging,encoding='utf-8');(out/(dest.name+'.manifest.txt')).write_text(manifest,encoding='utf-8')
    if dest.name=='app-debug.apk' and 'android:isolatedProcess' not in manifest:raise RuntimeError('Missing isolated service declaration')
    row['internet_permission']='android.permission.INTERNET' in badging
(out/'apk-audit.json').write_text(json.dumps({'aapt':str(aapt),'scope':'static package/manifest evidence, no Android execution','apks':rows},indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
