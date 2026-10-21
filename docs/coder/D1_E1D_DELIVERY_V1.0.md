# D1 E1D 完成交付边界集中修复交付 V1.0

2026-10-16。依据负责人 E1D 需求，集中修复 E1C-C01/C02 两项 P1，保留原 T02–T05 修复。在 `D:\CodexProjects\VideoKit\docs\coder\d1e1d` 完成本地编译、定向检查、61 行完整合成回归、证据审计与冻结。候选状态 **C01_C02_FIXED_SYNTHETIC_VERIFIED_PENDING_INDEPENDENT_REVIEW**，等待负责人安排整包独立复审；本窗口不自行派 tester 或实验。

## 最终证据

| 检查 | 最终选定证据 | 结果 |
|---|---|---|
| 完整合成回归 | `D:\CodexProjects\VideoKit\docs\coder\d1e1d\evidence\selfcheck-1792162234030690200.json` | 159 项断言 PASS；PF＋61 分支＋GC；执行根 `selfcheck/check-20261016T225034` |
| 定向检查 | `D:\CodexProjects\VideoKit\docs\coder\d1e1d\evidence\targeted-1792162366628428500.json` | 414 项 PASS：C01/C02 153、源/owner 139、恢复 33、短写 69、通用 20 |
| 只读审计 | `D:\CodexProjects\VideoKit\docs\coder\d1e1d\evidence\audit.json` | 573 项总数、执行顺序、预算、恢复、真实退出与关闭见证一致 |

只计以上最终 **573 项**。早期 393 项定向结果仍保留，不与最终 414 项重复累加；旧 E1/E1B/E1C 结果也不计成本批新通过项。E1D 只运行一次完整 J/R 合成回归，定向检查运行两轮；定向检查不启动 J/R、不读取媒体。

完整回归实际使用 351N＋83 新 query＋18 重放＝452 控制；输入请求 1,573,492B/59 次，剩余 30B 留在原行；目标信用 10、记录 32、输出信用 655,360B、验证请求 128B。64 个私有结果 cell 全部排空，cell 峰 1。受管资源峰 **23/24**，媒体句柄峰 5/6，64KiB 媒体槽峰 1/8，最终受管资源 0。Hub 64 次通知，最终 cells/queued/active/workersAlive 均 0、blocked=null。原 J/R 通过实际 wait 证明 code=0 退出，G/外层调用及所有受控测试线程均已返回，无本批已知任务或 IO 在途。

元数据请求/实际返回写量均为 6,396,288B，未知请求字节 0，HEALTHY；元数据文件峰 629,120B，累计写量与文件峰分开记。E1D 合成 fixture 累计 135,244B；两轮定向证据及本轮日志总量约 1MiB，精确冻结值见 freeze-summary，未超过 2MiB/4MiB 边界。

## 两项修复及逐路径映射

| 缺陷 | 活动实现 | 可观察回归 |
|---|---|---|
| C01：seal/fence 后晚完成仍交付 | `authority.py:SourceAuthority._delivery_locked/_decide_delivery_locked/complete/gate`；`gengine.py:Ops.open_j/read_j/seal` | 普通及 held 的 open/read 均重核原 operation 的 task/version/consumer/generation、当前 reservation、seal/global fence、handle 归属/disposition。单 seal 的交付先/seal 先两种顺序、全局围栏先、错绑定均检查真实 Future/交付次数及唯一释放；无同时 cancel 掩盖单 seal。 |
| C02：Future 同步回调在应用锁内执行 | `notifications.py:DeliveryFuture/CompletionHub`；`authority.py:PendingCell._post/_publish_outside_locks/_release_ready` | 真实 add_done_callback 在普通完成、held gate、end、cancel、deadline、GC 六条路径中，唤醒预先启动的另一线程取得同一 source/cell 锁。有限 Event 屏障及实际 join，无 sleep 猜概率；超时是失败或 Stop，不能假 PASS。 |
| C02：回调未排空却释放、无限扩张 | `gengine.py:Engine.private_cell`；`phases.py:Cleanup.__init__/release_gate/run/finish`；`controller.py` 异常分支 | 真实慢回调已发布 Future 但仍保留 buffer/operation/cell；drain/gate/close 到期 Stop、停止新接纳，受控回调实际退出后才释放和 join。固定 2 worker、8 cell/通知信用、每 cell 4 callback；超额 cell 与第 5 个 callback 拒绝。 |
| C02：决定与通知有间隔 | 同上；源锁内决定、Hub 锁外通知 | A 回调阻塞唯一 notifier，B 已决定成功但 Future 尚未发布；此时单 seal 不逆转 B。检查真实队列、后续成功、一次交付。active 私有资源已释放而 notifier 尚未返回的窗口仍保留容量信用；新 cell 拒绝，实际归还后可再接纳。 |
| C02：通知提交异常 | `PendingCell._post` | 受控 submit 异常保留 submit_error、Future 未发布、submitted=false、buffer/操作仍留账并停止接纳。测试仅在 finally 受控排空原取消结果，保留失败标志，不把失败改记成功或自动重试。 |

普通 complete 与 held gate 共用同一个源权威裁定，不重新 admit 旧操作，不新增 delegate。既接纳 read 采用保守规则：seal/fence/end/cancel 在尚未决定交付前获胜时丢弃结果并排空；交付决定已成功的结果不倒退。晚 open 的 H 仍由原 native owner 清理，discard cell 不等于关闭 H。

源锁/cell 锁只写一次 outcome。发布 Future 与其同步 done callbacks 由唯一 notifier 在 source/cell/Hub 等应用锁外执行。Future.done 先于 callback 返回是合法状态；只有 native 返回、gate 已到、全部注册 callback 实际退出，才执行私有 release/on_drain 并完成 cell 排空。每个 cell 一张通知信用，active 信用保持到 notifier 实际返回并原子归还，避免归还窗口超发。

## 预算与既有修复

PF/n01 既有 setup 内启动 G 本地 notify/deadline 两线程，各占一个 worker credit；GC/n31 既有 journalClose 内有界 join，两条线程实际退出才以 THREAD_JOIN_PROVEN 归还信用。新增的队列/截止扫描、一次性决定、通知与排空均为 G 内存步骤，无新 N/RPC/磁盘事务。manifest 的对应阶段 boundedEffects 与 callbackBudget 显式列出这些步骤。

维持 61 行/22 家族、PF16/GC32、452 分配/544 控制硬界、101 query、原 IO/事务/180 秒分配；每 N/D 最多两次 snapshot。原 PF admitted inventory 替代新 task 第一次 admission 写，完成写 task，不新增事务。T02 精确源绑定与接纳锁、T03 真实 owner 请求身份、T04 单调恢复/缺 shard UNKNOWN、T05 单次 exact_write/短写禁下游的定向回归均保留。

## 包与保留关系

- 源码与全源码依赖：`D:\CodexProjects\VideoKit\docs\coder\d1e1d\artifacts\E1D-source.zip`；当前有效产物 E1D.dll 与 JavaHelper 两个 class，本批本地编译一次成功，无下载。
- manifest：`D:\CodexProjects\VideoKit\docs\coder\d1e1d\manifest\branches.json`；源码清单与冻结摘要在该包 evidence，逐文件字节/SHA 关联源码、产物、文档及证据；只读 verify 核对 ZIP 全成员。
- `upstream-e1c` 保存 E1C 源 ZIP、freeze、source manifest、分支及 13 项 R1–R4 基线关系；嵌套 ZIP 继续保存 E1B/E1 源码依赖。原 E1C 16 个冻结文件＋430 个自检文件共 446 项只读 SHA 核验一致，未覆盖原 E1C 或删除失败证据。

限制详见同目录上层的 D1_E1D_IMPLEMENTATION_BOUNDARY/EXECUTION_APPENDIX_V1.0.md。未读取 test_media、未运行真实 PF/媒体/设备/Gradle/ADB/正式 run、未下载。requiredDurability、真实版本和运行时总资源口径仍 UNPROVEN；宿主 JNI BLOCKED，D1 NOT_PASSED，M0 NOT_STARTED，C14/P0/历史 FAIL 保持。573 项是修复候选的合成证据，不代表正式产品交付完成。
