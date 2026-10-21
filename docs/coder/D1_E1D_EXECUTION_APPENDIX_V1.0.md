# D1 E1D 编译、检查与停止说明 V1.0

2026-10-16。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e1d`。工具默认 inspect-only，不构建、不启动 helper、不读媒体；冻结后构建/合成执行入口拒绝原地重跑。后续执行另建授权批次，不能删除证据或改旧冻结包重置累计额度。

## 环境与只读入口

已有 Python：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。

已有 PowerShell 7.6.5 / .NET 10.0.11：`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`；已有 JDK 21.0.10：`D:\Android\Android Studio\jbr\bin`。无 dotnet SDK 或新依赖下载。

冻结完整性核验只读，无 helper：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e1d/tools/verify.py'
```

默认查看模式：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe' -NoProfile -File 'D:/CodexProjects/VideoKit/docs/coder/d1e1d/tools/launch.ps1'
```

`launch.ps1 -Mode Recover -Snapshot check-20261016T225034` 只读恢复完整权威，输出可能较长，不重造 native handle/writer。`tools/audit.py --audit` 只读核已有证据及原 E1C 446 个冻结文件。verify 另核13项 R1–R4 基线、输入SHA、全部源码ZIP成员和冻结文件。

## 本批已完成执行

`tools/build.ps1 -Compile` 使用本地编译器一次成功，生成 E1D.dll 和 JavaHelper*.class；启动只加载 E1D.dll，协议环境key为 E1D_KEY，未改原 d1e1c。之后仅修改 Python/工具映射/文档，无 C#/Java 变更或重复编译。

`tools/check-targeted.py --run` 共执行两轮：早期393项保留；修复内部静态审查发现的 active 容量归还竞态并新增屏障反例后，最终414项全过，选定 `evidence/targeted-1792162366628428500.json`。completion 新增153项，包括真实 add_done_callback、SourceAuthority/cell 锁访问、超时保留、决定/通知延迟、队列容量、active归还窗口和submit异常。测试所有有限屏障线程/Hub worker均实际join；异常测试在 finally 受控排空自身结果，不删除原错误标志。

`tools/run-selfcheck.py --run` 一轮启动 G，由既有 PF16 启动唯一一对 J/R，执行29行源＋30行输出＋最后S17两行，GC32一次收尾。最终159项PASS：`evidence/selfcheck-1792162234030690200.json`；执行根 `selfcheck/check-20261016T225034`。完整回归使用已修复的容量/投递代码；其后仅新增测试和 manifest 描述，未改变运行逻辑。共选定573项，不重复累加早期证据。

PF/n01 setup新增固定两条G内线程及2个worker信用；每次cell在native前登记有界通知信用。source/cell锁内裁定、锁外入队，由notifier发布Future并同步调用callbacks；deadline在固定monitor中扫描最多8个cell，不创建逐cell Timer。GC开始有限drain，在原GC/n31 join两worker并核真实退出。内部通知无额外R4控制、RPC、journal事务；manifest明确标记其所在原步骤。

原PF inventory/admission/completion仍最多两次snapshot，每次metadata写仍单次exact_write并核实际返回。T02–T05针对性回归保留，缺shard或较少日志不退款，短写/非法返回立即UNKNOWN且下游为0。

## 停止与冻结证据

Future.done不等于callback已退出。慢callback时gate/drain/close期限到达Stop，并停止新接纳；native、gate和实际回调三者齐全前不释放private cell/lease。晚open被拒仍由原owner清理H。原子交付决定后才发生seal时，已定成功不因通知排队而被逆转。

callback无返回时无法强制中断；PENDING保留G PID/helper实例/未证log关闭。非daemon线程可持续存活，最外层200秒仅停止等待，不自动证实进程已退出。线程部分启动失败和极端native挂起未注入验证，详见IMPLEMENTATION_BOUNDARY；不得把正常批次的无在途结论外推到所有异常。

GC/n32之前完成记账、关闭前receipt及PF意图；n32真实flush/fsync/close返回后G不再写盘。原stdout返回≤8KiB外层见证，关联关闭前摘要SHA `6ac2133b118394394b9a2dd0562ebb33a8f6ffb04e8fa8a8da19a4894291a498`。磁盘上GC/n32意图不能单独证明close完成；恢复仍保留该项待外部见证。

本批合成回执为两原helper实际wait code0、剩余受管资源0，64cell排空、Hub workers0；受控负例最终无遗留线程。全部工具调用返回后才冻结。source-manifest/freeze-summary对源码、产物、文档与证据给字节及SHA，源码ZIP嵌套保留E1C/E1B/E1完整源码关系。原E1C与历史失败证据未编辑。

没有读取test_media、真实PF/媒体/设备、Gradle/ADB/网络下载或正式run目录。JNI BLOCKED、D1 NOT_PASSED、M0 NOT_STARTED，真实版本/durability及运行时总资源仍未证。本批交付只申请独立复审，不自行启动后续tester或实验。
