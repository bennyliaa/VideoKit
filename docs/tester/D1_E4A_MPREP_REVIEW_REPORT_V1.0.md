# D1 E4A-MPREP 双源整批预置静态复审报告 V1.0

日期：2026-10-17；tester。依据 `docs/milestones/D1_E4A_MPREP_TESTER_REQUIREMENTS_V1.0.md`，仅审冻结源码/计划和已有有限本机证据，不ADB、不重跑fake或真实shell测试、不读取真实媒体、不Gradle。

**结论：SUPPORTED_FOR_SEPARATELY_DISPATCHED_MP4_THEN_CONDITIONAL_AVI_PRELOAD，新增静态阻断0。** 支持负责人正式派发一次固定整批：先MP4，在本批原完整证明、ready同步/关闭/读回及原owner归还全部成立后，同批条件继续AVI；无需每文件再造入口或交接。当前真实两源预置NOT_RUN，不能把本机小数据证据或T6P合成成功当作媒体已准备。D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL保持。

## 1. 冻结身份与审查边界

| 项目 | 核验结果 |
| --- | --- |
| 候选/根 | D1-20261017-E4A-MPREP / docs/coder/d1e4amprep |
| 外seal SHA256 | 96f62df6a902a8b20eab73d97de63ea82321ceffe42c15f983530a245c3b2660 |
| ZIP | 236592B；5c43f62ec601971427ae66bda0fe451c563018c81679c5c07d2f425bb7c01047 |
| 清单/ZIP准确成员 | 163源 / 165不可变，大小/SHA/集合PASS |
| 包内只读verify | PASS，178文件读取，物理2865837B/ZIP逻辑2445482B；无进程启动或媒体读取 |
| tester独立审计 | PASS，仅核现有原记录、元数据、封包及自有小产物，无生产函数导入/重跑 |

exact_process.py/command_response.py/stream_base64.py与T6逐字节相同；原T1 pump13077B，SHA `f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d`。t6_protocol.py仅机械替换批次/nonce/目录，其余代码与T6相同。T6P真实256B报告/result原来源绑定通过，旧结果不扩大为媒体或产品通过。产品冻结引用 `a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d` 不变。

已读需求、交付、PRELOAD_PLAN、preload_once/media_commands、固定manifest、local_transport/local_client、check_preload/close_unknown_case、package_tools/run_checks及产品方法准备。所有真实源身份仅比对旧冻结元数据，未stat/read/hash真实源。

## 2. 两个固定源和流式参数化

| 项目 | basic.mp4 | subtitle.avi |
| --- | --- | --- |
| 固定host源 | D:/CodexProjects/VideoKit/test_media/imgs_and_videos/videos/sample.mp4 | D:/CodexProjects/VideoKit/test_media/02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi |
| raw B | 349102 | 736454656 |
| 无LF编码B | 465472 | 981939544 |
| raw SHA256 | 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 | 3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f |
| producer含预哈希 | 60s | 600s |
| 每次temp/final hash | 15s | 120s |

生产CLI无任意source、从AVI开始、skip/resume/force或receipt摘要参数。固定manifest由封包身份绑定，load_manifest核alias/顺序/raw量/SHA及Spec；仅local_only自有≤128KiB测试路径允许小样本Spec，不进入生产ProcessTransport。编码量4×ceil(n/3)，AVI981939544B仍低于原1GiB encoded界，无扩上界。

receiver按准确temp/n、proof按准确temp或final/n/head-c-n参数化原T6模板；自定义解析器核相同UID/pwd/PID/DECODE/END、n及原始SHA，未误用旧256B常量作为媒体证明。source/raw与encoded/提交计量分列，validate_producer还核原pump expected/prehash/stream/submitted与encoding的计量和摘要对应关系。

同原只读FD预哈希/seek/流读、24576B raw块、carry≤2、32768B编码块、末padding、无LF和正短写信用保持。工作设计256KiB不随源长度增长，不整片缓存或存编码副本；不是总RSS测量。达到声明终点/FD元数据/rawSHA不等于恶意并发源快照。600s包括预哈希，不能把约1.56MiB/s编码吞吐下界当现场实测保证，无自动加时或重传。

## 3. 空间、临时件和无覆盖发布

固定设备HA1Q6WXR，app com.videokit.app/UID10221/pwd原值；新私有temp目录 `files/e4_mprep_TABLET_20261017_once`。准确temp为basic.mp4.part/subtitle.avi.part，final仅 `files/e4_fixtures/basic.mp4` 和 `files/e4_fixtures/subtitle.avi`。fixture父必须现成、非链接、rwx可访问；不补建父、不改权限、不用外部路径。新目录/两个final任何冲突都停。

初始df-k门为两源736803758B＋64MiB＋5B探针，向上取整需785071KiB。每源前重核准确temp/final冲突和父角色/剩余空间；AVI门为剩余736454656B＋同余量＋5B，需784731KiB。现有占用留在df used，不清理旧件或重复退还空间信用。格式异常/空间不足停止；df不是预留锁或并发空间保证。

初始features/admission后一次UID快照，旧receiver线索拒绝不signal，未见仍UNKNOWN_NOT_CLEARED；独占新目录，复用T6单父probe，正常两状态文件5B、cap4文件/4KiB。probe失败可以留下目录/文件，不复用旧“无文件”假设。

每源唯一producer原完整成功及计量门后，独立temp命令核普通非链接、UID10221、非全局可写、n及前后完整stat/SHA。发布前重核temp stamp、fixture父UID及同device，合作式mv-n；随后要求原mvRc0、temp确实消失、准确final普通非链接且完整stamp相同。再另条独立final命令重核temp消失、原n/SHA及前后stat，并要求与temp原stamp完全一致（含dev/inode）。这证明同文件rename，没有把额外整片copy当发布。

既有合作式mv-n边界可接受，不重复请求许可，也不宣称抵抗同UID恶意并发。目标在门后抢建导致mv跳过/rc0时，temp仍存在会使原脚本失败，控制器在该调用停止，**不继续hash冲突final**；mv0不能当发布成功。失败不回滚删除已发布件，不清理原temp或冲突目标。

旧81407B归档、26B、T6P状态、cache/budget不在任何准确设备读写路径中；本批不会再次归档或清额度。

## 4. MP4到AVI的真实证据依赖及artifact owner

每源ready只在receiver、temp独立证明、publish、final独立证明四份本次原记录均通过、所有原owner已归还后生成。body绑定本批manifest、完整Spec、raw/encoded事实及四原记录的文件名/长度/SHA/expected argv。Store以CREATE_NEW写入、正短写、flush/fsync、实际close后返回ref；verify_ready立即读回长度/SHA并比对当前body，再重读四份有界原JSON，重新验证argv/exit/成功归还、raw/encoded与源SHA、receiver完整标记、双raw proof及同stamp/temp消失。

AVI循环入口再次验证同一个MP4 ready及四份原记录，且retained必须0。没有外部任意摘要或READY字符串参数；即便自造非空摘要和自洽body，也会与原四证明重建结果不符而拒绝。MP4任何失败、缺原final、ready fsync/读回/close异常或UNKNOWN均停止AVI。它是本次执行依赖，不是跨进程恢复或重用旧receipt入口。

Store原读写file登记pending强owner；close正常返回才remove。写预留在执行前累计，失败不退款；producer尝试也在调用前消费。read有单次128KiB＋1探读、4MiB/128次界；有界原JSON不计媒体内容读预算。若close抛错，原file保留、拒绝下一设备I/O；不能安全持久最终result时只报告阻断状态，不反复close或新造成功回执。fsync失败但close正常返回时保留已写ready/已发布MP4并记录失败，不能继续AVI。

原T1 source/stdin/drain/wait/线程的实际归还门不变；源或artifact UNKNOWN持有原对象，CLI保持原解释器，不能靠GC/OS退出或信用退款放行。晚归还不恢复旧失败批次。ready fsync/close/readback只证明本次OS调用事实，不是Windows目录项掉电持久性、Android fsync/durability或产品COMMIT。

## 5. 已有37项/48＋隔离7的有限证据

唯一main-001，37/37，最终源码输入和check-attempt/result/log核验，外层exit0/60s界未触发。48顶层原调用均RETURNED；隔离另7条原记录中最后源close为UNKNOWN1，原rawFD已关闭但包装close未返回，MP4尝试1/AVI0、下一I/O拒绝；不以隔离外层返回或解释器结束回填内部归还。

| 既有本机场景 | metadata | MP4/AVI producer | 首因/证据 |
| --- | ---: | --- | --- |
| success | 13 | 1/1 | 两自有源65537/70001B真实编码解码、rename、双SHA及ready读回，15次receipt读取85601B |
| short | 6 | 1/0 | RECEIVER_CONTEXT_OR_COUNT；26B temp保留，未发布 |
| wrong-sha | 7 | 1/0 | INDEPENDENT_RAW_PROOF；错误temp保留，未发布 |
| conflict | 2 | 0/0 | 原成功响应门拒绝；既有fixture不覆盖 |
| ready-fsync-failure | 9 | 1/0 | 原CONTROLLED_READY_FSYNC_FAILURE；已发布MP4和已写ready保留 |

另有直接ready语义伪造/缺原final记录拒绝、空间不足解析拒绝、同证据目录拒复用。真实Git shell的正常生成mv-n脚本保持dev/inode；在无冲突门后插入目标时，原mvRc0但脚本失败，temp/冲突目标都保留，没有PUBLISHED。全新生成脚本集中sh-n通过。以上共48顶层调用：五控制器模型场景42、两真实rename各stat+publish共4、syntax1、隔离外层1。

模型使用自有小文件和真实Python解码/本机rename，Android UID/mode/df/回执字段是模型；真实Git的UID/pwd也用函数模拟，不证明Android权限或完整AVI性能。空间不足为直接解析证据，不冒充一次设备空间失败；所列实际失败覆盖MP4失败阻断AVI，不宣称已有真实AVI中途失败或artifact-close抛错全路径故障注入。后两者保留代码层门和未实测边界，不夸大37项覆盖。

独立只读审计逐封包/SHA、48＋7原记录完整输出、ready四引用与实际自有final长度/SHA、同stamp及旧自有归档占位不变，结果PASS。审计不导入或重执行生产函数，不把本机`.keep`占位当设备旧归档实证。

## 6. 整批预算和可派范围

| 范围 | 设计上限 |
| --- | --- |
| host raw预哈希＋流读 | 1473607516B（各源两遍） |
| encoded两遍生成/实际wire | 1964810032B / 982405016B，无编码落盘 |
| device独立raw hash | 1473607516B（每源temp＋final各一次n） |
| 新媒体空间 | 736803758B＋probe5B，rename不重复copy |
| metadata/producer | 计划13/硬20；每源producer最多1 |
| 普通metadata/共同归还观察 | 15s / 2s；producer/hash见源表 |
| 日志/单artifact | 8MiB / 128KiB，预留最终result，失败不退款 |
| stdout/stderr | 各16KiB硬界，完整前缀各8KiB；超前缀不认完整 |
| ready元数据读 | ≤4MiB / ≤128次，单次≤128KiB＋1 |

包外Store及输出留痕属于本批日志，不是额外媒体副本。普通系统调用不能强制按时中断，超时/owned client返回不代表远端全归还；原历史UNKNOWN保持。

正式派发可采用计划准确一次入口 `preload_once.py --execute --formal-batch D1-E4A-MPREP-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_MPREP_EVIDENCE`，证据目录须全新。本静态报告没有实际派发授权，不自动运行。既有安装身份沿原E4A记录核对适用性，异常停，不重建重装。

product-test-preparation仅计划四准确方法normalMp4SixRealFrames、normalAviSixRealFrames、capabilityDenialDoesNotOpenSource、cancelRejectsWrongEpochOversizeAndLateFrame；不自动整类/Binder/故障测试。cancel须同设备真实normal回执独立审查与原稳定budget身份，不能任意非空SHA或更换身份放行。预置完成也只记TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS。

复审证据 `docs/tester/D1_E4A_MPREP_REVIEW_EVIDENCE`，完成后主动发送负责人并保存回执。tester本轮ADB/设备0、fake/shell重跑0、真实媒体stat/read/hash0、Gradle0，无冻结/旧现场修改、无生产在途。后续整批执行和产品验证分别待正式派发。
