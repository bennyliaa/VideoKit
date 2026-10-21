"""Independent local audit; never runs metadata readers, collectors, tests, builds, or ADB."""
from pathlib import Path
import hashlib,json,os,re,shlex,subprocess,sys,zipfile
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
B=R/'docs/coder/d1e13b';E=B/'evidence';C=[]
PIN='e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def ck(n,v,d=None):C.append(dict(name=n,passed=bool(v),detail=d))
def verify(row,label):
    p=R/row['path'];b=p.read_bytes();ck(label,len(b)==row['bytes'] and sha(b)==row['sha256'],row['path'])
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
s=E/'e13b-freeze.json';seal=load(s)
ck('external seal',sha(s.read_bytes())==PIN)
ck('118 immutable rows',len(seal['immutableFiles'])==118)
for row in seal['immutableFiles']:verify(row,'E13B immutable')
verify(seal['archive'],'ZIP pin')
ck('approved ZIP',seal['archive']['sha256']=='557327a5e7bd28cf73e21ccee3a9131e02a0495e1e303942500593e02f0bca96')
with zipfile.ZipFile(R/seal['archive']['path']) as z:
    rows={r['path']:r for r in seal['immutableFiles'] if r['path']!=seal['archive']['path']}
    ck('117 exact ZIP entries',len(z.namelist())==117 and len(set(z.namelist()))==117 and set(z.namelist())==set(rows))
    for n in z.namelist():ck('ZIP byte equality',len(z.read(n))==rows[n]['bytes'] and sha(z.read(n))==rows[n]['sha256'],n)
for prior in seal['priorSeals']:
    verify(prior['seal'],'old seal')
    for row in load(R/prior['seal']['path'])['immutableFiles']:verify(row,'old immutable')
reuse=load(B/'release/overlay-binding.json')
for k in ['baseCandidateBinding','baseDevicePlan','metadataManifest']:verify(reuse[k],'overlay binding')
ck('v17 source15 unchanged',reuse['version']==17 and reuse['acceptedSourceVersion']==15 and not reuse['productChanges'] and reuse['actualScope'] is None and reuse['actualOnce'] is None)
for row in reuse['baseArtifacts']:verify(row,'reused base artifact')
ck('4 exact base artifacts',len(reuse['baseArtifacts'])==4)
j=load(R/'docs/coder/d1e13a/evidence/host-jar-manifest.json')
with zipfile.ZipFile(R/j['jar']['path']) as z:
    ck('172 exact base production classes',len(z.namelist())==172 and set(z.namelist())=={c['entry'] for c in j['classes']})
    for c in j['classes']:ck('base JAR class bytes',len(z.read(c['entry']))==c['bytes'] and sha(z.read(c['entry']))==c['sha256'],c['entry'])
history=load(E/'metadata-shell-check-results.json')
ck('20 recorded semantics',len(history['cases'])==20)
ck('4 historical raw inputs',len(history['historicalVendorInputs'])==4)
for row in history['historicalVendorInputs']:
    verify(row['source'],'real historical source');verify(row['copy'],'historical copy');ck('historical copy exact',row['source']['sha256']==row['copy']['sha256'])
for c in history['cases']:
    for k in ['input','stdout','stderr']:verify(c[k],'recorded semantic '+k)
    raw=(R/c['stdout']['path']).read_text(encoding='utf-8');inp=(R/c['input']['path']).read_text(encoding='utf-8')
    want=c['expected'];ck('recorded expected state',c['exitCode']==(42 if want=='BLOCKED' else 0) and (raw.startswith('E13B_PROCESS_BLOCKED ') if want=='BLOCKED' else raw.startswith('E13B_PROCESS_SNAPSHOT_V1 state='+want+'\n')),c['case'])
    if want in ['IDLE','ACTIVE']:
        ck('complete success frame',raw.rstrip().endswith('E13B_PROCESS_SNAPSHOT_END') and 'command_exit=0' in raw and inp.rstrip().endswith('E13B_DUMPSYS_EXIT=0'),c['case'])
    if want=='ACTIVE':
        source_lines=inp.splitlines();a=source_lines.index('  Active instrumentation:');b=source_lines.index('  OOM levels:',a)
        expected='\n'.join(source_lines[a:b])+'\n'
        got=raw.split('ACTIVE_BLOCK_BEGIN\n',1)[1].split('ACTIVE_BLOCK_END\n',1)[0]
        ck('all active multi-line bytes preserved',got==expected,c['case'])
    ck('no new device execution',c['originalDeviceExecution'] is False,c['case']) if 'originalDeviceExecution' in c else None
record=load(E/'overlay-check-results.json')
ck('32 recorded syntax checks',len(record['syntax'])==32 and all(c['exitCode']==0 for c in record['syntax']))
ck('4 exact collector substitute branches',len(record['collectorCases'])==4)
for c in record['collectorCases']:
    ck('collector expected exit',c['exitCode']==c['expectedExit'],c['case'])
    for suffix,key in [('stdout','stdoutSha256'),('stderr','stderrSha256')]:ck('collector raw pin',sha((E/(c['case']+'-collector.'+suffix+'.txt')).read_bytes())==c[key],c['case']+' '+suffix)
    if c['case']!='idle':ck('no later metadata after wait/blocked',c['laterMetadataPrevented'],c['case'])
manifest=load(B/'release/metadata/three-client-manifest.json');base=load(R/'docs/coder/d1e13a/release/metadata/three-client-manifest.json')
reader=(B/'tools/processes_reader.sh').read_text();fragment=load(B/'release/state-collector-fragment.json')['definition'];pins=[]
for c,old,n,limit,units in zip(manifest['clients'],base['clients'],[70,18,71],[53512,27588,56360],[23993,9899,24460]):
    p=B/'release/metadata'/(c['id']+'.argv.json');ck('standalone argv equals manifest',load(p)==c,c['id']);verify(c['script'],'new script')
    script=(R/c['script']['path']).read_text();argv=c['argv']
    ck('3 direct exact argv bytes',len(argv)==7 and argv[:6]==['D:/Android/SDK/platform-tools/adb.exe','-s','HA1Q6WXR','shell','sh','-c'] and shlex.split(argv[-1])==[script],c['id'])
    ck('exact production collector embedded',script.count(reader)==1 and script.count(fragment)==1 and script.count('if dumpsys activity processes 2>&1;')==1,c['id'])
    ck('no old command or awk runtime', 'dumpsys activity instrumentation' not in script and 'awk ' not in script,c['id'])
    ck('record allocation unchanged',c['records']==old['records'] and len(c['records'])==n and sum(r['maxBytes']+2*len(r['label'])+16 for r in c['records'])+256==limit==c['recordOutputUpperBound'],c['id'])
    count=len(subprocess.list2cmdline(argv).encode('utf-16-le'))//2+1
    ck('Windows command-line bound',count==units==c['windowsCommandLineUtf16UnitsIncludingNul'] and count<=32767,c['id'])
    pins.append(dict(id=c['id'],script=c['script'],argv=pin(p),records=n,recordBound=limit,commandLineUtf16=count))
expect=load(B/'release/metadata/expected-baseline.json');oldexpect=load(R/'docs/coder/d1e13a/release/metadata/expected-baseline.json')
ck('all previous baseline fields unchanged',{k:v for k,v in expect.items() if k!='instrumentationEvidence'}==oldexpect)
ck('34 stat /18 controls',len(expect['fixedStat'])==34 and len(expect['fixedControlPins'])==18)
ck('2271B full accepted ledger',expect['ledger']['bytes']==2271 and expect['ledger']['sha256']=='e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649')
ck('48 process /2MiB budget',manifest['budgetPcTotal']==48 and manifest['budgetTextTotal']==2097152 and 1+32+6+6+3==48 and 1638400+458752==2097152)
def snapshot():
    paths={R/r['path'] for r in seal['immutableFiles']}|{s}
    for folder,dirs,files in os.walk(B):
        dirs[:]=[d for d in dirs if d not in {'.checks','__pycache__'}];paths.update(Path(folder)/f for f in files)
    return {str(p.relative_to(R)):sha(p.read_bytes()) for p in paths if p.is_file()}
before=snapshot();runs=[]
for name,args in [('default',[]),('verify',['verify','--seal-sha',PIN]),('help',['--help']),('pack-help',['pack','--help'])]:
    argv=[sys.executable,'-X','utf8','-B',str(B/'tools/package_overlay.py')]+args
    p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);(O/('readonly-'+name+'.txt')).write_bytes(p.stdout)
    ck('readonly verify/help exit0',p.returncode==0,name)
    if name in ['default','verify']:ck('readonly verifier PASS',json.loads(p.stdout)['status']=='PASS_E13B_STRICT_READONLY_VERIFY',name)
    runs.append(dict(name=name,argv=argv,exitCode=p.returncode,bytes=len(p.stdout),sha256=sha(p.stdout)))
ck('snapshot bytes unchanged',before==snapshot(),len(before))
result=dict(atUtc=datetime.now(timezone.utc).isoformat(),status='PASS_LOCAL_READONLY_AUDIT' if all(c['passed'] for c in C) else 'FAIL_LOCAL_READONLY_AUDIT',scope='NO_DEVICE_BUILD_TEST_REPLAY_OR_REMOTE_SCRIPT; VERIFIER_ONLY',checkCount=len(C),failed=[c for c in C if not c['passed']],checks=C,readonlyEntryRuns=runs,snapshotFilesUnchanged=len(before),metadataPins=pins)
(O/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','checkCount','failed','snapshotFilesUnchanged']},ensure_ascii=False))
