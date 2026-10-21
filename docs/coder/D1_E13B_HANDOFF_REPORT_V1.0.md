# D1 E13B 完整交接报告 V1.0

日期：2026-10-18。提交负责人 VideoKit项目助理，请安排 tester 独立审查元数据语义及实际 argv；本次没有申请或启动真机执行。

## 范围与结果

E13A-F01/P1 的三处无效 instrumentation 命令改为无包过滤的 dumpsys activity processes。纯 shell 解析同一完整返回流，核验首行、All known processes、OOM阶段、末尾 mForceBackgroundCheck 和原命令退出码；诊断即使 exit 0、缺段、未知格式、截断、超限及非零原返回均阻断。活动列表保留全部项目、全部跨行内容及 FINISHED 但仍在列表的对象。有效 ACTIVE 输出完整证据后 exit 73 / ENVIRONMENT_WAIT，停止后续步骤；无效/过限分别 exit 21/22。不得抢占、免费轮询或把缺少标题判为空闲。IDLE 仅代表本次 instrumentation 快照。

最终解析器没有 awk 依赖；三处原有小字段筛选作同义替换。产品源码、绑定修复、APK/JAR、native、SDK与依赖版本均未改动。

## 本机验证与预算

20 个最终 shell 语义用例通过，其中 4 份为历史厂商原始空闲输出，其余活动/错误情形为明确标识的本机构造夹具。32 个脚本及嵌套语法检查、4 个精确 collector 替身检查通过。活动完整块逐字节验证。没有执行真实 dumpsys/ADB、remote 脚本、媒体、旧绑定九组/source/native/产品用例，也没有产品构建。

M1/M2/M3 的 shell 与实际嵌入 argv 一致，每份仅一条真实 processes 查询。记录数 70/18/71，输出上界 53512/27588/56360 B；Windows UTF16 命令行含 NUL 23993/9899/24460。仍是三次直接原 ADB 客户端，各 64KiB/55s，总计 48 PC 操作、2MiB 原预算不变，无额外 wrapper/query。ACTIVE 产生的部分 M 不能算成功完整 M，后续重查必须正式计入预算。

## 冻结与只读验证

覆盖包：docs/coder/D1-20261018-E13B-metadata.zip，1202556 B，SHA256 557327a5e7bd28cf73e21ccee3a9131e02a0495e1e303942500593e02f0bca96。
外部封印：docs/coder/d1e13b/evidence/e13b-freeze.json，27051 B，SHA256 e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e。
117 ZIP 条目、118 不可变记录。实际默认 verify、显式 verify、help、pack-help 均成功；176 文件前后快照一致，writes=0。回执：docs/coder/D1_E13B_FINAL_READONLY_VERIFICATION_V1.0.json。
E11基础375、E11R1 65、E12 46、E13 367、E13A 270 条历史封印记录均核验不变（存在重叠，不相加冒充唯一文件数）。

## 精确复用的 E13A 产物

全部位于 docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/，本覆盖包不复制或重建：

- app-debug.apk：10692238 B，SHA256 962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad。
- app-debug-androidTest.apk：2770225 B，SHA256 83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13。
- fixture-debug.apk：65609 B，SHA256 868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8。
- e13a-host-tools.jar：298510 B，SHA256 a0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f，172 个 production classes。

主/测试签名 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；fixture 签名 45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9。
E13A source ZIP：23947746 B，SHA256 45765142b21ca193d1b5ca26feb2e1023e5151e95303fd9ba5b167c1cc37e48e；E13A seal：56667 B，SHA256 24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6。
仍为产品 v17 / ACTIVATION / ABI1、已接受 source v15、批次 D1-E13A-SOURCE-20261018；各 scope 草案不改。actualScope/release/once 均未签发，once 名称仍 e13a-activation-deployment.once。

## 审查入口与边界

正式需求：docs/milestones/D1_E13B_CODER_REQUIREMENTS_V1.0.md、D1_E13B_TESTER_REQUIREMENTS_V1.0.md。
说明：docs/coder/D1_E13B_METADATA_DELIVERY_V1.0.md、D1_E13B_METADATA_CONTRACT_V1.0.md、D1_E13B_DEVICE_OVERLAY_V1.0.md。
工具、3 份完整 argv、期待记录、精确差分、固定 AOSP12 源码依据、厂商原始输出 pins、全部本机 stdout/stderr/exit 及封印均在 docs/coder/d1e13b/。开发期 AWK 原型明确排除冻结覆盖包，最终只认 shell 证据。

214483 B / 7R7S / 0reserved 及旧107218前缀仅为接受时点历史引用，本轮没有在线读写账本、输出/READY/R/S 或设备状态。oldCloseACK=false、全部 P0、历史 FAIL/UNKNOWN、许可、renderer/audio/Kit 剩余门均保持。D1 NOT_PASSED，M0 NOT_STARTED。请先独立审查；通过后由负责人另行正式派发原六方法设备范围。

