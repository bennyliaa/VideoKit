# D1 E1B 工具实现续作交付 V1.0

2026-10-16。用户在本窗口明确“恢复开发”后继续原 E1；原 E1 与 C14/R1–R4保持只读。本包状态为 **IMPLEMENTED_SYNTHETIC_VERIFIED_PENDING_INDEPENDENT_REVIEW**，请先独立审查，不自动派测或启动媒体实验。D1未通过，M0未启动，宿主JNI仍BLOCKED。

## 交付与结果

根目录：`D:\CodexProjects\VideoKit\docs\coder\d1e1b`。完整源码和上游关系位于 `artifacts/E1B-source.zip`；编译结果为 `artifacts/E1B.dll` 与 `artifacts/java/videokit/e1/JavaHelper*.class`。机器清单位于 `manifest/branches.json`，包含61行实际入口、所有N槽、PF16/GC32、数据路径及明确执行次序。S17的P10-D/C在全部Q后执行。

最终完整合成联调：`evidence/selfcheck-1792157499032096500.json`，148项断言通过；另有 `evidence/negative-checks.json` 的20项独立逻辑/恢复负例，**合计168项本批检查**。旧E1的80项不计入。最终运行根为 `selfcheck/check-20261016T213139`，行结果包含PF＋61行；GC通过32槽及返回通道单独证明，不伪称第62条媒体分支。

最终351个非query＋83次新query＋18次重放＝452个控制；59次输入请求、实际请求1,573,492B，未使用的30B仍锁在原行，不转移；10个目标信用、32个记录；输出信用655,360B、验证请求128B。工具账本峰值21个新增受管OS资源、5个媒体句柄、1个64KiB媒体缓冲槽；该运行元数据文件峰值630,431B，累计元数据写6,141,446B为独立计数，不能当文件峰值或4MiB超限。全批多轮合成fixture累计1,081,636B；日志和证据冻结前约3.55MiB，精确值见freeze-summary。原2MiB/4MiB边界未扩大。

两个原helper实例均返回后由父进程实际wait证明code=0退出；GC/n32真实flush/fsync/close返回，剩余受管资源0。关闭前summary故意仍写PENDING，关闭证据仅来自原调用的外层回执，不能据磁盘关闭意图推断成功。没有本批构建、helper、exec任务或已知IO在途。

## 五项续作落点

| 原缺口 | 本包实现及证据 |
|---|---|
| 全61行上下文、D/q位置 | `src/scenarios.py`、`src/controller.py`；具体状态、真实读取/写入/dup和有限故障路径；q日志含afterControl/afterData；最终全61行按预算完成。 |
| PF16/GC32与最后log close | `src/phases.py`；逐槽接纳、跳过不挪用、逐owner死亡通知、父pipe/process句柄归还、n32原返回通道见证。 |
| 预算/claim/epoch/native串联 | `Flow.transaction/data/query`、`Engine.remote`、HMAC一次请求、J/R独立角色检查；只有持久接纳的请求能发送一次白名单RPC；R使用真实Windows DuplicateHandle、ReadFile、WriteFile、FlushFileBuffers、CloseHandle。 |
| 完整持久恢复 | 两个8KiB校验压缩槽，完整任务/命令/版本/票据/信用/所有者/计数；J独立读取，G认证恢复；`src/recovery.py`独立重建32个记录并核全局预算，恢复只读围栏，不重做ADMITTED副作用、不从裸数字重造句柄。 |
| 资源/文件/跨行信用 | `Ledger`、`Budget`、`Store`；先保留行/任务/全局额度，目标信用一次；元数据文件额度与累计写分开，未知在途保留，owner事实逐份释放；全批fixture/log另做累计门禁。 |

这些是实现与合成证据，不替代真实版本、崩溃持久性或媒体边界验收。边界详见同目录的 `D1_E1B_IMPLEMENTATION_BOUNDARY_V1.0.md`；启动、停止与核验详见 `D1_E1B_EXECUTION_APPENDIX_V1.0.md`。

## 历史与完整性

原E1 freeze身份：`d4df4446b3e9624e14579cf00492b0d9f0b8cec56d31e97a45cfb058127a9072`；本包 `upstream-e1`含原源码ZIP、manifest、冻结摘要和旧自检/源码清单，既保留旧身份又提供全部依赖源码。原E1冻结50个产物/fixture核验一致；R1–R4共13个基线文件由只读verify核验。未修改正式Kit API、C14、Flutter、Android或原样本。全P0、历史FAIL、73项设备待测及2项历史信号方法状态不变。

本批早期联调的行超时、顺序/额度错误、恢复帧和快照膨胀，以及两次入口语法错误均保留失败痕迹；不删除失败运行或将它们记PASS。主编译1次失败（C#明确赋值错误），两次修复编译成功，历史DLL保留；空的before-repair-1.dll是失败痕迹，不能加载。

本包等待负责人独立审查安排。真实媒体/PF/完整实验、Gradle/ADB、网络新依赖、设备与M0都未运行、未获本包放行。
