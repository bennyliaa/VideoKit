# INPUT_SINK04 宿主结果边界集中修复要求

2026-10-21；INPUT_SINK04_FIX；正式集中修复。依据完整独立报告dfd9266819457f5d153d1a1d0c4d34fa65e7ee19e06b5e3cd027ad3d2172b5f3。原B03/B04指定修复有限通过，B01/B02/A01/A02及真实依赖身份门保持，但整包因B05/P2与C01/P3仍FAIL。新候选新目录，旧629项/此前2349冻结及tester历史证据不改，D1未过M0未启。纯离线无设备/SDK/ADB/5037/占用/旧handle查询，不并发Gradle。

1. B05：在消费同原QUERY成功结果前校验null、合法状态与允许状态转移、READY所需非空且有效token、原task/输出/授权/长度/摘要等本契约已定义的身份绑定；同原错误稳定脱敏一次登记firstFailure，不能直接NPE或接纳空token并归还。READY/COMMIT/readonly authority的同类校验一致，不能重新QUERY或伪造host成功/回滚求绿。坏响应只证明协议失败，实际宿主可能有副作用时保留业务UNKNOWN及原资源直到同原权威事实可安全收敛。
2. 集中审全部host返回边界，而非只补两个case：write ACK count/range、flush/close完成、reopen handle与源身份/长度、validator字段、READY/COMMIT/ABORT/QUERY状态-token组合与readonly authority三态。建立适用的null/空/非法状态/错task-token/负数溢出/不一致成功/重复观察/晚结果/原authority未返矩阵；缺契约字段不得凭空扩出新协议，明确候选约束和未决，保持单原task和原registry权威，不引入新框架或一套验证计数。
3. C01：每次新候选工具--review-output与本文/独立计划/正确tester新根一致；新路径正例、旧根/候选内写路径拒绝负例实际执行验证。不要允许任意输出目录或改旧冻结工具；文档命令本身必须可直接复核，无需tester临时绕过。
4. 原两非法QUERY源码/交付JAR双路径复现留证，再修复后独立风格回归；20/17/23/63/5与19矩阵受影响范围及原取消脱敏/firstFailure/原线程keeper回归，工具根目录实测作为交付门。不以增加重叠断言数代替边界。必要集中strict实际Media3/Android ABI构建一次，依赖锁/metadata/许可及native/host无关项不动。
5. 整批完整交源码差异/返回边界矩阵/实际JAR和APK身份/自测原日志/旧失败与新回归/可直接执行复审入口/ZIP-seal，主动送负责人后冻结。后续由tester集中复审，不逐点来回沟通；真实平台/业务提交依旧NOT_RUN，全部P0/历史UNKNOWN不减。
