# D1 E2E 准备证据、身份映射与只读复核 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2e`。本批仅新增wrapper、一次性门禁、静态/纯合成检查与封存工具。生产代码变化0、编译0、driver G/J/R0、full/诊断0、fresh资源检查0、真实媒体0；新许可在准备交付时未消费。

## 不可变生产与封存映射

原32源＋branches/profiles共37文件、E2C.dll/9 class十产物及原tools/r-helper.ps1均按E2C source manifest/freeze逐hash核验；C/D确认及所有更早FAIL只读保留。新增manifest/e2e-batch.json是独立授权描述，不修改原branches或policy。原gcore.BASE正常按本包位置解析，SYNTHETIC selfcheck命名空间保持；原真实入口/profile仍关闭。

独立driver只调用原生产Engine/Scenarios/preflight/Cleanup/stop_failure，不调用原controller.run、不改其拒绝分支、不对生产globals/函数打补丁。实际helper使用原R脚本与原产物，保原LoadFrom、原Channel/owner和修后compact链。

原R脚本拒绝活动evidence/freeze-summary.json，故本批不可变seal命名为 **evidence/e2e-freeze.json**。该名由新增launcher/verify使用；绝不删除旧C/D/B seal、不放宽原R脚本。旧入口继续拒绝，新层仅接受特定新机器/批次/外部预期sealSHA和一次自有actual执行。封存文件排自身hash；外部具体SHA由负责人报告交tester，命令中显式绑定。

immutableFiles收取源码、原产物、源ZIP、授权/准备证据和三文档；execution/与唯一selfcheck根是未来可变输出，不能纳入seal后再改hash。运行后只读verify继续核代码集合，实际输出另结果manifest记录，不把输出加入源ZIP或覆写准备检查。准备时两输出目录不存在；默认Inspect和准备检查不创建它们。

## 当前检查范围与成本

当前准备检查采用内存FS、假clock/PID/memory/launch，仅加载纯门禁/编排函数，默认Inspect另用import硬守卫验证。未导入生产模块/真实backend，不启动真实Thread/pool/process/Hub、Engine/Native/Channel、Win32 reader或fresh内存查询。预约竞争用确定性交错的同内存backend模拟，不声称实际跨进程故障或内核竞态已实测。源AST/字节hash和参数拒绝属静态范围；新许可不被测试消费。

本次准备断言153条全部通过（evidence/preparation-checks.json）；只读audit另核上游关系与配置，不将旧C1125、D六OS点、B955/partial77、A1003/另87加入本次计数。源码集合73文件；32生产源码＋5原配置、原r-helper和10原编译产物逐hash一致。没有新原owner实际退出/资源峰证明；所谓noInFlight在本准备阶段只指没有运行任何执行实例。

预算2MiB fixture/4MiB metadata与证据为准备＋执行总账。准备日志含seal≤819200B；保守预留原生产filePeak3178496B和wrapper196608B，不把该生产filePeak解释为全是日志、不提高原budget。原fixture输入135168B＋最大输出信用655360B另留空间。代码/依赖ZIP是源码产物，不算运行日志；wrapper和结果读取hash必须有界另计，不能塞进原452假称零动作。

wrapper完整性IO为每个父/子进程256MiB/8192文件次上界，hash块65536B；结果hash另限6MiB/512文件。父层无PIPE/collector worker；DEVNULL临时句柄上界4（共享NUL＋三个DuplicateHandle副本）、原Popen handle1、临时primary-thread handle1，启动父层预留合计6；另序列身份handle峰1。以上根据本地CPython3.12.14 Lib/subprocess.py静态核对（88747B，SHA256 85d29b2bf0249f5436838298c9a60ee93508b1102e9ac43b001f8a7e7ae8f375），不是本批OS峰实测。新wrapper在正式路径再次核该allowlisted库文件，变化即拒绝。准备阶段仅核该外部库文件，没有重hash Python DLL/Java等全部外部运行时；DLL原摘要仍来自已确认记录，正式路径才实核。全部wrapper文件单文件硬界相加（含launch.pending暂存及首/晚结果manifest）不超过196608B。预约/认领单次CREATE_NEW，launch仅在单次exact write、flush/fsync、实际close返回后无覆盖发布；关闭UNKNOWN不退款/重试。

生产短回执的最终资源数位于logClose.remainingResources；worker、helper、native、日志与父handle证据必须完整，缺失不能靠空集合推断排空。driver未排空原Engine及launcher原Popen持续强留，首PENDING保存后只等待/保持，不补RPC/OS样本或GC。G退出但原helper或关闭证据未知时，result-manifest仍为不完整，files为空、usage为UNKNOWN；不得hash活动root后宣称最终收取。晚结果另存并保首份回执。

## 只读复核

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2e\tools\verify.py'
```

该命令只读准备包/上游hash与已存在的结果证据，不启动G/J/R、OS指标/fresh检查或媒体，不创建root、预约或claim，不消费许可。封存状态PREPARED_NOT_RUN_PENDING_TESTER是seal时事实；若tester后来执行，应从独立执行状态/结果manifest判断，不因旧状态字段推断仍未运行。结果PENDING/失败不能自动触发新执行。

实际freeze SHA、源码ZIP字节/hash、源/不可变文件数、当前准备断言和含seal精确成本见封存摘要及负责人交测报告。独立tester核验后唯一运行命令见执行计划，具体expected-freeze由报告提供。本窗口没有运行该命令。

上游E2D freeze `f0a3e8fc9ae7e6e8c3def52d0002d23af77212ad35cb016a612e34e45f42de1b`、ZIP `6c6eef8c0d9541aefe1eb807a312d1fce7ba968038c127e565af9becd7ccf9d8`；C freeze `bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179`、ZIP `035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934`。D32冻结/63源、C103记录/70源及B/A/E2/E1E/13基线保持。

未读取/stat/hash test_media，未真实PF/runs、设备/Gradle/ADB/NAS/下载。真实媒体启动授权层仍未批准；JNI/P0/C14、历史G/R FAIL及五产品namespace/READY限制保持，D1 NOT_PASSED、M0 NOT_STARTED。
