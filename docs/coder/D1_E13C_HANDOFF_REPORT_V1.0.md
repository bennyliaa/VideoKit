# D1 E13C HOST_ONLY 完整交接报告 V1.0

日期：2026-10-18。正式需求已保存 docs/milestones/D1_E13C_CODER_REQUIREMENTS_V1.0.md / D1_E13C_TESTER_REQUIREMENTS_V1.0.md。请 tester 独立集中复审新主机修复及实际 CLI 接线，再由负责人派新设备批次；当前不启动任何设备范围。

## 修复与原门保持

针对真实报告 E13AB-DEPLOY-F01/P1（原报告 SHA256 7c7e4174fff072ed8a45dd9260137eaf4a50dcb30a5db8d7df33702e8d0a934a）。仅变两份主机源码：
- docs/coder/d1e13c/tools/E11DeploymentOnce.java：旧公开构造仍固定私有 E11 角色和 activation-deployment.once；新增 e13Activation 固定工厂选择私有 E13A 角色，仅 e13a-activation-deployment.once + e13ActivationDispatchIntent。无任意名称参数。
- E13HostActivationSession.java：保留准确 pin 配置的绝对路径/registry 外/新固定名校验，接上述工厂。

原 CREATE_NEW、重复/部分文件拒绝、无symlink/已有父路径、写入/force/readback/同一原close真返才从record返回并构造SDKport、提前 retainAuthority、UNKNOWN保原holder/custodian均保留。没有改旧 E11 入口/历史角色或 scope 文件名绕过。

## 本机验证及边界

1次已有 JDK 离线两源 host 编译成功；新 JAR 173成员，168成员直接复用旧JAR精确字节，5成员由两源生成（含新增私有enum）。源码/编译argv/pid/自然exit/逐成员来源见 evidence/host-build-001、host-jar-manifest.json。测试shadow不进入JAR。

8个 helper 分支通过：E13_OK、E11_OK、E13_OLD_NAME、E11_NEW_NAME、ARBITRARY、WRONG_INTENT、FORCE_FAIL、CLOSE_IN_FLIGHT。使用交付helper/真实监督器：close在途时原CLOSING/allOriginalsReturned=false/SDK后继0，真实pcIsolationAck保原custodian；释放同一原close后自然返回，原监督器自然结束。旧E11固定名在实际共享helper验证通过；旧E11公开CLI成员字节继承，未声称另跑旧部署套件。

8次真实公开 E13 CLI（包括第二JVM重复）通过预期门：准确E13A配置到首SDK前门；重复、旧名、任意名、错config role、SYNTHETIC_LOCAL环境、部分/空文件提前拒绝。真实入口/helper来自交付JAR，历史 DEVICE trust/完整registry和scope/release仅复制为本机夹具，门未伪造或替换。仅测试版 E9HostDeployment 的 private run 替成记录准确首argv后抛本机标记，首调用为原 data inode 查询；未调用 commands.run/启动SDKchild。每个实际监督器均自然pcClosed。原registry/失败报告前后字节未改。

UNKNOWN补强使用交付JAR的实际helper（verbose类来源证明），仅监督器引用保留接口为有限替身：CLOSE_AFTER受控异常，原UNKNOWN/returned=false，同一authority仍保留，dispatch0，close1，无第二close，重入拒绝。不声称永久UNKNOWN下真实custodian在线运行/最终归还实测；真实custodian逻辑原成员不变，其原close在途托管另有真实监督器证据。初轮同源另编UNKNOWN证据保留；补强原JVMexit0，事后类来源审计误纳运行时生成lambda，已只审现存raw排除lambda并通过，无JVM重跑/产品修补，原过程记录保留。

本轮 ADB/设备/install/媒体/真实once/实际scope=0；仅 evidence 下 local-test 夹具写入。APK/native构建0，旧绑定/source/信号套件0。

## 制品与冻结

新JAR：docs/coder/d1e13c/artifacts/e13c-host-tools.jar
299629 B / SHA256 9c36d04a728a5a5b6db04ab1ffbe3f5be051b84f249d8bdf868212ed03ef774c。

ZIP：docs/coder/D1-20261018-E13C-host.zip
449746 B / SHA256 1365dfa17cfaab28e9f4c2c8639bf204a95a0ca4949e837b6c77d3bfb0ced4d9。

外seal：docs/coder/d1e13c/evidence/e13c-freeze.json
31261 B / SHA256 14358fdb7e7900de669e76965c4ecce5b008eb8daea216b9abaa7f7891e45762。

140 ZIP条目/141不可变记录。默认verify、显式verify带独立seal SHA、help、pack-help均实际成功；139文件前后快照一致/writes0。包外回执 docs/coder/D1_E13C_FINAL_READONLY_VERIFICATION_V1.0.json。E11基础375/R1 65/E12 46/E13 367/E13A270/E13B118历史封印逐条只读复核保持；不相加冒唯一总数。

## 精确基础复用

E13A delivery三APK不复制重建：
app-debug.apk 10692238B SHA962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad；
app-debug-androidTest.apk 2770225B SHA83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13；
fixture-debug.apk 65609B SHA868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8。
主/测试 signer 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；fixture signer45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9。
旧host JAR a0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f仅来源基线，未来使用新C JAR。
E13B metadata三argv内容/manifest/ZIP/seal原字节复用；overlay seal e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e。仍产品v17/ACTIVATION/ABI1，accepted source15，产品batch D1-E13A-SOURCE-20261018。

## 新独立批次提案

release/candidate-binding.json、device-plan.json、new-scope-draft.json已同步新JAR/旧三APK/E13B metadata pins。sourceReview必须采用之后独立E13C完整复审报告，当前sourceReview/actualScope/release/config/once均未签发。保留固定basename e13a-activation-deployment.once，但未来必须新独立scope UUID目录：
D:/CodexProjects/VideoKit/docs/tester/D1_E13C_TABLET_EXECUTION/<NEW_SCOPE_UUID>/deployment/e13a-activation-deployment.once。
不回放旧已失败config/entry，不继承旧37/56余19。

必须fresh完整M1确认准确已接受v15 pair/UID/inode、fixture缺席、活动列表完整及当前守恒。15:59旧M1只证明该历史时点，本轮未读设备；未安装17仍是新批现场需再确认的前提。

成功路径48=部署入口1+children32+caseJava6+instrument6+metadata3；另提案2次仅部署前占用M1复查、至少30分钟间隔，最大50。文本2MiB不扩：1638400成功分配+131072占用复查=1769472，余327680。3metadata各原直接ADB64KiB/55s；无额外wrapper/STATUS/OP/CLEANUP/恢复/抢占/自动重试。环境失败停待负责人新范围，UNKNOWN原托管不回充预留。

说明见 docs/coder/D1_E13C_HOST_FIX_DELIVERY_V1.0.md，全部原输入日志/接线diff/来源/草案随包。214483B/7R7S/0reserved与107218前缀/oldCloseACK=false仅历史引用，无READY/R/S。全部P0/历史FAIL/UNKNOWN/许可/renderer/audio/Kit门保持。D1 NOT_PASSED / M0 NOT_STARTED。现保持新C候选及全部基础冻结，交独立复审。

