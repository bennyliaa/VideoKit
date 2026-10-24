# QUALIFICATION05 完整失败交付及原调用保留快照

2026-10-24。**FAIL / ORIGINAL_RETURN_UNPROVEN_RETAINED**。本批仅辅助宿主基础资格组实际PASS；事实采集原调用超过90秒仍未向原外层调用返回。后续独立review、正常生产链、错固件、同字节receipt替换、18项预算helper、346项V1回归均NOT_RUN。原worker没有最终result.json；本报告是外部观察快照，不能冒作原owner结果或归还证明。D1未通过/M0未启动。

## 正式范围与固定源

正式工作单SHA44925498544bf838cd49705594af5736a1611945829a946c49224e7883c5411b。仅新05目录开发；04和tester04独立B及05静态A全部原件前后核验bad0，分别284/260/28项。独立A报告71183372022222abf281a45281573a7fa248695eddf5357671ecbafd508acdd8、manifest40a048659d6e22b3474563033def291785abbdbf26cc82b73fb44b11b750959d。

source33 8952f6a2be114b1c1d4a5d2836007778a5e65f02e3157b613e7b4ed1c4df41e6；gate25 9bf0e0f198b9a247303d6daa15e52abb55de45365535187be22a54429c8afd82；profile63 2ce2a27722521bd1548dd44f8c00f662c637db99018357530789db9a9b7c19bb；批计划 70995212350843dfe2dc037efba4bcf9c37e4305f2747ca998030169be13ae41。runtime_binding原2056B/20CRLF/SHA47f9保持，metadata2593及14依赖准确核验；默认原bytes复制，只明确patch改动。动态开始后源、profile、驱动、输入均未修补或重试。

## 已实现但未实际获证的修复

1. 原receipt writer在WriteAsync原任务返回后Flush，通过自己的SafeFileHandle取得volumeId/fileId/大小/固定路径，SHA绑定当时排队的准确bytes，存入该原record后只进行原close。V2原console输出ORIGINAL_RECEIPT_IDENTITY_VIEW_V2和五字段receiptRef。Owner先完成原wait/readers/流/H及原console/native归档，再由原Runner从自己的原读句柄核writer身份、前后身份与原bytes，之后才恢复bindings/readers/input、merge原delta。错路径/类型在open前拒绝；错volume/fileId在内容read前拒绝，close返回；错SHA在读后拒绝。代码已冻结，**本批未到达任何实际receipt读/写，不能报修复通过**。
2. 原Runner新增前置完整控制消息UTF8预算，位于validate结束、Gate/claim/consumed/物化/controller之前。policy/activation与真正物化共用构造函数；independent evidenceRoot单独通过完整wire同时计入permit/policy；request/admission/proof/Gate/receipt/console/native和重复功能读取/两次console均计入原65536/262144/1048576。receipt/console使用原8192上限，halt2048；其余未来固定结构用冻结完整字段和数值宽度预留。未来量明确是RESERVATIONS，不冒原返回实测。完整控制ReadJsonExact和前驱原receipt读取进入proofReadBytes；新增前驱receipt读在PS原ticket永久预留8192B/1次，完整七角色预算14来源读取仅静态。
3. 驱动实际调用与Guard共用facts/review/aux argv factory，完整程序/cwd/env/options在Capture构造前检查，原launch重核。Guard已变独立可导入类，纯检查直接调用当前原Guard，无Capture/Popen。预算helper引用独立A冻结实现并仅适配新own work根；18个ID、逐项持久化、try/catch/finally、$false与结果缺失错误已准备。本批**未实际运行该helper**，不冒18项通过。引用A不是独立B验收。
4. 一次冻结图预期16宿主Popen+facts内2+.NET4+worker1=23，缺陷导致多走替换scope后继的条件最大25，96/并发1/retry0。替换夹具只对本批新receipt在原返回后操作，保留原文件并同字节新建，原reader应以writer ID拒绝；正常链另含错path/volume/fileId/SHA原API负例。这些分支均未运行。

## 纯预检及其准确限制

42项纯契约预检PASS，34项原SourceBudget纯模型PASS，PowerShell全部解析及裸true/false/null命令检查PASS；当前Snapshot36字段与shape完全对应，源/caller/runtime/未来tester05 roots/精确prefix类型及实际辅助argv正反例均核。实际Guard正例facts、三review、budget/v1；错误source/executable/cwd/env/额外argv在Capture构造前拒绝，原Popen数0。

完整控制消息纯模型：普通目标最大局部64925B<65536，共享250339B<262144；7189字符独立证据根候选在CONTROL_ENVELOPE_CONTROLLER_65536:92967>65536拒绝。该候选只是条件容量模型，OS路径/完整资格可达性未证明、未物化，不报真实溢出。未来证明数值仍需独立B审，真实生产合法/超量准入均未到达。

**纯预检缺口：新增两个Gate源后，没有覆盖事实采集从初始Gate直到真正fixture构造点的完整64次读取预算。** 因而42项通过不能代表本批可运行，更不能代表receipt/容量动态修复已通过。

## 原调用保留与可能原因

原fact Capture创建记录pid=17264，creationUtc=2026-10-23T23:02:14.848943+00:00；外部快照观察已过272.233秒，children/facts仅有原launch-intent及original-identity，无original-return/管道archive/return.json，也无worker最终result。原Gate receipt由自身写入，checker原临时资源返回、claim明确保留，sourceHashReads=55。外部没有查询、接管或补齐原对象，不推定内层是否已经Popen。

静态重建：原Gate55→PreparedFacts.receive五次pin读取60→raw原读及child reservation62→runtime metadata/exe64→fixture_guard在调用真正Popen之前还要读source seal，第65次按原source_read会SOURCE_READ_BUDGET。OwnedFactCapture在guard调用前已经entered，捕获任何异常即unknown=True；facts_entry对此保留原调用不退出。**该路径与现象一致，但原异常没有持久输出，仅列强静态推断，不能当原异常或底层进程状态实测。** 这是coder漏掉完整事实读取链预检的问题。

当前外层原worker和facts调用均无返回证明，原claim/once/预算原样保留，未造ACK/退款，不kill/二close/补收尾。辅助资格组3个宿主原调用及其exit0/7/0返回已保存；不能据此清零facts/worker custody，不能报全原件归还或新UNKNOWN为0。360秒预算只约束新执行；对不能证明返回的原调用继续保留，不以截止时间取消。当前已停止新增，后六组明确未跑，不消耗其他scope重试。

|组|准确状态|
|---|---|
|qualification|PASS|
|actual-max-facts|ORIGINAL_RETURN_UNPROVEN_RETAINED|
|independent-review|NOT_RUN_DEPENDENCY_RETAINED|
|production-prefix-positive|NOT_RUN_DEPENDENCY_RETAINED|
|production-wrong-firmware|NOT_RUN_DEPENDENCY_RETAINED|
|production-receipt-replacement|NOT_RUN_DEPENDENCY_RETAINED|
|source-budget-and-reload-models|NOT_RUN_DEPENDENCY_RETAINED|
|V1-regression|NOT_RUN_DEPENDENCY_RETAINED|

## 交接与剩余工作

本批不再补跑、不改浮动源。下一正式整批应修事实调用完整读取链的资源前准入/重复读取计费，保留原64上限与原来源权威；然后在新scope完成正常/错固件/物理receipt替换、18辅助、实际容量与原delta整合。不能为修复直接清理本批保留调用，不触旧tester capture1或其他历史UNKNOWN；不能以源码完成代动态通过。

本批SDK/ADB/设备/Native route/TCP/Gradle/媒体/Git操作0；路由checker为原离线fixture，未安装APK，test_media未触及。读取预留960MiB<1GiB；实际未完成调用的完整计数未知，未造全量物理I/O测量。源/输入/静态预检冻结后只执行这一批，当前资料含全部阶段与失败限制。新增文件全在docs/coder新05目录。

manifest/ZIP封存的是此时可读固定bytes快照，**不是保留原调用的最终完成包**。原cooperative-default-route.lock由原claim排他持有，打包读取返回PermissionError；未重新读取、解锁或复制其内容，manifest准确列为excludedOriginals，不能声称全部原件已入ZIP。若原调用未来自然返回，其新增文件不在本快照中，须另行记录，不能反写此manifest或恢复本批。冻结回执和通知回执在hash循环外。完整报告主动交负责人，等待集中裁定后续正式批次；当前不交独立B通过候选。
