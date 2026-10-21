# VideoKit 输出生命周期、验证与恢复协议

V1.0；2026-10-21；当前设计基线，非实现/性能/许可验收证明。项目PAUSED_WAITING_USER，D1未过/M0未启；仅文档更新，不派开发、补测、设备或恢复自动跟进。

## 1. 所有权与接口

宿主Sink独占提供授权临时WriteHandle；Kit无源改名/覆盖/删除/COMMIT权。逻辑操作都带exportId/handleId/requestId，真实调用只由一个任务owner串行派发。

| 操作 | 前置/结果 | 关键约束 |
| --- | --- | --- |
| preflight(preset,requiredCapabilities) | 顺序/随机/seek/空间/验证能力报告 | 不够在open前拒绝；未知剩余空间不假精确 |
| openTemporary(exportId,requestId) | 唯一handleId/outputGeneration | 同ID去重，同ID不同参数拒绝；不新开第二输出 |
| write/seek/flush/close | 实际结果与原返回状态 | 同原缓冲/handle；close物理一次，pending/未知不可二close |
| openValidationLease(handleId) | 只读验证句柄/原租约 | 仅写者finalize/flush/close真实归还后可开；不绕过Sink用路径打开 |
| reportValidation(validationId,checks) | 不可变验证结果 | 可由受信宿主等价验证回调代替，但须bind输出身份/plan和原返回 |
| markReady(exportId,validationId,requestId) | 唯一OutputToken | 验证成功/验证租约原返/全部写者关闭之后；不等业务COMMITTED |
| queryOutputStatus(exportId,handleId?) | 版本化逻辑/原返/validation/token/cleanup快照 | 无副作用；不能顺便重读原流/新建句柄 |
| abort(exportId,requestId) | ABORT_REQUESTED→已确认ABORTED | 停准入、等待原写/验证/回调归还，再宿主清理；未知不假完成 |

这些是正式实现前待冻结接口方案，不在现有D1artifact添加方法或重跑测试。验证回调与query需要宿主能力支持，否则BLOCKED且无READY，不能隐式生成未授权暂存路径。

## 2. 仲裁与状态转换

业务状态采用OPEN/WRITING/FINALIZING/VALIDATING/READY/ABORT_REQUESTED/ABORTED/FAILED；另有独立originalReturnState=PENDING/RETURNED/UNKNOWN及cleanupState，UNKNOWN不是READY或ABORTED的别名。持久记录先于外部发布token（存储能力需评审），单任务仲裁器确定一次终态。

| 当前位置/事件 | 新状态/动作 |
| --- | --- |
| OPEN有效写入 | WRITING |
| 写完且资源准备收尾 | FINALIZING，flush/close一次 |
| 写者均真返 | VALIDATING，授权只读验证 |
| 验证合格+原验证者真返+cancel未赢 | 仲裁markReady；成功发布READY/OutputToken |
| 任一非READY阶段cancel赢 | ABORT_REQUESTED，停止新任务；资源真返并清理确认后ABORTED |
| markReady在途但结果未知 | 保持待确认/UNKNOWN，只查询，不并行abort或重复物理markReady |
| query确认READY | 返回同一token；取消请求报告TOO_LATE，不转ABORTED或删ready输出 |
| query确认未READY且原调用已返 | 同一仲裁器处理取消/失败，按记录决定下一合法操作 |
| query不可用/调用永久未知 | 隔离输出、停后继，保留原owner/预算和人工恢复事项，无补ACK/退款 |

外部markReady callback的副作用与本地状态需有幂等operationId和可查询记录；仅自称幂等不足。重送网络/跨进程消息只允许向保证同ID去重的broker重取同逻辑结果，不重复原写/close/markReady；若broker不能证明“不产生第二物理调用”则禁止自动重送。

## 3. 验证与提交边界

验证对实际容器/编码、可重开、尺寸/方向/时长、适用音画与实际遮罩覆盖给结果，失败任一安全必需项不得READY。验证读也受空间/字节/时限/源消费者预算，不依赖平台仅声明支持。只读租约通过host授权，不对ready前未知输出擅自移动/释放。

READY只表示Kit临时输出合格，宿主还核存在/权限/版本/业务策略并让用户确认后COMMIT。宿主删除原件等是其独立业务，本SDK不得提供删除源API。COMMIT/abort清理不能复用正在返回UNKNOWN的handle。

## 4. 进程退出与恢复

宿主broker持久索引记录exportId/临时所有权/操作ID/最后已确认状态（不含凭据）。进程死只表示某worker不能继续，不自动证明所有宿主读/验证/写callback归还。broker核对generation/实际端点/handle状态后query：READY恢复同token；确认未READY且所有原资源已返才清理隔离临时；未知保留隔离与诊断，不扫目录猜身份/删所有tmp。

不承诺断点编码恢复。用户重新导出是新exportId/新临时目标/新预算，旧任务证据与UNKNOWN独立保留。硬终止只在未来准确批准的任务范围和安全策略下执行，本设计不是当前强停任何历史进程授权。

## 5. 验收

OUT-01能力先验/同ID去重；OUT-02随机回写/短写/空间/flush-close失败；OUT-03验证租约与源不变；OUT-04READY-cancel先后/晚返回/查询不可用；OUT-05worker死/重启/隔离清理；OUT-06宿主COMMIT权限分离。M4早期集成、M6完整安全、M7宿主回归，全部待正式恢复与阶段准入。
