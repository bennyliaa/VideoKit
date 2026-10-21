"""Independent readonly evidence reconciliation; no candidate imports or probes."""
from pathlib import Path
from datetime import datetime
import hashlib,json,ast
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e3'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
probes=read(BASE/'evidence/native-probes.json');checks=read(BASE/'evidence/preparation-checks.json')
assert checks['status']=='PASS' and checks['assertions']==len(checks['checks'])==280
assert read(BASE/'selfcheck/preparation-01.stdout.json')==checks
assert probes['nativeProbeAssertions']==25 and len(probes['cases'])==2
for case in probes['cases']:
    folder=BASE/'selfcheck'/('java-bridge-'+case['mode'])
    assert read(folder/'stdout.json')==case['receipt']
    assert (folder/'stdout.json').stat().st_size==case['stdoutBytes'] and (folder/'stderr.log').stat().st_size==case['stderrBytes']==0
    assert (folder/'L.bin').stat().st_size==4096 and case['processExitObserved'] and case['exitCode']==0
    assert case['receipt']['assertions']==len(case['receipt']['checks'])
    for p in folder.iterdir():
        dest=OUT/'native-probe-archive'/folder.name/p.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
build=read(BASE/'evidence/build.json')
for r in build['sourceFiles']+build['compiledArtifacts']:
    p=BASE/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
assert len(build['compiledArtifacts'])==14 and build['csharpCompilations']==build['javaCompilations']==1 and build['repairCompilations']==0
for name in ('authority.py','notifications.py','runtime_metrics.py'):
    assert (BASE/'src'/name).read_bytes()==(ROOT/'docs/coder/d1e2f/src'/name).read_bytes()
manifest=read(BASE/'manifest/branches.json');old=read(ROOT/'docs/coder/d1e2f/manifest/branches.json')
fields=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')
assert manifest['limits']==old['limits'] and manifest['executionOrder']==old['executionOrder']
for a,b in zip(manifest['branches'],old['branches']):
    assert a['id']==b['id'] and all(a[k]==b[k] for k in fields)
assert (BASE/'profiles/runtime-policy.json').read_bytes()==(ROOT/'docs/coder/d1e2f/profiles/runtime-policy.json').read_bytes()
completion=(BASE/'tools/completion_evaluation.py').read_text(encoding='utf-8')
assert 'EXPECTED_USAGE' not in completion and 'SEAL_SHA256' not in completion and 'ORIGINAL_160' not in completion
assert '_assertions(preclose, witness, check)' in completion
for name in ('e3_admission.py','completion_evaluation.py'):
    tree=ast.parse((BASE/'tools'/name).read_text(encoding='utf-8'))
    imports={a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
    assert not imports&{'ctypes','subprocess','threading','gcore','gengine'}
assert not (BASE/'execution').exists() and not (BASE/'runs').exists()
save('independent-scope-review.json',dict(at=datetime.now().astimezone().isoformat(),scope='Source/bytes/JSON only; no candidate imports, code tests or OS sampling',recordedPurePreparationAssertions=280,recordedPureNegativeCases=len(checks['negativeCases']),recordedJavaProbeAssertions=25,recordedJavaProbeProcesses=2,recordedJavaProbeRequestedBytes=2,recordedJavaProbeActualBytes=1,recordedFixturesBytes=8192,rawProbeReceiptsMatch=True,compiledRuntimeArtifacts=14,recordedCompilations=dict(csharp=1,java=1,repair=0),unchangedCore=['authority.py','notifications.py','runtime_metrics.py'],originalRowBudgetsAndOperationsUnchanged=True,originalPolicyByteIdentical=True,GNewNativePathExecuted=False,RNewNativePathExecuted=False,postReadVersionChangeInjectionExecuted=False,JavaBindingFailureOrCloseUnknownInjectionExecuted=False,newProbeRunsByTester=0,mediaStatCalls=0,mediaBytesRead=0,reservationConsumed=False,findings=[]))
print('PASS: raw Java receipts, build hashes, unchanged core/policy/61 budget and parameterized source; no execution')
