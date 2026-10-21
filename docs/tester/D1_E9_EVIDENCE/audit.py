"""Tester metadata-only audit. Does not execute candidate code or contact devices."""
import csv, hashlib, json, pathlib, struct, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).parent
BASE=ROOT/'docs/coder/d1e9/evidence'
def sha(data): return hashlib.sha256(data).hexdigest()
def read(name): return json.loads((BASE/name).read_text(encoding='utf-8-sig'))
def check_rows(rows):
    errors=[]
    for row in rows:
        p=pathlib.Path(row['path'])
        if not p.is_absolute(): p=ROOT/p
        if not p.is_file(): errors.append({'path':str(p),'error':'MISSING'}); continue
        data=p.read_bytes()
        if len(data)!=row['bytes'] or sha(data)!=row['sha256']: errors.append({'path':str(p),'error':'HASH_OR_SIZE'})
    return {'count':len(rows),'errors':errors}
freeze=read('e9-freeze.json'); manifest=read('source-manifest.json')
result={'scope':'TESTER_INDEPENDENT_METADATA_ONLY_NO_CANDIDATE_EXECUTION','freezeSha256':sha((BASE/'e9-freeze.json').read_bytes()),'freeze':check_rows(freeze['immutableFiles']),'manifest':check_rows(manifest['files'])}
archive=freeze['archive']; result['archive']=check_rows([archive])
with zipfile.ZipFile(ROOT/archive['path']) as z:
    entries={x.filename:x for x in z.infolist() if not x.is_dir()}
    result['zipEntries']=len(entries)
    errors=[]
    for row in manifest['files']:
        if row['path'] not in entries: errors.append({'path':row['path'],'error':'MISSING'}); continue
        data=z.read(row['path'])
        if len(data)!=row['bytes'] or sha(data)!=row['sha256']: errors.append({'path':row['path'],'error':'HASH_OR_SIZE'})
    result['zipErrors']=errors
    result['zipExtraEntries']=check_rows([dict(path=p,bytes=len(z.read(p)),sha256=sha(z.read(p))) for p in entries if p not in {r['path'] for r in manifest['files']}])
result['finalBuildInputs']=check_rows(read('final-build-inputs.json')['files'])
result['baselineSeals']={}
for rel in ['docs/coder/d1e7a/evidence/e7a-freeze.json','docs/coder/d1e8a/evidence/e8a-design-seal.json']:
    raw=(ROOT/rel).read_bytes(); old=json.loads(raw.decode('utf-8-sig'))
    result['baselineSeals'][rel]={'sha256':sha(raw),**check_rows(old['immutableFiles'])}
result['finalBuildInputSha256']=sha((BASE/'final-build-inputs.json').read_bytes())
public=read('public-android-entry-check.json'); result['publicInputs']=check_rows(public['inputs']); result['publicEntries']=public['actualPublicEntries']
inherit=read('native-and-strict-logic-inheritance.json')
result['inheritedInputs']=check_rows([r[k] for r in inherit['exactUnchanged'] for k in ('current','baseline')])
result['inheritanceMismatches']=[r for r in inherit['exactUnchanged'] if r['current']['sha256']!=r['baseline']['sha256']]
apks=read('apk-audit.json'); result['apks']=check_rows(apks['apks']); native=[]
for row in apks['nativeLibraries']:
    with zipfile.ZipFile(ROOT/row['apkPath']) as z: data=z.read(row['entry'])
    # The frozen upstream native entry is independently hash-checked in the package manifest.
    offset=struct.unpack_from('<Q',data,32)[0]; size,count=struct.unpack_from('<HH',data,54)
    loads=[struct.unpack_from('<Q',data,offset+i*size+48)[0] for i in range(count) if struct.unpack_from('<I',data,offset+i*size)[0]==1]
    native.append({'entry':row['entry'],'bytes':len(data),'sha256':sha(data),'matchesAudit':sha(data)==row['sha256'],'loadAlignments':loads,'all16K':all(n>=16384 and n%16384==0 for n in loads)})
result['native']=native
local=read('local-check-results.json'); result['localEvidence']={k:local[k] for k in ('status','groups','processInvocations','finalMappedInvocations','assertions')}
result['localResultRows']=len(local['results']); result['localExitCodes']=sorted(set(r['exitCode'] for r in local['results']))
with (BASE/'test-mapping.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
result['mapping']={'groups':len(rows),'assertionSum':sum(int(r['assertions']) for r in rows),'groupIds':[r['group'] for r in rows]}
result['buildAttempts']=[{k:r[k] for k in ('id','kind','exitCode','inputSnapshotSha256','log')} for r in read('build-results.json')['attempts']]
result['sbomDifference']=read('sbom-difference.json')
def coordinates(bom): return sorted((r.get('group',''),r['name'],r.get('version','')) for r in bom['components'])
baseline_bom=json.loads((ROOT/'docs/coder/d1e7a/evidence/sbom.json').read_text(encoding='utf-8-sig'))
result['sbomCoordinateComparison']={'current':len(coordinates(read('sbom.json'))),'baseline':len(coordinates(baseline_bom)),'equal':coordinates(read('sbom.json'))==coordinates(baseline_bom)}
result['nativeBaselineInputs']=check_rows([r[k] for r in result['sbomDifference']['native'] for k in ('current','baseline')])
result['snapshotInputs']={}
preserved={sha(p.read_bytes()):p for p in BASE.glob('*before*.java.txt')}
for rel in read('selfcheck-execution-command-index.json')['inputSnapshots']:
    snap=json.loads((BASE/rel).read_text(encoding='utf-8-sig'))
    result['snapshotInputs'][rel]=check_rows([dict(path=p,**r) for p,r in snap.items()])
    reconciled=[]; unresolved=[]
    for error in result['snapshotInputs'][rel]['errors']:
        key=next((p for p in snap if str(ROOT/p)==error['path'] or p==error['path']),None)
        original=snap.get(key,{})
        match=preserved.get(original.get('sha256'))
        if match and match.stat().st_size==original['bytes']:
            reconciled.append({'originalPath':key,'preservedPath':str(match.relative_to(ROOT)),'sha256':original['sha256']})
        else: unresolved.append(error)
    result['snapshotInputs'][rel]['historicalReconciliations']=reconciled
    result['snapshotInputs'][rel]['unresolvedErrors']=unresolved
result['hostCommands']=[{k:r[k] for k in ('name','exitCode','expected')} for r in read('host-surface-check.json')['commands']]
result['deviceCalls']=0; result['builds']=0; result['candidateSelfcheckReruns']=0
(OUT/'independent-metadata-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('sbomDifference','native')},ensure_ascii=False))
