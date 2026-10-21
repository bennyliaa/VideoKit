# D1 E1C 五项集中修复交付 V1.0

2026-10-16。依据 D1_E1C_CODER_REQUIREMENTS 与 E1B 独立审查，集中修复4项P1、1项P2，在 `D:\CodexProjects\VideoKit\docs\coder\d1e1c` 完成编译、针对性合成检查、完整场景回归并冻结。状态 **T01_T05_FIXED_SYNTHETIC_VERIFIED_PENDING_INDEPENDENT_REVIEW**。请负责人安排整包复审；本窗口不自行派tester或实验。

## 本批结果与证据

- 最终完整回归：`evidence/selfcheck-1792159977751886300.json`，158项断言通过，执行根 `selfcheck/check-20261016T221257`。
- 最终针对性检查：`evidence/targeted-1792160323238457900.json`，260项通过：源/响应/owner逻辑138、恢复负例33、短写负例69、通用预算/资源回归20。
- **本批选定最终证据共418项**。前期185/249/258项检查和前一轮完整回归均保留，不重复累计；旧E1的80和E1B的168项不当作新结果。
- `evidence/audit.json`只读核验：61行实际顺序、PF16/GC32、各行deadline、32记录与admitted inventory齐全、恢复额度一致、原S17事实保留、原实例退出、n32外层回执与关闭前摘要SHA关联均通过。

最终回归：351N＋83新query＋18重放＝452控制；输入请求1,573,492B/59次，目标信用10、任务记录32、写信用655,360B、验证请求128B。未用30B留在原行，不补读。64个私有结果cell全部释放，同时峰1；受管OS资源峰21、媒体句柄5、64KiB媒体槽1，最终受管资源0。两个原J/R helper由实际wait证明code=0退出，无本批构建/helper/exec或已知IO在途。

该轮元数据请求与实际返回写量均为6,396,167B，UNKNOWN请求字节0、提交状态HEALTHY；文件峰628,999B。累计写量与文件峰分开。E1C多轮合成fixture累计270,488B，日志/证据约1.9MiB，精确冻结值见freeze-summary，保持2MiB/4MiB边界。两轮完整合成回归各自执行既定预算，不能把单轮452误写成所有开发自检累计仅452。

## 五项缺陷闭合映射

| 缺陷 | 修复入口 | 有意义负例与结果 |
|---|---|---|
| E1B-T01 P1 待完成响应/取消超时/ZERO | `authority.py:PendingCell/complete_source_response`；`gengine.py:Engine.private_cell/Ops.open_j/read_j/read_zero`；GC真实cell排空 | held与普通open/read均先创建私有Future；取消/超时完成具体错误，结果不交付，原操作及buffer租用继续持有。真实Engine allocator＋Ledger验证取消后第二租用BUFFER_LIMIT、gate后才能重用；owner引用退出不能代写G私有cell完成。完整场景实际J返回后观察Future仍等待，取消/超时后gate丢弃、交付0；ZERO实际bridge入口、J读取计数不增。 |
| E1B-T02 P1 consumer结束及句柄绑定 | `authority.py:SourceAuthority`共享同一RLock；活动Ops均调用该接纳点 | 已end(A)且B仍活时复开A拒绝、借B身份读A拒绝；task/version/consumer/generation错配和closed/UNKNOWN/in-flight对象拒绝。end/cancel与open/read的两种确定并发顺序均验证：后接纳拒绝，先接纳只排空，B状态不变。逻辑反例不冒充实测OS delegate。 |
| E1B-T03 P1 旧owner布尔快捷拒绝 | `capture_ready_request/validate_ready_request`、`Ops.ready/takeover/cancel_output`同锁仲裁 | 删除ready(old=True)路径，提交owner实例、epoch、export、handle/grant、attempt、revision与receipt；Q07捕获真实e1请求，e2持久接管后原样发送并得STALE_OWNER。未接管合法请求成功，错误epoch、receipt、其他绑定分开拒绝。 |
| E1B-T04 P1 恢复降计数/缺shard | `Flow.transaction`的PF持久inventory、`recovery.py:recover`、活动J恢复回调 | 同身份两个快照、inventory最小信用及可信q日志逐维max；日志较少/部分/身份错不退款且标UNKNOWN。已接纳shard缺失保留最小使用量与unknownShard，不能当0；无inventory不能声称未接纳。覆盖GC跨shard max及无raw handle重建；正常32记录恢复精确一致。 |
| E1B-T05 P2 元数据短返回 | `Store.exact_write/ensure_writable`及`phases.py` | snapshot、行/q/global event、setup header、最终receipt单次有界write核实际返回；短/None/非法/异常立即UNKNOWN，无补写、无伪提交。自有writer注入和真实Flow接纳顺序检查证明下游action=0、RPC未授权、后续接纳仍停止；请求信用/实际written/未知请求分别记。 |

## 控制与事务差异

没有新增R4控制token、RPC或媒体请求；ZERO为原P02-ZERO规定的零delegate D入口。新增inventory在每个新task第一次请求中，**用PF admission事务替代该task的admission事务**，完成时再写task：最多两次8KiB事务。PF自己的初次记录含自身inventory。已知first grant/res等纯元数据请求因持久最小信用需要现在可用两事务，仍不超过原上限；额外累计元数据写已如实计入。

held操作只先持久ADMITTED，私有完成暂不标DONE，放闸用原有gate事务记录真实排空及响应；没有额外“释放”RPC。普通完成同样走cell，自动gate前在源权威锁内核生命周期；takeover与ready提交使用同一锁。

## 文件与保留关系

源码：`artifacts/E1C-source.zip`；有效编译输出：`artifacts/E1C.dll`、`artifacts/java/videokit/e1/JavaHelper*.class`。两次本地编译成功：首次保留旧输出名E1B.dll于新E1C目录作为历史，第二次统一E1C协议key/产物名；启动只加载E1C.dll，不把该历史DLL当旧冻结包或有效启动入口。

`manifest/branches.json`含61行、修复映射、阶段与事务说明；`evidence/source-manifest.json`和`freeze-summary.json`给源码/产物/证据字节与SHA。完整上游E1B源码ZIP及冻结关系在`upstream-e1b`，其ZIP内仍保留E1源码关系。原E1B冻结854个文件只读核验一致，R1–R4共13份基线继续核验；原E1/E1B/C14/失败证据和样本未编辑。

限制与启动详见 `D1_E1C_IMPLEMENTATION_BOUNDARY_V1.0.md`、`D1_E1C_EXECUTION_APPENDIX_V1.0.md`。未读取test_media、未真实PF/媒体实验、未Gradle/ADB/下载/设备或正式run目录。requiredDurability、真实版本与运行时总资源限制没有因修复变PASS；JNI仍BLOCKED，D1未通过，M0未启动，历史FAIL保持。
