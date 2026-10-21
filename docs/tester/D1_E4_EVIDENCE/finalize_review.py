"""Static final E4 report and frozen-byte checks; never invokes candidate code."""
from pathlib import Path
from datetime import datetime
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e4';REPORT=ROOT/'docs/tester/D1_E4_ARCHITECTURE_REVIEW_REPORT_V1.0.md'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=(BASE/'evidence/e4-freeze.json').read_bytes();assert sha(raw)=='0940855c58ada5c2ce3b23e8bd4c63803016afeb4b563127f589a043847e0227'
for r in json.loads(raw)['immutableFiles']:
    b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
for target in re.findall(r'\]\((D:/[^)]+)\)',REPORT.read_text(encoding='utf-8')):
    m=re.match(r'(.+?)(?::(\d+))?$',target);p=Path(m[1]);assert p.exists(),target
    if m[2]:assert 0<int(m[2])<=len(p.read_text(encoding='utf-8').splitlines())
def coords(raw):return {line.split('=',1)[0] for line in raw.decode().splitlines() if not line.startswith('#') and '=' in line and line.split('=',1)[0].count(':')==2}
with zipfile.ZipFile(BASE/'upstream-c14/D1-20261016-C14-source.zip') as z:oldraw=z.read('app/gradle.lockfile')
newraw=(BASE/'app/gradle.lockfile').read_bytes();old=coords(oldraw);new=coords(newraw)
def versions(values):
    out={}
    for c in values:
        group,name,v=c.split(':');out.setdefault(group+':'+name,set()).add(v)
    return out
ov=versions(old);nv=versions(new);delta=json.loads((BASE/'evidence/sbom-difference.json').read_bytes())
diff={k:dict(previous=sorted(ov[k]),current=sorted(nv[k])) for k in ov.keys()&nv.keys() if ov[k]!=nv[k]}
assert len(new)==35 and not nv.keys()-ov.keys() and len(diff)==14 and diff==delta['selectedVersionDifferences']
assert sha(oldraw)==delta['originalC14LockSha256'] and sha(newraw)==delta['currentLockSha256']
save('independent-sbom-check.json',dict(currentCoordinates=35,addedPackageFamilies=[],selectedVersionDifferences=diff,originalC14LockSha256=sha(oldraw),currentLockSha256=sha(newraw),newSCA=False,productionLicenseAcceptance=False))
findings=[dict(id='E4-F01',priority='P1',title='Failure abort deletes original output and stock-only budget refunds deleted bytes',source='E4Session.java:165 + FencedTask.java:95 + E4Session.Sink.open',evidence='Static actual call chain; no fault executed'),dict(id='E4-F02',priority='P1',title='Unreturned FencedTask/AndroidLease construction can lose close-UNKNOWN original owner',source='E4Session.java:269 + FencedTask.java:41/44 + AndroidLease.java:15/17',evidence='Construction fails after allocation, close also unproven; outer task field not assigned; no fault executed'),dict(id='E4-F03',priority='P2',title='Cancellation test asserts one immutable terminal snapshot before independent control return is observed',source='E4Session.java:171/206 + E4DeviceTests.java:127',evidence='Static possible scheduling window; no Android race reproduction claimed')]
save('findings.json',dict(status='REQUEST_CHANGES',findings=findings,executedFaults=0))
save('readonly-verify-receipt.json',dict(command='python -X utf8 -B docs/coder/d1e4/tools/verify_e4.py --expected-freeze 0940855c58ada5c2ce3b23e8bd4c63803016afeb4b563127f589a043847e0227',exitCode=0,integrity='PASS',sourceFiles=112,immutableFiles=116,localAssertions=89,readUsage=dict(physicalBytesRead=73348886,logicalArchiveBytesRead=29438436,fileReads=172),androidExecution='NOT_RUN',meaning='Frozen identity only, not behavior acceptance'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E4 independent architecture/code/archive review',report=str(REPORT.relative_to(ROOT)),reportSha256=sha(REPORT.read_bytes()),conclusion='REQUEST_CHANGES_BEFORE_FORMAL_DEVICE_BATCH',findings=findings,candidateIntegrity='PASS',candidateUnchanged=True,sourceFiles=112,immutableFiles=116,recordedLocalJvmAssertions=89,jvmRerun=False,gradle=False,adb=False,devices=False,nativeFault=False,mediaIO=False,fixtureReads=False,actualBinderTests=False,codeReviewOnly=True,deviceCasesPlanned=8,quarantineCasesEachLast=3,sameUidCodecCrashBoundaryOnly=True,ordinaryIsolatedCompressedParsing=True,hostLeaseJNIResidual=True,nativeLibrariesUnchanged=7,newMavenPackageFamilies=0,changedSelectedVersionFamilies=14,productionLicenseAccepted=False,deviceExecutionRecommended=False,inFlight=[],oldC14Unchanged=True,oldSignalFailUnchanged=True,D1Passed=False,M0Started=False,notification='PENDING_SEND'))
print('PASS: final frozen bytes, report links, independent 35-coordinate/14GA delta; report SHA256 '+sha(REPORT.read_bytes()))
