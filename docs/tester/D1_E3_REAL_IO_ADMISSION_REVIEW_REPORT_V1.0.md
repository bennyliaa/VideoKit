# D1 E3 真实有限 IO 启动层独立准入审查报告 V1.0

日期：2026-10-17。角色：VideoKit tester。依据：E3 正式测试/开发需求及负责人冻结交接。

**结论：本轮静态及只读证据审查通过，新增代码阻断项0。建议负责人在独立凭据交接问题解决、正式派发及现场前置满足后，批准本固定批次至多一次真实 L/C/Z 有限 IO。当前未授权或执行真实媒体/PF/61，不消费预约。**

G/R 新原生路径、真实大文件窗口、完整入口集成和现场资源轨迹尚未实测。280条纯准备检查与25条Java自有文件探针不能证明这些项目已通过。D1 未通过、M0 未启动，JNI/P0/C14及历史FAIL保持。

## 1. 整包与只读核验

| 项目 | 结果 |
|---|---|
| E3 freeze SHA256 | `7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709` |
| E3-source.zip SHA256 | `aa966284378778d799d473446e744a939a5b83817c867fce13eaea96b84902e7` |
| 源码/不可变/runtime集合 | 54/90/65，逐长度/hash、精确集合及ZIP成员一致 |
| 状态 | PREPARED_PENDING_COORDINATOR_HANDOFF；execution/runs不存在，正式预约未消费 |
| 原历史产物 | E2C.dll＋原Java共10项仅作只读基线 |
| 新runtime产物 | E3.dll＋java-e3共13个class；集中C#/Java各编译1次，repair0 |
| 新E3.dll | 84480 B；SHA256 `9e5b0208402917012db518dc054c497b8855c2ca5fe7917a13fc95cf69a61d3b` |
| 本轮tester活动 | 只读verify1次、自有静态/hash/AST及原探针回执核对；未重跑检查/探针/编译 |

只读verify在外部expected seal约束下PASS。读取实体文件103,494,201 B/100次、ZIP逻辑成员104,793,631 B/133次，总208,287,832 B/233次≤256MiB/8192；压缩容器实体字节与成员解压字节均计入。完整E2F源码ZIP及其更早依赖按冻结成员承接，不递归重开全部历史ZIP。准备metadata136,241 B、fixture8192 B，均在预留界内。

生产32源中13文件有适配变化，详见 [独立源码差异](D:/CodexProjects/VideoKit/docs/tester/D1_E3_EVIDENCE/production-diff.txt)。SourceAuthority/PendingCell、CompletionHub及原runtime_metrics字节保持；future/compact和原关闭票据关键链未被改写。原runtime-policy逐字节保持，61分支N/query/IO/time及operations分配未改。

证据见 [独立封存核验](D:/CodexProjects/VideoKit/docs/tester/D1_E3_EVIDENCE/independent-package-audit.json) 和 [原始验证范围核对](D:/CodexProjects/VideoKit/docs/tester/D1_E3_EVIDENCE/independent-scope-review.json)。只读verify PASS仅证明冻结一致和已记录准备事实，不是执行许可或真实结果PASS。

## 2. 真实profile、版本与首字节前门禁

仅授权声明的三个精确本地路径，未stat/read/hash这些路径：L=3212959911 B、C=4096 B、Z=0；B=2147483648。四个L窗口offset为2147418112、2147450880、2147483648、3212894375，各请求65536 B。输入profile的旧stat/hash已改为明确历史声明，不能作为当前版本快照。

G 的guard仍由CreateFileW(read-only/share1/OPEN_EXISTING)取得原HANDLE，opened length必须等于本profile声明长度。J同一OPEN帧及本行已分配R reference接收G预期physical identity/length/mtime；opened proof缺失、不匹配或查询未知均拒绝依赖访问。G [source_identity](D:/CodexProjects/VideoKit/docs/coder/d1e3/src/gengine.py:331) 在依赖访问前重查原guard三元组，并与本行有效reference缓存及原opened记录一致核对。

J [StrictInput](D:/CodexProjects/VideoKit/docs/coder/d1e3/src/JavaHelper.java:55) 由FFM CreateFileW获得一个原HANDLE，将该值绑定到原FileDescriptor/FileInputStream；正长度READ在原Handle同步区调用requireInputVersion后才seek/read。元数据查询借用原FD，不重新打开路径取得“相同”证明。初次guard不匹配或后续版本变化锁存blocked，保留原对象供关闭。原生open已返回无HANDLE、open结果UNKNOWN、已开HANDLE但绑定失败分别处理；后者保留rawHandle以供既有票据一次关闭。

J绑定成功走原stream.close，未绑定走CloseHandle(rawHandle)，closeAttempted防止不明关闭被再次调用；关闭异常仍为UNKNOWN，不能重试换成成功。A05自有注入构造保留，正式生产OPEN使用strict构造。Java私有FD/FFM路径仅适用于固定Windows x64/JBR21运行合同；不能由此推断产品host JNI已解除阻断。

R [OpenedMetadata/RequireInputVersion](D:/CodexProjects/VideoKit/docs/coder/d1e3/src/Native.cs:150) 在原NativeFile同步区完成。初次expected guard与原opened baseline一致后，正长度ReadAt/ReadDigest先QueryMetadata，再SetFilePointerEx/ReadFile；查询失败/变化使versionBlocked锁存。分配对象及CloseTicket先记录，即使元数据证明失败仍有原票据可供原owner收尾，未通过重开源文件取得证据。

G/J/R各512次opened身份查询上限，失败的实际查询尝试也消费计数；J/R通过已有READ/EXIT回执返回计数，无新增控制RPC或源字节。R计数还包括输出对象原有身份查询，不能全算源查询。祖先检查、最终属性检查及包装层元数据另列，不把“66个祖先节点上限”当全部元数据调用数。

输入精确路径、输出独立根/CREATE_NEW、祖先reparse拒绝和输入physical ID拒写链保持。它们是受控本地命名空间下的条件，不宣称对敌对祖先替换的原子保护。share1是固定打开参数，不由GetFileInformationByHandle反查。identity/length/mtime相同不证明内容相同，已有可写映射不在保证范围；当前合同是原opened对象受控访问区间，没有全片hash或快照承诺。

## 3. 一次性授权与UNKNOWN所有权

固定批次 `D1-E3-11a896d3c2c34483ba2dff60fa63f5c8`，固定root为本包runs/e3-11a896d3c2c34483ba2dff60fa63f5c8。默认Inspect无资源采样、目录、媒体或执行副作用。

[OnceAdmission.reserve/claim](D:/CodexProjects/VideoKit/docs/coder/d1e3/tools/e3_admission.py:250) 绑定外部seal、精确runtime集合、机器LZF、原CPython身份、profile hash和源码固定secret commitment。任意approved JSON或profile数据不能解锁；即使取得模块私有issuer，缺独立secret也不能签发RuntimePermit。claim持久CREATE_NEW后才签发进程内许可，Engine还要求类型及root/profile/commitment/HMAC一致。

父在G之前CREATE_NEW预约；预约后fresh不足仍消费、不退款。launch暂存完成exact write/flush/fsync/close后一次无覆盖发布；child以原父子PID＋creation完成claim，先于root/Engine/媒体。父仅一次spawn，凭据经child临时环境传递，child先pop再导入生产代码，helpers不继承，receipt不写凭据。

180秒包含原budget起点至cleanup实际返回，超时/UNKNOWN不能作成功。外200秒只结束有界等待；原父持有原Popen，原child强留Engine/Channel/原生所有权。未排空不扫描活动root，不凭进程析构/空集合退款；原close UNKNOWN只保留不重试，首PENDING与晚结果分文件保存。没有kill、换owner、第二G或补跑授权。

执行凭据目前未交付。负责人告知此前凭据传送被自动审批拒绝，具体拒绝理由未随本批交接提供；tester未索取、重试或绕过。该外部执行阻断与本轮代码审查分开记录；即使本报告建议条件准入，也不能据此启动。

## 4. 参数化完成、资源、结果层

新 [completion_evaluation](D:/CodexProjects/VideoKit/docs/coder/d1e3/tools/completion_evaluation.py:281) 接收本批manifest/preclose/witness/claim/events，不依赖E2F固定batch/hash/160或原FAIL。仍核PF首条、61精确ID集合/唯一性/批准顺序、逐行control/data/query/time、批准Refused和三个WAITING实际归档、GC31个DONE及n32原flush/fsync/close返回。P01-S四个合法1B短读仅记UNFILLED/4，不冒称填满窗口，不追加读完；下一外层请求由原预算拒绝。

断言trace最多1024项、seq连续、row受限、label≤160字，preclose完整保留，原短回执携count/hash；数量与返回hash相互绑定，不固定160。语义有效性依赖冻结Engine.check原控制流，trace不是第三方运行证明。完成模块不单独证明原G退出或全程时长。

[resource_gate](D:/CodexProjects/VideoKit/docs/coder/d1e3/tools/e3_driver.py:73) AND核原claim的G身份、J/R原HELLO身份/退出、原observer永久STOP事实、原基线绝对值与增量、fresh、Hub/native/private/metadata/ledger以及512计数界。driver仅在原完成、资源和quiescence同时成立后返回PASS；父还要求原G exit0及原process handle关闭。

[最终结果收取](D:/CodexProjects/VideoKit/docs/coder/d1e3/tools/e3_runtime.py:472) 只在原退出和所有权明确后扫描固定root，核preclose原返回hash、精确10个输出目标、当前文件hash清单及总账/manifest自身字节后产生batchPassProven。launcher早期状态带finalResultManifestRequired，不能只看其provisional PASS。最终hash证明文件集合与原结果绑定；真实字节内容仍需本批原J/R独立读比、输出验证及tester实际结果复核，当前未取得这些真实证据。

query与sample的逐项duration记录能力沿用既定边界：原源码guard/STOP及完成返回可支持guard未触发，但未落盘的逐项精确时长不能补造；采样峰不是连续OS峰。IO线程没有独立序列化join布尔，实际GC/n32返回须结合冻结shutdown(wait=True)控制流及原所有权证明采信。

## 5. 已有验证及实现风险

280条纯检查为静态/内存模型，包含两个未来batch、不同freeze/root及173/181条断言模型，语义负例重新绑定模型hash，覆盖错hash、缺重乱额外/PF缺/未完成、trace错误、WAITING未排空、n32仅意图、原资源UNKNOWN/超界、错误真实geometry及UNFILLED。它们没有真正创建RuntimePermit、原G/J/R或真实claim，不能以“280通过”代替启动层实测。

两个Java自有4KiB探针原stdout/字节/hash与记录一致、两个原exit0：

| 探针 | 查询 | seek/read | 请求/实际字节 | 原HANDLE关闭 |
|---|---:|---|---|---|
| strict-success（13断言） | 2 | 1/1 | 2/1 | 原一次open/close返回 |
| strict-guard-mismatch（12断言） | 1 | 0/0 | 0/0 | 原一次open/close返回 |

它们支持当前Java同HANDLE绑定、正短读及初次guard mismatch阻止访问。**没有实测G新inspect链、R新metadata/baseline/read链、Java读后版本变化/FD绑定失败/CloseHandle UNKNOWN注入、真实大文件seek或全入口集成。** 静态上已找到对应拒绝/票据/保留路径，未发现必须先修的具体缺陷；上述项目应保留待真实运行证据，不能预写通过。本轮也没有再次执行A05或以两个新探针冒称旧A05整套重跑。

## 6. 可执行范围与硬前置

仅建议正式另派本固定一次真实L/C/Z有限IO，范围为PF＋原61工具probe＋原GC；不包含素材复制、全片hash、解码、NAS、设备、杀进程/重启、权限或线程实验。

正式派发前须解决独立凭据交接、明确授权本batch/外seal/唯一新root，复核runtime精确集合与未消费状态。正式入口内父fresh、child fresh、生产PF fresh均≥2GiB；原G PF/n01前基线及J/R原HELLO基线固定，首字节前当前opened身份/length/mtime/share合同成立，不能用历史hash替代。任何拒绝、首FAIL/PENDING不退款、不降低门槛、不自动再派或补跑。

| 预算类别 | 原界保持 |
|---|---|
| 控制/硬界/query | 452/544/101 |
| 输入请求/次数 | 1573522 B/59；计划1573492 B为模型值，尚无真实结果 |
| 输出/验证/目标/记录 | 655360 B/262144 B/10/32 |
| 资源/media/buffer；cell累计/活跃 | 24/6/8×64KiB；64/8 |
| 时间 | 原180秒；外200秒只停止等待 |
| G | thread16/+12，handle256/+64，WS/private256MiB/+128MiB |
| J/R | thread64/+32，handle512/+128；J内存768MiB、R512MiB，增量各256MiB |
| observer/log | 1秒/201周期/gap2.5秒/返回后0.1秒；event104320＋metric26752=131072 B |
| 独立wrapper | metadata196608 B；父spawn预留6、metadata峰1、identity峰1，非生产24账内零成本 |
| 源码/完成证据/结果读取 | 每父/子源码≤256MiB/8192次；已关闭preclose+log≤262144 B；最终结果≤6MiB/512次 |

准备metadata≤819200＋生产3178496＋wrapper196608=4MiB；准备fixture≤1441792＋真实输出fixture655360=2MiB。源码ZIP不当运行日志，真实媒体源不复制为fixture。累计覆盖写入与存量峰分开，新增身份元数据及包装层成本另计，不藏入452。

五产品变体继续NOT_RUN_DURABILITY_UNPROVEN；OS_DATA_SYNC_ACK及工具READY不是产品OutputToken/COMMIT。Q06不是G实际死亡重启。正式执行后必须交完整结果/hash/预算/已执行与NOT_RUN、首失败及原return/close/join/exit和在途结论再审，不能以本次准备审查替代。

## 7. 最终状态

新增具体代码缺陷0、代码准入阻断0；执行外部阻断为凭据未交付及尚无正式真实执行交接。本轮媒体stat/read/hash、真实PF/61、新G/R/Java、OS采样、编译、设备均0，正式许可未消费，无在途任务。原E2E FAIL/exit2/工具exit1/160/已消费许可及E2F有限事实采信保持，旧G369/+209、R519 FAIL不改。

建议负责人完成执行前置后裁定一次真实有限IO；当前不运行、不索取或绕过凭据、不自行下一批。host JNI BLOCKED、Kit/Flutter/AAR/Android/licensing P0、C14原限制/平板功能0保持，**D1 NOT_PASSED、M0 NOT_STARTED**。报告与证据主动交负责人。
