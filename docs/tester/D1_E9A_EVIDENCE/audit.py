"""Independent metadata inspection only; no candidate execution, build or device access."""
import base64,csv,hashlib,json,pathlib,re,struct,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/coder/d1e9a'; EV=BASE/'evidence'; OUT=pathlib.Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def path(p):
    p=pathlib.Path(p)
    return p if p.is_absolute() else ROOT/p
def check(rows):
    errors=[]
    for r in rows:
        p=path(r['path'])
        if not p.is_file():errors.append({'path':r['path'],'error':'MISSING'});continue
        b=p.read_bytes()
        if len(b)!=r['bytes'] or sha(b)!=r['sha256']:errors.append({'path':r['path'],'error':'HASH_OR_SIZE'})
    return {'count':len(rows),'errors':errors}
seal=read(EV/'e9a-freeze.json'); manifest=read(EV/'source-manifest.json')
r={'scope':'TESTER_METADATA_ONLY','sealSha256':sha((EV/'e9a-freeze.json').read_bytes()),'immutable':check(seal['immutableFiles']),'manifest':check(manifest['files']),'archive':check([seal['archive']])}
with zipfile.ZipFile(path(seal['archive']['path'])) as z:
    errors=[]; names=[n for n in z.namelist() if not n.endswith('/')]
    for n in names:
        p=path(n)
        if not p.is_file() or p.read_bytes()!=z.read(n):errors.append(n)
    r['zip']={'files':len(names),'errors':errors}
r['baselines']={}
for name in ['d1e9/evidence/e9-freeze.json','d1e7a/evidence/e7a-freeze.json','d1e8a/evidence/e8a-design-seal.json']:
    p=ROOT/'docs/coder'/name;j=read(p)
    r['baselines'][name]={'sealSha256':sha(p.read_bytes()),**check(j['immutableFiles'])}
inputs=read(EV/'final-build-inputs.json');r['buildInputs']={'sha256':sha((EV/'final-build-inputs.json').read_bytes()),**check(inputs['files'])}
public=read(EV/'public-android-entry-check.json');r['publicInputs']=check(public['inputs']);r['publicEntries']=public['publicEntries'];r['runtimeGrantSequence']=public['runtimeGrantInvalidationSequence']
apk=read(EV/'apk-audit.json');r['apks']=check(apk['apks']);r['native']=[]
for n in apk['nativeLibraries']:
    with zipfile.ZipFile(path(n['apkPath'])) as z:b=z.read(n['entry'])
    off=struct.unpack_from('<Q',b,32)[0];sz,count=struct.unpack_from('<HH',b,54)
    alignment=[struct.unpack_from('<Q',b,off+i*sz+48)[0] for i in range(count) if struct.unpack_from('<I',b,off+i*sz)[0]==1]
    r['native'].append({'entry':n['entry'],'matches':sha(b)==n['sha256'],'alignment':alignment,'all16KiB':bool(alignment) and all(a>=16384 and a%16384==0 for a in alignment)})
inherit=read(EV/'native-and-strict-logic-inheritance.json');r['inherited']=check([v[k] for v in inherit['exactUnchanged'] for k in ('current','baseline')])
sbom=read(EV/'sbom-difference.json');r['sbom']={k:sbom[k] for k in ('coordinates','coordinateDelta','nativeLibraries','nativeDelta')}
def coords(p):return sorted((v.get('group',''),v['name'],v.get('version','')) for v in read(p)['components'])
r['sbomAllComponentsEqualE9']=coords(EV/'sbom.json')==coords(ROOT/'docs/coder/d1e9/evidence/sbom.json')
provenance=read(EV/'host-binary-provenance.json');r['hostJar']=check([provenance['artifact']]);err=[];old_err=[]
with zipfile.ZipFile(path(provenance['artifact']['path'])) as z:
    names=[n for n in z.namelist() if n.endswith('.class')]
    for c in provenance['productionClasses']:
        b=z.read(c['entry']);p=path(c['source'])
        if sha(b)!=c['sha256'] or len(b)!=c['bytes'] or sha(p.read_bytes())!=c['sourceSha256']:err.append(c['entry'])
        compiled=BASE/'.selfcheck/frame-validation-008/classes'/c['entry']
        if not compiled.is_file() or compiled.read_bytes()!=b:err.append('008:'+c['entry'])
    for n in provenance['unchangedLifetimeAndSharedClassBytes']:
        if z.read(n)!=(BASE/'.selfcheck/final-pc-007/classes'/n).read_bytes():old_err.append(n)
    r['productionJar']={'classes':len(names),'provenanceRows':len(provenance['productionClasses']),'errors':err,'unchanged007':len(provenance['unchangedLifetimeAndSharedClassBytes']),'unchanged007Errors':old_err,'testClassNames':[n for n in names if any(s in n for s in ('ProductionCheck','SelfCheck','TestFiles','RuntimeGrantCheck'))]}
preserved={sha(p.read_bytes()):p for p in EV.glob('*before*') if p.is_file()};r['targetedSnapshots']={}
for attempt in ['final-pc-007','frame-validation-008']:
    rows=read(EV/'selfcheck-attempts'/attempt/'inputs.json');snap={v['path']:v for v in rows};v=check(rows); resolved=[];unresolved=[]
    for e in v['errors']:
        row=snap[e['path']];p=preserved.get(row['sha256'])
        if p and p.stat().st_size==row['bytes']:resolved.append({'original':e['path'],'preserved':str(p.relative_to(ROOT))})
        else:unresolved.append(e)
    v['historicalReconciliations']=resolved;v['unresolvedErrors']=unresolved;r['targetedSnapshots'][attempt]=v
local=read(EV/'targeted-check-results.json');r['targeted']={k:local[k] for k in ('groups','finalMappedInvocations','finalValidationInvocations','assertions','boundaryAssertions','sharedFixtureAssertions')}
r['targetedLogHashes']=check([v[k] for v in local['results'] for k in ('stdout','stderr')])
r['stdoutAssertionMismatches']=[]
for v in local['results']:
    text=path(v['stdout']['path']).read_text(encoding='utf-8-sig')
    m=re.search(r'PASS production_e9a=(\S+) assertions=(\d+) boundaryAssertions=(\d+) sharedFixtureAssertions=(\d+) realPCProcess=(\w+) deviceCalls=0',text)
    if not m or m.group(1)!=v['case'] or tuple(map(int,m.group(2,3,4)))!=(v['assertions'],v['boundaryAssertions'],v['sharedFixtureAssertions']):r['stdoutAssertionMismatches'].append(v['case'])
with (EV/'test-mapping.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
r['mapping']={'groups':len(rows),'assertions':sum(int(v['assertions']) for v in rows),'realPCGroups':sum(v['actualPCProcess']=='True' for v in rows)}
r['attemptExitCodes']={}
for attempt in ['final-pc-007','frame-validation-008']:
    j=read(EV/'selfcheck-attempts'/attempt/'results.json');r['attemptExitCodes'][attempt]=j['results']
r['processBoundaries']={}
platform=EV/'selfcheck-attempts/final-pc-007/platform'
for group in ['EARLY_EOF','READER_ERROR','OUTPUT_BOUND','CONSOLE_EOF','CONSOLE_TRUNCATED','CONSOLE_OVERFLOW','CONTROL5','CLOSE_LATCH','CLOSE_UNKNOWN']:
    p=platform/group/group;j=read(p/'main-returned.json')['fields'];encoded=j['operationState'];op=json.loads(base64.urlsafe_b64decode(encoded+'='*((-len(encoded))%4)))['fields'];log=(p/'stderr.txt').read_text(encoding='utf-8-sig')
    v={'elapsedNanos':j['elapsedNanos'],'operationState':op,'isolationAckLogged':'E9_PC_ISOLATION_ACCEPTED' in log,'closedAckLogged':'E9_PC_CLOSED' in log}
    if group=='CLOSE_UNKNOWN':v['unknownHold']=read(p/'unknown-hold-before-fixture-teardown.json')['fields'];v['fixtureTeardown']=read(p/'fixture-teardown.json')['fields']
    r['processBoundaries'][group]=v
r['buildAttempts']=[{k:v[k] for k in ('id','kind','exitCode','inputSnapshotSha256')} for v in read(EV/'build-results.json')['attempts']]
r['newStaticFinding']={'id':'E9A-F01','priority':'P2','scope':'PC_LOCAL_CONNECTION_BOUND','source':'docs/coder/d1e9a/tools/E9PcSupervisor.java','witness':['accept happens before ++accepted>128','Known excess client closes successfully','supervise catches the bound exception without marking transport uncertain','loop calls acceptAndServe again'],'runtimeReproduction':'NOT_RUN','limitedReadOnlyBatchImpact':'NON_BLOCKING_ONLY_WITH_EXPLICIT_QUERY_LIMIT_BELOW_128'}
r['residualStaticFinding']={'id':'E9A-F02','originalFinding':'E9-F02','priority':'P1','scope':'REGISTRY_ORIGINAL_RESOURCE_CUSTODY','witness':['Store.checkTotal walk holder is local and never added to outstanding','walk close UNKNOWN can leave Store.returned true','HostManager authority predicate can then allow pcClosed','Activation openKnownHead and recordActivationRelease precede creation of Processes/supervisor'],'runtimeReproduction':'NOT_RUN','deviceBatchImpact':'BLOCKING'}
r['reviewVerdict']='NEEDS_FIX_NOT_SUPPORTED_FOR_DEVICE_BATCH'
r['testerDeviceCalls']=0;r['testerBuilds']=0;r['testerCandidateRuns']=0
(OUT/'independent-metadata-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k not in ('processBoundaries','native','attemptExitCodes')},ensure_ascii=False))
