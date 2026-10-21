# D1 E4A-T3 开发交付 V1.0

2026-10-17。候选 D1-20261017-E4A-T3。修复 T2P 实证 E4AT2P-F01/P2；本机离线检查完成，设备诊断 NOT_RUN，待负责人集中审查另派。路径相对 D:\CodexProjects\VideoKit。

## 问题与修改

T2P 唯一 features 原命令正常退出并完整返回 220B，SHA256 05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce。原清单使用 CRLF，第一项 shell_v2。旧代码仅按逗号拆分，形成包含整段清单的一个元素，造成假拒绝。这是工具格式兼容缺陷，不能记作设备不支持 shell_v2，也不是产品 codec 失败。

新目录 docs/coder/d1e4at3 保留完整工具及引用，新 command_response.py 直接用于生产 diagnose_once.py。features 支持 CRLF、LF、逗号及其混合分隔，精确比较 shell_v2；不以子串包含判定。可接受连续分隔及结尾分隔；不接受空响应、前导分隔、空格、单独 CR、控制字符、非 ASCII 或 BOM。token 限定 ASCII 字母/数字/下划线；未来出现其他 token 格式会明确拒绝，不猜测放宽。

所有命令响应在解析前统一确认原 PROCESS_IO_COMPLETE_ONLY、ownership RETURNED、原 exit0/已观察、无原错误、实际 flush/stdin close/source close/writer 归还；stdout/stderr 均需 drain close、无 drain 错误、前缀未截留，并对完整原字节复核总长度与 SHA。stderr 必须为完整空响应。保留原收据，不将解码后文本的摘要替换原字节摘要。此门只核验已返回结果，不主动关闭、重试或推定远端资源归还。

exact_process.py 与 T1/T2 字节一致：13077B，SHA256 f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d。实际 close 强 owner、一次 attempt、原资源归还及迟到返回不升级旧 attempt 规则不变。旧目录、报告、产品及残件均未修改。

## 集中格式检查

| 剩余命令 | 解析检查与限制 |
| --- | --- |
| features | 真实原220B离线回归通过；兼容三类明确分隔，无 fallback |
| context / DIRECTORY | 自有 printf 标记，strip 后按固定字段解析；合成 CRLF 合同通过，设备本次未运行 |
| UID ps | 按 splitlines 和最多四个空白列拆分，不使用逗号；原 PID/UID 检查和旧接收线索停止规则不变。OEM 列/语法兼容性未证，不预判通过 |
| 三历史 lstat | 原 rc/输出作为事实保留，不把错误或空输出解释为不存在；不依赖逗号拆分，无内容读取 |
| 原接收 BEGIN/END | splitlines，精确 nonce/UID/pwd/path/PID/256 计数；合成 CRLF 合同通过，设备未证 |
| 独立 stat/SHA PROOF | 自有固定字段，独立命令同 UID/pwd/准确路径/256B/SHA；合成 CRLF 合同通过，设备未证 |

除新批次目录/nonce 及 LF→CRLF 文本换行转换外，remote_command.py 与 T2 内容一致，由封存核验器比较原完整 ZIP 中的源码；没有基于未观察的设备输出改写命令或放宽门。T2P 在第一步停止，因此不能声称 UID/pwd、ps、stat、接收端或 SHA 的设备兼容性已验证。

## 有限验证证据

main-001 一次离线批次，**67 项断言 PASS**，无修复补跑。直接导入生产解析器及 run_diagnostic；未启动假子进程，未重复历史 43/63/72 项。入口 evidence/local-check-results.json 绑定最终五个被测源码与真实输入；evidence/attempt-main-001.json、attempt-result.json、checks.log 保留原尝试与日志。检查脚本不能覆盖既有尝试或冻结结果。

检查包含原220B长度/摘要/原收据一致、旧假拒离线复现、LF/逗号/混合/单项/重复项成功，以及缺失、shell_v20、noshell_v2、shell_v2_extra、大小写、无效编码、BOM、控制字符、截留、长度/SHA错误、异常退出、stderr和实际资源未归还的拒绝。7个内存 transport 场景只检查生产 features 准入或停止；另1个内存场景集中检查其余自有标记的 CRLF 合同。

内存场景的“命令调用”只是返回合成收据，没有执行 adb、shell、设备或假子进程，也没有打开/哈希/流式读取 payload。其合成成功状态只说明解析合同成立，不是文件已写入或系统资源实测。全部独立旧远端 ownership 仍 UNKNOWN_NOT_CLEARED。

本轮实际 child process starts=0（检查解释器内部）、adb=0、device=0、真实媒体 stat/read/hash=0、Gradle=0、下载=0、payload源读取=0，retainedLocalOwners=0。外层工具调用的 Python 解释器不计为检查脚本创建的子进程。

## 新提案与交接

新 T3P 批次、唯一入口、证据目录、诊断目录及 nonce 见 D1_E4A_T3_DIAGNOSTIC_PLAN_V1.0.md。仍为一个 256B 合成输入，metadata最多20、每命令/接收15s、本机归还观察2s、日志1MiB，保留全部原 UID/pwd、标记、独立 SHA、历史准确 lstat、失败产物与旧未知。当前 executionAuthorized=false，只提案，由负责人另派。

T2P 已消费，实际 metadata1/producer0，无新诊断文件；不复用它的 attempt、证据目录或临时名。原 T2P 报告、原220B及原收据作为不可变引用保留。完整 T2 源码 ZIP 随包保留，外 seal ce571e95cd294a46b2f852e2d07c7f91126d2b388eb6b27ddcc589e91010b09a；E4A product seal a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d 不变。

T1P 实际远端退出码、SDK37.0.1与所查源码精确映射、81407B截断根因、旧远端资源完全归还继续 UNKNOWN。原81407B残件已归档，不恢复或改名。D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL保持。

封存前一次只读整包检查因核验器未规范 LF/CRLF 而拒绝；已证仅文本换行差异，保留原核验器和失败原因后修正比较方式。生产被测源码和67项结果未变，未重跑测试。

新 seal 为 d1e4at3/evidence/features-freeze.json，精确清单 evidence/source-manifest.json，完整源码包 artifacts/D1-20261017-E4A-T3-source.zip。外部 SHA、文件数量、ZIP 身份及只读 verify 结果集中发送负责人；seal 不自引用。封存后目录只读。package_tools.py 核验原引用、完整ZIP、被测源码、日志、有限语义事实及精确成员集合，不启动进程。
