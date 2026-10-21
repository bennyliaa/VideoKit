# D1 E13K 唯一G只读补充实际执行报告 V1.0

2026-10-18；tester。机械核验与实际执行分别留痕，依据负责人已明确预授权执行一次；未重复申请设备权限。

**执行结论：FIRST_QUERY_FAILED / BUDGET_UNKNOWN / ORIGINAL_OWNER_RETAINED。** 第一只读query的通道额度判定失败，继而在70656B应用IO硬预算停止新读；没有EOF/EXIT或原Socket归还证明。第二query NOT_RUN。新Java51664及原工具session49433继续保管，无最终进程/reader/pipe/launch归还回执。不能将这次停止写成完整Android现状核查通过。

**机械结论：PASS。** 192/193 class完全原字节，唯一策略外class只改准确release常量；release/request/scope/launch/脚本/原owner主体/8157≤8192B预算独立通过后，才启动一次唯一四argv。报告：D1_E13K_MECHANICAL_REVIEW_REPORT_V1.0.md。功能基线R1通过不代表本次query通过。

## 1. 准确执行身份及次数

| 身份 | 本次准确值 |
| --- | --- |
| 新执行batch | d7b4ca4f-36a3-49c9-9b61-cdc7ebdcb5b6 |
| originalScope | aeefe32f-816d-4c0b-aca7-16f76dbd45ff |
| 原runtime SHA | 116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef |
| serial / endpoint | HA1Q6WXR / 127.0.0.1:5037 |
| typed release SHA | a5a7fd2f15c41f2a01f8e49f11b942c34bb23c9e890e5d6f8f275d49a7bffa03 |
| 功能review | f9e5a63acf2aea2fc51c9c71ec50ceba5ed080cdded46676cd7fd9cec6374583 |
| 实际JAR SHA | 09aec958873b2f4cf6fcb562e608d0143f7f865c742170bd30fd49432b5f9797 |
| 原新Java | PID51664，startUtc=2026-10-18T13:48:53.1610574Z，即21:48:53.1610574 |
| 原launch工具session | 49433；首次调用等待30秒后报告running，exitCode未返回/输出0B；没有再次poll |

机械核验时准确root不存在，无前次记录冲突；启动前4762份K核验输入冻结pins实际复核，保存唯一launch intent，未改已封候选或输入。只使用release/execution-command.json中的准确四argv：固定pwsh.exe、-NoProfile、-File、固定launch_once.ps1；没有额外用户参数、helper旁路、root/id/once变更或重发。

工具第一次调用返回running后，仅接收该原tool调用结果（functions.wait不是再次查询其Process），未write_stdin轮询新session或旧42537。之后只离线读取这次已经生成的文件用于审证，不发新网络/设备/原进程查询。

## 2. 原实际证据与停止点

实际root：`D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE`。

once=e13j-r1-g-readonly.once，实际177B；outer intent951B、原Java PID记录147B、PENDING marker145B均存在。生产第一query intent145B、facts696B、original.wire70656B。第二query目录缺席。完整raw不重复复制/echo，引用原文件及cutoff SHA。

wire SHA256：**4db90cf3bbe16197f22fdaeb1b873ef8b241d04ab1efee788c6f692fc1a350cb**。离线逐段核原wire：准确host:transport:HA1Q6WXR→OKAY，同一流的shell,v2,raw:固定脚本→OKAY，再一次准确close-stdin零载荷帧；TX289B。没有其他出站服务，SDK启动/server start/kill/version/feature均0。路由与shell接受不证明旧instrumentation或owner归还。

第一原生产T切片：

| 字段 | 实际值与含义 |
| --- | --- |
| cw / in / tx | 70656 = 70367 + 289；实际应用RX＋保守发送意图 |
| we / wr | 3 / 3；三个原写入进入/返回，非整个任务closeACK |
| rt / off / disk | 70656 / 70656 / 70656；本次留存尝试/queue接受/成功write一致，原wire长度独立匹配 |
| frames / rawQuota | 10 / 64868；rawQuota为已准入帧长配额，不表示完整全局正文已收到 |
| why | IOException:I_FRAME_LENGTH_OR_RAW_CAP |
| failed / qualification | true / FAILED |
| budgetUnknown | true |
| eof / exitSeen / exit | false / false / -999（未证，不是退出码0） |
| readerBody / readerAlive | true / false，仅T执行时点的字段 |
| socketReturned / physical | false / false |
| writerAlive / auditOwnClose | true / UNPROVEN；T不能自证writer或自身文件close |

准确路径：单query累计通道门在第10帧拒绝后进入同reader的受预算drain；余额耗尽则停止新增read，包括EOF偷读，原Socket不强关并保budgetUnknown。原query失败资格不是10秒late：T的late=false；外层后来55秒响应窗未见Java结束，才写PENDING_SAME_ORIGINAL_CUSTODY。不能混同逻辑资格和外层Process归还。

first query未返回成功的完整global activity processes/ps，无完整退出/EOF边界，不能调用第一证据派生门去选PID。第二条boot_id/stat/status/cmdline未启动；不得用截断内某些行补唯一instrumentation/无其他占用结论，也不能自动改grep或追加第三条。

## 3. 实际预算与资源状态

单query硬门实际停在cw70656，未越限；磁盘wire也精确70656。生产intent145＋facts696共841B，低于该query元数据2048B预留；P/T快照与自身close证明分别处理。once177B低于batch intent2048B。没有原wire/完整console额外副本或raw原文echo，未提额/借用/退款。

按已审生产分配逻辑：base116736＋一条已进入query72704=**189440B已占用预留**，总profile262144B，第二条72704B未进入，不转作第一条收尾。原exec65536B子项没使用但继续保留；Java32768及observer8192也保守保留，不能因为当前磁盘stdout/stderr文件0B就退款或断言原pipe无数据。outer最坏8157B（含准确command JSON204B）仍在8192B分配内；未收到最终console/receipt，因此不写成完整外层实际字节已结算。

截至cutoff 21:53:05（UTC13:53:05.818525）的已落盘证据：Process最终receipt缺席、launch最终≤128B摘要未收到；stdout/stderr文件当次读取0B不代表内存/管道为空。原observer仍有自身Process/readers/文件custody，Java原Batch/Op/Socket及non-daemon keeper按budgetUnknown保管；外层工具session49433是本次实际保管入口。新PowerShell OS PID未单独落盘，本轮未用CIM补查，不编造。

这类到限UNKNOWN在现profile没有重新读取/close解除入口，可能持续保管；不能期待多读一次自然EOF来退款或用词法退出补归还。是否及如何处理该新Socket/Java/外层宿主，必须负责人另派准确范围和原保管交接。本轮不调用清理/终止/第二close，不重建Process/Socket或用新UUID/目录再读。

## 4. 目的达成范围与未决分栏

| 对象/目标 | 本次结果 |
| --- | --- |
| 精确绑定 | PASS，唯一策略及输入/脚本/预算可核 |
| 第一query | FAILED/BUDGET_UNKNOWN，有实际固定服务握手与有限原wire；全局证据不完整 |
| 第二query/当前PID启动身份 | NOT_RUN，第一门未通过 |
| Android原scope唯一active/其他项目占用 | UNKNOWN，不能凭不完整dump判定无占用；未联系其他项目 |
| 原exec42537单次空收取 | BLOCKED / 0次；工具提供token上限，无法保证≤65536B原文本，不试探、不循环，预留不借用 |
| 旧v17主任务 | 原PENDING/UNKNOWN保持，未查询旧PID/旧handle；新只读对象不能补其ACK |
| 旧ps诊断 | 独立LOST_DIAGNOSTIC_OWNER_UNKNOWN保持 |
| H本地30384 | 独立RETURN_UNPROVEN保持，本轮未查 |
| 新K第一query | 新增独立E13K_QUERY1_BUDGET_UNKNOWN_OWNER_RETAINED；与三个历史未决分开，不是丢失owner |

本轮没有完成fresh Android状态/启动身份目标。实际完整输出在规定限额内未取得，不将部分资料升级为终止资格；不据历史PID或握手成功去处置任何对象。

## 5. 保全与后续边界

本次唯一once已实际消耗，不能重放launch、更名root/id或清除记录。冻结机械输入及report；原运行中stdout/stderr/将来receipt/launch console仍可能变化，不纳入不可变终态封印。cutoff index仅记录当时文件长度/SHA，不宣称所有原文件关闭或永不增长；原wire不另复制。

机械与执行独立审证位于 `D:/CodexProjects/VideoKit/docs/tester/D1_E13K_REVIEW_EVIDENCE`，包括原一次工具回执、启动intent、execution-checkpoint原计费核验和源文件cutoff索引。记录原session49433/Java51664/准确start/scope，保持其原保管，不循环轮询。收到同一原handle真实自然结果才另补报告，不改本切片；到限条件不靠新对象冒原归还。

后续仅请负责人评审当前新budgetUnknown保管/处置，以及未达成Android证据目的。任何新只读方案也须先另定准确范围/预算及已有owner处理，不能因本次失败自动缩过滤、提额或重复探针；所有行政终止仍另审。本轮安装/部署/产品/T07/外部终止0，D1 NOT_PASSED / M0 NOT_STARTED，P0/许可/历史FAIL保持。
