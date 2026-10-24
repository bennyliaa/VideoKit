# D1 FACTS_V2_QUALIFICATION01 独立整包B测试要求

2026-10-24；负责人正式派发，仅离线整包复审，不执行SDK/ADB/设备/Gradle或媒体。开发与测试要求分别保存，完整结果集中回负责人，未经新派单不逐缺陷回交修复。

## 来源与负责人核验

候选 docs/coder/d1android02-facts-v2-qualification01。DELIVERY SHA256 20601b961d781773bee8e62703051f4673e7182b675437d8a3373f3b1d247338；source26 dfcd0add7bf89b9363b7efe23b45bed0145ee977fddd48fd45725546350e74d0；gate18 e404f32bccb9aac960b001b7e529d7aed06a501d93aca2eca255c12b8a264a61；七角色plan b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8。

负责人实际逐项核 reference/full-manifest.json（07a7572ce553f4ad7cd85ca98a97e6fe7b643275d228deb6a9e05cb4c111a0c4）132项/5125910B，大小与hash bad0；冻结ZIP 070989425d65bcc487ca1f7addfc7a9c425ee9cf9b1ed0e5bbd192397d7d551d，共133唯一成员。ZIP内容仍由tester独立逐字复核，不以唯一成员数代内容核验。coder六组自测是开发限定证据，非独立验收。此前额度不足导致报告通知失败，负责人从冻结原件恢复审核，不要求重跑开发自测。

## 整批验收范围

1. 以阶段A oracle-and-matrix.json的160项为追踪表，对齐最终Schema和实际Python/PowerShell字段；每项标实际执行/静态/引用同源/未执行及证据。不得复制旧20源通过到新26源，不将计划数写为实际覆盖数。
2. FactsBundle必须来自实际原Capture对象，逐字绑定raw、原CLI回执、preauth/policy/runtimeBinding、scope/source/plan/run/nonce/route/proof和实际原返回。dict、自述controllerReturned、缺失wait/readers/streams/H、UNKNOWN以及错源证据准确拒绝。实际对象与纯模型分别标记，不制造真实资源UNKNOWN。
3. 未批准导出恒REQUIRES_REVIEW/approved=false/services=[]；系统标志/OEM/UID不能自动授信。外批review原字节hash、candidate/bundle、窄HOME/服务证据、package/user/UID/firmware、APP/PERS、严格整数state和EXACT_SNAPSHOT窗口逐层核验，TOP2/3及instrumentation竞争规则优先，禁止任意异常冒作准确拒绝。
4. 补age=0及299.999合法边界、300及未来/反向/类型错误；逐字段缺失/多余/null/错误类型、重复JSON和大小写碰撞、V1/V2混合、review字节链篡改、准确target/source/plan。必要组合按风险矩阵覆盖，不要求无意义全笛卡尔积；未覆盖明确列出。
5. 独立执行实际原global_idle的V2消费和V1回归，保留原45/17及窄服务正例，验证目标再次核鲜度且导出/审阅不刷新时间。Schema文件与运行嵌套严校验职责逐项对应，不能只跑Schema。
6. **传输容量**：核实际rawHex序列化、receipt和外层Capture的262144B限制；使用合法接近raw139264B上限的资料做精确字节计算和必要有界原通道验证。连同qualification嵌套review/candidate/bundle/outer的真实UTF8体积，对照全部接收限制。小样本成功不能证明全部宣称范围，不能扩大既有cap来掩盖缺陷。
7. **真实外部审批可操作性**：静态并用现有有界离线fixture验证原资源归还后保留真实Capture对象、导出候选、接收明确外部review、在原300秒鲜度内签发的顺序。不得从文件或布尔值伪造原Capture，不把同调用方合成review当真实负责人往返，不新造IPC/密钥/签名或通用框架。缺失的真实交接能力集中报告，不自行扩实现。
8. 核原preStart、实际Popen/.NET全图、raw父环境与Windows子环境差异、写入保护和异常/finally路径；不改旧源码、冻结包/账本/once/历史FAIL/UNKNOWN。PREAUTH原误写恢复等历史照记。本B不运行完整真实七角色或给HOME服务真实资格。

## 执行边界与交付

仅新建 docs/tester/D1_FACTS_V2_QUALIFICATION01_INDEPENDENT_B_EVIDENCE 及同名前缀报告/manifest，不写候选。先冻结测试驱动、输入、来源、预算及全Popen/.NET图，再一次集中执行。复用已审原capture和ENV02环境规范，不另建诊断/释放框架。动态总预算360秒、320秒停止新增；读取1GiB、产物16MiB、辅助进程最多96、并发1，生产/SDK重试0；生产时间/字节/once原限制不扩大。纯准备未进入产品且无新未知可在本批保留修订后改驱动，不为每个纯准备错误单独交接；原调用未知停止新增，保留原证据，不主动二close/kill/attach/补ACK退款。

完整报告给各组真实结果、准确拒绝阶段、160项追踪、容量计算、外批操作可行性、集中缺陷/缺口与建议下一整批，附完整manifest和原返回/预算审计。全部完成后主动向负责人聊天01a107c3-2bf9-7fa0-94a0-234258ca6774(local)发完整交付；通知失败保存回执，不绕过。负责人审核后才派修复或新功能。此批不Git/index/提交；后续由负责人安排静止检查点，遵循既有分支/草稿PR规则。D1未通过/M0未启动；既定成熟开源框架、精确版本许可、Flutter/独立Kit与全P0不变。