"""E13 provenance, host-only JAR from final checked classes, docs/ZIP/external seal/byte audit.
No device dispatch, media, Gradle, JNI build or candidate test execution.
"""
from pathlib import Path
import hashlib,json,re,zipfile,difflib,shutil,struct,collections
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e11';E=B/'evidence'
ID='D1-20261018-E13'
def rel(p):return p.relative_to(R).as_posix()
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return {'path':rel(p),'bytes':len(b),'sha256':sha(b)}
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def inherited():
 oldSeals=[(OLD/'evidence/e11-freeze.json','fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5'),(OLD/'revision-r1/evidence/e11-final-freeze.json','2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3'),(R/'docs/coder/d1e12/e12-freeze.json','6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640')]
 result=[]
 for seal,h in oldSeals:
  assert pin(seal)['sha256']==h
  rows=json.loads(seal.read_text(encoding='utf-8'))['immutableFiles']
  for row in rows:verify(row)
  result.append({'seal':pin(seal),'immutableRowsVerified':len(rows)})
 return result
for row in json.loads((E/'final-build-inputs.json').read_text())['files']:verify(row)
for row in json.loads((E/'local-checks/final-003/inputs.json').read_text()):verify(row)
oldVerified=inherited();js(E/'external-readonly-verification.json',{'status':'PASS','baselines':oldVerified,'deviceCalls':0,'mediaProcessing':0})
# Pin all final check registry bytes, identifying actual .checks inputs plus portable exact copies.
reference=B/'reference';reference.mkdir(exist_ok=True)
registry=B/'.checks/final-003/accepted-registry-copy';portable=reference/'accepted-registry';shutil.copytree(registry,portable,dirs_exist_ok=True)
registryRows=[]
for p in sorted(registry.rglob('*')):
 if p.is_file():
  target=portable/p.relative_to(registry);source=OLD/'source-export/accepted-registry-snapshot'/p.relative_to(registry)
  assert p.read_bytes()==target.read_bytes()==source.read_bytes();registryRows.append({'actualFinalCheckInput':pin(p),'portableCopy':pin(target),'acceptedSource':pin(source)})
js(E/'selfcheck-registry-provenance.json',{'scope':'Supplementary after-run byte audit; final checker itself computed before/after equality','files':registryRows})
for p in [R/'docs/tester/D1_E11_FINAL_R1_TABLET_EXECUTION_REPORT_V1.0.md',R/'docs/tester/D1_E12_REQUIREMENT_GATE_REVIEW_REPORT_V1.0.md',R/'docs/milestones/D1_E13_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13_TESTER_REQUIREMENTS_V1.0.md']:
 shutil.copyfile(p,reference/p.name)
js(E/'requirements-and-accepted-source-pins.json',{'files':[pin(p) for p in [R/'docs/tester/D1_E11_FINAL_R1_TABLET_EXECUTION_REPORT_V1.0.md',R/'docs/tester/D1_E12_REQUIREMENT_GATE_REVIEW_REPORT_V1.0.md',R/'docs/milestones/D1_E13_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13_TESTER_REQUIREMENTS_V1.0.md']]})
# Exact diff against E11 final R1 override, not its superseded base host source.
derivation=[]
roots=['src','android','upstream-c14/src','upstream-c14/android','checks','tools','app/src','fixture/src']
allSources=[]
for folder in roots:allSources += [p for p in (B/folder).rglob('*') if p.is_file()]
allSources += [p for folder in [B,B/'app',B/'fixture'] for p in folder.iterdir() if p.is_file() and p.suffix in {'.kts','.properties','.lockfile'}]
for p in sorted(set(allSources)):
 prior=OLD/p.relative_to(B)
 if p.relative_to(B).as_posix() in ['tools/E9HostActivationSession.java','tools/E11DeploymentOnce.java']:prior=OLD/'revision-r1'/p.relative_to(B)
 before=pin(prior) if prior.is_file() else None;after=pin(p);same=before and before['sha256']==after['sha256']
 derivation.append({'current':after,'baseline':before,'relationship':'BYTE_IDENTICAL' if same else 'DERIVED_E11_FINAL_R1' if before else 'NEW_E13'})
 if not same and p.suffix in {'.java','.py','.ps1','.kts','.xml','.properties','.lockfile'}:
  target=E/'diffs'/p.relative_to(B);target=target.with_suffix(target.suffix+'.diff');target.parent.mkdir(parents=True,exist_ok=True)
  a=prior.read_text(encoding='utf-8-sig').splitlines(True) if prior.is_file() else [];b=p.read_text(encoding='utf-8-sig').splitlines(True)
  target.write_text(''.join(difflib.unified_diff(a,b,fromfile=rel(prior) if prior.is_file() else '/dev/null',tofile=rel(p))),encoding='utf-8')
js(E/'source-derivation.json',{'baseline':'E11 final R1','files':derivation})
# APK's generated API/tool definitions are recorded separately from Maven dependency resolution.
apkAudit=json.loads((E/'apk-delivery/apk-audit.json').read_text());fixture=next(p for p in apkAudit['apks'] if p['kind']=='fixture')
defined=[]
with zipfile.ZipFile(R/fixture['path']) as z:
 for name in z.namelist():
  if not name.endswith('.dex'):continue
  data=z.read(name);u=lambda off:struct.unpack_from('<I',data,off)[0];strings,types,classes,count=u(60),u(68),u(100),u(96)
  for i in range(count):
   p=u(strings+u(types+u(classes+i*32)*4)*4)
   while data[p]&128:p+=1
   p+=1;defined.append(data[p:data.index(0,p)].decode())
assert not any(n.startswith('Lkotlin/') for n in defined)
js(E/'fixture-defined-classes.json',{'apk':fixture,'classCount':len(defined),'definedClasses':defined,'note':'Actual DEX definitions include Android API modeling/tool generated stubs from the frozen Android toolchain; zero fixture Maven runtime coordinates does not mean APK consists solely of handwritten classes. This is a location inventory, not a new distribution-license clearance.'})
# Host JAR from classes compiled by final-003. No Android classes or selfcheck fixtures are packaged.
classes=B/'.checks/final-003/classes';production=[p for folder in ['src','upstream-c14/src'] for p in (B/folder).rglob('*.java')]+[p for p in (B/'tools').glob('*.java') if p.name!='E13ProductionCheck.java']
allow={}
for p in production:
 package=re.search(r'package\s+([\w.]+);',p.read_text(encoding='utf-8-sig')).group(1);allow[package.replace('.','/')+'/'+p.stem]=p
jar=B/'artifacts'/ID/'delivery/e13-host-tools.jar';jarRows=[]
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(classes.rglob('*.class')):
  name=p.relative_to(classes).as_posix();top=name[:-6].split('$')[0]
  if top not in allow:continue
  raw=p.read_bytes();z.writestr(name,raw);jarRows.append({'entry':name,'bytes':len(raw),'sha256':sha(raw),'source':pin(allow[top])})
js(E/'host-jar-manifest.json',{'jar':pin(jar),'classes':jarRows,'scope':'Final production host classes from final-003; no recompile/device invocation','checkClassesExcluded':True})
# Draft binding is intentionally separate from any future sourceReview/dispatch authority.
release=B/'release';release.mkdir(exist_ok=True)
binding={'schema':1,'status':'DRAFT_REQUIRES_INDEPENDENT_REVIEW_AND_SPECIFIC_DISPATCH','candidate':ID,'version':16,'role':'ACTIVATION','abi':1,'sourceAcceptance':pin(R/'docs/tester/D1_E11_FINAL_R1_TABLET_EXECUTION_REPORT_V1.0.md'),'targetApks':apkAudit['apks'],'hostJar':pin(jar),'approvedScope':None,'approvedRelease':None,'onceRecord':None,'licenseClearance':'NOT_GRANTED'}
js(release/'candidate-binding.json',binding)
methods=['ordinarySenderCannotBindCodec','authorizedHostSourceReadAndClose','oldGenerationNeverOpensSource','twoConsumersHoldSourceUntilLastReturn','cancelLateOpenRetainsOriginalOwner','lateReadAndCloseFailureDoNotReleaseEarly']
js(release/'device-plan.json',{'status':'REVIEW_ONLY_NOT_DISPATCHED','candidate':ID,'runner':'com.videokit.app.test/com.videokit.spike.e4.E13Instrumentation','hostEntry':'com.videokit.spike.e4.E13HostCase','deploymentEntry':'com.videokit.spike.e4.E13HostActivationSession','methodOrder':methods,'scopeRequired':True,'argsExact':['class','e13Case','e13Batch','e13ScopeSha256'],'budget':{'sourceBytes':4096,'readBytes':65536,'opens':8,'closeAttempts':16,'perOriginalTicketMaxAttempts':3,'methodQualificationSeconds':30,'bridgeAwaitMillis':5000,'pcOperationLimit':48,'pcDeploymentChildren':32,'caseEntries':6,'caseChildren':6,'independentMetadataClients':3,'textBytes':2097152,'deploymentChildText':524288,'caseChildTextEach':65536,'caseEntryTextEach':81920,'deploymentEntryText':32768,'independentMetadataTextEach':65536,'allocatedText':1638400,'remainingTextForExistingMetadata':458752,'mediaOutputBytes':0,'newReservations':0,'newSettlements':0},'scopeTemplateFields':['kind','batch','scopeId','sourceAcceptance','sourceApp','sourceTest','app','test','fixture','fixtureSigner','sourceReview','methods','budget'],'configTemplateFields':['kind','plan','planSha','authorization','review','registryPath','head','dispatchRecord','scopePath','scopeSha'],'releaseTemplateFields':['kind','head','catalog','app','test','signer','role','abi','version','sourceReview','environment','sourceAcceptance','scope'],'newOnceBasename':'e13-activation-deployment.once','actualApprovedConfig':None,'actualOnce':None,'metadataPlanMustBeFinalizedBeforeDevice':True,'D1':'NOT_PASSED','M0':'NOT_STARTED'})
text='''# D1 E13 完整开发交付 V1.0

日期：2026-10-18。唯一候选D1-20261018-E13，v16/ACTIVATION/ABI1。本批六方法及实际source/runner/PC结束接线已实现；本机自检与离线构建/制品审计通过，交tester独立静态复审。**设备六方法全部NOT_RUN，未派发真实新scope/release/once。D1 NOT_PASSED / M0 NOT_STARTED。**

## 完整实现与范围

E12 F01–F04集中落实：精确接受v15 ACTIVATION→16新部署门/原data身份/新scope和固定once；生产AsyncReadBridge与LeaseRegistry原owner强保管、共享消费者聚合、原runtime排空后终止；真实finish/onException与原E9PcSupervisor OriginalAuthority；同生产SourceAdmission当前代实际open/read成功再旧task/epoch/instance零增量拒绝；独立不同签名普通UID fixture的kernel绑定负例与授权host HELLO分栏；六方法/逐ticket/48操作/2MiB预算。

SourceAdmission只是提取CpuTaskClient原等值身份检查，其余CPU取帧/原生解码/验证与严格6帧/EOF/PTS门未改。SourceGroup是本批生产直接source机制，不是全产品多消费者已经集成通过。普通第三方拿不到codec Binder，不声称触达内部onTransact或提供同UID RCE隔离。

五source场景在JVM实际调用生产bridge/ticket/registry/owner，固定4096B非媒体内存定义，最终实际合计6open、4224B read、7close；延期原对象未返时runner门false，实际原返回后才释放，旧代正反对照/双consumer继续可读/一次明确close失败重试/迟到private buffer拒采纳均通过。另有精确v15→16部署port45断言和边界/选择/PC结束解析22断言。最终7组结果在evidence/local-checks/final-003。它们不是Android Binder/kernel/native实测；旧套件和信号方法重跑0。

## 构建及必要修正留痕

主尝试main-001被工作区外Gradle缓存写锁拒绝，在Gradle配置/编译前结束；不是源码编译失败，也不是审批拒绝。经已授权本机缓存访问，repair-001一次离线完整app/test/fixture构建成功，101任务、约1m14s。

制品审计发现AGP为纯Java fixture自动加入Kotlin stdlib2.2.10/annotations13.0；早期审计中fixture运行时0的未充分核验声明不作最终依据，原记录保留。离线依赖检查确认后，用fixture配置排除不必要运行时并锁空依赖，repair-002约33s（6执行/95 up-to-date），主app/test字节未变。最终又补F02/F04原keeper身份/scope与取消/实际返回时间证据，repair-003约28s完成；最终输入138项SHA6eeea5bd2a5faf97cea6f7905f01ebf4f1c91a22707cd1a5d61dd1f93bccbd95。所有尝试、输入hash、原日志和早期制品保留，最终仅以artifacts/D1-20261018-E13/delivery为派发候选。没有native重建、依赖下载或设备操作。

主Maven锁与E11字节一致35坐标，7原native库与继承源/最终APK逐字节一致。fixture最终空Maven runtime锁，无kotlin定义/资源；其Debug APK仍含Android工具链生成的API/tool类，实际DEX清单另记，不能称全部字节都来自手写fixture。SBOM/NOTICE仍是受限Debug，闭源发行/模型/专利等门未准入。主app/test沿用原signer，fixture不同signer。

## 精确交付身份

'''
for a in apkAudit['apks']:text+=f"- {a['kind']}：{a['path']}；{a['bytes']}B；SHA256 `{a['sha256']}`；signer `{a['signer']}`\n"
text+=f"- host JAR：{rel(jar)}；{jar.stat().st_size}B；SHA256 `{pin(jar)['sha256']}`；{len(jarRows)}个production classes，无自检类。\n"
text+='''
四文档为DELIVERY、ARCHITECTURE_AND_THREAT_BOUNDARY、REMAINING_GATE_REVIEW、DEVICE_EXECUTION_APPENDIX；同包附RENDER_AUDIO_SOURCE_AND_KIT_DECISION具体设计。源码/差分/最终编译输入与日志/APK签名manifest审计/原registry自检输入副本/SBOM/设备只读计划随包。fixture签名键仅本机保管，不归档私钥；其hash在构建输入中，未来重建须相应本机签名环境或另发新candidate/pins，不能替换当前已审APK。

## 未执行与交接门

当前ADB/设备/真实媒体/新媒体输出/READY/新R/S全部0。原接受账本214483B/7R7S/0reserved与旧107218B前缀、产物/fence/oldCloseACK=false保持；只引用E11报告时点，不称本次在线确认。E11限定四方法PASS和E6B-OBS-F01跨host有限关闭保留；C13 self系统signal0严格FAIL、外部raw11/另一方法OS11、C14 NOT_RUN与ordinary UNKNOWN不回填。

renderer/audio/Kit是具体设计差距决定，显示/声音未运行、合法压缩音频→PCM仍BLOCKED；完整AAR/Fake/Flutter/后续P0不因本批通过。unexpected UNKNOWN保原group/host/Java/ADB/custodian并拒结束，停止交负责人，不注入永久UNKNOWN或造强制cleanup框架。三份独立现场metadata须tester派单前锁定，预算不够交BLOCKED，不运行中加次数。

请tester一次完整静态审本候选及F01–F04、原资源/源码身份/预算/依赖与冻结；负责人审后另派设备批次。长期设备授权已给，他项目占用等待，不重复向用户索权。当前停止进一步实现/构建/设备，等待集中结果。
'''
(R/'docs/coder/D1_E13_DELIVERY_V1.0.md').write_text(text,encoding='utf-8')
# Preserve final actual code and reports. Exclude local caches, class scratch, private key and the seal itself.
excluded={'build','.gradle','.checks','__pycache__'}
files=[p for p in B.rglob('*') if p.is_file() and not any(v in excluded for v in p.relative_to(B).parts) and p.suffix!='.p12' and p.name!='e13-freeze.json']
files += list((R/'docs/coder').glob('D1_E13_*.md'))+[R/'docs/milestones/D1_E13_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13_TESTER_REQUIREMENTS_V1.0.md',R/'docs/coder/e13_bootstrap.py']
names=sorted({rel(p) for p in files});archive=R/'docs/coder/D1-20261018-E13-source.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for name in names:z.write(R/name,name)
with zipfile.ZipFile(archive) as z:
 assert sorted(z.namelist())==names
 for name in names:assert z.read(name)==(R/name).read_bytes()
seal={'schema':1,'candidate':ID,'status':'FROZEN_E13_COMPLETE_IMPLEMENTATION_DEVICE_NOT_RUN','atUtc':datetime.now(timezone.utc).isoformat(),'archive':pin(archive),'immutableFiles':[pin(R/name) for name in names]+[pin(archive)],'sourceEntries':len(names),'priorSeals':oldVerified,'exclusions':['local caches/build intermediates/.checks','fixture-signing.p12 private local signing key','e13-freeze.json self','D1_E13_FINAL_READONLY_VERIFICATION_V1.0.json','post-freeze handoff/notification'],'deviceCalls':0,'realMediaProcessing':0,'actualScope':None,'actualOnce':None}
js(E/'e13-freeze.json',seal)
for row in seal['immutableFiles']:verify(row)
assert inherited()==oldVerified
for row in json.loads((E/'final-build-inputs.json').read_text())['files']:verify(row)
receipt={'schema':1,'status':'PASS_E13_FINAL_READONLY_VERIFICATION','atUtc':datetime.now(timezone.utc).isoformat(),'archive':pin(archive),'externalSeal':pin(E/'e13-freeze.json'),'archiveEntries':len(names),'immutableRows':len(seal['immutableFiles']),'priorSeals':oldVerified,'apks':apkAudit['apks'],'hostJar':pin(jar),'hostClasses':len(jarRows),'localGroups':7,'deploymentAssertions':45,'boundaryAssertions':22,'nativeLibraries':7,'mavenCoordinates':35,'fixtureRuntimeCoordinates':0,'deviceCalls':0,'actualScope':None,'actualOnce':None,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
js(R/'docs/coder/D1_E13_FINAL_READONLY_VERIFICATION_V1.0.json',receipt)
print(json.dumps(receipt,ensure_ascii=False))
