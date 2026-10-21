# D1 E7A MANAGED READ ONLY 正式设备派发 V1.0

2026-10-17。负责人01a107c3-2bf9-7fa0-94a0-234258ca6774接受E7A静态复审SUPPORTED，正式派平板单次受管只读诊断。用户永久平板授权保持，无需重复询问。本消息覆盖已审device_plan的REVIEW_ONLY，不改冻结文件。

仅HA1Q6WXR/user0/原app UID10221/test10222，按docs/coder/d1e7a/tools/device_plan.json及附录准确version10/final同签名双APK，app→test各install-r一次。先确认无未归档旧在途任务/原身份，不通过新安装启动杀旧任务。

唯一组件com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation；非-w/非proto/非UiAutomation/非class/JUnit，精确plan四参数，handle9f19bfb5-60e0-4bcc-9666-852409cfe3b4。启动前归档handle/命令/设备/身份。本批固定owner最多257B/history一次max8/no grant，不observe/force/恢复写/媒体/normal/CPU。

外部控制总共最多6请求，每次响应预算5秒，总log1MiB，含STATUS/STOP_DEPENDENCIES/ACK_FINISH，统一不可清零台账。约1s及>=10s按实际需要读取；安全完成可提前归档，不凑时间多查。只有原operationsReturned=true且holder EMPTY未分配或CLOSED真实归还、完整外部snapshot已保存、同handle准确sequence时ACK_FINISH一次；resultCode1/finishClaimed不作实际finish或close ACK，另核runner结束与资源证据。

10s过界永久PENDING；PENDING/UNKNOWN停止依赖，归档handle/PID/UID/component/phase/holder/未返操作和剩余控制额度，保原受管任务，不kill/force-stop/interrupt/restart/clear/重装或无限轮询。后续同handle另派，不清零请求账。系统/通信丢失记LOST_OWNER_UNKNOWN，不冒close。启动客户端返回不当作诊断完成；DUMP资格/实际广播递达响应/唯一平台结束为本批实测范围，能力不符/设备不可用即停，不改权限或轮询。

无副作用只读脚本兼容错误最多两次留痕修正，不适用于安装/启动/产品/UNKNOWN重试，不重复成功检查。原107218消费/产物/归档保持，不额外读媒体或预算内容求证，无Gradle设备并发，不操作手机模拟器。

最终docs/tester/D1_E7A_MANAGED_DIAGNOSTIC_REPORT_V1.0.md，分别报告收集结果/当前死亡门/实际owner及平台结束/控制账，主动报告负责人。E6B-OBS-F01长期仍OPEN，QUALIFIED不放AVI/cancel，D1未过/M0未启。
