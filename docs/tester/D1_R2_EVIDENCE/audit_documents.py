"""Offline document identity/link/source audit only. Does not open test media."""
from pathlib import Path
import hashlib, json, re, zipfile
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
def save(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
inputs = sorted((ROOT/'docs/coder').glob('D1_R2_*.md'))
assert len(inputs) == 5
expected = {
 'D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md':'b0bae695abdb189251ca81c40a45f2a6a27dacb2a9d740fbbe5d153f3a0dea17',
 'D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md':'b64ba9c1ce43cff8c353e17dff2370c7de407342c63a0130652f1ddca5d67a52',
 'D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md':'c070320396513c5d23d31535df62297f2961b6a4a0648716fc72c93439e75bf1',
 'D1_R2_NATIVE_FAILURE_GATE_PLAN_V1.0.md':'e3adbcda852d421df0beda8c228e74de38f3e00421982da04089bbf476df07ec',
 'D1_R2_DELIVERY_V1.0.md':'c1ce4ae44be23219c41e1089db94aa6a67f3e68512c7a5f26f617dfddab74454'}
identities=[]; links=[]; anchors={}
for p in inputs:
    data=p.read_bytes(); text=data.decode('utf-8-sig')
    (OUT/p.name).write_bytes(data)
    identities.append(dict(path=p.relative_to(ROOT).as_posix(), bytes=len(data), sha256=sha(data), expected=expected[p.name], matches=sha(data)==expected[p.name]))
    anchors[p.name]=[{'line':i,'text':s} for i,s in enumerate(text.splitlines(),1) if re.search(r'close失败|S07|O06|commandId|GRANT|180|10秒|分支|最多12|P01|P09|Q03|Q05|Q07|Q08|Q09|guard|fileKey|BLOCKED_HOST|NOT_RUN_UNCHANGED|batch-status-',s)]
    for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',text):
        target=m.group(1); line=None
        lm=re.search(r':(\d+)$',target)
        if lm: line=int(lm.group(1)); target=target[:lm.start()]
        t=Path(target); exists=t.is_file()
        valid=exists and (line is None or 1<=line<=len(t.read_text(encoding='utf-8-sig').splitlines()))
        links.append(dict(source=p.name, sourceLine=text[:m.start()].count('\n')+1, target=target, line=line, exists=exists, lineValid=valid))
fixed=ROOT/'docs/tester/D1_C14_EVIDENCE/batch-status-20261016T123818.json'
fixed_data=fixed.read_bytes()
save('input-and-link-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Offline documents; no device, media window, harness, build or functional tests',inputs=identities,links=links,linkOccurrences=len(links),uniqueTargets=len({r['target'] for r in links}),allLinksValid=all(r['lineValid'] for r in links),fixedSnapshot=dict(sha256=sha(fixed_data),expected='1f8fa4c6ca11c271d19fab16da06a3e490723c50251837219f6b0e3d49ca3d7a',content=json.loads(fixed_data))))
save('reference-anchors.json',anchors)
prior=json.loads((ROOT/'docs/tester/D1_R1_EVIDENCE/selected-source-audit.json').read_text(encoding='utf-8'))
paths=[r['path'] for r in prior['sources']]
for tail in ['src/com/videokit/spike/c14/HostFixtures.java','android/com/videokit/spike/c14/EncoderCapabilities.java','android/com/videokit/spike/c14/AndroidLease.java','android/com/videokit/spike/c14/NativeCpu.java','native/cpu.c','android/com/videokit/spike/c14/MediaEngine.java','android/com/videokit/spike/c14/PlatformFaceProbe.java','android/com/videokit/spike/c14/CpuIsolatedService.java','android/com/videokit/spike/c14/IsolatedMediaService.java','worker_app/src/main/AndroidManifest.xml']:
    p='docs/coder/d1c14/'+tail
    if p not in paths: paths.append(p)
manifest=json.loads((ROOT/'docs/coder/d1c14/evidence/source-manifest.json').read_text(encoding='utf-8'))
zip_path=ROOT/'docs/coder/d1c14/artifacts/D1-20261016-C14/D1-20261016-C14-source.zip'
rows=[]
with zipfile.ZipFile(zip_path) as z:
    names=z.namelist()
    for rel in paths:
        data=(ROOT/rel).read_bytes()
        candidates=[n for n in names if n==rel or n.endswith('/'+rel) or n==rel.removeprefix('docs/coder/d1c14/')]
        assert len(candidates)==1,(rel,candidates)
        frozen=z.read(candidates[0])
        # Manifest schema is intentionally inspected through recursive records.
        def records(x):
            if isinstance(x,dict):
                if x.get('sha256')==sha(data): yield x
                for v in x.values(): yield from records(v)
            elif isinstance(x,list):
                for v in x: yield from records(v)
        mr=list(records(manifest))
        assert data==frozen and mr,rel
        rows.append(dict(path=rel,sha256=sha(data),bytes=len(data),zipEntry=candidates[0],zipMatches=True,manifestMatches=True))
        dest=OUT/'sources'/Path(rel).relative_to('docs/coder/d1c14')
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
save('selected-source-audit.json',dict(scope='Static byte comparisons only, not runtime verification',sources=rows))
inventory=json.loads((ROOT/'docs/coder/d1c02/evidence/media-inventory.json').read_text(encoding='utf-8'))
selected=[r for r in inventory['files'] if r['relative_path'] in ['03_large_files/large_video_over_2GiB.mkv','04_corrupted_files/corrupted_video.mp4','04_corrupted_files/empty_video.mkv']]
assert len(selected)==3
save('historical-input-identities.json',dict(scope='Historical inventory records only; no media bytes read and no current full-file SHA claim',inputs=selected))
assert all(r['matches'] for r in identities)
assert all(r['lineValid'] for r in links)
print(json.dumps(dict(inputFiles=len(inputs),allHashesMatch=True,linkOccurrences=len(links),uniqueTargets=len({r['target'] for r in links}),sourceFiles=len(rows),allSourcesMatchFrozen=True),ensure_ascii=False))
