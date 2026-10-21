# D1 E1B 编译、启动、停止与核验 V1.0

2026-10-16。所有目录均以 `D:\CodexProjects\VideoKit\docs\coder\d1e1b` 为根；不读取test_media，不需要网络或新SDK。

## 本地环境与入口

Python：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。

PowerShell：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`，7.6.5／.NET10.0.11，使用现有Roslyn与ref编译；没有dotnet SDK。JDK：`D:\Android\Android Studio\jbr\bin`，21.0.10。

在项目根执行以下命令只读核验，不编译、不启动helper、不运行PF：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e1b/tools/verify.py'
```

默认检查入口：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe' -NoProfile -File 'D:/CodexProjects/VideoKit/docs/coder/d1e1b/tools/launch.ps1'
```

`build.ps1`默认不编译，只有显式`-Compile`才构建；已有DLL需`-Repair`保留历史。`launch.ps1 -Mode SelfCheck`、`NegativeChecks`是显式执行入口，本包冻结后不直接重跑；所有多轮fixture/log累计仍受2MiB/4MiB限制，目前剩余日志信用不足下一整轮，门禁会拒绝。需要重跑应先由负责人安排新批次/副本与累计额度，不删除旧失败证据后假装额度未花。

`launch.ps1 -Mode Recover -Snapshot check-20261016T213139`仅从既有合成记录只读恢复，不授写、不启动J/R。输出含完整权威状态，可能较长；可以用audit.py的汇总核验代替展示完整状态。

## 记录位置与实际流程

1. controller显式创建独占合成根；PF按16槽启动同一对J/R，取得原PID/instance和版本，读各16B校验。
2. Scenarios按manifest.executionOrder执行：29行源、30行输出、最后S17两行。D有独立ID和先行预算，N严格对应原操作token；q日志记录相对N/D位置。每个行完成检查真实elapsedSeconds，不放大时限。
3. GC32槽合用正常/停止清理，不重启helper。至多现存安全资源可关，UNKNOWN/耗尽不关；实际wait后逐owner事实归还，再各关父端pipe与process句柄。
4. 最终记账/summary在log关闭前完成；n32真实flush/fsync/close后只经既有stdout返回≤8KiB见证。外层run-selfcheck.py作为原调用者保存见证文件，不让G再打开一份log为上一份关闭作证。

最终外层见证：`evidence/selfcheck-1792157499032096500.json`；关闭前摘要：`selfcheck/check-20261016T213139/result-before-close.json`。二者SHA关联由audit核验。最终源/产物/SHA清单：`evidence/source-manifest.json`、`evidence/freeze-summary.json`；verify还检查源ZIP逐项内容及原基线，不仅检查文件名。

## 停止与失败语义

无自动retry、补读、额外owner或重启PF。行/全局deadline到即停止新工作并进入既有GC槽；行/任务/全局预算任何一层失败都保留已用额度。已接纳native尚未返回则保留pending事实，不声称线程取消能中断内核IO。异常收尾只能操作本次Popen持有的确切两个helper实例，实际退出另证，不扫描或终止其他窗口的进程。外层200秒只停止等待并记录原G PID的PENDING，不推断退出、不代写close成功。

本次所有构建和运行已结束，最终正常退出证明在外层见证中；独立核验不产生helper。Windows2GiB/真实媒体版本/requiredDurability、Android/JNI/设备/原P0与历史FAIL均保持待验证或原阻塞状态。没有Gradle、ADB、媒体/PF真实实验、依赖下载或正式run目录。
