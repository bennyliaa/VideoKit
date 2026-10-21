E13A集中P1/P2修复完整交付，已冻结并完成真实默认/显式只读verify，请整包交tester独立复审。当前不ADB/设备/真实媒体/实际scope或once，D1 NOT_PASSED / M0 NOT_STARTED。

正式双需求：
D:/CodexProjects/VideoKit/docs/milestones/D1_E13A_CODER_REQUIREMENTS_V1.0.md
D:/CodexProjects/VideoKit/docs/milestones/D1_E13A_TESTER_REQUIREMENTS_V1.0.md

完整四文档（docs/coder）：
D1_E13A_DELIVERY_V1.0.md
D1_E13A_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md
D1_E13A_REMAINING_GATE_REVIEW_V1.0.md
D1_E13A_DEVICE_EXECUTION_APPENDIX_V1.0.md

候选D1-20261018-E13A / v17 / ACTIVATION / ABI1，实际已接受升级源仍精确v15。E13 v16本批未安装，不把它当设备来源。batch改为D1-E13A-SOURCE-20261018，独立新固定e13a-activation-deployment.once；实际scope/release/once均未签发，release/candidate-binding和device-plan仍REVIEW_ONLY/DRAFT。

P1：
本机SDK Context.java4206–4215、ContextImpl的先getServiceDispatcher后系统bind、unbind先forget的顺序及LoadedApk.doForget/排队回调规则已读，准确来源/hash/片段在evidence/sdk-binding-contract.json。只称SDK36.1静态契约，不冒API31实测。
实际SenderService和E13PermissionProbe共用小型生产E13BindingOwner，原ServiceConnection不换；keeper在bind前登记。bind调用进入、正常true/false、SE/其他异常已实际返回、回调在途、原unbind进入/正常返回/抛出分别记账。false和SE同样无条件对原连接执行一次必要unbind/forget；不再用accepted决定跳过。bind在途时先保管，原调用返回后才可续同原解绑。解绑一旦进入，不重bind、不换对象、不重复unbind；异常已返不等成功ACK，未证仍保同owner。回调尚在途即使unbind返也不归还，关闭后的迟到回调不接纳endpoint。
fixture结果resourcesReturned只由原owner实际门计算，主端还保原fixture Binder/远端归还，unknown保host/fixture/connection/runner/PC门；ordinary原输出增加targetBinding、authorizedClient、fixtureClient三份binding状态。kernel拒绝与归还分栏，无endpoint依旧internalTransactAttempted=false，不称内部onTransact跨UID实测。

直接生产共同owner九组/72断言通过，原输入/argv/stdout/stderr/exit在evidence/local-checks/binding-001：
FALSE、SECURITY、OTHER_EXCEPTION、TRUE_CALLBACK、BIND_IN_FLIGHT、UNBIND_IN_FLIGHT、CALLBACK_IN_FLIGHT、LATE_CALLBACK、UNBIND_EXCEPTION。
其中false/SE原连接unbind一次成功；原解绑在途不可归还且重复close不第二解绑；回调在途保管；解绑异常分支预期原keeper retained/resourcesReturned=false，不以JVM自然结束冒Android关闭ACK。只替换平台Context调用/调度，生产owner本身真实执行；这些不是Android Binder/dispatcher运行PASS。两处真实APK的共同owner/unbindSucceeded/bindingState DEX接线另已查。

P2：
tools/package_delivery.py默认就是严格只读verify；显式verify同入口；--help/pack --help在参数解析先返回。只有明确pack才加载_write_package.py，后者自己也先检查pack参数。verify只读metadata/hash/完整ZIP/JAR及旧seal，不复制/写证据/构建/运行候选或设备。可用：
Python -B tools/package_delivery.py
Python -B tools/package_delivery.py verify --seal-sha 24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6
写封装仅pack，冻结后不重pack。
前冻结default/verify/help/pack-help共197份候选文件前后相同；原E13 seal/367行全匹配，没有重执行旧误用脚本。旧既有JAR x异常只记打包误调用，非功能FAIL。最终封印后又实际执行默认+带独立seal pin的verify，两者exit0、PASS_E13A_STRICT_READONLY_VERIFY/writes0；候选目录264份文件前后完全一致，全部270不可变行/完整ZIP成员/JAR成员与旧封印由只读入口校验。回执在D1_E13A_FINAL_READONLY_VERIFICATION_V1.0.json，外部写回执与verify本身无写明确分开。

构建与依赖：
一次主集中离线app/test/fixture main-001成功，约1m7s/101任务，E13A repair0。最终输入139项SHA2c71c4e24e28abff2c6cd03ad30e8a638e7a39b95c8b3eb91348c213df4b939c。主锁精确35Maven，7native与继承源/最终APK库逐字节相同；fixture空runtime依赖，沿用不同原Debug signer；无下载/native重建。
原AsyncReadBridge/LeaseRegistry/SourceGroup/SourceAdmission/CpuTaskClient/原source场景与E4Session字节继承，未跑未变source/旧19/32等套件、native或信号。真实六方法范围保留，ordinary权限owner修正。

最终唯一制品：docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/
app-debug.apk 10692238B SHA962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad
app-debug-androidTest.apk 2770225B SHA83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13
fixture-debug.apk 65609B SHA868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8
app/test原signer5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f
fixture signer45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9
e13a-host-tools.jar 298510B SHAa0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f，172production classes，直接取binding-001实际编译类，不含检查类/不额外重编。私钥只本机保留不归档，构建输入留hash；重建需原签名环境或新candidate/pins，不能替换当前APK。

M1/M2/M3精确计划已落地：
release/metadata/expected-baseline.json
release/metadata/M1_PRE_DEPLOY.sh + .argv.json
release/metadata/M2_POST_DEPLOY_PRE_CASE.sh + .argv.json
release/metadata/M3_AFTER_SIX.sh + .argv.json
release/metadata/three-client-manifest.json
采用tester原three-metadata-field-plan及实际最后raw的34stat/18control pins，缺失新四产物stat只取已有acceptedStat、不造inode；更新到新v17 pair及fixture实际hash。70/18/71个完整记录，含标记最坏53512/27588/56360B，均≤单65536B，总仍保留196608B。每份1原直接受管ADB shell client，无额外PC Java/Python wrapper，无push脚本/探路查询。非零媒体只stat；控制18文件完整base64/匹配pins，完整2271B ledger保持e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649，旧已结算operation.pending.N2-e5-aborted按原pin保留不误删。APK hash只用于静态制品身份。控制/字段缺失、命令失败/过限/未知输出都须BLOCKED，不凭exit0或截断填完整。
本机Git Bash -n读取三脚本及嵌套body共29条语法检查通过，无脚本内容/ADB执行。初始MSYS沙箱对象权限和Windows -c传参引用检查问题留说明，改用精确UTF-8文件-n，非Android运行失败。
48总操作不变：部署entry1+内部32+六Java6+六instrument6+metadata3。2MiB分配不变1638400B+余458752B，top/child重复raw分别计，STATUS/OP/CLEANUP额外连接0。需要既有controller占用证据，其他项目在用等待；实际API31字段或预算不符提前集中报缺口，不补wrapper/查询/次数。正式scope仍须独立审查采纳这些精确脚本pins，当前actualScope=null。

冻结与真实只读验证：
docs/coder/D1-20261018-E13A-source.zip
23947746B SHA45765142b21ca193d1b5ca26feb2e1023e5151e95303fd9ba5b167c1cc37e48e
docs/coder/d1e13a/evidence/e13a-freeze.json
56667B SHA24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6
ZIP269项、封印270行。原E13 367、E12 46、E11基础375/R1 65及四seal全不变（分层数不相加作唯一文件数）。源码/diff/SDK主证据/自检原输入日志/三APK/JAR/SBOM/metadata精确argv/实际verify回执路径齐全。

原214483B/7R7S/0reserved、旧107218前缀/产物/fence/oldCloseACKfalse只引用接受时点，不在线重读/写账；当前媒体输出/READY/新R/S=0。E11限定PASS，C13系统0严格FAIL/外部raw11/另方法11、C14 NOT_RUN/ordinary UNKNOWN不变。renderer/audio/Kit沿E13已审SUPPORTED_DESIGN_ONLY，声音显示NOT_RUN/合法压缩音频PCM BLOCKED，独立AAR/Fake/Flutter/全部P0/许可/长期门不因修复自动关闭。

请完整静态复审后正式派实测；当前保持冻结，不追加构建/设备/修补。常规真机长授权有效无需再问，他项目占用稍后试。
