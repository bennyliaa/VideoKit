# D1 E2 有限真实 IO 配置与准入 V1.0

2026-10-16。**这是配置候选，真实执行入口关闭。** 本批只做配置、精确路径stat、已有清单读取、必要合成适配与元数据组件自检。不能凭本文件、改SelfCheck名称或JSON approved标志启动真实PF。Java opened-FD身份桥及真实输入/输出命名空间尚待选择和适配，具体差异见 `D:\CodexProjects\VideoKit\docs\coder\d1e2\evidence\adapter-feasibility.json`；需负责人审定后另派适配/执行批次。

## 样本与真实窗口

| 角色 | 精确路径 | 历史长度与SHA256 |
|---|---|---|
| L | `D:\CodexProjects\VideoKit\test_media\03_large_files\large_video_over_2GiB.mkv` | 3,212,959,911B；28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26 |
| C | `D:\CodexProjects\VideoKit\test_media\04_corrupted_files\corrupted_video.mp4` | 4096B二进制；c0d66c6510904af0301dc1d923a403a1983f446e5a326299074f1b6a88a75405；不解析或修复视频 |
| Z | `D:\CodexProjects\VideoKit\test_media\04_corrupted_files\empty_video.mkv` | 0B；e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

来源为R2计划、tester历史身份JSON及原d1c02媒体清单；三份文档的SHA在 `D:\CodexProjects\VideoKit\docs\coder\d1e2\profiles\inputs.json`，verify只hash这些文档，不打开媒体。2026-10-16 23:33的三文件stat长度均相符，文件项均非reparse；没有检查祖先路径。**stat/mtime和历史hash均不证明当前字节、物理对象或版本；未重算全文件hash。** 不修改/复制/移动输入，不扫描NAS，不新增素材请求。

B=2,147,483,648，四个真实窗口如下。P01-N逐方各一次65536请求；P01-S在相同起点只进行原四次cap1请求和reference4，明确UNFILLED，不补读成整窗成功。

| N/S窗口 | offset | N每方请求 |
|---|---:|---:|
| 1：B−65536 | 2,147,418,112 | 65,536B |
| 2：B−32768 | 2,147,450,880 | 65,536B |
| 3：B | 2,147,483,648 | 65,536B |
| 4：L−65536 | 3,212,894,375 | 65,536B |

`profiles/cases.json`逐61行继承原R4全部分配/操作，列真实/注入部分、windows、输出写入、requiredDurability、成功条件与阻断出口。派生请求1,573,492B/59、验证128B；P01-S余8B、P05余6B、P13余16B，合计30B留在原行。输入硬分配1,573,522B/59不变。零长bridge仅0B/delegate0可不计费，普通窗口不能用charge=false隐藏IO。

## 版本和共享模式硬门槛

后续获批时，宿主用opaque source/version/consumer/generation绑定原guard epoch；不以路径或历史hash当租约ID。原G guard采用GENERIC_READ、OPEN_EXISTING、shareMask=1；各已分配J/R对象须在任何字节读之前证明volumeSerial/fileIndex64/length/lastWriteTime与guard一致，并绑定原owner/object/ticket。reference只在原分支已分配时要求，不为未分配reference的P03等分支偷加r+；这些分支仍须G/J opened-object证明。

只读共享方案对应正常本机文件共享规则；不兼容就CASE_BLOCKED_VERSION_NOT_PROVEN，不放宽共享。Windows句柄信息可比较volume与fileIndex；这不是全文件不可变快照、已有可写映射、敌对磁盘或NAS保证。[FileShare](https://learn.microsoft.com/en-us/dotnet/api/system.io.fileshare?view=net-10.0)、[GetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle)。

现有G/R有opened-handle身份，J的RandomAccessFile.length来自FD，但fileKey/mtime来自再次按path查属性，不能代替J已打开FD身份。A05方案是在固定Windows/JDK21的J内部实现经审定opened-FD桥，只回opaque身份，raw HANDLE不得出J或入journal；放在原h+内部且在PF/n10比较，不新增N/RPC/媒体read。具体JNI/FFM/内部FD机制及flags本批未选、未实现、未放行；当前JNI BLOCKED不变。A02另须将只读L/C/Z别名与CREATE_NEW输出根分离，保持原安全sandbox，不复制素材进SelfCheck绕过。缺任一证明即真实读取前阻断。

guard及原引用保留到native/gate/callback/reference真实排空。P12是宿主版本模型注入，不声称素材真的改变；未获可信换版证据不报SOURCE_CHANGED。

## 逐case durability与终态

31个源分支requiredDurability=NONE，只验原始字节/引用/包装器协议，不要求生成持久输出。30个Q分支逐项声明OS_DATA_SYNC_ACK：按该行原flush/写/日志分配核实际OS确认，明确仅本机字节与权威恢复probe。该层失败或无法提供时，依赖该层的case为NOT_RUN_DURABILITY_UNPROVEN，不能以UNKNOWN代表完成，也不能补noop sync。

Q01-SEQ、Q05-STREAM、Q06-LOST、Q08-READY、Q07-READYFIRST的产品namespace/READY变体逐项为 **NOT_RUN_DURABILITY_UNPROVEN**。工具protocol READY只是IO demo状态，不是产品OutputToken/业务COMMIT，不发布业务提交，不降低既定产品P0。任何组合显式要求NAMESPACE_DURABLE或namespaceRequired=true，都维持这个出口；把level偷降OS_ACK会使配置无效。

Q06配置精确定义为原J独立读G已sync日志并由活G重载权威；不是实际G崩溃/重启、断电恢复。若实验目的改为真实进程死亡重启，须另交具体控制/实例/信用差异，不能暗加process或称现61行已经证明。P06结果0、P07声明4097/真实C4096 EOF、短读cap、晚完成及ACK丢失均注明注入，不称磁盘真实故障。

## 两栏资源与停止阈值提案

受管硬界仍24资源/6媒体/8×64KiB槽；875项合成证据中的23/5/1不是运行时总量。另列原G/J/R的PID＋creationTime100ns＋HELLO owner、threads/handles/workingSetBytes/privateBytes；基线为G的PF前和三原实例HELLO后、首媒体读前。只保留相同实例，PID复用、计数缺失、非有限值、阈值或采样间隔超限都停止新接纳，保PENDING，不强杀。

以下均为 `profiles/runtime-policy.json` 中 **PROPOSED**，需要负责人审定，尚未用于真实执行：

| 进程 | 线程绝对/增量 | 句柄绝对/增量 | 工作集绝对/增量 | private绝对/增量 |
|---|---|---|---|---|
| G | 16 / +8 | 256 / +64 | 256MiB / +128MiB | 256MiB / +128MiB |
| J | 64 / +32 | 512 / +128 | 768MiB / +256MiB | 768MiB / +256MiB |
| R | 64 / +32 | 512 / +128 | 512MiB / +256MiB | 512MiB / +256MiB |

根据18逻辑CPU、16,605,540,352B物理内存，区分JVM/.NET与G基线并同时限制绝对量/基线增量；它们不是已测G/J/R基线。提案还要求真实PF前availablePhysical≥2GiB；本批23:33瞬时available=964,145,152B、load94%，不满足该提案。未来须新鲜采样并由负责人决定，不能据旧快照自动放行或修改预算。

候选每1秒、最多201周期、gap≤2.5秒、单次返回后观察期限0.1秒；不称绝对内核峰，短尖峰与未返回IO期间可能漏采。观察时间和日志成本计入原行/整批180秒，不额外延长；如果无法同时完成就Stop，不补时间。OS调用未返回时0.1秒不能强制中断，后续接线可复用既有native pool及pending事实，不增加线程/替换owner。

准备的Win32 reader先用一个thread-only snapshot取目标PID计数并关闭，再逐目标OpenProcess读取counter并关闭，最多一个observer自有句柄/预留信用；全额24时拒绝采集，不临时开三个process handle。快照API内部枚举线程owner，只保原目标计数，不记录其他线程信息。查询不读进程内存内容。[线程快照](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot)、[进程创建时间](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes)、[句柄计数](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesshandlecount)、[内存计数](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo)。

活进程exit FILETIME未定义，组件使用SYNCHRONIZE权限及零时长process wait核当时未终止；不是长期存活保证。[WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)。未知close保原句柄及信用，不重试或伪归还。组件未接入真实runner，真实MetricObserver不认approved布尔；纯mock专用模式不能变成真实批准。

## 元数据及额外开销

observer不增process/thread/RPC/media-call/journal事务。提案复用既有global.log 131072B：原事件预留≤104320，metrics≤26752（201×128＋1024头），合计不扩界。E1E实际事件92902B、E2合成92901B仅作根据，不是未来容量证明；须先获批分配并验证组合。compact记录用毫秒及各role线程/句柄/WS KiB/private KiB，原字节阈值先检查；每次write仍exact_write、累计元数据写另计。不能容纳即BLOCKED_OBSERVER_LOG_CREDIT，不开额外日志或扩峰3,178,496B/硬4MiB。

协议frame8192B；R reply≤2048，J reply<8192；各helper最多512缓存项。缓存计数门槛196608编码单位，J预留2048后允许更长reply，单次最终counter保守界202752，不能把196608宣传为全cache堆字节硬界。key/signature、字符串/数组头、JSON/Zlib/allocator/GC、native pool2、pipe线程4、P10临时并发2及completion2的运行时开销另受进程指标观察；大read只传digest，≤32B才传base64≤44字符。逻辑record64KiB、8槽及有限条目不等整个堆内存测量。

## 启动合同与准入次序

默认batch/root均null，规划根 `D:\CodexProjects\VideoKit\docs\coder\d1e2\runs\{approvedBatchId}-{uniqueNonce}` 必须尚不存在；当前未创建。后续须依次完成：独立审查配置与durability目的；选择并实现/审查真实命名空间和J opened-FD桥；审定指标阈值/采样接线/日志信用；负责人明确新执行批次，绑定冻结SHA、原owner及唯一新输出根；现场版本/共享/资源条件满足后才允许首字节。批准配置本身不会解锁此包的真实入口，不能直接据875项合成结果派媒体实验。

452/544控制、101query、输入1,573,522B/59（硬4MiB/256）、10目标/32记录、输出655360/验证262144、元数据峰3178496/硬4MiB、180秒和外层200秒仅停止等待规则不变。JNI/P0/历史FAIL/C14保持，D1未通过、M0未启动。
