# D1 E3 真实有限 IO 执行计划 V1.0

2026-10-17。本文件描述后续唯一批次的执行合同，当前状态为准备未运行。负责人先审完整冻结包及 tester 结论，再决定是否正式释放独立许可并交接；本批不读取真实媒体字节，不启动真实 PF/full。

1. 只读核对外部提供的 freeze SHA256、完整源码及产物/profile/manifest/自检证据，确认固定机器与未使用批次。Inspect 不创建 execution/runs，不申请 claim，不开始 helper，不采 OS 指标，不触媒体。没有独立许可的直接真实请求拒绝。
2. 正式原父入口先校本批 seal 与精确 runtime 文件集，再核许可 commitment 与绑定运行时。CREATE_NEW execution 和 reservation 在启动 G 前完成，记录父 PID/创建时间、固定 batch/root、profile SHA、freeze 与 nonce；许可成功核验但 fresh 不足仍消费预约，不退款。
3. 父在单次 Popen 前预建强所有者，独立 spawn 资源上限 6（NUL 4、process/thread handle 各1），元数据操作上限1、身份查询原生 handle 上限1。父发布 launch.pending，经 write/flush/fsync/close 原返回后无覆盖改名为 launch.json。原 child 以父子 PID+创建时间与同一 reservation/launch 完成 CREATE_NEW claim；claim 之前不创建 Engine 或接触源。没有 retry 或第二个 G。
4. 父前置 fresh、child claim 后 fresh、生产原 PF 前 fresh 均要求可用物理内存至少 2147483648 B；失败立即停止接纳。G 原 PF 前 baseline、J/R 原 HELLO baseline 固定，不重采替换，不用历史机器信息作当前准入。
5. G 原 guard、J 原 opened-FD 和该行已分配 R reference 核验同一个 identity/length/mtime。share1/read-only 由固定 CreateFileW 参数实施，GetFileInformationByHandle 本身不能读回 share mask。祖先禁止 reparse、输出 CREATE_NEW、输入物理 ID 拒写等原保护保持。原 opened proof 缺失、变化或查询 UNKNOWN 阻止依赖行，不降级共享、不以历史 hash 替代当前证据。
6. 按原 PF、61 分支顺序执行实际 L/C/Z 的有限字节 IO，四个 L 窗口围绕真实 2 GiB；不复制或遍历源，不全片 hash。P01-S 合法正请求短读累计4 B 后保持 UNFILLED，下一次外层输入预算请求本地拒绝。所有查询、读写与关闭仍使用原分配，不添加 reference RPC。
7. 使用原清理顺序及 n32 原 flush/fsync/close 返回证据。通用判据核每个 checkpoint、原事件完成/预期错误/WAITING 归档、有序断言 trace、实际 geometry、claim 和返回 hash；资源门禁读取同一次原 observer 证据，不再采样。180 秒从原 budget 起点计至 cleanup 返回。
8. 原父等待最多200秒，仅停止等待。若未完成，写 PENDING 并继续持有原 process，原 child 持有全部未证明对象。只有原 G 实际退出且所有原所有权已知返回，才能清点并 hash 结果集；最终结果必须 AND completion、resource、exit0、父 handle 关闭与输出账。晚结果保留最初 PENDING，不覆盖历史证据，不另开收集进程。

唯一批次：`D1-E3-11a896d3c2c34483ba2dff60fa63f5c8`。唯一输出根：`D:/CodexProjects/VideoKit/docs/coder/d1e3/runs/e3-11a896d3c2c34483ba2dff60fa63f5c8`。当前二者均未启动/未创建。父 child launch、claim、结果均用 CREATE_NEW；任一步首 FAIL/PENDING 都保留证据与已消费预约，不补跑、不改为合成通过。

| 输入 | 精确路径 | 声明长度 B |
|---|---|---:|
| L | D:/CodexProjects/VideoKit/test_media/03_large_files/large_video_over_2GiB.mkv | 3212959911 |
| C | D:/CodexProjects/VideoKit/test_media/04_corrupted_files/corrupted_video.mp4 | 4096 |
| Z | D:/CodexProjects/VideoKit/test_media/04_corrupted_files/empty_video.mkv | 0 |

L 请求窗口为 `[2147418112, 65536]`、`[2147450880, 65536]`、`[2147483648, 65536]`、`[3212894375, 65536]`。历史全片 SHA256 只作来源声明，不在本次读取或重新证明。长度/mtime 相同也不能证明内容相同；当前版本保证只限原 opened-object 受控访问期间，已有可写映射不在保证范围内。

| 账目 | 原批准上限 |
|---|---:|
| 控制分配 / 硬界 | 452 / 544 |
| query | 101 |
| 输入请求 / 次数 | 1573522 B / 59 |
| 目标 / 记录 | 10 / 32 |
| 写信用 / 验证 | 655360 B / 262144 B |
| 生产元数据峰 / 合并硬界 | 3178496 B / 4194304 B |
| 托管 OS / 媒体 / 64KiB buffer | 24 / 6 / 8 |
| cell 历史总数 / 活跃 | 64 / 8 |
| 原执行 / 外层等待 | 180 s / 200 s |

已声明的实际请求模型为输入1573492 B/59次、验证128 B；它不是本批实际读取结果。每 actor 最多512次身份查询是另列元数据成本，没有额外控制 RPC、额外源字节或增加上述数据预算。

原 runtime-policy.json 逐字节保持：observer 1 s、最多201样本、gap≤2.5 s、单次样本≤0.1 s；事件区104320 B、指标区26752 B。G threads16/+12、handles256/+64、WS/private256MiB/+128MiB；J threads64/+32、handles512/+128、WS/private768MiB/+256MiB；R threads64/+32、handles512/+128、WS/private512MiB/+256MiB。退出后的零值不替换原峰值；采样峰不冒充绝对瞬时最大值。

每 case 的 OS_DATA_SYNC_ACK probe、五项产品 namespace 变体 NOT_RUN、工具 READY 与产品 OutputToken/COMMIT 的区分保持。Q06-LOST 仍为原有限恢复工具路径，未开展 G 实际死亡/重启、kill、权限、线程压力或设备试验。任何后续失败都应原样交负责人，不在原批次中改限制、降低验收或退款重试。
