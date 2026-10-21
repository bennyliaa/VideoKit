# D1 E4A-T1 原 stdin 关闭证明独立复审报告 V1.0

日期：2026-10-17 08:53。依据 D1_E4A_T1_TESTER_REQUIREMENTS_V1.0.md。

**结论：SUPPORTED_FOR_SEPARATE_CONDITIONED_PRELOAD。E4AT-F01 在静态生产路径及已有六组有限本机证据范围内获得修复支持，未发现新的阻止单独有限预置交接的问题。当前实际预置仍 NOT_RUN，须负责人另行正式派发；不能从本机结果推导真实 ADB 传输已修好。PREP-01 截断层次保持 UNKNOWN。D1 未通过，M0 未启动，原 P0/历史 FAIL 保持。**

## 1. 冻结及范围

| 项目 | 核验 |
|---|---|
| 候选 | D1-20261017-E4A-T1 |
| 外 seal SHA-256 | 954288092916e5281c7a50183adc9041e82c05d16cfe6fd6cd5013fb75139c0f |
| ZIP SHA-256 | 0ed267e6665b481c0858492413b56a6b0ac79c257765e063ba37ee2521cf08bb |
| 已检查的只读 verifier | PASS，41 源/43 不可变，ZIP 精确成员与内容一致；物理 936,255 B/50 文件，逻辑归档 439,708 B |
| tester 独立哈希/记录审计 | PASS；D1_E4A_T1_EVIDENCE/audit.py、identity-and-cases-audit.json |
| 历史保持 | 实际旧 T seal、E4A seal及旧 T 审查报告完整哈希未变；fixture_transfer.py、fake_child.py 与旧 T 字节相同 |

本轮仅静态阅读、归档及已有本机记录审查。未导入生产工具进行故障执行；fake 重跑、ADB、设备、真实媒体 stat/读取/hash/复制、Gradle 和预置均为零。无在途执行。

## 2. E4AT-F01 修复判断

生产 `exact_process.py` 的 `Job.ownership_returned` 对实际分配 stdin 明确要求 stdin_closed，同时保留原 process wait、source/writer、两个 drain 关闭及全部原线程结束条件。原 writer 只对保存的同一个 job.stdin 做一次 close；仅正常返回置 stdin_closed，异常对象保留在 stdin_close_error。原 Job 由 _OWNERS 强持，继续可达 process、原 stdin/raw pipe、source、argv 及异常。

close 抛错或仍在调用内时，原进程 exit0、raw.closed 属性、source 返回及其他线程结束都不能替代原 stdin close 返回；collect 和 transfer_file 的 _reserve 在新进程启动/源预检之前拒绝。没有以二次 close、强制 GC 或换对象取得归还证明。

`_prune_proven_returns_locked`、retained_owners 与后续明确请求只观察原字段和 thread.is_alive；不执行 IO/close，不修改原证明字段，不重置计时。原 close 若迟后正常返回、原 source/drain/wait/线程也全部返回，才可移除已证归还的本机占用。原超时 record 仍 NOT_ADMITTED，不会恢复原传输、hash 或发布流程；实际批次仍须失败即停止。

启动前绝对路径/普通非 symlink 文件检查的拒绝确实发生在 Popen 之前；这时 process/stdin 未分配，不能虚构 close 成功，但已有 source 仍需实际关闭。已返回 process 的 stdin 若实际未分配，记录 Allocated/Attempted/Returned 均 false，其他资源返回后可解除占用，而缺请求输入仍使本次 NOT_ADMITTED。

已进入不透明 Popen 构造但未取得正常返回时，creation_unknown 和原 startup_error 保留，归还谓词拒绝；没有从异常或空 process 推断“肯定零分配”。**该保守启动异常分支获得静态支持，但六组现有记录未单独执行不透明构造抛错；不能把 no_process 的启动前拒绝写成已经覆盖此异常。**

## 3. 已有生产路径证据

一个 MAIN、零 repair，共 63 条新断言。六个独立 case 解释器、7 个真实自有 fake 子进程；旧 T 72 条未重跑、未叠加。五项生产/检查输入与原日志及 JSON 均绑定冻结。close_case 仅在原 Popen 返回后对实际 stdin 置受控 close 代理，其他路径仍经过生产 collect/transfer_file→_run→writer finally→原归还谓词及全局准入；没有复制谓词或直接改证明字段。

| case | 断言 | 证据解释 |
|---|---:|---|
| success_transfer | 4 | 256 B 实际二进制传输及同字节文件，已分配 stdin close 正常返回，实际资源归还 |
| no_process | 4 | 缺失 exe 在 allocator 前拒绝，未分配 process/stdin；source 实际关闭后允许一个独立后续请求 |
| no_stdin | 5 | 适配器明确用 DEVNULL，没有 parent stdin，不调用或伪造 close；其余资源归还，本次仍不准入 |
| throw_before | 15 | 原 exit0、source/其他 pipe/全部线程均结束，原 close 抛错，UNKNOWN；双入口拒绝、close 恰一次、原 owner 可达；case 退出前仍 1 |
| throw_after | 16 | raw 已 closed 后 close 仍抛错，不借属性或 exit0 减账；case 退出前仍 UNKNOWN owner 1 |
| blocked_return | 19 | 原 close 在屏障内、process/drain 已返回，仍 UNKNOWN 并拒绝下一请求；放行同一次 close、join 原线程后只观察归还，原超时仍不准入；之后仅独立 metadata 请求可接纳 |

两个抛错 case 的解释器最终退出只说明本机测试执行已结束，**不算两个原 owner 协议归还**，不得把各自的 1 合并写成全局 0。原错误/超时结果与迟后同原 Job 的观察分别保留；没有清 registry 或强制 GC。真实预置时不能仿照隔离 case 退出解释器洗 UNKNOWN，应保持原解释器与原 owner 并交负责人。

## 4. 原传输与计划回归

fixture_transfer.py 字节未变，原静态结论继续适用：二进制 pump 同 FD prehash/stream、短写实际累计、并发有界输出；exit0 仅 PROCESS_IO_COMPLETE_ONLY，仍需独立临时及最终 stat/SHA。残件先核 81,407 B/原摘要，无覆盖归档并再核原字节；临时 noclobber、固定唯一 attempt、同目录 mv -n 后独立证明，失败保留不补传/续传/删除/回滚。整体 run-as 脚本引用、metadata-only 碰撞、内容 hash 前长度界和安装多行提示解析未弱化。

T1 计划只调整新批次、两个临时名/attempt 及关闭证明规则；executionAuthorized=false。拟定目标仅 HA1Q6WXR，先 MP4，完全准入后才首次预置 AVI。原残件归档名及字节保持；不重建/安装产品，不查手机/模拟器，不重跑 Binder，不动预算 anchor/marker、历史 cache/输出或旧 fixture，也不接着执行媒体/取消/故障方法。

| 全成功计划量（不是实际流量） | B |
|---|---:|
| payload | 736,803,758 |
| host prehash + 同 FD 传输读取 | 1,473,607,516 |
| 新临时/最终件 hash | 1,473,607,516 |
| 残件前后 hash | 162,814 |
| 设备内容 hash 合计 | 1,473,770,330 |
| 新件 + 保留残件 | 736,885,165 |

AVI 首次 736,454,656 B 仍完整计入。MP4 60 秒、AVI 300 秒、每 metadata/hash 命令最多 120 秒、共同 cleanup 2 秒及包外证据 8 MiB 总量门保持。以上算术/限额可供正式交接使用，不代表当前空间、吞吐或 Android toybox 兼容性已确认。

## 5. 另派实际预置的条件

1. 负责人另行绑定本冻结、平板、准确源/目标、T1 两个唯一 attempt 及次数。tester 在新包外证据目录运行，验证实际导入 T1 exact_process.py，避免误用旧 T。
2. 必要一次只读现场准入确认包/签名、enabled、空间、run-as id/pwd、父目录 UID/非 symlink，以及 toybox 命令支持；失败或未知即停。余量须覆盖旧缓存/安装包/其他 fixture，不删文件凑空间。
3. 保留原残件与所有临时/归档结果，独立核字节后才准入；MP4 任何失败阻断 AVI。UNKNOWN 时保留原工具解释器/Job，不换路线或进程重试，不自动续期、放宽上限或下一批。
4. 每进程原 argv/退出、实际 writer/close/drain/wait、源读取量、独立文件证明及累计日志原样落盘。主机进程/pipe 归还不等于远端 adb 接收 owner 归还；远端未证实保持未知，不宣称超时就是远端终止。

source open/prehash 或普通 OS 调用无硬可中断保证；先 stat 后 sha 的字节界依赖合作式稳定普通文件，并不抵御恶意并发增长。真实二进制流、Windows/ADB/Android 路径、设备文件和兼容性仍待下一批首次有限实证。本报告只解除原工具 F01 的静态阻断，不是执行授权或产品验收。

旧 E4A-N PASS1/BLOCKED9、PREP-01 UNKNOWN、81407 B 设备残件与全部旧备份/报告保持；D1 未通过，M0 未启动，P0/历史信号 FAIL/C14 待测不变。
