# D1 E3 真实 L/C/Z 有限 IO 测试结果独立复核报告 V1.0

日期：2026-10-17。执行者：项目负责人；结果独立复核：VideoKit tester。依据：D1_E3_REAL_IO_TESTER_EXECUTION_V1.0.md。

**结论：PASS，限本机、本固定批次真实 L/C/Z 有限字节 IO 工具回归。新增缺陷0，61个场景完成、160条原执行断言，独立输出验证及原资源/关闭/退出证据符合要求，无在途任务。** 本次由负责人执行唯一一次；tester只读原结果，没有重读媒体或重跑。许可已消费，不退款、不自行下一批。

该结论不代表视频解码/播放、NAS、产品持久性、Android/C14或D1整体验收通过。五项产品namespace变体仍NOT_RUN_DURABILITY_UNPROVEN，D1 NOT_PASSED、M0 NOT_STARTED，JNI/P0及历史FAIL保持。

## 1. 原批次与证据身份

| 项目 | 原始事实 |
|---|---|
| batch | D1-E3-11a896d3c2c34483ba2dff60fa63f5c8 |
| freeze SHA256 | `7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709` |
| 唯一root | docs/coder/d1e3/runs/e3-11a896d3c2c34483ba2dff60fa63f5c8 |
| 原父 | PID37344，creation100ns=134366643480486090 |
| 原G | PID32588，creation100ns=134366643483703824，原exit0已观察 |
| 原J | PID33776，creation100ns=134366643488544661，原exit0 |
| 原R | PID43980，creation100ns=134366643489636299，原exit0 |
| result-manifest SHA256 | `870896d1063c465382a25a48fa501a22dc47f409e72ce48c003b17ae240e06c0` |
| preclose SHA256 | `688aa901d497018220b3210b6c0941c22479b00ba6293bf3242556deb27cb731` |

预约先G、claim先root/Engine，父子PID/creation、profile、外seal、reservation/launch原字节hash串联一致，coordinatorSecretVerified=true。tester未接收或保存明文凭据。此前凭据交接阻断已由负责人正式交接解决，本轮以原授权与claim证据为准，不修改此前准备审查的历史记录。

原driver、launcher和最终manifest均PASS；completion/resources accepted、reasons空。最终manifest complete/resultHashComplete/batchPassProven均true、原G退出已观察、原父process handle已实际关闭，未仅采信launcher早期状态。143个输出文件的精确集合、长度/hash及manifest自身计账独立一致；没有源.bin副本。

本轮只读verify一次PASS，54源码/90不可变/65runtime集合仍符合原seal。原封存中的PREPARED字段属于seal时事实，不能据此否认后续已执行。独立审计不导入候选模块、不调用OS采样，不stat/read/hash test_media。

## 2. 四个真实大文件窗口

profile B=2147483648，L声明及原opened合同长度3212959911 B，C4096 B、Z0 B。下列参数、结果及摘要来自原snapshot中的命令记录，已与最终global终结事件resultDigest交叉核验；未再次读取源。

| 窗口 | offset | J/R各请求与实际 B | J/R一致的SHA256 |
|---|---:|---|---|
| N1 | 2147418112 | 65536/65536 | `fbeb5351992afd0f9fc9f7266096b90c14377b68809a395a6414a663e2fe66f4` |
| N2 | 2147450880 | 65536/65536 | `a6e7a0490611bc8ad50d6cd51cfd3859040c6e1562301e54bb76763791a06247` |
| N3 | 2147483648 | 65536/65536 | `a91b60954623fb9fd972c86de15c965bc2d4268f96f3fd78330ae225f20d5be4` |
| N4 | 3212894375 | 65536/65536 | `cc7bb4088bb7c4bd9f169eb52dc71d8ffc091792e5809aa99df461bff590fe3e` |

四组P01-S分别在对应offset+i请求65536、65535、65534、65533 B，J每次合法返回1 B，四字节前缀与R在原offset读取4 B的摘要一致。四个checkpoint均UNFILLED/4，未冒称65536已填满，也未补读；下一外层65532 B请求按原预算本地拒绝。每组请求计费262142 B包括R的4 B，实际J4 B/R4 B分别保留。

四窗全文摘要、短读前缀摘要和原请求参数见 [独立语义审计](D:/CodexProjects/VideoKit/docs/tester/D1_E3_REAL_IO_EVIDENCE/semantic-audit.json) 与 [原窗口命令解码](D:/CodexProjects/VideoKit/docs/tester/D1_E3_REAL_IO_EVIDENCE/decoded-window-commands.json)。它们支持本次已读窗口的跨actor一致性，不证明全片内容hash或快照。

## 3. opened身份、查询及完成语义

32任务/61个原snapshot shard按header、digest、有界解压及最高有效seq选取。逐项核56个源guard/H/REF记录：原physical identity、length、mtime与同version guard一致；G guard为readOnly/share1，原H/REF与之绑定。包括输出alias拒绝探针保留的guard，未把空version误作普通源版本。

原退出回执身份metadata累计G116/J63/R53，各≤512，extraRPCs=0、extraSourceBytes=0。R计数含输出身份查询。每次正长度READ前对原opened对象重查、同同步区内先query再seek/read的保证，来自已核冻结源码/产物及本次原完成、查询计数和身份链；没有每次query三元组的独立逐条raw trace，不能补造。share1为固定打开参数，元数据query不反查share mask；受控opened访问不等于防已有可写映射或原子命名空间快照。

PF恰1条、61个场景ID唯一且顺序完全匹配批准manifest，P10-D/P10-C在末尾；原62是PF＋场景checkpoint数，未与场景数混淆。160条原断言trace连续、count/hash与短回执一致，各row control/data/query/时间符合原分配。160是本次观察值，不是复用旧E2E固定判定值；准备280/Java探针25不累加。

独立核全部PF/场景N/D槽终结、18个批准Refused槽及原并发STALE_REVISION竞态结果，未接受非预期错误。三个WAITING分别以原cell native_done/gated/released/notification_done/notifier_quiescent/archived、discarded未交付、callback返回及原source operation done/nativeReturned证实排空；没有用Future.done或盘上WAITING当native返回。原64个source operation均有返回事实。

见 [独立控制及等待审计](D:/CodexProjects/VideoKit/docs/tester/D1_E3_REAL_IO_EVIDENCE/control-and-waiting-audit.json)。原P10关闭UNKNOWN由后续原owner退出证明资源释放，原故障/票据历史不被改成“原关闭成功”。

## 4. 输出字节与最终清单

Q01原J/R独立读取的32 B源前缀完全一致，SHA256=`beab5af9a46e668988b5f1fbb9a1793453ee4835388719180ee387ad8a87518b`。独立预期据该已保存前缀与批准写入计划构造，未再次打开源，也未使用输出自身定义预期。

| 输出 | 字节数 | 独立核验 |
|---|---:|---|
| T01/T05 | 各32 | 等于原J/R一致源前缀，hash同上 |
| T02 | 10 | Z、0、x、y、0、0、0、a、b、c；SHA `7d15403b09dff06a0fdcc2393f99e7e5b9263d1766c4883084855ddf89524227` |
| T03/T04 | 各1 | 等于源前缀首字节0x92；SHA `956062137518b270d730d4753000896de17c100a42f9e24f5acee2faa75d5fdd` |
| T06..T10 | 各0 | 原终止/abort计划空输出，仍须文件存在 |

10目标合计76 B，逐字节及SHA均匹配。原manifest列142成员，manifest自身另计，总143文件/719649 B。完整原输出只读归档见 [最终manifest](D:/CodexProjects/VideoKit/docs/tester/D1_E3_REAL_IO_EVIDENCE/original-output-archive/execution/result-manifest.json)，逐文件hash见 [独立收取清单](D:/CodexProjects/VideoKit/docs/tester/D1_E3_REAL_IO_EVIDENCE/collection-integrity.json)。

## 5. 原资源、预算及时间

原G PF/n01前baseline、J/R原HELLO baseline未重置。本次6个实际周期，最大记录gap约1.906秒≤2.5秒，末次duration0.0为时钟粒度，最终OBSERVED/reasons空/finished支持原永久STOP和时限guard未触发；未补做OS采样。

| 角色 | 线程baseline→采样峰 | 句柄baseline→采样峰 | WS峰 B | private峰 B |
|---|---|---|---:|---:|
| G | 5→12（+7） | 159→208（+49） | 29315072 | 20291584 |
| J | 24→24（+0） | 266→266（+0） | 74276864 | 375201792 |
| R | 24→24（+0） | 496→496（+0） | 87760896 | 28000256 |

原G16/+12线程、256/+64句柄及内存256MiB/+128MiB，JR64/+32线程、512/+128句柄及J768MiB/R512MiB/+256MiB均满足。采样峰不是连续OS峰，逐周期未落盘的duration/PID或精确byte不能重构。

- fresh可用内存：父3408056320 B、child3392462848 B、原PF sampler3393007616 B，均≥2GiB。
- 托管资源峰23≤24、媒体峰5≤6、64KiB buffer峰1≤8；cell累计64/归档64/active0/retained0/峰1，达到累计硬界但未超。未强GC、退款或删历史换额度。
- observer identity3（借用2）、6周期、20开20关、同时自有峰1、最终信用0，无close UNKNOWN/nativeQueryPending。
- N351＋query83新/18重放=452≤硬544；输入请求1,573,492 B/59次≤1,573,522 B/59，validation128 B、目标10、记录32、output信用655360 B符合原界。输入是请求计费口径，不声称实际累计返回相同字节。
- metadata累计请求/写入均6,443,406 B，UNKNOWN请求0、HEALTHY；文件存量峰676,238 B，与累计覆盖写分别计账。
- 执行metadata719,573 B＋准备136,241 B＝855,814 B≤4MiB；实际输出76 B＋准备fixture8192 B＝8268 B≤2MiB。wrapper43,335 B≤196608，生产676,238 B≤3178496，未复制真实源计fixture。
- 最终global.log=93,482 B，其中event92,907 B≤104320、metrics575 B≤26752。原回执event92,833在最后n32意图事件前取值，差74 B保持原时点。
- 原生产elapsed约5.953秒≤180，checkpoint elapsed合计约5.672秒另列，不能冒充完整命令时长；负责人交接记录原唯一命令exit0，父回执没有200秒停止等待/PENDING。原G实际exit0由原Popen回执独立确认。

本轮原输出收取/已审只读verify及tester副本语义核对均计入有界读取；控制审计结束累计3,916,138 B/458次≤6MiB/512，包含一次因alias探针guard空version而停止的tester审计读入，修正后仅重读必要副本，不重开媒体或重跑候选。签发时少量汇总与最终manifest复核另记最终回执，仍保持总界。

## 6. 原收尾与证据边界

GC/n01..n31原顺序DONE；n32盘上READY_TO_CLOSE只证明意图，原短回执另证flush/fsync/close实际返回、remainingResources=0。J owner957c1168-2ab2-4bb4-aaab-2fe593903daa、R owner9ea0587a5f0d4b2ca509d652880903a7与原pid/creation/HELLO/退出链一致，二者原exit0。Hub两个原worker均实际entered/exited/joinReturned/THREAD_JOIN_PROVEN，CLOSED且无剩余worker/queued/active/monitorInFlight/credit。原native/source/private/observer均排空。

原IO shutdown(wait=True)没有独立序列化join布尔；依据原冻结控制流，其实际返回先于GC/n32日志关闭返回，再结合原owner退出与账本归零采信，不补造独立线程回执。原父Popen已观察同一G exit0并实际关闭原handle，spawn信用0、wrapper metadata/identity信用0，无UNKNOWN。driver/launcher/最终manifest均noInFlight=true，支持无在途结论。

原.q无逐query duration，原行完成和冻结0.1秒query guard支持guard未触发，不能重构逐查询时长。读取窗口摘要与opened三元组只适用于本次受控访问；历史全片hash没有重算，长度/mtime相同不证明全片内容未变。

## 7. 已执行、未执行与后续

已执行：本唯一REAL_IO批次的PF、31源＋30输出工具场景、GC32槽和原资源/结果收取；tester只读结果独立复核。无未执行的本批有限IO场景，无新增实际尝试。

NOT_RUN/未证明：五产品namespace durability变体、全片hash/快照、已有可写映射防护、视频解码/音画/字幕/播放、NAS、设备/C14、产品端到端及新批次。OS_DATA_SYNC_ACK/tool READY不等产品OutputToken/COMMIT；Q06不是G实际死亡重启。准备阶段未测的故障注入不能因本次正常运行一并计为通过。

建议负责人有限采信本次真实字节IO/资源/输出/收尾通过事实，再另行裁定下一阶段；不自动新建任务或补跑。原E2E FAIL/exit2/工具exit1/160/已消费许可、E2F有限重评、旧G369/+209和R519 FAIL均作为历史保留。本批新通过不能回写这些历史，也不能直接解除host JNI BLOCKED、Kit/Flutter/AAR/Android/licensing P0或C14限制；C14平板功能仍0。**D1 NOT_PASSED，M0 NOT_STARTED。**
