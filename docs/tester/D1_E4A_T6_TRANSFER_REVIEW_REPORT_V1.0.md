# D1 E4A-T6 单父写者探针静态复审报告 V1.0

日期：2026-10-17；tester。依据 `docs/milestones/D1_E4A_T6_TESTER_REQUIREMENTS_V1.0.md`，仅审冻结源码及已有证据，未执行设备、fake、真实shell探针、历史测试或媒体。

**结论：SUPPORTED_FOR_SEPARATE_PRIVATE_256B_T6P_DIAGNOSTIC，新增静态阻断问题0。** E4AT5P-F01的共享回执并发写者设计已在源码中消除，支持另派唯一T6P实机回归。旧T5P原交织实证及NOT_ADMITTED不变；本次不宣告该问题实机回归通过。Android解码/od-N1及新协议实际结果仍UNKNOWN/NOT_RUN，D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL保持。

## 1. 冻结身份与继承

| 项目 | 复审结果 |
| --- | --- |
| 根/候选 | docs/coder/d1e4at6 / D1-20261017-E4A-T6 |
| 外seal SHA256 | 861d2e179c66801f80353d79c6c2420a10f5748dfdd090db991a95e3ac0d6f37 |
| ZIP | 86977B；73bef2bc282e4474e53f9d867bc317d8ee5f6928c64ed7418a706b557b8be681 |
| 准确清单/ZIP成员 | 52源 / 54不可变，大小/SHA/集合PASS |
| 只读verify | PASS；67文件读取、物理482555B/ZIP逻辑264756B，无启动候选或设备 |
| tester独立审计 | PASS；只读清单、封包、AST及既有原记录/小产物，无生产函数导入或重跑 |
| 原T1 pump | 13077B，SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d，逐字节继承 |

command_response.py、stream_base64.py和future-media-plan.json与T5逐字节相同。按T5→T6批次/标记替换后，argv/context/context_script/processes_script/mkdir_script/receiver_script/proof_script/parse_line/one/receiver_observation/parse_receiver/parse_proof/check_processes共13函数AST相同，未借修探针放宽接收、旧owner或独立SHA门。产品冻结引用仍为 `a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d`。

已读需求、交付、传输提案、private_commands、diagnose_ascii_once、check_serial_probe、local_client、run_checks、package_tools及原记录；继承部分结合T5已有源码复审和字节身份核验，不重跑旧51项。

## 2. 真正单写者及原失败状态

新probe没有管道、后台段或共享FD3。原父shell前台printf固定AA==到probe.ascii，返回后保存a；只有a=0才前台base64-d从该文件重定向到probe.raw并保存d，否则d=SKIPPED。两条stat命令替换分别保存原rc和大小；满足前端成功、4/1B及两文件普通非链接后才od-N1，返回后保存t，否则t=SKIPPED。子命令正常stdout仅进入准确文件或父命令替换，协议stdout只由父shell在这些操作返回后串行输出。

因此修复依据是消除并行协议写者，而非假定一次printf等于一次原子write。父shell的三个PROBE_RC及最终PROBE依次输出；parse_probe严格要求四行、固定printf/decoder/od顺序和准确字段，不排序/拼接/忽略异常字节。

各端rc必须全部0；原UID10221/pwd原值、正parentPid、mode=SEQUENTIAL_FILES、两stat rc0、asciiBytes4/rawBytes1、hex只00也必须相符。非零与SKIPPED均拒绝，未执行阶段不填伪0。父脚本最后的test可能返回通用exit1，但回执中仍保留实际printf7/decoder8/od9，不将父exit冒充各端原错误。wrong-hex即便外层exit0、三端rc0，仍被内容门拒绝。

缺失/截断/重复/乱序/空rc/旧交织均拒绝，支持CRLF。原286B T5P stdout SHA `f15424ea4759dc3e299308d50f8da8ebf3a48d0e79169ee65525122a2ad7a8d3` 与tester原证据逐字节一致；已有证据还拒绝仅替换新nonce/前缀后的交织内容，拒绝不局限于旧批次身份不同。

## 3. 状态文件、顺序和预算

新准确目录 `files/e4_diag_T6P_TABLET_20261017_once`，只允许其中probe.ascii、probe.raw和payload256.bin。本方案明确使用负责人允许的诊断状态文件：正常两文件4B＋1B，最多4个/4KiB；加payload正常三文件261B。

创建前原context/files及新目录不存在，UID快照按旧接收器门拒绝，不signal；然后umask077独占mkdir准确目录，probe再次检查状态文件不存在/非链接，set-C拒覆盖。固定输入创建ASCII状态文件，解码写raw状态文件；两文件stat4/1及普通非链接门通过才od最多读1B。失败留目录/已建空件或部分件，不清理、重用或切路。

状态文件上限是准确受控工具/输入合同，代码只有两个写目标；没有内核配额，不能宣称限制任意恶意故障解码器输出量或抵抗同UID恶意并发替换。stat长度异常会阻止后续od/producer，不授权额外文件或无限读取。

流程已变为features→context→UID快照→新目录→顺序probe→producer→独立proof。probe失败时**目录及状态文件可能已存在**，producer源尚未打开；不得套用T5旧“探针无文件”的假设。任一原响应失败先保存原JSON，严格门拒绝；完整成功探针才形成result.decoderProbe，失败原标记仍在原JSON中保留。

T6P metadata计划6/硬20、producer1；每命令及producer15s、共同本机归还观察2s、日志1MiB、单原收据64KiB；stdout/stderr各16KiB、保留各4KiB，超前缀不能认完整响应。CREATE_NEW attempt在远端变更前消费，失败不补跑、改令、加时或清理。设备工具支持仍须另派实际验证。

## 4. 接收、独立rawSHA和原owner保持

固定合成raw256B，SHA `40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`；无LF编码344B。原同FD预哈希/流读各256B、编码预哈希/提交各344B，rawSource和encoding分列计量摘要，不把344B提交当作256B落盘。24576B raw块、carry≤2、32768B编码块、末padding、正短写信用和原SHA/FD身份门均继承。

唯一producer不带-n，noclobber直接私有解码；原BEGIN/DECODE/END须完整、原UID/pwd/同PID/目标一致，decoderRc0/statRc0/raw256。独立新命令再次核普通非链接/UID10221/长度256/非全局可写、前后stat身份和head-c256原始SHA。缺END、decoder非零、短件或错误SHA原门未放宽。文件字节证明不等于fsync/durability、播放或产品COMMIT。

T1实际stdin/source close、drain、wait及线程门未变；未知原Job/源/管道强持有、不下一I/O、不二次close/GC/OS退出清信用，CLI保持原解释器直到实际归还；晚归还不升级旧失败attempt。前台命令返回与文件stat可观察结果不等于独立审计内核所有FD关闭或全部历史远端已归还，priorRemoteOwnership仍UNKNOWN_NOT_CLEARED。15s不是远端生命周期硬保证。

## 5. 45项断言/14原调用的已有有限证据

唯一main-001，45/45；输入hash绑定最终源码，check-attempt/result/log核验原外层exit0、60s界未触发。14原调用由6个不同真实Git shell场景、1次全部6脚本sh-n及7条正常整合模型调用构成，每场景一次、无stress/失败后重复探针。tester未重放任何场景。

| 真实本机shell场景 | 原printf/decoder/od rc | 原外层exit | 原状态文件B | 结果 |
| --- | --- | --- | --- | --- |
| normal | 0/0/0 | 0 | 4/1 | 四行及hex00通过 |
| printf-nonzero | 7/SKIPPED/SKIPPED | 1 | 0/未创建 | 拒绝，原7保留 |
| decoder-nonzero | 0/8/SKIPPED | 1 | 4/0 | 拒绝，原8保留 |
| od-nonzero | 0/0/9 | 1 | 4/1 | 拒绝，原9保留 |
| truncated-file | 0/1/SKIPPED | 1 | 1/0 | 拒绝，实际短件保留 |
| wrong-hex | 0/0/0 | 0 | 4/1，值01 | 内容门拒绝 |

以上由真实本机shell/工具及文件执行，回执实际完整、各原本机owner返回；UID/pwd由本机函数模拟，toybox路径映射为已有本机工具，因此不能证明Android兼容或权限。该45项不是任意设备失败的穷举覆盖。

正常整合模型调用生产run_diagnostic，实际自有小文件probe.ascii=AA==、probe.raw=00、payload256.bin=0..255，raw256/encoded344/独立SHA正确，metadata6/producer1；但Android模式/UID/协议字段由Python固定模型提供。该模型不执行Android probe脚本，单写者代码依据和6真实本机场景单独评估，不能混为设备实证。

所有14原记录完整长度/SHA、退出和实际stdin/source/writer/flush及输出close核验通过，retainedLocalOwners0；已归还只针对这批本机调用，不洗掉T5隔离UNKNOWN历史或设备旧UNKNOWN。没有本轮生产诊断在途。

## 6. 交付与后续范围

未来媒体计划逐字节继承T5：MP4 raw349102→wire465472B、AVI raw736454656→wire981939544B，总wire982405016B。仅计划同FD流式、256KiB工作缓冲预算（非RSS测量）、transfer60/600s与hash15/120s；无媒体CLI、源重查或执行，无整片编码副本。当前固定256B不自动扩大媒体路径/n；无覆盖fixture发布和产品测试仍另批审查，先MP4后AVI，传输通过不等于播放通过。

tester证据：`docs/tester/D1_E4A_T6_EVIDENCE/identity-and-recorded-evidence-audit.json`及只读audit.py。报告完成主动通知负责人并保存回执。tester本轮ADB/设备0、fake/probe重跑0、媒体stat/read/hash0、Gradle0，无冻结源码或旧现场修改、无在途。支持另派T6P，不自动执行设备或下一批。
