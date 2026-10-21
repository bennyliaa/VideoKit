# D1 E5C 原 N2 狭义 ABORT 执行报告 V1.0

2026-10-17；tester。依据 `docs/milestones/D1_E5C_N2_ABORT_TESTER_REQUIREMENTS_V1.0.md`，沿已装 E5C、固定原平板和 N2 身份准备唯一一次 ABORT。

**结论：BLOCKED_AUTO_APPROVAL_EXACT_ABORT_NOT_RUN。预检 PASS，ABORT 未执行。** 自动审批在启动执行进程前拒绝这项写状态操作，要求人类用户对准确原 ABORT 直接明确批准。没有绕过或改用其他通道执行，没有重复调用、写恢复、后续观察或产品测试。

## 1. 已完成的独立前置

仅 HA1Q6WXR/user0，现装 com.videokit.app versionCode5 / D1-E5C、UID10221，test UID10222/versionCode0，包 installed/hidden/suspended/enabled 状态符合连续记录。沿用已审签名及最终 APK 身份，不安装或重复设备 APK hash。

本机再绑定 E5C seal `75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c`、E5B 源 seal `3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee`；准入报告 SHA `6e89690066ac47c83d7ac5ce92e1024b7d0a412ab0018d6c882a98a292184720`、原 QUERY 回执 SHA `0ac55263ad5c2f5af073cc6721274d0d8f1195cb241773007ac1cce1c6b9c115` 均匹配。最后报告中的系统退出事实仍属前批实际 QUERY 证据，本批没有再执行 QUERY。

本批一次包身份查询和一次准确原 metadata 核验均通过。原 identity225B、WRITING journal85B、lease36B/原 fence、owner0B、输出0B、ledger192B/R2MiB 无 S、operation.pending0B 与已审 QUERY 后记录逐属性/准确字节/SHA 一致；恢复目录、完成和归档 marker 均不存在，预置 MP4/AVI 仅 stat 且保持原属性，未读取/hash 媒体内容。

本机先集中审核执行/取证脚本语法、shlex.quote 整段引用和固定路径/字节界限。预检未发生兼容错误或修正重试。

## 2. 被拒绝的准确操作

拟执行固定入口 `com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort`，runner `com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner`，参数：

- e5N2Action=`ABORT_ORIGINAL_N2`；
- e5N2Task=`86cafdb3-0fc4-447d-920b-b19c884bf494`；
- e5N2Budget=`730a73e1-50e1-4198-a515-047104f00e31`；
- e5RecoveryBatch=`D1-E5B-N2-RECOVERY-20261017`。

该生产方法会获取准确原 guard 的非创建真实锁、保存四份前像/writer/guard.identity、更新 fence 和 ABORTED journal、保留原输出并按实际长度/SHA 追加唯一 S，然后等待实际资源/目录同步返回、归档 pending 并写完成记录；原协议 closeACK 始终 false。它会改变原 N2 账本及待处理状态，具有可能不可逆的状态影响。

自动审批原文理由：

> 该命令会对原N2任务持锁、修改fence和账本并归档pending，属于可能不可逆的生产数据状态变更；可见可信用户消息未明确授权这项精确ABORT，不能仅依据助手转述或需求文件放行。

工具返回 `CreateProcess ... Rejected`；执行解释器未创建。本机 `abort-stage-attempt.json` 和 `02-original-abort-attempt.json` 均不存在，ADB ABORT/仪器调用为 0，后取证未启动。没有实际新的 fence、前像、writer、guard.identity、ABORTED、S、归档或完成结果；不得把拟执行流程写成已经通过。

## 3. 预算与资源状态

本批实际仅 2 次 ADB 元数据调用，exit0，分别 0.156s/0.968s，均在每项15s内；低于元数据8次门。日志18418B <8MiB，两客户端实际 wait 返回、管道关闭，本批无在途 host client/handle。

ABORT0、instrumentation0、安装0、真实媒体内容读取/hash0、Gradle/开发模型0、信号/force-stop/cancel0。恢复输出≤2MiB、holder32/dirbarrier16 及后 metadata16KiB/单4096B 计划均未由 ABORT 消费。

原 N2 协议 UNKNOWN/FAIL/PENDING、根因 UNKNOWN、R2MiB/pending 未解除；本次拒绝发生在设备执行前，不能登记为产品恢复失败或释放成功。已取得的 G01 限定边界补验/QUERY 证据不改写。D1 NOT_PASSED、M0 NOT_STARTED、全部 P0/JNI、历史 signal FAIL、C14 待测保持。

## 4. 后续所需确认

已完成不受影响的预检和报告。继续该准确 ABORT 需要本窗口人类用户直接明确批准对上述原 task/budget 更新 fence、追加实际消费结算并归档 pending；负责人消息或需求文件不能代替自动审批要求的人类授权。不更换通道、参数、目录、task、budget 或包装方式绕过拒绝。

取得直接批准后，仍只执行该一次原 ABORT，不自动 OBSERVE 或正常方法；若连续性状态变化则停止。执行成功与否、实际原锁/FD/目录同步及前像/S/marker结果必须另行补充独立证据，当前报告的 NOT_RUN 历史保留。

证据：[approval-rejection.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_N2_ABORT_EVIDENCE/approval-rejection.json)、[final-independent-review.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_N2_ABORT_EVIDENCE/final-independent-review.json)。本报告主动发送负责人并保存通知回执。
