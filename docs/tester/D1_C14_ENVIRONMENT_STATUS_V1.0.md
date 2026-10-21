# D1 C14 环境状态中间报告 V1.0

日期：2026-10-16；整理时间：12:40（+08:00）。候选D1-20261016-C14。**本文件仅记录有限预检和环境阻断，不是C14最终功能测试报告或验收结论。D1未通过，不进入M0。**

## 当前状态

| 对象 | 已记录状态 | 实际执行范围 |
| --- | --- | --- |
| 手机U4999DLBNRR89DOR / OPPO PDYM20 | App系统禁用，73项ENVIRONMENT_BLOCKED | 身份/包状态/空间只读查询、旧APK及可读cache备份；未更新、未启动C14方法 |
| 预期平板HA1Q6WXR / TB138FC | ADB未发现该serial，73项计划未执行 | 首项只读model查询即device not found；未取得本次实际平板身份/API/ABI/空间，不沿用历史值冒充现场核验 |
| 两历史CPU信号方法 | 每设备2项NOT_RUN_UNCHANGED_PLATFORM_LIMIT | 不属于73可调度项；未安装/预检或调用这些方法，不计PASS或手机环境阻断数 |

负责人更新为用户暂无法连接平板，现转环境等待；不再轮询设备或重复询问连接/授权。后续仅在收到可用环境通知并由负责人安排后继续保留的C14真机计划，不自动换候选或派下一批。

## 有限检查时间与身份

- 手机预检证据落盘时间：12:37:00（文件时间，非instrumentation执行时间）。已核serial、model=PDYM20、API31、arm64-v8a、页大小4096、user0；主App UID10262，测试包UID10263。/data当时可用98,502,076KiB。
- 手机73条环境阻断记录生成时间：12:37:24.189–12:37:24.190。此时间是结果登记，不是73次设备执行。
- 平板准备约12:37开始，第一次getprop ro.product.model返回`device 'HA1Q6WXR' not found`。随后一次有限devices列表确认只有U4999DLBNRR89DOR，邻近时钟记录12:37:38。没有进入平板备份、安装、fixture复制或测试；tablet证据目录为空。
- 12:38:18保存等待快照batch-status.json；本报告基于既有材料整理，没有再次调用ADB。最终协调状态为停止设备轮询、等待负责人安排。

手机原始包状态记录enabled=2，lastDisabledCaller=com.oplus.athena；environment.json为ENVIRONMENT_APP_DISABLED_MANUAL_ENABLE_REQUIRED。这里保留原始技术错误码，并非要求用户再次寻找“启用”按钮。此前用户已在正确设置页且没有该按钮的事实保持，不强启、不更改安全设置、不换包名、不卸载或清数据。

## 已完成的候选审核及备份

C14独立verify_c14.py --working-tree通过：342源文件、139证据文件、5产物；逐归档entry、源码和实际产物hash校验，并独占复制5产物。冻结时间12:33:42.094772。

| 对象 | SHA256 |
| --- | --- |
| freeze-summary | 880b38f3896df2f6bed2657d54c7fb8a954d3d05d8c730faf1b11278726e7155 |
| source ZIP | 69ca847d7c1947ae65eb3ed6e79d8ab50e21ac9463a1a686cdeda6cfef2d683d |
| 手机当前旧主APK（已备份、匹配C09） | 55e5bea436b2195517af72c991c9f36ede75e6da390c450bb65ae9ad2106a9f0 |
| 手机当前旧测试APK（已备份、匹配C09） | 2701b39a780174c76235db86262583204f0f9ac27b7ffd513ba32574a4a0c673 |
| 手机cache-before-c14.tar | 9e360a3db2d1a59cd4fb095c32b52060d1aaee7357e857ee7213ed673939c628 |

三个复制的Debug包apksigner核验通过，证书SHA256为5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；16个native包条目实际hash/ZIP布局/ELF静态对齐通过。只证明候选身份/静态准入，不能证明C14实际安装、配置、六帧接续或设备16KiB页运行。871条交付本机断言不计作本轮设备PASS。

手机旧包和缓存备份是从设备读取后保存到tester目录，未改设备输入或旧缓存。平板数据未读取/更新。未复制C14设备fixture、未建立新输出或capture、未动test_media或历史候选。未运行Gradle、安装release或修改产品/冻结源码。

## 明确保留的未执行项和门禁

73项计划保持：35 CPU、7 host、8 legacy、17 pipeline、6 encoder。手机全部环境阻断；平板全部未开始。尚无C14实际公开能力快照、有限configure尝试、候选关闭/选择、六真实帧/PTS/内容/EOF、新反例或host/legacy运行结论。

| 编译保留方法 | 每设备状态 |
| --- | --- |
| cpuSelfSigsegvSignalMustBeProven | NOT_RUN_UNCHANGED_PLATFORM_LIMIT |
| cpuSecondSlotAndHostSurviveFirstSelfCrash | NOT_RUN_UNCHANGED_PLATFORM_LIMIT |

退出采集路径未变，两项不为包身份变化重跑；原C13-T02的self系统signal0 FAIL、独立双槽系统11结果以及各自raw/trace/实际释放事实保持原报告，不改验收、不回填信号、不计新PASS。ordinary UNKNOWN及trace缺失继续OPEN。

执行前正式预算已在准备材料中保留：整批新task/journal上限48，全部新输出8MiB；pipeline24 journals/4MiB、单输出2MiB；每设备日志/文本32MiB；8份可达RGBA1179648B＋YUV55296B为静态保守预算。数量调整不更改字节上限、不批准超额或删除旧证据。当前无C14媒体输出，不据此称运行预算已实测通过。

## 在途与后续

本轮没有向任何设备派发C14 instrumentation、worker、编码或媒体任务；全部有限查询/备份命令均已返回，无本轮在途设备操作。没有为了本中间报告再查询ps/services；“无C14在途”不等于新采集到了设备所有进程为空的快照。

完整最终功能报告D1_C14_TEST_REPORT_V1.0.md尚未生成。既有证据位于D1_C14_EVIDENCE，包括freeze-check、admission-check、签名记录、phone/preflight/environment/results、旧包/cache备份、not-run-plan及batch-status。

已全文读取D1_R1_TESTER_REQUIREMENTS_V1.0.md：等待完整R1正式交接后，仅按SUPPORTED/CONTRADICTED/MISSING和具体来源独立审材料，不改历史FAIL/P0、不自行批准架构变更或把材料审核当D1通过。当前不设备、不Gradle、不改源码。以本报告和任务完成事件交付负责人，不重试跨窗口通知。
