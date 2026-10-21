"""Tester-owned read-only audit. Never imports/runs candidate code or contacts devices."""
from pathlib import Path
import hashlib,json,re,struct,subprocess,zipfile
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
B=R/'docs/coder/d1e13'; E=B/'evidence'
checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
def verify(row,label):
    b=(R/row['path']).read_bytes()
    check(label,len(b)==row['bytes'] and sha(b)==row['sha256'],row['path'])
def pin(p):
    b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=sha(b))
s=E/'e13-freeze.json';seal=load(s)
check('E13 seal',sha(s.read_bytes())=='3b80d430aa7f859174ffae0a4b5ca948a01aa032d15c0666fb595e6a1bba5cc0')
check('367 rows',len(seal['immutableFiles'])==367)
for row in seal['immutableFiles']:verify(row,'E13 immutable')
verify(seal['archive'],'ZIP')
check('ZIP approved hash',seal['archive']['sha256']=='dbaa6f510b54ad17e020b81be0d4e26ff378c7f4de1d40da4dea2f5230af98bb')
with zipfile.ZipFile(R/seal['archive']['path']) as z:
    rows={x['path']:x for x in seal['immutableFiles'] if x['path']!=seal['archive']['path']}
    check('366 exact ZIP members',len(z.namelist())==366 and len(set(z.namelist()))==366 and set(z.namelist())==set(rows))
    for n in z.namelist():
        b=z.read(n);p=rows[n];check('ZIP bytes',len(b)==p['bytes'] and sha(b)==p['sha256'],n)
for old in seal['priorSeals']:
    verify(old['seal'],'prior seal')
    rows=load(R/old['seal']['path'])['immutableFiles']
    check('prior row count',len(rows)==old['immutableRowsVerified'])
    for row in rows:verify(row,'prior immutable')
inputs=load(E/'final-build-inputs.json')['files']
check('138 final inputs',len(inputs)==138)
check('final input snapshot',sha((E/'final-build-inputs.json').read_bytes())=='6eeea5bd2a5faf97cea6f7905f01ebf4f1c91a22707cd1a5d61dd1f93bccbd95')
for row in inputs:verify(row,'final build input')
for row in load(E/'local-checks/final-003/inputs.json'):verify(row,'final local-check source input')
for row in load(E/'requirements-and-accepted-source-pins.json')['files']:verify(row,'accepted requirements')
derivation=load(E/'source-derivation.json')['files']
for row in derivation:
    verify(row['current'],'derivation current')
    if row['baseline']:verify(row['baseline'],'derivation baseline')
    check('derivation relationship',(row['relationship']=='BYTE_IDENTICAL')==(bool(row['baseline']) and row['baseline']['sha256']==row['current']['sha256']),row['current']['path'])
for row in load(E/'selfcheck-registry-provenance.json')['files']:
    for k in ['actualFinalCheckInput','portableCopy','acceptedSource']:verify(row[k],'registry provenance')
    check('registry copies identical',len({row[k]['sha256'] for k in ['actualFinalCheckInput','portableCopy','acceptedSource']})==1)
j=load(E/'host-jar-manifest.json');verify(j['jar'],'final JAR')
with zipfile.ZipFile(R/j['jar']['path']) as z:
    check('170 production classes',len(j['classes'])==170 and set(z.namelist())=={c['entry'] for c in j['classes']})
    for row in j['classes']:
        b=z.read(row['entry']);check('JAR class bytes',len(b)==row['bytes'] and sha(b)==row['sha256'],row['entry']);verify(row['source'],'JAR source pin')
    check('no checker classes',not any('E13ProductionCheck' in n or 'E13SourceCases' in n for n in z.namelist()))
    check('no distributed signing key',not any(n.endswith('.p12') for n in zipfile.ZipFile(R/seal['archive']['path']).namelist()))
sdk=Path('D:/Android/SDK');java=Path('D:/Android/Android Studio/jbr/bin/java.exe')
toolruns=[]
def tool(name,args):
    run=subprocess.run([str(a) for a in args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    check('independent SDK inspection',run.returncode==0,name)
    check('inspection output bounded',len(run.stdout)<=65536,name)
    (O/(name+'.txt')).write_bytes(run.stdout)
    toolruns.append(dict(name=name,argv=[str(a) for a in args],exitCode=run.returncode,bytes=len(run.stdout),sha256=sha(run.stdout)))
    return run.stdout.decode('utf-8',errors='replace')
apks=load(E/'apk-delivery/apk-audit.json')['apks']
for a in apks:
    verify(a,'final APK')
    text=tool(a['kind']+'-signature',[java,'-jar',sdk/'build-tools/36.0.0/lib/apksigner.jar','verify','--print-certs',R/a['path']])
    check('actual signature',('Signer #1 certificate SHA-256 digest: '+a['signer']) in text,a['kind'])
    text=tool(a['kind']+'-manifest',[sdk/'build-tools/36.0.0/aapt.exe','dump','xmltree',R/a['path'],'AndroidManifest.xml'])
    check('actual package',('package="'+a['package']+'"') in text,a['kind'])
    if a['kind']=='app':
        check('v16 and ACTIVATION',bool(re.search(r'versionCode\(0x0101021b\)=(?:16\b|\(type 0x10\)0x10\b)',text)) and '"ACTIVATION"' in text)
        check('fixture visible and codec nonexported', '"com.videokit.e13.sender"' in text and '"com.videokit.spike.e4.E4CodecService"' in text and 'exported(0x01010010)=(type 0x12)0x0' in text)
diff=load(E/'sbom-difference.json')
verify(diff['lock'],'main dependency lock')
check('35 locked coordinates',len([s for s in (R/diff['lock']['path']).read_text().splitlines() if s and not s.startswith('#') and not s.startswith('empty=')])==35)
oldlock=R/'docs/coder/d1e11/app/gradle.lockfile'
check('main lock unchanged',(R/diff['lock']['path']).read_bytes()==oldlock.read_bytes())
check('fixture runtime empty','debugRuntimeClasspath' in (B/'fixture/gradle.lockfile').read_text() and all(s.startswith('#') or s.startswith('empty=') or not s for s in (B/'fixture/gradle.lockfile').read_text().splitlines()))
app=next(a for a in apks if a['kind']=='app')
with zipfile.ZipFile(R/app['path']) as z:
    check('7 native libraries exact',len([n for n in z.namelist() if n.endswith('.so')])==7)
    for row in diff['nativeLibraries']:
        verify(row,'native source pin');b=z.read(row['entry']);check('APK native byte equality',len(b)==row['bytes'] and sha(b)==row['sha256'],row['entry'])
fixture=next(a for a in apks if a['kind']=='fixture')
defined=[]
with zipfile.ZipFile(R/fixture['path']) as z:
    for name in z.namelist():
        if not name.endswith('.dex'):continue
        b=z.read(name)
        def u(p):return struct.unpack_from('<I',b,p)[0]
        for i in range(u(96)):
            p=u(u(60)+u(u(68)+u(u(100)+32*i)*4)*4)
            while b[p]&128:p+=1
            p+=1;defined.append(b[p:b.index(0,p)].decode('utf-8'))
check('292 actual fixture DEX definitions',len(defined)==292 and sorted(defined)==sorted(load(E/'fixture-defined-classes.json')['definedClasses']))
check('no Kotlin DEX definitions',not any(n.startswith('Lkotlin/') for n in defined))
groups=['authorizedHostSourceReadAndClose','oldGenerationNeverOpensSource','twoConsumersHoldSourceUntilLastReturn','cancelLateOpenRetainsOriginalOwner','lateReadAndCloseFailureDoNotReleaseEarly','DEPLOYMENT','BOUNDARIES']
totals=[0,0,0]
for group in groups:
    p=E/'local-checks/final-003'
    check('recorded final group exit0',load(p/(group+'.exit.json'))['exitCode']==0,group)
    text=(p/(group+'.stdout.txt')).read_text()
    check('recorded final PASS',('PASS_E13_' if group in ['DEPLOYMENT','BOUNDARIES'] else 'PASS_PRODUCTION_SOURCE_SCENARIO '+group) in text,group)
    m=re.search(r'opens=(\d+) reads=\d+ payload_bytes=(\d+) close_attempts=(\d+) retained=0',text)
    if m:totals=[a+int(b) for a,b in zip(totals,m.groups())]
check('recorded 6 open /4224 read bytes /7close',totals==[6,4224,7],totals)
check('text budget arithmetic',32768+524288+6*81920+6*65536+3*65536==1638400 and 1638400+458752==2097152)
check('process allocation arithmetic',1+32+6+6+3==48)
supplement=[pin(sdk/'sources/android-36.1/android/content/Context.java'),pin(sdk/'sources/android-36.1/android/app/ContextImpl.java')]
result=dict(atUtc=datetime.now(timezone.utc).isoformat(),status='PASS_LOCAL_BYTES' if all(c['passed'] for c in checks) else 'FAIL_LOCAL_BYTES',scope='READ_ONLY_INDEPENDENT_AUDIT_NO_ADB_NO_BUILD_NO_CANDIDATE_EXECUTION',checkCount=len(checks),failed=[c for c in checks if not c['passed']],checks=checks,independentSdkInspections=toolruns,supplementalSdkPins=supplement)
(O/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','checkCount','failed']},ensure_ascii=False))
