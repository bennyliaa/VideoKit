# D1 E13A＋E13B_OVERLAY 平板执行报告 V1.0

日期：2026-10-18。正式批次：`db65c958-5163-4467-90e0-6f099076142f`。依据：`docs/milestones/D1_E13A_E13B_TABLET_TESTER_REQUIREMENTS_V1.0.md`及同批`D1_E13A_E13B_TABLET_ENV_RECOVERY_SUPPLEMENT_V1.0.md`。

## 结论

**批次在单次部署入口阻断，未安装任何APK，六方法全部NOT_RUN。** 恢复后的真实M1完整通过179项独立核验；实际原E13A host JAR随后因`E11_ONCE_FIXED_ROLE`退出，尚未创建新once，也未进入任何SDK部署child或install。

发现唯一集中缺陷 **E13AB-DEPLOY-F01/P1：外层要求`e13a-activation-deployment.once`，内部共享once写入器仍只接受`activation-deployment.once`，实际CLI无法派发部署。** 不在tester侧改名绕过，不重发部署，不进入M2或六方法。请集中修复host门接线及受影响证据后整包复审。

D1 NOT_PASSED，M0 NOT_STARTED。原长期真机授权及本次派单有效，不需要再次询问用户使用许可；当前停止是具体部署门失败。原E13绑定/只读入口的有限关闭、E13B元数据静态结论不撤销、不外推为六方法真机PASS。

## 授权、输入与原材料

执行根目录：`D:/CodexProjects/VideoKit/docs/tester/D1_E13A_E13B_TABLET_EXECUTION/db65c958-5163-4467-90e0-6f099076142f/`。人类长期授权原文、历史来源文件pin、负责人正式派单及环境恢复补充均已固化；原registry历史prepare authorization只作为接受来源，不充本次新许可。

| 输入 | SHA256 |
|---|---|
| inputs/execution-scope.json（6067B） | `8b0b15f122de321e1d3f569720f2b7b84fce7996b16d49b1fb7a8bd6f3cd032c` |
| inputs/runtime-scope.json | `723df325c6c4e515dff6d71cf17d1e19731a80d480d34ffbb43f7aee4482bc82` |
| inputs/activation-release.json | `910f51490d20d2974e768de54ef5f333d7688bf8a646020d3a7b8575275c44bc` |
| inputs/activation-trust-deploy.json | `f4a2621c3d77d1b355a22261c8c6e36324ebafc98278d44b4a5fea053f1077f2` |
| inputs/env-recovery-authority.json | `5d6bb937cd6a1bb2b5121d25aa1618036ea788461d0601fe3ffd0ffd10095b26` |
| sourceReview：E13B独立报告 | `b3f19c478dbae2218b0b776b6f85463d43c1df70c4e6baccdb1a2d63fc51c876` |

真实生产record保持已审精确schema的process48常量，外执行scope及补充独立计入占用复查/环境恢复，未修改冻结候选。固定新once路径只在config中绑定，生产入口失败前后均不存在，没有伪造已完成或预先消费的once文件。

使用已审E13A delivery三APK/JAR，未混入历史root/final制品：

| 制品 | SHA256 |
|---|---|
| app-debug.apk | `962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad` |
| app-debug-androidTest.apk | `83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13` |
| fixture-debug.apk | `868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8` |
| e13a-host-tools.jar | `a0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f` |

E13B seal/ZIP/manifest、三完整argv及E13A sourceReview均由外执行scope按实际pins绑定。产品/冻结源码、APK、JAR、旧封印均未改；本批没有构建、native重编、旧套件/信号重跑或媒体payload读取。

## 实际时间线与环境恢复

下列时间为2026-10-18本地时间。

| 时间/步骤 | 实际结果 |
|---|---|
| 前置controller检查 | 发现LendManager本机构建及近期同串号记录，最初占用不明；负责人澄清不能据此永久推定设备占用，允许已审M1实际只读确认。未联系、抢占或操作其他项目 |
| 15:49:26 首个M1 | 原直接adb客户端PID50780，0.353秒自然exit1；stdout0B/stderr144B：daemon启动失败、cannot connect to daemon。没有设备记录，非产品FAIL，不误判设备离线或空闲 |
| 15:54:30 有界host恢复只读检查 | 5037 listener归属准确SDK adb.exe PID5340，进程早于本批；无operator start-server/kill-server/重启。采用已有server，未以旧client PID消失补任何原closeACK |
| 15:59:14–15:59:18 恢复后的新M1 | 负责人明确补充授权的新attempt，不记为两次设备占用复查；通过正常工具权限入口直接启动原adb.exe，PID31440，4.635秒自然exit0，完整21803B/70记录，独立179项通过 |
| 16:06:03–16:06:04 唯一部署Java entry | PID35180，0.619秒自然exit1，stderr819B为once固定角色冲突；原监督器pcClosed、原Process/reader/pipe真返，未创建once、未启动内部部署SDK child或安装 |
| 后继 | M2、六方法及M3均未启动，停止依赖，无安装重试/换名/换UUID或额外设备诊断 |

SDK文件身份只读记录：`D:/Android/SDK/platform-tools/adb.exe`，8273560B，SHA `b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f`；source.properties为37.0.1。已有server为127.0.0.1:5037、PID5340，记录的启动时间为前一天。该共享daemon预期长期运行，不当作产品残留资源。

原Node执行入口失败与后续正常权限入口成功分开保留，不将它当USB/设备故障的已确认根因。第一次ADB stderr报告过自动daemon启动尝试，但未给独立子PID/归还回执；没有据后续PID观察回填该尝试的closeACK，也不外推部署pcClosed证明整条外部进程树。

另有一次本机控制器时钟兼容错误发生在任何原进程分配/启动之前，已改用显式performance时钟并留痕；该阶段设备调用0，不是重复M1或产品重试。现存raw解析兼容修正使用0次。原失败M1全程保留，没有改成成功。

## M1当前实测及限定关闭

以下只描述15:59恢复M1的实际观察，不代替之后未执行的M2/M3：

- HA1Q6WXR / TB138FC / API31 / arm64 / user0，RUNNING_UNLOCKED。
- 完整E13B支持路线输出IDLE：原processes扫描372343B、5028行，all-known/OOM/最后尾标记/原exit0完整，active_entries=0。相关ps仅表头，app/fixture服务均(nothing)；不由空grep或脚本exit0推定空闲。
- 精确已接受v15 ACTIVATION app/test byte pair、UID10221/10222、原data inode6972/4741符合。test APK自身versionCode=0按精确byte allowlist核，不错误要求test也显示17。
- fixture现场确实未安装；没有执行首次安装，因此实际fixture UID、kernel拒绝和原binding归还尚未实测。
- 34stat、18control完整小字节、精确inventory及全部七个旧产物stat符合，非零媒体payload未读取或重新hash。已归档`operation.pending.N2-e5-aborted`保留，无新在途pending。
- 完整ledger2271B，SHA `e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649`；独立重算7R/7S、214483B、reserved0、链尾`0eadfcd645c9ea796ba13b813c02e1604c128ef619683f1f6f2bb76b68a96a75`。旧1011B/107218B接受前缀哈希保持，原13metadata、三迁移控制记录及fence/oldCloseACK=false未改。

**限定关闭：E13B元数据查询/完整读取路线在该平板这一次M1实际成功。** 不外推ACTIVE厂商实际事件、长期/重启、其他设备、全部source生命周期或六方法已通过。之后没有设备操作，最终在线状态没有重新读取；不将本次M1当后续修复批次的实时许可。

## E13AB-DEPLOY-F01 / P1：真实once角色接线冲突

触发：使用本批已审原JAR、精确v15→17 scope/release/config及新固定once路径，执行一次`E13HostActivationSession --approved-e13-deploy`。

原异常：

```text
java.io.IOException: E11_ONCE_FIXED_ROLE
at ...E11DeploymentOnce.record(E11DeploymentOnce.java:22)
at ...E13HostActivationSession.lambda$main$1(E13HostActivationSession.java:32)
```

源码和实际JAR class常量均核实：

- `docs/coder/d1e13a/tools/E13HostActivationSession.java:31`要求basename为`e13a-activation-deployment.once`，下一行调用继承的E11DeploymentOnce。
- `docs/coder/d1e13a/tools/E11DeploymentOnce.java:22`只接受`activation-deployment.once`，在attempted置位、owner.allocate/CREATE_NEW以及SDK port初始化之前直接拒绝。
- 实际冻结JAR中的两个class分别包含上述不同名称，不是源码/JAR错配或本次参数拼写错误。

因此两道生产校验不存在可同时满足的filename。tester不能将config改成旧名规避，因为外层会拒绝且违反本批固定newonce范围。

影响：本次无法升级或启动六方法；没有部分安装，fixture未装，没有设备输出/READY/R/S。原PC registry监督器实际返回同一handle的pcClosed/allOriginalsReturned=true，外层原Java及stdin/两reader/pipe自然归还，没有原部署资源UNKNOWN。

修复建议：集中最小修复host once接线，使本批同一精确新角色能通过，同时保持旧E11固定角色、CREATE_NEW、父路径/非symlink、force/readback及原close规则；不放宽为任意filename，不改历史once/registry或重放本次entry。补覆盖真实CLI与共享once写入器接线的有限本机证据，不能仅用绕过此层的synthetic deployment port充验收。若仅改host tools，不要求机械重建未变APK/native或重跑绑定/source/信号套件；以新完整冻结包交复审。

**此前静态复审漏查了共享once实现的固定名称接线。** 本次按真实入口发现后立即停止，没有修改候选或批准文件名，也不以再试一次验证修复。原部署失败entry和所有输入保留。

## 六方法结果

| 方法 | 结果 | 原因 |
|---|---|---|
| ordinarySenderCannotBindCodec | NOT_RUN | 部署前置失败，fixture未安装 |
| authorizedHostSourceReadAndClose | NOT_RUN | 同上 |
| oldGenerationNeverOpensSource | NOT_RUN | 同上 |
| twoConsumersHoldSourceUntilLastReturn | NOT_RUN | 同上 |
| cancelLateOpenRetainsOriginalOwner | NOT_RUN | 同上 |
| lateReadAndCloseFailureDoNotReleaseEarly | NOT_RUN | 同上 |

没有执行4096B非媒体source夹具、20KiB准备、4224B read/6open/7close，也没有将静态/历史或本机替身结果写成此次Android方法PASS。未主动注入永久UNKNOWN/OOM/重启/信号。

## 资源及停止结算

ENV_RECOVERY补充总上限56/文本2MiB，原成功路径48及两个半小时占用复查分别记账，未清零。

| 项目 | 实际/保守记录 |
|---|---|
| 原直接执行 | 失败M1、恢复M1、部署Java，共3个，均实际自然返回 |
| host恢复只读检查 | 1/3；operator start-server 0/1 |
| 已知实际操作 | 4；ADB首次自动daemon尝试另保守计1，实际/报告尝试保守合计5 |
| 未派发部署child | 实际0；原32个child预留仍单列冻结，不冒称32个实际调用、不用它回充后继重试 |
| 操作保守总占用 | 37/56（5实际/报告尝试＋32未发预留），余19不构成自动续跑许可 |
| 原三个客户端输出 | 22766B；host只读记录1001B，已观察文本23767B |
| 未发child文本预留 | 524288B单列冻结；保守文本548055B < 2097152B，不能把预留冒充已产生原raw |
| 占用复查 | 0/2；没有半小时重查、额外PC STATUS/OP/CLEANUP连接或安装/方法重试 |
| 数据副作用 | 本批安装0、fixture安装0、新once0、source实验0、媒体payload读0、新输出/READY/R/S=0 |

原输入及current M1审证完整，known原Process/reader/pipe实际返回。部署原监督器handle `11939531-0c75-41b3-b9a6-1e6afde0f247`返回pcClosed，未依赖kill/force-stop、第二close、换对象或新进程冒充旧资源归还。

## 可复核证据与交接

执行根下主要证据：

- `inputs/`：真实授权引用、原scope/release/config及ENV_RECOVERY补充，固定newonce路径。
- `evidence/01-M1_PRE_DEPLOY-*`：首次原失败argv/stdout/stderr/receipt，保留host环境失败原文。
- `evidence/env-recovery-read-01.json`：同SDK文件hash、5037实际listener/进程来源；未采无关完整命令。
- `evidence/02-RECOVERED-M1_PRE_DEPLOY-*`：完整M1原文、实际Process/reader/pipe回执及179项审证。
- `evidence/03-DEPLOY-*`：原Java入口argv、819B异常/物理pcClosed、外层回执。
- `evidence/resource-ledger.json`、`live-resource-ledger.json`：实际、未发预留、环境及文本各自结算。
- `evidence/independent-final-audit.json`：**425项最终证据核验通过**，包括原raw、实测M1、实际JAR冲突常量和E13A/E13B冻结未变。此PASS是证据一致性，不是本批产品测试通过。

本报告与manifest/原回执集中发负责人安排最小修复，之后整包复审并重新安排准确现场前置，不拿15:59 M1替代后续当前门。当前批次停止，不自动修产品、重发部署或进入下一方法。

E11有限PASS、C13系统signal0严格FAIL/外部raw11/另方法OS11、C14 NOT_RUN、ordinary UNKNOWN及全部P0/许可/renderer/audio/Kit门保持。D1 NOT_PASSED / M0 NOT_STARTED。发送后报告字节保持，通知回执另存。
