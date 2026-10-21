"""Generate E5B complete review documents from final artifacts. Explicitly retain the OS symlink gap."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];BASE='docs/coder/d1e5b/'
def load(n):return json.loads((B/'evidence'/n).read_text())
def link(p,label):return '['+label+']('+str(R/p).replace('\\','/')+')'
def main():
 if (B/'evidence/e5b-freeze.json').exists():raise ValueError('FROZEN')
 audit=load('apk-audit.json');jvm=load('local-check-results.json');build=load('build-results.json');external=load('external-readonly-verification.json');assert all(x['status']=='PASS' for x in [audit,jvm,build,external])
 apkrows='\n'.join('| '+x['role']+' | '+str(x['bytes'])+' | `'+x['sha256']+'` | '+link(x['path'],'APK')+' |' for x in audit['apks']);cert=audit['apks'][0]['signerCertificateSha256'];snapshot=hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()
 delivery=f"""# D1 E5B 完整候选交付 V1.0

2026-10-17。D1-20261017-E5B，新根docs/coder/d1e5b。实现与本机支持场景、离线构建已完成，提交整包静态复审；**真正文件符号链接反例仍为OS权限阻断、NOT_RUN，不将本包说成全部要求已验证。** Android fstat/flock/设备/QUERY/ABORT/观察/真实媒体均未运行。D1未通过、M0未启动、全部P0/JNI与N2/旧signal FAIL保持。

## 修复范围

依据 {link('docs/milestones/D1_E5B_CODER_REQUIREMENTS_V1.0.md','E5B需求')} 和 {link('docs/tester/D1_E5A_ARCHITECTURE_REVIEW_REPORT_V1.0.md','E5A复审')} 修E5A-F01/P1。观察与恢复只能调用existingGuard；现存owner/lease使用非创建、NOFOLLOW打开，核实际FD普通文件/UID、owner0B/lease36B与准确fence，path与FD的dev/inode在锁前后及使用/关闭前复核。恢复前像增加82B guard.identity，观察须与实际打开句柄匹配，拒绝事前同字节替代文件。

同时修当前输出任务的原lease重开：初始化owner与首次issue lease仅走独立createNew/O_EXCL接口；workerLeaseClear、READY与abort走openExisting，沿用已捕获身份/epoch。abort先取得既有正确原锁，再写journal，缺失不补或改journal。移除没有调用者的MODE_CREATE旧锁工厂；WorkerLease继续只接已授权PFD，不按路径创建。

相关核账也改为既有READ/WRITE/NOFOLLOW FileChannel；只有全新预算初始化可CREATE_NEW，不再使用可能创建缺失ledger的RandomAccessFile("rw")。旧R/S字节格式、累计实际消费、未知关闭、跨host默认拒与原绝对截止规则保持；没有借缺失或链接清账、换UUID或补元数据。

## 定点证据与明确缺口

最终JVM repair-003通过82项父检查，子进程内部断言另保日志不叠加。16种观察夹具包含健康、missing-owner/lease、两个目录角色、owner1B、lease0/35/37B、错误36B fence、两个同字节替代inode、两个Junction重解析点、缺guard.identity与替代身份记录。直接走生产观察，拒绝项逐原路径/角色/volume-fileID/字节清单不变、无新R/S/live grant，创建接口调用数0；替代身份用实际打开FileChannel的Windows内核句柄属性核验，非仅路径布尔值。

另有直接生产恢复missing-owner/missing-lease两项、正常新任务的两次合法创建/后续非创建重开、缺lease时worker-clear/READY/abort不补写、一个completion-close UNKNOWN及新host明确观察对照、原首次30秒/计时回调迟到定点回归。不重跑旧270项；E5A的Admission/Lifecycle/CallbackGate/DirectoryBarrier逐字节保持，原证据仅引用。

Windows真实句柄核验使用本机JBR的GetFileInformationByHandle包装及volume/fileIndex，模块反射开关仅用于本机工具；UID映射与目录FD替身是模型，不能当Android UID/fstat/flock或目录fsync实测。两个Junction是实际重解析节点，**不是实际文件SymbolicLink**。

普通及提升执行创建真正文件符号链接均失败WinError1314；当前token无该权限，WSL亦不可用，未安装环境或改系统设置。Junction普通沙箱受限，获准在新自有目录运行后通过。{link(BASE+'evidence/environment-gate.json','环境门')}。所有前次失败日志保留：main为拒绝前未获锁的fence校验重复导致过度保留，修正后repair-001遇Junction沙箱权限；repair-002支持场景通过；补相关路径后repair-003为最终82项。

已备 {link(BASE+'tools/invoke_true_symlink_once.ps1','固定源码单次真正符号链接补验脚本')}，默认INSPECT，只有明确Run、一次ExecutionId和精确freeze SHA才运行；仅在docs/coder/E5B_SYMBOLICLINK_ONCE的新目录编译/生成自有夹具，将原guard移到本夹具旁再建真正文件符号链接，确保目标仍为原inode，执行同一生产观察并核不创建/不改原字节/无R/S/grant。它不提升权限、不改系统设置、不接设备或媒体；现有权限环境才可由负责人准确派发。该脚本本批未执行，缺口不自动关闭。

## 构建、签名与来源

offline Gradle main-001一次通过，公共Android Os.open/lstat/fstat/pread/pwrite/fcntlInt API编译通过；没有Gradle并发、下载、安装或新fault。最终build输入SHA256 `{snapshot}`。

| 角色 | 字节 | SHA-256 | 文件 |
|---|---:|---|---|
{apkrows}

两包证书SHA256 `{cert}` 与E5A/E5/E4A一致；appIdcom.videokit.app / test、versionCode4/D1-E5B、原两非导出服务/权限，无INTERNET/companion。35 Maven坐标、七native字节差异0，Media3 1.9.3/FFmpeg8.0.3及完整C14对应源码/NOTICE许可映射保留，不宣称许可、安全或发布放行。

{link(BASE+'evidence/local-check-results.json','定点JVM结果')}；{link(BASE+'evidence/build-results.json','构建')}；{link(BASE+'evidence/final-build-inputs.json','最终输入')}；{link(BASE+'evidence/apk-audit.json','签名/Manifest/native审计')}；{link(BASE+'evidence/original-open-audit.json','所有相关原打开调用审计')}；{link(BASE+'evidence/preserved-invariants.json','未回退组件')}；{link(BASE+'evidence/sbom-difference.json','SBOM差异')}。

完整 {link(BASE+'artifacts/D1-20261017-E5B/D1-20261017-E5B-source.zip','源码ZIP')} 包含最终源/工具、必要旧来源摘要、新定点日志/自有夹具、四文档与完整C14对应源；没有重复复制E5A的2243项自检产物，无密钥/local.properties/build/classes/缓存/真实媒体。双APK独立immutable。{link(BASE+'evidence/e5b-freeze.json','外freeze')}绑定精确成员；ZIP和freeze自身SHA在集中交接外列，避免循环。只读复核：Python -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1e5b/tools/e5_package.py verify。

直接基线E5A2247项与native来源E4A207项共2454 immutable只读核验，旧seal一致。旧候选/工具/报告/设备fixture/缓存/预算/失败现场未改。本次仅提交审查，符号链接实测缺口须单列；不自动派发部署、QUERY、恢复或产品回归。
"""
 architecture="""# D1 E5B 原资源打开与架构边界 V1.0

2026-10-17。处理E5A-F01，不回退旧E5-F01/F02静态支持。保持压缩解析普通isolated CPU、同UID codec故障边界、真实六帧/isolated EOF/PTS/缩略图、flags与实际STARTED ACK及trace。:e4_codec不是权限/RCE沙箱；独立Kit/Flutter/P0不因此完成。

## 专用现存与全新创建入口

E5BGuard.existing只调用IO.openExistingNoFollow；Android为O_RDWR|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK，明确没有O_CREAT/O_TRUNC。正常新owner/lease只能经E5BGuard.createNew，Android另用O_CREAT|O_EXCL|O_NOFOLLOW、0600，不能复用孤立旧文件。不存在“exists成功后MODE_CREATE”的回退。旧AndroidLease.exclusiveInto工厂无调用者后已移除；仅增现有JNI的注册PFD lock/unlock桥，不改native二进制。

Guard在任何open前注册，描述符结构先存raw，再存dup，再设置dup FD_CLOEXEC。fstat核实际raw；JNI flock在共享同一open-file-description的dup上，因此身份属于实际被锁对象。close逐实际unlock/dup.close/raw.close尝试并存状态，任何未知不重试，原资源保持可达。尚未取得锁的准入失败不重复作关闭前fence校验，实际FD正常关闭可如实归还，但操作失败不授予资格。

## 句柄角色与身份

现存入口先lstat NOFOLLOW核普通文件/预期UID/长度，再非创建打开。对实际打开FD fstat核同角色，dev/inode/UID须与打开前路径和指定历史身份一致；锁前后verify重做fstat、lstat和fence读取。owner必须0B，lease必须36B且实际FD读取最多37B与准确UUID逐字节相同。非普通节点、符号链接、错误长度/fence/UID、缺失、替代inode或路径/句柄不一致均拒绝。

O_NONBLOCK避免路径类型竞态变为FIFO等时无界阻塞；类型仍必须fstat普通文件，未读取不合角色的数据。fence只写已锁的lease原FD，前后复核身份/长度/epoch，不通过路径重新打开写。任何身份变化或真实close失败不得成为live proof。

恢复在实际取得旧N2 owner/lease且未修改前，把两原FD的dev/inode/UID写成82B guard.identity，绑定原task。旧N2 lease仍须准确原epoch；记录不允许来自caller布尔或随意替代文件。之后fence、S前和关闭前复核原guards。观察读记录和已ABORTED journal当前fence，再取得指定原身份的两existing guards，元数据前后均核记录不变；文件同字节但inode不同也拒绝。旧E5A无此记录的部分恢复状态不能倒填，必须BLOCKED另审。

## 全部相关消费者

原N2恢复、最终观察、当前E4FencedTask.workerLeaseClear/READY/abort都走existing。新任务initialize owner及首次issue lease才走createNew；记录lease身份后不再创建原锁。abort把现存lease成功获取移到任何ABORT_PENDING journal修改之前，避免缺lease还改原journal。WorkerLease接已授权PFD并核epoch，本来不按路径创建。正常transfer打开是READ_ONLY/WRITE_ONLY，无CREATE。原input/输出哈希、before/anchor/complete读取加NOFOLLOW；新metadata仍明确CREATE_NEW。

还移除“现存ledger RandomAccessFile rw可补建”的路径。恢复及预算已有ledger使用READ/WRITE/NOFOLLOW FileChannel和原实际FileLock；只有全新预算初始化单独CREATE_NEW，原header/R/S/哈希链/累计消费和实际force/close保持。缺失/链接不补文件，不换账户或目录。

## 原准入、收尾与证据边界

E5AAdmission固定N2预算新host默认拒绝、完成文件不提供许可，E5ALifecycle原owner/CONTROL真实归还或首次30秒绝对截止仍保持。源码与E5A逐字节核验；仅跑定点close UNKNOWN/新host观察与late-deadline，不重新执行全部历史模型。新guard身份失败不会让预算R/S或live grant出现；正常健康现存资源仍可通过当前真实返回资格后reserve。

观察现有文件force从14增为15（新增guard.identity），两次metadata读回仍有界；guard record82B、owner record≤256B、proof≤2048B、ledger≤128KiB、输出hash≤2MiB，无递归设备扫描。恢复holder仍≤32，观察≤48，另保预算校验holder与目录barrier≤16。原R/S/失败产物、guard文件和前像保留。

本机用真实Windows FileChannel句柄，经本机JBR内核属性包装读volume/fileIndex绑定，而非文件名布尔；Windows范围锁是本机替身，不是Android flock。UID映射与目录FD替身是模型。两个实际Junction代表重解析拒绝，但不等真正文件SymbolicLink；当前普通/提升环境均Win1314，因此真实符号链接本地证据NOT_RUN。Android public API已离线编译，真实Android symlink/fstat/flock及掉电语义仍未执行，不能外推。
"""
 gates="""# D1 E5B 剩余门禁 V1.0

2026-10-17。源修复与可用本机证据完成，等待独立静态复审；不将支持场景PASS说成全部E5B要求已实测。旧E5A REQUEST_CHANGES/N2 FAIL和全部历史结果保持。

| 门禁 | 当前证据 | 尚未满足 |
|---|---|---|
| 原锁不得创建 | 恢复/观察/当前任务重开全部existing，Android无CREATE/NOFOLLOW，定点缺失/角色/长度/fence/身份无修改无R/S/grant | 独立复审与真实Android fd/flock后测 |
| 实际句柄身份 | Windows真实打开句柄volume/fileIndex，替代同字节inode拒绝；Android fstat/lstat public API编译 | 非Android UID/内核实测 |
| 真正文件符号链接反例 | 当前OS1314，两种权限上下文均拒绝创建；Junction重解析模型通过 | **NOT_RUN，不能关闭**；须另定点授权已有权限环境运行单次脚本 |
| 旧跨host尾部UNKNOWN | Byte-identical Admission，定点completion-close未知/newhost直接生产观察对照 | 旧8场景仅引用不叠加；Android恢复未执行 |
| 原失败终局/绝对截止 | Byte-identical Lifecycle，定点原owner/重复cancel/迟到计时资格拒绝 | Android Handler/Binder/仪器结束后测 |
| 实际六帧/isolated EOF/PTS/缩略图 | 门保持，无绕过 | 未执行正常MP4/AVI及后续能力/cancel |
| Media3/FFmpeg/native/许可 | 无新依赖，35坐标/7native差异0，完整对应源保留 | 不关闭漏洞、许可、发布P0 |

不以符号链接API代码存在、普通目录拒绝、Junction通过、路径exists或新文件锁成功代替真正符号链接实测。已提供精确freeze绑定/一次ID/仅新自有目录的补验脚本，默认INSPECT；没有获得OS特权，不改系统设置，不自动运行。负责人可保管并决定准确补验安排，本包无该项成功回执。

所有新host原N2许可仍要求明确当前观察与实际资源归还，缺guard.identity/原锁/元数据、错误身份、链接或新pending都BLOCKED。旧E5A半恢复不得补记录或重复S；后续正常新pending不由原N2工具清理。不清marker/失败输出、不换UUID/目录、不卸载清数据、不扩等待求通过。

本批ADB/设备/真实媒体stat-read-hash/安装/QUERY/ABORT/观察/新nativefault/下载为0。D1 NOT_PASSED、M0 NOT_STARTED、全部P0/JNI和N2/旧signal FAIL保持。完整复审与必要补验通过后再准确分段派发实际计划。
"""
 appendix="""# D1 E5B 执行与补验附录 V1.0

2026-10-17。仅计划，不是安装/设备/恢复许可。所有旧冻结、N2现场、fixture和失败产物保留。实现可审、本机支持项通过，但真正文件符号链接本地反例因Windows1314尚未执行；须在审查中单列，不偷偷用Junction替代。

## 一、可选单次本机补验（尚未执行）

脚本为D:/CodexProjects/VideoKit/docs/coder/d1e5b/tools/invoke_true_symlink_once.ps1，默认不执行。只有负责人明确派发、当前已有OS文件符号链接权限、给定一次ExecutionId及精确E5B freeze SHA后才用-Run。脚本不自行提升、不更改DeveloperMode/安全策略、无ADB/Gradle/设备/真实媒体。

输出固定在D:/CodexProjects/VideoKit/docs/coder/E5B_SYMBOLICLINK_ONCE/<ExecutionId>新目录，同ID存在即拒绝；核freeze和每个JVM源输入SHA，再用现有JDK编译同一生产Guard/Recovery/Observation代码。分别生成owner和lease自有假夹具，把原guard移动到本夹具相邻目标，真正SymbolicLink指回该原inode。这样错误地跟随会看到相同原身份/字节；正确NOFOLLOW必须拒绝。读取Get-Item.LinkType强制SymbolicLink，不能Junction代替。直接生产观察须无新文件/原字节/ID修改、无R/S/live grant，保存原日志；四个JVM实际exit0及两真LinkType才生成独立receipt.json。

普通与提升执行当前均1314，故本窗口未运行这份脚本。执行计划/一次ID可在外部freeze确定后由负责人保管；它不等OS权限，也不意味着设备恢复获准。失败无PASS回执，未用ID不能自动重派，禁止以改系统设置绕过本批范围。

## 二、实际设备阶段（均待另派）

完整静态复审与必要补验→同签名保数据部署versionCode4/D1-E5B→原N2只读QUERY→独立审阅→另派ABORT→独立结算审→当前host实际最终观察→正常MP4→正常AVI→能力拒绝→条件取消。每个正常instrumentation新host都须在fixture读取/Session创建前做明确本次观察；独立报告/完成文件/旧host资格不跨进程生效。

原appIdcom.videokit.app、UID10221、budget730a73e1-50e1-4198-a515-047104f00e31、task86cafdb3-0fc4-447d-920b-b19c884bf494、epoch5131975343750146374/gen1、service775a5ee9-fff3-4340-a03b-97751099c0c4、旧host24853/codec24873和原fixture不变。原R/marker/WRITING保留至另派合法ABORT的全部实际门成立；不卸载/清数据/换UUID/清失败输出或旧cache。

恢复仅选com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort，固定e5N2Task、e5N2Budget如上，e5RecoveryBatch=D1-E5B-N2-RECOVERY-20261017。动作默认QUERY；另派分别ABORT_ORIGINAL_N2或OBSERVE_SETTLED_N2。观察另需e5aSettlementReceiptSha256关联真实独立结算报告。QUERY不锁/fence/hash输出/写S，不创建guard.identity，不可据此直接运行ABORT/编码。

ABORT使用专用非创建NOFOLLOW原guards，实际owner0B/lease36B、fence/UID/devinode核验，保存82B guard.identity及原四份前像和writer身份后才修改。原S按真实保留输出消费，原closeACK=false；所有真实返回后才本host准入。观察必须有该精确记录和实际writer死亡，不能替旧E5A半状态补记录。原文件缺失、角色/链接/身份变动、记录不足或任何close/sync未知均BLOCKED，无创建/补文件/R/S/grant。

正常只选E4DeviceTests的normalMp4SixRealFrames→normalAviSixRealFrames→capabilityDenialDoesNotOpenSource→cancelRejectsWrongEpochOversizeAndLateFrame，e4Case精确单方法，e4Batch=D1-E4A-E5B-NORMAL-TABLET-20261017、e4BudgetIdentity=原budget；每项需e5aObservation=REVIEWED_ORIGINAL_N2_SETTLEMENT、e5aSettlementReceiptSha256=真实独立结算报告SHA。cancel另需e4NormalReceiptSha256=真实两正常独立报告SHA。receipt语法不是授权，实际FD/记录/当前观察资格必须成立。

不运行整类、三个quarantine、旧Binder、新fault、手机或其他平台；任一观察BLOCKED或产品FAIL/PENDING即停止后续，保存原结果再集中报负责人。不循环重试、不延长60秒产品/12秒协商/15秒STARTED或首次30秒取消。原source/真实六帧/isolated EOF/PTS/缩略图门保持。

## 三、取证与结束门

保留原identity/journal/R/S/marker、guard.identity与真实句柄lstat/fstat dev/inode/UID/类型/长度/fence、锁前后与关闭前校验、原PID退出reason/status/时间、实际PFD/raw/目录FD返回。路径存在或取得新文件锁不等原资源证明；FileChannel/kernel句柄与路径、历史记录都要匹配。

正负/cancel/await异常/close/@After仍共用原owner终局或首次30秒截止。记录terminalReason/phase、原cancelAt/deadline、ownerFinishEntries/originalOwnerReturned、callback/native/Image/CONTROL及预算在途。原计时派发迟到或原资源迟到可如实更新raw计数，但不能取得窗口内ACTUAL_OWNERS_RETURNED资格或把原失败改READY。系统结束仪器不补closeACK。D1未通过/M0未启动/P0与全部历史FAIL保持。
"""
 for name,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',gates),('DEVICE_EXECUTION_APPENDIX',appendix)]:
  with (R/('docs/coder/D1_E5B_'+name+'_V1.0.md')).open('x',encoding='utf-8',newline='\n') as f:f.write(text)
 print(json.dumps(dict(documents=4,trueFileSymlink='NOT_RUN_OS_PRIVILEGE_1314',deviceCalls=0)))
if __name__=='__main__':main()
