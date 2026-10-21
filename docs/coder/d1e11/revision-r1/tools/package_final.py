"""Final E11-R1 source bundle: sealed E11 base + host-only override. No Gradle/device operations."""
import argparse,datetime,hashlib,json,pathlib,zipfile,subprocess
B=pathlib.Path(__file__).resolve().parents[1];BASE=B.parent;R=B.parents[3];J=pathlib.Path('D:/Android/Android Studio/jbr/bin/java.exe');DOCS=[R/f'docs/coder/D1_E11_R1_{x}_V1.0.md' for x in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(p):raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=sha(raw))
def read(p):return json.loads(p.read_bytes())
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def text(p,s):
 with p.open('x',encoding='utf-8') as f:f.write(s.strip()+'\n')
def check(x):assert row(R/x['path'])==x,x['path']
def base_verify():
 seal=BASE/'evidence/e11-freeze.json';assert sha(seal.read_bytes())=='fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5';d=read(seal)
 for x in d['immutableFiles']:check(x)
 original=read(BASE/'evidence/original-registry-before-export.json')
 for x in original['files']:check(x)
 return d
def prepare():
 assert not (B/'evidence/e11-final-freeze.json').exists();base=base_verify();h=read(B/'evidence/host-revision-results.json');assert h['status']=='PASS';binding=read(BASE/'release/candidate-binding.json');binding['hostJar']=h['artifact'];binding['revision']='E11-R1_FINAL_HOST';binding['requiredDeploymentConfigField']='dispatchRecord';binding['originalBaseSeal']=row(BASE/'evidence/e11-freeze.json');save(B/'release/candidate-binding-final.json',binding)
 trust=read(BASE/'source-export/activation-trust.json')['fields'];trust['dispatchRecord']='REQUIRED_APPROVED_ABSOLUTE_EXECUTION_PATH/activation-deployment.once';save(B/'release/activation-trust-deploy.template.json',dict(templateOnly=True,state='NOT_APPROVED_NOT_EXECUTABLE',wireFields=trust,rule='Canonical config SHA binds this one permanent outside-registry path. Parent must already exist. Same config copied elsewhere still names same record; changing path requires a different reviewed/approved config.'))
 logs=B/'evidence/host-default';logs.mkdir(exist_ok=False);commands=[]
 for name in ['E9HostActivationSession','E9HostManager','E9PcClient']:
  args=[str(J),'-cp',str(R/h['artifact']['path']),'com.videokit.spike.e4.'+name];p=subprocess.run(args,capture_output=True,timeout=10);assert p.returncode==0 and b'INSPECT_ONLY' in p.stdout;(logs/(name+'.stdout.txt')).write_bytes(p.stdout);(logs/(name+'.stderr.txt')).write_bytes(p.stderr);commands.append(dict(argv=args,exitCode=p.returncode))
 host=(B/'tools/E9HostActivationSession.java').read_text();assert 'config.exact("kind","plan","planSha","authorization","review","registryPath","head","dispatchRecord")' in host;assert host.index('once.record(')<host.index('E9HostDeployment.Processes processes=');assert 'oncePath.startsWith(originalRoot)' in host
 save(B/'evidence/final-review.json',dict(schema=1,status='PASS',baseImmutableVerified=375,apkBuildsTotal=1,extraApkBuilds=0,baseAndroidInputsByteIdentical=True,hostOnlyOverride=['E9HostActivationSession','E11DeploymentOnce'],hostJar=h['artifact'],classes=h['productionClasses'],crossProcessTestInvocations=8,configPathDigestBound=True,missingDispatchRecordRejectsBeforeDevice=True,authorityRegisteredBeforeOpen=True,originalRegistryUnchanged=True,unknownCloseNotAck=True,sourceOrderStaticChecks=True,defaultCommands=commands,deviceCalls=0,actualApprovedRelease=None,independentReview='PENDING'))
 text(DOCS[0],f'''# E11 最终交付修订 R1

本修订是E11最终主机执行包，替代初始E11主机JAR/部署配置规则；初始375 immutable、其完整源ZIP、四文档和已签v15 APK原样保留。完整产品候选实现与证据详见初始四文档；本四文档给出最终覆盖规则，不是新的设备许可。状态 BUILT_NOT_DEPLOYED_PENDING_INDEPENDENT_REVIEW。

复核发现：移出原registry的detached release如果只用进程内install counter，弱于原CREATE_NEW跨进程防重放。因此补最小host-only E11DeploymentOnce；不改Android源码/APK、不再构建。原一次离线APK构建总数仍1。新JAR由已封E11生产JAR逐项继承，替换E9HostActivationSession并增Once/IO/Cut三class，共{h['productionClasses']}生产classes；没有OnceCheck测试类。实际JAR {h['artifact']['bytes']}B，SHA{h['artifact']['sha256']}。

部署配置必须精确包含dispatchRecord绝对路径，它在canonical config SHA内固定，不在任意CLI附加参数或可换目录的release旁猜路径。文件名固定activation-deployment.once、原父目录预存在、无symlink、不得落在原final registry内；helper不新建目录。新配置不含record的内容/hash，record反向引用config/release/head/catalog，单向无自指。旧base JAR不接受带新字段的配置，新final JAR不接受缺该字段的部署配置，避免误用旧工具。只读export仍兼容原7字段配置，不消费记录。

在任何安装调用前，原supervisor先强持有once原holder，CREATE_NEW→写精确意图→force(true)→readback→原close真正返回，全部成功才进入原部署gate。记录表示RESERVED_OUTCOME_NOT_ASSUMED，不是批准、安装完成或资源回执。已存在（包括部分）一律拒，不清理重建；换JVM/复制同一config/release仍指同一路径。FileAlreadyExists竞态确知无open可安全结束拒绝；其他open/force/close未知继续原keeper，不假归还/第二close。文件force/readback沿用原主机Store语义，不新增断电硬件持久性承诺。

8次合成本机JVM检查通过：首次/新JVM重放、两个并发、force失败/新JVM重放、close UNKNOWN保持原custodian/另JVM仍拒重放。无真实安装器/ADB；UNKNOWN专用夹具最后由控制器有限收尾，originalCloseAck=false，不是原安全退出。首次已知force失败并已close可结束失败，但记录仍消费，不能重试。原13文件未改。

原E11的12组154断言/13次本机调用、14个SDK公开门断言、真实5853B catalog导出/四事件DAG和单次APK签名审计均完整继承，无旧套件重跑。真实catalog27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7/head6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5、source role ACTIVATION/ABI1/版本15及当前observer/runner安全门不变。

app SHA2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48；test SHAe644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb，原证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。7native/35坐标/原框架严格六帧EOF1000us/P0/Kit/Flutter不变。

最终source bundle包含完整已封E11 base ZIP和本host修订源码/JAR/输入日志/绑定/本四文档；先解base再使用本最终hostJAR及新配置，不修改base封存项。release/candidate-binding-final替代旧host引用，sourceReview/新部署scope/current proof/两个normal receipt仍空。没有实际device/媒体/激活/播放/迁移或actor2；原107218/三R三S/全部产物/oldCloseACKfalse保留，D1未过M0未启长期准入OPEN。
''')
 text(DOCS[1],'''# E11-R1 最终架构边界

继承E11 source-pinned真实catalog→每host当前guard/fence/完整合法ledger/无pending/实际原holder返回→进程内epoch grant链；历史catalog、测试选择或normal receipt不代替live proof。原6帧/fullEOF/1000us/生命周期门未改，Android runner/UNKNOWN finish仍未实机验证。

部署链改为：新的人类明确授权+真正接受的E11 source/release→新canonical deployment config（内含固定dispatchRecord）和其原SHA→原同JVM supervisor持有独立once原holder→CREATE_NEW/force/readback/真close→原精确APK/source/ABI/UID/idle/升版/同签名两install-r门→原Process/pipe真实归还。原final registry只读，不追加release/events/head。持久一次记录替代原registry CREATE_NEW闩锁，不能只凭进程内计数；未知不能换JVM/同config换路径重试。

记录只在未来新E11执行目录，≤4096B；配置pin绑定唯一绝对路径，既存父目录，不在旧registry内。没有新secret/密钥/远端根/审批bool，原N2授权只是历史DAG来源，不能授权新安装。若人为换路径，就是改变配置SHA，需要新的明确审定范围，不能作为自动恢复。记录无完成/close声明，力求只保留原先的一次派发强度；不声称SHA可认证人类批准或抵抗root/恶意同UID/自洽回滚。

E4Owned mutable IO在open前登记；并发FileAlreadyExists明确无FD，其他UNKNOWN/在途原对象保留。已知业务失败真返只允许失败安全结束，不授准入。force之后close未知也不能安装；marker存在使另一进程拒绝。原supervisor/96操作/128accept/5s控制55s一般响应、无强停取消、不可重放语义保持。文件force不额外证明Windows目录项在任意掉电模型下的持久性。
''')
 text(DOCS[2],'''# E11-R1 剩余门

R1仅补主机跨进程一次闩锁，已通过8次本机合成JVM检查和来源/JAR验证；不是设备安装、故障注入或批准签发。初始E11已封375项完整继承，原E10A463及终局13原文件保持；Android输入166项与已构建v15精确一致，没有第二次Gradle构建。

独立tester须审原E11全部候选及本R1覆盖规则，尤其新配置字段绑定、原holder强持有、关闭未知不派发/不重试、初始未带闩锁JAR不可作为最终部署工具。最终sourceReview及设备派单目前未给，candidate-binding仍为draft。原用户暂停设备激活/播放限制保留，恢复开发不代表解除。

当前NOT_RUN：安装14→15、真机当前观察、MP4/AVI/能力/cancel、Android runner未知结束钩子、内核raw/dup故障、普通发送者权限负例、长期回归。两个真实normal receipt没有生成。P0许可、Framework/独立Kit/Flutter/长期准入OPEN、D1 NOT_PASSED/M0 NOT_STARTED均不因签名APK或本机模拟通过解除。

原107218/三R三S/0reserved、0B/S0/53651/53567、fence/档案/oldCloseACKfalse不改。不清账、删记录、reset预算、强停未知或创建actor2。未来合法normal输出可在受审预算内追加R/S，不修改旧前缀或承诺新总消费仍107218。
''')
 text(DOCS[3],'''# E11-R1 最终未来设备附录

当前NOT_AUTHORIZED/NOT_RUN。沿用初始E11设备附录完整的14→15同签名保数据→每新host当前观察→MP4→AVI→能力→条件cancel顺序及两个normal receipt绑定要求，本附录覆盖部署配置/最终host工具规则；其余没有放宽。不得用初始base host JAR执行最终部署。

正式独立接受本候选、取得新的人类具体安装/测试许可后，负责人在新执行批目录记录真实scope及当时有效release/sourceReview。release绑定同一实际v15 APK SHA，无APK自指；原N2写scope和旧E3许可不能挪用。使用最终e11-host-tools-final.jar，不能使用初始375快照中的旧JAR。

activation-trust-deploy.template必须去除模板外壳并按E9 canonical规则生成新配置，除原历史plan/planSha/authorization/review/registryPath/head/kind外，必须含dispatchRecord绝对路径。该路径在新受控E11执行目录中，文件名activation-deployment.once，父目录事先存在，不能位于原final registry或symlink路径。真实config SHA包含路径；copy配置到别处不能选择新记录，换路径属于新的配置/审定，不允许自动重试。

未来仍采用--approved-deploy <new config> <config SHA> <real approved detached release> <release SHA> <app> <test>逐项argv。工具在任何install前先持久化一次意图，只有force/readback/原close全真返后才做原artifact/source/ABI/installed14/idle门及两install-r。记录即使只部分、force失败、close未知或后续preflight/安装失败，也不删除、覆盖或换JVM重试；保全原记录/Process/Store/keeper和未知，集中另审。marker是已预留未知结果，不证明批准/安装完成/资源归还。若配置缺dispatchRecord，会在设备调用前拒绝；旧base工具亦不接受新8字段配置。

安装后真实核exact新pair/UID/15/ACTIVATION/ABI1、原数据目录inode及旧账档保留。每新host当前观察与原holders真返才grant；BLOCKED/UNKNOWN不得跑媒体。MP4正常独立接受后才AVI；两份本scope/同actual pair/15/catalog/batch的不同report和outputTask回执，READY/6帧/fullEOF/PTS1000us/owners returned均有原证据，能力和条件cancel才可选择；e4NormalReceiptSha256仍为两canonical回执连接的hash，不是开发模拟或第三报告。外部独立核来源，APK选择器不是审批机关，自己的@Before仍实际观察。

仍限4MiB总量/2MiB单任务全额预留/128任务、原96PC操作/128accept/≤16受审查询、5秒控制/55秒一般响应、1MiB原输出/日志、48holders。余量不足/未知/不返/来源不同（含已经15）停止，不reset、不重复安装、不强停。按实际已批范围集中报告后停止，不额外故障/actor2/normal回归。当前未产生once正式派发记录、批准release、device current proof或normal receipts。
''')
 print('PASS final R1 draft bindings, four complete override documents and static review')
def freeze():
 base=base_verify();assert read(B/'evidence/final-review.json')['status']=='PASS';files=sorted([p for folder in ['tools','evidence','release'] for p in (B/folder).rglob('*') if p.is_file()]+[B/'e11-host-tools-final.jar']+DOCS+[BASE/'evidence/e11-freeze.json',R/base['archive']['path']]);save(B/'evidence/source-manifest.json',dict(schema=1,kind='E11_FINAL_R1_BASE_PLUS_HOST_OVERRIDE',files=[row(p) for p in files]));files.append(B/'evidence/source-manifest.json');archive=R/'docs/coder/D1-20261018-E11-final-source.zip'
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 save(B/'evidence/e11-final-freeze.json',dict(schema=1,status='FROZEN_E11_FINAL_R1_NOT_DEPLOYED',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=row(archive),baseSeal=row(BASE/'evidence/e11-freeze.json'),immutableFiles=[row(p) for p in files]+[row(archive)],baseImmutableItems=375,apkBuildsTotal=1,deviceCalls=0,approvedRelease=None,normalReceipts=None));verify()
def verify():
 d=read(B/'evidence/e11-final-freeze.json');base_verify()
 for x in d['immutableFiles']:check(x)
 expected={x['path']:x for x in d['immutableFiles'] if x['path']!=d['archive']['path']}
 with zipfile.ZipFile(R/d['archive']['path']) as z:
  assert set(z.namelist())==set(expected)
  for name,x in expected.items():raw=z.read(name);assert len(raw)==x['bytes'] and sha(raw)==x['sha256']
 print(json.dumps(dict(status='PASS_READ_ONLY',seal=row(B/'evidence/e11-final-freeze.json'),archive=d['archive'],finalImmutableVerified=len(d['immutableFiles']),baseImmutableVerified=375,mutation=False,deviceCalls=0)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare','freeze','verify']);a=p.parse_args();globals()[a.operation]()
