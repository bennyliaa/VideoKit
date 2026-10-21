# D1 E13E 生命周期集中修复完整交接 V1.0

2026-10-18。R01–R06/T01–T07按独立复审要求集中落实，完整冻结后提交，请安排tester独立审查；当前仍不设备/部署/处置。正式需求已保存 docs/milestones/D1_E13E_CODER_REQUIREMENTS_V1.0.md / D1_E13E_TESTER_REQUIREMENTS_V1.0.md，依据E13D复审SHA0955705e5d83784c5a5cdb76528b52836ae71850c12d65dfe20fb3b54dd8876e。

四交付文档：
1. docs/coder/D1_E13E_LIFECYCLE_DELIVERY_V1.0.md
2. docs/coder/D1_E13E_IMPLEMENTATION_CONTRACT_V1.0.md
3. docs/coder/D1_E13E_SELF_CHECK_REPORT_V1.0.md
4. docs/coder/D1_E13E_ORIGINAL_TASK_DISPOSITION_PLAN_V1.0.md

## 实际实现

R01：actual test@Before入观察前、E9阶段、原bind/HELLO/fixture RPC/callback/unbind入返及完成门，固定scope/method/原ownerID/UID/PID/thread/单调序号。单进程48事件、单条500ASCII、总24576B含换行/尾部；满额只dropped不改资源。实际平台日志在owner锁外；最后检查又将E9整段class monitor收窄为原ACTIVE原子登记，平台IO/日志均在该锁外，原准入未放宽。

R02：actual E13Instrumentation在onCreate先订阅原归还，再保存首个code/Parcel深拷贝result（16KiB上限），原异常/资格超时不洗掉，FD结果原引用UNKNOWN不finish。单一强持有非主finalizer，最多一次super.finish；不调用super.onException越过原门。callback/unbind/Probe/E9实际返事件驱动；source直接等待原registry notify、原caller.join和原runtime graceful termination，避免Future完成早于线程归还的漏通知。封新增依赖，允许原return；永久UNKNOWN仍pending。Android finalizer为daemon、强静态owner保留，未冒PC非daemon custodian/JVM退出证明；实际Android平台生命周期仍T07。

R03：actual SenderService强持同scope唯一TargetBinding；code1单次，code2即时原snapshot，必要code3等待该同原owner归还或已不可恢复UNKNOWN，wait释放owner monitor，不新bind/二unbind/新owner。附加读最多2、请求1024B/响应4096B，精确caller UID10221/scope/ownerID/fixtureUID/PID/kernel结果。并非两次早快照后遗忘：原ACK可跨响应资格保持原Binder调用在途；永久unbind异常回UNKNOWN而不重试；迟到只补原资源事实，保原失败/超时资格。

R04：actual E9PcSupervisor唯一原reader进入E13OperationArchive，原writer/每个E4Owned文件先登记，intent在Process前，实际PID独立持久化；8×4096队列、原raw既有cap、固定记录4096B、2秒写资格不取消原IO。55秒前后同operation连续raw，EOF/readerDone/naturalexit/pipe/archive归还分栏；磁盘失败保原owner，未返则原PCcustodian继续托管。actual observe_original.ps1外层先强持Process、两ReadAsync、bounded writer和metadata FileStreams，记录失败不丢局部owner/不开二reader/二close。持久receipt不证明自身close；console只在实际metadata close后给全资源状态。

R05：actual E13/E11 deploy与case公开入口共用固定HA1Q6WXR+app/test/fixture目录；非阻塞FileLock原子检查/CREATE_NEW claim/force/atomic pointer，扫描未决claim含部分条目，只有准确claim SHA的原返marker才可继续，新UUID/新once/PID不见不放行。当前E13GuardLocation.DISPOSITION_SHA=ABSENT，因此任何新scope在SDK child之前拒绝。未来独立审定行政记录的固定源码pin才可接受，外部终止必须originalJavaReturn=false，诊断另有disposition digest。此封锁约束受审新入口/各窗口共同路径，不声称能回溯拦截旧JAR或手工ADB，也不控制旧bytecode。

R06：新候选app v18/ACTIVATION/ABI1、fixture v2，原已装17未动。历史v17 pair仅作精确已安装byte前身，引用E13C部署报告，不把ordinary或全部source当验收PASS；旧E11/E13A once角色仍固定，新固定once e13e-lifecycle-deployment.once。actualScope/release/once/sourceReview及处置pin均未签发。

## 有限生产边界证据

- android-00518组：实际Probe/共同owner/Sender/runner；countDown-finally成功结果/原失败，完整Probe、fixture UNKNOWN/错身份/replay，原异常/FD结果未知，订阅前/中/检查后/worker退出前，永久UNKNOWN，同原晚ACK，stage cap，实际bind/HELLO/fixture/unbind未返。HELLO为生产E4CodecWire，扣住31秒后原返仍失败资格；其余扣住5.2秒。不能声称每个调用都保持55秒。
- actual-after-007：直接执行生产E13DeviceTests.@After、真实JUnit4.13.2 TestName/TestWatcher和实际runner，callback未返的原@After失败自动传至原结果，晚返唯一finish仍含失败。CALLBACK_PASS是直接成功结果完成门分支，不冒称实际@After在未返时通过。
- host-0047组（含观察/五archive正常异常/原55秒路径）：actual HostCase/Supervisor/Archive，本机原子JVM56秒自然退出，55秒先PENDING；早晚raw同operation逐字节存、同原pipe/archive真返后原custodian自然终结，未改成PASS。子进程模拟Android token仅主机解码门夹具。open/write/write在途/close UNKNOWN保持事实，不二close。
- host-006最终生产classes：GUARD、原source caller.join/runtime真实termination、原@Before观察在途、正常archive4组。最终JAR直接筛这些生产classes，不额外重编。
- public-004：两个新UUID case并发、E13及旧E11 deploy真实公开入口，actual Guard和entry；仅固定位置class影子到本机目录。全在监督器/SDK child之前PENDING拒绝，SDK/install0。
- outer-009：最终实际PS observer，已有stdout记录不可用时不覆盖，stderr/空stdout仍原drain，原Process/readers/pipes自然返；文件自身close在持久receipt为未证/null，console在metadata原close后才全返。
- r01-lock-010：实际最终E9观察，stage sink和平台原边界都不持E9CurrentObservation.class monitor，ACTIVE原登记/退回与无假grant同时核验。
- 随包保留16份实际已测class字节并与最终JAR逐字节核对，涵盖55秒原PC pipeline及公开入口/Guard，非仅同名source推断。

平台/Android UID、内核、Looper和base runner均明确有限JVM替身；monitor1.8.0非主约束以准确缓存源码+实际生产runner调用线程核，不称真实Android monitor执行。T07 NOT_RUN。未机械重跑旧绑定9组/source/历史signal/native套件，仅新增完成门所需原source等待直接分支。新处置/诊断/STATUS/ADB/媒体0，不读原主session/live ledger/当前进程，不联系其他项目。

## 开发期失败和构建来源

全部失败保留：host-001指针误入*.claim扫描后修active.pointer；stage总长换行/尾部漏计后收紧48×500；android-004 protocol-only旧汇总多列11个未执行组，原commands仅6，另存计数审计，最终汇总认真实执行。outer-008 Process本身自然返后console JSON审计发现VoidTaskResult杂讯，源头[void]抑制并于outer-009重验；不冒设备/资源PASS。

APK构建4尝试：main-001 Gradle缓存锁权限失败；env-002 Android源目录DSL错误，均在APK编译前。fixed-003修checks/com+原ACK后成功约80秒；最后发现R01旧整段class锁仍包含日志，于r01-004真实源码修改再成功约26秒（101tasks，6 executed/95 up-to-date），旧成功产物/输入保留，不是相同源码机械重建。最终167输入快照SHAcb54a7aa3ce2a23dbcc84b0a2349d4a24f573ae2837457436be651d8952deabb。host自检编译6轮是源修正/直接边界验证，最终JAR复用host-006，无再编译。

35 Maven/7 native原锁及库字节不变，fixture零第三方runtime；native未编译、下载0、许可NOT_GRANTED。SBOM/差异/原签名审证随包，私钥不分发。未混入平台替身或自检DEX，真实APK Dex与JAR成员来源均已查。

## 最终准确制品

统一使用 docs/coder/d1e13e/artifacts/D1-20261018-E13E/delivery-final/：
- app-debug.apk 10708622B，SHA5a196bb225ad5f3811fd8daa06769ebdfa41b1da410c1487c7b3a91f954e0045。
- app-debug-androidTest.apk 2774237B，SHA49808fb23aabb8e01b2b0a18f89b5d6aa5767b4365d9c5ee8e2fcafaafca8c97。
- fixture-debug.apk 78841B，SHA454f50865f6393c03d4b914aece10289cd1ae2f7c60b1c2512e860e089eb8eb5。
- e13e-host-tools.jar 318828B，SHA8d17b39c999d8b2e135af69927f1a2614672995ed5e39575d99e1bfcb5ab9223；182 production classes，151与旧E13A JAR字节相同、31新/变。test/fixture与fixed-003字节相同，最终app因R01变更有新SHA；旧delivery只开发历史，不选用。

app/test signer5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；fixture signer45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9。test自身versionCode按准确byte pair，不要求等于18。

ZIP docs/coder/D1-20261018-E13E-source.zip，24662899B，SHA633540d0d5ceea6c5e69e4ad41b3f9daa4bfc706276b479fedb207a71467fb3e。
外seal docs/coder/d1e13e/evidence/e13e-freeze.json，215351B，SHAa07b56f55733ecc775a21a8c5622b3cdd5b99480386b7ba627520e71e2c6f978。
1000准确ZIP成员/1001不可变记录，默认verify、显式带seal SHA verify、help及pack-help实际通过，1000文件前后快照一致/writes0。包外回执 docs/coder/D1_E13E_FINAL_READONLY_VERIFICATION_V1.0.json。E11基础375/R1 65/E12 46/E13 367/E13A270/E13B118/E13C141/E13D9旧封印逐条保持；tester旧35+6冻结切片也核保持，不加总冒唯一文件数。

## 原任务处置与下一准入

四号文档按既有最后身份给A自然保管/B外部终止两个待审分支：先fresh准确exe/启动时间/父子/argv/scope、Android package/UID/启动身份，不能凭历史PID；明确排除共享5037 ADB server、device adbd、system_server、其他app/serial/项目。原Android→原ADB/pipe→旧Java/custodian→原PS分别审，不笼统结束树。
旧已装17没有受审恢复入口，E13C retainAuthority(owner,null,owner)无cleanup handler；新包不能让旧对象写TERMINATED_WITHOUT_RETURN。若以后明确选择外部处置，只能在旧监督器之外行政记录同scope外部死亡/原JavaReturn=false/损失/仍未知对象；旧status仍PENDING或随死亡丢失，不造原pcClosed/finish/closeACK。旧内层最多64KiB原raw可能不可导出，外层缓存长度本轮未知。失败ps诊断无准确原PID/对象，独立LOST_DIAGNOSTIC_OWNER_UNKNOWN及行政隔离方案，不因主case收尾抵消、不退款。
解除封锁须完整原返或明确外部处置选择+独立诊断处置+fresh身份/预算/独立审查，未来源码固定disposition pin再审；单凭PID消失/文件/UUID均不放行。本轮A/B均未选择、零处置。

release/candidate-binding.json及device-plan-draft.json只有离线草案。51成功/53含2占用复查是全六方法profile的未批准上界（部署35child，因为fixture1已在场需3次额外准确核验），文本2MiB保持、archive磁盘另提3MiB，旧余额不继承。**不是T07单方法派单**：若后续决定T07，仅准确单方法还需另定稿更小outer scope/预算及v17 fixture1→18 fixture2 metadata，当前source pin ABSENT一切拒发，actualScope/release/once均null。现没有可执行新scope或自动六法续跑。

已按补充把 docs/MILESTONE_COORDINATION_V1.0.md、docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md顶部新增E13D/E13E最新安排，明确持续真机授权已存在，当前不设备因原任务未决；原历史段落保留。封包保存当时副本，未把滚动共享文档锁成旧候选不可变原件。

现在候选/旧基础全部冻结，待完整独立审查和负责人选择原任务处置/后续批次。D1 NOT_PASSED/M0 NOT_STARTED；214483/7R7S及107218前缀仅历史准入，未读case后账本。全部P0/历史FAIL/UNKNOWN、许可、renderer/audio/Kit门保持。

