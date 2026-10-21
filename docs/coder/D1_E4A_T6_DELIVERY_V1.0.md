# D1 E4A-T6 开发交付 V1.0

2026-10-17。候选D1-20261017-E4A-T6。集中修复E4AT5P-F01/P1的共享回执写者问题，本机有限验证完成，设备NOT_RUN。项目根D:\CodexProjects\VideoKit。

## 修复与已证边界

T5P原探针286B/SHA f15424ea4759dc3e299308d50f8da8ebf3a48d0e79169ee65525122a2ad7a8d3已经交织；不能凭末hex00、pipelineRc0或重拼片段判各端成功。T5P原metadata3/producer0/目录未创建/NOT_ADMITTED不变。原报告、原收据和准确交织字节保留在d1e4at6/reference。

T6不再使用FD3或管道回执，也不假设一次shell printf等于一次原子write。新probe在独占私有目录顺序执行：printf固定AA==到probe.ascii；取得原返回后，用文件重定向供base64-d解码到probe.raw；取得原返回和两文件stat后，od-N1最多读一个字节。仅在这些前台操作或命令替换返回之后，由唯一父shell串行输出printf/decoder/od三个原rc与最终PROBE。子进程正常stdout分别进入准确文件或被父命令替换捕获，没有子端向协议stdout写标记，没有后台任务或共享回执FD。

未执行的后续阶段明确SKIPPED，不填0。最终回执同时要求原UID/pwd/正parentPid、SEQUENTIAL_FILES、两原stat rc0、ASCII4B/raw1B及hex00。解析器严格要求四行和固定阶段顺序；非零、SKIPPED、缺失、截断、重复、乱序、错误hex或旧交织均拒绝，不重排/拼接/忽略异常。外层exit0不能覆盖某端失败。

本实现利用负责人明确允许的准确微小诊断状态文件：同一新私有目录下probe.ascii和probe.raw，正常4B＋1B；预算最多4文件/4KiB，实际协议只创建这两个。采用原UID、umask077、noclobber，精确不存在/非symlink门，不创建其他路径、改权限或清理。固定输入决定正常数据大小，stat不合4/1立即拒绝后续od/producer；od自身最多读1B。该预算是受控工具合同，不宣称对任意恶意故障程序提供内核文件配额。

由于探针现在有文件，流程调整为features→context→一次UID观察→独占新目录→顺序probe→唯一256B producer→独立raw proof。probe失败会留下新目录与可能的两个状态文件，payload源未打开、producer0；不能再套用T5的“失败前无文件”假设。所有失败产物保留，不自动清理或复用attempt。

## 保持的传输和owner门

exact_process.py、command_response.py、stream_base64.py均从T5逐字节继承并绑定外seal。T1 pump仍13077B/SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d。源同FD两遍/3字节carry/padding/无LF编码、raw与encoded分别计量、实际stdin/source/drain/wait/线程close及UNKNOWN强owner不变；不重复旧51项全套。

receiver/proof/context/UID观察等原函数仅新批次身份和T6标记前缀变化，封存器按AST逐函数与原T5源码比较，避免借修probe放宽256B计数、原DECODE/END或独立原始SHA。无新增依赖、权限、manifest、产品架构、外部暂存或媒体入口。

原本机客户端实际返回和设备文件字节证明分别保留。前台命令原rc、文件大小、独立SHA和本机管道归还不是fsync/durability或全部历史远端资源归还；priorRemoteOwnership全程UNKNOWN_NOT_CLEARED。未知close继续原对象强持有、拒下一I/O，不用OS退出或GC清信用，迟到归还不升级旧attempt。

## 有限本机证据

唯一main-001，**45项断言PASS，14条实际本机原调用**：6个不同真实Git shell探针场景、1次全6脚本sh-n、7条完整生产流程模型命令。每场景只运行一次，没有压力碰调度或失败后重复探针。

真实shell覆盖正常、printf原rc7、decoder原rc8、od原rc9、printf写入短件、解码错误字节。失败的原rc/完整父回执与状态文件原样保留；正常实际文件恰AA==和00。各场景的UID/pwd用本机函数模拟，实际printf/base64/od/文件和进程返回来自本机，不冒充Android实测。不是仅用假客户端论证单写者安全。

直接生产parse_probe拒绝状态缺失、截断、空rc、重复、乱序、真实T5P原交织286B，以及只替换为新nonce/前缀后仍交织的版本；后者证明拒绝不限于批次身份不一致。严格串行回执支持CRLF。没有宽松修复字节，也没有重试直到通过。

完整本机模型仅验证新流程整合：目录先创建、正常5B状态文件、实际Python子进程标准解码256B落盘，raw预哈希/流读256B、实际ASCII提交344B、独立rawSHA匹配。Android UID/mode与回执字段为模型，不能证明设备兼容。14原本机进程/管道返回、retainedLocalOwners0，无新增在途owner；外层检查exit0、60s界未触发，无测试repair或历史整套重跑。

证据evidence/local-check-results.json绑定最终被测源码、原记录、6真实shell场景与整合结果；check-attempt.json/check-attempt-result.json/checks.log保留原执行。准备阶段一次Python路径笔误未启动修改脚本，更正后继续准备，没有因此重跑测试或设备。

## 下一提案与交付

新批次D1-E4A-T6P-TABLET-20261017，nonce E4T6P_TABLET_20261017_ONCE，新目录files/e4_diag_T6P_TABLET_20261017_once，唯一payload256.bin与两个准确探针文件；旧26B、归档、T5目录和媒体不访问。详细入口见D1_E4A_T6_BINARY_TRANSFER_PLAN_V1.0.md，当前executionAuthorized=false，待负责人另派。

仍为raw256B/encoded344B无LF，host raw预哈希/流读各256B，编码预哈希/提交各344B；probe额外4B输入文件和1B解码文件，od最多读1B；独立payload hash最多256B。metadata计划6/上限20、producer1、每命令15s/共同本机收尾2s/日志1MiB。状态文件额外≤4/4KiB，当前正常2/5B；加payload后正常三文件261B。

未来媒体流量/内存/时限设计以原T5 tools/future-media-plan.json字节继承，不重查源：MP4 349102→465472B，AVI736454656→981939544B；无整片缓存或编码大副本，raw块24576B/编码块32768B/carry≤2，工作缓冲设计256KiB而非RSS测量；拟定transfer60/600s、hash15/120s仍未授权。可复用相同流式pump/receiver，正式媒体n/path实例化和无覆盖fixture发布另批审查，先MP4后AVI及原产品验证，不把诊断成功等同播放成功。

本轮ADB/device/真实媒体stat-read-hash/Gradle/下载均0。旧T5/T4/产品冻结只读，旧失败不回填，D1 NOT_PASSED/M0 NOT_STARTED/P0与历史FAIL保持。仅必要来源和新证据，无历史ZIP嵌套。

新seal d1e4at6/evidence/serial-freeze.json；清单evidence/source-manifest.json；完整小包artifacts/D1-20261017-E4A-T6-source.zip。外seal SHA/ZIP身份/数量及实际只读verify结果集中交负责人，封存后只读。核验包含精确成员、原日志与最终源码、继承模块及未改receiver函数，不启动候选或设备。
