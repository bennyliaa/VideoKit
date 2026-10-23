# D1 GLOBAL_IDLE_CONTRACT03 独立整包 B 要求

2026-10-23；负责人已收到并审核双方完整报告，正式派本次独立整包B。当前候选属于集中修订的评审包，不是已通过或稳定交付。开发有限故障簇原FAIL与未覆盖目标保持，本次新scope独立验证这些目标，不续跑原scope。

## 1. 准确完整输入

| 层 | 准确来源与已审范围 |
| --- | --- |
| 五项修订候选 | `docs/coder/d1android02-global-idle-contract03-fix`；原BLOCKED报告 `8e4e5b6f26867465852eeeee914c590b06204a7c6c7722e2dd5ffc7022cc7dba`；98项manifest `55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81`，负责人核98项/1245040B、bad0及ZIP99唯一成员。原辅助失败/临时close未证不改。 |
| 固定运行源码 | source17 `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93`；gate9 `9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72`；plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`；原FIX02/Native/runtime和实际角色预算保持。 |
| 完整开发自测SELFCHECK02 | 报告 `docs/coder/D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_REPORT_V1.0.md` SHA `9acdf4089a4134997e53adf6a765b11ca4f6ca48a35a256eeaa21b7497f30246`；材料manifest `ec171260f95bfcfd712d4e2245c68b6612f2a8939631ba79a92f9b7f73b2343a`，负责人核484项/5286017B、bad0；ZIP `d3425d18bbf12910ac204bf9d0db7ab03c32687c4f47f95266387aca72af2c65`，485唯一成员。14组13PASS/1已知时限FAIL，不能写成全绿。 |
| 已独立验收的同源语义A | 报告 `a6f2f4fe2cf1e7d8553d27f428f79753251ab8653e7d579a4fab621f506d7ea2`；manifest `8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066`，408项/3877819B、bad0。366语义+34纯静态全部通过、原45和17条件正例通过。 |

语义A可作为本次独立整包验收的一部分：先核准确源码与原输入/宿主/证据身份未变，清楚标注其独立原执行范围，不必机械重跑400项。至少核本次完整入口实际调用相同已测生产函数，补充新发现的同类边界；身份模型/根谓词原纯替身不能替实际Gate/目录链。开发346重放与A不混算新增独立案例，也不据A通过推定完整B通过。

## 2. 独立整包必验范围

1. **五缺陷到实际原链。** 解析与条件正例引用已接受A并核入口调用关系；fixture准确程序/完整argv及14文件运行时、原Gate source读账/固定producer真实归还；三入口在同一当前tester根中进入原完整链、越界/旧根/别名拒绝；当前提案六组path/hash与false执行批准；无OEM/system/UID默认信任或instrumentation降级。
2. **完整调用和资源。** 原collector/wire、原Gate/Owner/PS七角色、END、once拒重入、初proof不变、原唯一释放/原外层回执；preStart13的准确已知返回、PS post与最后Start、物化变化、准确小追加 `OWNER_SOURCE_PIN_ENTRY`。保守未证字段不补ACK，原WRONG_OUTPUT_SOURCE先cap缺口与准确小追加结果分列。
3. **11个有限故障目标逐项准确判据。** MATERIALIZE_KNOWN_REJECT、NO_SDK_ABORT、WRONG_HOLDER、WRONG_OUTPUT_SOURCE、MATERIALIZE_LATE、RECEIVER_LATE、TAIL_LATE、EXPIRE_DURING_MATERIALIZE、BUSY、PRESTART_KNOWN_REJECT、OWNER_END_TAIL。每项固定预期目标、最少已进入阶段、真实拒绝原因、原归还/claim释放与计账；任意ValueError、先触gate/proof/cap或其他提前拒绝不能当目标通过。失败注入本身的业务结果与测试判据结果分开。
4. **静态可操作性和未证。** 外部routeProof后双hash接收与proof10s/gate30s、facts至target至多300s仍未实际验证。当前签名/公钥/密钥托管/IPC方案未获实施批准、不开发、不签authority；本轮只核当前明确未实现/未批准边界。离线B结果不能自动签真实facts、系统服务资格或现场。

开发有限故障簇实际首例为GATE_STICKY、第二例RUNNER_GATE_STICKY，均未到目标；后九项NOT_RUN。其原scope不重放，原宽断言不复用成准确判据。先静态核当前候选允许的OFFLINE配置、计时起点、驱动/profile/source核验成本及每场景期望，将实际采用值冻结。正常及不跨时窗的场景使用候选允许的原预算；需要跨窗的注入只可用当前契约允许的准确fixture值，不擅改生产门或扩大候选允许范围，不暖机/重复尝试来规避首次成本。原限内若再提前拒绝，如实列为目标未覆盖并交完整原因，不能换一个scope循环重试。

## 3. 独立驱动、预算与停止边界

复用已成功的revision02整包B和已接受SELF原身份/双流/原wait/原H返回机制，准确派生新驱动/profile并冻结；不要运行原错误run_batch.py。实际程序、完整argv/cwd/env、PS/.NET后代调用图及读取写入/进程预算在构造前核定；Windows audit只观察，不能在临时pipe之后主动抛参数拒绝。新实际元组不能偷套不相关profile。

本次独立B：outer上限720s、worker660s、600s停止新准入，并发1/retry0；辅助原调用观察期按准确固定SELF派生profile，单次不超过180s，不强停。输入/源码及控制总读取预存不超过4GiB/8192次（明确后代/物理IO未证），归档不超过128MiB/4096项、单证据文件1MiB；辅助进程保守图最多128、原审计事件最多512。执行前把准确总量和更紧逐组值落盘，原生产source/字节/角色/600/30/20/10/120门全部保持。

只使用当前统一白名单中的全新 `docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures` 子scope与独立新证据子目录；原SELF02的 `dev03-ce9fcb60`、旧001a/session55065、旧c45d等scope/锁/进程不查询或操作。开发和阶段A的原件全部只读，原98文件及484/408记录不覆盖。全包前后身份核验与准确ZIP路径/唯一成员核对。

预估无法在预算内完成时，动态前完整交静态估算；不得执行后加额。普通已知FAIL且所有原件已证归还，可继续原计划中其他新场景，不重试失败scope；遇不确定创建/原返回/close则停止新增动态，集中报告，不制造无限UNKNOWN或强制收尾。不得以空PID、工具退出、自写marker或custody空单独替临时资源原返回证明。

真实SDK/ADB/Native route/TCP/help/设备/Gradle/媒体/新依赖均0；不存在本次LIVE授权。无共享Git/index操作，用户要求后续tester按需整批分支/PR提交仍有效，B完成后由负责人选准确静止检查点，不在动态过程中切分支。

## 4. 交付

一份集中完整B报告：五项修订整包映射、A引用与本次实际结果分别统计、全部11目标精确命中/未覆盖及原因、原返回和预算/未证、source/gate/plan/提案/调用图、输入/独立驱动/profile、全包核验、新证据manifest/唯一ZIP或独立回执。所有新旧FAIL/NOT_RUN/UNKNOWN和once账目保全，不补ACK退款。

完整结果主动报告负责人 `01a107c3-2bf9-7fa0-94a0-234258ca6774`；缺陷集中回交，不逐问题联系coder、改候选或自动启动下一批。D1未通过/M0未启动，主里程碑与Flutter/独立Kit/成熟开源框架版本许可及全P0保持。
