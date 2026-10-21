"""Independent static/metadata audit. No candidate imports, tests, build, device or UUID generation."""
import ast,hashlib,json,pathlib,struct,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3];B=ROOT/'docs/coder/d1e10a';EV=B/'evidence';OUT=pathlib.Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def path(s):
    p=pathlib.Path(s)
    return p if p.is_absolute() else ROOT/p
def check(rows,root=ROOT):
    errors=[]
    for v in rows:
        p=pathlib.Path(v['path']);p=p if p.is_absolute() else root/p
        if not p.is_file():errors.append({'path':v['path'],'error':'MISSING'});continue
        b=p.read_bytes()
        if len(b)!=v['bytes'] or sha(b)!=v['sha256']:errors.append({'path':v['path'],'error':'HASH_OR_SIZE'})
    return {'count':len(rows),'errors':errors}
seal=read(EV/'e10a-freeze.json');manifest=read(EV/'source-manifest.json')
r={'scope':'E10A_STATIC_IMPLEMENTATION_AND_EXECUTION_PACKAGE_REVIEW','sealSha256':sha((EV/'e10a-freeze.json').read_bytes()),'immutable':check(seal['immutableFiles']),'manifest':check(manifest['files']),'archive':check([seal['archive']])}
with zipfile.ZipFile(path(seal['archive']['path'])) as z:
    names=[n for n in z.namelist() if not n.endswith('/')];r['zip']={'files':len(names),'errors':[n for n in names if not path(n).is_file() or path(n).read_bytes()!=z.read(n)]}
external=read(B/'plan/external-input-pins.json');r['externalInputs']=check(external['files']);r['oldSeals']={}
for pin in external['oldSeals']:
    r['oldSeals'][pin['path']]={'seal':check([pin]),'immutable':check(read(path(pin['path']))['immutableFiles'])}
r['readonlyManifest']=check([external['readonlyDeviceManifest']]);r['historicalReadonlyEvidence']=check(read(path(external['readonlyDeviceManifest']['path']))['files'],path(external['readonlyEvidenceRoot']))
r['buildInputs']={'sha256':sha((EV/'final-build-inputs.json').read_bytes()),**check(read(EV/'final-build-inputs.json')['files'])}
apk=read(EV/'apk-audit.json');r['apks']=check(apk['apks']);r['native']=[]
for v in apk['nativeLibraries']:
    with zipfile.ZipFile(path(v['apkPath'])) as z:b=z.read(v['entry'])
    off=struct.unpack_from('<Q',b,32)[0];size,count=struct.unpack_from('<HH',b,54)
    aligns=[struct.unpack_from('<Q',b,off+i*size+48)[0] for i in range(count) if struct.unpack_from('<I',b,off+i*size)[0]==1]
    r['native'].append({'entry':v['entry'],'matches':sha(b)==v['sha256'],'all16KiB':bool(aligns) and all(a>=16384 and a%16384==0 for a in aligns)})
r['strictInheritance']=check([v[k] for v in read(EV/'native-and-strict-logic-inheritance.json')['exactUnchanged'] for k in ('current','baseline')])
android=read(EV/'android-entry-inheritance.json');r['androidInheritance']=check([v[k] for v in android['exactUnchanged'] for k in ('current','baseline')]+[android['oldPublicEntryEvidence']])
sbom=read(EV/'sbom-difference.json');r['sbom']={k:sbom[k] for k in ('coordinates','coordinateDelta','nativeLibraries','nativeDelta')}
prov=read(EV/'host-binary-provenance.json');r['hostJar']=check([prov['artifact']]);errors=[];old_errors=[]
old=read(ROOT/'docs/coder/d1e9b/evidence/host-binary-provenance.json')['artifact']
with zipfile.ZipFile(path(prov['artifact']['path'])) as z,zipfile.ZipFile(path(old['path'])) as prior:
    names=[n for n in z.namelist() if n.endswith('.class')]
    for c in prov['productionClasses']:
        b=z.read(c['entry'])
        if len(b)!=c['bytes'] or sha(b)!=c['sha256'] or sha(path(c['source']).read_bytes())!=c['sourceSha256']:errors.append(c['entry'])
        for attempt in ('targeted-002','console-003'):
            p=B/'.selfcheck'/attempt/'classes'/c['entry']
            if not p.is_file() or p.read_bytes()!=b:errors.append(attempt+':'+c['entry'])
    for n in prov['unchangedLifetimeAndSharedClassBytes']:
        if prior.read(n)!=z.read(n):old_errors.append(n)
    r['productionJar']={'classes':len(names),'errors':errors,'sameE9B':len(prov['unchangedLifetimeAndSharedClassBytes']),'sameE9BErrors':old_errors,'testClasses':[n for n in names if any(s in n for s in ('ProductionCheck','SelfCheck','TestFiles'))]}
local=read(EV/'targeted-check-results.json');r['targeted']={k:local[k] for k in ('groups','assertions','sharedFixtureAssertions')};r['results']=[]
rows=[v[k] for v in local['results'] for k in ('stdout','stderr')]+[v['fixtureTeardown'] for v in local['results'] if 'fixtureTeardown' in v]
r['logPins']=check(rows)
r['targetedInputPins']=check(local['inputs']);r['tracePins']=check(local['trace'])
for v in local['results']:
    parent=path(v['stdout']['path']).parent;attempt=parent.name;p=EV/'selfcheck-attempts'/attempt/'platform'/v['case'];actual=read(p/'result.json');final=read(p/'final-supervisor.json')['fields'];log=path(v['stderr']['path']).read_text(encoding='utf-8-sig')
    r['results'].append({'case':v['case'],'assertions':v['assertions'],'sharedFixtureAssertions':v['sharedFixtureAssertions'],'matchesResult':all(actual[k]==v[k] for k in ('assertions','sharedFixtureAssertions','productionExitAllowed','originalCloseAck')),'originalCloseAck':v['originalCloseAck'],'productionExitAllowed':v['productionExitAllowed'],'closedLogged':'E9_PC_CLOSED' in log,'finalSupervisor':final,'fixtureTeardown':read(path(v['fixtureTeardown']['path'])) if 'fixtureTeardown' in v else None})
preserved={sha(p.read_bytes()):p for p in EV.glob('*before*') if p.is_file()};r['snapshots']={}
for attempt in ('targeted-001','targeted-002','console-003'):
    p=EV/'selfcheck-attempts'/attempt/'inputs.json';rows=read(p);v=check(rows);by={q['path']:q for q in rows};resolved=[];unresolved=[]
    for e in v['errors']:
        q=by[e['path']];old=preserved.get(q['sha256'])
        if old and old.stat().st_size==q['bytes']:resolved.append({'original':e['path'],'preserved':str(old.relative_to(ROOT))})
        else:unresolved.append(e)
    v['historicalReconciliations']=resolved;v['unresolvedErrors']=unresolved;r['snapshots'][attempt]=v
r['assertionSums']={'boundary':sum(v['assertions'] for v in local['results']),'shared':sum(v['sharedFixtureAssertions'] for v in local['results'])}
plan=read(B/'plan/execution-plan.json');scope=read(B/'templates/scope.template.json');config=read(B/'templates/manager-config.template.json')['wireFields'];prepare=read(B/'templates/prepare-plan.template.json')['wireFields']
r['draftNotIssued']=scope['status']=='DRAFT_NOT_EFFECTIVE' and all(scope[k] is None for k in ('registry','migration','attempt','handle','issuedAt','executionDispatchEvidence','acceptedE10AReviewSha256')) and plan['newIdentity'] is None and plan['currentDeviceFacts'] is None
r['deployment']={'sourceVersion':plan['deployment']['sourceVersion'],'targetVersion':plan['deployment']['candidateVersion'],'sourcePairMatchesConfig':[v['sha256'] for v in plan['deployment']['sourcePair']]==[config['originalApp'],config['originalTest']],'targetPairMatchesPlan':[v['sha256'] for v in plan['artifacts'][:2]]==[prepare['app'],prepare['test']],'originalVersion':config['originalVersion'],'planVersion':prepare['version']}
desc=(B/'plan/descriptor.json').read_bytes();commit=(B/'plan/expected-commit.json').read_bytes();r['deviceWriteCost']={'files':plan['deviceFileCount'],'descriptorBytes':len(desc),'descriptorSha256':sha(desc),'commitBytes':len(commit),'commitSha256':sha(commit),'contentCeiling':2048+len(desc)+len(commit),'allocatedCeiling':sum(v['maxBytes'] for v in plan['deviceFiles']),'newDirectories':plan['deviceMaxNewDirectories']}
r['commandTemplates']=[{'file':p.name,'fields':read(p)['wireFields']} for p in sorted((B/'templates').glob('[0-9][0-9]-*.template.json'))]
tree=ast.parse((B/'tools/validate_package.py').read_text(encoding='utf-8-sig'));imports=[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names];calls=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
r['validatorStatic']={'forbiddenImports':sorted(set(imports)&{'subprocess','socket','requests','urllib','shutil','os'}),'forbiddenCalls':sorted(set(calls)&{'write_bytes','write_text','mkdir','unlink','rename','uuid4','uuid1','system','spawn','connect','Popen'})};r['recordedPackageValidation']=read(EV/'execution-package-validation.json')['results']
r['buildAttempts']=[{k:v[k] for k in ('id','kind','exitCode','inputSnapshotSha256')} for v in read(EV/'build-results.json')['attempts']]
r['closedStaticLocal']=['E10-PREEXEC-BOUND-CLEANUP','E10-POSTARCHIVE-STOP'];r['nonblockingNote']='Activation DAG step 2 still says E9B fixed APK SHA; machine plan/templates/runbook correctly use E10A version14 target. Execute only the exact version14 pins, correct wording in next documentation revision.'
r['custodialEvidenceBoundary']={'executed':'Real shared prepareControl plus real console failure boundary and Processes.controlResponse(cleanupOnly=true), Registry/Run/Remote/entry closure','notExecuted':['Approved DEVICE CLI','actual manager.operation failed flag and manager.custodialCleanup through live CLEANUP IPC'],'status':'Source integration inspected; do not widen finite runtime claim'}
r['verdict']='SUPPORTED_FOR_EXACT_ACTOR1_EXECUTION_PREPARATION_NOT_EXECUTION_AUTHORITY';r['testerDeviceCalls']=0;r['testerBuilds']=0;r['testerCandidateRuns']=0;r['actualUUIDsGenerated']=0;r['scopeIssued']=False;r['migrationWrites']=0;r['catalog']='NOT_CREATED';r['activation']='NOT_CREATED'
(OUT/'independent-review-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k not in ('results','native','commandTemplates','recordedPackageValidation')},ensure_ascii=False))
