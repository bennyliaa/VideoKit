# D1 E4A-T2 有限设备诊断提案 V1.0

2026-10-17。**本文件是待审提案，设备执行尚未授权或运行。** 负责人审查后另派 tester；coder 不自行派发。批次 D1-E4A-T2P-TABLET-20261017。

## 固定范围

仅平板 HA1Q6WXR，com.videokit.app，原 UID 10221，原 pwd /data/user/0/com.videokit.app，沿用 T1P 已观察的 pwd 接口，不改猜测为另一规范路径。新目录 files/e4_diag_T2P_TABLET_20261017_once，唯一目标 payload256.bin，nonce E4T2P_TABLET_20261017_ONCE。目录或目标已经存在/为符号链接即停止，不删除、不换名字再试。

唯一输入为随包 payload256.bin，恰为 bytes(range(256))：256B，SHA256 40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880。主机预哈希与流式读取各 256B；独立设备 SHA 只读新诊断文件 256B。无 --source 参数，不接受 MP4/AVI。一次 attempt 在首次远端变更前记录为已消耗；失败也不得重试。

计划 6 个 metadata 客户端命令，加 1 个接收命令。硬上限 metadata 20、producer 1、日志合计 1MiB；每命令及接收各 15s，后续本机归还观察 2s；stdout/stderr 各计数上限 16KiB、各保留前缀 4KiB。达到限额立即停止。15s 是主机命令等待边界，不是远端全部资源按时归还的承诺。

## 执行顺序与通过条件

1. 读取该平板 features，必须有 shell_v2。固定 shell -T -e none，关闭 PTY/转义处理，不改走 legacy 通道。
2. 原 run-as sh -c 输出实际 id -u 与 pwd，再验证 UID、目录及 files 非符号链接。失败保留真实输出并停止，不替换期望值重新运行。
3. 仅一次指定 UID 的进程快照，保留当前 shell PID 与 PID/PPID/UID/ARGS。可见其他 cat/tee/sh/mksh 或旧 T1P 接收线索即停止，不 kill。未见匹配仍记 UNKNOWN_NOT_CLEARED；不能推断全部旧资源已归还。[上游 ps UID 选择实现](https://android.googlesource.com/platform/external/toybox/+/08dc20a/toys/posix/ps.c) 只支持该可得观察的解释，不代表检查了设备 OEM 实现。
4. 仅对以下三个准确历史路径做无 -L 的 stat，保留原 rc/输出。默认 lstat 依据 [上游 stat 实现](https://github.com/landley/toybox/blob/master/toys/other/stat.c)，未检查 OEM 源码；失败不能推为 ABSENT。无 test -e 跟随探针、内容读取、SHA、递归、通配或媒体修改。
5. 独占创建上述新诊断目录，umask 077；收到对应 DIRECTORY 标记。
6. 唯一接收原始 256B。原接收命令在任何写入前输出 BEGIN 的实际 UID/PID/pwd/准确目标路径；验证角色后以 noclobber cat 写入。stat 数量必须 256，再由同一 PID 输出 END。主机要求两行完整标记及原进程/源/管道实际归还，不用 submittedBytes 代替接收计数。
7. 独立新命令重新验证 UID/pwd、目标普通文件与非符号链接、stat=256、SHA 一致，输出 PROOF。只有三份标记全部一致才记合成诊断通过；不发布为 fixture、不准入真实媒体或产品方法。

第三步未见旧接收只能支持独立新目录的有限诊断观察。旧远端 ownership 全程维持 UNKNOWN；tester 应在报告中保留该边界，不添加“旧任务全部结束”的结论。

允许历史 lstat 的完整路径仅为：

```text
files/e4_fixtures/basic.mp4
files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep
files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part
```

81407B 残件在 T1P 已归档至第二个路径，不恢复、不再次改名。保留旧 temp、媒体、失败诊断目录及目标原状。不扫描 app/设备目录，不查询手机，不安装、不读写 budget/pending 标记、不跑 Binder/产品方法、Gradle 或真实媒体检查。

## 直接入口与证据

默认只打印计划，不打开输入文件或执行 adb：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at2/tools/diagnose_once.py'
```

仅在负责人另批正式派发后，tester 使用以下固定命令一次；批次标志只是误用防护，不构成授权凭据。evidence-dir 必须是新的绝对目录，且在冻结工具目录外。不得改冻结 JSON 或源码重跑。

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at2/tools/diagnose_once.py' --execute --formal-batch D1-E4A-T2P-TABLET-20261017 --evidence-dir 'D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T2P_EVIDENCE'
```

工具内固定 adb 路径 D:/Android/SDK/platform-tools/adb.exe。若环境、现有角色、功能或语法不满足，报告失败并停，不搜索另一设备或更换路线。

保存 attempt.json、每条原客户端 argv/退出/管道/源归还事实和有界输出、result.json。hostSubmittedBytesSnapshot 与 syntheticPayloadBudgetBytes 分列；receiverExecution 只有获得 BEGIN/END 后才升级。任何超时/缺标记/非零返回/独立校验失败均 NOT_ADMITTED，已有产物留在原处，无自动重跑。若保留本机 UNKNOWN owner，原解释器继续持有对象，仅观察原事实，不退出冒充回收，不启动下一 I/O；通知负责人处理。

冻结包的只读核验方式（外部 seal SHA 从集中交付消息取得）：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at2/tools/package_tools.py' verify --expected-freeze <外部seal-SHA256>
```

本机诊断模型通过不代表设备通过。该批不改变 D1 NOT_PASSED、M0 NOT_STARTED、P0 和历史 FAIL；实际媒体恢复需负责人根据诊断证据另行决策。
