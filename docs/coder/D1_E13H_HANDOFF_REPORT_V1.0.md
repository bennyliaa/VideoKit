# D1 E13H 完整冻结交付与剩余限制 V1.0

2026-10-18；coder交VideoKit项目助理。正式E13H需求及server补充已分别保存coder/tester文件。本批完成最小离线准备、有限自检、一次必要host编译、最终JAR/脚本字节绑定、差异及准确补充方案，完整冻结交审。**结论：PREPARE_ONLY_DIRECT_ADB_DISABLED。生产直ADB入口实际硬拒绝，不能作为可立即执行的E13G补充核查入口。** 此边界遵照负责人“若最小方案不能排除server替换重启路径，生产保持拒绝、提交受审替代”的明确补充。

## 1. 准确冻结身份

- ZIP：`D:/CodexProjects/VideoKit/docs/coder/D1-20261018-E13H-source.zip`，928716 B，SHA256 `38ba1472783cf540cea451ea811af83ea1dfd8e9d60f1a4f08c3aa4bcf35af76`。
- 外seal：`D:/CodexProjects/VideoKit/docs/coder/d1e13h/evidence/e13h-freeze.json`，41354 B，SHA256 `befdcfcc5c04722cb138f845a27fe6d434d63fd204c211b39028914cdce2fc9e`。
- 180个准确ZIP成员/181条唯一冻结记录。默认verify、显式准确seal SHA verify、help、pack-help实际全部exit0；182份前后文件字节一致，writes0；校验不编译/启动SDK/联网或修改候选。
- 最终JAR：`D:/CodexProjects/VideoKit/docs/coder/d1e13h/artifacts/e13h-host-tools.jar`，334906 B，SHA256 `b610227fb564d8fb0d0085dcd12dd398e042ead38b28d36d9d9a3bc1babced35`，188生产class。
- 原E13F的183生产class逐字节沿用，不重编；5新增生产class全部是host-001实际测试使用的同一次编译字节，准确class与原source pin/fixture class另存。检查类不进入最终JAR。
- 十组旧seal及准确成员核验保持：E11/E11R1/E12/E13/E13A/E13B/E13C/E13D/E13E/E13F；不将重叠行数合称唯一文件。E13F外seal仍7b72f1bade91286b7d99fbba5459777261e905f4317e0daa969042148b5bf38f。
- 原回执在ZIP外：`D:/CodexProjects/VideoKit/docs/coder/D1_E13H_FINAL_READONLY_VERIFICATION_V1.0.json`。本报告与通知回执也在ZIP外，不改已封候选。

## 2. 实现与可执行边界

新增固定`E13GReadOnly`角色，无外部exe/serial/PID/任意shell参数。第一命令固定SDK路径、127.0.0.1:5037、serial HA1Q6WXR、shell -T与完整dumpsys activity processes、ps -A -w -o UID,PID,PPID,NAME,ARGS及显式成功边界。不grep、不把截断当完整；超过64KiB/10秒、权限失败/格式不符或出现其他active instrumentation即停止，不追加探针。

第二命令仅由第一完整raw严格推导：唯一原instrumentation组件、mFinished=false、准确原runtime SHA/batch/class/method、对应mRunningProcesses中的app/u0a221，与全局ps UID10221/name/完整argv/存在父对象匹配；原am客户端UID2000、准确全scope argv与父UID匹配。只生成这两个已确认角色的数字PID固定/proc boot_id/stat/status/cmdline读取，检查第二完整边界、PID/UID/PPID/准确argv/正启动ticks。未匹配fixture/codec等不能被当作不存在或归还；两次间连续性及终止资格仍不能自证。

包内Chain保留同一supervisor/retainAuthority，沿用既审Process/唯一reader、原archive/队列/E4Owned、原线程实际归还及非daemon custodian。第一未返/失败或解析不合格，第二不启动；超时是资格失败，不kill、不二reader/二close。直接Chain目前仅包内离线适配原型，公开CLI没有放行路径、未发once/审批入口，不绕过旧pending。

PowerShell新脚本`D:/CodexProjects/VideoKit/docs/coder/d1e13h/tools/observe_g_only.ps1`只接受准确G角色/JAR/固定根/原scope/32768B host cap；原Process/readers/文件记录/异常custody主体与既审E13F逐字节相同。正确G角色也因server限制在Process、文件分配或网络前硬拒绝；旧case/deploy角色拒绝。Java正确--g-readonly也在owner/网络前硬拒绝。--describe仅输出准备说明，不授执行权限。

## 3. server协议前置及准确限制

SDK仅静态读取：`D:/Android/SDK/platform-tools/adb.exe`，8273560 B，SHA256 `b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f`，实际启动0。

官方[AOSP客户端](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/android15-qpr2-s8-release/client/adb_client.cpp)在server协议不匹配时有kill/start路径；版本预检之后、SDK重新连接之前仍有server替换竞态，固定-H127.0.0.1不能成为绝对保证。官方[ADB头文件](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/adb.h)的ADB_SERVER_VERSION=41仅为候选协议来源，**准确SDK二进制到该源码/协议常量的构建映射仍UNPROVEN**，未从37.0.1软件版本猜测，也没有执行SDK读版本。

按补充要求做最小固定host:version原型：默认127.0.0.1:5037、一个服务、≤1KiB/2秒资格，严格OKAY/长度/候选0029；E4Owned原Socket/唯一reader/非daemon keeper先登记，超资格不关闭在途调用，实际原reader join/close返回后才退keeper；未知close继续原保管。测试只连接自身临时端口，实际5037连接0；该原型未接入生产dispatch，也不能消除后续连接竞态。

受审替代建议已完整列于补充方案：同已存在server的原socket上固定serial transport＋固定shell-v2，并完整处理stdout/stderr/exit framing，不经过SDK版本不匹配kill/start分支。它改变“必须由SDK adb.exe执行”的要求，**须负责人另明确最小范围和独立审查，当前未实现，不自行扩展为通用ADB客户端**。协议缺席/不兼容/未知应拒绝，仍最多两条固定设备命令。当前生产硬拒绝是实码及实测结果，不是仅写风险说明。

## 4. 有限实际回执与未决测试记录

`D:/CodexProjects/VideoKit/docs/coder/d1e13h/evidence/host-001`：唯一javac exit0，只编新增生产源及HCheck，对既审base JAR编译；SUCCESS/TIMEOUT/POLICY/WRITE_FAILURE四组自然exit0。实际包内Chain使用原PC监督器/reader/archive，唯一替身是有限本地JVM child，无SDK。成功两条自然原返；50ms短超时同原保管、第二0，释放本地fixture后原自然归还仍不恢复首资格。错exe/serial/argv/scope/UID/截断/其他instrumentation/启动ticks/父身份及生产dispatch均拒绝。写失败是实际archive IO直接故障，原close一次、资格失败；不是完整公开入口磁盘故障组合链证明。

首VERSION_OK在受限环境等待15秒未完成，保存pending(pid30384,killed=false)，Python抛TimeoutExpired。一次仅针对这一新本地测试PID的jcmd Thread.print返回no such process；**该probe原exit/reader close仍UNPROVEN，不因进程不在而补自然ACK**。未操作或查询任何旧产品PID/原handle，也未由coder终止它。原因NOT_UNIQUELY_DETERMINED；同一字节获得自身临时loopback权限后成功支持环境相关性，但不称已唯一诊断。单列`local-probe-environment-history.json`，不混成旧LOST诊断、不涂成PASS。

`evidence/final-002`：在明确仅本地临时端口的工具权限下，同一已编译字节完成VERSION_OK/BAD/TIMEOUT三组自然exit0；错误协议拒绝，50ms未返时同socket/reader/keeper保管，有限释放peer后实际原线程/socket归还。另有--describe、Java生产拒绝、PowerShell完整AST解析及正确角色禁用/错exe/旧产品角色拒绝三组真实原输出及exit；脚本原owner主体字节比较通过。没有第二次编译，没有实际5037/ADB/原会话连接。

直接官方源下载DNS失败，未冒完整下载/source SHA；使用官方web源码线索，版本编译对应明确未证。未编Android APK/Gradle/native、未重跑旧套件/长55秒/媒体；未引新Maven或native依赖，原APK身份/SBOM/许可门不变。

## 5. 四文档与准确补充预算

以下位于`D:/CodexProjects/VideoKit/docs/coder/`且纳入ZIP：

- `D1_E13H_READONLY_ENTRY_DELIVERY_V1.0.md`
- `D1_E13H_IMPLEMENTATION_CONTRACT_V1.0.md`
- `D1_E13H_SELF_CHECK_REPORT_V1.0.md`
- `D1_E13H_E13G_SUPPLEMENT_PLAN_V1.0.md`

正式coder/tester需求位于`D:/CodexProjects/VideoKit/docs/milestones/D1_E13H_CODER_REQUIREMENTS_V1.0.md`及`D1_E13H_TESTER_REQUIREMENTS_V1.0.md`，包含负责人server补充。两份滚动协调文件顶部已同步E13H准备/生产拒绝，旧段落保留，包内封副本。

未来原exec42537最多一次空输入收取、响应资格≤10秒，不循环、不发非空输入/Ctrl-C、不重建session。本轮读取0；空输出/工具返回不当原Java/reader/pipe/Android ACK。工具若无法保证文本资格先BLOCKED，不能靠取消Promise丢弃返回。

独立总预算256KiB草案：原host及父工具已采保守8192 B；两设备原raw各65536 B；一次server前置1024 B/2秒；原exec收取预留65536 B；外层Java stdout/stderr32768 B（不重复echo设备raw）；observer facts console8192 B。共246784 B，保留15360 B，重复console计相应预留；不继承旧余额/退款、不扩大额度或转供处置。每设备10秒及server2秒均是资格，未返保原对象。

## 6. 请求审议及停止门

请按正式tester需求独立整包离线复审，尤其核**生产确实拒绝、server预检不能绝对保证、SDK准确协议映射未证**与原始失败分栏；本包不是可直接执行的设备核查入口。之后请负责人选择是否另审固定同连接transport/shell替代范围，或继续拒绝；不得由本包自动启动E13G补充或任何处置。

原主任务最后PENDING/UNKNOWN、独立诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN均未解除，实际根因仍NOT_UNIQUELY_DETERMINED。actualScope/release/once/sourceReview均null；原E13F pin ABSENT保持，旧v17不能被新候选反控。用户持续设备授权已存在，当前限制来自准确范围和原任务未决。D1 NOT_PASSED / M0 NOT_STARTED，T07未派，P0/历史FAIL/UNKNOWN/许可保持。当前E13H完整冻结，等待集中复审与下一准确安排。
