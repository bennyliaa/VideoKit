# D1 E13A 完整修复交付 V1.0

日期：2026-10-18。候选D1-20261018-E13A，v17/ACTIVATION/ABI1。修复E13-F01/P1、E13-F02/P2；当前交独立tester整包静态复审。六方法Android全部NOT_RUN，没有ADB/真实媒体/实际新scope/release/once，D1 NOT_PASSED / M0 NOT_STARTED。

## 改动及验证

P1：两处实际Android绑定适配器共同使用E13BindingOwner。false和SecurityException也对同一原ServiceConnection执行一次必要unbind/forget。bind进入/正常或异常实际返回、回调在途、原unbind进入/返回/异常独立记账；一次进入后不重复unbind，未知保原owner并阻止真实runner/PC结束。kernel拒绝与resourcesReturned分栏，普通负例仍未取得codec endpoint，不称内部onTransact跨UID实测。原日志增加target/两个client的真实binding状态。

九个有限分支直接执行生产共同owner，平台Context调用/回调调度替身：FALSE、SECURITY、OTHER_EXCEPTION、TRUE_CALLBACK、BIND_IN_FLIGHT、UNBIND_IN_FLIGHT、CALLBACK_IN_FLIGHT、LATE_CALLBACK、UNBIND_EXCEPTION。解绑异常预期保原keeper，未用第二次unbind伪造ACK；替身没有Android dispatcher，JVM自然结束不是Android关闭证据。原source keeper/AsyncReadBridge/LeaseRegistry/SourceAdmission/CpuTaskClient/source场景字节继承，无旧source/native/历史signal套件重跑。

P2：package_delivery.py默认和verify均严格只读，help参数先返回；唯一显式pack才加载写封装器，写封装器本身也先检查pack。前冻结default/verify/help/pack-help比较197份候选文件前后全相同，原E13 seal/367行全字节未变；没再执行旧误用入口，也不把既有JAR x误用异常算产品FAIL。最终冻结后又实际执行默认和带独立seal pin的verify，并比较全文件快照，结果在包外最终回执。只读核验只读metadata/hash/ZIP/JAR，不跑候选、自检、构建、设备或媒体。

一次主离线集中app/test/fixture构建main-001成功，约1m7s、101任务，0修正构建。最终输入139项SHA2c71c4e24e28abff2c6cd03ad30e8a638e7a39b95c8b3eb91348c213df4b939c；主锁仍35Maven、7native与原源/实际APK相同，fixture空runtime锁、不同原Debug signer不变，未下载/重建native。SDK签名/manifest/ZIP静态检查和两APK实际BindingOwner DEX接线检查通过。静态16KiB对齐不是设备运行证据。

M1/M2/M3采用tester既有字段计划：34固定stat、18control pins/2271B原ledger/固定inventory，并更新v17 pair/fixture实际hash。三个精确完整argv及remote脚本在release/metadata；每份一个直接原ADB客户端，无预算外Java/Python wrapper。70/18/71个记录，含标记的上界53512/27588/56360B，均在单64KiB/总196608B原分配内；原48process/2MiB不增。29个本机Git Bash -n文件语法检查通过，未执行脚本内容；早期本机MSYS沙箱/Windows -c引用检查问题另记，不冒设备FAIL或API31字段成功。

## 最终制品

- app：docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/app-debug.apk；10692238B；SHA256 962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad；signer 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f
- test：docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/app-debug-androidTest.apk；2770225B；SHA256 83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13；signer 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f
- fixture：docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/fixture-debug.apk；65609B；SHA256 868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8；signer 45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9
- host JAR：docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/e13a-host-tools.jar；298510B；SHA256 a0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f；172个production class，来自binding-001实际编译，没有检查类。
- 本机binding：9组、72个断言；完整原输入/argv/stdout/stderr/exit随包。不是设备用例通过数。

四文档为DELIVERY、ARCHITECTURE_AND_THREAT_BOUNDARY、REMAINING_GATE_REVIEW、DEVICE_EXECUTION_APPENDIX；SDK主证据/精确diff/原输入日志/三APK与JAR/空fixture锁/SBOM/metadata精确计划随包。fixture私钥只本机保管，不归档；重建需相应签名环境或新candidate/pins。源接受仍是v15，v16未安装；新target17/batchE13A/e13a固定once，未签发实际scope/许可。

严格只读核验用Python -B tools/package_delivery.py（默认）或同命令verify --seal-sha 独立SHA；帮助--help。写封装只能pack，冻结后不重pack。外seal不自哈希，ZIP与全部不可变字节/JAR及原E11/E12/E13封印由真正只读入口核验；最终回执是包外记录。

原接受214483B/7R7S/0reserved、107218B前缀/旧产物/fence/oldCloseACK=false只引用E11报告时点，未在线重读/写账，媒体输出/READY/新R/S=0。E11有限实机PASS、C13系统0严格FAIL/外部raw11/另方法11、C14 NOT_RUN/ordinary UNKNOWN保持。renderer/audio/source/Kit继续E13已审SUPPORTED_DESIGN_ONLY，声音显示NOT_RUN、合法压缩音频→PCM BLOCKED，独立AAR/Fake/Flutter/全部P0/许可/长期门未过。

请tester一次完整静态复审后，由负责人另行正式设备批次；设备长期授权和他项目占用稍后试有效，当前不自行实测或扩修。若metadata实际字段/命令/输出或48预算不足，先BLOCKED交负责人，不能增加wrapper/查询/截断填成功。
