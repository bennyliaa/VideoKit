# D1 E2A 检查入口、停止与冻结附录 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2a`。本包真实入口固定关闭，无批次/root授权生成器；冻结后编译、合成及Java探针均拒绝原地重跑。

## 只读核验

使用本机已有Python，不构建、不启动helper、不访问媒体路径：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2a/tools/verify.py'
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/admission.py' --inspect
```

Inspect只读四个配置JSON与manifest，executionAllowed恒false。`tools/audit.py --audit`只读核原证据与恢复权威；`profile_audit.py`只hash既有文档/上游源码，不打开test_media。默认`tools/launch.ps1 -Mode Inspect`同样只读。

下列是拒绝检查，预期退出2，加入mock也不能解锁：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/admission.py' --request-real E2A-CONFIGURATION-DENIED
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/controller.py' --synthetic-selfcheck --synthetic-observer-mock --profile REAL_IO
```

真实分派位于fixtures/Engine之前，Engine第一句严格require_synthetic仍先于Native/目录操作。SYNTHETIC别名强制selfcheck范围，不能改名或给approved JSON后读取test_media。默认real batch/root均null，规划runs根从未创建。

## 本批中央执行

1. 已有PowerShell7.6.5/.NET10.0.11编译E2A.dll，JBR javac21.0.10以`--enable-preview --release 21`编译JavaHelper/JavaBridgeProbe，一次成功、无repair重编。当前C#/Java源码hash记录在`evidence/build.json`。
2. `tools/check-java-bridge.py --run`一次，证据`java-bridge-1792168105652835000.json`：10个独立进程/87断言PASS，使用新建4096B/17B文件。缺preview实际在启动拒绝，不冒称已进入原生桥；其它受控失败保原已open对象并close一次。原生metadata查询不读字节/不seek；decoy-path对照不是实际rename试验。
3. `tools/run-selfcheck.py --run`一次，实际OS observer在PF/n05 R519>512停止，原FAIL保留，input0/0、清理及原helper退出完成。该记录是实际策略门禁证据，不是实际阈值通过。
4. 显式`--run --synthetic-observer-mock`两次。只替换`read_cycle`返回的指标值，沿用同一MetricObserver、时限、日志、原pool与清理；真实原进程身份、FFM/Native原FD、源及输出操作仍只对自建文件实际执行。首轮P12时间失败保留；优化重复stat后最终159PASS，`selfcheck-1792168565737747500.json`。mock没有批准现场runtime。
5. `tools/check-targeted.py --run`两次，保留首次硬链接创建失败；最终`targeted-1792168592014078700.json`844PASS。observer纯受控数据、Store实际BytesIO短写/容量、原Future pending、worker与锁门禁；namespace实际自有FD/fstat，但hardlink/symlink创建受本机限制，明确未测跨路径hardlink/实际reparse跳转。
6. 两真实入口实际拒绝均code2，`entry-denials.json`。最终只读audit及freeze/verify关联所有通过与失败文件。

1003＝完整159＋定向844，另Java87；不累计旧E2、失败组或实际R超限STOP。所有新建验证文件和证据保留，累计fixture≤2MiB/日志证据含seal≤4MiB，精确总量由freeze-summary给出。

## 原生、等待与停止

G原PF前observer基线在任何PF/n01 worker启动前建立，不能HELLO后重置。J/R仅注册原HELLO实例，并借原Popen hProcess核创建时间与PID；不关闭该借用句柄。实际采样每周期snapshot关闭后再逐目标查询/关闭，observer始终最多1自有句柄/1信用。正常helper actual wait证明原实例退出后退休该角色，历史baseline/峰不删除，G保持到n32前结束观察。

仅creator线程且不持Engine锁的安全边界/等待点可提交观察；callback/native worker不会同步等待自己。observer查询及日志成本占当前行和全局180秒，不另给时间。0.1秒是等待/返回后停止界限，不能中断OS；未返回原Future保在pending，停止新接纳，不提交替代query，不强杀/假退出。GC只做已知可安全清理；外层200秒也只停止等待。

Store事件104320及指标26752分别强制预留，头≤1024、201条每条≤128；沿用原global.log文件/信用。每次写经exact_write，短写/异常/未知均停止，不能补写修复或继续采集后假称有完整日志。最终选定日志93462B，其中指标560B；这是本次事实，未来依旧按每次门禁判断。

Store性能修复只改变元数据大小观察：G为唯一写者，成功真实close后更新该path已证size，仍开放global.log按原FileIO位置及有效返回写入量计入；其它已关闭文件沿用上次已证size，最终可全量stat复核。没有缓存媒体内容或身份，没有少做journal/flush/fsync，仍保累计写与文件峰单独口径；不宣称检测敌对外部元数据修改。

源首字节前必须有仍持有的G guard及J/该行已配R实际opened同对象/length/mtime证据；G/R share1、只读OPEN_EXISTING，输出CREATE_NEW。每J OPEN最多66次ancestor GetFileAttributesW及1次原GetFileInformationByHandle，均在原h+内，无新identity RPC。查询失败原对象仍入ledger/原helper map、按原ticket关闭；不以path属性/hash/再开对象回退。未配R分支不添r+。

## 冻结及后续

seal状态ADAPTERS_FROZEN_PENDING_INDEPENDENT_REVIEW。源码ZIP覆盖src/tools/manifest/profiles/upstream-e2/upstream-e1e；freeze/source-manifest把产物、三文档、证据及所有自检文件逐项字节/SHA绑定。verify重列文件集合，新增或修改已冻结证据会失败；旧E2 231＋43源、旧E1E188＋33源及13基线同时核验。冻结后只读检查，不改旧包和失败证据，不在原根重编/重跑。

运行时状态仍BLOCKED_R_HANDLES_519_GT_512。未来必须先由负责人审查适配和该资源阻断/验证限制，再明确唯一新执行批次/root、冻结hash绑定及新鲜版本/≥2GiB资源准入；本包不能自解锁。五产品namespace/READY变体保持NOT_RUN_DURABILITY_UNPROVEN，OS_ACK不等namespace/掉电耐久，不声称真实G崩溃重启。宿主JNI/P0/C14/历史FAIL保持，D1未通过、M0未启动。无真实媒体、NAS、Gradle/ADB/设备或下载执行。
