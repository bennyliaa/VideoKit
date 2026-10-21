# D1 E13A＋E13B_OVERLAY 平板正式测试需求 V1.0

日期：2026-10-18。来源：负责人VideoKit项目助理在本tester聊天中的正式设备派单，接受E13B报告SHA `b3f19c478dbae2218b0b776b6f85463d43c1df70c4e6baccdb1a2d63fc51c876`。本文件固化该派单，不是E13B静态报告自动授予设备许可。

真实用户已明确“以后使用平板测试，不需再重复授权，你可以直接使用。”另有已保存长期授权来源`docs/tester/D1_E11_DEVICE_AUTHORITY_20261018.json`；无需再次向用户索权。其他项目占用或占用不明先等待，不抢占。

## 唯一来源与交付

- 唯一平板HA1Q6WXR，TB138FC/API31/user0。源必须是已接受v15 ACTIVATION精确pair、原签名/UID10221/10222/data inode6972/4741；源不同停，不改pin。
- 目标E13A v17/ACTIVATION/ABI1，三APK只用`docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/`：app SHA `962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad`，test SHA `83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13`，fixture SHA `868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8`；host JAR SHA `a0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f`。
- 主签`5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；fixture不同签`45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9`且现场不存在才首次安装一次。
- metadata只用已审E13B完整M1/M2/M3 argv；seal `e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e`，ZIP `557327a5e7bd28cf73e21ccee3a9131e02a0495e1e303942500593e02f0bca96`，manifest `223e0d42a045fce01df8c4564945221276fbe78120fa7dad60641a10a2985af5`；不能用旧unsupported metadata。
- 先保存本次真实授权引用/不可变测试scope、生产精确schema scope/release/config、新固定`e13a-activation-deployment.once`路径及全部输入pins。原registry/head/catalog只读；原历史authorization/preparePlan只作已接受registry来源，不冒充本次新设备许可。生产CREATE_NEW once仅部署时创建，不预造已完成记录。

## 顺序与唯一执行

M1完整预检通过→生产单次app/test各install-r一次＋fixture首次安装一次→M2完整部署后核验→以下六项各一次、独立host→M3完整终态核验：

1. ordinarySenderCannotBindCodec
2. authorizedHostSourceReadAndClose
3. oldGenerationNeverOpensSource
4. twoConsumersHoldSourceUntilLastReturn
5. cancelLateOpenRetainsOriginalOwner
6. lateReadAndCloseFailureDoNotReleaseEarly

batch沿已审`D1-E13A-SOURCE-20261018`及原runner精确四字段选择。每host独立真实E9当前观察，不整类、不旧套件、不并发设备/Gradle。partial安装、FAIL、BLOCKED、PENDING、UNKNOWN或回执/资源证据缺失均停止依赖；不重发安装或方法，不卸载/clear/降级、kill/force-stop、重启、换UUID求PASS。

普通fixture核实际独立普通UID/不同签名、clearCallingIdentity、同目标授权host HELLO；kernel拒绝不等内部onTransact被触达。false/SE须同原connection一次必要unbind实际返回，原回调/owner全部归还才资源释放。

五source使用真实AsyncReadBridge/LeaseRegistry/SourceAdmission。当前代真open/read后旧task/epoch/instance零增量拒绝；双consumer首退不退整代；迟到open/read、取消响应、原返回分别计时。每ticket initial＋最多两次明确失败后重试，pending不并行。retired、consumers0、operations0、!closeFailed，原线程真返且executor实际terminated后才SourceReleased/清keeper。未知runner finish/onException和PC强custody不能结束，保原scope/case/task/generation/handle；不得第二close/换对象填ACK。不主动注入永久UNKNOWN/OOM/重启/信号。

## 总预算及有限环境等待

成功路径原48操作：部署Java entry1＋内部32、六Java entry6＋instrument child6、metadata3。负责人本次明确另给**至多2次M1只读占用复查，总上限50**；正常间隔约半小时，不能用于失败方法、安装或未知产品重试。消费累计不清零，无第51次或免费查询。生产原精确schema budget字符串仍是已审process48，附加2次仅由本次外层执行scope授权并记账，不改候选或放大生产门。

文本总2MiB不变：原分配1638400B＋余458752B；额外两次M1各≤64KiB从余量扣，余量327680B。部署内部32child/512KiB、deployment top32KiB、每case child64KiB/top80KiB、每metadata64KiB/55秒，重复保存top/child raw分别计。PC STATUS/OP/CLEANUP额外连接0。实际余量不足先停，不能自增次数/延时。

M1 ACTIVE73为环境等待，不抢占；21/22为未知/格式/过限阻断，不以exit0或部分M假成功。既有controller独占证据在M1前必要。主机只读解析兼容错误最多2次，仅对现存raw留痕修正，不改产品期待、不重发成功请求。

每方法30秒仅资格/观察，不覆盖原5000ms接口。4096B非媒体定义每source host内存准备，五份20KiB与实际payload分栏；计划6open/4224B read/7close，上限8/64KiB/16。媒体输出/READY/新R/S为0。

## 不变量、报告和停止

M1/M3完整旧ledger2271B、7R/7S、214483B、reserved0，旧107218B前缀、13metadata、三迁移记录、七产物stat及完整inventory保持；非零媒体payload不读、不重hash。原fence/oldCloseACK=false及历史signal/ordinary UNKNOWN不泛化。

集中输出`docs/tester/D1_E13A_E13B_TABLET_EXECUTION_REPORT_V1.0.md`及每方法原raw/独立审证/资源账、metadata完整pins，主动发负责人。限定实际范围才关闭；D1 NOT_PASSED/M0 NOT_STARTED。完成后不自动进入下一测试阶段。
