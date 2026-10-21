# D1 E3 真实大文件有限 IO 启动层交付 V1.0

2026-10-17。交付范围为准备代码、一次集中编译、纯数据负例与自有小文件验证。状态为 `PREPARED_PENDING_COORDINATOR_HANDOFF`；真实 PF、真实 61 分支均为 `NOT_RUN`，正式预约未消费，`d1e3/execution` 和 `d1e3/runs` 尚未创建。D1 未通过，M0 未启动，JNI、C14 与原 P0 边界保持。

本次实现固定批次的真实 profile、外部 freeze 校验、原父子 PID/创建时间绑定、CREATE_NEW 预约及 claim、全新输出根和进程内 RuntimePermit。任意 approved JSON、历史 hash、合成 profile 或直接 Engine 参数均不能取得真实执行许可。公开包仅含随机许可的 SHA256 commitment；实际许可由负责人另行保管，在正式审查交接后释放。准备交付本身不释放执行权限。

固定批次为 `D1-E3-11a896d3c2c34483ba2dff60fa63f5c8`，唯一输出根为 `D:/CodexProjects/VideoKit/docs/coder/d1e3/runs/e3-11a896d3c2c34483ba2dff60fa63f5c8`。默认入口只 Inspect。正式运行需要本批外部 freeze SHA256、固定 batch、独立许可、当前机器 LZF、绑定的 CPython 3.12.14/64 位运行时及 fresh 内存门禁同时成立。许可在 child 环境中先取出再移除，之后才导入生产代码；helper 不继承许可，磁盘 receipt 不写许可。

真实输入只限原 R2 的 L/C/Z 三条精确路径，声明长度分别为 3212959911/4096/0 B，边界 B=2147483648。四个 L 窗口起点为 2147418112、2147450880、2147483648、3212894375，每窗请求 65536 B。没有媒体目录扫描、NAS、复制源、重算全片 hash、写源、解码或 Android 实验。profile 中旧 stat 与 SHA256 已明确为历史声明，本批没有采集真实媒体 stat 或字节。

G 使用原只读 share1 guard；J 通过 FFM CreateFileW 打开只读 share1 原 HANDLE，并将同一个 HANDLE 绑定到原 FileDescriptor/FileInputStream；该行已分配的 R reference 使用原 HANDLE。OPEN 中比对 physical identity、opened length 和 mtime，正长度源 READ 在原对象同步区、seek/read 之前重新核对原 opened 三元组。缺失或不匹配即阻止依赖访问，保留原对象供既有关闭流程处理。该保证仅覆盖受控共享的原 opened-object 访问区间，不是全文件快照、当前全片内容 hash 或对预先存在的可写映射的防护。

新增身份查询没有增加控制 RPC 或读取源字节；G/J/R 各自上限 512 次并计失败尝试，退出证据带累计计数。R 计数包括其原有输出对象的身份查询，不能全部解释为源查询。J/R OPEN 扩展同一帧的预期三元组，READ/EXIT 带计数；原 61 分支、452 分配、544 硬界、101 query、1573522 B/59 次输入上限均保留。路径祖先检查是有限元数据操作，C# 最终 role 属性查询单列，不把“最多 66 个祖先节点”误写成所有元数据调用总数。

完成判据按本批 manifest/profile/claim 参数化：PF 先完成，61 个精确 ID 唯一且按批准顺序完成，每行控制/query/data/时间检查通过，预期 Refused 与 3 个 WAITING 的原结果归档成立，GC n01–n31 完成及 n32 的实际 flush/fsync/close 返回成立。断言使用有序证据 trace 与返回 hash，不依赖 E2F 的固定原 hash、160 个断言或仅有 62 行。P01-S 的 4 个合法 1 B 短读明确记为 `UNFILLED/4`。完成、原资源门禁、原 G exit0、原父 process handle 关闭、最终输出 hash 与总账必须全部成立才报告 PASS。

原 G/J/R fresh、baseline/delta、observer、future、compact、A05、R LoadFrom 与退出所有权链保持。200 秒仅停止等待；原父继续保有原 child/process handle，child 保有 Engine/Channel/原生对象。PENDING、UNKNOWN、首个 FAIL 不退款、不补跑、不 mock、不重设基线、不强制 GC、不换进程、不杀进程。180 秒门禁涵盖原 budget 起点到实际 cleanup 返回，包括晚返回的最终关闭。

逐 case 的 OS_DATA_SYNC_ACK 仅为有限工具 probe。Q01-SEQ、Q05-STREAM、Q06-LOST、Q08-READY、Q07-READYFIRST 五项产品 namespace 变体继续 `NOT_RUN_DURABILITY_UNPROVEN`。工具 READY 不构成产品 OutputToken/COMMIT，Q06 也不构成 G 实际死亡重启。

验证证据位于 `D:/CodexProjects/VideoKit/docs/coder/d1e3/evidence/`。build.json 记录 C#/Java 各一次集中编译、零修复。native-probes.json 记录两个显式 Java 自有 4 KiB 文件探针、25 项断言，两个原进程均 exit0：正常路径 query2、seek1/read1、请求2 B 实际1 B；版本不匹配路径 query1、零 seek/read；各自原 HANDLE 一开一关。fixture 合计 8192 B。preparation-checks.json 的280项纯数据/静态检查通过，包含两个未来批次、173/181 个不同断言的模型及错 hash、缺重乱额外 ID、n32 意图替代返回、资源 UNKNOWN、真实 geometry 等负例；它没有实际进程采样、真实 claim 或媒体访问。两类共305项断言，历史断言不计入；另有38份Python源文件语法检查通过，源文件数不计作断言。

`artifacts/E2C.dll` 及原 java 目录共 10 个二进制作为只读基线；正式新入口只加载 `artifacts/E3.dll` 与 `artifacts/java-e3`。E3.dll 为 84480 B，SHA256 `9e5b0208402917012db518dc054c497b8855c2ca5fe7917a13fc95cf69a61d3b`。Java 新产物为 13 个 class，逐项 hash 见 build.json。完整上游只保存 E2F 的 freeze、source manifest 与一个完整源码 ZIP；其内部历史依赖作为已冻结成员保留，不重复展开和递归重读所有旧包。E2E 的原 FAIL、原 G exit2、预约消耗、实际 full pass=0 均保持，E2F 的有限采信不转写成新实际通过。

冻结包及只读 verify 同时核不可变集、源码 ZIP、运行时子集、旧基线、自检证据和未执行状态。源码校验每条命令实际统计实体文件读取与 ZIP 成员解压读取，上限合计 256 MiB/8192 次；结果读取另为 6 MiB/512 次。准备元数据限 819200 B、自有 fixture 限 1441792 B，分别预留生产元数据 3178496 B、wrapper 196608 B 及输出 fixture 655360 B，合并硬界仍为元数据 4 MiB、fixture 2 MiB。

最终 freeze SHA256、源码 ZIP 大小/hash、实际校验读取成本和最终断言数通过独立完整交付报告交负责人，避免在被自身 hash 绑定的文档内循环嵌入 seal hash。执行步骤与边界见同目录 `D1_E3_REAL_IO_EXECUTION_PLAN_V1.0.md` 和 `D1_E3_EXECUTION_APPENDIX_V1.0.md`。后续真实执行必须由负责人正式交接明确准入，本窗口不自行执行。
