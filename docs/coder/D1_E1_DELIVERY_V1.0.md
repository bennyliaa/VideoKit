# D1 E1 工具源码与合成自检交付 V1.0

2026-10-16。按[E1需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E1_CODER_REQUIREMENTS_V1.0.md)保存源码、机器清单、编译产物、合成证据和冻结工具。**交付状态：PARTIAL_IMPLEMENTATION_NOT_READY_FOR_MEDIA_EXPERIMENT。** 这批有真实可编译实现和80项合成自检，不是完整61场景harness；尚未满足E1全部实现要求，不建议直接派真实媒体实验。具体未完成代码工作列在边界§2，不以缺设备或待运行掩盖。

## 1. 完整材料位置与身份

| 材料 | 路径/说明 | SHA-256 |
|---|---|---|
| 实现边界 | [D1_E1_IMPLEMENTATION_BOUNDARY_V1.0.md](D:/CodexProjects/VideoKit/docs/coder/D1_E1_IMPLEMENTATION_BOUNDARY_V1.0.md) | `d4b677a02efc1c1d6cfe8949931ec39f816b075273287232a892be6e3faee0d8` |
| 执行附录 | [D1_E1_EXECUTION_APPENDIX_V1.0.md](D:/CodexProjects/VideoKit/docs/coder/D1_E1_EXECUTION_APPENDIX_V1.0.md) | `3f1b1f32dd425d31f1d5c91ebce7c39fbd1017514d26e1ac59af6f4c427ce053` |
| 源码ZIP | [E1-source.zip](D:/CodexProjects/VideoKit/docs/coder/d1e1/artifacts/E1-source.zip)，43,087B，11条目（5源码＋5工具脚本＋机器manifest） | `b3b71f5b899c34adb2c441af2fb7420f7d26d9f648090ed1357b3b71430a556f` |
| C#当前产物 | [E1.dll](D:/CodexProjects/VideoKit/docs/coder/d1e1/artifacts/E1.dll) | `1b234e574016431e78cde4a092be56c69f8ebdc06174536b5db5ef7b37758801` |
| Java当前产物 | [JavaHelper.class](D:/CodexProjects/VideoKit/docs/coder/d1e1/artifacts/java/videokit/e1/JavaHelper.class) | `91b097f8d043c7ad2dcced8313b2f700e45451ca919feea64b5047f736d703ab` |
| Java内部类 | JavaHelper$Owned.class，同产物目录 | `271661143d7d92aa45b9b55f9a5bfa230c3aa09399eed7f2fd5c30f3ac8d6a56` |

[source-manifest.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/source-manifest.json)逐项冻结源码原始字节；[freeze-summary.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/freeze-summary.json)另列三文档、所有当前/历史产物、证据及合成fixture的字节/SHA。本回执不嵌自己或freeze-summary的hash，避免循环；主动通知另给这两项实际身份。旧DLL仅历史，不加载。

## 2. 实现与检验结果

实现独立Core状态机、Windows native绑定、Java文件helper、.NET helper、G进程管理、冻结预算/事件层、真实双槽journal/只读恢复、机器manifest生成和只读完整性校验。具体入口/边界见上述实现边界表，不修改Kit公共API或C14。

本机没有.NET SDK，使用现成PowerShell7.6.5内置Roslyn编译，在.NET10.0.11宿主运行；Java21.0.10。已有独立.NET8.0.23 runtime未用于本工具，不声称.NET8兼容。无下载/新SDK/新依赖。集中主编译及4次必要修复重编全部成功，最终代码编译后80断言自检PASS；构建/版本历史在[build-info.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/build-info.json)。

最终[selfcheck.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/selfcheck.json)只证明：

- 三层预算先预留、空收费拒绝、row超额不发生副作用；合成阻塞超时仍保留原Task和请求计费，晚完成后实际结束。
- close预delegate可重试/实际close后ACK丢失/UNKNOWN模型、同revision并发、同command重放、三次耗尽/拒第四；真实wrapper关闭不因重放再次进入native。
- 双consumer/future-open、seal先赢、晚open、父guard计入释放条件、旧版本/旧通知隔离、一次完成闸门。
- writer元数据重放、真实引用证明去重、唯一send/take/claim、epoch先接管后旧ready拒绝；真实Windows guard阻止新写打开、实际DuplicateHandle、A关后B小写/FlushFileBuffers/close、独立验证read回SHA和receipt，READY先赢保留token。
- 真FileStream.Flush(true)、独立journal读取、损坏槽校验/DEGRADED拒当成功、已有journal未恢复禁止覆盖；Java helper独立验证并返回合成READY record。
- 两个真实J/R进程分别打开同一合成文件，独立读取长度/摘要/字节一致，Java零请求/EOF/close及.NET实际dup写读；原PID/启动时间/instance实际退出证据均留存。

80包含最终合成产物体积断言；不是80次媒体/设备测试。合成UNKNOWN故障native0、超时为受控合成阻塞，非实际native close错误/内核故障。恢复record由合成构造，未称真实导出回复丢失闭环。当前5次自检全部合成文件累计143,816B≤2MiB，日志/证据≤4MiB；J/R均已实际退出，无构建或helper在途。

## 3. 61分支与预算映射

[branches.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/manifest/branches.json)给61行→每token真实代码原语入口、requestId/并发组、共享task、数据/控制预算和未接线状态；PF16/GC32也完整列出。**映射不等于完整执行器。** 61行executionStatus均NOT_RUN，完整场景上下文/数据位置、各检查点/q时序和PF/GC自动执行尚缺，启动入口因此拒绝Experiment。

[manifest-audit.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/manifest-audit.json)离线核对仍为P176＋Q127＋PF16＋GC32＝351非query，query101，全控制452≤544；1,573,522B/59输入请求、10目标/32记录、写655,360B/验证262,144B、180秒，保留文件峰值3,178,496B及24总句柄/6媒体/8缓冲计划。未分配92控制不授额外步骤。metadata累计写与文件峰值分开。

这些是冻结门禁与机器分配，不是本轮真实实验实耗/整批达标证据。FrozenSession和Native/helper之间尚非不可绕过的完整调用链，所有层live-vector、跨行输出信用及两次元数据事务还需串联；不得因单模块测试通过放行总量/时限。R helper底层WRITE没有独立claim校验，G必须在真实驱动中先CanWrite并收费；目前不能将该通道当完整writer协议。

## 4. 保留与剩余条件

R1三份、R2五份、R3三份、R4两份共13原件SHA均与此前交付一致，见[preserved-baselines.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/preserved-baselines.json)。C14只读working-tree完整性核对PASS：342源/139证据/5产物；冻结摘要 `880b38f3896df2f6bed2657d54c7fb8a954d3d05d8c730faf1b11278726e7155`、源ZIP `69ca847d7c1947ae65eb3ed6e79d8ab50e21ac9463a1a686cdeda6cfef2d683d`。未重跑871断言，未修改C14/R1–R4、原需求或测试素材。

没有读取test_media媒体字节、执行PF/完整真实实验、创建正式run目录、Gradle/ADB、产品/M0、设备任务或模型下载。默认入口Inspect只看清单；源码/产物冻结校验只读。Kit独立/Flutter控制层/AAR/C ABI/框架许可、全部P0/历史FAIL不变；宿主JNI仍BLOCKED，D1未通过、M0未启动。

下一步必须继续完成边界§2列出的实现缺口，并独立审查：全61场景驱动、完整G/S/O↔J/R预算和证据串联、权威journal恢复、PF16/GC32含最终log结果见证。实际额外RPC/绑定/持久性能力不符要给具体差异，不能隐藏或扩大硬限额。源码认可并另获负责人派发后才可真实媒体实验；本包不满足该准入。

按用户已有通信授权，完整保存/冻结/只读自查后一次通知负责人 `01a107c3-2bf9-7fa0-94a0-234258ca6774`，明确“部分实现、不能交真实实验”，不自行派tester或下一批。通知结果以本窗口最终回复为准；失败保留报告，不反复绕过。
