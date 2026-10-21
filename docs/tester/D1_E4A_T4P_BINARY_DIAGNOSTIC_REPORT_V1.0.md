# D1 E4A-T4P 标准二进制诊断报告 V1.0

执行日期：2026-10-17，约 10:25；测试人：tester。唯一正式批次 `D1-E4A-T4P-TABLET-20261017`，nonce `E4T4P_TABLET_20261017_ONCE`，指定设备 `HA1Q6WXR`。

结论：**NOT_ADMITTED / 本轮诊断未通过准入，传输路线 NOT_RUN**。features 通过；第二条 shell 既有外部 base 准入命令原始 exit=1、stdout/stderr 均 0B，按冻结方案立即停止。具体失败谓词 **UNKNOWN**，不能仅凭这个结果断言目录不存在、权限不足、SELinux 拒绝或工具不兼容。无新产品缺陷结论；设备二进制路线尚未验证。

## 1. 授权与冻结身份

依据 `docs/milestones/D1_E4A_T4P_TESTER_REQUIREMENTS_V1.0.md`，只执行已审 `docs/coder/d1e4at4/tools/diagnose_binary_once.py` 固定 CLI 一次，参数 `--execute --formal-batch D1-E4A-T4P-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T4P_EVIDENCE`。新证据目录在执行前不存在；未改冻结文件。

执行前只读 verifier 核验 PASS：72 源文件 / 74 不可变文件；seal `8eb3b4d82adaaba225eb22ee0afe90d551f9735a7518d1b34a7355927e4b2e67`；ZIP 113618B，SHA256 `a5a3b34daad71a86d7d5a993deb9c56e83895c662b9c9362b25268573676d0af`。准确导入路径和 T1 原始所有权保留机制沿已审冻结包。执行使用主机权限提升以连接既有 ADB 服务，设备端没有 root 或权限修改。

负责人已接受自有合作式 256B 范围内标准 push 缺少原子 no-replace 的边界；本次尚未走到新目录或 push，不据此作任何原子性或产品安全推论。

## 2. 全部实际原调用与停止点

| 次序 | 原调用/证据 | 原 exit | stdout / stderr | elapsed | 本机所有权 | 结果 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `adb -s HA1Q6WXR features`，`00-features.json` | 0 | 220B / 0B | 0.062s | RETURNED | 完整响应精确含 shell_v2，通过 |
| 2 | `adb -s HA1Q6WXR shell -n -T -e none sh -c <冻结 shell base 脚本>`，`01-shell-existing-base.json` | 1 | 0B / 0B | 0.125s | RETURNED | PROCESS_NONZERO_EXIT，立即停止 |

第二条脚本原 argv 完整保存在原 JSON。其顺序为 `set -eu`，检查 shell UID=2000；准确 base `/storage/emulated/0/Android/data/com.videokit.app/files` 为目录、非 symlink、rwx；新 stage 不存在；base stat；`head -c 0 /dev/null` 与 SHA 工具探针；`set -C`；最后输出准确 marker。原响应没有 marker，也没有中间检查输出，因此不能定位最先失败的检查，更不能把 UID2000、base 角色、权限、stat 或工具支持记为已验证。

冻结上层首因 `ORIGINAL_RESPONSE_NOT_SUCCESSFULLY_RETURNED` 表示完整成功响应门拒绝；**不表示本机进程仍在运行**。原客户端 exit=1 已实际观察到，所有本机原 owner 已归还。主 CLI 正常结束 exit=1，没有重跑、补查或更换路线。

features 原 stdout SHA256 `05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce`，完整 CRLF 字节和首条 shell_v2 均由原记录保留。shell base stdout/stderr 为空，SHA 均为标准空 SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

## 3. 未执行阶段与证明

app UID10221/pwd 双视图 base 检查、UID 进程快照、固定合成源预哈希、独占 stage 创建、app/shell stage 访问门、标准 push、独立 stage proof、本地 copy、独立 internal proof 全部 **NOT_RUN**。

`stageProof=null`、`copyProof=null`、`internalProof=null`。没有本轮源/目标 stat、长度、摘要或 BEGIN/END 证明。固定目标仍仅为计划：stage `/storage/emulated/0/Android/data/com.videokit.app/files/e4_stage_T4P_TABLET_20261017_once/payload256.bin`；internal `files/e4_diag_T4P_TABLET_20261017_once/payload256.bin`。本轮没有创建这些目录或文件；也没有额外访问来证明它们当前不存在。attempt.json 已按方案消费本轮执行机会，不能据未发生远端变更而自动复用或重试。

## 4. 预算、归还与范围

| 项目 | 实际 | 冻结上限/说明 |
| --- | --- | --- |
| metadata | 2 | 计划9，硬上限20 |
| push / copy | 0 / 0 | 各1 |
| payload stdin | 0B | 必须0B；两次命令 submittedBytes 均0 |
| 主机合成源预哈希 | 0B | 正常256B，硬257B；未到此阶段 |
| ADB 合成源读取 | 未调用 push | 不伪造实际内部读取计数 |
| stage hash / copy / internal hash | 0B / 0B / 0B | 各≤256B |
| 新增远端文件 | 0 | 未执行任何 mkdir/push/copy |
| 单调用时限 | 0.062s / 0.125s | 各15s；本机归还观察2s |
| 单原记录 | 1828B / 2497B | 各≤65536B |
| 原始 attempt + 两记录 + result | 5530B | <1MiB；后续 tester 审计/报告另计 |
| 单流输出 | 最大220B | 流硬16KiB，保留前缀4KiB；均完整未截断 |
| 保留本机 owner / 在途 | 0 / 无 | 原实际返回成立 |

两条记录均证明原退出已观察、flush/实际 stdin close/source close/writer 返回、stdout/stderr close 返回，无 creationUnknown、无 stdin close error，无强制终止 owned child。第二条的 errors 只有 PROCESS_NONZERO_EXIT。本机归还不代表清除了历史远端资源；`priorRemoteOwnership=UNKNOWN_NOT_CLEARED`，本轮未执行 UID 快照或信号。

未访问旧26B残件、旧81407B或任何历史媒体/临时文件；真实媒体读取0，手机/模拟器0，安装0，Gradle0，Binder/预算/产品调用0，设备信号0，权限/manifest修改0，上层目录补建0，清理/重试/改路0。已有 CRT TEXT26/BINARY256 仅保留原本机结论，设备截断层与已装 SDK 源码映射仍 UNKNOWN。

## 5. 证据与后续

证据目录 `docs/tester/D1_E4A_T4P_EVIDENCE`：attempt.json、00-features.json、01-shell-existing-base.json、result.json。tester 的 audit.py 只读现有本机回执，receipt-audit.json 核验完整字节长度/SHA、实际归还及计数 PASS；没有再次调用 ADB。

原记录文件 SHA256：features `72a8eaef8ed474a381f354835aaca689a50860db4cd9ee3f737ba3aa8f744c3b`；shell base `e8b24b683f67ca6f280764563bfbbf285254fb5a27331899c5d3670199d283ff`。

已停止，后续定位须负责人另行限定范围正式派发。本报告不请求现场补建 base、改权限或重试，也不授权恢复媒体。**D1 NOT_PASSED、M0 NOT_STARTED、P0及历史 FAIL 保持；无在途工作。** 完成后主动发送负责人，并保存发送回执。
