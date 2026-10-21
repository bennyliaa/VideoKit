# D1 E1 工具构建与执行附录 V1.0

2026-10-16。仅已批准工具编译/合成自检；真实媒体/PF/整批实验未获批准且没有完整驱动。完整边界见[实现边界](D:/CodexProjects/VideoKit/docs/coder/D1_E1_IMPLEMENTATION_BOUNDARY_V1.0.md)。

## 1. 已用环境与代码

源码：[d1e1/src](D:/CodexProjects/VideoKit/docs/coder/d1e1/src)。命令/版本及编译历史：[build-info.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/build-info.json)。本机PowerShell位置为`C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`，自带Roslyn和.NET10.0.11；Java/Javac在`D:\Android\Android Studio\jbr\bin`，21.0.10。无dotnet SDK，没有使用dotnet restore/build或安装任何依赖。

首次集中编写Core/Native/Java/Controller后主编译成功；随后为receipt、只读恢复/退化状态、FrozenSession/deadline、原进程证据及空收费拒绝等必要补充修复重编4次。共5次编译成功，没有编译失败；合成自检断言历史67→74→79→79→80。初次离线manifest生成器不识别无括号grant重放token，已修正再生成；不是媒体/工具编译失败。当前产物为最后一次源码版本，`E1-before-repair*.dll`仅保留历史、不得当候选加载。

## 2. 默认只查看，不执行实验

以下默认入口只读取机器清单并显示NOT_RUN/DENIED，不建立run目录、不读媒体、不启动helper：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' -NoProfile -File 'D:\CodexProjects\VideoKit\docs\coder\d1e1\tools\launch.ps1'
```

`-Mode Experiment`明确抛出`E1_MEDIA_PF_FULL_RUN_NOT_AUTHORIZED`。即使手动编辑manifest的experimentEnabled，入口仍拒绝；不能把它当可用完整实验启动命令。当前没有获准或可用的真实媒体最小启动命令。后续须先完成边界§2缺口、源码/控制数量复审，再由负责人另派真实实验。

只读校验冻结包（不会编译、启动helper或读取测试媒体）：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\CodexProjects\VideoKit\docs\coder\d1e1\tools\verify.py'
```

## 3. 显式工具编译与合成自检命令

下面是已执行过的工具命令记录，**不是默认自动执行步骤**。重新运行会改变已冻结产物/证据；应在另一个明确派发的工具修订批次处理，不能把重跑写回本次冻结包后继续沿用旧hash。

```powershell
# 首次编译（目标E1.dll不存在时）
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' -NoProfile -File 'D:\CodexProjects\VideoKit\docs\coder\d1e1\tools\build.ps1' -Compile
# 明确修复后重编：先保留既有DLL，不下载SDK，不运行媒体
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' -NoProfile -File 'D:\CodexProjects\VideoKit\docs\coder\d1e1\tools\build.ps1' -Compile -Repair
# 仅自建小fixture；不进入test_media/PF/61场景整批
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' -NoProfile -File 'D:\CodexProjects\VideoKit\docs\coder\d1e1\tools\launch.ps1' -Mode SelfCheck
```

build.ps1无`-Compile`只打印说明，generate_manifest.py无`--generate`、freeze.py无`--sources/--seal`均不写文件。JavaHelper无显式`--synthetic-helper`参数拒绝运行；R只通过`-Mode Helper -FixtureRoot`显式启动。正式包只允许默认Inspect/只读verify，不自动自检。

自检只在`D:\CodexProjects\VideoKit\docs\coder\d1e1\selfcheck\synthetic-*`生成4KiB输入、几十字节输出、固定8KiB journal槽和有界事件。每次开始核既有fixture体积，最终核全目录≤2MiB；当前5次共143,816B。没有稀疏2GiB假大媒体、memory provider冒充磁盘、mock dup、noop sync或真实native crash。自检证据中的PID/instance/start/exit时刻属于该批合成helper，不是C14/Android设备。

## 4. 停止、未知和证据

FrozenSession将任务登记在副作用执行前，row/task/global检查后才派发；deadline到保留原Task与预算，不重发。超时停止接纳/等待不是停止内核调用；完成前资源/缓冲继续属于原operation。具体场景还未全部绑定到此层，不能单独调用Native原语后宣称全控制门禁已实施。

Child传输超时标TRANSPORT_PENDING，不再盲目复用帧序；清理可发送一次EXIT并等待原Process实例，5秒未退出即OWNER_EXIT_PENDING，不Kill、不假报退出。G自己持有的guard/pipe/process/log必须另处理。当前自检都实际收到EXIT、确认同PID/start实例和exitCode0，收尾记录在selfcheck.json；没有残留helper或构建任务。

UNKNOWN close只有匹配owner实际退出才有进程私有资源释放证据，不能改成原close成功；父引用未证仍PENDING。journal损坏只保留已验证历史视图，ReadOnlyRecovery拒绝DEGRADED；不以旧快照重开writer。仅Flush(true)/FlushFileBuffers的实际调用成功属于OS data-sync事实，必要namespace/durability未证必须拒绝/NOT_RUN。

源码ZIP、编译产物和证据身份由source-manifest.json与freeze-summary.json冻结；校验脚本只读检查每项字节/SHA和ZIP条目。D1未通过、宿主JNI仍BLOCKED，未进入M0或设备实验。
