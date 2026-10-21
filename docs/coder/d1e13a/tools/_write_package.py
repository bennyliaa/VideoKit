"""Explicit E13A pack only. Default verification lives in package_delivery.py and never imports this."""
import sys
if sys.argv[1:]!=['pack']:raise SystemExit('Explicit pack required; use package_delivery.py verify for read-only verification')
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile,re,difflib,shutil,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e13';E=B/'evidence';ID='D1-20261018-E13A'
def sha(b):return hashlib.sha256(b).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def pin(p):b=p.read_bytes();return {'path':rel(p),'bytes':len(b),'sha256':sha(b)}
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def baselines():
    result=[]
    for name,h in [('d1e11/evidence/e11-freeze.json','fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5'),('d1e11/revision-r1/evidence/e11-final-freeze.json','2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3'),('d1e12/e12-freeze.json','6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640'),('d1e13/evidence/e13-freeze.json','3b80d430aa7f859174ffae0a4b5ca948a01aa032d15c0666fb595e6a1bba5cc0')]:
        path=R/'docs/coder'/name;assert pin(path)['sha256']==h
        rows=json.loads(path.read_text(encoding='utf-8'))['immutableFiles']
        for row in rows:check(row)
        result.append({'seal':pin(path),'immutableRowsVerified':len(rows)})
    return result
prior=baselines();write(E/'external-readonly-verification.json',{'status':'PASS','baselines':prior,'oldMisusedPackagerReexecuted':False,'scope':'Current exact old bytes, not a new functional test'})
inputs=json.loads((E/'final-build-inputs.json').read_text())['files']
for row in inputs:check(row)
compiled=json.loads((E/'local-checks/binding-001/inputs.json').read_text())
for row in compiled:check(row)
reference=B/'reference';reference.mkdir(exist_ok=True)
refs=[R/'docs/tester/D1_E13_ARCHITECTURE_REVIEW_REPORT_V1.0.md',R/'docs/tester/D1_E13_REVIEW_EVIDENCE/three-metadata-field-plan.json',R/'docs/milestones/D1_E13A_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13A_TESTER_REQUIREMENTS_V1.0.md',R/'docs/coder/D1_E13_RENDER_AUDIO_SOURCE_AND_KIT_DECISION_V1.0.md']
for path in refs:shutil.copyfile(path,reference/path.name)
write(E/'requirements-and-review-pins.json',{'files':[pin(p) for p in refs]})
sdk=[]
for filename,ranges in [('android/content/Context.java',[(4206,4216)]),('android/app/ContextImpl.java',[(2273,2304),(2358,2379)]),('android/app/LoadedApk.java',[(2091,2110),(2226,2236),(2283,2295)])]:
    path=Path('D:/Android/SDK/sources/android-36.1')/filename;raw=path.read_bytes();lines=raw.decode('utf-8').splitlines()
    sdk.append({'path':path.as_posix(),'bytes':len(raw),'sha256':sha(raw),'excerpts':[{'firstLine':a,'lastLine':b,'text':'\n'.join(lines[a-1:b])} for a,b in ranges]})
write(E/'sdk-binding-contract.json',{'scope':'Local SDK36.1 primary source; not API31 device execution','sources':sdk})
untouched=[]
for name in ['src/com/videokit/spike/e4/E13SourceGroup.java','upstream-c14/src/com/videokit/spike/c14/AsyncReadBridge.java','upstream-c14/src/com/videokit/spike/c14/LeaseRegistry.java','upstream-c14/src/com/videokit/spike/c14/SourceAdmission.java','upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java','android/com/videokit/spike/e4/E4Session.java','checks/com/videokit/spike/e4/E13SourceCases.java']:
    assert (B/name).read_bytes()==(OLD/name).read_bytes();untouched.append({'current':pin(B/name),'baseline':pin(OLD/name)})
write(E/'unchanged-source-lifecycle.json',{'files':untouched,'oldSourceCasesRerun':0,'nativeRuns':0})
sources=[]
for folder in ['src','android','upstream-c14/src','upstream-c14/android','app/src','fixture/src','binding','checks','tools']:
    sources += [p for p in (B/folder).rglob('*') if p.is_file()]
sources += [p for folder in [B,B/'app',B/'fixture'] for p in folder.iterdir() if p.is_file() and p.suffix in {'.kts','.properties','.lockfile'}]
derived=[]
for path in sorted(set(sources)):
    old=OLD/path.relative_to(B);before=pin(old) if old.is_file() else None;after=pin(path);same=before and before['sha256']==after['sha256']
    derived.append({'current':after,'baseline':before,'relationship':'BYTE_IDENTICAL' if same else 'DERIVED_E13' if before else 'NEW_E13A'})
    if not same and path.suffix in {'.java','.py','.ps1','.kts','.xml','.properties','.lockfile'}:
        target=E/'diffs'/path.relative_to(B);target=target.with_suffix(target.suffix+'.diff');target.parent.mkdir(parents=True,exist_ok=True)
        a=old.read_text(encoding='utf-8-sig').splitlines(True) if old.is_file() else [];b=path.read_text(encoding='utf-8-sig').splitlines(True)
        target.write_text(''.join(difflib.unified_diff(a,b,fromfile=rel(old) if old.is_file() else '/dev/null',tofile=rel(path))),encoding='utf-8')
write(E/'source-derivation.json',{'baseline':'Frozen E13 367 rows','files':derived})
classes=B/'.checks/binding-001/classes';production=[]
for folder in ['src','upstream-c14/src','binding']:production+=list((B/folder).rglob('*.java'))
production += [p for p in (B/'tools').glob('*.java') if not p.name.endswith('Check.java')]
allow={}
for path in production:
    pkg=re.search(r'package\s+([\w.]+);',path.read_text(encoding='utf-8-sig')).group(1);allow[pkg.replace('.','/')+'/'+path.stem]=path
art=B/'artifacts'/ID/'delivery';jar=art/'e13a-host-tools.jar';classRows=[]
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for path in sorted(classes.rglob('*.class')):
        entry=path.relative_to(classes).as_posix();top=entry[:-6].split('$')[0]
        if top not in allow:continue
        raw=path.read_bytes();z.writestr(entry,raw);classRows.append({'entry':entry,'bytes':len(raw),'sha256':sha(raw),'source':pin(allow[top])})
write(E/'host-jar-manifest.json',{'jar':pin(jar),'classes':classRows,'scope':'Exact production classes from binding-001; no recompile, no binding/source selfcheck classes'})
apk=json.loads((E/'apk-delivery/apk-audit.json').read_text());release=B/'release';release.mkdir(exist_ok=True)
write(release/'candidate-binding.json',{'status':'DRAFT_NOT_APPROVAL','candidate':ID,'version':17,'role':'ACTIVATION','abi':1,'acceptedSourceVersion':15,'sourceAcceptance':'60eb18e88e346e49ec34491083f2b67da21670d7cd5fde40ce3b72ba8246b635','targetApks':apk['apks'],'hostJar':pin(jar),'actualApprovedScope':None,'actualRelease':None,'actualOnce':None,'onceBasename':'e13a-activation-deployment.once','batch':'D1-E13A-SOURCE-20261018'})
plan=json.loads((OLD/'release/device-plan.json').read_text());plan.update({'candidate':ID,'targetVersion':17,'acceptedSourceVersion':15,'batch':'D1-E13A-SOURCE-20261018','newOnceBasename':'e13a-activation-deployment.once','exactMetadataManifest':pin(release/'metadata/three-client-manifest.json'),'metadataPlanMustBeFinalizedBeforeDevice':True,'exactMetadataArgvProvided':True,'metadataFinalizationRemaining':'Independent review and adoption of these exact pins into future approved scope; no device client executed','metadataRuntimeCompatibility':'NOT_RUN; missing/unsupported field is BLOCKED, not extra queries','status':'EXACT_ARGV_REVIEW_ONLY_NOT_DISPATCHED'})
write(release/'device-plan.json',plan)
logs=[]
for path in sorted((E/'local-checks/binding-001').glob('*.stdout.txt')):
    if path.stem.startswith('compile'):continue
    match=re.search(r'assertions=(\d+)',path.read_text());logs.append({'log':pin(path),'assertions':int(match.group(1))})
write(E/'binding-check-summary.json',{'groups':len(logs),'assertions':sum(x['assertions'] for x in logs),'logs':logs,'productionOwnerExecutes':True,'contextCallsAndScheduling':'PLATFORM_SUBSTITUTES_ONLY','androidBinderTests':0})
write(E/'metadata-syntax-attempt-note.json',{'scope':'Local syntax harness only, no script content execution','first':'MSYS native synchronization object creation denied in workspace sandbox; not a script syntax result','second':'Windows/MSYS -c transport quote parsing reported unmatched quote; not Android execution','correction':'Read exact UTF-8 files with bash -n, outer plus nested bodies; 29 checks passed','productFunctionalityFail':False,'deviceCalls':0})
delivery='''# D1 E13A 完整修复交付 V1.0

日期：2026-10-18。候选D1-20261018-E13A，v17/ACTIVATION/ABI1。修复E13-F01/P1、E13-F02/P2；当前交独立tester整包静态复审。六方法Android全部NOT_RUN，没有ADB/真实媒体/实际新scope/release/once，D1 NOT_PASSED / M0 NOT_STARTED。

## 改动及验证

P1：两处实际Android绑定适配器共同使用E13BindingOwner。false和SecurityException也对同一原ServiceConnection执行一次必要unbind/forget。bind进入/正常或异常实际返回、回调在途、原unbind进入/返回/异常独立记账；一次进入后不重复unbind，未知保原owner并阻止真实runner/PC结束。kernel拒绝与resourcesReturned分栏，普通负例仍未取得codec endpoint，不称内部onTransact跨UID实测。原日志增加target/两个client的真实binding状态。

九个有限分支直接执行生产共同owner，平台Context调用/回调调度替身：FALSE、SECURITY、OTHER_EXCEPTION、TRUE_CALLBACK、BIND_IN_FLIGHT、UNBIND_IN_FLIGHT、CALLBACK_IN_FLIGHT、LATE_CALLBACK、UNBIND_EXCEPTION。解绑异常预期保原keeper，未用第二次unbind伪造ACK；替身没有Android dispatcher，JVM自然结束不是Android关闭证据。原source keeper/AsyncReadBridge/LeaseRegistry/SourceAdmission/CpuTaskClient/source场景字节继承，无旧source/native/历史signal套件重跑。

P2：package_delivery.py默认和verify均严格只读，help参数先返回；唯一显式pack才加载写封装器，写封装器本身也先检查pack。前冻结default/verify/help/pack-help比较197份候选文件前后全相同，原E13 seal/367行全字节未变；没再执行旧误用入口，也不把既有JAR x误用异常算产品FAIL。最终冻结后又实际执行默认和带独立seal pin的verify，并比较全文件快照，结果在包外最终回执。只读核验只读metadata/hash/ZIP/JAR，不跑候选、自检、构建、设备或媒体。

一次主离线集中app/test/fixture构建main-001成功，约1m7s、101任务，0修正构建。最终输入139项SHA2c71c4e24e28abff2c6cd03ad30e8a638e7a39b95c8b3eb91348c213df4b939c；主锁仍35Maven、7native与原源/实际APK相同，fixture空runtime锁、不同原Debug signer不变，未下载/重建native。SDK签名/manifest/ZIP静态检查和两APK实际BindingOwner DEX接线检查通过。静态16KiB对齐不是设备运行证据。

M1/M2/M3采用tester既有字段计划：34固定stat、18control pins/2271B原ledger/固定inventory，并更新v17 pair/fixture实际hash。三个精确完整argv及remote脚本在release/metadata；每份一个直接原ADB客户端，无预算外Java/Python wrapper。70/18/71个记录，含标记的上界53512/27588/56360B，均在单64KiB/总196608B原分配内；原48process/2MiB不增。29个本机Git Bash -n文件语法检查通过，未执行脚本内容；早期本机MSYS沙箱/Windows -c引用检查问题另记，不冒设备FAIL或API31字段成功。

## 最终制品

'''
for row in apk['apks']:delivery+=f"- {row['kind']}：{row['path']}；{row['bytes']}B；SHA256 {row['sha256']}；signer {row['signer']}\n"
delivery+=f"- host JAR：{rel(jar)}；{jar.stat().st_size}B；SHA256 {pin(jar)['sha256']}；{len(classRows)}个production class，来自binding-001实际编译，没有检查类。\n"
delivery+=f"- 本机binding：{len(logs)}组、{sum(x['assertions'] for x in logs)}个断言；完整原输入/argv/stdout/stderr/exit随包。不是设备用例通过数。\n"
delivery+='''
四文档为DELIVERY、ARCHITECTURE_AND_THREAT_BOUNDARY、REMAINING_GATE_REVIEW、DEVICE_EXECUTION_APPENDIX；SDK主证据/精确diff/原输入日志/三APK与JAR/空fixture锁/SBOM/metadata精确计划随包。fixture私钥只本机保管，不归档；重建需相应签名环境或新candidate/pins。源接受仍是v15，v16未安装；新target17/batchE13A/e13a固定once，未签发实际scope/许可。

严格只读核验用Python -B tools/package_delivery.py（默认）或同命令verify --seal-sha 独立SHA；帮助--help。写封装只能pack，冻结后不重pack。外seal不自哈希，ZIP与全部不可变字节/JAR及原E11/E12/E13封印由真正只读入口核验；最终回执是包外记录。

原接受214483B/7R7S/0reserved、107218B前缀/旧产物/fence/oldCloseACK=false只引用E11报告时点，未在线重读/写账，媒体输出/READY/新R/S=0。E11有限实机PASS、C13系统0严格FAIL/外部raw11/另方法11、C14 NOT_RUN/ordinary UNKNOWN保持。renderer/audio/source/Kit继续E13已审SUPPORTED_DESIGN_ONLY，声音显示NOT_RUN、合法压缩音频→PCM BLOCKED，独立AAR/Fake/Flutter/全部P0/许可/长期门未过。

请tester一次完整静态复审后，由负责人另行正式设备批次；设备长期授权和他项目占用稍后试有效，当前不自行实测或扩修。若metadata实际字段/命令/输出或48预算不足，先BLOCKED交负责人，不能增加wrapper/查询/截断填成功。
'''
(R/'docs/coder/D1_E13A_DELIVERY_V1.0.md').write_text(delivery,encoding='utf-8')
excluded={'build','.gradle','.checks','__pycache__'}
files=[p for p in B.rglob('*') if p.is_file() and not any(v in excluded for v in p.relative_to(B).parts) and p.suffix!='.p12' and p.name!='e13a-freeze.json']
files+=list((R/'docs/coder').glob('D1_E13A_*.md'))+[R/'docs/milestones/D1_E13A_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13A_TESTER_REQUIREMENTS_V1.0.md',R/'docs/coder/e13a_bootstrap.py']
names=sorted({rel(p) for p in files});archive=R/'docs/coder/D1-20261018-E13A-source.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for name in names:z.write(R/name,name)
with zipfile.ZipFile(archive) as z:
    assert sorted(z.namelist())==names
    for name in names:assert z.read(name)==(R/name).read_bytes()
seal={'schema':1,'candidate':ID,'status':'FROZEN_E13A_P1_P2_REPAIR_DEVICE_NOT_RUN','atUtc':datetime.now(timezone.utc).isoformat(),'archive':pin(archive),'immutableFiles':[pin(R/n) for n in names]+[pin(archive)],'sourceEntries':len(names),'priorSeals':prior,'exclusions':['cache/build/.checks','fixture private signing key','external seal self','post-freeze verification receipt/handoff/notification'],'deviceCalls':0,'actualScope':None,'actualOnce':None}
write(E/'e13a-freeze.json',seal);sealPin=pin(E/'e13a-freeze.json')
def snapshot():return [pin(p) for p in sorted(B.rglob('*')) if p.is_file() and not any(v in excluded for v in p.relative_to(B).parts)]
before=snapshot();verifications=[]
for args in [[],['verify','--seal-sha',sealPin['sha256']]]:
    argv=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py')]+args
    result=subprocess.run(argv,capture_output=True,timeout=60);assert result.returncode==0,(args,result.stderr.decode())
    parsed=json.loads(result.stdout);assert parsed['status']=='PASS_E13A_STRICT_READONLY_VERIFY' and parsed['writes']==0
    verifications.append({'argv':argv,'exitCode':result.returncode,'stdout':parsed,'stderr':result.stderr.decode()})
assert before==snapshot(),'READONLY_FINAL_VERIFY_MUTATED_FILES'
receipt={'status':'PASS_E13A_FINAL_STRICT_READONLY_VERIFICATION','atUtc':datetime.now(timezone.utc).isoformat(),'archive':pin(archive),'externalSeal':sealPin,'archiveEntries':len(names),'immutableRows':len(seal['immutableFiles']),'readonlySnapshotFilesUnchanged':len(before),'verifications':verifications,'priorSeals':prior,'apks':apk['apks'],'hostJar':pin(jar),'hostClasses':len(classRows),'bindingGroups':len(logs),'bindingAssertions':sum(x['assertions'] for x in logs),'nativeLibraries':7,'mavenCoordinates':35,'fixtureRuntimeCoordinates':0,'deviceCalls':0,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
write(R/'docs/coder/D1_E13A_FINAL_READONLY_VERIFICATION_V1.0.json',receipt)
print(json.dumps({k:v for k,v in receipt.items() if k!='verifications'},ensure_ascii=False))
