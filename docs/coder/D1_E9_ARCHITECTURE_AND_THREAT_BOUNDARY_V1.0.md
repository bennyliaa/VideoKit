# D1 E9 架构与威胁边界 V1.0

2026-10-18。基线为冻结E7A，设计依据为E8A四文档和独立静态接受报告。本实现不改变原资源框架计数、时限或native协议；48仅是新增owner集合上界。主要变更及逐文件来源见evidence/source-derivation.json和diffs。

## 权威与无环顺序

受信本机操作员保管的批准plan/pin/授权引用/独立审查引用 → prepare双APK完整SHA+原签名+sourceReview → actor预写身份实际返回 → 外部BOUND reserve实际force/close/readback → actor commit实际操作与原返回 → 精确回执外部归档 → ACK_FINISH → 原instrumentation正常finish与OS事实 → 最多一次恢复actor重验证 → 最终events head H_actor → final catalog → checkpoint → seal → 未来activation包固定同catalog/head → 单独activation-release记录实际APK SHA。

events仅引用已有较早证据，不引用catalog/checkpoint/seal/未来APK。seal本身及ZIP seal都不对自己求hash。本批真实链未执行；SYNTHETIC_LOCAL测试链不能成为DEVICE_HA1Q6WXR的发布输入。E9Phase只读取编译固定release authority，不接受device hash、instrumentation参数或外部BOOL作为激活开关。prepare无论文件/回执多完整都不激活。

## 资源与收尾

E9MigrationRun构造即开始identity资格钟；bindAndReserve接受时即保留commit和资格钟，worker启动不会重置。FD尚EMPTY但操作已保留依然未返。核心状态、seq、8控制/STATUS3、ACK hash及finish仅一次由同一对象管理。10秒到界、控制异常或原资源UNKNOWN形成永久PENDING；晚返仅更新资源已返回状态。没有Future.cancel、强杀或把锁重获当资源归还。

E9OwnedFiles在open之前登记IO-free mutable handle；Android raw/dup/stream/lock均保留原对象，逐一unlock/close，不重试未知close。数据holder先返回，最后guards返回。错误保留首因与cleanup suppressed。身份FD也属原identity集合。受管Instrumentation用DUMP权限动态广播入口，限定case/batch/mode/handle/seq/state，不接FD；onStart返回不会触发JUnit自动结束，平台finish仅经过精确ACK与真实safe边界。失败发生在任何自身IO之前的拒绝可安全终止，但不形成迁移成功authority。

迁移只写三层新控制目录：legacy-acceptance/M/actors，以及0001.intent、可选0002.intent、n2-v2.acceptance、n2-v2.commit。单文件上界2048/2048/4096/256，总8448B；只CREATE_NEW，已有完整对象逐一精确重验，截断/错内容/额外项隔离，不覆盖或删除。每个原目录/文件/完整账本保持检查，未追加业务R/S。

actor2只有两种前序处分：真实晚返非合格且正常finish，或精确原boot/PID/start代次终止且SELF_NO_FD_TRANSFER。前者保留旧PENDING；后者旧Java返回继续ABSENT，不能写成CLOSED。actor2使用新attempt/handle、真实身份和独立资格，逐一返回自身原资源。缺外部旧身份/回执不重建authority，actor2未知没有actor3。

## 每host与产品边界

当前host使用固定release catalog，仅退休legacy V1 PID4869的历史查询例外；不豁免当前host、当前actor或当前资源。实际持原owner/lease guards，匹配UID/dev/inode/fence，核13项原档案元数据、N2 0B输出、完整合法链及固定1011B已接受前缀、合法后续R/S与预算、无active pending，再核精确控制inventory和摘要。只有本host原force/fsync/close全部返回才创建liveproof；失败先失效旧grant并保留未知owner，不复用旧host证明。

prepare入口在Session/CpuTaskClient构造之前、CPU source/验证、任务initialize、预算reserve、codec BEGIN/debug、CPU START/debug及encoder create上应用共享phase。原低层guard/close primitive仍供迁移及cleanup，不把“通用primitive存在”当公开产品绕过入口。旧E5观察/恢复及E7A debug入口明确禁用。activation的可写迁移入口在requireMigrationPair第一步拒绝；源码共用，不需要第二套迁移模型。

## PC工具与成本

外部registry固定20种文件、155648B元数据cap，同时不超过192KiB；原日志额外合计1MiB。catalog实现上限16KiB，比合同24KiB更窄。固定2actor，各8控制/STATUS3。任何PC原open/force/close不确定导致store不可继续。日志/进程超时保留原对象，不自动kill/retry。PC实际dispatch只发目标HA1Q6WXR的install-r app/test，核完整候选SHA/审核角色ABI/原证书/已装精确pair/UID/版本/无相关进程，并在dispatch前再次仅比对本次候选SHA，安装后复核。CLI默认inspect，activation CLI与原迁移阶段分开，使用同一registry/catalog/gate，既有release不重试。

本机批准配置和hash由受信操作员/负责人保管，本工具不是远端签名服务器，也没有新密钥或新硬件根。拥有同签名重打包、adb/管理员权限或可任意改本机registry/编译固定常量的人可以绕过合作部署流程；不宣称Android绝对阻止高version旧码。真实旧E7A reader会忽略新marker的限制已由真实旧类证明。外部撤销json也不能追溯修改旧程序，必须部署源审查兼容版本。

同UID主动并发替换父目录、恶意native/内核、root或恶意operator不在当前静态合作模型保证内；NOFOLLOW、lstat/fstat及当前guards仍用于正常竞态/误配失败关闭。设备fsync/锁/boot source/日志来源的真实有效性未通过本地替身证明。Kit独立于Flutter、帧不经Dart、六帧/full EOF/1000us、原预算身份和全部许可P0均保持；当前仍非正式交付。
