# D1 RESUME01_RELEASE 机械绑定交付

2026-10-20；候选 D1-20261020-RESUME01-RELEASE。负责人已接受 RESUME01 静态 PASS 与43操作/3MiB文本/4MiB归档，正式派本批机械绑定。整包冻结后交tester独立机械核验；其PASS并满足所有现场门后，负责人同批授权M1→部署→M2→唯一ordinarySenderCannotBindCodec。coder未执行现场阶段。

## 准确身份与来源

新执行批次/scopeId：`1f1cc608-2337-438f-a9f5-086cda29ceb2`。

| 材料（目录 docs/coder/d1resume01-release/release） | SHA256 |
|---|---|
| runtime-scope.json | 917d8c1dc57d267a25101355f077e4a0c3ed62b6c93c10d63ec8255def6b1bde |
| activation-release.json | 04605dcf8f1ab1b2c0d0147da255e6514f309f4669f79efa1bf0f404042f35e5 |
| activation-trust-deploy.json | c988760490747e7d456311b3b4df1fdf4579bc753ac0cf0130a8115d5ad958eb |
| one-shot-permit.json | 37e899f0cc92ef97d8d473f96d8491050e5985210975db56337efe0b4ce6bead |

scope/release 的 sourceReview 准确绑定独立报告 `docs/tester/D1_RESUME01_STATIC_REVIEW_REPORT_V1.0.md`，SHA256 `0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743`。本批新授权记录单独保存；原registry的authorization/review/preparePlan身份照原受审字节保留，不替换为新来源报告，避免破坏原catalog信任链。

行政disposition仍610B、SHA `7270e5c0208d2895394bbd1cd25508b239bbe7a711a40b3e8d2b3d59a37a265d`，四个证据摘要逐项一致。A/K原Java终止无原返回、B/H行政UNKNOWN、K预算UNKNOWN、平板OBSERVED_ALREADY_STOPPED/强停0均保持，不补原ACK、不退款。行政记录仍仅位于发布候选，未安装真实root。

## 零构建与逐成员等价

无生产源码/策略常量变化，全部74生产来源和183个JAR成员与静态PASS候选逐字节相同，故零host/Android/Gradle/native构建，无功能扩展或长套件。JAR复用字节 SHA `03a27c74061b740a879e2dfec3341b0b07172c68bf374b9231c20e42a46566c5`；observer复用 SHA `0667bc7fe93cf2010cd337eeafaeabd94b7a795efa74059365af3fb83c8485b8`；app19/test/fixture3复用已冻F三个APK。新JAR文件名变化不改变字节身份，member-equivalence列全部183项。

registry方案使用原真实root及准确原head/catalog，但coder只读取已封存的 `d1e11/source-export/accepted-registry-snapshot`。逐文件与历史export前清单核对，并沿F封存的E11-final seal→原E11 seal→原快照链验证。未打开真实registry；tester必须在现场核原root完整inventory、每字节摘要及quiet状态，不能用复制出来的快照替代真实registry蒙混准入。

## 逐操作、计费与执行材料

五条M1/M2元数据请求、两个真实主机observer请求（配置/范围SHA已实填）、唯一instrumentation argv、35部署子调用图和所有源文件pin齐全。`pm path`之后的远端APK路径属于运行时相关响应参数，明确引用前一同包操作及源代码固定解析规则，拒绝离线假路径或外部任意值；原archive在每个child前记录实际完整argv，不新增命令来解析依赖。

| 分组 | 操作 | 原始/重复输出预留B |
|---|---:|---:|
| M1 identity/global/ps | 3 | 655360 |
| 部署主机入口 | 1 | 81920 |
| 部署SDK子调用 | 35 | 524288 |
| M2 identity/global | 2 | 589824 |
| 唯一case主机入口 | 1 | 32768 |
| 唯一instrumentation | 1 | 65536 |
| 合计 | 43 | 1949696 |

元数据控制预留786432B（原细目712704B），未分配409600B不可使用；总3145728B、归档4194304B。控制栏中的releaseAndScopeRecords六个8192B槽明确为scope/release/config/permit/授权/本地前置回执；不新增操作额度。所有重复转发、实际console/归档文本均计费，不把控制器或Android内部创建的进程混报为“全系统物理进程数43”。

原maxTextBytes是保存/合格界，不是物理读取硬界。超界仍计实际成功读取stdout+stderr和重复文本；确切量无法从原记录证明时记UNKNOWN并保留整个对应分栏，不报成名义cap或保存前缀。停止所有后续调用，原owner/pipe/reader继续按原链保管；若继续原排空造成实际超额，保留超额事实，不借409600B遮账、不强关原对象。不具备这种原采集/计费能力则在启动child前BLOCKED报告，不重造生命周期/诊断框架。

同源工具门要求在任何SDK客户端前，使用已有主机能力一次核当前既有5037监听者与固定ADB路径/已审文件SHA及时序，确保没有重定向环境。服务缺失、来源不符或不明即停，不启动server、不额外运行version、不重启或另造协议。coder未读取当前工具/监听者；已审ADB字节来自封存平板证据。

## 准入、once与停止门

准确部署once目标：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_RELEASE_EXECUTION/1f1cc608-2337-438f-a9f5-086cda29ceb2/e13f-lifecycle-deployment.once`。本批未创建该目录或文件、未消费许可；实际不存在仍须tester前置核。case once复用已审固定root的同scope+method持久claim规则，不预造claim或return marker。

机械PASS后先核本地工具、真实registry、ledger/claim和许可，再M1确认HA1Q6WXR/TB138FC/API31/user0、app/test准确v17与原byteallowlist、fixture1准确hash、UID10221/10222/10228、data6972/4741及新鲜fixture数据身份、完整占用与双EOF/原记录归还。任何其他项目活任务或归属未知都停止，不自动复查；不凭上次LendManager状态推定当前空闲。

独立未结claim仍阻断，逐个原marker/hash/pcHandle/threadJoined门保留，不清理/通配豁免。原B/H隔离与A/K行政接受不等于豁免新claim。全部M1门过后才允许准确CREATE_NEW安装disposition（已有同字节仅复核，不同字节即停），再执行原部署入口。前置不是准确v17/fixture1即停，不同版重装/降级或换设备。

部署真实结果及原PC/线程/文件归还满足后才M2，确认19/3和全局无其他项目，再唯一case一次。首失败/超时/超限/占用/UNKNOWN即停止，无其他五方法、重试、status轮询或处置。55秒响应资格不是杀进程许可。真实单项PASS仍需JUnit/scope/token/最终instrumentation、不同签名fixture/UID/Binder内核拒绝及原owner/资源归还；目前全部NOT_RUN。

## 核验与交接

ZIP：`docs/coder/D1-20261020-RESUME01-RELEASE-source.zip`；seal：`d1resume01-release/evidence/release-freeze.json`；外部只读回执另存，避免自引用。默认verify/help/pack-help只读，只有显式pack生成一次新包。独立机械报告尚未存在，不在scope中伪造；由tester在核验后以真实报告绑定外seal，方可进入已授权条件执行。

生成工具最初一个语法错误和一个E11两层seal定位断言已修正留痕，均在发出scope/permit前；最终只生成一个准确scope/许可，无执行重试。初始名称检索涉及docs/tester，未打开真实registry/ledger/claim内容；此后registry仅从coder封存快照读取。无设备/SDK调用、原handle查询或现场文件变更。

分别coder/tester正式需求已保存，两协调顶部同步。旧RESUME01/F及原账目/once保持。Flutter/独立Kit/全P0/既定框架许可保持，D1未过/M0未启。本批只交准确材料，实际准入与执行由tester在独立机械PASS后按负责人同批授权承接。
