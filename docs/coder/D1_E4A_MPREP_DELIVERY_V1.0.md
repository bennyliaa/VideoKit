# D1 E4A-MPREP 开发交付 V1.0

2026-10-17。候选D1-20261017-E4A-MPREP。固定MP4→条件AVI整批预置、无覆盖fixture发布及回执依赖已完成本机验证；真实预置NOT_RUN，待负责人整包审查派发。项目根D:\CodexProjects\VideoKit。

## 完整入口与固定来源

tools/preload_once.py默认PLAN_ONLY；正式入口一次处理两个固定源，无任意source、receipt SHA、跳过MP4、从AVI开始、resume、force或产品方法参数。固定身份来自旧冻结future-media-plan，只读取该元数据，coder未stat/read/hash真实源。

| alias | 原始B | 无LF编码B | 原始SHA256 |
| --- | ---: | ---: | --- |
| basic.mp4 | 349102 | 465472 | 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 |
| subtitle.avi | 736454656 | 981939544 | 3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f |

准确绝对源路径见d1e4amprep/tools/fixed-media-manifest.json及PRELOAD_PLAN。临时目录files/e4_mprep_TABLET_20261017_once，两临时名basic.mp4.part/subtitle.avi.part；最终仅files/e4_fixtures/basic.mp4及subtitle.avi。任何目录/temp/final冲突都停止，不覆盖、不删除、不猜已准备，不再次归档旧81407B文件。旧归档、26B、T6P状态、输出cache/budget完全不访问。

## 流程和MP4依赖

T6P唯一实机结果已完整通过，原报告/result作为来源保留；不把它扩成真实媒体或产品通过。本批仍现场确认features/原UID10221/pwd/files/fixture父目录正向可访问、无链接、新目录和两个final不存在；以df-k核两源新增空间＋64MiB余量＋5B探针。现有占用（含历史文件）已从df available扣除，不删除腾空间或重复当信用。df是观察，不是空间锁定。

一次原UID快照未见旧receiver不清UNKNOWN，疑似旧接收即停不信号。独占创建新私有目录，复用T6已证单父探针，正常probe.ascii/probe.raw共5B；额外状态cap4文件/4KiB不变。每个源发送前再次正向核父/准确temp和final无冲突、并核剩余源空间；源码参数和source都不能由CLI替换。

每源唯一producer复用同FD流式Base64/强owner。原BEGIN/DECODE/END与原raw/encoded计量立即核验后，才执行temp独立前后stat/原UID/普通非symlink/n字节/SHA。之后核fixture父与temp同一device、父UID与已准入源一致，执行合作式mv-n。原mv rc单列；必须temp消失、准确final为普通非symlink且完整原stamp相同。再用独立新命令复核final前后stat/n/SHA和temp仍消失；完整stamp含dev/inode，保持同一文件跨目录rename，不通过额外整片copy发布。

mv-n不是对抗恶意并发的原子事务；本方案范围为已审合作式同目录/同文件系统场景。mv返回0不能替代发布证明：即使目标在无冲突门之后被抢建、mv跳过返回0，temp仍存在也会拒绝，且不继续读取/哈希冲突目标。无法证明的发布不回滚删除原文件。

MP4完成后，包外basic.mp4-ready.json以CREATE_NEW写入、flush/fsync、原文件close并读回长度/SHA；内容绑定本批固定manifest、源期望、raw/encoded事实、receiver/temp/publish/final四份本次原记录的准确文件身份。验证器重读这些有界原JSON，重新校验原argv、exit/归还门、计数/源SHA/编码SHA、receiver标记、两次独立raw proof、同stamp及temp消失；再比对回执语义内容。不是非空摘要、单READY字段或任意外部传入回执自证。

AVI开始前会再次读回MP4回执并重核四原记录，且所有原owner必须实际归还。通过即在**同一次正式批次授权内条件继续AVI**，不需要每文件再造工具或暂停交接。任何MP4失败/UNKNOWN、回执写入/同步/关闭/读回失败或证据不符都停止AVI。若MP4已发布但ready同步失败，final和失败ready原样保留，不删件退款或重跑。

文件fsync/close与读回是当前运行的OS文件确认，不宣称Windows目录项掉电持久性或Android产品COMMIT；没有跨进程恢复/复用旧ready入口。现有source元数据和原FD摘要核对也不是恶意并发源快照。所有历史UNKNOWN保持原状。

## 预算和资源

| 范围 | 精确预算 |
| --- | --- |
| host原始prehash＋流读 | 1473607516B，两源各两遍 |
| 编码生成总量 | 1964810032B，两遍生成，不写编码副本 |
| 实际最大编码提交 | 982405016B，无LF |
| device独立原始hash | 1473607516B：每源temp一次n＋发布后final一次n |
| 新增媒体占用 | 736803758B，不因rename重复复制；另探针5B |
| 初始可用空间门 | 两源＋67108864B余量＋5B，按KiB向上取整 |
| producer时限 | MP4 60s、AVI600s，从host预hash前开始 |
| 每次独立hash时限 | MP4 15s、AVI120s |
| 普通metadata / 共同本机收尾 | 15s / 2s |
| metadata / producer | 计划13、硬20；每源producer恰最多1 |
| 包外日志 | 8MiB，单文件128KiB，预留最终回执空间 |
| ready核验本机metadata读取 | ≤4MiB / ≤128次，独立于媒体读取预算 |

原raw块24576/编码块32768/carry≤2/编码工作缓冲设计256KiB保持；不等于Python/ADB/OS总RSS。AVI981939544B编码仍低于原pump1GiB上界，不扩上界。600s包括预hash开销，不保证现场吞吐、不自动加时或重传。原stdout/stderr各16KiB、完整保留至8KiB；超出完整前缀即拒绝。

exact_process.py、command_response.py、stream_base64.py与T6字节一致。原T1 pump13077B/SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d；T6协议模板只机械换batch/nonce/目录，再按固定n/temp参数化receiver和proof，未放宽原close或SHA门。

源/进程UNKNOWN仍由原Job持有，禁止下一设备I/O。新增包外artifact文件读写也记录原close：异常继续强持有原file，不二次close/GC/退出洗清；无法安全写最终result时输出原阻断状态并保留原文件。原producer尝试和artifact预留额度在失败时不退款。CLI在UNKNOWN时保留原解释器，晚归还不恢复旧失败批次或继续AVI。

## 有限本机证据

唯一main-001：**37项PASS**；48条顶层本机原调用＋源close故障隔离用例7条内部调用。顶层全部原RETURNED/退出已观察、topLevelRetainedOwners0；隔离原Job保持UNKNOWN1并拒下一I/O，不以用例解释器退出计归还。无测试repair、无历史整套重跑。

两自有源65537B/70001B均大于64KiB。完整生产控制器在本机模型中条件完成两源实际流式编码、Python解码、临时/最终独立SHA、真实本机rename保持dev/inode、持久回执重读与四原记录重验；metadata13、producer各1、回执读15次。模型UID/mode/Android回执是合成字段，不证明设备权限/完整大文件性能。

真实Git shell另执行生产生成的mv-n脚本：正常保留本机原dev/inode；目标在无冲突门后插入，原mv rc0仍被拒绝，temp和冲突目标均保留。该测试UID/pwd由函数模拟，文件身份和mv行为来自本机，不当作Android权限实测。全新生成脚本集中sh-n通过。

失败覆盖短件exit0、正确长度错误SHA、既有fixture、MP4 ready fsync失败、中途停止AVI、有效非空receipt摘要但语义伪造、缺少原final记录、空间不足，以及原source close UNKNOWN。失败记录/部分件/已发布MP4/自有归档占位保留，无退款/换路。隔离close用例原rawFD已关但包装close未正常返回，原Job仍UNKNOWN，MP4尝试1/AVI0、下一I/O拒绝，未用OS退出清历史。

证据evidence/local-check-results.json、check-attempt/result/checks.log绑定最终被测源码、完整原记录与失败首因；外层检查exit0/60s界未触发。实际ADB/device/真实媒体stat-read-hash/Gradle/下载/产品调用均0。仅本机自有小数据、已有Git与Python，无历史大ZIP嵌套。

## 产品准备与交接

tools/product-test-preparation.json只计划normalMp4SixRealFrames、normalAviSixRealFrames、capabilityDenialDoesNotOpenSource、cancelRejectsWrongEpochOversizeAndLateFrame。原APK/testAPK、原单app架构及稳定budget身份不变；逐准确方法另批执行，不跑整类/Binder/故障方法。cancel必须同设备实际normal回执经独立审查，不能用任意摘要或新budget身份清额度。预置工具不自动调用任何产品方法。

准确整批入口、源路径、空间/receipt/失败政策见D1_E4A_MPREP_PRELOAD_PLAN_V1.0.md。当前executionAuthorized=false，等待负责人正式交tester；后续可同批条件预置完两源集中报告，再另派产品验证。旧归档/26B/T6P/cache/budget和产品冻结只读，D1 NOT_PASSED/M0 NOT_STARTED/P0及历史FAIL保持。

seal d1e4amprep/evidence/mprep-freeze.json，清单evidence/source-manifest.json，完整包artifacts/D1-20261017-E4A-MPREP-source.zip；外seal/ZIP身份/数量及只读verify结果集中发送负责人，封存后只读。
