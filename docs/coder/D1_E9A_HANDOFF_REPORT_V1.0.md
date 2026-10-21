# D1 E9A 完整集中修复交付报告 V1.0

2026-10-18。依据E9独立复审2P1+2P2正式派单，E9A已集中实现、自检、一次offline prepare双APK构建、四文档、源码差异/来源/SBOM/原始证据/生产PC工具JAR和源码ZIP，封存与只读核验完成。请一次交tester整包独立静态复审。旧E9 NEEDS_FIX/NOT_SUPPORTED_FOR_DEVICE_MIGRATION未由coder自行解除；当前不派设备/写迁移/activation。

修复对应：
- F01/P1：实际launcher无-w，am instrument -r非等待；原launcherclient结束不等actor结束。完整transport走actual custom runner DUMP保护ordered broadcast，POLL实际STATUS，不再靠watcher/sendStatus。首次不用猜state，缺失STATUS保守扣额；显式READ_ONLY_IDENTITY可查询和身份only安全收尾，无reserve/COMMIT/final资格。
- F02/P1：生产E9PcSupervisor原ProcessBuilder/start/wait、3pipe/reader/decoder和所有console/部署退出路径统一保留。非daemon原custodian+静态强根持续持原manager/registry/remote/Process。EOF/异常的pcIsolationAck是同JVM原custodian实际接管，不让JVM自行退出；本机状态与受限cleanup保持原handle/PID/operation身份。remote必须类型化原正常finish/终止，不能由launcher退出或readerEOF替代。生产无kill/cancel；原UNKNOWN不重关。
- F03/P2：实际每个控制原响应5秒绝对资格，覆盖start、process、pipe、wait、帧解码及身份/模式/seq校验；不共享55s/不加1s join/不重置，迟到不改PASS。已发EXECUTE/ACK在真实registry命令账只一次，未知不能换seq重发；8/STATUS3和原两phase10秒保持。
- F04/P2：observe入口即撤销旧grant并取epoch，含used等早拒；旧在途调用不得晚发grant。同步准入/发布，Runtime在authority/context异常前也撤销；实际成功→重复拒绝→requireCurrent拒绝及并发交错断言通过。

最终身份：
- 工程 D:/CodexProjects/VideoKit/docs/coder/d1e9a，version12 / D1-E9A-PREPARE。
- ZIP 24710914 B，SHA256 378b2ceec7ac5d47e0f63710efde0d590a33adea6316219e554f193de7b37acb，D:/CodexProjects/VideoKit/docs/coder/D1-20261018-E9A-source.zip
- 外置seal 159567 B，SHA256 edfb13109b1cc5103ed348f3ce757165597fe16fe8320a1426afd4cd9651fdfb，D:/CodexProjects/VideoKit/docs/coder/d1e9a/evidence/e9a-freeze.json
- ZIP 732项（含source-manifest），只读核733 immutable项（含ZIP，不含seal自身）。旧E9全部1045项、E7A200项、E8A42项均一致。
- 外部只读回执 1599 B，SHA256 4c5b88f896f683478b80fd5f21fd7473bed174c3abe3462487b36656a89ab8d3，D:\CodexProjects\VideoKit\docs\coder\D1_E9A_READONLY_VERIFICATION_V1.0.json
- 最终APK构建输入SHA256 06fc16bd7e27f766d30fc2b57810c0952df56aaf59011c4d93b0f3b0aee87d0b（163项）。
- app-debug 10643010 B，SHA256 1edb820faea79cf87d261555adbd397f32c6796447ace127bd39cb756e10c841，D:/CodexProjects/VideoKit/docs/coder/d1e9a/artifacts/D1-20261018-E9A/final/app-debug.apk
- androidTest 2749733 B，SHA256 2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b，D:/CodexProjects/VideoKit/docs/coder/d1e9a/artifacts/D1-20261018-E9A/final/app-debug-androidTest.apk
- 原证书SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。
- 生产host JAR 255014 B，SHA256 709fa796ed59ce6394b25f75bc69391099f7a4d398cafbd79cef91ef257d17e4，D:/CodexProjects/VideoKit/docs/coder/d1e9a/artifacts/D1-20261018-E9A/final/e9a-host-tools.jar；155生产class，不含测试类。final007至final008有148个共享/生命周期class字节一致；来源/默认inspect日志在host-binary-provenance.json。

验证口径：19组映射，19次集中+2次末段纯host定向，共21次最终调用，279断言（199+6=205新增边界，74共享实际夹具不变量）。真实本机manager JVM和Java child、ProcessBuilder/pipe/reader/console/原custodian/生产查询客户端；平台Hook只注入IO/时延，没复制判定模型。旧32全套/native未重跑；共享Fixture只建合成元数据并调生产对象，不计旧历史PASS。额外6个实际新Gradle Android公共入口SDK桩拒绝+1个Runtime失败撤销旧grant序列通过。真实Android完整approved-session依然NOT_RUN。

原始argv在各attempt/commands.json，输入/source before快照、stdout/stderr、主结束边界、实际child PID/原holder状态均可核。main001沙箱禁止Socket.connect导致失败；原监督者继续存在，失败合成夹具的清理单独记录No closeACK。正常本机权限后通过。004/005夹具把Windows conhost.exe误算为业务child，保留原失败并修正仅夹具识别。最终CLOSE_UNKNOWN通过的事实是UNKNOWN/allReturned=false、原JVM不退出且状态可查；有限观察后controller清理仅合成夹具，原holder未改CLOSED、无E9_PC_CLOSED、无生产closeACK。不要把清理简写为UNKNOWN关闭成功。只读残留核验，本轮合成Java夹具残留0。

由于actual Android runner transport改变，一次集中offline主双APKmain001通过，无APK repair；后续帧语义验证为纯PC差异，APK源码/输入不变，针对性补TRANSPORT/DECODE_DEADLINE并封存最终JAR，没有再构建APK。签名/manifest/DEX/zipalign16审计通过。7个native和35依赖、原native源/配置/六帧完整EOF1000us等继承不变，无下载/native编译或许可清权变化。

四文档：
- D:/CodexProjects/VideoKit/docs/coder/D1_E9A_DELIVERY_V1.0.md
- D:/CodexProjects/VideoKit/docs/coder/D1_E9A_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md
- D:/CodexProjects/VideoKit/docs/coder/D1_E9A_REMAINING_GATE_REVIEW_V1.0.md
- D:/CodexProjects/VideoKit/docs/coder/D1_E9A_DEVICE_EXECUTION_APPENDIX_V1.0.md

重点证据：d1e9a/evidence/targeted-check-results.json、test-mapping.csv、selfcheck-attempts/final-pc-007及frame-validation-008、原先所有失败attempt；final-static-review.json、source-derivation.json/diffs、host-binary-provenance.json、public-android-entry-check.json、final-build-inputs.json、build-results.json/build-attempts、apk-audit.json、sbom.json/sbom-difference.json、native-and-strict-logic-inheritance.json、external-readonly-verification.json。最终状态/控制/收尾方法及精确CLI见设备附录。host默认三个入口仅inspect；原已审配置pin只是同scope收尾绑定，不生成新密钥/远端根，也不宣称抵御有配置/签名/管理员权的主动攻击者。

当前ADB/安装/设备/真实媒体/写迁移/实际approval token、H_actor/catalog/activation均NOT_RUN或NOT_CREATED。永久内核start/close/监听UNKNOWN、原Androidraw/dup/dirsync/真正boot/start/系统finish及全部调度排列未穷举，表格如实NOT_RUN。没有新ABORT/清账/换budget；原107218/三R三S/reserved0、N2 S0=0B、fence/输出档案与oldCloseACKfalse继承保持，没重读实际设备导出件作新声明。

PREPARE仍无catalog authority，尺寸4文件8448B/3目录、外部20文件155648B/≤192KiB metadata+1MiB日志、catalog16KiB≤24KiB、2actor/各8控制STATUS3、两phase各10秒/48仅新增Android owner均保持。新增PC本机监督记录上界不扩Android框架。D1未过/M0未启/E6B-OBS-F01长期准入OPEN；独立Kit/Flutter及全部框架/许可P0保持。请集中复审再派下一批，当前不启动实际执行。
