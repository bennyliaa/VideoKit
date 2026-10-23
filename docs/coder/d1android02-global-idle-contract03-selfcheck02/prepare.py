"""Static prepare: validate immutable inputs, helper lineage, complete profiles."""
from pathlib import Path
import json,hashlib,os,ast,difflib
H=Path(__file__).resolve().parent;B=Path('D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract03-fix')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
manifest=json.loads((B/'reference/freeze-manifest.json').read_text())
for r in manifest['files']:assert sha(B/r['path'])==r['sha256']
plan=json.loads((H/'reference/plan.json').read_text());assert sha(B/'reference/runner-source-seal.json')==plan['sourceSealSha256']
runtime=json.loads((H/'reuse/runtime-pins.json').read_text())
for r in runtime['files']:assert sha(Path(r['path']))==r['sha256']
paths=[p for d in (H,H/'helpers',H/'reuse') for p in d.iterdir() if p.is_file() and p.suffix in ('.py','.ps1','.json')]
for p in paths:
 if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
qc=H/'work/qualification';qc.mkdir(exist_ok=False)
env={'SystemRoot':'C:\\Windows','WINDIR':'C:\\Windows','TEMP':str(qc),'TMP':str(qc)}
sources=json.loads((B/'reference/runner-source-seal.json').read_text())['sources']
profile=dict(schema='CONTRACT03_SELFCHECK02_PROFILE_V1',hostCwd=str(Path.cwd()),qualificationCwd=str(qc),qualificationEnv=env,inheritedEnvSha256=hashlib.sha256(json.dumps(dict(os.environ),sort_keys=True,separators=(',',':')).encode()).hexdigest(),inheritedEnvPolicy='UNCHANGED_ENV_NONE; digest only, no secret values saved',routingOverridesAbsent={k:k not in os.environ for k in ('ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT','ANDROID_ADB_SERVER_ADDRESS','ADB_VENDOR_KEYS','ANDROID_SERIAL','ADB_SERVER_ADDRESS')},candidateOutput=plan['candidateOwnOutput'],candidateSources=sources,scriptPins={str(p):sha(p) for p in paths if p.suffix in ('.py','.ps1')},callFamilies=['SELF python-ok/fail and PS-ok explicit4-env','fixed current helper PS with exact IO switches','frozen production-runner CLI default deny/exact OFFLINE permit hashes','frozen route_fixture with OFFLINE context','frozen fact_fixture COMPLETE','original fresh fixed PS capture controller+exact request/precedessor/admission hashes','post-guard-host.ps1 from frozen helper producer in fresh owned scope'],popenKwargs=dict(stdin='DEVNULL',stdout='PIPE',stderr='PIPE',shell=False,closeFds=True,executable='None or exactly argv[0]',cwd='None or qualificationCwd',env='None unchanged or exact four-entry qualificationEnv'),audit='OBSERVATION_ONLY: applicationName may be None; commandLine must match Windows list2cmdline. Unexpected event stops subsequent admission after original return, never throws in callback.',helperCodePins={str(p.relative_to(H)):sha(p) for p in paths},productionChanges=0)
assert all(profile['routingOverridesAbsent'].values())
put(H/'reference/profile.json',profile)
orig=(H/'reuse/future_capture.py').read_text();new=(H/'owned_capture.py').read_text();(H/'reference/receiver-diff.patch').write_text(''.join(difflib.unified_diff(orig.splitlines(True),new.splitlines(True),fromfile='SELF/future_capture.py',tofile='SELFCHECK02/owned_capture.py')),encoding='utf-8')
put(H/'reference/lineage.json',dict(originalSELFManifestSha256=sha(H/'reference/SELF-original-source-manifest.json'),originalCaptureSha256=sha(H/'reuse/future_capture.py'),derivedReceiverSha256=sha(H/'owned_capture.py'),nativeIdentityUnchanged=sha(H/'reuse/native_identity.py')=='094539b62d0c8e6876921c678914c98e6d20d453771091c8819c44eecb64b2a0',journalUnchanged=sha(H/'reuse/evidence_io.py')=='ffeac99ea5b071a6fb3700277556907ee55969ae479831bf70f5381d512c4bf0',changes=['Original wait/drain/stream/handle close+disposition algorithm reused','Replace old activation/fixed-three launch admission with this exact frozen scope profiles','Move parameter/program/cwd/env validation before original constructor','Audit observation in memory; no callback exception or IO','Profile-specific auxiliary observation5/80 seconds; original production limits unchanged','All derived helper output paths new and frozen product path retained']))
put(H/'reference/pre-audit.json',dict(candidateManifestSha256=sha(B/'reference/freeze-manifest.json'),originalRows=len(manifest['files']),bad=0,sourceSealSha256=sha(B/'reference/runner-source-seal.json'),gateSourcesSha256=sha(B/'reference/gate-sources.json'),planSha256=sha(B/'reference/exact-seven-role-plan.json'),profileSha256=sha(H/'reference/profile.json'),scripts=len(paths),estimatedSeconds=245,maxSeconds=360,plannedGraphProcesses=78,capProcesses=96))
print(json.dumps(dict(profile=sha(H/'reference/profile.json'),candidateRows=len(manifest['files']),bad=0,helperPaths=len(paths))))
