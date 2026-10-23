# VideoKit CONTRACT03 独立整包 B 报告 V1.0

2026-10-23；tester；批次 `99e9bab6-e818-4fcf-a487-d0aed85b3a78`。

## 结论

**FAIL_TARGET_COVERAGE_GAPS：本次整包不签无保留通过。** 11组中10组通过、1组有限故障簇因目标未覆盖失败。11个故障场景逐项执行一次，9项准确命中，2项未覆盖；没有循环重试、扩大原生产门或修改候选。本次没有新增已确认的产品源码缺陷。

同源语义A、程序身份/源读账、同一新tester根完整链及准确source门已有下述通过证据，不能据此把两个原场景改绿。全部本轮原进程/资源已返回，无新资源UNKNOWN。D1未通过、M0未启动；不自动进入下一批或现场。

## 准确来源与冻结

负责人会话 `01a107c3-2bf9-7fa0-94a0-234258ca6774`，turn `01a16887-3bee-7bc0-a134-7d2b8eda09e6`，call `exec-1f81fe42-e7ec-49b9-8a34-6bc34c0b0cfc`。[本批工作单](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_TESTER_REQUIREMENTS_V1.0.md) SHA-256 `856ccf3063c4d869d1233a14ab95aeaf4987d983b4dc0ba1a17e0bdc3beee942`。

| 层 | 准确身份 |
|---|---|
| 产品 | docs/coder/d1android02-global-idle-contract03-fix，原98文件/1245040B |
| source17 / gate9 / plan | `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93` / `9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72` / `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8` |
| 产品manifest / ZIP | `55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81` / `45fb593f8b7aa916095540275a7287bdf01e524f5a983befc3768e9c9cb4a58c`；99唯一成员 |
| 开发SELFCHECK02 manifest / ZIP | `ec171260f95bfcfd712d4e2245c68b6612f2a8939631ba79a92f9b7f73b2343a` / `d3425d18bbf12910ac204bf9d0db7ab03c32687c4f47f95266387aca72af2c65`；484文件/485唯一成员 |
| 已验收A报告 / manifest | `a6f2f4fe2cf1e7d8553d27f428f79753251ab8653e7d579a4fab621f506d7ea2` / `8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066`；408文件 |
| 本次订单 | `99153c6d38f34034eee118bf939550a363b785c5a4984614f9936d1fc3f50529` |

98/484/408文件启动前后核验bad0；两份原ZIP按完整成员路径、长度/hash、唯一性核验通过并关闭原流。原件未改。

全部新夹具位于 `D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures/b03-fad80286`；独立证据位于同父根 `b03-evidence-fad80286`。没有写coder目录、读取其动态状态或复用旧工作根。

## 五项修订与实际链

1. 解析两项：准确引用A的366语义+34纯静态、原45矩阵和17条件正例；不机械重跑400或把开发346混算新增独立案例。408原件未变，当前admission SHA仍 `fc09218ed9094641a7c89b69ae4d06226f758b2909bde84dbd171c4f0edcbd8a`；本次实际global_idle入口仍调用其 `Get-GlobalIdleDecision`，完整七角色经该入口通过。A的68条归档缺真实资格继续未证。
2. 程序/身份：原prepared且未消费Gate上实际运行固定本地producer，生产完整argv及身份守卫执行。runtime identity `2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48`，程序hash `5640e9be2fd33d05a1a9ae1228e2354609a69ab831605995ec4e2bd6da8fff5e`；原Gate source实际增加 **112759B/2次**，与生产fixtureRuntime完全一致。原Popen/reader/wait/stream/H和原claim返回、错误外部hash及once拒绝通过。原producer输出532B；status、长度偏大、尾项、NUL四个坏wire均按准确原因拒绝。
3. 提案：同源A六组path/hash、false执行批准由原98前后不变核验保证，历史/当前提案归属保持；未生成authority。
4. 根：同一个新tester根实际通过Runner/Gate/Owner/PS七角色、END、初proof不变、once和原唯一释放；真实Runner准入中越界、相似prefix、旧候选根、点别名分别准确拒绝FIXTURE_HOME或CANONICAL_OUTPUT_PATH_REQUIRED，home未创建，没有以A纯替身代整链。

正常链scope `6e8f6fb6da84a81952b2aa4e206591d2cfbd2fa1c3f404440554a28bbb1a513d`；初proof `dde0366106dea969f627dab281231b05b6622972fedd955ca3d116eab3076f7c` 未改。terminal writer及原claim unlock/close返回。install/scopeAll均为固定本地fixture，不能解读成实际安装或平台scopeAll通过。

## 全部11个故障目标

每项的期望、最少阶段、原配置和一次尝试预存于scenarios.json/faults.py及scope内target-before-constructor.json。原因与阶段必须同时满足；提前拒绝不能当目标通过。已知原件归还后继续其他预定场景，无失败scope重试。

| 场景 | 实际原因 / 本地控制器数 | 判定与到达阶段 |
|---|---|---|
| MATERIALIZE_KNOWN_REJECT | CONTROLLED_MATERIALIZATION_REJECT_BEFORE_OPEN /0 | PASS；原Gate/proof及物化proof读已到、尚未开activation |
| NO_SDK_ABORT | CONTROLLED_NO_SDK_ABORT /0 | PASS；原物化receipt writer已返回 |
| WRONG_HOLDER | WRONG_HOLDER_REJECTED /0 | PASS；原不同线程holder检查达到指定拒绝 |
| WRONG_OUTPUT_SOURCE | RUNNER_CONTROL_CAP /0 | **目标未覆盖**；原改源读取先超control，未到OWNER_SOURCE_PIN_ENTRY |
| MATERIALIZE_LATE | RUNNER_PROOF_STICKY /0 | PASS；原10.25s延迟activation writer返回，超时观察pending>0且原lease持有 |
| RECEIVER_LATE | RUNNER_PROOF_STICKY /0 | PASS；原延迟receiver返回，超时观察pending>0且lease持有 |
| TAIL_LATE | RUNNER_PROOF_STICKY /0 | PASS；原物化receipt先返，固定10.25s尾段越窗 |
| EXPIRE_DURING_MATERIALIZE | PERMIT_EXPIRED_OR_FUTURE /0 | **目标未覆盖**；9s permit在前置阶段过期，无home/Gate/proof/物化阶段证据 |
| BUSY | OWNER_STICKY_NO_SUCCESSOR:CAPTURE_FAILED_STICKY /2 | PASS；第二role实际捕获ActiveInstrumentation，后继阻断 |
| PRESTART_KNOWN_REJECT | OWNER_STICKY_NO_SUCCESSOR:CAPTURE_FAILED_STICKY /1 | PASS；Start未入、2raw/Process唯一收尾，无假EOF/pipeClose |
| OWNER_END_TAIL | OWNER_STICKY_NO_SUCCESSOR:PROOF_WALL_TIMEOUT_STICKY /7 | PASS；END原及时writer归还后，原允许2s尾门越同一窗口 |

九个命中及改源cap场景均已证原线程归还和holder唯一释放。过期场景实际9.344s，`f-7/actual-home`未创建；原行originalClaimReleased=false保留，该项未进入claim而无释放可做，不改成true或UNKNOWN。同码不能补足物化阶段未到。9s配置在faults.py中预冻，未事后调整或换scope重试。

两个覆盖缺口不等于两项新确认产品源码缺陷。原WRONG_OUTPUT_SOURCE cap结果保持，物化内过期也不能凭前置过期拒绝或开发其他局部通过签绿。

## 其他准确通过

- preStart13先于生产链通过：0/1/2raw、输入source、原Process唯一Dispose；真实已启动本地子进程正常归还；未知只纯模型。
- 默认/live缺准许、批准/hash/source/scope/backend/产品/角色/schema/类型/预算反例通过；无SDK。
- 原PS post reset/重复/event/source/holder/mode/类型与最后Start时钟/过期/窗口守卫通过。
- 原物化字节变化准确MATERIALIZATION_ORIGINAL_PENDING_OR_BYTES，原返回/释放通过。
- 小追加预先算账，只给本次自有PS副本追加1换行字节，原write/flush/close返回，控制器0、pending0、初proof未改，准确 **OWNER_SOURCE_PIN_ENTRY**，原holder唯一释放。它提供准确source门覆盖，同时原改源场景未命中的事实不改。

小追加预界runner242406B/gate218281B；实际236316B/195253B，均<262144；自己的输入创建11662B计pre，追加1B，无免费整文件control重读。

## 原返回与预算

复用已接受SELF原Popen/H、双reader、单wait、唯一stream/H close。13源包 `b3cdd53b3527e39aac726d1014473e69f2c1a552fa7243a6be434adc5901c2e1`、SELF报告 `2fd415f0bbee624abae236934514a4f9a3310e3d04ac7937d10b65cc9f3fb613`和14运行时文件启动前已核。新驱动/profile/生成者与33项纯启动配置先冻结。前置wrapper仅校验本批固定程序、完整argv/cwd/env/流与脚本族，未经改写委托原Popen，返回同原对象，不接管candidate流。

Windows audit仅内存观察，无回调文件IO或主动拒绝。父worker31构造/31观察均匹配且构造返回，外层另1观察匹配；CLI/.NET后代依冻结图和原回执校验，不冒称全局hook观察。

| 项目 | 上限 / 实际 |
|---|---|
| outer/worker/停新增 | 720/660/600s；外层214.016s、worker212.563s |
| 原辅助观察 | 每次≤180s；7个自有辅助全原wait/readers/streams/H返回，stream合计3032B；外层观测worker stdout166B/stderr0B |
| 图/audit | 保守图78、上限128；父构造31，audit31+mismatch0，外层audit1+mismatch0，无真实审计拒绝注入 |
| source/control读取 | 4GiB/8192次；可记录in-process Runner source109913881B/359次，driver960368B/58次、外层93746B/21次、后验12073275B；拒绝构造、helper及CLI/.NET后代未合并为完整实测总量，不把小计称全部物理IO |
| 正常链逻辑control | 初proof183644B+post40762B+receiver13754B=238160B<262144；END466723B<1048576，logical inbound468775B<3276800 |
| 归档 | 128MiB/4096项、单1MiB；实际文件字节/hash见新manifest及独立回执 |
| 保守未证 | candidateOnlyTerminalWriterCloseNotProven等原值保留；physicalIO UNPROVEN，业务FAIL/amountUnknown不因资源已返补绿 |

原worker PID18256、creation FILETIME `134372300414254367`；原H身份及实际自身命令行/nonce、wait/readers/streams/H唯一close已观察。7个自有辅助原返回已核，候选collector与Gate/Owner返回按原回执和本批持有原对象核验；最终五类custody均0。没有只用空custody或工具退出替资源证明。worker/外层观察exit2，工具层exit1分列，原因是目标覆盖失败，非资源UNKNOWN。

原生产source、600/30/20/10/120、metadata4/SDK7、字节/角色/once门均未扩。完整Python/.NET物理IO未全局测量；所有失败原预算/once/账目保留，无退款/补ACK。

## 辅助失败与全部未证

首个文件型准备脚本因-I漏加自身模块路径，在纯profiles导入处ImportError；当时无订单、候选调用或Popen。原脚本/错误回执保留，第二文件型入口仅完成剩余纯检查与冻结，未重复复制或动态scope；最终订单仅执行一次。报告草稿的一次工具字符串解析失败也未执行I/O，修正文本写入后不重跑测试。

外部routeProof后双hash受proof10s/gate30s、facts至target最多300s；签名、公钥/密钥托管、IPC及authority当前未批准实施、未实现、未运行。本次不签真实外部往返、facts、系统服务政策或现场就绪。

旧dev03-ce9fcb60/c45d/001a/session55065及其他旧对象不查询、attach、kill、二close、补ACK退款。原开发13PASS/1时限FAIL、临时close未证及所有旧FAIL/NOT_RUN/UNKNOWN保持。没有Git/index、test_media写入、新依赖或真实SDK/ADB/Native route/TCP/help/设备/Gradle/媒体动作。

本报告完整集中回负责人，两个准确目标缺口与小追加补充证据分别裁定；后续准确范围及静止检查点提交由负责人决定。tester当前不新增测试，不逐问题联系coder或自动进入后续。

关键原证据：[逐场景汇总](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/b03-evidence-fad80286/fault-summary.json)、[前置过期裁定](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/b03-evidence-fad80286/expiry-target-adjudication.json)、[准确小追加](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/b03-evidence-fad80286/group-11.json)、[原外层返回](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/b03-evidence-fad80286/outer-final.json)、[原包后验核验](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/b03-evidence-fad80286/post-audit.json)。完整文件清单与独立冻结回执和本报告同目录。
