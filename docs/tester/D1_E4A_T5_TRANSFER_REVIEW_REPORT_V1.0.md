# D1 E4A-T5 流式 ASCII 封装静态复审报告 V1.0

日期：2026-10-17；tester。依据 `docs/milestones/D1_E4A_T5_TESTER_REQUIREMENTS_V1.0.md`，只读检查完整冻结源码及已有有限本机证据，未重跑fake、编码/解码探针、异常用例或历史测试。

**结论：SUPPORTED_FOR_SEPARATE_PRIVATE_256B_T5P_DIAGNOSTIC，新增静态阻断问题0。** 支持负责人另派固定T5P；当前设备decoder兼容和传输结果仍UNKNOWN/NOT_RUN，不能将本报告当作实机通过或媒体准入。负责人已选定测试专用Base64路线覆盖旧工具实现选择，无须再次确认这一路线；不是产品权限/架构变更。D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL保持。

## 1. 冻结身份和复审范围

| 项目 | 核验结果 |
| --- | --- |
| 候选/根目录 | D1-20261017-E4A-T5 / docs/coder/d1e4at5 |
| 外部seal SHA256 | 425c53957f6733eda7c23d3cbb81251c31ddd20c3ab4da5a87187ff799291363 |
| ZIP | 126167B；32f5bb3d90c41491b7251f66e75b88798f6489c127f3e9cea92cb784f3de6eb8 |
| 源/不可变清单 | 88 / 90，准确集合、大小、SHA、ZIP成员一致 |
| 包内只读verify | PASS；101文件读取，物理878861B、ZIP逻辑604405B；无子进程/ADB/媒体 |
| tester独立审计 | PASS；只读现有清单、封包、原记录及自有小测试产物，不导入生产runner |
| 继承T1 pump | 13077B，SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d；与T4逐字节相同 |
| 继承响应门 | command_response.py与T4逐字节相同 |
| 产品冻结 | a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d，引用核验不变 |

已审交付/传输计划、stream_base64.py、private_commands.py、diagnose_ascii_once.py、原Job相关实现、command_response.py、check_ascii.py、local_client.py、close_unknown_case.py、run_checks.py、package_tools.py和未来媒体计划。包内verify还核对记录源码输入、旧引用和原检查日志身份。tester证据在 `docs/tester/D1_E4A_T5_EVIDENCE`。

## 2. 原始数据与编码流

生产EncodedSource以同一原只读FD执行raw预哈希、seek0及实际流读。每次raw读最多24576B，按声明剩余量限制；短读留0..2B carry，完整3字节组编码，只有声明终点才编码末尾carry/padding。标准Base64实现产生无LF ASCII，避免传输NUL/0x1A；编码不落盘、不整片缓存。

声明终点检查原始计数、raw SHA及同FD dev/inode/size/mtime_ns，之后done=true。它没有额外超界探读，所以 `streamReachedDeclaredEnd` 只能说明达到声明长度并验证身份，不能改称额外EOF观察。文件元数据和SHA门也不提供恶意并发改写源的快照保证。

| 当前固定合成源 | 预哈希 | 实际流读/提交 | 摘要含义 |
| --- | --- | --- | --- |
| 原始0..255 | 256B | raw stream256B | raw SHA 40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880 |
| 无LF编码 | 344B | encoded submit344B | encoded SHA ab7727e21f4bbba6508dd72804d97435a78eb44a1e277af1c0f65a8522de382e |

top-level expected/sourcePrehash/submitted对应编码量；rawSource分列raw预哈希/流读计数摘要及实际close，encoding分列编码预期和实际提交。344B编码提交不能替代设备原始256B落盘证明。沿T1 write_all只按原write返回的正短写计入信用，不把一次请求长度当作已写量。

编码块上界32768B，raw块24576B/carry≤2；单次read有限，追踪缓冲和设计256KiB工作预算与媒体长度无关。peakTrackedBuffer只统计被追踪对象，不是总RSS，也不包括Python/ADB基线、OS缓冲和日志。已有小用例不能证明全媒体速度或RSS。

## 3. 精确Job复用与UNKNOWN

薄适配器直接使用原exact_process的Job/_reserve/_run/_validate/_release_if_returned等内部API；本候选通过冻结清单和外seal绑定精确版本，不能宣称适配任意未来版本。预哈希前创建/注册原Job并挂接EncodedSource；打开/预哈希异常时按实际source.close返回决定归还。流式发送使用原writer/stdin实际close、drain、wait及线程门。

源close未正常返回时，即使包装内部rawFD已经关闭，Job.sourceCloseReturned仍false，强owner保留并拒绝下一I/O；不能把实际raw关闭和包装close正常返回混为一谈。原始源对象、进程/管道和Job随原owner保留，不用重复close/GC清零。CLI在原owner仍UNKNOWN时保持原解释器，仅观察实际归还；晚归还不升级已失败attempt。

已有隔离用例正是“底层close完成后包装抛错”：原记录UNKNOWN_RETAINED、sourceCloseReturned=false、rawSource.actualRawCloseReturned=true、保留1且nextIoRefused=true，直到该用例解释器结束。隔离外层进程后来RETURNED只表示外层调用返回，**没有回填内部原Job为RETURNED或以OS退出清除UNKNOWN信用**。本轮复审无实际生产诊断在途。

常规系统调用不构成强制可中断保证；15s及共同2s归还观察不是远端生命周期上限或所有历史远端已清除保证。

## 4. 设备端原返回和独立raw证明

固定T5P仅HA1Q6WXR、com.videokit.app、UID10221、pwd原值。metadata使用shell -n -T -e none；只有producer带编码stdin。固定执行顺序为features完整shell_v2响应→原context/files及新目录不存在→无文件1B探针→一次UID进程快照→一次新私有目录创建→唯一producer→独立raw proof。

1B探针固定printf `AA==` → toybox base64-d → od。通过FD3独立输出printf、decoder、od各原rc；外层另记录pipelineRc和实际FD3关闭rc；所有rc0、完整四条标记、原UID/pwd及hex仅00才准入。它不依赖pipefail、不把NUL放入shell变量，也不把管道末端exit0当作中间解码成功。探针只产生管道内1B，不创建文件；Android实际兼容仍须另派探针确认。

随后UID快照疑似旧接收器即停止不signal，缺行/格式异常也拒绝；未见仍UNKNOWN_NOT_CLEARED。仅允许独占新目录 `files/e4_diag_T5P_TABLET_20261017_once`，umask077/mkdir，无mkdir-p、权限变更或外部路径。准确目标为该目录下payload256.bin；拒绝既有目标/链接，noclobber直接解码到新文件。

producer必须完整原BEGIN、DECODE rc0、END，原UID/pwd/同一正PID/准确目标一致，decoderRc0/statRc0/bytes256。原非零退出时先保存可证明完整stdout里的部分原标记，再拒绝成功门，所以DECODE rc7不会因host输入提交完成而消失。缺END或缺DECODE均不能通过。

最后另条命令验证准确目标普通非symlink、UID10221、非全局可写、stat长度256、前后dev/inode/size/uid/mode/mtime一致，head-c256有界raw SHA必须等于原始源SHA。编码摘要、ASCII机制假设、原exit0、后续观察都不能代替这些条件。本证明是文件字节证明，不是fsync/durability、播放、产品COMMIT或全局资源归还。

## 5. 已有51项有限本机证据

唯一main-001既有结果51/51；输入源码hash和外层check-attempt/result/log绑定最终源码，原检查exit0、60s限时未触发。独立只读审计核验33顶层原记录和1隔离内层记录的完整长度/SHA及相应归还事实，未重跑用例。

覆盖0/1/2/3/256/65535/65536/65537B、全字节、短raw块carry/padding、正短写信用、有限追踪缓冲；0/1/65537B另外经生产pump和真实Python解码子进程核计量。最大自有源65537B，未编码真实媒体。

33顶层原调用构成为：3个生产pump解码进程、1个全部6脚本集中sh-n、2个真实Git shell探针、26个四场景模型调用、1个隔离关闭异常外层进程。另有隔离内部producer1条。顶层owner均实际RETURNED，隔离内部UNKNOWN单独保留，不合并成“34个全部归还”。

真实本机printf/base64/od探针正常通过；中间decoder强制exit7时外层仍exit0，原decoder rc7被独立标记并拒绝。探针UID/pwd由本机函数模拟，不能据此推断Android身份或工具兼容。

| 本机模型 | 原目标实际B | 首因/结果 | 控制流 |
| --- | ---: | --- | --- |
| normal | 256，原始SHA正确 | 合成路线模型通过 | metadata6、producer1、独立proof完成 |
| decoder-nonzero | 0 | 原成功响应门拒绝，保留DECODE rc7 | metadata5、producer1，proof未运行 |
| short-exit0 | 26 | RECEIVER_CONTEXT_OR_COUNT | metadata5、producer1，END计数拒绝、proof未运行 |
| wrong-sha | 256，摘要错误 | INDEPENDENT_PROOF | metadata6、producer1，独立摘要拒绝 |

模型用Python标准解码/xb写入自有小文件，所以可核实际字节和生产控制流；Android权限/UID/mode/ps/命令输出由固定模型提供，不是设备shell执行或SELinux证明。四场景旧自有26B占位不变、失败产物保留、同attempt拒复用；不能将此占位与设备历史26B残件混为一谈。51项并非所有未知异常的穷举覆盖。

## 6. 固定诊断预算及未来媒体边界

T5P metadata计划6/硬20、producer1，每命令及producer15s、共同归还观察2s，日志1MiB、每原记录64KiB；stdout/stderr各16KiB/各保留4KiB，响应超保留前缀拒绝完整性。CREATE_NEW attempt在变更前消费，固定源raw预哈希/流读各≤256B、encoded预哈希344B/提交≤344B；前置探针ASCII4B→管道1B，新目标预期256B、独立raw hash≤256B。失败保留产物，不补传/换路/加时/自动清理。

未来媒体只有设计，没有可运行媒体CLI、没有重新stat/read/hash真实源，没有授权执行：

| 旧元数据源 | raw B | 无LF wire B | host raw两遍 B | transfer/hash时限提案 |
| --- | ---: | ---: | ---: | --- |
| basic.mp4（sample.mp4） | 349102 | 465472 | 698204 | 60s / 15s |
| subtitle.avi | 736454656 | 981939544 | 1472909312 | 600s / 120s |

按4×ceil(N/3)，总wire982405016B，编码两遍生成1964810032B但不落盘，host raw两遍1473607516B，独立设备raw hash总cap736803758B；AVI编码量在原pump1GiB界内。600s仅编码有效速率下界约1.56075MiB/s，尚未包含raw预哈希和协议开销，不是实测承诺。预哈希计入总transfer时限，无自动加时。

媒体receiver/proof需按新批次实例化准确目标、长度和hash界；当前入口固定256B。先MP4、报告审查后另派AVI；临时件到产品fixture的无覆盖发布及正常产品方法也须另批审查。任何传输成功不升级为播放通过。

本轮tester ADB0、设备运行0、fake/probe重跑0、真实媒体stat/read/hash0、Gradle0，未改冻结源码或旧现场；无在途工作。完成后主动通知负责人并保存回执，实机T5P须另行正式派发。
