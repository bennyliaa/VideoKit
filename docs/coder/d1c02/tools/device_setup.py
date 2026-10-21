"""Run only after coordinator obtains USB/device authorization. No network/upload."""
import argparse,hashlib,json,subprocess,shutil,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--serial',required=True);p.add_argument('--authorized',action='store_true');p.add_argument('--large',action='store_true');p.add_argument('--cleanup',action='store_true');args=p.parse_args()
if not args.authorized:p.error('Coordinator must obtain device authorization before setup/cleanup; then pass --authorized')
root=Path(__file__).resolve().parents[4];adb=Path('D:/Android/SDK/platform-tools/adb.exe');prefix=[str(adb),'-s',args.serial];package='com.videokit.app'
def run(*command):return subprocess.check_output(prefix+list(command),stderr=subprocess.STDOUT).decode('utf-8',errors='replace').strip()
fixtures={'basic.mp4':root/'test_media/imgs_and_videos/videos/sample.mp4','subtitle.avi':root/'test_media/02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi','subtitle.srt':root/'test_media/02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.chs.srt'}
if args.large:fixtures['large.mkv']=root/'test_media/03_large_files/large_video_over_2GiB.mkv'
if args.cleanup:
    # Fixed, app-owned aliases only; never delete a user-provided arbitrary directory.
    for name in ('basic.mp4','subtitle.avi','subtitle.srt','large.mkv'):run('shell','run-as',package,'rm','-f','files/d1_c02_fixtures/'+name)
    print('Removed only four D1 fixture aliases. APK uninstall and successful outputs require coordinator retention decision.');sys.exit(0)
def hashfile(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
artifacts=root/'docs/coder/d1c02/artifacts/D1-20261005-C02';manifest=json.loads((root/'docs/coder/d1c02/evidence/freeze-summary.json').read_text(encoding='utf-8'))
for name in ('app-debug.apk','app-debug-androidTest.apk'):
    apk=artifacts/name;expected=next(x['sha256'] for x in manifest['artifacts'] if Path(x['path']).name==name)
    if hashfile(apk)!=expected:raise RuntimeError('Frozen APK hash mismatch')
    print(run('install','-r',str(apk)))
print('Device free space:',run('shell','df','-k','/data'));run('shell','run-as',package,'mkdir','-p','files/d1_c02_fixtures')
records=[]
for name,source in fixtures.items():
    source=source.resolve()
    if not source.is_relative_to((root/'test_media').resolve()):raise RuntimeError('source boundary')
    digest=hashfile(source);destination='files/d1_c02_fixtures/'+name
    process=subprocess.Popen(prefix+['exec-in','run-as',package,'tee',destination],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        with source.open('rb') as src:shutil.copyfileobj(src,process.stdin,1024*1024)
        process.stdin.close();process.stdin=None;_,error=process.communicate(timeout=120)
        if process.returncode:raise RuntimeError('fixture transfer failed: '+error.decode(errors='replace'))
    except Exception:
        process.kill();raise
    device=run('shell','run-as',package,'sha256sum',destination).split()[0]
    if device!=digest:raise RuntimeError('device fixture hash mismatch')
    records.append({'alias':name,'bytes':source.stat().st_size,'sha256':digest});print(name,'SHA256 match',digest)
print(json.dumps({'serial':args.serial,'fixtures':records,'computer_sources':'read-only, unchanged'},indent=2))
