# D1 E4A-T2 开发交付 V1.0

2026-10-17。候选 D1-20261017-E4A-T2；本机有限验证完成，设备诊断 NOT_RUN，待负责人审查后另派 tester。所有路径相对项目根 D:\CodexProjects\VideoKit。

## 已证结论与未知边界

已定位 T1 参数适配中的模式混用：相同的 shlex.quote(script) 同时用于 shell 与 exec-in。所查 AOSP 客户端的 shell 分支直接连接参数，exec-in/exec-out 分支则会再次转义首个命令之后的每个参数。因此预先引用的脚本在后者成为带有字面单引号的 sh -c 输入，整段脚本被解析成一个命令名。参见 [AOSP commandline.cpp 固定提交](https://android.googlesource.com/platform/packages/modules/adb/+/7c2fd99d6ec7e0d2d977ba03cecc82375af1baad/client/commandline.cpp) 与 [escape_arg 实现](https://android.googlesource.com/platform/system/core/+/refs/tags/android-7.1.2_r24/adb/adb_utils.cpp)。

本机按该源码的参数拼接规则，使用已有 Git sh.exe 的真实解析器回放 T1P 原 producer 参数：模型客户端返回 0，实际内层 shell 返回 127，未创建目标。改为 exec-in 传原始脚本后，同一合成数据完整写入；但该旧通道仍无原接收端 stdout/stderr/退出码证明。exec-out 的方向相反，模型不会将主机提交的 256B 转发给远端 cat。以上均为本机源码模型的结果。

| 项目 | 结论 |
| --- | --- |
| 模式混用造成重复引用 | 源码支持；原参数本机真实 shell 已复现 |
| 本机 SDK 版本 | 只读 source.properties：37.0.1；未运行 adb |
| 该 SDK 二进制与所查源码的精确提交映射 | UNKNOWN |
| T1P 设备上是否实际返回过远端 127 | UNKNOWN；原日志没有该证据 |
| E4A-N 的 81407B 截断根因 | UNKNOWN；旧路径并不等同 T1P 参数 |
| 设备上新路径是否可用 | NOT_RUN，不能由本机通过推断 |
| 前次远端接收资源是否全部归还 | UNKNOWN_NOT_CLEARED |

T1P 原证据仍为主机提交 349102B、客户端 exit0、独立 temp ABSENT；不能将其改写为远端成功。原 81407B 残件已经归档为 files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep，本批未恢复、改名或读取它。原 backend argv、完整 T1P 报告均保存在 d1e4at2/reference，引用映射见 evidence/reference-map.json。

## 最小修改

新增 d1e4at2/tools/remote_command.py：shell 仅在传入整体脚本时预引用一次；legacy exec 使用原始脚本。没有修改冻结的旧工具或产品源码。实际拟派诊断固定选择 shell -T -e none，并要求 shell_v2；不满足即停止，不回落到 exec-in/out。该选择需要独立通道承载 stdout/stderr/退出码，依据 [ADB daemon shell 服务](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/daemon/shell_service.cpp)；所阅 blob 为 0b71b035a02d0d347cb06d69732c6b5e7f4a8e8d，未声称与设备 OEM 实现一致。

新增 diagnose_once.py 是固定 256B 合成诊断入口，无真实媒体源参数。只有原接收端 BEGIN/END 同时证明实际 UID、pwd、准确相对路径、同一 PID、256B 计数，再经另一条命令独立 stat/SHA 一致，才记 SYNTHETIC_DIAGNOSTIC_VERIFIED_NOT_A_MEDIA_FIXTURE。主机 submittedBytes 单独保留为快照，无法取得时为 null；预算值不是落盘量。

exact_process.py 从 T1 原样继承：13077B，SHA256 f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d。实际 stdin close、源关闭、原 wait、drain 与线程均须归还；UNKNOWN 继续强持有原对象，禁止后续 I/O。迟到的归还不会把旧失败尝试升级为通过。普通文件 open/read 与系统调用无法保证可强制中断；发生 UNKNOWN 时原解释器保留等待观察，不以退出解释器作为归还证据。

## 有限本机验证

最终 repair-004：**43 项断言通过，32 条直接调用记录，保留的本机 owner 为 0**。证据入口 d1e4at2/evidence/local-check-results.json 绑定最终六个源码、原检查日志及 owned/local-results.json 的长度与 SHA；不是将历次断言累加。无旧 72 项、63 项重复执行。

32 条记录由参数回放/五种诊断场景及本机上下文探针构成。假客户端内部实际调用已有 Git shell；run-as 仅替换命令名并移除包名，没有切换 UID；toybox 前缀映射到已有本机工具。成功场景使用真实本机 UID/pwd 和真实本机合成文件，不冒充 Android UID 10221。UID 进程列表场景为合成快照，不能证明设备状态。

覆盖：原双重引用、修正后的 legacy 输入、exec-out 方向、全 256 字节、缺 END、缺 shell_v2、疑似旧 cat、独立 SHA 错误、标记 UID/路径/PID/计数拒绝、同 attempt 再调用拒绝、旧自有占位文件不变、历史路径仅三个准确 lstat、预算与实际提交量区分。所有最终直接调用都观察到原退出和本机资源归还。

| 尝试 | 结果与保留原因 |
| --- | --- |
| main-001 | FAIL；受限令牌下 MSYS 同步对象创建失败，尚未取得有效 shell 复现 |
| repair-001 | FAIL；本机探针的 id 查找 PATH 问题，原参数 127 的独立回放已发生 |
| repair-002 | PASS 39；随后收紧历史路径检查，旧证据保留 |
| repair-003 | PASS 41；随后明确原上下文输出及提交快照，旧证据保留 |
| repair-004 | PASS 43；最终源码与最终证据 |

必要修复及被替代源码/结果保存在 check-attempts 与 preserved-before-repair-*。本机 Git shell 需要受限令牌外的同步对象访问；已获自动审核允许，仅执行自有假进程/合成数据检查。上述不是设备重跑或历史测试重跑。

## 下一步与交付完整性

可直接执行的有限诊断方案见同目录 D1_E4A_T2_DIAGNOSTIC_PLAN_V1.0.md；当前 executionAuthorized=false。只允许未来另批平板一次 256B，不预置 MP4/AVI，不继续编码、Binder、预算标记或其他产品方法。失败保留诊断产物，无补跑/换路。

本轮 adb=0、设备=0、真实媒体 stat/hash/read=0、Gradle=0、新依赖=0。既有 E4A seal a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d 不变；T1 seal 954288092916e5281c7a50183adc9041e82c05d16cfe6fd6cd5013fb75139c0f 及完整源码 ZIP 随引用保留。D1 NOT_PASSED、M0 NOT_STARTED、全部 P0 与历史 FAIL 保持。

封存入口 d1e4at2/evidence/remote-freeze.json，源码清单 evidence/source-manifest.json，完整包 artifacts/D1-20261017-E4A-T2-source.zip。外部 seal SHA、ZIP 身份及只读 verify 结果在集中交付消息中提供，避免文件自引用。package_tools.py 的 inspect/freeze/verify 只检查有限源码与证据，不启动任何进程；verify 必须提供负责人收到的外部 seal SHA，检查精确文件集合、完整 ZIP 成员及最终语义证据。
