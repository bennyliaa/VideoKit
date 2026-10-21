# D1 E2B 别名修复与R启动资源定位开发需求 V1.0

2026-10-17。负责人全文审阅E2A独立报告，采纳主路径静态认可、A01 P2及R519>512阻断。新docs/coder/d1e2b集中完成，旧E2A/失败证据只读，不提高512/+128、不重采洗去、不真实媒体执行。

A01：Ops.grant(alias=True)原控制内用Namespaces精确C输入路径、原已证物理身份，保留只读open/identity/close及失败原对象账目。补真实自有inputs/outputs分离布局到Q09-ALIAS活动链检查，INPUT_ALIAS拒绝、delegate字节0、无新增N/RPC，不能复制C到输出根掩盖。

R定位：批准一个预定有限对照，不制造媒体对象/不启动61场景。固定已有pwsh7.6.5/.NET10.0.11与同DLL，baseline Add-Type方案一个原R实例、候选直接绝对路径Assembly.LoadFrom一个原R实例，共至多2实例，不重启碰低值。各实例固定四阶段：最小NoProfile/NonInteractive启动、加载已有程序集、RHost/Sandbox初始化、首次HELLO序列化。每阶段一次原PID/creation/owner/线程/句柄/WS/private采样，保第一超限与全部阶段差异；若阶段无法安全暂停就明确缺证，不强编阶段样本。LoadFrom仅待验证加载开销假设，不预称少7句柄；仅清理可归因自有不必要对象/加载，不关CLR内部任意句柄、不强制GC、不换runtime/owner/flags偷改基线。

诊断单独成本：至多2helper实例、8阶段观测、单临时observer句柄且逐份close、每阶段≤5秒/每实例≤30秒/总≤90秒决策与清理（不可中断OS仍PENDING），诊断日志≤512KiB并纳入本新批4MiB，fixture≤2MiB。控制/metadata为诊断独立清单，不能记入原452假称无额外动作；不读test_media/运行真实PF。保留不满足512的历史，候选基线不符合仍BLOCKED，交具体必要宿主兼容性结论而非无限调优。

如候选原R在规定HELLO门槛满足512且其余诊断条件具证，允许本批一次自有非媒体文件、actual OS observer完整61回归（非mock），按既定全部原行/180秒/24/6/8/512等硬界；未满足则不启动该回归。全回归如果停止保FAIL和清理事实，不补跑求通过；mock仅明确标范围的逻辑自检，不能替准入。所有编译/有界针对性回归集中完成再冻结，不小项交测。

交D1_E2B_DELIVERY/REAL_IO_ADMISSION/EXECUTION_APPENDIX_V1.0.md及源码ZIP/产物/manifest/诊断清单/阶段证据/只读verify/hash。根因证据与假设分开，明确是否只证明LoadFrom前后总数差异而非句柄类型因果。完整无在途后主动报告负责人，不自行派tester/真实实验。真实授权层/unique root未批准，JNI/C14/P0/历史FAIL保持，D1未通过/M0未启动，无Gradle/ADB/设备/下载。
