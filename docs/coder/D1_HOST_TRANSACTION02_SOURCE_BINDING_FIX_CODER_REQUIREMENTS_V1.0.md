# D1_HOST_TRANSACTION02_SOURCE_BINDING_FIX 集中开发修复

2026-10-24 负责人审核完整独立B：report08781fabff3344242280f82050e46cb6e92a0abff5fb87e66111b672d0610380，manifest96f7c3939ea434a87b4503bd1e48019a010b85c602448509afd9f6d90202b5ad，逐核160项859708B bad0。原runner在准确受审边界外8新+3旧有限PASS保持，整包FAIL_STATIC_F01/P1；没有动态注入错源或错误移动，旧开发两FAIL和全部原证据保持。

新目录docs/coder/d1-host-transaction02-source-binding-fix，复用01原源码/真实JAR/依赖和API，不改旧01/原SDK/FIX02/Sink05。目标集中修复现有Binding遗漏source.identity.task及相关key/record/消费者的权威绑定，不新建身份/资源/事务框架或SDK公共Identity接口。

1. 捕获原source task的不可变快照，纳入同grant/source身份准确比较与必要私有key/格式/恢复记录。sourceInstance/uid/pid/epoch/generation相同、仅task不同的原group不得混用。按既有合同绑定原同一个source authority（如持有原group引用及已存在identity/lease），不能将新registry generation1当原权威，不能用path/hash/mtime替代。若同字段但不同原authority也应拒绝，在本批准确说明端口契约，不擅自要求旧SDK新增字段。
2. Binding.requireSource/require及LocalTransaction constructor、moveDrainedSource、RecoveryRef与LocalFormat实际消费者集中核。授权比较用准确字段/原authority，不仅靠可能有歧义的字符串拼接；私有持久key/record编码需包含task且可无歧义，不读取或迁移旧原事务。旧有限record遇新版本按合同拒绝，保留旧档，不补新COMMIT。不改原opaqueTask构造后快照正例，访问器改标签但不重定向原已捕获grant的合法用途保持。
3. 在一个串行worker预声明有限新增矩阵：相同uid/pid/epoch/instance/generation、task SRC_A/SRC_B的错源构造写前拒绝；原source完整排空后错source移动读写前拒绝且原源/目标未变；同grant其他字段全同仅task不同的Binding/record只读恢复拒绝；准确原source/task和合法原task快照正例通过。必要同字段不同authority按原契约在同一矩阵核，不扩无限场景。不调用旧01重新注入/移动或改旧历史FAIL；旧纸面F01与新实际正反证据分别标。
4. 集中回归原8真实文件集成+3authority及所有受此绑定/记录编码影响点。原内容校验/VKH1与真实Media3/Android层次保持；R03同bytes物理替换、TOCTOU/原FD竞态/隔离安全未测不靠本修复宣布关闭。READY/COMMITTED、firstFailure/UNKNOWN、同原ACK/worker归还及源全租约排空仍严格；新源错误必须实际发生于原接口，不由驱动先拒冒修复。

执行许可：一个准确本地离线新批，可将固定Python/JBR/新独立根的必要编译自测命令通过工具require_escalated自动审核在受限边界外执行，仅本批临时生成源/输出/硬链接/发布文件，不能管理员/改ACL防护/换目录绕审核。先冻结本轮准确源/argv/cwd/env/hash/预算再实际Popen；如自动审核拒绝保留理由不绕过，不在受限/外部来回重复探针。旧01独立B已经证明一个正常硬链接路径可用，不重建权限诊断。

集中最多一次严格JDK编译+一个串行worker，必要一次修复与受影响自检允许但不逐问题交接，保留两次准确来源/日志；两轮仍失败完整回交。固定原依赖/许可/版本，不新下载/升级/Gradle或Android构建。整批45分钟（首读前同调用立即建立单调时钟），具名读512MiB/永久输出32MiB，样本8MiB/源2/块64KiB/输出payload16MiB不变；每子观察300秒不强杀，原未返停新增保管不二close/ACK退款。无SDK/ADB/TCP/设备/媒体/网络/Git，不操作原UNKNOWN。

完整API/编码变更与差异、准确源/产物、自测原日志/预算/真实归还、静态/动态/未测范围、manifest/seal一次冻结后主动报负责人01a107c3-2bf9-7fa0-94a0-234258ca6774；完整新包审核后交tester独立整包复审，缺陷集中修复回归。通知失败留报告不绕过。D1未过/M0未启，主阶段/Flutter/独立Kit/框架许可/P0保持。