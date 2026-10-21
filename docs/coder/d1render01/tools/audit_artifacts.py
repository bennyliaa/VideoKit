from pathlib import Path
import hashlib,json,shutil,zipfile,struct,subprocess,xml.etree.ElementTree as ET,sys
R=Path('D:/CodexProjects/VideoKit').resolve();B=R/'docs/coder/d1render01';E=B/('evidence/apk-audit'+('-'+sys.argv[1] if len(sys.argv)>1 else ''));E.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(name,value):(E/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=json.loads((B/'evidence/build-inputs-final.json').read_text(encoding='utf-8'))
assert all(sha(B/x['path'])==x['sha256'] for x in inputs)
prior=json.loads((B/'evidence/reused-inputs.json').read_text(encoding='utf-8'))
assert all(sha(R/x['source'])==x['sha256'] for x in prior)
local=json.loads((B/'evidence/local-006/source-pins.json').read_text(encoding='utf-8'))
assert all(sha(B/x['path'])==x['sha256'] for x in local)
assert (B/'app/gradle.lockfile').read_bytes()==(R/'docs/coder/d1e13f/app/gradle.lockfile').read_bytes()
art=B/'artifacts';art.mkdir(exist_ok=True);apks=[]
for p in [B/'app/build/outputs/apk/debug/app-debug.apk',B/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk']:
    d=art/p.name
    if d.exists():assert d.read_bytes()==p.read_bytes()
    else:shutil.copyfile(p,d)
    apks.append(d)
audits=[]
for p in apks:
    z=zipfile.ZipFile(p);natives=[];raw=p.read_bytes()
    for info in z.infolist():
        if info.filename.startswith('lib/') and info.filename.endswith('.so'):
            b=z.read(info);source=B/'native-libs'/Path(info.filename).relative_to('lib')
            assert source.exists() and b==source.read_bytes()
            name_length,extra_length=struct.unpack_from('<HH',raw,info.header_offset+26)
            offset=info.header_offset+30+name_length+extra_length
            assert b[:6]==b'\x7fELF\x02\x01';phoff=struct.unpack_from('<Q',b,32)[0];ents,num=struct.unpack_from('<HH',b,54)
            loads=[]
            for i in range(num):
                kind,flags,off,va,pa,fs,ms,align=struct.unpack_from('<IIQQQQQQ',b,phoff+i*ents)
                if kind==1:loads.append({'alignment':align,'offset':off,'vaddr':va})
            alignment=info.compress_type==zipfile.ZIP_STORED and offset%16384==0 and all(x['alignment']>=16384 and x['offset']%16384==x['vaddr']%16384 for x in loads)
            assert alignment
            natives.append({'member':info.filename,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'zipDataOffset':offset,'static16KiBAligned':alignment,'loads':loads})
    dex=b''.join(z.read(x) for x in z.namelist() if x.endswith('.dex'))
    if p.name=='app-debug.apk':
        assert len(natives)==7
        for c in ['WorkSession','PlatformRenderer','PlatformAudio','PresentationActivity']:
            assert ('Lcom/videokit/d1present/'+c+';').encode() in dex
        assert b'Lcom/videokit/d1present/LocalSelfCheck;' not in dex
        assert hashlib.sha256(z.read('assets/d1/generated-pcm16.raw')).hexdigest()=='268d0e111f05ef5ad7ba405df6b78e5e8f6b3a43ebd926c48429d139a27da4ff'
        assert not any(x.lower().endswith(('.mp4','.avi','.mkv','.srt','.onnx','.p12','.jks','.keystore')) for x in z.namelist())
    else:
        for method in ['generatedMutedDualConsumers','existingMp4RawMutedDualConsumers','cancelRejectsLateGeneration','pausedSeekAndSurfaceRecreation']:assert method.encode() in dex
        assert not natives
    audits.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'natives':natives,'dexPresenceOnly':True,'runtimeTest':'NOT_RUN'})

# Inspect AGP's generated text manifest; no SDK, ADB or package-manager query.
ns={'a':'http://schemas.android.com/apk/res/android'};ak=lambda n:'{'+ns['a']+'}'+n
manifests=[]
for p in sorted((B/'app/build/intermediates').rglob('AndroidManifest.xml')):
    if not any(x in p.parts for x in ['merged_manifests','merged_manifest']):continue
    t=ET.parse(p).getroot();pkg=t.get('package');inst=t.find('instrumentation')
    dest=E/('test-merged.xml' if inst is not None else 'app-merged.xml')
    if dest.exists():continue
    shutil.copyfile(p,dest)
    if inst is not None:
        assert inst.get(ak('name'))=='com.videokit.d1present.RenderInstrumentation'
        assert inst.get(ak('targetPackage'))=='com.videokit.d1present'
        assert inst.get(ak('targetProcesses'))=='com.videokit.d1present:presentation'
    else:
        assert pkg=='com.videokit.d1present'
        acts=t.findall('application/activity');act=next(x for x in acts if x.get(ak('name')).endswith('PresentationActivity'))
        assert act.get(ak('exported'))=='false' and act.get(ak('process'))==':presentation'
        svc=next(x for x in t.findall('application/service') if x.get(ak('name')).endswith('CpuIsolatedService'))
        assert svc.get(ak('exported'))=='false' and svc.get(ak('isolatedProcess'))=='true'
        assert 'android.permission.INTERNET' not in [x.get(ak('name')) for x in t.findall('uses-permission')]
    manifests.append({'source':p.relative_to(B).as_posix(),'copy':dest.relative_to(B).as_posix(),'package':pkg,'instrumentation':inst.attrib if inst is not None else None})
assert len(manifests)==2

# Official, already verified Maven apksig library through JDK; no private signing key or SDK CLI.
jar=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';assert jar.exists()
repo=json.loads((B/'evidence/offline-repository-004.json').read_text(encoding='utf-8'))
pin=next(x for x in repo['files'] if x['path']==jar.relative_to(B).as_posix());assert sha(jar)==pin['sha256']
classes=E/'verifier-classes';classes.mkdir();J=Path('D:/Android/Android Studio/jbr/bin')
commands=[('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',str(jar),'-d',str(classes),str(B/'tools/VerifyApk.java')]),
          ('verify',[str(J/'java.exe'),'-cp',str(classes)+';'+str(jar),'VerifyApk',*map(str,apks)])]
receipts=[]
for name,argv in commands:
    r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(E/(name+'.stdout')).write_bytes(r.stdout);(E/(name+'.stderr')).write_bytes(r.stderr)
    receipts.append({'name':name,'argv':argv,'exit_code':r.returncode,'stdout_bytes':len(r.stdout),'stderr_bytes':len(r.stderr),'original_process_returned':True})
    print(r.stdout.decode('utf-8',errors='replace'));print(r.stderr.decode('utf-8',errors='replace'));assert r.returncode==0
out('signer-verification.json',{'apksig_jar':pin,'commands':receipts,'usesSDKCommand':False,'privateKeysRead':False})
out('artifact-audit.json',{'result':'PASS_STATIC_BUILD_ARTIFACT_ONLY','artifacts':audits,'manifests':manifests,'buildInputHash':sha(B/'evidence/build-inputs-final.json'),'buildInputsUnchanged':len(inputs),'legacySourcesUnchanged':len(prior),'localTestSourcesMatchFinal':len(local),'lockMatchesFrozenE13F':True,'deviceExecution':'NOT_RUN','static16KiBIsNotDevicePageTest':True})
print(json.dumps({'result':'PASS_STATIC_BUILD_ARTIFACT_ONLY','artifacts':[{k:v for k,v in x.items() if k!='natives'} for x in audits],'input_files_unchanged':len(inputs)},ensure_ascii=False,indent=2))
