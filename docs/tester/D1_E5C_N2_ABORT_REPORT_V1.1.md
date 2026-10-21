# D1 E5C 原 N2 狭义 ABORT 实际执行报告 V1.1

2026-10-17；tester。人类用户在本窗口直接批准对 HA1Q6WXR 原 N2 执行一次 ABORT_ORIGINAL_N2，更新 fence、按实际产物结算账本并归档 pending，要求报告负责人且不自动后续测试。执行仍按 `docs/milestones/D1_E5C_N2_ABORT_TESTER_REQUIREMENTS_V1.0.md` 的固定实现和边界。

**结论：PASS / ABORTED_SETTLED，准确原方法执行一次。** 原 R 保留，新增唯一 S=ABORTED/实际0B，原输出保留，新 fence 与 ABORTED journal 一致，前像/原 guard 身份/链式结算/原 pending 同 inode 归档/完成记录独立核验通过。原协议 closeACK=false，旧 N2 无帧失败与根因 UNKNOWN 不改写。

本批到此结束，未执行 OBSERVE_SETTLED_N2、完整新 host 观察或任何正常产品方法。D1 NOT_PASSED、M0 NOT_STARTED、全部 P0/JNI、历史 signal FAIL、C14 待测保持。

## 1. 直接批准、连续性及实际调用

原 V1.0 报告记录自动审批拒绝且执行进程未创建，ABORT0；原报告、拒绝和预检回执完整保留。本次直接批准原文见 [direct-human-approval.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_N2_ABORT_EVIDENCE/direct-human-approval.json)。批准后因距旧预检约一小时，再作一次包身份和一次原 metadata 连续性核验，全部符合已审 CONT/QUERY 现场。没有把旧拒绝算成一次设备执行，也没有重试已执行 ABORT。

设备 HA1Q6WXR / user0；已装 app versionCode5 / D1-E5C / UID10221，test UID10222/versionCode0，两包启用及安装状态符合原记录。沿用已证最终 APK/签名，不安装或重复设备 APK hash。E5C seal `75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c`、E5B 源 seal `3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee` 及准入 CONT 报告/QUERY 回执哈希再次匹配。

唯一实际方法：`com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort`；runner `com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner`；显式 e5N2Action=ABORT_ORIGINAL_N2、task `86cafdb3-0fc4-447d-920b-b19c884bf494`、budget `730a73e1-50e1-4198-a515-047104f00e31`、e5RecoveryBatch=D1-E5B-N2-RECOVERY-20261017。未传调用者伪造的死亡信息、其他 task/路径或 settlement receipt。

实际回执 ABORTED_SETTLED / retainedBytes=0 / sha=e3b0…b855 / originalCloseACK=false / retainedOperations=0，JUnit **OK (1 test)，0.073s**；ADB 客户端 2.516s、exit0。原始回执 SHA `f079eed91f75a6f457a2610a5b55c8af40179bf3fe6de16644a95020838f54e8`。

## 2. 原死亡、真实原锁与恢复 writer

冻结实现重新核对原 metadata 及实际退出记录，在取得原两把锁后再次核对；原始回执各 PID 出现两次相同的系统事实。

| PID | UID / process | queryRows / uniqueMatches | timestamp | reason / status | /proc |
| --- | --- | --- | --- | --- | --- |
| 24853 | 10221 / com.videokit.app | 每轮1 / 1 | 1792208963379 | 10 / 0 | absent=true |
| 24873 | 10221 / com.videokit.app:e4_codec | 每轮1 / 1 | 1792208963381 | 10 / 0 | absent=true |

时间均在固定原 N2 窗口内。reason/status 为系统原数值，未把退出事实回填成旧协议 closeACK 或原失败根因。

原 guard 使用已审非创建 O_NOFOLLOW、实际 FD lstat/fstat/角色长度UID/fence/dev-inode 及排他 flock 路径。新 82B guard.identity 独立解码：owner dev64522/inode20304/UID10221、lease dev64522/inode20385/UID10221，与恢复前后原路径相符；没有创建替代 guard。owner0B、lease36B 原 inode 保持。

恢复 writer 记录为 attempt `8c6673b7-38a5-4a24-838d-ca8466d8b75f`、PID4869、UID10221、process com.videokit.app、began1792224193301。记录104B，格式与准确生产记录一致，已保存在原恢复目录及本地取证。未查询该 writer 的后续死亡或为新 host 执行独立观察。

## 3. 前像、fence、ABORTED 与实际结算

四前像与批准后准确预检逐字节匹配：identity.before225B、journal.before85B（原 WRITING/granted=true）、lease.before36B（原 fence）、ledger.before192B（原 header+唯一 R）。当前 task.identity 的原225B及原属性保持，原 epoch `5131975343750146374`/gen1/service `775a5ee9-fff3-4340-a03b-97751099c0c4` 不变。

原 fence `a256356e-361b-47a0-b2e9-32dce4ccea8e` 更新为 **`662e9ecd-bede-42e6-bb58-ce81d668ff44`**。当前 lease36B 与 ABORTED journal85B 的 fence 完全相同；独立二进制解析 journal state=2、granted=true。journal 经冻结实现 ABORT_PENDING → ABORTED 两次持久化，当前原子替换后的 inode13082；两个临时 journal 均不存在。

原输出仍 dev64522/inode20386/0B，UID/mode/mtime 与恢复前相同，未删除或替换。生产方法实际打开保留输出、读至 EOF 并计算 SHA，得到 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。tester 后取证仅 stat 输出，没有追加输出读取/hash；当前0B与生产实际哈希一致。

原 ledger inode20303、原 header 和 R192B逐字节保留；仅追加一条179B的 S，最终371B：

```text
S 86cafdb3-0fc4-447d-920b-b19c884bf494 ABORTED 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 1747c406b45987a8f4a3e8194bb170dfac92eb938d94ad2950bbb1f303ad4055
```

tester 从旧 R 链哈希 `6660cfb1b19dee6ced8fb9427d6605eb394ba9ecd9ab5931905a9a8727ffd026` 独立重算新 S 链一致；proof.txt 内 S 与实际 ledger 追加字节完全相同，未新增 R 或重复 S。最终 ledger SHA `9654a49d6fb667fa28d9a63580ddcb0c08d88c378cc46c653f15fa0605e829f6`。按原链逻辑，未结算保留额降为0，实际累计消费0B；这是原任务真实0B产物的终局结算，不是删除输出/marker或重置预算。

原 identity.anchor inode20302/准确预算字节保持；proof401B 包含原两退出记录、originalCloseACK=false、新 fence 与唯一 S，均独立核验。

## 4. 原资源归还、目录同步与归档

ABORTED_SETTLED 只有在冻结生产实现的全部原 holder/平台目录 barrier 实际返回、原 ledger锁/FD及 owner/lease 的 unlock/dup/raw close 返回后才成立；回执 retainedOperations=0 且 JUnit 精确断言通过。当前实际成功回执结合冻结源码门支持本次恢复所有者返回，不只依据系统结束 instrumentation 或磁盘完成文件存在。

后取证确认原 operation.pending 不再占用活动路径，归档为 `operation.pending.N2-e5-aborted`，仍是原 **dev64522/inode20492/0B/原UID/mode/mtime**；同目录归档身份保持，没有通过手工删除解除 pending。`N2-e5-recovery.complete` 为96B准确完成字节。前像、writer、guard.identity、proof 和原输出全部保留。

证据范围：实际返回资格由冻结 E4Owned/Guard/目录 barrier 检查与本次成功回执证明；没有另外采集每个 FD 数字、逐系统调用 trace 或掉电持久化结果。原 host/codec 的旧协议 closeACK 始终 false，旧 N2 FAIL/根因 UNKNOWN 不升级。本次 writer 的资格限该实际原操作，不跨 host 继承；没有新 host 最终观察，也没有以完成字节给未来 host 发许可。

## 5. 保全、预算与停止

批准后准确元数据连续性通过；后取证核对原/恢复目录的固定16条 metadata 路径，其中15份实际文件共1974B、活动 pending 路径不存在，单文件≤4096B、总≤16384B，低于任务授权上限。后取证回执9261B，SHA `62b1e7ddf8c5ce05ee96b7e72285cc07963391014f9e707469eadf13693529c5`。本地另保存解码二进制副本，来源绑定该原始 HEX 回执，未向设备写入取证副本。

真实媒体未读：预置 basic.mp4/subtitle.avi 仅 stat，分别仍为 inode20198/349102B 和 inode20199/736454656B，原 dev/UID/mode/mtime 不变；cache/旧失败文件未扫描清理。夹具 root 未操作。

含审批拒绝前预检，本证据目录共6次实际 ADB：5次 metadata、1次 ABORT；批准后4次。metadata均在15s内，低于8次门；ABORT仅1次，无重试或只读兼容修正。日志47627B <8MiB，单回执 <256KiB。原生产恢复 holder≤32、目录 barrier≤16、输出hash≤2MiB 门保持；实际输出内容0B。全部实际 ADB 客户端 wait 返回、管道关闭，当前无在途 client/handle。

安装、QUERY重跑、OBSERVE、正常 MP4/AVI/能力/取消、Gradle/开发模型、手机/模拟器、故障/信号/force-stop均0。用户要求“不要自动进入后续测试”，本次执行后已停止；平板后续已明确安排的测试可直接使用，不再重复询问设备使用授权。

## 6. 报告与后续边界

本报告 V1.1 是直接批准后的实际结果；V1.0 的自动审批拒绝/NOT_RUN 历史及原回执不改写。本次仅完成已批准的原任务狭义收尾，不代表正常编码能力或项目 D1 通过。后续如由负责人安排新 host 独立观察和产品回归，仍须先有准确测试需求、当前真实资格和独立报告；本次不自动启动。

独立审证：[actual-abort-independent-review.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_N2_ABORT_EVIDENCE/actual-abort-independent-review.json)。本报告完成主动发送负责人并保存新通知回执。
