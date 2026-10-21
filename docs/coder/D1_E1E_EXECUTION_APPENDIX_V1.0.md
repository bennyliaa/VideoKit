# D1 E1E 编译、检查与停止说明 V1.0

2026-10-16。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e1e`。所有入口默认inspect-only；冻结后拒绝原地构建/执行/重生成manifest。后续新授权批次另建目录，不能删证据或修改原冻结包重置累计额度。

## 本地环境与只读命令

Python：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。

PowerShell：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`，7.6.5/.NET10.0.11；已有Roslyn/ref。JDK：`D:\Android\Android Studio\jbr\bin`，21.0.10。无dotnet SDK、无新依赖下载。

冻结核验只读，无helper/媒体：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e1e/tools/verify.py'
```

默认查看模式：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe' -NoProfile -File 'D:/CodexProjects/VideoKit/docs/coder/d1e1e/tools/launch.ps1'
```

`launch.ps1 -Mode Recover -Snapshot check-20261016T231420`只读恢复完整权威，不造native handle/writer。`tools/audit.py --audit`只读核既有证据、逐worker退出事实及原E1D228文件。verify另核全部源码ZIP成员、13项R1–R4基线和manifest输入SHA。

## 本批已执行

本地 `tools/build.ps1 -Compile` 一次成功，生成E1E.dll与JavaHelper*.class；协议key E1E_KEY，R helper只加载E1E.dll。无repair重编/下载。后续只改Python/工具/文档，没有C#/Java变更。

`tools/run-selfcheck.py --run` 一轮：G经PF16启动同一对J/R，执行29源＋30输出＋最后S17两行，GC32一次收尾；159项PASS，回执 `evidence/selfcheck-1792163660432915800.json`，执行根 `selfcheck/check-20261016T231420`。产物是合成.bin/.out，不是test_media视频。

`tools/check-targeted.py --run` 一轮，集中205项启动负例＋414项既有相关检查，共619项PASS，回执 `evidence/targeted-1792163909644634300.json`。合计选定778项，无旧结果或多轮重复累计。测试代理只编辑自有startup_checks.py，所有执行由主窗口集中完成。

startup_checks通过自有factory/starter和实际Thread核第一/第二start、第一/第二reserve、第二reserve提交后抛错、实际start后异常、UNKNOWN状态、join超时、STARTING门禁、重复close及原stdout非零回执。有限Event屏障，无sleep碰概率；TrackingThread记录每次join之前Thread是否真实启动。所有受控线程最终真实join，未启实例从不join。原UNKNOWN/PENDING保存于startupObservations/originalReturnChannels，测试finally的受控退休与原回执分开，绝不清原错误或自动重启Hub。

Flow/query/RPC测试调用生产入口但使用自有逻辑状态和不可达副作用哨兵，核budget/state/action/IO不增加。未构造Engine/Native/Channel，不制造真实系统线程耗尽或磁盘故障。helper未知前提检查也不启动helper，原stdout使用生产emit_failure和真实JSON解析，不手拼假回执。

## 生命周期、预算与停止

PF/n01唯一NEW setup例外内逐worker预留和启动；RUNNING只在两worker真实entry且存活后成立。失败立刻封闭、保留原异常、停止已启worker、有限回收。未分配不退款，确证未启THREAD_NOT_STARTED_PROVEN，实际已启须原Thread真实join；通用异常/identity缺失/包装exit单独均不能伪证明。重复close保持事实且不对未启对象join，未知保留Stop/PENDING。

正常GC/n31在原控制内join两worker、归还信用；最终n32前核Hub CLOSED、无credit/unknown/错误。启动失败若尚无J/R，直接进入controller原返回通道，不尝试缺失helper的GC/RPC。helper_attempts明确区分从未尝试、构造中/未知与已有对象；缺对象不足声明从未启动。原返回code2，即使已回收也FAIL，未证所有权PENDING。未开log不声称实际close，实际flush/fsync/close返回才记证明。

这批新增逐worker观察/停止/有限join属于PF/n01和既有异常收尾/GC/n31的G本地步骤；无额外N/RPC/metadata事务。仍保留452分配/544硬界、101query、IO/文件/资源/180秒、每N/D最多两snapshot。正常受管峰23，媒体5、槽1，最终0；仅工具受管信用，不是全系统线程/句柄测量。

任意callback或native IO不返回时，保留原owner/credit和PENDING，不强杀，不保证进程180秒退出。外层200秒只停止等待并记录原G PID。失败出口对仍有callback/native/worker所有权时不关依赖资源；已有但未证helper继续PENDING，不发额外EXIT/RPC。启动/关闭注入接口和内存事实不构成新的崩溃持久性保证。

正常n32真实flush/fsync/close后G不再写盘，原stdout≤8KiB外层见证关联关闭前摘要SHA `07854054899797fcddc9cf32231bf7f1062368777214849cfa04d9b266460d2c`。恢复仍将GC/n32意图留待外部见证，不能单凭磁盘意图推断close。

全部本批执行返回且无在途后一次冻结；source-manifest/freeze-summary记录源码、产物、文档、证据字节与SHA。旧E1D/E1C及失败证据保持只读，源码ZIP嵌套保留完整源码依赖。未读test_media、未真实PF/媒体/设备/Gradle/ADB/下载或正式run；JNI BLOCKED、D1 NOT_PASSED、M0 NOT_STARTED及原真实配置/版本/durability/总资源限制不变。不自行派tester/实验，冻结后主动交负责人安排。
