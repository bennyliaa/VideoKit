# D1 E4A-T2P 唯一合成诊断报告 V1.0

日期：2026-10-17 09:24。批次 D1-E4A-T2P-TABLET-20261017。依据 D1_E4A_T2P_TESTER_REQUIREMENTS_V1.0.md。

**结论：NOT_ADMITTED，发现工具解析缺陷 E4AT2P-F01（P2）。原 features 命令成功，实际输出含 shell_v2，但以 CRLF 换行分隔；工具仅按逗号拆分，错误停止于 SHELL_V2_REQUIRED_NO_FALLBACK。这不是设备缺失 shell_v2 的证据，也不是 codec 产品失败。唯一入口已消耗，不修改后重跑；256B producer 未启动。**

## 1. 唯一执行与冻结

执行前只读验证外 seal `ce571e95cd294a46b2f852e2d07c7f91126d2b388eb6b27ddcc589e91010b09a`、ZIP `9d4d2f6a65b93876fedf6df0257704beecb73cfc6d81928e349ed9a32237ac54`，295源/297不可变文件及精确归档身份 PASS。未修改冻结源码或JSON。新 Python 进程直接以已审脚本所在 tools 目录解析其同目录模块，执行准确入口：

`diagnose_once.py --execute --formal-batch D1-E4A-T2P-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T2P_EVIDENCE`

09:22:42 创建新包外目录及 CREATE_NEW attempt，固定期望 HA1Q6WXR/UID10221/pwd原值。只发起一次 `adb -s HA1Q6WXR features`；未查询或操作手机、模拟器及其他设备。入口进程最终退出1，原唯一ADB客户端退出0且正常归还。

## 2. 原始结果与缺陷

原命令 stdout **220 B**，SHA `05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce`；完整前缀未截留，stderr0 B。首部实际为：

```text
shell_v2
cmd
stat_v2
ls_v2
```

原字节为CRLF换行，输出没有逗号；完整清单见 `D1_E4A_T2P_EVIDENCE/features-original-stdout.txt`。该文件从保存的原prefixHex逐字节还原，并按原总量与摘要复核，不是再次查询设备。

缺陷位置 `docs/coder/d1e4at2/tools/diagnose_once.py:52–53`：`.decode('ascii').strip().split(',')` 对本次合法逐行清单形成一个包含全部多行的元素，后续精确成员比较找不到 shell_v2。因而结果写入 SHELL_V2_REQUIRED_NO_FALLBACK，尽管原清单第一项就是 shell_v2。此次仅解析已有原返回即可直接确认，不需重跑或推断。

T2本机fake features输出为逗号分隔 `cmd,shell_v2`，未覆盖本次真实CLI逐行格式。此前静态复审未识别这一兼容性缺口；本次真实证据优先，不能继续沿用“无静态阻断”作为设备准入。本批不改旧报告/冻结哈希，新增本报告反馈集中修复。

建议对已完成原features响应按明确支持的分隔规则（CRLF/LF及逗号）产生精确token集合，仍保持原exit/完整输出/协议门与无fallback规则；不能改为子串包含而误接纳 shell_v20、noshell_v2。以本次220B原输出为回归输入，补正常/缺失/相似token的有限纯解析证据后新冻结交审；这些工作不是本批再次设备执行许可。

## 3. 已执行与未执行

| 环节 | 状态与实证 |
|---|---|
| features原命令 | PASS：exit0、完整220B stdout、stderr0、含shell_v2 |
| features工具解析 | FAIL：仅逗号分割造成假阴性 |
| UID/pwd、files角色确认 | NOT_RUN，第一步已停；不从旧记录推定本次现场值成立 |
| UID进程快照/旧receiver线索 | NOT_RUN，未kill或清理 |
| 三历史准确路径no-L stat | NOT_RUN，无额外历史路径访问 |
| 新诊断目录/目标 | 未创建、未写入 |
| 256B producer | 0次；源未open/hash/stream，submitted快照0 |
| BEGIN/END、独立stat/SHA | NOT_RUN，无原接收执行或落盘证明 |
| 总诊断结果 | NOT_ADMITTED；receiverExecution=NO_COMPLETE_RECEIVER_PROOF |

attempt已按合同记录CONSUMED_BEFORE_REMOTE_MUTATION。即使producer次数为0，也不自行重用入口、证据目录或临时名补跑。没有自动回退通道、修改期望UID/pwd、补媒体、增加命令或时限。

## 4. 实际预算与所有权

实际metadata1/上限20，producer0/上限1；合成源prehash/stream读取0 B、payload提交0 B、独立设备诊断hash0 B、真实媒体内容0 B。原220B stdout低于16KiB门与4KiB前缀，不发生截留；所有包外证据低于1MiB，实际总量见review-summary.json。没有使用后续计划的6metadata+1producer全量，也不能把预算256B记作实际写入。

唯一原客户端耗时0.094秒，未超15秒/共同2秒收尾，没有terminate/kill。原stdin实际关闭、source关闭、writer返回、stdout/stderr关闭及原process wait均已证返回；ownership=RETURNED、retainedLocalOwners=0，原解释器正常结束，无本机保留handle或在途Job。入口exit1是诊断拒绝，不是未知owner退出洗许可。

旧远端ownership继续UNKNOWN_NOT_CLEARED；本次根本未执行进程快照或历史lstat，不能声称旧receiver已归还、原设备文件存在性已复核或旧失败根因已清除。没有新诊断产物需要清理，旧残件归档与全部旧现场保持。

## 5. 交接

原attempt.json、00-features.json、result.json均保留；audit.py仅解析原收据，生成audit-summary及evidence-manifest，不触发设备/媒体访问。报告完成主动交负责人，建议先集中修复 E4AT2P-F01，再完整新冻结审查并另派精确批次。

本批不执行安装、Gradle、Binder、预算标记、MP4/AVI或产品正常/取消/故障；不重跑、不换路、不加时、不自动下一批。D1未通过、M0未启动，旧PREP-01/T1P未知、E4A-N PASS1/BLOCKED9、P0/历史FAIL/C14待测保持。
