# D1 E4A-T3P 有限诊断提案 V1.0

2026-10-17。**待负责人审查另派，当前 executionAuthorized=false，未执行设备诊断。** 批次 D1-E4A-T3P-TABLET-20261017。旧 T2P attempt 已消费（metadata1/producer0/无新诊断文件），不复用。

## 唯一新范围

平板 HA1Q6WXR，com.videokit.app，期望原 UID10221、pwd /data/user/0/com.videokit.app。新目录 files/e4_diag_T3P_TABLET_20261017_once，目标 files/e4_diag_T3P_TABLET_20261017_once/payload256.bin，nonce E4T3P_TABLET_20261017_ONCE。协议标记前缀 E4T2_CONTEXT/BEGIN/END/PROOF 为沿用的协议名；新身份由上述 nonce、批次和新目录区分。

输入仅冻结包 payload256.bin，256B，全字节0..255，SHA256 40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880。无 --source 或媒体选项。计划6条 metadata+1接收，metadata硬上限20、producer硬上限1、日志1MiB、每命令及接收15s、本机归还观察2s，stdout/stderr各计数16KiB、各保留4KiB。主机预哈希/流式读取各256B，独立新文件哈希256B；预算不是实际落盘量。

## 顺序与拒绝

1. features 原命令成功、资源实际归还且 stdout/stderr 完整长度/SHA一致。按 CRLF/LF/逗号的明确规则解析，精确要求 shell_v2；缺失、类似token、错误编码或不完整原响应停止。固定 shell -T -e none，无 legacy fallback。
2. 原 run-as 输出实际 id -u/pwd，再核对期望与 files 非符号链接；不猜另一 UID/目录或修改期望重跑。
3. 一次指定 UID 的 ps 快照，保留原列/当前 PID。可见旧接收或其他 cat/tee/sh/mksh 线索即停止，不 kill。未见仍 UNKNOWN_NOT_CLEARED，不能认定全部旧资源归还；设备 OEM 格式尚未实测。
4. 对下列三个准确历史路径仅做不带 -L 的 stat，保留原 rc/输出，不读内容或哈希、不推断错误等于 ABSENT、不递归扫描。
5. 新目录独占创建、umask077；已存在或符号链接即停止，不换名重试。
6. 唯一接收：原 BEGIN 先输出实际 UID/PID/pwd/准确相对路径；验证后 noclobber cat 接收，原 stat计数须256，同一PID输出 END。必须完整原返回和匹配标记；主机 submitted 快照单独记录。
7. 另一独立命令核对原 UID/pwd、准确目标普通文件且非符号链接、stat256与SHA，取得 PROOF。齐全才记合成诊断通过，不准入真实媒体或产品方法。

唯一历史路径：

```text
files/e4_fixtures/basic.mp4
files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep
files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part
```

旧81407B已归档第二路径，不恢复、不改名、不覆盖、不删除。所有诊断失败保留新目录/目标及本机记录，无补跑、换路或清理。实际15s超时不证明远端归还；T1实际close强owner保持，未知本机对象继续由原解释器持有，仅观察原事实，不启动新I/O。晚归还不会升级旧失败尝试。

## 入口与证据

默认计划预览（不打开payload、不执行adb）：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at3/tools/diagnose_once.py'
```

负责人另批正式派发后，tester仅一次执行以下准确入口。固定批次只是误用防护，不是授权凭据。新证据目录必须不存在且位于冻结工具目录外；不能改源码/JSON或重用T2P入口。

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at3/tools/diagnose_once.py' --execute --formal-batch D1-E4A-T3P-TABLET-20261017 --evidence-dir 'D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T3P_EVIDENCE'
```

固定 adb 路径 D:/Android/SDK/platform-tools/adb.exe；环境或命令格式不满足即报告原事实并停止。保留 attempt.json、每条原命令有界收据及 result.json；hostSubmittedBytesSnapshot 与 syntheticPayloadBudgetBytes 分列，原收据仍有长度/SHA和实际资源返回状态。无手机、安装、Gradle、媒体补传、产品方法、Binder、预算/pending标记、递归扫描或额外现场清理。

执行前用集中消息中的外部 seal SHA 只读核验：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at3/tools/package_tools.py' verify --expected-freeze <外部seal-SHA256>
```

新features解析通过不等于后续设备步骤通过；其余格式仅有离线合成合同检查。D1未通过、M0未启动、P0/历史FAIL及原设备未知保持，媒体恢复由负责人根据实际报告统一决定。
