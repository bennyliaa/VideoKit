"""Read-only frozen-material verification; never starts a process or parses media."""
from pathlib import Path
import argparse, datetime, hashlib, json, zipfile
B=Path(__file__).resolve().parents[1]
R=B.parents[2]
E=B/'evidence'
SEAL=E/'observation01-freeze.json'
MAIN=R/'docs/coder/D1_JCODEC_OBSERVATION01_DELIVERY_V1.0.md'
ARCHIVE=R/'docs/coder/D1-20261021-JCODEC-OBSERVATION01-source.zip'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def check_rows(rows):
    for x in rows:
        p=(R/x['path']).resolve()
        assert p.is_relative_to(R) and p.suffix.lower() not in {'.mp4','.mov','.mkv','.avi','.wav','.mp3','.srt'}
        assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'], str(p)
def verify_inputs():
    pins=read(E/'compile-source-pins.json')
    assert len(pins)==709
    for x in pins: assert sha(B/x['path'])==x['sha256']
    changed={x['path'] for x in read(E/'original-source-pins.json') if sha(B/x['path'])!=x['sha256']}
    assert changed=={'source/org/jcodec/containers/mp4/boxes/DataRefBox.java','source/org/jcodec/containers/mp4/boxes/SampleDescriptionBox.java','source/org/jcodec/codecs/h264/mp4/AvcCBox.java'}
    rows=read(E/'class-origin.json')
    assert len(rows)==980 and sum(not x['testOnly'] for x in rows)==977
    for x in rows:
        assert sha(B/x['compilerOutput'])==x['sha256']==sha(B/x['copy'])
        assert sha(B/x['sourcePath'])==x['sourceSha256'] and x['major']==55
    ja=read(E/'jar-audit.json'); jar=B/ja['path']
    assert sha(jar)==ja['sha256']=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
    assert sha(B/'patches/observation01.patch')=='f5f472b6bf6422832c66db4764a1a2d431be4c296c0f33d8bc3e853c2382f23c'
    with zipfile.ZipFile(jar) as z:
        assert z.testzip() is None
        assert {x.filename for x in z.infolist() if not x.is_dir()}==set(ja['jarFileNames'])
        for x in rows:
            if not x['testOnly']: assert hashlib.sha256(z.read(x['jarEntry'])).hexdigest()==x['sha256']
        manifest=z.read('META-INF/MANIFEST.MF').replace(b'\r\n ',b'')
        assert b'Implementation-Version: 0.2.5-videokit-observation01' in manifest and b'Main-Class:' not in manifest
    build=read(E/'build-result.json')
    assert build['compilerCalls']==build['jarCalls']==1 and build['status']=='BUILT_AUDIT_FORK_ONLY'
    owner=read(E/'metadata-001/owner.json')
    assert owner['processInvocations']==1 and owner['exitCode']==1 and owner['originalProcessReturned'] and owner['outputHandlesClosed'] and not owner['unknownSticky'] and owner['killInterruptRetry']==0
    stdout=(E/'metadata-001/stdout.raw').read_bytes(); stderr=(E/'metadata-001/stderr.raw').read_bytes()
    assert len(stdout)==425 and len(stderr)==393
    out=[json.loads(x) for x in stdout.decode().splitlines()]
    assert len(out)==3 and sum(x.get('result')=='PASS_NONMEDIA_METADATA' for x in out)==2
    assert b'Box$LeafBox.hasOriginalParseObservation()' in stderr
    failure=read(E/'metadata-failure-result.json')
    assert failure['completedParseDifferentialCases']==0 and failure['completedCases']==2 and failure['originalJvmExitCode']==1
    prior=read(E/'tool02-preservation.json'); p=R/prior['sealPath']
    assert sha(p)==prior['sha256']; old=read(p); assert len(old['files'])==2774; check_rows(old['files'])
    for x in read(E/'independent-baseline-preservation.json'):
        p=R/x['path']; assert sha(p)==x['sha256']; m=read(p)
        assert sha(R/m['report'])==x['reportSha256'] and len(m['evidenceFiles'])==x['evidenceFiles']
        check_rows(m['evidenceFiles'])
    report=read(E/'main-report-identity.json')
    assert sha(MAIN)==report['sha256'] and MAIN.stat().st_size==report['bytes']
    return {'productionClasses':977,'helperClasses':3,'modifiedProductionSources':3,'unmodifiedProductionSources':705,'buildCalls':1,'jarCalls':1,'metadataJvmCalls':1,'metadataExitCode':1,'freshGuardCasesCompleted':2,'parseDifferentialCasesCompleted':0,'mediaReadsOrGeneration':0,'processLaunchesByThisVerifier':0,'priorTool02FilesUnchanged':2774,'checkerEvidenceFilesUnchanged':31,'phaseAEvidenceFilesUnchanged':9,'validation':'BLOCKED_HELPER_FACTORY_CONTEXT_FAILURE'}
def verify_frozen():
    seal=read(SEAL); check_rows(seal['files'])
    expected={p.relative_to(R).as_posix() for p in B.rglob('*') if p.is_file() and p!=SEAL}|{MAIN.relative_to(R).as_posix()}
    assert expected=={x['path'] for x in seal['files']}
    assert sha(ARCHIVE)==seal['archive']['sha256'] and ARCHIVE.stat().st_size==seal['archive']['bytes']
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None and set(z.namelist())==expected
        for x in seal['files']: assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
    result=verify_inputs(); result.update({'sealSha256':sha(SEAL),'sealedFiles':len(seal['files']),'archiveSha256':sha(ARCHIVE),'status':'FROZEN_MATERIALS_MATCH_METADATA_VALIDATION_REMAINS_BLOCKED'})
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True); args=parser.parse_args()
    out=Path(args.output); root=R/'docs/tester/D1_JCODEC_OBSERVATION01_REVIEW_EVIDENCE'
    assert out.is_absolute() and out.resolve().parent==root.resolve() and not out.exists()
    result=verify_frozen()
    root.mkdir(parents=True,exist_ok=True); out.mkdir()
    result['verifiedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt=out/'material-verification.json'; receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'receipt':str(receipt),'sha256':sha(receipt),'result':result},ensure_ascii=False))
