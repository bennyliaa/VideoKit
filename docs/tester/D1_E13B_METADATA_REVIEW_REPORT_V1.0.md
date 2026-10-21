# D1 E13B 元数据覆盖包独立复审报告 V1.0

日期：2026-10-18。依据：`docs/milestones/D1_E13B_TESTER_REQUIREMENTS_V1.0.md`。本包D1-20261018-E13B-METADATA覆盖三份metadata；产品仍为冻结E13A v17 / ACTIVATION / ABI1，真实接受来源仍为v15。

## 结论

**复审通过，未发现新的准入阻断项。E13A-F01/P1在受支持查询、静态解析及本机已记录证据范围关闭；支持负责人正式派发准确范围的六方法设备批次。** 当前不是设备执行，也未生成真实scope、release或once，Android六方法仍全部NOT_RUN。

原E13绑定P1及只读入口P2关闭范围保留，不重开、不外推为真机通过。本批无ADB/设备、构建、产品用例、候选测试重跑、remote脚本或媒体payload执行。只运行tester独立字节/原记录审计及已读源码确认纯读的verify/help，未执行pack、生成器、shell reader/collector或本机候选套件。

D1 NOT_PASSED，M0 NOT_STARTED；原214483B、7R/7S、reserved=0、旧107218B前缀/产物/fence/oldCloseACK=false继续按E11接受时点引用，未在线重新确认或写账。此次通过只消除元数据计划的静态阻断，不关闭后端/音频/独立Kit等产品门。

## 完整性及来源核验

证据目录：`docs/tester/D1_E13B_REVIEW_EVIDENCE/`。独立脚本`audit_e13b.py`及`independent-audit.json`共**1721项文件/成员/pins/预算/已记录输出一致性检查通过**，不是1721个功能用例。

| 对象 | 独立结果 |
|---|---|
| 外seal | `e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e` 一致 |
| ZIP | `557327a5e7bd28cf73e21ccee3a9131e02a0495e1e303942500593e02f0bca96`；118条封印、117个唯一成员逐字节一致 |
| 五份旧封印 | E11基础375/R1 65、E12 46、E13 367、E13A 270条及各seal均未变 |
| 基础制品 | 四份E13A三APK/JAR实际字节/哈希一致；原JAR172个production class集合及字节一致 |
| 原metadata基线 | 除新增instrumentationEvidence外，expected-baseline全部原字段与E13A一致；34stat/18control及完整2271B ledger pins保留 |
| 独立只读入口 | 默认、显式verify独立seal pin、help、pack-help均exit0；182份审查集合前后字节一致 |

开发方176份快照与tester182份是不同选取集合，不互相替代；独立审计同时核验完整封印及旧文件。没有为了原误调用重跑产品或打包旧包。

## 唯一原阻断的修复

实际三argv的INSTRUMENTATION记录已统一替换为无包过滤`dumpsys activity processes`，每客户端只查询一次；实际.sh中逐字节嵌入同一`processes_reader.sh`及collector。旧unsupported入口和awk运行依赖均不在最终脚本中；包内旧awk原型只是未部署参考。

API31输出在已知进程及isolated列表后输出活动instrumentation，再进入OOM及后续状态；这个顺序支持在同一完整流中保留整个活动块。[AOSP ProcessList固定标签原文](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ProcessList.java)。活动对象包含多行class、running、target、arguments及未缩进权限字段，FINISHED标记本身不等于已从全局列表移除。[AOSP ActiveInstrumentation固定标签原文](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActiveInstrumentation.java)。

本次核源码确认：

- 必须唯一完整首行、All known processes、OOM、最后非空mForceBackgroundCheck尾标记，以及唯一原命令exit=0。缺活动标题不能单独产生IDLE，缺头尾/阶段不符/诊断即使exit0也BLOCKED。
- 直接保留活动标题到OOM之前的所有原行，包含全部index、跨行target/arguments、未缩进字段和仍在列表中的FINISHED项；不按包名丢弃其他项目。IDLE只描述一次完整instrumentation快照，不代表总体设备空闲或SourceReleased。
- collector在原命令结束后追加其真实退出状态，解析同一条pipe，不由管道右侧成功掩盖左侧失败。解析遇错后继续排空同一原流，不提前关pipe冒充归还。
- ACTIVE完整记录输出后退出73/ENVIRONMENT_WAIT，阻止当前M的后续字段、部署和方法；异常/unsupported/缺段退出21，输出过限可退出22。ACTIVE部分M不能当完整预检PASS，BLOCKED不因文本小或脚本exit0变为空闲。
- 内部扫描界限为524288B/8192行/单行4096B、活动块3000B；超限拒绝，不截断宣称完整。PC留存的该记录仍≤4096B，客户端≤65536B/55秒；内部扫描是元数据文本，不是媒体payload或新增PC文本额度。

裁定：**E13A-F01=CLOSED_STATIC_METADATA_CONTRACT**。这是静态命令/格式及已记录本机证据的关闭；没有声称现场API31/OEM当前输出刚取得或六方法已跑。

## 本机证据边界

已独立读核20份语义分支的输入/stdout/stderr pins及记录退出值。四份历史E11厂商raw与原文件/参考副本逐字节相同；用于Linux shell解析的输入按行结束处理并附原exit标记，不将处理后的输入冒充新的设备原raw。

其余活动/多个对象/FINISHED/跨行，以及unsupported、非零返回、缺头尾、未知OOM、重复头、尾后诊断、空活动标题、缺字段和过限等均是明确标记的构造变异。本机ACTIVE输出与对应输入的完整活动块逐行比较一致，未丢续行或其他对象。

32份语法核对记录仅为语法；四份实际嵌入collector的平台替身记录分别为IDLE→0继续、ACTIVE→73且停止、unsupported即使原exit0→21、原命令非零→21。后两类和ACTIVE均未继续后续metadata。它们验证本机有限读取/控制逻辑，不是设备活动实测；tester未重跑这些分支。

没有新增控制、安全、权限或强制清理模型。未知仍由既有原Process/pipe/custodian保持，不因本机读取结束宣称Android资源归还。

## M1–M3精确pins与预算

路径均为`docs/coder/d1e13b/release/metadata/`。独立核验三份完整argv为同一个直接`adb.exe -s HA1Q6WXR shell sh -c`客户端，最后一个参数解引号后与相应.sh逐字节一致，无PC wrapper/push或额外探路。

| 文件 | 字节 | SHA256 |
|---|---:|---|
| three-client-manifest.json | 136231 | `223e0d42a045fce01df8c4564945221276fbe78120fa7dad60641a10a2985af5` |
| expected-baseline.json | 15508 | `7f7d32f6b52f027c615a2aab5bb5f79d464bd924d8052c48e27e2a11ba346544` |
| M1_PRE_DEPLOY.sh | 21038 | `c87fd9d07da88d1821536732eaa28aec2cdaf27a1ba779de9fadf75dd7393160` |
| M1_PRE_DEPLOY.argv.json | 54939 | `b447ab2476eac04b8a07d4decaae6cbfdc9f7abd29f7dbe744582c8e101cafae` |
| M2_POST_DEPLOY_PRE_CASE.sh | 8422 | `755fc6a102af55223ff173053bd3828daeed8e57702376504fe2a32bba6cc60a` |
| M2_POST_DEPLOY_PRE_CASE.argv.json | 20772 | `4c0f0c10325ee37030971eb65dab720a8caeeec476d211e67cb7a9309dd15fbf` |
| M3_AFTER_SIX.sh | 21353 | `0b9b28a5357a081f838337063bb804e679b6615b572c812591db4799af9b5a13` |
| M3_AFTER_SIX.argv.json | 55823 | `70735a6c2aa31f128ae6ed4e4e68879280b20e8fa952246ffd3fc8d6e04ec020` |

记录数/含标签上界独立重算为M1 70/53512B、M2 18/27588B、M3 71/56360B，单份均在64KiB内。Windows完整命令行UTF16含NUL分别23993、9899、24460单位，均低于32767；此项是主机传参静态尺寸核验，不等于设备已执行。

M1仍核设备/用户/占用、v15源pair/UID/原data、fixture不存在与旧账档；M2核v17目标pair/fixture实际独立UID、原data及无在途；M3核原账档/产物不变及关联原结束证据。完整ledger固定2271B、SHA `e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649`；新四旧产物stat沿acceptedStat，无虚造inode。非零媒体只stat，18control完整小字节核pins。实际字段未知/不匹配仍应停止，不能只接受脚本exit0。

PC48=部署entry1+内部32+六entry6+六instrument6+metadata3；文本1638400B+余458752B=2MiB，三metadata留存预算196608B。无额外Java/Python进程、socket STATUS/OP/CLEANUP查询或免费重查。**48是一次成功路径的分配，不含重试余量。** 若ACTIVE消耗了一次M1，稍后复查同样入总账；不足以完成后续时须负责人重新分配或修订准确范围，不能自动补第49次或清零消费。

M1前既有controller独占/他项目占用证据仍必要；占用不明就等待，不能以instrumentation IDLE单独认定设备可用。55秒只是原响应界限，未知不强杀、不换进程/UUID，不把部分M当完整成功。

## 基础制品复用及设备准入范围

`release/overlay-binding.json`为2185B，SHA `e7087d22b9065c68bab6ae7599457d0ddf2bb795bfb28c54a845df34a573e28f`。精确复用E13A delivery：

| 制品 | SHA256 |
|---|---|
| app-debug.apk | `962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad` |
| app-debug-androidTest.apk | `83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13` |
| fixture-debug.apk | `868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8` |
| e13a-host-tools.jar | `a0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f` |

原E13A完整审查和签名/35依赖/7native结论保留，实际哈希未变，无理由为本元数据修正重编或重测产品。实际升级仍v15→17/ACTIVATION/ABI1、原signer/UID10221/10222/data inode6972/4741，batch `D1-E13A-SOURCE-20261018`及新固定`e13a-activation-deployment.once`不变。v16未安装，不作为来源。

支持正式派单后按原顺序，每方法一次、独立host：

1. ordinarySenderCannotBindCodec：真实普通不同签名UID kernel拒绝、授权host HELLO、原三binding归还；不冒内部Binder调用。
2. authorizedHostSourceReadAndClose：原生产门授权open/read/close。
3. oldGenerationNeverOpensSource：同生产门当前代真读，再旧task/epoch/instance零增量拒绝。
4. twoConsumersHoldSourceUntilLastReturn：同源双consumer，首退不使第二个失效，最后真实聚合归还。
5. cancelLateOpenRetainsOriginalOwner：取消响应与原open/原handle close归还分栏。
6. lateReadAndCloseFailureDoNotReleaseEarly：迟到read不采纳、明确失败close按同ticket允许规则处理，未归还保keeper。

源仍为4096B非媒体定义、五host共20KiB准备、合计实际计划4224B read/6open/7close；上限read64KiB/open8/close16，且每ticket initial+最多两次明确失败后重试、pending不重叠。原await5000ms、方法30秒只资格，无编码/validator/新输出/READY/R/S。

正式设备派单应以不可变测试材料和sourceReview链绑定本覆盖包seal/ZIP/manifest/三个argv及上述原制品，沿原受审运行schema，不修改基础冻结。准确scope/config/release与新once路径由负责人正式派发，不能把草案或随机digest当许可。任一FAIL/BLOCKED/PENDING/UNKNOWN停止后继并保原holder；不得因静态通过重跑信号、永久UNKNOWN/OOM/重启或整类旧normal。

## 剩余状态与停止

长期真机授权有效，正式范围内无需向用户重复索权；本批停在复审，等待负责人具体设备派单。原P1/P2仅保持各自静态/本机关闭范围，Android普通UID/原dispatcher及六方法尚未实测。

E11限定四方法PASS、E6B跨host有限关闭、C13系统signal0严格FAIL/外部raw11/另方法OS11、C14 NOT_RUN、ordinary UNKNOWN及全部P0保持。renderer/audio/Kit仍SUPPORTED_DESIGN_ONLY，真实显示声音NOT_RUN、合法PCM接续BLOCKED，独立AAR/Fake/Flutter/许可/长期门未过。D1 NOT_PASSED / M0 NOT_STARTED。

报告主动发负责人；本轮不自动执行设备或进入后续阶段。通知回执另存证据目录，发送后报告字节不变。
