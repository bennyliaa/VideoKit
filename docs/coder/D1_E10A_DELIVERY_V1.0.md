# D1 E10A 最小实现与执行包交付 V1.0

P1 BOUND未EXEC取消收尾和P2终局/已归档后STOP已集中实现，12组受影响本机有限检查通过；状态 CODER_FIXED_FINITE_LOCAL_PENDING_INDEPENDENT_REVIEW。执行包仍PREPARATION_ONLY_NOT_EXECUTABLE，未来scope/实际新身份/现场值均未生成，不能使用原E10 BLOCKED报告当准入。D1未过、M0未启、长期准入OPEN。

## 实现

Registry复用并严格校验已存合格identify及reserve，不再CREATE_NEW覆盖identify；同actor（完整canonical含birth）、同plan/authorization/reserve/最后BOUND head、实际磁盘events与原内存连续链一致、命令同handle连续seq、无任何EXEC/ACK意图、确有唯一STOP、当前原回执PENDING/EXTERNAL_STOP/IDENTITY/executeDone=false/0未返且原identity时间及owned一致，才归档新取消return。原合格identify/reserve保持逐字节，追加BOUND_IDENTITY_CANCELLED_NO_COMMIT，不改旧记录。原Android STOP的PENDING本已永久sticky，不能再bindAndReserve；原registry命令门额外拒STOP后EXEC或第二STOP。没有新取消wire或通用取消框架。该IDENTITY结局永远不是final/actor2的COMMIT资格。

HostManager共用公开prepareControl在intent/seq/wire之前拒已归档return、实际已知safe COMMIT终局、此前STOP/finish后的STOP；Registry也在append前拒归档后STOP及STOP重放/后继EXEC。ACK当前proof与原已归档字节比较移到写ACK意图前。重复归档先拒，不让CREATE_NEW失败毒化Store。真正已发的EXEC/ACK意图仍单次不可重放；IO close/force UNKNOWN与PC失败规则保留，不把前置拒绝变成资格恢复。生产operation失败后仍failed，只能经原scope/CLEANUP白名单收尾，不能SEAL_FINAL。

## 验证与边界

12组通过，383边界断言、222共享合成夹具断言。真实生产Registry/Run、与原host CLI实际共用的prepareControl、原ProcessBuilder/5秒decoder、真实console错误退出和原custodian→精确ACK/normalfinish路径参与。平台身份/控制/System normalfinish为SYNTHETIC替身，不是获批DEVICE CLI或Android故障/内核实测。旧19/32/24/native未重跑。

targeted-001只在测试callback checked Exception处编译失败，无执行；原源码和原日志保留。targeted-002通过11组；console-003仅新增一组实际console拒绝→custodial ACK并增加raw合并子进程输出日志，未重复旧11组；两次所有生产class字节一致。002保留每次child argv、canonical frame及原测试JVM stdout/stderr，未另存每次child raw stdout；003额外原样保存它。EXEC_INTENT_ISOLATION在真实Registry先记EXEC意图、故意不投wire，然后直接原Run.stop生成真实取消proof，证明后者仍不能抹去先前意图；不声称host会合法发那条错位控制。UNKNOWN_COMMIT_CLOSE与该意图隔离两组均保留原责任，有限观察后控制器只终止专用夹具JVM且所有真实child已返，originalCloseAck=false；不算生产安全退出。正向分支经原console/entry及自然JVM退出收尾。

|组|边界断言|结束边界|
|---|---:|---|
|BOUND_CANCEL|40|原资源已返/正常结束|
|BOUND_NOT_STOPPED|42|原资源已返/正常结束|
|BOUND_WRONG_ACTOR|41|原资源已返/正常结束|
|BOUND_WRONG_RESERVE|42|原资源已返/正常结束|
|BOUND_WRONG_HEAD|42|原资源已返/正常结束|
|BOUND_WRONG_PLAN|42|原资源已返/正常结束|
|EXEC_INTENT_ISOLATION|8|原责任保留；仅专用夹具有限收尾|
|TERMINAL_PREARCHIVE_STOP|33|原资源已返/正常结束|
|POSTARCHIVE_STOP|33|原资源已返/正常结束|
|FAILED_RETURN|36|原资源已返/正常结束|
|UNKNOWN_COMMIT_CLOSE|10|原责任保留；仅专用夹具有限收尾|
|CONSOLE_REJECT_THEN_CUSTODIAL_ACK|14|原资源已返/正常结束|

## 必要构建及真实制品

共享Registry源码在Android输入中，不能宣称纯PC继承旧APK。因此一次必要main-001离线构建成功（68 tasks，约1分钟），无repair/下载/native重编。163最终输入SHA `77bae40d39c2a390e149335302681ab71e362deac933145e8888098febdd45d9`。版本14/D1-E10A-PREPARE，AndroidIdentity准确版本门14；原Run/Instrumentation/IO/ABI1及框架逻辑按字节继承，仅该身份版本条件随候选更新。protocol批标签仍D1-E9A-PREPARE-TABLET-20261018，不为改文案重建。

|制品|字节|SHA256|
|---|---:|---|
|app-debug|10659394|`611672a9f2a7eab3f08a495832d513e79ee446cb1a9f99001fe323e944f2af54`|
|androidTest|2749733|`2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b`|
|生产host JAR|261552|`8f5cbce3461d61fecf4c9bc1c026e66ddc4ed3ee1f9ab705ecdebaa594f800a0`|

JAR含159生产classes，不含测试类，来源targeted-002已测编译，并与003生产class逐项相同；三个默认入口INSPECT_ONLY。两APK原签名5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f，7native/35坐标不变、16KiB对齐/角色/ABI/服务审计PASS。测试APK恰与E9B同字节；app已更新。未安装候选。

四文档：本DELIVERY含实现/证明；EXECUTION_RUNBOOK为新受管部署+actor1正常/取消条件流程；FAILURE_AND_FINAL_REVIEW为阶段化收尾/UNKNOWN/actor2门；ACTIVATION_INPUT_DAG为终局后独立发布。机器plan/scope/12个条件命令/只读校验器已同步新14候选、原13来源pair及新host JAR，review占位必须未来E10A接受审查SHA。旧E10“安装0次/复用旧host/BOUND无出口”不再适用新候选，旧文档只作冻结历史。

固定descriptor725B SHA4a1877713ba2b6763d777e73e9b956914a3b5fefa8c8c35c340f81531e6c2adb、commit244B不变；新actor1只3控制文件，intent≤2048B，总内容≤3017B/分配上界6400B、最多3新目录，目录FS开销另计。原task/attempt/budget/fence、0B/S0、53651+53567=107218、13原metadata与oldCloseACKfalse不改；固定1011B前缀与完整合法settled后缀分开。非零媒体不读写，原旧bytes不改、不追加R/S/ABORT/清账/换budget。

E9B/E10原冻结完整只读核验，新ZIP含源码/原日志/差异/输入/制品/完整执行包，外seal避免循环；冻结后独立verify及完整交接报告另存包外。当前0ADB/设备/真实UUID/scope签发/迁移写/token/catalog/activation，无H_actor。用户项目/设备权限与负责人未来具体scope采纳明确分开，不造随机批准token或额外用户授权文本。Framework/独立Kit/Flutter/48资源/严格6帧fullEOF1000us/全部许可P0保持。
