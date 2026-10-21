# VideoKit 多实例资源、音频与故障隔离设计

V1.0；2026-10-21；当前设计基线，非实现/性能/许可验收证明。项目PAUSED_WAITING_USER，D1未过/M0未启；仅文档更新，不派开发、补测、设备或恢复自动跟进。

## 1. 资源树和优先级

宿主注入ResourceBudget，不使用全局播放器。树：HostBudget→Session/TaskLease→decoder/surface/PCM/model/worker/IO子lease。reserve成功后才创建，部分创建失败只归还真实返的资源；UNKNOWN保留占用。resourceReport包含reserved/actualKnown/unknown及消费者，不以一个会话释放冒整个源租约可移动。

默认优先：当前可见发声会话的基本播放→其他可见媒体→离屏缓存→ASR/翻译预取等可选新任务。此为新准入排序，不是强抢正在调用的buffer/模型；用户编辑/导出预算在正式批次预留，不静默饿死原P0。公平策略采用队列+优先级和有界等待，准确槽配额/等待/热阈值按指标表冻结，拒绝时结构化告知宿主。

宿主控制4/9默认布局和12视频硬上限，实际活跃数以设备预算判定；不足时静态占位/减活跃/离屏暂停由宿主选择，不把声明12路当可解12路。压力先停可选新任务/预取，后请求宿主降级，不取消其他槽原调用或强关缓存。

## 2. 唯一音频切换协议

AudioCommand={hostAudioEpoch,sourceSessionId?,targetSessionId?,actionId}；Coordinator是唯一owner，平台焦点处理可委托后端但不再另有竞争owner。

1. 检查epoch新于已接纳值并记录目标；命令串行，旧回调只补原返不改当前目标。
2. 先将旧声源静音/释放其声音许可，等待原操作确认；若未知，不给新槽发声许可，保持状态待确认，不能宣称两者安全切换。
3. 为目标申请焦点与许可，确认后取消其静音；失败保持全静音并告知宿主，不偷偷重新激活旧槽。
4. 新epoch中途到达覆盖意图但不能跳过旧原操作归还；目标释放/移除后全静音。锁定优先，任何晚到恢复都不能解锁。

## 3. worker及IPC边界

高风险解析/跟踪/导出按单会话或单任务隔离单元设计，不能以一个共享worker承担所有槽后宣称单槽隔离。worker数量受预算；无法给任务独立安全边界时BLOCKED/排队，不悄悄共用扩大故障域。Android具体Service/进程/权限配置必须验证，不能以普通exception捕获代SIGSEGV/OOM隔离；Apple等平台限制仍待原M9验证，不能假定跨平台保证。

IPC Envelope={protocolVersion,workerId,workerGeneration,sessionId?,bindingGeneration,taskId,requestId,sequence,messageType,payloadSize,payload}，消息白名单、最大长度及队列先验。handle跨进程通过授权broker token，不传任意路径/网络URL/凭据，共享buffer有retain/release与实际端点generation。重启worker使用新generation，旧响应拒绝但相关源/缓冲仍核归还。

worker DIED事件触发停止该单元新准入、静音/隐藏对应画面、记录原操作UNKNOWN/宿主端仍在途，broker按真实可核返回汇总资源；进程死不自动证明远端存储write已停止。只重启独立新任务并经范围/预算准入，不能重放旧scope或擅自杀其他项目。原生SDK不能独自承诺系统OOM不影响宿主，需专门故障注入证据后判能力。

## 4. 状态查询与恢复

ResourceSnapshot有leaseId/owner/unitGeneration、原创建与返回记录、未知原因；只读query不触发重试原close。失联时受影响单元故障，其他单元预算/纹理不被全局清空。宿主重启恢复只读记录与隔离任务，不复用裸PID；终止/清理必须准确对象和已批准策略，此文件不授权处理当前历史UNKNOWN。

## 5. 验收

RES-01原1/4/9/12视频/静态/动态图混排与拒绝；RES-02音频切换各种先后/未知/焦点失败/锁定；RES-03可见性/热/队列公平；ISO-01单元崩溃/OOM/卡住/坏消息；ISO-02worker重启/晚代响应/bufferbroker原返；ISO-03输出任务死亡与宿主只读源安全。M3资源、多实例，M5/M6高风险任务，M7宿主，M9跨平台。D1原隔离可行性门保持，本文未判已通过，永久故障注入只可在未来正式范围执行。
