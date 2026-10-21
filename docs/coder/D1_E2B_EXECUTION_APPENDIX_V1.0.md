# D1 E2B 执行与只读复核附录 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2b`。本附录记录已结束活动，**不是重跑说明或真实媒体授权**。A01四case通过，诊断候选合格；唯一actual OS完整回归尝试FAIL，R501≤512但G369>256、delta209>64，原退出/清理完成。交付待独立审查。

## 原活动顺序与原文件

| 顺序 | 本批已执行活动 | 证据与结果 |
|---|---|---|
| 1 | 有界定向第一轮 | targeted-1792170977795045900.json：955 PASS，保留，不与最终轮累加 |
| 2 | 一次 C#/Java 集中编译 | build.json：1 compile、0 repair，pwsh7.6.5/.NET10.0.11/JBR21.0.10；原既有限flags，无Gradle |
| 3 | 固定两实例 R 诊断 | diagnostic-reservation.json 在首进程前 CREATE_NEW；diagnostic-1792171021038062900.json，2R/8阶段；summary判候选合格 |
| 4 | 唯一条件 actual OS 完整自有回归尝试 | actual-regression-reservation/claim.json → run-selfcheck-1792171193652554100.json：FAIL，20完成行/77局部断言；该次已消费，不补跑 |
| 5 | 最终有界定向与入口拒绝 | targeted-1792171365263345400.json：955 PASS；entry-denials.json：真实入口2拒绝＋第二reservation拒绝，无额外helper |
| 6 | 只读核对、三文档、集中封存 | audit.json、source-manifest.json、E2B-source.zip、freeze-summary.json；verify仅检查文件/既有证据，未启动任何helper |

单次DLL SHA256：`06befb5eee245e4d90ca5c91b35b50093cde9cd30bb639a242295f613fc01ac8`。两诊断方法及actual回归均绑定同产物；没有中途重编以改变比较。最终封存对 Python/脚本、配置、产物与三文档逐文件hash，日志/caps也纳入。

## 固定八阶段原样本

每行线程、句柄、WS、private来自一个实际原进程的单次有界 reader 周期；阶段原PID/creation/owner保持。MINIMAL_START只是诊断差异参照，不能替换未来actual的原HELLO baseline。WS/private单位B。

| 方法 / 原PID | 阶段 | threads | handles | WS | private | 从该实例MINIMAL的句柄差 |
|---|---|---:|---:|---:|---:|---:|
| ADD_TYPE / 14880 | MINIMAL_START | 25 | 498 | 78,221,312 | 24,862,720 | 0 |
| ADD_TYPE / 14880 | LOAD_COMPLETE | 26 | 511 | 84,160,512 | 28,635,136 | +13 |
| ADD_TYPE / 14880 | INIT_COMPLETE | 26 | 511 | 85,925,888 | 29,786,112 | +13 |
| ADD_TYPE / 14880 | HELLO_SERIALIZED | 26 | **513** | 88,231,936 | 29,970,432 | +15 |
| LOAD_FROM / 39424 | MINIMAL_START | 24 | 497 | 82,857,984 | 26,091,520 | 0 |
| LOAD_FROM / 39424 | LOAD_COMPLETE | 24 | 497 | 83,431,424 | 26,492,928 | 0 |
| LOAD_FROM / 39424 | INIT_COMPLETE | 24 | 497 | 85,098,496 | 27,340,800 | 0 |
| LOAD_FROM / 39424 | HELLO_SERIALIZED | 24 | **499** | 87,437,312 | 27,672,576 | +2 |

ADD_TYPE原creation100ns `134366446210466136`，owner `818140126cbd278c1569daf354950d6d`；LOAD_FROM原creation `134366446217969538`，owner `39708869dc52c72941903a34ef2aa7f2`。初始身份通过借原Popen hProcess建立creation锚，八周期各用自己有限临时查询句柄重新核该锚；字段 `sameCreationValidatedByReader=true`，不把每次查询描述成借原hProcess取全部指标。

首次超限精确保留为 ADD_TYPE/HELLO_SERIALIZED/handles513>512。该实例阶段决策约0.407/0.234/0/0.047s、实例约0.750s；LOAD_FROM约0.344/0/0.015/0.032s、实例0.453s；总1.203s。0或sampleDuration0.0是本机时钟记录粒度结果，不声称零CPU成本。均在5s/30s/90s界内；不可中断OS调用的原Future仍按PENDING规则保留，未超时替换查询。

这不是句柄类型追踪。两实例初始句柄已不同，候选HELLO499与对照513的差14不能直接归因于某类CLR对象，不能保证下一实例同值；历史E2A519为另一旧原实例，原FAIL始终保留。有限对照支持候选在该次HELLO门槛合格，不证明所有宿主兼容性问题已解决。

## 诊断独立成本与原资源

| 项 | 实际值 | 约束及解释 |
|---|---:|---|
| 原 R 进程 | 2 | 各只启动一次；Add-Type一个，LoadFrom一个；未制造媒体对象 |
| 固定阶段 metric samples | 8 | 每原实例四个，不重采择低 |
| 原 hProcess 借用身份查询 | 2 | 不open/dup/close借用的进程句柄 |
| 独立控制请求 / ACK | 4 / 8 | 各原实例HELLO＋EXIT、四阶段ACK；单列，不偷记原452无额外 |
| observer自有句柄 | 16开 / 16关，峰1 | 八次reader周期各snapshot与process query顺序持有；credit最终0，无unknown |
| 诊断原worker / transport reader | 1 / 每原R两个 | 明确独立诊断成本；原worker及四reader均join，无新replacement worker |
| ledger峰 / 最终 | 11 / 0 | 独立受限24；保过程/管道/worker/observer所有权 |
| fixture | 0B | 空自有诊断根，无输入文件或媒体对象 |
| 日志/证据含summary | 20,698B | ≤512KiB且计本批4MiB；原report内17,962B为含reservation的当时快照，不改写 |
| 原进程退出 | 各exit0 | PID/creation/owner与四阶段同一原实例，未kill、未复启 |

`RunDiagnostic`与正常R共用初始化；只允许HELLO/EXIT，协议或媒体命令立即拒绝。C#在完成实际序列化、Wire.Pack及cache登记后才发布HELLO_SERIALIZED暂停。原owner不换，加载失败/阶段不具证不会编造样本。控制流和输出都有上限，stdout bounded queue、stderr限量、独立metadata账，不把低资源宿主或卡住线程写成关闭成功。

诊断纯校验所得规范摘要 SHA256：`f3c82bb9d99dbbad68660c88a21f44967a8451b97631cef8accce77c9d55a797`。summary的validation须和原report重新计算完全一致，原文件另有raw SHA绑定。

## 一次实际自有回归的不可重用门禁

外层在任何G/helper启动前，将上述诊断摘要、原文件hash、DLL hash、runtime-policy hash、父PID和唯一runId以CREATE_NEW记录 reservation。原G核父进程/runId/profile、原证据及hash，先CREATE_NEW claim，再创建自有fixtures或Native。模仿真实授权的字典不能解锁REAL_IO；真实profile的拒绝发生在claim/fixture之前。

此实现只准自有SYNTHETIC＋ACTUAL_OS_OBSERVER；不是执行真实批次的授权层。`reserve_actual`在reservation已经存在时无条件拒绝，包括上次FAIL；没有refund。第二次预约的直接拒绝检查无Popen、原reservation/claim hash不变。诊断PID39424的499不作实际baseline；本次R31884自己的原HELLO是501，G36192原PF前baseline160不重置。

唯一actual触限事实：第4周期G369、delta209，绝对256与增量64同时超限。此前完成PF＋19行，P09-TIMEOUT内停止；77仅为失败前partial assertion，passedFull0。现场fresh memory2,454,781,952B达门槛不能抵消句柄失败。原指标limits、1s/201/gap2.5/返回后0.1、24/6/8及61原行/180s未改；外层200s只是停止等待界，不能伪造原IO取消。

原reader4周期、14开14关、同时峰1、身份查询3（其中借原J/R hProcess2）；无待返回Future、observer信用0。最大间隔1.687s。global.log最终36,951B（events36,555＋metrics396/3条正常周期），触限第4样本保存在原observations、failure和关闭前摘要；不得以少一正常metric行推断没有采到失败。

原J/R wait exit0，G返回FAIL后退出；Hub CLOSED，workerjoin与信用归还具证；44cells全释放，retained0；global.log closed、原资源最终0，外层noInFlight true。保原preclose摘要及hash `623bc77602fdb668336b1955f54db74cf57724e0846a5573e831963f14664f02`。恢复检查仅冷读本次已落盘的11个任务记录（含PF），原UNKNOWN状态保持，不能要求失败前尚未运行的32记录/全场景尾部出现，也不能把UNKNOWN恢复解释成业务成功。

## 只读复核

封存后可在项目目录运行以下命令。它只读本包与已有历史docs源/证据，重算hash、ZIP映射、配置/预算与回执一致性，不compile、不运行诊断/自有full、不查OS指标、不访问test_media。

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2b\tools\verify.py'
```

预期完整性结果为PASS，`actualFullStatus=FAIL`、`actualFullAssertions=0`、`targetedAssertions=955`、真实媒体NOT_RUN。冻结hash、ZIP字节与hash、source/frozen/selfcheck文件数及整批fixture/日志精确量以freeze-summary和verify输出为准，避免摘要自引用。

上游E2A freeze SHA `a74cceea70b94354f328cb348ef5c0dd126ce50ca1125b3d7f8fcf401c3ff37e`，E2A-source.zip1,541,520B/SHA `9ea9be9c6a2e734e364bcc22e5946e91eab9c359474ada2870107e56d5526a50`。旧326记录/53源文件、E2231/43、E1E188/33、13基线均只读逐hash核对；旧E2A1003及独立桥87不加到本批955。

本包不再执行固定诊断、已消费actual full、mock full、真实PF/61或设备实验。后续由负责人裁定独立审查及G资源阻断的必要下一步；真实授权层与唯一root仍缺，JNI/P0/C14及历史FAIL不变，D1未通过、M0未启动。
