# D1 R2 真实本机Provider有限实验计划 V1.0

2026-10-16。回应R1-R03。**全部为PLANNED_NOT_RUN**；R2没有打开媒体读取窗口、创建实验目录、实现harness或执行这些case。依据[负责人决定§5](D:/CodexProjects/VideoKit/docs/D1_R1_COORDINATOR_DECISIONS_V1.0.md)，首个候选限本机授权文件小块IO，不是NAS、Android/SAF、完整播放或M0实现。须先独立评审本文件及源/Sink语义，再由负责人派有限实现和执行。

## 1. 实际输入、版本和独立对照

| 输入/用途 | 本机实际路径、历史身份来源 |
|---|---|
| L：真实2GiB边界 | `D:\CodexProjects\VideoKit\test_media\03_large_files\large_video_over_2GiB.mkv`；3,212,959,911B；历史SHA256 `28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26` |
| C：小块/注入底层 | `D:\CodexProjects\VideoKit\test_media\04_corrupted_files\corrupted_video.mp4`；4096B；历史SHA256 `c0d66c6510904af0301dc1d923a403a1983f446e5a326299074f1b6a88a75405`。这里只当授权二进制文件，不解析/修复或声称有效视频 |
| Z：真实空文件 | `D:\CodexProjects\VideoKit\test_media\04_corrupted_files\empty_video.mkv`；0B；历史SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

身份来源为冻结[media-inventory.json](D:/CodexProjects/VideoKit/docs/coder/d1c02/evidence/media-inventory.json)。以上是读取既有清单取得的历史完整hash，不是R2重算或小块抽样重新证明全文件hash。首轮不重读3.21GB整片；现场长度/对象/版本或控制条件不满足时停止，不悄然扩大IO预算做全片验真。

真实调用首选复用冻结[HostFixtures.file / FileHandle](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/HostFixtures.java)：Provider.open→RandomAccessFile("r")→Handle.length/readAt→synchronized seek(long)+read(byte[],off,n)→closeAsync，按既有[AsyncReadBridge](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/AsyncReadBridge.java)接入。实际ReadHandle日志由外层计数adapter记录，不能用memory provider代替真实文件IO。

**版本保证提案**：每case由宿主测试权威对同一fixture显式赋opaque L/v，不将路径或hash交Kit当租约ID；别名case的两个token由同一宿主表明确归到同一L/v。读取前保留只读Windows guard（FileMode.Open/FileAccess.Read/FileShare.Read），在其生存期内允许其他reader而拒绝正常共享规则下的新write/delete打开；记录fileKey（可用时）、length、mtime及guard/reader实例。guard与独立reference FD也计入宿主liveHandles，期望全源DRAINED前都必须实际close，不能漏账。

guard方案依据2026-10-16查阅的[Microsoft FileShare，.NET 9文档](https://learn.microsoft.com/en-us/dotnet/api/system.io.fileshare?view=net-9.0)；JVM只读/seek/read/close依据[Java SE 21 RandomAccessFile](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/RandomAccessFile.html)。实际执行时记录本机JDK/.NET版本；文档语义不是已运行兼容证明。guard与Java reader不兼容、file identity不可靠或版本条件不满足则CASE_BLOCKED_VERSION_NOT_PROVEN，不改共享模式放行。该条件针对受控本机文件/普通文件共享，不是敌对磁盘、已有可写映射、远端缓存或全文件不可变快照的证明。

独立reference使用另一进程的只读.NET FileStream，对同一guard保护对象逐窗口读取相同offset/length，计算窗口SHA256；不得调用待测Handle或复用其已读缓冲。两方记录原始n与分块SHA，只有累计实际字节数相等且SHA相等才窗口一致。reference在该case终态前真实关闭。guard前后元数据/对象不一致则判版本不确定；只有宿主可信版本转换日志才能归为SOURCE_CHANGED。所有原文件始终不写、不移动、不改名、不截断。

## 2. 范围、预算和停止

- 每次实际read请求≤65536B，至多4个源/guard/reference句柄合计并行，至多8个64KiB有界私有缓冲；原始输入全部provider＋reference累计请求预算≤4MiB、原始IO调用≤256。调用前预留请求字节，失败/未知也占额度，不能只计成功字节隐藏重试。
- 只做下表22个case，各一次；有分支者按指定两种确定顺序各一次，无随机反复调度。补齐固定窗口的短读循环最多16次，未收齐即有界失败/未证，不无限0进展循环。
- 后续获派时才创建独占 `D:\CodexProjects\VideoKit\docs\coder\d1r2_spike_runs\<runId>`；输出用CREATE_NEW且不得跟随符号链接/输入别名，每文件≤128KiB、最多12个目标、总输出≤2MiB，输出验证读取累计≤4MiB，日志≤4MiB。上限包含Q07两种顺序各自目标，元数据记录最多32。不是C14设备目录，不改其24journal或tester48总记录限额。
- 响应deadline1秒，case观察/清理≤10秒，整批≤180秒；打开/读取真实卡住不因deadline强行认定完成。任何未证句柄/在途、身份冲突、原样本变化、超预算或未知持久终态：停止依赖项、保留PENDING与证据，禁止新池/换ID/删旧证据求通过。
- 协议close首次＋最多2次显式不重叠重试；query同键最多3次、每次≤1秒；均计总预算。不存在“每次超时重新开始180秒”。系统IO永久不返回时保留隔离harness资源账本并由负责人处置，不假发SourceReleased。

22项是首个本机IO/协议实验提案，不是新增设备计划。现有C14缺少聚合lease/capability/query等公共adapter；需后续有限harness实现并经审查，未实现部分标NOT_RUN_CONTRACT_ADAPTER_MISSING，不能mock一条成功日志宣称真实API已存在。大文件基础readAt可复用现代码；提前EOF分类等与现实现的差异须如实暴露，不修改冻结类使其偷偷符合新判据。

## 3. 每case共用证据

统一记录`run/case/authority/lease/version/consumer/generation/operationId/handleId`，每次接纳、真实delegate进入/返回、取消、close attempt、R向量和stateSequence；publicCode＋stage＋reason＋retryable与资源状态分别列。SourceReleased终态通知不计入产生它的资源前提。使用[源方案](D:/CodexProjects/VideoKit/docs/coder/D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md)和[输出方案](D:/CodexProjects/VideoKit/docs/coder/D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md)的身份/线性化；没有实现就记录缺口，不能混用C14单任务计数。

| ID/类别、输入与操作 | 预期原始事实/稳定结果候选 | 资源与唯一允许终态 |
|---|---|---|
| P01 REAL，L，B=2147483648；四窗口(B−65536,65536)、(B−32768,65536)、(B,65536)、(L−65536,65536) | provider真实64位seek/read，独立reference逐窗口长度/SHA一致；允许正短读，≤16次补齐。不得仅测8GiB虚拟provider的1字节 | 四窗口完成、双reader/guard真实关闭、consumer结束后可RELEASED；证明本机范围IO，不证明MKV解码/完整大视频或NAS |
| P02 REAL，L，在offset=L请求1；另length=0 | 正请求EOF为−1，零请求返回0且不消耗媒体IO；不能int截断回文件开头 | 句柄/guard实际归还，正常EOF/RELEASED，不把未知长度当0 |
| P03 REAL，Z，length=0且请求16 | Handle层空源可报告0长度/−1 EOF；媒体输入preflight候选CORRUPT_MEDIA/EMPTY_MEDIA，不误称CPU支持或未知长度 | 无decode/writer创建，真实close后RELEASED；不伪造有效媒体 |
| P04 INJECT_METADATA＋REAL_READ，C，wrapper只将length改null | raw未知长度不等空；先顺序读32真实字节与reference比较。需已知长度的CPU探针拒绝候选SOURCE_CAPABILITY_UNSUPPORTED/SOURCE_PREFLIGHT/LENGTH_REQUIRED（新增待评审码） | 顺序read真实完成可成功；CPU能力负例不启动decode。关闭归还，不能把包装器称真实未知长度存储 |
| P05 INJECT_REQUEST_CAP＋REAL_READ，C，外层请求32但每次delegate最多7 | 正短读合法，最多5次真实read补齐32字节/hash；不报SOURCE_CHANGED | 记录outerRequested/delegateRequested/actualN，实际归还；只证明合法短读处理，不声称磁盘真的随机短读 |
| P06 INJECT_RESULT，C，非零读固定返回0、不调用delegate | 第一次即INTERNAL_ERROR_REDACTED/SOURCE_READ/INVALID_PROVIDER_RESULT，retryable=false；现内部INVALID_READ_RESULT与公共码映射分列 | 不重试忙循环，取消/close实际完成后RELEASED；0原始IO可证，不伪装网络故障 |
| P07 INJECT_LENGTH＋REAL_EOF，C，声明length=4097，在4096请求1 | delegate真实EOF−1但已知remaining>0，候选CORRUPT_MEDIA/SOURCE_READ/EARLY_EOF；没有可信换版证据，不报SOURCE_CHANGED | 当前AsyncReadBridge该分支仅返回−1是静态契约差距；新分类未实现则缺证/FAIL，不能用原文件截断制造case |
| P08 INJECT_COMPLETION_DELAY＋REAL_OPEN，C，先真实open再扣住完成 | seal/取消在返回前发生；取消响应CANCELLED，OPEN在途/隐藏句柄仍保留 | 放闸后晚H只能close；真实close及在途回报0后RELEASED。延迟是包装注入，不是磁盘慢open实证 |
| P09 INJECT_COMPLETION_DELAY＋REAL_READ，C，先真实读32入私有缓冲，再扣住完成 | 取消后CANCELLED（或未请求取消而超时为SOURCE_TIMEOUT）；operation仍1，不能复用缓冲或把旧数据发布新代 | 真实底层IO已返回、完成投递被延迟，明确区别kernel阻塞；放闸/排空后才RELEASED |
| P10 INJECT_CLOSE_FAILURE_BEFORE_DELEGATE，C | 第一次close故意失败、底层H仍开；原C14内部SOURCE_IO_FAILED与公共候选INTERNAL_ERROR_REDACTED/SOURCE_CLOSE分列，失败引用保留；显式第二次执行真实close | 同一closeAttempt不重入；第二次真实返回后才清failedCloses并RELEASED。不是实际文件系统close故障实测 |
| P11 INJECT_ALIAS_SCHEDULE＋REAL_HANDLES，C；A/B同L/v，两个consumer，第二者将来open | 对照源S01/S02：第一释放不全源可移动；seal后第二future open为SESSION_RELEASED，factory额外调用0 | owner确认future-open结束、全部guard/句柄/操作清空后DRAINED；没有原文件移动操作 |
| P12 INJECT_AUTH_VERSION，C，v1排空后宿主发布v2，旧open/通知迟到 | 旧open SESSION_RELEASED/STALE_VERSION；可信版本变化另有SOURCE_CHANGED候选事件；旧通知query仅v1 | v2计数/可移动状态不受旧seq影响；这是权威版本模型注入，不声称原文件发生变化 |
| P13 INJECT_CAPABILITY，C，wrapper声明SEQUENTIAL_ONLY，再seek | SEEK_UNSUPPORTED/SOURCE_SEEK，实际delegate seek调用0；前面顺序读取可真实完成 | 正确关闭后RELEASED，不能把本来可seek的文件称真实pipe/SAF能力证明 |
| Q01 REAL_OUTPUT＋INJECT_CAPABILITY，独占新.bin，顺序可写且验证可读 | 用C的至多32字节作为IO probe payload，真实write/flush/close和独立只读读回SHA一致；验收scope仅D1_IO_BYTE_PROBE | 所有writer/validation引用0才demo READY_ELIGIBLE/READY；不是有效视频、不替代六帧/双轨/遮罩验证，token不进入产品业务 |
| Q02 REAL_OUTPUT，独占新.bin，显式seek/randomWrite/length可查询 | 三次小写入含覆盖已写区间，逐offset读回正确；同一计数预算，位置64位 | 实际close后验证lease读回/归还，记录实际能力；不由FD存在推断任意后端可seek |
| Q03 INJECT_CAPABILITY_CONFLICT，声明仅顺序却计划要求random，或validationReadLease=NONE | OUTPUT_CAPABILITY_UNSUPPORTED/OUTPUT_PREFLIGHT；两分支各一次 | writer、写FD、媒体字节0；无暗建可读副本，拒绝结束 |
| Q04 REAL_OS_HANDLE_DUP＋INJECT_ACK_LOSS，本机新临时输出 | 计划用同一harness进程的Windows DuplicateHandle＋DUPLICATE_SAME_ACCESS、不可继承、不用CLOSE_SOURCE，明确两个SafeFileHandle owner；关闭原句柄后dup仍可小块写/close。不能把两个open、两个Java wrapper或同一fd整数称dup | 全部stream/原HANDLE/dup/guard实际归还；实际close已返回但故意扣ACK时保守PENDING，确认返回后才清账。绑定无法提供则NOT_RUN_PLATFORM_DUP_UNAVAILABLE；Android ParcelFileDescriptor/Binder和跨进程传递全部NOT_RUN |
| Q05 INJECT_SPACE_FACT＋REAL_OUTPUT，knownFreeSpace=null，低额输出 | null不等无限；只有预先允许bounded流式模式才真实写。另注入空间错误OUTPUT_SPACE_INSUFFICIENT/OUTPUT_WRITE，真实磁盘不填满 | 取消/close/abort后无READY；未知空间与注入错误分别记，不称真实磁盘满 |
| Q06 REAL_OUTPUT＋INJECT_RESPONSE_LOSS，demo数据/journal实际sync与提交后扣住应答 | 原宿主回复丢失后由另一进程只读恢复query，同export/handle/token/intent一致；open计数1，不改id | READY维持、无第二writer；记录实际数据/日志/命名空间ACK层级，仅证本机进程恢复。缺必要durability/提交能力则NOT_RUN_DURABILITY_UNPROVEN，不能用noop DirectorySync冒充；不证明Android/NAS或掉电安全 |
| Q07 INJECT_OWNER_SCHEDULE＋REAL_OUTPUT，旧ready与新owner abort两确定顺序 | ready先则READY同token；takeover先则旧ready EXPORT_FAILED/STALE_OWNER，abort在实际writer/验证归还后ABORTED | 原lease/attempt账本保留；不是实际进程native故障/系统失电恢复证明 |
| Q08 INJECT_CANCEL_QUERY_UNKNOWN，writer或validation引用仍1，取消应答/query暂扣住 | EXPORT_FAILED/ABORT_QUERY/OUTCOME_UNKNOWN且PENDING；同键最多3次query，不重开 | 放闸后若abort先胜为ABORTED；若此前READY已持久则同READY，不能伪CANCELLED；未释放停止依赖 |
| Q09 INJECT_IDENTITY_OR_TARGET_CONFLICT，重复open与不同意图/输入别名目标 | 合法重复附着同handle且writer1；意图冲突EXPORT_FAILED/OUTPUT_IDENTITY；试图指向输入则OUTPUT_CAPABILITY_UNSUPPORTED/OUTPUT_PREFLIGHT | 拒绝分支真实写0，原输入不写不删；实际输出仅独占新目录 |

本表13个P＋9个Q＝22个case；P09的取消/超时、Q03和Q07等明示分支各有确定顺序，仍只一轮，不借分支追加无限attempt。对拟议码/新状态未实现的case，先交有限harness变更评审，不把断言抄进现C14测试即声称实现完成。

Q04依据2026-10-16查阅的[Windows DuplicateHandle官方文档](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle)（页面标2022-08-23更新）：它是真正复制同一对象的句柄，文件位置也共享，故本case只测受控顺序写与关闭所有权，不将其当独立游标。所需调用仅限自身测试进程/自己的输出，不访问他进程；后续harness绑定须先审，不在R2实现，也不构成Windows Kit产品开发。

## 4. 公共码提案、当前限制与退出材料

现有码使用SOURCE_NOT_FOUND/PERMISSION_DENIED/DISCONNECTED/TIMEOUT、CORRUPT_MEDIA、SEEK_UNSUPPORTED、CANCELLED、SESSION_RELEASED、INTERNAL_ERROR_REDACTED，以及输出方案的OUTPUT_*、EXPORT_FAILED。stage/reason固定枚举化，不公开第三方异常；retryable描述允许的下一动作，不能授权重复open或资源复用。

新增候选仅`SOURCE_CAPABILITY_UNSUPPORTED`（输入能力不足，不误指容器/codec坏）与`SOURCE_CHANGED`（宿主可靠版本证据）。它们尚未冻结；需API/schema/binding版本与未知码fallback审查，旧binding可保守映射INTERNAL_ERROR_REDACTED并保留阶段/原诊断，不静默成功。已知提前EOF无换版证据选CORRUPT_MEDIA；合法短读不错误归因变化。

正式执行报告须包含输入历史hash引用/现场版本保证、实际delegate与reference窗口结果、注入位置/原始返回/目标码差异、完整R向量/FD归还和每case终态、预算实耗、未实现/不支持的明确NOT_RUN。验证者能区分真实文件IO、包装器故障、协议调度、真正平台失败；任何一项不能外推NAS/Android/完整媒体处理。

成功出口只接受经上述独立证据验证的本机IO/最小协议行为；真实资源未证、版本不稳、越预算或新状态尚未实现是PENDING/BLOCKED/NOT_RUN出口，不冒充PASS。后续完整API/Fake/TestKit、Android真实provider、NAS/播放、实际视频Sink验证仍在M0/M1/M6/M7；C14冻结、73项和2历史信号NOT_RUN保持。
