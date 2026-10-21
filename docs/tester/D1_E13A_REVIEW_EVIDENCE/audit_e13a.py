"""Tester-owned local audit; no ADB, builds, candidate tests, or remote scripts."""
from pathlib import Path
import base64,hashlib,json,os,re,shlex,struct,subprocess,sys,zipfile
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
B=R/'docs/coder/d1e13a';E=B/'evidence';C=[]
PIN='24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def ck(n,v,d=None):C.append(dict(name=n,passed=bool(v),detail=d))
def verify(row,n):
    b=(R/row['path']).read_bytes();ck(n,len(b)==row['bytes'] and sha(b)==row['sha256'],row['path'])
s=E/'e13a-freeze.json';seal=load(s);ck('external seal',sha(s.read_bytes())==PIN)
ck('270 immutable rows',len(seal['immutableFiles'])==270)
for row in seal['immutableFiles']:verify(row,'E13A immutable')
verify(seal['archive'],'archive pin')
ck('approved ZIP',seal['archive']['sha256']=='45765142b21ca193d1b5ca26feb2e1023e5151e95303fd9ba5b167c1cc37e48e')
with zipfile.ZipFile(R/seal['archive']['path']) as z:
    rows={r['path']:r for r in seal['immutableFiles'] if r['path']!=seal['archive']['path']}
    ck('269 ZIP exact members',len(z.namelist())==269 and len(set(z.namelist()))==269 and set(z.namelist())==set(rows))
    ck('private key excluded',not any(n.endswith('.p12') for n in z.namelist()))
    for n in z.namelist():
        b=z.read(n);ck('ZIP member',len(b)==rows[n]['bytes'] and sha(b)==rows[n]['sha256'],n)
for prior in seal['priorSeals']:
    verify(prior['seal'],'old seal')
    for row in load(R/prior['seal']['path'])['immutableFiles']:verify(row,'old immutable')
inputs=E/'final-build-inputs.json';ck('139 input snapshot',sha(inputs.read_bytes())=='2c71c4e24e28abff2c6cd03ad30e8a638e7a39b95c8b3eb91348c213df4b939c' and len(load(inputs)['files'])==139)
for row in load(inputs)['files']:verify(row,'final input')
for row in load(E/'source-derivation.json')['files']:
    verify(row['current'],'current derivation')
    if row['baseline']:verify(row['baseline'],'derivation baseline')
for row in load(E/'unchanged-source-lifecycle.json')['files']:
    verify(row['current'],'unchanged current');verify(row['baseline'],'unchanged original');ck('same source lifecycle',row['current']['sha256']==row['baseline']['sha256'])
j=load(E/'host-jar-manifest.json');verify(j['jar'],'JAR pin')
with zipfile.ZipFile(R/j['jar']['path']) as z:
    ck('172 exact production classes',len(j['classes'])==172 and set(z.namelist())=={r['entry'] for r in j['classes']})
    ck('no checker classes',not any('E13ABindingCheck' in n or 'E13ProductionCheck' in n or 'E13SourceCases' in n for n in z.namelist()))
    for row in j['classes']:
        b=z.read(row['entry']);ck('JAR byte',len(b)==row['bytes'] and sha(b)==row['sha256'],row['entry']);verify(row['source'],'JAR source')
def snapshot():
    paths={R/r['path'] for r in seal['immutableFiles']}|{s}
    for folder,dirs,files in os.walk(B):
        dirs[:]=[d for d in dirs if d not in {'.checks','.gradle','build','__pycache__'}]
        paths.update(Path(folder)/f for f in files)
    return {str(p.relative_to(R)):sha(p.read_bytes()) for p in paths if p.is_file()}
before=snapshot();runs=[]
for name,args in [('default',[]),('verify',['verify','--seal-sha',PIN]),('help',['--help']),('pack-help',['pack','--help'])]:
    argv=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py')]+args
    p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    (O/('readonly-'+name+'.txt')).write_bytes(p.stdout)
    ck('readonly entry exit0',p.returncode==0,name)
    if name in ['default','verify']:ck('readonly entry result',json.loads(p.stdout)['status']=='PASS_E13A_STRICT_READONLY_VERIFY',name)
    runs.append(dict(mode=name,argv=argv,exitCode=p.returncode,stdoutSha256=sha(p.stdout),bytes=len(p.stdout)))
after=snapshot();ck('all candidate snapshot bytes unchanged',before==after,len(before))
sdk=Path('D:/Android/SDK');java=Path('D:/Android/Android Studio/jbr/bin/java.exe')
sdkRuns=[]
def inspect(n,args):
    p=subprocess.run([str(a) for a in args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    (O/(n+'.txt')).write_bytes(p.stdout);ck('independent SDK inspection',p.returncode==0 and len(p.stdout)<=65536,n)
    sdkRuns.append(dict(name=n,argv=[str(a) for a in args],exitCode=p.returncode,bytes=len(p.stdout),sha256=sha(p.stdout)))
    return p.stdout.decode('utf-8',errors='replace')
def dexclasses(raw):
    def u(p):return struct.unpack_from('<I',raw,p)[0]
    result=[]
    for i in range(u(96)):
        p=u(u(60)+4*u(u(68)+4*u(u(100)+i*32)))
        while raw[p]&128:p+=1
        p+=1;result.append(raw[p:raw.index(0,p)].decode())
    return result
apks=load(E/'apk-delivery/apk-audit.json')['apks'];defs={}
for a in apks:
    verify(a,'final APK')
    txt=inspect(a['kind']+'-signature',[java,'-jar',sdk/'build-tools/36.0.0/lib/apksigner.jar','verify','--print-certs',R/a['path']])
    ck('actual signer','Signer #1 certificate SHA-256 digest: '+a['signer'] in txt,a['kind'])
    txt=inspect(a['kind']+'-manifest',[sdk/'build-tools/36.0.0/aapt.exe','dump','xmltree',R/a['path'],'AndroidManifest.xml'])
    ck('actual package','package="'+a['package']+'"' in txt,a['kind'])
    if a['kind']=='app':ck('v17 actual',bool(re.search(r'versionCode\(0x0101021b\)=(?:17\b|\(type 0x10\)0x11\b)',txt)) and '"ACTIVATION"' in txt)
    with zipfile.ZipFile(R/a['path']) as z:defs[a['kind']]=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))]
for k in ['app','fixture']:ck('actual shared BindingOwner class','Lcom/videokit/spike/e4/E13BindingOwner;' in defs[k],k)
ck('fixture no Kotlin definitions',not any(c.startswith('Lkotlin/') for c in defs['fixture']))
d=load(E/'apk-delivery/sbom-difference.json');verify(d['lock'],'dependency lock')
ck('35 unchanged coordinates',(R/d['lock']['path']).read_bytes()==(R/'docs/coder/d1e13/app/gradle.lockfile').read_bytes() and len([s for s in (R/d['lock']['path']).read_text().splitlines() if s and not s.startswith(('#','empty='))])==35)
fixturelock=(B/'fixture/gradle.lockfile').read_text();ck('fixture empty runtime',all(not s or s.startswith(('#','empty=')) for s in fixturelock.splitlines()) and 'debugRuntimeClasspath' in fixturelock)
with zipfile.ZipFile(R/next(a['path'] for a in apks if a['kind']=='app')) as z:
    ck('7 APK native libraries',len([n for n in z.namelist() if n.endswith('.so')])==7)
    for row in d['nativeLibraries']:
        verify(row,'native pin');ck('APK native equals original',sha(z.read(row['entry']))==row['sha256'],row['entry'])
binding=load(E/'binding-check-summary.json');ck('9 groups 72 recorded assertions',binding['groups']==9 and binding['assertions']==72 and sum(r['assertions'] for r in binding['logs'])==72)
for row in binding['logs']:
    verify(row['log'],'binding raw log');p=R/row['log']['path'];exitfile=p.with_name(p.name.replace('.stdout.txt','.exit.json'))
    ck('recorded binding exit0',load(exitfile)['exitCode']==0,p.name)
for row in load(E/'sdk-binding-contract.json')['sources']:verify(row,'SDK primary source')
plan=load(B/'release/metadata/three-client-manifest.json');source=load(R/plan['sourceFieldPlan']['path']);verify(plan['sourceFieldPlan'],'tester field plan')
expected=load(B/'release/metadata/expected-baseline.json');ck('34stat18control',len(expected['fixedStat'])==34 and len(expected['fixedControlPins'])==18)
ck('original control pins unchanged',expected['fixedControlPins']==source['fixedControlPins'])
ck('original stat paths unchanged',set(expected['fixedStat'])==set(source['fixedStatPaths']))
ck('ledger exact accepted',expected['ledger']==source['ledger'] and expected['ledger']['bytes']==2271 and expected['ledger']['sha256']=='e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649')
metadata=[]
for cl,count,bound in zip(plan['clients'],[70,18,71],[53512,27588,56360]):
    argfile=B/'release/metadata'/(cl['id']+'.argv.json');item=load(argfile);ck('manifest and argv record identical',item==cl,cl['id']);verify(cl['script'],'metadata script')
    script=(R/cl['script']['path']).read_text();argv=cl['argv']
    ck('one exact direct adb argv',argv[:6]==['D:/Android/SDK/platform-tools/adb.exe','-s','HA1Q6WXR','shell','sh','-c'] and len(argv)==7 and shlex.split(argv[-1])==[script],cl['id'])
    ck('metadata count/cap arithmetic',len(cl['records'])==count and sum(r['maxBytes']+len(r['label'])*2+16 for r in cl['records'])+256==bound==cl['recordOutputUpperBound']<65536,cl['id'])
    ck('record labels unique',len({r['label'] for r in cl['records']})==count,cl['id'])
    if cl['id']!='M2_POST_DEPLOY_PRE_CASE':
        ck('exact 34 stat and 18 controls in records',{r['label'][5:] for r in cl['records'] if r['label'].startswith('STAT:')}==set(expected['fixedStat']) and {r['label'][8:] for r in cl['records'] if r['label'].startswith('CONTROL:')}=={r['path'] for r in expected['fixedControlPins']},cl['id'])
    metadata.append(dict(id=cl['id'],script=cl['script'],argvFile=dict(path=argfile.relative_to(R).as_posix(),bytes=argfile.stat().st_size,sha256=sha(argfile.read_bytes())),records=count,upperBound=bound))
ck('48 processes 2MiB unchanged',1+32+6+6+3==plan['budgetPcTotal']==48 and 32768+524288+6*81920+6*65536+3*65536+458752==plan['budgetTextTotal']==2097152)
syntax=load(E/'metadata-syntax.json');ck('29 recorded syntax-only checks',len(syntax['checks'])==29 and all(c['exitCode']==0 for c in syntax['checks']))
result=dict(atUtc=datetime.now(timezone.utc).isoformat(),scope='LOCAL_READONLY_NO_DEVICE_BUILD_TEST_OR_REMOTE_SCRIPT_EXECUTION',status='PASS_LOCAL_AUDIT' if all(c['passed'] for c in C) else 'FAIL_LOCAL_AUDIT',checkCount=len(C),failed=[c for c in C if not c['passed']],checks=C,readonlyEntryRuns=runs,snapshotFilesUnchanged=len(before),independentSdkInspections=sdkRuns,metadataPins=metadata,actualDexDefinitions={k:len(v) for k,v in defs.items()})
(O/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','checkCount','failed','snapshotFilesUnchanged','actualDexDefinitions']},ensure_ascii=False))
