# D1 E4A-T 测试传输工具完整交付 V1.0

2026-10-17。候选D1-20261017-E4A-T，依据[开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_E4A_T_CODER_REQUIREMENTS_V1.0.md)。本批修复测试基础设施，**未修改E4A产品/冻结，无Gradle、ADB、设备、真实媒体stat/读取/复制/hash、网络或模型下载**。D1未通过、M0未启动、原P0/历史FAIL保持。下一实际预置仍待负责人另派。

## 原证据与根因限度

[原设备报告](D:/CodexProjects/VideoKit/docs/tester/D1_E4A_N_DEVICE_TEST_REPORT_V1.0.md)为PASS1/BLOCKED9，非codec产品失败。basic.mp4主机349102B，设备实际81407B、SHA a790f44fc3c6ff4579c83f57b42a4b31cd95278cca28fd4aa6b97fd295fd9695，原传输exit0/stderr空。以上为历史证据，本窗口没有访问源或设备。独立Binder PASS不重跑，AVI尚未预置，手机仍不准入。

| 原准备路径 | 证实事实 | 不能据此断言 |
|---|---|---|
| finish_prepare_tablet.py的exec-in/run-as/tee | 源以rb打开，Popen stdin默认二进制；copyfileobj后close stdin，再communicate等待；stdout指DEVNULL、stderr PIPE稍后读取。exit0与实际长度不符 | 不能说原脚本忘记关闭/等待，也不能说DEVNULL是不消费stdout的PIPE。stderr压力可能死锁是结构风险，原stderr空不证明它导致本次截断；具体Windows/ADB/远端层次UNKNOWN |
| 安装返回处理 | 原完整stdout是Performing Streamed Install换行Success，严格全文等于Success误拒；原app实际已装，后续只装未装test | 解析错误不等安装失败，不授权重复安装/卸载/清数据 |
| preflight.py的run-as sh -c | 原ADB参数中的组合脚本未作远端整体引用，分号命令可能越出run-as范围；原Permission denied/缺目录不能当可信私有目录事实 | 不从这份错误目录输出推断预算为空，也不据此修改产品或启用手机 |

本地Python3.12.14的Popen签名/二进制stdin实现及copyfileobj源码短摘在evidence/local-runtime-analysis.json。copyfileobj本身不检验每次write返回，但原默认阻塞缓冲写入器通常已处理短写；现有证据不能把这一点确定为81407B的根因。新工具提供强失败准入和可观测机制；本机fake通过不证明实际ADB已修好。人为SUB截断用例仅是假失败，未验证原ADB使用文本模式。

## 实现

工具在[docs/coder/d1e4at/tools](D:/CodexProjects/VideoKit/docs/coder/d1e4at/tools)：

- [exact_process.py](D:/CodexProjects/VideoKit/docs/coder/d1e4at/tools/exact_process.py)：参数数组、shell=False、二进制无缓冲管道，64KiB源块；生产write_all只累计每次实际正返回，短正写继续原余量，0/None/异常拒绝。源同一只读FD先完整长度/SHA，再归零转发、重新累计实际提交SHA；完成才显式flush、close stdin、等原进程与两条drain和writer实际返回。
- stdout/stderr分别持续消费/摘要，默认各1MiB上限，各只存64KiB前缀；超额最多多读一个16KiB块就停止并拒绝。超时只停止自己创建的原客户端子进程，2s共同清理窗口；不杀ADB server/设备进程。原wait/pipe/线程未返回强留原Job/参数/source/process，阻止后续调用，结果UNKNOWN_RETAINED，不借退出码或超时声称归还。
- [fixture_transfer.py](D:/CodexProjects/VideoKit/docs/coder/d1e4at/tools/fixture_transfer.py)：一次provision_once，先CREATE_NEW持久attempt记录；残件先核原长度SHA、同目录无覆盖改名、再核原字节且固定路径已空。新临时名不存在才启动一次生产者。生产者完整提交/exit0仅标PROCESS_IO_COMPLETE_ONLY，必须独立读取临时文件长度/SHA全符，再同目录无覆盖rename及独立发布后核验，最后FIXTURE_ADMITTED。
- 目标存在性只读metadata，不对碰到的旧文件全hash；真正内容probe先stat并在超过本文件审定上限时拒绝，然后才sha256sum。后者的实际SHA/长度来自独立进程，不能用submittedBytes/producer echo代替。短件、同长度错SHA、超大件、非零、挂起或未知都保留，不补传/续传/覆盖/删除/换方式重试。
- 远端整个脚本以POSIX literal quoting放在同一个run-as sh -c参数，host仍用数组；二进制接收改为noclobber的cat重定向，不让tee回显媒体。源路径不进入远端shell，远端只允许files/e4_fixtures下受限basename。多层引用在本机做解析检查，实际ADB/Android toybox兼容性仍NOT_RUN；不把本地shlex检查冒充设备执行。
- installation_success只解析已结束的原响应：exit0、stderr空、末个独立行Success，之前仅容许明确安装banner；Failure/Error/NotSuccess/非零/截断未知拒绝。它从不安装或自动重装。已记录原成功提示在本机解析通过，本批及下一预置计划均不重装APK。

预检的完整源hash和普通文件系统调用有有限字节界，但无法强制中断一个不返回的OS读/open。进程期限/清理窗口不等磁盘或ADB远端绝对硬时限；任何未证完成都不发布，下一正式批次需保留现场和原owner。这是合作式测试工具，不提供同UID恶意篡改/RCE沙箱、不可抵赖账本或掉电绝对安全。

## 有限本机结果

最终[local-check-results.json](D:/CodexProjects/VideoKit/docs/coder/d1e4at/evidence/local-check-results.json)：**72断言PASS**，52条调用记录，其中51个真实启动并结束的自有假子进程、1次源SHA预检拒绝而未启动子进程；没有52次真实设备/ADB调用。最终自有host预hash+stream读取6480444B，真实媒体0B。所有假进程/pipe/writer已返回，retainedProcessOwners=0。

MAIN为66断言/48调用记录；核对读取预算后补强metadata-only碰撞检查及内容probe前长度界，必要REPAIR为72断言/52调用记录。不将前后断言相加；MAIN原源码五文件、原日志/结果/全部自有产物保留，最终源码绑定5个生产/检查输入。没有Gradle或产品APK重建。工具只依赖现有Python标准库，没有新增第三方包。

覆盖实际生产pump/workflow：完整349102B全字节模式（含NUL/CR/LF/SUB/FF）、实际短正写累计/0写拒绝；完整提交+exit0却仅81407B落盘；相同长度错SHA；超大落盘先长度拒绝且hash读0；早退短消费、非零原19、挂起有界停止；stdout262144B+stderr131072B并发压力及超额拒绝；残件改名前后同字节、临时名/attempt冲突不覆盖不重试、源错SHA不启动、Windows路径空格/Unicode/引号/尾反斜杠、远端整个脚本引用、安装多行提示。假文件/子进程全部在本候选evidence的受标记目录，不能访问真实媒体或设备。自有失败临时件仍在，没有清理来求PASS。

--plan的独立预览也通过，sourceOpened=false/adbCalls=0；仅构造命令字符串。预览与正式[计划JSON](D:/CodexProjects/VideoKit/docs/coder/d1e4at/tools/tablet-preload-plan.json)仍executionAuthorized=false。默认AdbBackend拒绝任何设备调用；布尔护栏不是外部正式授权的替代。

## 后续一次预置及冻结交接

[精确使用计划](D:/CodexProjects/VideoKit/docs/coder/D1_E4A_T_PRELOAD_PLAN_V1.0.md)规定：只在负责人另派批次后处理平板，保留81407B残件，固定全新临时名各传一次，独立核验后同目录发布；MP4任一步失败即阻断AVI。AVI只一次首次预置，手机不再查询/催启用；不运行Binder或产品媒体方法，不重建/安装产品，不碰预算marker/cache/旧fixture。残件路径/摘要不符即停，不猜已归档或补跑。

成功全两文件的计划payload736803758B，host源两遍1473607516B；设备新件临时及发布两次hash1473607516B，加残件改名前后162814B，总1473770330B。新文件峰值新增736803758B；保留残件81407B后合计736885165B，历史APK/cache与余量另核。不是已发生流量或可用空间事实。

完整源码、计划、生产工具、原证据文本及本机证据以transfer-freeze/source-manifest/源码ZIP一次封存；外部完整报告提供seal/ZIP SHA以免自绑定。只读package_tools.py verify需外部--expected-freeze，只核文件/ZIP和语义，不启动进程或访问媒体/ADB。既有产品冻结保持，其中E4A seal a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d原样引用。

完整无在途后主动一次交负责人，待独立静态审查另派实际预置。本批不证明正常六帧、codec、FD/native回收、信号或产品质量通过；E4A-N的PASS1/BLOCKED9、C14及全部历史结论保持，D1未通过/M0未启动。
