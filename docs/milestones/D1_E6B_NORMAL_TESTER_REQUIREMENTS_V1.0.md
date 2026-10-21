# D1 E6B NORMAL 真机测试正式派发 V1.0

2026-10-17。负责人 VideoKit项目助理（01a107c3-2bf9-7fa0-94a0-234258ca6774）接受 E6B 静态复审 SUPPORTED，正式授权本批执行；用户已有永久平板使用授权，无需重复询问。此派发覆盖冻结计划的 REVIEW_ONLY 状态，不修改冻结计划。

按 docs/coder/d1e6b/tools/device_plan.json 使用准确 version8/final 双 APK；仅 HA1Q6WXR/user0，原同签名 UID10221/test10222，app→test 各 install-r 一次。先核身份/安装连续性/既有 fixture/无在途，再单方法 normalMp4SixRealFrames → 独立审证通过后 normalAviSixRealFrames → 通过后 capabilityDenialDoesNotOpenSource → 本批两个正常完整独立审证报告准确新 SHA 替换占位符后 cancelRejectsWrongEpochOversizeAndLateFrame。Tester 可在同批形成两正常独立审证报告，无需阶段性等待负责人，不能用旧 receipt 或任意 hash。

batch D1-E4A-E6B-NORMAL-TABLET-20261017；budget 730a73e1-50e1-4198-a515-047104f00e31；原 53651 消费、原 N2 S0/归档及结算报告 SHA 5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962 保持。每新 host 的原 Before 实际观察；无新 QUERY/ABORT/独立 OBSERVE/G01。

严格六源/六输入/六编码/六 accepted/PTS1000us/双 EOF/drain/content/thumb/READY，以及真实 owner/FD/slot/CONTROL/唯一 R/S/无 pending；完整 source/validator 分离诊断，native OK 不能替代整体成功。

任一 FAIL/BLOCKED/PENDING/UNKNOWN 或缺关键诊断/EOF/画面/资源归还证据立即停止依赖，保留产物现场；不重试产品方法、不清数据/卸载/删产物/换预算/放宽时限。沿原 60s/协商12s/STARTED15s/首 cancel30s，每 CPU64MiB/8192reads，每输出2MiB/3hash6MiB，每方法日志4MiB与累计预算，不扩大。

无副作用只读脚本兼容错误最多两次留痕修正，不重复成功检查；不适用于安装/产品/UNKNOWN写操作。可复用既有 fixture identity，不重传或冗余全量 hash；必要当前 stat/安装身份检查保留。无设备/Gradle并发，禁止手机/模拟器操作；设备不可用即报告环境阻塞，不轮询。

最终报告 docs/tester/D1_E6B_NORMAL_DEVICE_TEST_REPORT_V1.0.md，分方法原始证据、两正常 receipt（仅在实际成功时形成）、资源账本汇总，完成主动通知负责人。D1 NOT_PASSED/M0 NOT_STARTED；成功仅关闭相应实测范围，不作全部 P0 通过。
