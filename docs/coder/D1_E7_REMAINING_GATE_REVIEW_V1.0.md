# D1 E7 剩余门槛复审 V1.0

2026-10-17。请求独立静态复审整个批次后，由负责人决定是否正式派发只读设备诊断。当前不提供任何一次性真实执行许可，不复用已耗E3许可。

|项目|本批状态与依据|
|---|---|
|E6B-OBS-F01/P1 每新host持续可审准入|OPEN；结构诊断完成，可靠持久协议设计阻塞，未提供长期准入|
|实际生产诊断|本地27场景316断言PASS；唯一匹配/正reason/proc门保持；Android适配器与独立只读入口均编译，Android NOT_RUN|
|旧 E5C-REG-F01|仅E6B_NORMAL平板MP4真实6/6/6/6 READY/PTS0/双EOF/画面/全部资源/唯一S53567限定关闭；不扩大至AVI或其他设备|
|AVI正常|E6B Before WRITER_DEATH未证；根因谓词UNKNOWN；E7不重跑|
|能力拒绝与cancel|NOT_RUN，cancel前两正常完整同批独立审证条件尚未成立|
|原N2结算/安全性质|原guard/观察/准入/owner/账本/资源边界不放宽；最后tester消费107218/reserved0，所有原产物保留，未重新测量|
|构建与来源|一次39秒离线双APK、同原证书、version9；7native和35依赖不变；E6B191只读PASS；源码/diff/输入/SBOM/外seal/ZIP可核|
|D1/M0/历史signal/许可全P0|D1未过/M0未启，历史signal未改；所有既定许可/平台/设备/16KiB实测与余下P0继续保持，不以诊断通过替代|

tester应独立核对 production gate 确实从 Android requireRecoveryWriterDead 调用，原错误拒绝无绕过；API最多一次max8/无重试，计数未采集与0分明，无关process/异常正文不进入输出；匹配先于reason、仅ENOENT可通过。核对Report不是Proof、没有持久事实缓存/解析入口、原观察全链条及实际资源归还仍必要。

核对只读入口 class#method/参数、固定owner精确字节、路径UID/角色/noFollow/读界/原FD持有者/实际close/10秒PENDING保留；确认没有调用observe或任何新恢复写/CPU/服务/媒体。该方法的JUnit PASS只代表诊断被收集，可带BLOCKED_CURRENT_GATE；不等于当前历史证据合格，更不等于FRESH_OBSERVATION_ADMITTED。

精确审阅 source-derivation/diffs、输入与build关联、local-check-results原始日志、APK signer/aapt/zipalign/DEX、SBOM/native来源、reference原始AVI/MP4日志及独立报告、freeze和包外只读receipt。持久协议风险项明确为NOT_IMPLEMENTED/不能准入，不得登记为模拟通过。

需要负责人后续决策的实际缺口：能否取得旧writer精确启动代次及可信死亡来源、防回滚的外部保证；若无法取得，则必须正式设计旧V1安全迁移/处置，不能自动重写原档案。仅增加历史limit、同host重试、复用receipt、移除死亡门都不满足要求。现阶段仅可派发一次只读诊断，不串接正常/能力/cancel。
