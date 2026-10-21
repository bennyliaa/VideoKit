# D1 E1C 编译、检查与停止说明 V1.0

2026-10-16。根目录 `D:\CodexProjects\VideoKit\docs\coder\d1e1c`，所有入口默认不构建、不运行helper/PF；当前包冻结后执行入口拒绝原地重新构建或自检，先安排新授权批次，不能改旧失败/删除证据重置额度。

## 环境与只读命令

已有Python运行时：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。

已有PowerShell：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`，7.6.5／.NET10.0.11，已有Roslyn与ref；JDK `D:\Android\Android Studio\jbr\bin` 21.0.10。无dotnet SDK、无新依赖下载。

完整性核验（只读，无helper）：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e1c/tools/verify.py'
```

默认入口只查看模式：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe' -NoProfile -File 'D:/CodexProjects/VideoKit/docs/coder/d1e1c/tools/launch.ps1'
```

`launch.ps1 -Mode Recover -Snapshot check-20261016T221257`只读重建完整权威，输出可能较长，不重建native句柄或writer。`tools/audit.py --audit`只核已有合成证据与上游冻结文件。

## 已执行的检查

`tools/build.ps1 -Compile`使用现有本地编译器；首次延用历史输出名，第二次统一E1C产物和协议环境key，两次成功；无第三方组件。启动加载E1C.dll。保留新目录中的旧输出名E1B.dll作历史，不覆盖旧d1e1b。

开发时显式 `tools/check-targeted.py --run`集中运行四组针对性检查；`tools/run-selfcheck.py --run`启动该轮G，再由PF16启动同一对J/R，执行29行源＋30行输出＋最后S17两行，GC32一次收尾。最后一次选定负例260、完整回归158，合计418；多个早期通过记录保留但不重复计入。

负例只对自建逻辑状态与独立小元数据目录操作，源/owner部分不启动Native/Channel；metadata部分自有writer返回短值，验证单次write、UNKNOWN、未授权RPC与下游0，不制造实际磁盘故障。原始合成.bin/.out不是test_media样本。

PF admitted inventory替代新task的第一次admission快照，完成写该task槽，最多两次事务；没有新增控制/RPC。每次q日志带batch/task/row身份与相对N/D位置；snapshot/可信日志取max，缺失或较少日志只得UNKNOWN/已知最小信用，不可用其差额继续。

## 证据与停止

最终回归回执：`evidence/selfcheck-1792159977751886300.json`；关闭前摘要在 `selfcheck/check-20261016T221257/result-before-close.json`。最终针对性回执：`evidence/targeted-1792160323238457900.json`。源ZIP、源码清单、冻结摘要与verify逐文件SHA关联。

取消/超时只结束消费者Future；private result、operation、buffer lease仍留账，gate/可信排空后一次释放。GC的源owner死亡证明不能把G尚持有的private cell直接标done。UNKNOWN close、耗尽attempt不重关；原C UNKNOWN/D native0事实在owner退出后仍保留。

元数据短写/异常时Store停止新接纳，不补写；不得继续native/RPC。deadline到停止等待，不声称强行中断内核IO。最外层200秒停止等待只保存原G PID的PENDING，不推断G/helper已死；真实挂起出口未做压力实验。

GC/n32前先完成记账、receipt和PF意图记录，n32执行真实flush/fsync/close后G不再写文件；外层调用者经原stdout接收≤8KiB见证，再保存外层回执。完整性工具不把磁盘关闭意图视为实际close完成。

本批无构建/helper/exec任务或已知IO在途。没有读取test_media、真实PF/媒体/设备实验、Gradle/ADB/网络下载或正式run目录。JNI、D1/M0及全部历史门禁仍保持原状态。
