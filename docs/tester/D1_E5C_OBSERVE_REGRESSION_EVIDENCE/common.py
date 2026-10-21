"""One authorized E5C batch, split by explicit tester review gates. Never retries/kills ADB or device owners."""
from pathlib import Path
import subprocess,json,hashlib,time,sys,re,struct,shlex
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
ADB='D:/Android/SDK/platform-tools/adb.exe';SERIAL='HA1Q6WXR';TOTAL=32*1024*1024
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,value):
    with (E/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def load(name):return json.loads((E/name).read_bytes())
def call(name,args,cap=256*1024):
    save(name+'-attempt.json',dict(args=args,serial=SERIAL,began=time.time()))
    argv=[ADB,'-s',SERIAL,*args];began=time.monotonic();p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    chunks=[];count=0;overflow=False
    # Drain to actual client return; do not cancel/kill on a host clock or substitute for device close.
    while True:
        b=p.stdout.read(4096)
        if not b:break
        count+=len(b)
        if count<=cap:chunks.append(b)
        else:overflow=True
    p.stdout.close();rc=p.wait();b=b''.join(chunks)
    with (E/(name+'-stdout.txt')).open('xb') as out:out.write(b)
    row=dict(argv=argv,exitCode=rc,elapsedSeconds=time.monotonic()-began,receivedBytes=count,savedBytes=len(b),sha256=sha(b),overflow=overflow,clientReturned=True)
    save(name+'-receipt.json',row)
    assert sum(x.stat().st_size for x in E.glob('*-stdout.txt'))<=TOTAL,'BATCH_LOG_BUDGET'
    assert not overflow,'OUTPUT_BUDGET_EXCEEDED'
    print(json.dumps(dict(call=name,exitCode=rc,bytes=count,elapsedSeconds=row['elapsedSeconds'])),flush=True)
    assert rc==0,name+' ADB_RETURN_NONZERO'
    return b.decode('utf-8',errors='replace').replace('\r\n','\n')
TASK='86cafdb3-0fc4-447d-920b-b19c884bf494';BUDGET='730a73e1-50e1-4198-a515-047104f00e31'
SCRIPT='''set -eu
printf 'APP_UID|'; id -u
printf 'APP_PWD|'; pwd
for p in files/e4a_output_budget/identity.anchor files/e4a_output_budget/ledger.bin files/e4a_output_budget/operation.pending files/e4a_outputs/TASK.identity files/e4a_outputs/TASK.journal files/e4a_outputs/TASK.lease files/e4a_outputs/TASK.owner files/e4a_outputs/TASK.mp4; do
 test -f "$p"; test ! -L "$p"
 printf 'STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
done
for p in files/e4a_output_budget/identity.anchor files/e4a_output_budget/ledger.bin files/e4a_output_budget/operation.pending files/e4a_outputs/TASK.identity files/e4a_outputs/TASK.journal files/e4a_outputs/TASK.lease files/e4a_outputs/TASK.owner; do
 n=$(stat -c %s "$p"); test "$n" -le 2048
 printf 'SHA|'; sha256sum "$p"
done
printf 'ANCHOR|'; cat files/e4a_output_budget/identity.anchor; printf '\n'
printf 'LEDGER_BEGIN\n'; cat files/e4a_output_budget/ledger.bin; printf 'LEDGER_END\n'
for p in files/e4a_outputs/TASK.identity files/e4a_outputs/TASK.journal files/e4a_outputs/TASK.lease; do
 printf 'HEX_BEGIN|%s\n' "$p"; od -An -v -tx1 "$p"; printf 'HEX_END\n'
done
for p in files/e4a_output_budget/N2-e5-recovery files/e4a_output_budget/N2-e5-recovery.complete files/e4a_output_budget/operation.pending.N2-e5-aborted; do
 if [ -e "$p" ] || [ -L "$p" ]; then printf 'UNEXPECTED|%s\n' "$p"; exit 44; fi
done
for p in files/e4_fixtures/basic.mp4 files/e4_fixtures/subtitle.avi; do
 test -f "$p"; test ! -L "$p"; printf 'FIXTURE_STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
done
'''.replace('TASK',TASK)
def private(name):return call(name,['shell','run-as com.videokit.app sh -c '+shlex.quote(SCRIPT)])
def expected(s):
    assert 'APP_UID|10221\n' in s and 'APP_PWD|/data/user/0/com.videokit.app\n' in s
    ledger='E4A1 '+BUDGET+' 4194304 2097152 128\nR '+TASK+' D1-E4A-N2-TABLET-20261017 6660cfb1b19dee6ced8fb9427d6605eb394ba9ecd9ab5931905a9a8727ffd026\n'
    assert s.split('LEDGER_BEGIN\n')[1].split('LEDGER_END')[0]==ledger
    def utf(v):b=v.encode();return struct.pack('>H',len(b))+b
    identity=utf('E4A_ORIGINAL_IDENTITY_V1')+utf('D1-E4A-N2-TABLET-20261017')+utf(BUDGET)+utf(TASK.replace('-',''))+struct.pack('>qq',5131975343750146374,1)+utf('775a5ee9-fff3-4340-a03b-97751099c0c4')+struct.pack('>ii',10221,10221)+utf(TASK)
    journal=struct.pack('>i',0x45344131)+utf(TASK)+struct.pack('>i',0)+utf('a256356e-361b-47a0-b2e9-32dce4ccea8e')+b'\1'
    for suffix,value in [('identity',identity),('journal',journal),('lease',b'a256356e-361b-47a0-b2e9-32dce4ccea8e')]:
        h=s.split('HEX_BEGIN|files/e4a_outputs/'+TASK+'.'+suffix+'\n')[1].split('HEX_END')[0]
        assert bytes.fromhex(h)==value,suffix
    assert re.search(r'STAT\|files/e4a_outputs/'+TASK+r'\.mp4\|\d+,\d+,0,10221,',s)
    assert 'FIXTURE_STAT|files/e4_fixtures/basic.mp4|64522,20198,349102,10221,8180,1792207996' in s
    assert 'FIXTURE_STAT|files/e4_fixtures/subtitle.avi|64522,20199,736454656,10221,8180,1792208513' in s
def core(s):return [x for x in s.splitlines() if x.startswith(('STAT|','SHA|','FIXTURE_STAT|'))]
def artifacts():
    assert sha((R/'docs/coder/d1e5c/evidence/e5c-freeze.json').read_bytes())=='75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c'
    plan=json.loads((R/'docs/coder/d1e5c/tools/device_plan.json').read_bytes())
    for a in plan['artifactIdentity']:
        b=(R/a['path']).read_bytes();assert len(b)==a['bytes'] and sha(b)==a['sha256']
    return plan
def packages(name,version,appsha,testsha):
    script="set -eu; getprop ro.product.model; getprop ro.build.version.sdk; getprop ro.product.cpu.abilist; am get-current-user; dumpsys package com.videokit.app; dumpsys package com.videokit.app.test; df -k /data"
    s=call(name,['shell',script]);assert s.startswith('TB138FC\n31\narm64-v8a,armeabi-v7a,armeabi\n0\n')
    assert 'userId=10221' in s and 'userId=10222' in s
    assert re.search(r'versionCode='+str(version)+r'\b',s)
    assert 'installed=true' in s and 'hidden=false' in s and 'suspended=false' in s
    paths=re.findall(r'codePath=(/data/app/[^\s]+)',s);assert len(paths)==2,paths
    for p in paths:assert re.fullmatch(r'/data/app/[A-Za-z0-9_~+=./-]+',p)
    for role,path,h in [('app',paths[0],appsha),('test',paths[1],testsha)]:
        actual=call(name+'-'+role+'-apk',['shell','sha256sum',path+'/base.apk']);assert actual.split()[0]==h
    df=s.split('Filesystem')[-1].splitlines()[-1].split();assert int(df[3])>=65536,'INSUFFICIENT_FREE_SPACE'
    return dict(version=version,appSha256=appsha,testSha256=testsha,uid=10221,testUid=10222)

