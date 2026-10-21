# D1 E13C HOST_ONLY 修复交付 V1.0

日期：2026-10-18。针对 E13AB-DEPLOY-F01/P1：真实 E13A+E13B 批次的唯一部署入口在 E11_ONCE_FIXED_ROLE 拒绝，未创建 once、未启动 SDK child、未安装，六方法 NOT_RUN。本批只改主机接线，交独立复审；D1 NOT_PASSED / M0 NOT_STARTED。

## 修复

E11DeploymentOnce 原公开构造仍选择私有 E11 角色，只接受 activation-deployment.once，历史执行规则不改。新增 e13Activation 固定工厂选择私有 E13A 角色，只接受 e13a-activation-deployment.once 及 e13ActivationDispatchIntent；没有任意 basename 参数。E13HostActivationSession 保留已 pin 配置中的绝对路径、registry 外和固定名检查，使用该工厂。仅两份生产 Java 源码变化。

原 CREATE_NEW、existing-parent/no-symlink、已存在完整/部分文件拒绝、写入/force/readback、同一原 close 真返后才能返回 record、原 holder 提前注册监督器均未改。record 异常不进入后继 SDKport。UNKNOWN 不重试/第二 close，不改原 E4Owned/E9PcSupervisor/custodian。

## 本机证据

只用已有 JDK 离线编译两份源码；新 JAR 173 成员，其中 168 个精确继承 E13A JAR，5 个由两份修复源码生成（新增私有 enum）。成员逐项记录 source pin；不把 test shadow 或检查类混入交付 JAR。

8 个 helper 分支：E13_OK、E11_OK、E13_OLD_NAME、E11_NEW_NAME、ARBITRARY、WRONG_INTENT、FORCE_FAIL、CLOSE_IN_FLIGHT。执行实际交付 helper 与真实监督器。在途原 close 尚未返回时 state=CLOSING、allOriginalsReturned=false、SDK后继=0，真实 pcIsolationAck 保原 custodian；只释放该原 close 调度后自然返回、原监督器自然结束。

8 次真实公开 E13 CLI：精确历史 DEVICE trust/registry/scope/release 本机夹具到首 SDK 前门；第二 JVM 同一 config/once 拒绝；旧名、任意名、错 config role、SYNTHETIC_LOCAL environment、部分文件、空文件均拒绝。原 E13HostActivationSession 和 helper 由实际新 JAR 加载。只将 E9HostDeployment.private run 的首调用替换为记录准确 argv 后抛本机标记，真实授权/registry 门没有替身、没有伪造 DEVICE 环境。首命令为原 data inode 查询；没有调用 commands.run 或创建 SDK child，所有真实监督器均返回 pcClosed。

UNKNOWN 使用交付 JAR 的原 helper，CLOSE_AFTER 受控异常令 holder=UNKNOWN、returned=false、同一原 authority 保留、dispatch=0、close仅一次、对象重入拒绝。监督器仅为有限引用保留替身，避免故意遗留永久非 daemon 进程；**不声称永久 UNKNOWN 下真实 custodian 的在线运行/最终归还已实测**。真实监督器保留逻辑字节继承，其在途原 close 托管由上一组实测。初轮 UNKNOWN helper 同源码另编证据保留，补强检查明确从交付 JAR 加载。补强 JVM 自身退出0，初始日志审计将 JVM 生成 lambda 也误要求 JAR 来源，已针对现存输出修正过滤，没有重跑 JVM、没有产品失败。

所有测试写入只在 docs/coder/d1e13c/evidence 下明确 local-test 夹具目录，不写历史 registry/真实 once/新正式执行目录。没有 ADB、install、设备、媒体、APK/native 构建、旧绑定/source/信号套件。

## 复用与新批方案

产品精确复用 E13A v17/ACTIVATION/ABI1 三 APK及签名；source 仍已接受 v15，旧失败批未安装17。元数据精确复用 E13B 完整三 argv，不改内容或预算。E13B 已在平板一次 M1 实际通过只作历史引用，后续必须 fresh M1，不外推 ACTIVE 事件或当前在线状态。

新候选 docs/coder/d1e13c/release/candidate-binding.json、device-plan.json、new-scope-draft.json 绑定新 host JAR，sourceReview/actualScope/release/config/once 均未签发，独立 E13C 复审通过后才由负责人采纳。runtime 的产品 batch 和固定 once basename 保持 E13A，**新独立 scope UUID/执行目录**承载新 once，不重放已失败批 config、不继承旧一次性许可或预算。

成功路径48=部署入口1+子32+六 Java6+六 instrument6+metadata3；另提案2次仅部署前占用 M1 复查，至少间隔30分钟，最大50。文本仍2MiB：成功路径分配1638400B，复查预留131072B，总1769472B，余327680B。每 metadata 原直接ADB64KiB/55s，原配额不扩；无额外STATUS/OP/CLEANUP、恢复/重试/抢占。遇环境失败需负责人新明确范围，不能继承旧37/56余19；UNKNOWN停依赖保原托管，不用未发预留回充重试。

旧214483B/7R7S/0reserved、旧107218前缀/oldCloseACK=false仅引用接受时点；本批无在线读写、READY/R/S。全部P0、历史FAIL/UNKNOWN、许可、renderer/audio/Kit门保持。新ZIP外seal和最终实际只读回执另存，交负责人集中审查后再派设备批次。
