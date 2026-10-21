# D1 E11 final R1 平板部署与回归集中报告 V1.0

日期：2026-10-18。设备：HA1Q6WXR / Lenovo TB138FC / API31 / user0。批次：a129ad0a-9d93-49c6-8289-9087afd419ff。

**结论：PASS_E11_FINAL_R1_TABLET_AUTHORIZED_SCOPE。** 本批唯一保数据14→15部署，以及 MP4、AVI、能力拒绝、条件取消四个精确单方法均实际执行并独立审证通过。两份本批真实normal回执已形成；全部原客户端、Android任务及五个PC会话已正常归还，无PENDING/UNKNOWN遗留。原账档保持，新增消费按实际产物结算。本结论仅关闭本次部署和四方法范围；D1 NOT_PASSED、M0 NOT_STARTED、长期准入及其他P0/许可/历史FAIL与UNKNOWN保持。

## 授权、占用与绑定

负责人 VideoKit项目助理（01a107c3-2bf9-7fa0-94a0-234258ca6774）在用户明确“授权在项目开发测试过程中使用真机测试，无需再授权。”后派发本批。该消息及“如果有其他项目在使用真机测试，可以稍后再试。”已通过read_thread核实，原来源保存在 docs/tester/D1_E11_DEVICE_AUTHORITY_20261018.json。后续常规项目真机使用无需再问授权；具体方法、预算及未知状态门继续有效。

需求先保存于 docs/milestones/D1_E11_FINAL_R1_TABLET_TESTER_REQUIREMENTS_V1.0.md。接受的E11静态报告SHA cf905ea90b30899fdfe0724920d6f869c55c5a486c184879fbda83bd423a9e5f，终局补审报告SHA a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff。

本批初始及每个后续方法前有限一次检查占用；未发现活动instrumentation或相关在途进程。另一个活跃项目最近任务为Windows管理端开发，未据其历史“平板实测”摘要抢占设备；实际设备前置证据另存。不高频轮询、不并发其他设备项目、不中断他人任务；没有触发占用等待或稍后复查。

原registry的head6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5、5853B catalog SHA27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7及13个原文件保持。旧N2授权只用于读取原历史DAG，新安装/方法范围来自本次真实授权及独立scope，未挪用旧写许可。

| 本批实际输入 | SHA256 |
| --- | --- |
| scope，4286B | 76ea80a1fdc86103eb040c3f4ad0f82a041a317b80b2332369101b83d743b600 |
| 独立activation release，580B | 3ae21bc86bc6e45586f3f6580ec4f1c9f0b6fe81d3611c62d119f7ef627864c0 |
| 固定路径deploy config，1684B | bd57d662e654cc9eb8c33d6659f36bea78e037472337a5e3664682dd4eba12aa |
| 生产once记录，497B | 8b299373dcf381c92a8bdce3ca5ba3bd29287b33813ef75abdf28210715b2b11 |

scope/input-index绑定真实人类来源、受审制品、独立release及含dispatchRecord的config；没有随机hash充许可。唯一once路径在本批deployment/activation-deployment.once，位于原registry外，由scope和config采纳。记录状态RESERVED_OUTCOME_NOT_ASSUMED仅表示已消费派发，不代替部署成功或原close证明。

## 唯一部署与保数据核验

前置实测为精确E10A14 PREPARE来源pair、原UID10221/10222、原ceDataInode6972/4741、无相关在途；guard/fence、13不可变metadata、完整1011B账本、原107218消费/三R三S/0预留及三迁移记录均符合。fixture只预查stat，没有预读非零媒体payload或重传媒体。

使用最终R1 e11-host-tools-final.jar，SHA adb7b384ed305c925be7b2a670f33063e8d4309e085f1a6b7950f4b7125ebc27，未使用基础旧JAR。原生产入口先完成once CREATE_NEW/force/readback/原close门，再由原gate受管执行app/test install-r各一次，14→15保数据。部署原Java PID38576 / handle c64ad2fa-1811-49b2-aa17-27a01ccc2598，原exit0、两reader返回、唯一物理pcClosed allOriginalsReturned=true。未重装、降级、卸载、clear或人工force-stop。

安装后独立核精确pair、v15/D1-E11-ACTIVATION/ABI1、UID10221/10222、同签名及原数据目录inode、无相关进程，旧账档仍为107218/0reserved。目标app SHA2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48；test SHAe644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb；原证书SHA5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。

生产部署内部原命令由冻结监督器处理，成功固定路径为制品检查5、安装前当前检查7、install2、安装后检查7，共21个原process操作。顶层原stdout/stderr、真实exit/pcClosed、once及独立前后pair证据已保存；生产CLI没有逐个导出这21个内部stdout，本报告不补造其独立安装输出。

## 四项实际结果

每项均是新的独立Android instrumentation host，原@Before实际输出 FRESH_E9_OBSERVATION_ADMITTED，验证当前guard/fence、13metadata、完整账本接受前缀及合法结算后缀、无pending、精确三迁移记录和本host原holders归还后才继续。历史catalog和normal回执只提供受审来源与次序，不直接授实时grant。

| 精确方法 | 结果 | 原JUnit耗时 | host / codec PID | 原产物结果 |
| --- | --- | ---: | --- | --- |
| normalMp4SixRealFrames | PASS | 3.107s | 30191 / 30212 | READY，53567B |
| normalAviSixRealFrames | PASS | 7.175s | 30787 / 30809 | READY，53698B |
| capabilityDenialDoesNotOpenSource | PASS，预期拒绝 | 0.491s | 31264 / 31285 | PIPE_CAPABILITY_UNSUPPORTED，ABORTED 0B |
| cancelRejectsWrongEpochOversizeAndLateFrame | PASS，预期取消 | 0.867s | 31557 / 31576 | E4_CANCELLED，ABORTED 0B |

### MP4与AVI的严格normal门

两项均真实6帧接收、6输入、6输出sample；原validator为E6_NATIVE_OK / VERIFIED，packets6、decoded6、accepted6、demux_eof1、decoder_eof1、drain1。输出内容/thumbnail及PTS1000µs原严格实现门通过，未降低标准。MP4末PTS1000000µs，AVI末PTS1001000µs，AVI偏差为允许边界1000µs。

完整保存原接口给出的source/validator诊断。MP4最后source任务read_at_calls3/compressed_bytes196608；AVI最后source任务104/6815744，均在原每CPU8192reads/64MiB门内。该source诊断对应最后一个独立源任务，其他源任务由原框架硬门、6帧结果及实际归还证据约束，未伪造六份不存在的逐帧诊断。完整双EOF/drain指本次6帧输出的validator；按目标取帧的source诊断仍如实为EOF0/0。

各项原REMOTE_OWNERS显示liveResources0、unknownResources0、nativeCalls0、callbackInFlight0、callbackEntered=callbackReturned、callbackAckFailed=false、callbackUnknown=false，各encoder/sink/lease/frame均释放。原host为ACTUAL_OWNERS_RETURNED、originalOwnerReturned=true、ownerFinishEntries1、controlInFlight0。原JUnit released()实际断言slot0、retainedSessions0、callbackRejected0及主线程响应；未把未打印的断言值伪装成新增日志字段。

每个normal实测6个source隔离CPU任务及1个validator任务，其独立原出生与系统isolated not needed结束均已核；最后source/validator task与原native诊断准确绑定。原host与codec正常finished inst后PID缺席。两项均在原PC55秒与原方法/启动/协商预算内返回，未扩门限。

### 本批两份真实normal回执

MP4独立接受、原PC自然关闭及回执形成后才启动AVI；两项报告和outputTask不同，同本批scope/actualpair/v15/ACTIVATION/catalog/batch。capability与cancel实际携带这两份canonical回执及其连接hash，未使用旧prepare或模拟回执。

| 回执对象 | 实际值 |
| --- | --- |
| MP4 outputTask | acb10ab9-b26c-42b3-b04a-d27417c868fd |
| MP4报告SHA | 971ec78faa9466dfab3fa9472a53a163bd0b2fed1f7e7d328796aa9320128a7f |
| MP4回执SHA | e9a240576d719a7a635ed64c595a848fa40b8705d007dcdf9eb7d39303858255 |
| AVI outputTask | 5b78515c-1699-4374-be66-8b8a367a6dec |
| AVI报告SHA | fae02cadcf51a8e373f6b96ef579fe264e85e158c7d478c9696fcadf52f406a4 |
| AVI回执SHA | 77b48db910d92752c60962a7d19d24b172ebdbd442195c41e6e9db84c7b150fc |

### 能力与取消门

能力拒绝的生产CountingProvider opens/bytes/reads均0，由原精确JUnit方法断言验证；原source/validator诊断NOT_STARTED，独立系统记录没有启动本项隔离CPU，0帧、0B、无READY，资源全返。fixture自身完整hash自检与生产broker计数分开，不据broker0声称fixture没有被验证读取。

能力项独立接受并自然收尾后才选择取消项。取消原方法对错误epoch、147457B超尺寸的E4_FRAME_LAYOUT、取消后迟到帧的E4_FRAME_TASK_NOT_ACTIVE拒绝均实际断言通过。首次取消175694520093288ns，原截止175724520093288ns，差值准确30秒；无READY、0输入/输出，实际source CPU正常归还结束，原host/codec/资源及PC正常返回。拒绝细节由原已冻结方法实际断言证明，不伪造额外逐拒绝日志。两个新增ABORTED 0B为本次受审负向方法的合法结算，没有重做原N2 ABORT。

## 最终账本与旧档守恒

旧budget730a73e1-50e1-4198-a515-047104f00e31、fence662e9ecd-bede-42e6-bb58-ce81d668ff44保持。原owner64522:20304:10221/0B、lease64522:20385:10221/36B及13metadata原字节hash保持。原0B/S0、53651B、53567B三产物stat身份/大小及原三笔结算完全保持；原107218/三R三S的1011B接受前缀SHA仍为f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba。

| 本批新增outputTask | 状态 | 字节 | SHA256 |
| --- | --- | ---: | --- |
| acb10ab9-b26c-42b3-b04a-d27417c868fd | READY | 53567 | 9bfc3de9879578d88329542ff269a554954c24972202f5f147ea4fd019a0ea83 |
| 5b78515c-1699-4374-be66-8b8a367a6dec | READY | 53698 | b66d9ec0335c9cc1bb3d42d68ca88687e03b0ecc72ae62b3d387ce5ffd4dcd10 |
| 64507c9c-a650-462f-9af7-bc2bf32b1f5a | ABORTED | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| 0e3dcbcc-d7db-451e-ad17-00b95c3c04a1 | ABORTED | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

最终完整ledger2271B、7R/7S、7任务、消费214483B、预留0；增量107265B，剩余累计容量3979821B。完整链及唯一R/S独立从最后原raw解码重算，原前缀不截断、不重写、无pending。

最终ledger SHA e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649；链尾0eadfcd645c9ea796ba13b813c02e1604c128ef619683f1f6f2bb76b68a96a75。每任务2MiB全额预留、总4MiB/128任务门保持，未清账或换budget。原迁移三控制文件及原终局registry13文件保持只读，未追加release/events/head或重SEAL。oldCloseACK=false及历史出生/信号UNKNOWN未回填。

## 原资源、日志与统一账本

四方法各通过已冻结生产E9PcSupervisor监督一个55秒/1MiB原instrumentation客户端。测试侧小型Java适配器只负责精确方法参数、原raw转存与独立Android结束审证后的PC收尾，不修改候选、Android实现或框架，不用普通外部超时杀任务。原客户端Process/stdin/stdout/stderr均真实返回；独立系统结束与原资源审证通过后才接受本scope固定finish证明，原监督器再自然关闭。

| 项目 | 本批实际/结算 | 上限与说明 |
| --- | --- | --- |
| 独立metadata客户端 | 40，均exit0/两pipe返回 | 分配40，不按阶段清零；无UNKNOWN |
| 部署原process操作 | 成功固定路径21 | 不冒称有逐个导出的最终OP快照；保守记账24 |
| 原PC entry | 部署1+四方法4 | 各自然exit0、两reader返回、共5个唯一物理pcClosed |
| 四方法原instrument客户端 | 4，均SUCCEEDED/allReturned | 每项55秒，单原输出≤1MiB |
| 测试侧host适配器编译 | 1 | 仅本批适配器，无Gradle/APK重构建 |
| 全批统一process记账 | 保守74/96，余22；成功路径推导71 | 含metadata、部署/方法entry、原child和适配器编译 |
| PC STATUS/OP/CLEANUP连接查询 | 0/16；总accepted socket0/128 | 四个进程内status快照不伪作连接查询 |
| 原系统日志累计 | 787585B/1048576B | 首项完整buffer；后续从方法启动前设备时钟起保留完整窗口，无clear、条数截尾或伪拼接 |
| 隔离CPU正常结束 | 15 | MP4 7、AVI 7、能力0、取消1，均有原系统证据 |
| host/codec正常结束 | 4对 | 每项原finished inst与独立PID缺席证据 |

原60秒方法、12秒协商、15秒启动、首次cancel30秒、每CPU64MiB/8192reads、三次输出hash6MiB、48owner等门保持。没有额外operator输出payload hash、媒体重传或全量扫描；原方法自己的fixture验证沿用受审实现。

测试侧出现一次Windows长路径兼容问题：最后metadata原client已成功返回，保存派生副本时路径过长，后继审证因此暂未完成。原错误、控制器快照及40份原回执保留，仅将本机派生文件改为短名并显式映射原路径，复用同三份成功回执恢复审证；未新增ADB/取消用例重跑，兼容修正1/2。其后的独立最终文件审计一次通过。

自动审批曾将Python控制台收尾输入误作Java接口格式而拒绝，首次拒绝未送达。核实原接收进程、固定转发路径和证明SHA后，在原同一接口安全执行并自然关闭；没有绕路传输、换进程或重复Android动作。其余方法使用完整固定路径/SHA收尾参数。全部拒绝/核查/实际归还记录保留，无剩余阻塞动作。

## 限定关闭范围与停止状态

本次实测关闭：准确14→15保数据部署、当前host真实观察后准入、两项严格normal、双真实normal回执先后门、能力源不开启及条件取消协议收尾这几个已派范围。没有选择旧迁移、整类、close-unproven、self-kill、native-segv、actor2/3或额外故障，也没有人工kill/force-stop/restart/换port/强制close/未知重跑。

NOT_RUN：长期回归、Android/native UNKNOWN故障注入、普通发送者权限负例、其他播放器/字幕/声音人工体验、独立Kit/Flutter/多平台/正式分发及全部其他P0许可验收。当前正常退出场景通过不宣称未知结束钩子的故障实测已完成。D1整体未过、M0未启、长期准入及历史FAIL/UNKNOWN和原oldCloseACK=false保持。

四项完成后已停止，不因剩余额度自动扩展测试。

## 证据索引

批次根：docs/tester/D1_E11_FINAL_R1_TABLET_EXECUTION/a129ad0a-9d93-49c6-8289-9087afd419ff。

- inputs：原scope、实际release、固定once配置和单向input-index；deployment：生产once原文件。
- cases/每个精确方法：原instrumentation全文、原PC stdout/stderr/实际exit/两reader归还、独立preclose审证、实际系统结束证明及accepted-case-report；两个normal目录另有canonical normal-receipt.json。
- evidence/command-resource-ledger.json：SHA1dc8bd07ca301cff2f72adcf54450f53aed2f9c98045fc461025396ce69384e4。
- evidence/independent-final-audit.json：SHA98bcd84c6368ad1b98e506b81d251eddc1c69a99a92817880dc305705f50c31c。
- evidence/evidence-manifest.json：SHA1fa5e8ca632952fc2056a2973c4c43b10361c1d3660ef583cdd4ad8755e92c56；固定原文件集合，排除自身、后生成报告与通知回执。
- harness：受管客户端适配器源码/编译输入/实际class及只读最终审证脚本；evidence含全部原metadata argv/stdout/stderr/hash/exit/pipe归还、长路径修正和审批拒绝解决记录。

本报告完成后主动发送负责人并保存通知回执，无中间小功能交接。
