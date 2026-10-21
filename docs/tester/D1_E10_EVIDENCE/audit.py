"""Independent local metadata/static audit. Never imports or runs candidate tools."""
import ast,hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3];B=ROOT/'docs/coder/d1e10';OUT=pathlib.Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def check(rows,root=ROOT):
    errors=[]
    for v in rows:
        p=root/v['path']
        if not p.is_file():errors.append({'path':v['path'],'error':'MISSING'});continue
        b=p.read_bytes()
        if len(b)!=v['bytes'] or sha(b)!=v['sha256']:errors.append({'path':v['path'],'error':'HASH_OR_SIZE'})
    return {'count':len(rows),'errors':errors}
seal=read(B/'evidence/e10-freeze.json');manifest=read(B/'evidence/source-manifest.json')
r={'scope':'STATIC_PACKAGE_REVIEW_ONLY','sealSha256':sha((B/'evidence/e10-freeze.json').read_bytes()),'immutable':check(seal['immutableFiles']),'manifest':check(manifest['files']),'archive':check([seal['archive']])}
with zipfile.ZipFile(ROOT/seal['archive']['path']) as z:
    names=[n for n in z.namelist() if not n.endswith('/')];r['zip']={'files':len(names),'errors':[n for n in names if not (ROOT/n).is_file() or (ROOT/n).read_bytes()!=z.read(n)]}
external=read(B/'plan/external-input-pins.json');r['externalInputs']=check(external['files']);r['e9bSealPin']=check([external['e9bSeal']]);r['e9bImmutable']=check(read(ROOT/external['e9bSeal']['path'])['immutableFiles'])
r['readonlyManifestPin']=check([external['readonlyDeviceManifest']]);r['historicalDeviceEvidence']=check(read(ROOT/external['readonlyDeviceManifest']['path'])['files'],ROOT/external['readonlyEvidenceRoot'])
scope=read(B/'templates/scope.template.json');plan=read(B/'plan/execution-plan.json');r['scopeDraftNoIssuance']=scope['status']=='DRAFT_NOT_EFFECTIVE' and all(scope[k] is None for k in ('registry','migration','attempt','handle','issuedAt','executionDispatchEvidence','acceptedE10ReviewSha256')) and plan['newIdentity'] is None and plan['currentDeviceFacts'] is None
desc=(B/'plan/descriptor.json').read_bytes();commit=(B/'plan/expected-commit.json').read_bytes();r['descriptor']={'bytes':len(desc),'sha256':sha(desc),'matchesActualProductionDescriptor':desc==(ROOT/'docs/tester/D1_E9B_READ_ONLY_IDENTITY_EVIDENCE/external-registry/descriptor.json').read_bytes()}
d=json.loads(commit)['fields'];expected={'kind':'commit','descriptor':sha(desc),'payload':sha(desc),'policy':json.loads(desc)['fields']['policy']};r['expectedCommit']={'bytes':len(commit),'sha256':sha(commit),'matchesProductionSchema':d==expected}
r['costs']={'files':plan['deviceFileCount'],'contentCeiling':sum([plan['deviceFiles'][0]['maxBytes'],len(desc),len(commit)]),'allocatedFileCeiling':sum(v['maxBytes'] for v in plan['deviceFiles']),'newDirectories':plan['deviceMaxNewDirectories'],'baselineConsumed':sum(v['bytes'] for v in plan['legacy']['settledRecords'])}
r['artifacts']=check(plan['artifacts']);r['sourcePins']=check(read(B/'evidence/static-blockers.json')['findings'][0]['sourcePins'])
prefix=(B/'reference/accepted-ledger-prefix.bin').read_bytes();lines=prefix.decode('ascii').splitlines(keepends=True);chain=sha(lines[0].encode());chain_errors=[];reserves={};settled=[]
for n,line in enumerate(lines[1:],2):
    payload,stored=line.rstrip('\n').rsplit(' ',1);chain=sha((chain+' '+payload).encode())
    if chain!=stored:chain_errors.append(n)
    words=payload.split(' ')
    if words[0]=='R':reserves[words[1]]=None
    else:reserves[words[1]]=int(words[3]);settled.append({'task':words[1],'state':words[2],'bytes':int(words[3]),'sha256':words[4],'output':'files/e4a_outputs/'+words[1]+'.mp4'})
r['acceptedPrefix']={'bytes':len(prefix),'sha256':sha(prefix),'matchesPlan':sha(prefix)==plan['legacy']['acceptedLedgerPrefixSha256'],'chainErrors':chain_errors,'reserves':len(reserves),'settlements':len(settled),'reserved':sum(2097152 for v in reserves.values() if v is None),'consumed':sum(v for v in reserves.values() if v is not None),'settledRecordsMatch':settled==plan['legacy']['settledRecords']}
r['templateCommands']=[{'file':p.name,'operation':read(p)['wireFields']['operation'],'templateOnly':read(p)['templateOnly'],'notForProductionCli':read(p)['notForProductionCli']} for p in sorted((B/'templates').glob('[0-9][0-9]-*.template.json'))]
source=(B/'tools/validate_package.py').read_text(encoding='utf-8-sig');tree=ast.parse(source);imports=[v.name for n in ast.walk(tree) if isinstance(n,ast.Import) for v in n.names]
forbidden={'write_bytes','write_text','mkdir','unlink','rename','uuid4','uuid1','system','spawn','connect','Popen','run'}
calls=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
r['validatorStatic']={'imports':imports,'forbiddenImports':sorted(set(imports)&{'subprocess','socket','requests','urllib','shutil','os'}),'forbiddenCalls':sorted(set(calls)&forbidden),'boundPositiveDeviceExecution':'NOT_RUN','candidateRerun':False}
validation=read(B/'evidence/validation-results.json');r['recordedValidation']={'status':validation['status'],'results':validation['results'],'commands':validation['commands']}
inputs=read(B/'evidence/local-validation/inputs.json');r['validationInputs']=check(inputs['files'])
r['validationOriginalLogs']=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted((B/'evidence/local-validation').glob('*.txt'))]
r['findings']=[{'id':'E10-PREEXEC-BOUND-CLEANUP','priority':'P1','confirmed':'STATIC_SOURCE','runtime':'NOT_RUN','witness':['RESERVE creates identify.json and reserve.json plus BOUND','Current identity return remains IDENTITY until actual executeDone','captureIdentityForFinish rejects existing reserve','It also CREATE_NEW identify.json, so merely removing reserve check is insufficient','ACK requires exactly archived current original return']},{'id':'E10-POSTARCHIVE-STOP','priority':'P2','confirmed':'STATIC_SOURCE','runtime':'NOT_RUN','witness':['Existing immutable returned.json holds R0','Allowed STOP_DEPENDENCIES calls pend, clears proof, advances stateSeq and creates R1','Host adopts R1 but ACK compares it with archived R0 and fails','Re-archival CREATE_NEW cannot replace returned.json','Specify phase-aware cleanup and reject inadmissible STOP before intent/wire or retain correct original terminal receipt semantics']}]
r['reviewVerdict']='BLOCKED_FOR_EXECUTION_MINIMAL_CONSOLIDATED_FIX_REQUIRED';r['deviceCalls']=0;r['builds']=0;r['candidateToolRuns']=0;r['actualIdsGenerated']=0;r['scopeIssued']=False;r['migrationWrites']=0;r['activation']='NOT_CREATED';r['D1']='NOT_PASSED';r['M0']='NOT_STARTED'
(OUT/'independent-package-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k not in ('recordedValidation','validationOriginalLogs','findings')},ensure_ascii=False))
