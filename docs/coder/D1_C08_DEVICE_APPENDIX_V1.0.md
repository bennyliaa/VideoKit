# C08 设备验证说明：不准派测

2026-10-05。状态 NOT_READY / NOT_RUN。没有C08可安装CPU APK，也没有CPU isolated service或真实PTS路径。本说明只列出恢复后需要实现与集中验证的事项，不是测试执行命令或派测请求。

先闭合 `D1_C08_LICENSE_BUILD_REVIEW_V1.0.md` 所列严格组件/许可阻断，再实现有界opaque token AVIO、只读seek、CPU decode/PTS及受控帧协议。只有APK内nonexported isolated服务可执行新CPU实验，不安装companion支持该路径；既有companion回归基线不能充当CPU隔离证明。

集中验证需分别覆盖AVI MPEG4与MP4 H264真实frame/PTS、损坏源、worker自身SIGSEGV、挂起有界终止、实际Binder death与SourceReleased、第二任务与宿主存活、输入hash不变；记录task/epoch/PID/UID及帧/读请求/队列预算。raw匹配崩溃和App历史reason/status/trace/cause分别记录；status0必须UNKNOWN，cleanup kill不得充当目标signal11。缺实际故障证据或释放证据不能通过。

C08 ExitEvidence修正只经过本机反例与Java编译；TABLET-C07-01原FAIL保持。不得自动清缓存、重新安装、同条件重跑该FAIL、重新派测ordinary UNKNOWN或把裸帧成功当P0关闭。所有设备操作均需用户恢复后另行明确安排。
