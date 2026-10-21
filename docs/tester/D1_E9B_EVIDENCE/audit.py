"""Independent tester metadata-only audit: no candidate execution, build or device calls."""
import hashlib,json,pathlib,struct,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3];BASE=ROOT/'docs/coder/d1e9b';EV=BASE/'evidence';OUT=pathlib.Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def path(s):
    p=pathlib.Path(s)
    return p if p.is_absolute() else ROOT/p
def check(rows):
    errors=[]
    for v in rows:
        p=path(v['path'])
        if not p.is_file():errors.append({'path':v['path'],'error':'MISSING'});continue
        b=p.read_bytes()
        if len(b)!=v['bytes'] or sha(b)!=v['sha256']:errors.append({'path':v['path'],'error':'HASH_OR_SIZE'})
    return {'count':len(rows),'errors':errors}
seal=read(EV/'e9b-freeze.json');manifest=read(EV/'source-manifest.json')
r={'scope':'TESTER_METADATA_ONLY','sealSha256':sha((EV/'e9b-freeze.json').read_bytes()),'immutable':check(seal['immutableFiles']),'manifest':check(manifest['files']),'archive':check([seal['archive']])}
with zipfile.ZipFile(path(seal['archive']['path'])) as z:
    names=[n for n in z.namelist() if not n.endswith('/')]
    r['zip']={'files':len(names),'errors':[n for n in names if not path(n).is_file() or path(n).read_bytes()!=z.read(n)]}
r['baselines']={}
for name in ['d1e9a/evidence/e9a-freeze.json','d1e9/evidence/e9-freeze.json','d1e7a/evidence/e7a-freeze.json','d1e8a/evidence/e8a-design-seal.json']:
    p=ROOT/'docs/coder'/name;j=read(p);r['baselines'][name]={'sealSha256':sha(p.read_bytes()),**check(j['immutableFiles'])}
r['buildInputs']={'sha256':sha((EV/'final-build-inputs.json').read_bytes()),**check(read(EV/'final-build-inputs.json')['files'])}
apk=read(EV/'apk-audit.json');r['apks']=check(apk['apks']);r['native']=[]
for n in apk['nativeLibraries']:
    with zipfile.ZipFile(path(n['apkPath'])) as z:b=z.read(n['entry'])
    off=struct.unpack_from('<Q',b,32)[0];size,count=struct.unpack_from('<HH',b,54)
    aligns=[struct.unpack_from('<Q',b,off+i*size+48)[0] for i in range(count) if struct.unpack_from('<I',b,off+i*size)[0]==1]
    r['native'].append({'entry':n['entry'],'matches':sha(b)==n['sha256'],'loadAlignments':aligns,'all16KiB':bool(aligns) and all(a>=16384 and a%16384==0 for a in aligns)})
inherit=read(EV/'native-and-strict-logic-inheritance.json');r['inheritedInputs']=check([v[k] for v in inherit['exactUnchanged'] for k in ('current','baseline')])
android=read(EV/'android-entry-inheritance.json');r['androidEntryInputs']=check([v[k] for v in android['exactUnchanged'] for k in ('current','baseline')]+[android['priorEvidence']]);r['inheritedSections']=[]
for v in android['unchangedProductionSections']:
    now=(BASE/'tools'/v['file']).read_text(encoding='utf-8-sig');old=(ROOT/'docs/coder/d1e9a/tools'/v['file']).read_text(encoding='utf-8-sig')
    a=now.split(v['start'],1)[1].split(v['end'],1)[0];b=old.split(v['start'],1)[1].split(v['end'],1)[0]
    r['inheritedSections'].append({'file':v['file'],'equal':a==b,'hashMatches':sha(a.encode())==v['sha256']})
sbom=read(EV/'sbom-difference.json');r['sbom']={k:sbom[k] for k in ('coordinates','coordinateDelta','nativeLibraries','nativeDelta')}
def coords(p):return sorted((v.get('group',''),v['name'],v.get('version','')) for v in read(p)['components'])
r['sbomAllComponentsEqualE9A']=coords(EV/'sbom.json')==coords(ROOT/'docs/coder/d1e9a/evidence/sbom.json')
provenance=read(EV/'host-binary-provenance.json');r['hostJar']=check([provenance['artifact']]);errors=[];same=[]
prior=read(ROOT/'docs/coder/d1e9a/evidence/host-binary-provenance.json')['artifact']
with zipfile.ZipFile(path(provenance['artifact']['path'])) as z,zipfile.ZipFile(path(prior['path'])) as old:
    names=[n for n in z.namelist() if n.endswith('.class')]
    for c in provenance['productionClasses']:
        b=z.read(c['entry'])
        if len(b)!=c['bytes'] or sha(b)!=c['sha256'] or sha(path(c['source']).read_bytes())!=c['sourceSha256']:errors.append(c['entry'])
        for attempt in ['production-002','accept-failure-004']:
            p=BASE/'.selfcheck'/attempt/'classes'/c['entry']
            if not p.is_file() or p.read_bytes()!=b:errors.append(attempt+':'+c['entry'])
    for n in provenance['unchangedLifetimeAndSharedClassBytes']:
        if old.read(n)!=z.read(n):same.append(n)
    r['productionJar']={'classes':len(names),'provenanceRows':len(provenance['productionClasses']),'errors':errors,'unchangedE9A':len(provenance['unchangedLifetimeAndSharedClassBytes']),'unchangedE9AErrors':same,'testClasses':[n for n in names if any(x in n for x in ('ProductionCheck','SelfCheck','TestFiles','RuntimeGrantCheck'))]}
local=read(EV/'targeted-check-results.json');r['targeted']={k:local[k] for k in ('groups','assertions','sharedFixtureAssertions')};r['recordedResults']=[]
r['targetedLogHashes']=check([v[k] for v in local['results'] for k in ('stdout','stderr')]+[v['testControllerTeardown'] for v in local['results'] if 'testControllerTeardown' in v]+local['commands']+local['inputSnapshots'])
for v in local['results']:
    parent=path(v['stdout']['path']).parent;attempt=parent.name;p=BASE/'.selfcheck'/attempt/v['case'];result=read(p/'result.json');final=read(p/'final-supervisor.json')['fields'];log=path(v['stderr']['path']).read_text(encoding='utf-8-sig')
    mismatches=[k for k in ('assertions','sharedFixtureAssertions','productionExitAllowed','originalCloseAck') if v[k]!=result[k]]
    r['recordedResults'].append({'case':v['case'],'assertions':v['assertions'],'sharedFixtureAssertions':v['sharedFixtureAssertions'],'mismatches':mismatches,'productionExitAllowed':v['productionExitAllowed'],'originalCloseAck':v['originalCloseAck'],'closedAckLogged':'E9_PC_CLOSED' in log,'finalSupervisor':final,'fixtureTeardown':read(path(v['testControllerTeardown']['path'])) if 'testControllerTeardown' in v else None})
preserved={sha(p.read_bytes()):p for p in EV.glob('*before*') if p.is_file()};r['snapshots']={}
for attempt in ['production-002','accept-failure-004']:
    rows=read(EV/'selfcheck-attempts'/attempt/'inputs.json');v=check(rows);original={q['path']:q for q in rows};resolved=[];unresolved=[]
    for e in v['errors']:
        q=original[e['path']];p=preserved.get(q['sha256'])
        if p and p.stat().st_size==q['bytes']:resolved.append({'original':e['path'],'preserved':str(p.relative_to(ROOT))})
        else:unresolved.append(e)
    v['historicalReconciliations']=resolved;v['unresolvedErrors']=unresolved;r['snapshots'][attempt]=v
r['assertionSums']={'boundary':sum(v['assertions'] for v in local['results']),'shared':sum(v['sharedFixtureAssertions'] for v in local['results'])}
r['setupFailure003']=read(EV/'selfcheck-attempts/accept-failure-003/setup-failure.json')
r['buildAttempts']=[{k:v[k] for k in ('id','kind','exitCode','inputSnapshotSha256')} for v in read(EV/'build-results.json')['attempts']]
r['testerDeviceCalls']=0;r['testerBuilds']=0;r['testerCandidateRuns']=0
(OUT/'independent-metadata-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k not in ('recordedResults','native')},ensure_ascii=False))
