# D1 E9B READ_ONLY_IDENTITY 真机测试报告 V1.0

2026-10-18；tester；依据 [本批测试需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E9B_READ_ONLY_IDENTITY_TESTER_REQUIREMENTS_V1.0.md)。实际设备阶段08:45–08:51，随后仅整理本地证据。

**结论：PASS_FINITE_REAL_DEVICE_READ_ONLY_IDENTITY。** HA1Q6WXR实际完成一次受管更新、单actor显式只读身份、非等待启动后的独立存活、完整权限保护广播状态、原身份资源返回、原字节归档、唯一精确结束ACK、系统正常finish与PC原资源自然归还。无UNKNOWN、无重试、无强退或测试夹具清理。

通过范围仅为这次Android只读身份/控制正常快路径。D1 NOT_PASSED、M0 NOT_STARTED、E6B-OBS-F01长期准入OPEN；原产品回归、真实迁移和activation没有执行或获得本报告许可。本批已结束，不自动进入后续测试。

## 1. 授权、准确scope与产物

本窗口用户永久授权使用平板，用户2026-10-18继续推进项目，负责人「VideoKit项目助理」在接受E9B独立复审后正式派发本次单批。执行前已保存需求、实际只读scope、config/canonical命令及SHA台账。实际scope明确禁止RESERVE/EXECUTE_COMMIT/SEAL_FINAL、媒体、正常产品、actor2/3、旧ABORT或预算变更；scope文件SHA只是绑定真实派发范围，不是写迁移批准token。

| 标识 | 本批实际值 |
| --- | --- |
| 平板 | HA1Q6WXR / Lenovo TB138FC / API31 / user0 |
| 应用身份 | com.videokit.app UID10221；com.videokit.app.test UID10222 |
| Registry | `b1d2b533-2461-4a85-ad05-d64509a6b1f9` |
| 生产协议scope字段migration | `eed3bd1d-7f52-47a4-bd66-992f5b8937f1`；本次仅作只读身份scope，未执行迁移 |
| Actor | ordinal1；attempt `fa4e3689-90dc-4bef-b565-fb602863d97f` |
| 原handle | `8419402b-16a0-45a0-92fe-d1ec7019848c` |
| 受审config SHA256 | `085d9d0e01f4e7910c19ca752b9292878015e231a4b827ad8d836a7ca23966a5` |
| 受审prepare-plan SHA256 | `909d2803628fc6358f5b6a1c0088b88bc96cd40a7f0e74df42e8f5b0854dc9ac` |
| 静态复审来源 | E9B报告SHA256 `03cae4e6313db391ea0838bc289814b97a1319bd98ac6d08e30f2a4df1fa5fb1` |

配置environment=DEVICE_HA1Q6WXR，无SYNTHETIC_LOCAL代入。字段严格采用生产managerTrust/preparePlan schema；authorization绑定实际只读scope文件及其需求来源，review/sourceReview绑定已完成的E9B复审。生产首次登记的descriptor与执行前已存descriptor逐字节一致，没有填造identity或终局catalog。源文本换行归一化摘要与原冻结文件摘要在独立审计中分别标明，不将归一化值冒充原文件SHA。

最终制品均在启动前重新核精确字节摘要，生产部署门另核角色/ABI/签名、现场pair/UID/版本、无相关进程及安装后精确pair：

| 制品 | 本批SHA256 |
| --- | --- |
| version13 E9B PREPARE app | `ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020` |
| androidTest | `2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b` |
| 生产host JAR | `4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707` |
| 原签名证书 | `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f` |

沿用协议批标签D1-E9A-PREPARE-TABLET-20261018，实际包版本为13，没有为改标签重编。E9B外seal核验一致，未构建或修改冻结候选。

## 2. 现场预检与唯一受管更新

现场设备存在；current user=0。安装前实际base.apk摘要分别为 `78ec2d3b057b91736ea0bf273ab6bf1b1028dae97916052b5ddb235087d84baf`、`5a97f705813dfbe6f1476d9409c6448a7de981ea77420f2733890691a2248646`，精确对应已核E7A version10双包及原证书来源。两包user0 installed=true/hidden=false/suspended=false/enabled=0，原UID10221/10222；原相关应用进程不存在。

调用生产DEPLOY_PREPARE一次；固定app/test两条install-r各一次，无卸载、clear、降级或重复安装。生产部署任务返回成功后INSPECT完成；监督者显示21个原操作全已返、nonqualified=0、liveProcesses=0。21包括5个本机制品审计工具与16个ADB客户端；安装前后精确pair核验是生产门内实际执行，不以高version/相同证书字样替代完整字节门。

结束后另作一次包/进程元数据核验：app versionCode13、test versionCode0、原UID及启用状态保持，app ceDataInode6972、test ceDataInode4741与安装前一致，无相关应用进程。证明原数据目录身份保留；未逐文件重新扫描历史账本、媒体或全部档案。

## 3. 实际只读身份与完整广播状态

08:49:05，唯一LAUNCH已返回，明确mode=READ_ONLY_IDENTITY、ordinal1、bootKind=SYSTEM_BOOT_COUNT。实际命令am instrument -r，不带-w；生产管理器独立保留Android Remote责任，不用启动客户端退出代替actor结束。

08:49:12，唯一POLL发送STATUS seq1/state=-1；经DUMP保护ordered broadcast取得完整transport，生产原5秒响应任务完成语法、result、模式/UID、actor/request/PID/handle/seq与回退校验。原回执：

| 项 | 实际结果 |
| --- | --- |
| PID / UID / process | 17434 / 10221 / com.videokit.app |
| 环境与boot来源 | DEVICE_HA1Q6WXR / SYSTEM_BOOT_COUNT / boot=2 |
| 原进程start | 16410590 |
| identityNanos | 39316667，约39.3ms，低于10秒资格界 |
| verdict / phase | IDENTITY_QUALIFIED / IDENTITY |
| 原holder / 未归还 | owned=2 / unreturned=0 |
| 原资源安全状态 | safe=true，reason=NO_WRITE_INGRESS_CLOSED |
| 写入状态 | executeReserved=false、executeDone=false、device/deviceRecord=ABSENT |
| 请求计数 | commandSeq1 / requests1 / statuses1 / finishClaimed=false |

随后独立读取实际ps、系统boot_count和/proc/17434/stat，确认原PID在启动客户端返回后仍独立存活，UID和进程名相符，boot=2及start=16410590与回执完全一致。原身份操作早已返回，而actor继续受管等待归档ACK；等待期间没有延长仍在途资源的资格钟。

原actor canonical字节SHA256 `356a1684dfcad37bdb6c08903c8f3e2960fd97d6f54d2dad19f05a6b472ce3e3`。原identity return为384B，SHA256 `79fe97e999acc561e691b91589baf7eb6213c5106ca0dd18cf90b81a56c979bd`；snapshot、actor与return互相绑定，严格指向本scope。

原2个/proc身份读取holder的资格由本次实际生产E4Owned close返回门与原回执共同证明。没有单独采集每个FD数字或系统调用trace，不将源码推断冒充另外执行的内核故障测试。

## 4. 精确归档、唯一ACK、正常Android finish

08:49:58完成ARCHIVE_RETURN；本地原384B return与生产registry actors/0001/returned.json逐字节/摘要一致。原identify记录及只读事件已持久化，无reserve、COMMIT、device控制文件或actor2。

08:50:16唯一ACK_FINISH，commandSeq2，精确原handle/state及已归档return hash。ACK回复仍绑定同一actor和同一原return，safe=true、finishClaimed=true、requests2/statuses1，未重发或因未知回复更换seq。finishClaimed本身不作为最终完成证明。

08:50:25生产CAPTURE_FINISH独立检查原PID缺席、系统原日志及唯一锚点，并记录NORMAL_FINISH_CONFIRMED。原日志 [actor-0001.finish.log](D:/CodexProjects/VideoKit/docs/tester/D1_E9B_READ_ONLY_IDENTITY_EVIDENCE/external-registry/logs/actor-0001.finish.log:5398) 在5398行包含准确本handle/actor hash/return hash的唯一E9_FINAL_FINISH；紧随其后的5399/5400行记录user0 finished inst和Killing 17434 ... finished inst。原日志754722B，SHA256 `d81c06023d79f916f528c1f3da6bbb1a889917862da3c942a7907dbff93e36ab`。

这些Force stopping/Killing是ActivityManager对正常finished inst的系统记录，本批未发送force-stop/kill命令。随后独立ps再次确认本批原PID及相关应用进程缺席，不能只用一次客户端exit或磁盘完成文件代证。

本scope只有两条外部事件：IDENTITY_ONLY_RETURN_NO_COMMIT → NORMAL_FINISH_CONFIRMED；parent/evidence摘要独立重算一致。该只读事件链不是写迁移final H_actor，没有checkpoint/final catalog/seal/activation release，也不能拿来授COMMIT或复用为actor2恢复资格。

## 5. PC原资源、控制预算与完整收尾

原PC管理者handle `5ee53215-c4d4-4437-9db9-fd3f2c12c495`，PID27924，原loopback端口14691，同一个非daemon custodian贯穿本批。使用的都是冻结生产JAR，不是本机测试夹具。

最终一次本机查询显示26个原生产操作、unreturnedOperations=0、liveProcesses=0、nonqualifiedOperations=0、unresolvedActors=0；registryReturned=true、registryOwned=0。26=21部署制品/安装门+1非等待启动+1STATUS+1ACK+2独立finish证据客户端，与准确已执行阶段相符。

查询回复中的allOriginalsReturned=false包含正在处理该次STATUS的本机Socket原holder，不是遗留Android或业务资源；没有据此补查询或忽略其关闭。随后正常关闭管理器输入，原custodian等待本机accepted holder及listener实际返回后记录唯一E9_PC_CLOSED与allOriginalsReturned=true。main和共用entry boundary回报的是同一pcClosed ACK，不是两次结束操作。

08:50:49原Java管理器自然exit0，controller实际stdout/stderr reader均返回，终端会话也自然完成；没有隔离ACK、未返任务或残留custodian。独立进程检查未再发现原PID27924。原资源最后是在正常路径真返，未采用任何测试controller terminate/destroy、取消future或手动关未知holder。

| 项目 | 实际使用 / 上限 |
| --- | --- |
| Android控制 | 2 / 8：STATUS seq1、ACK_FINISH seq2 |
| STATUS | 1 / 3 |
| ACK / actor启动 / 安装 | ACK1；actor1；app/test install-r各1 |
| 本机STATUS/OP/CLEANUP连接 | 2 / 16；无OP/CLEANUP，原128总额未重置 |
| 生产Process操作 | 26 / 96；全部合格实际返回 |
| 外部registry元数据 | 8文件 / 20；5606B / 155648B（同时低于192KiB） |
| 原系统日志 | 754722B / 1MiB |
| 主机只读兼容修正 / 未知重试 | 0 / 2；未知重试0 |
| 设备媒体内容读写/导出、产品/迁移/ABORT | 均0 |

实际16个独立元数据ADB客户端均exit0且管道返回，最长0.125s。生产管理器另执行21个ADB客户端；合计37个，包含2次安装、1次启动、2条控制及元数据/finish证据。本机2次查询不是Android STATUS，不计入那1次STATUS；16次独立元数据也不是本机端点16次查询额度。

生产子进程分解由冻结port流程、21/26实际操作计数和本批阶段账相互核对；没有为每个生产子进程另加argv/stdout跟踪器。原广播完整transport、原回执、命令文件/seq账、原系统日志和入口/退出日志均保存，不能把未单独保存的中间工具原stdout说成已采集。

## 6. 证据、未执行项和停止边界

证据目录：[D1_E9B_READ_ONLY_IDENTITY_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E9B_READ_ONLY_IDENTITY_EVIDENCE)。主要文件：

- [independent-device-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_E9B_READ_ONLY_IDENTITY_EVIDENCE/independent-device-audit.json)：34项独立证据检查全通过，身份、归档、事件链、normal finish、预算与真实收尾。
- [command-resource-ledger.json](D:/CodexProjects/VideoKit/docs/tester/D1_E9B_READ_ONLY_IDENTITY_EVIDENCE/command-resource-ledger.json)：准确scope/config/命令SHA、Android seq与本机请求/原资源账，inFlight=[]。
- 原transport/actor/identity return/snapshot、manager原始stdout/stderr、外部registry、现场前后元数据与各客户端回执、evidence-manifest.json。

以下均NOT_RUN：普通app发送者的DUMP权限负例、KERNEL_BOOT_ID分支、超时/断连/Exception/Error/UNKNOWN故障、真实raw/dup系统调用trace、128端点耗尽、完整registry恢复/actor2、COMMIT/迁移、activation、新host当前guard/ledger观察、正常产品/媒体/native fault。E9/E9A/E9B本地有限故障证据仍维持原范围，不因为本次正常快路径通过就升级为Android故障实测通过。

安装保留原数据目录身份；只读actor仅查询包、Settings boot_count与自身/proc身份，没有触碰原N2 guard、fence、账本或档案。原budget `730a73e1-50e1-4198-a515-047104f00e31`、107218/三R三S/reserved0、原ABORTED0B/S0、fence `662e9ecd-bede-42e6-bb58-ce81d668ff44`、oldCloseACK=false及旧根因UNKNOWN作为历史已接受事实保留；本批未额外扫描它们，不能因此关闭长期准入。

本批没有生成写迁移批准token、final H_actor/catalog、激活包或新权限。Framework/独立Kit/Flutter、严格六帧/完整EOF/1000us、原预算与许可/P0不变。后续任何写迁移或新host实际观察需负责人另定准确scope和准入，本批不自动转入。报告冻结后主动发送负责人并另存通知回执。
