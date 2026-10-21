# D1 E5C 续行设备测试报告 V1.0

2026-10-17；tester。执行依据：`docs/milestones/D1_E5C_EXECUTION_CONTINUATION_TESTER_REQUIREMENTS_V1.0.md`，外部留痕 `D1-E5C-CONT-TABLET-20261017`。仅原平板 HA1Q6WXR / user0 / app UID10221；内部产品 batch 与准确参数保持已审计划。

**结论：部署 PASS；隔离补验 PASS（三场景、一个 JUnit 方法）；原 N2 只读 QUERY PASS / QUERY_ELIGIBLE。** G01 已取得批准范围内的 Android 真文件链接、原生产观察锁边界及实际 FD 返回证据，独立审核通过。完整 observe、写恢复及正常产品方法均未执行或授权；原 N2 仍 FAIL/PENDING、R2MiB 无 S/pending 未解除，根因 UNKNOWN。

D1 NOT_PASSED、M0 NOT_STARTED、全部 P0/JNI、历史 signal FAIL、C14 待测不变。旧 Windows 文件 symlink NOT_RUN 与前批 tester 引号错误报告保留，不改写为成功。

## 1. 续行前置与部署

复用前次成功采集的 HA1Q6WXR / TB138FC / API31 / ARM64 / user0、app UID10221/test UID10222、E4A 两 APK 完整 SHA 与既有签名身份、85360328KiB 可用空间证据。前批 install=0、instrumentation=0、客户端均返回。续行仅一次 get-state 和一次当前包/version/UID/user 状态检查确认连续性，未重复设备 APK 完整 hash 或包备份。

整份远端只读脚本改用 shlex.quote；集中完成 Python AST、整脚本引用 round-trip 及已知 Android 命令/固定路径审查后执行。原 N2 metadata 的准确字节、ledger R/pending 与自有 root 不存在前置均一次通过。续行中只读取证/本机解析兼容修正次数 0，没有用授权的两次便利重跑成功项；原失败脚本和回执仍在 D1_E5C_DEVICE_EVIDENCE。

| 部署项 | 实际结果 |
| --- | --- |
| app install -r | 一次 Success，客户端 0.531s |
| test install -r | 一次 Success，客户端 0.266s |
| 更新后身份 | app versionCode5 / D1-E5C，原 UID10221；test UID10222 / versionCode0；user0 两包 enabled=0、installed=true |
| 原数据必要保全 | 安装后准确原 metadata/stat 与安装前一致，最终核对仍一致 |

最终候选 seal `75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c`、ZIP `ac7d5bc2901ab66bb16299cf8c2052e6e7bd3344276b1c3d2a0b50b38a291743`；app SHA `5b7992f1ec01f8782b59dd1508c6a47e3af4f2602ba428e1b65892724f73f464`、test SHA `5101c8efa43fd4ab5944479c8bafa8934ab9c4a1a1318fd9c6eae4c5d3f0e36c`。本机准确文件身份再次核验后交给 install-r，继承同签名证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。未重复设备更新后 APK hash；部署依据为准确输入文件、两次 Success 与包版本/原 UID 核验。没有卸载、clear、降级或改变签名。

## 2. 隔离补验：实际结果与独立准入

准确选择 `E5CGuardFixtureTests#isolatedOriginalInodeSymlinks`，参数 e5cCase=isolatedOriginalInodeSymlinks、e5cBatch=D1-E5C-GUARD-LINK-TABLET-20261017、e5cRun=FORMAL_DEBUG_FIXTURE_ONLY。只调用一次，JUnit **OK (1 test)，0.147s**；ADB 客户端 2.890s。原始回执 SHA `2481a0c337252a6eb5f9d16e4d56f261c61222b7ebc76541567a5f55b5b67513`。

| 场景 | 实际证据 | 结果 |
| --- | --- | --- |
| healthy | 原观察 private lock 经原 Android 适配器/Guard/IO 获取 owner、lease；两个 raw/dup 对及两个原 holder 真实关闭 | HEALTHY_TWO_LOCKS_CLOSED |
| owner_symlink | 真 owner symlink 指回相同原 inode/字节；独立打开 ELOOP，生产原锁边界准确 role 拒绝；第一个 holder 前置拒绝无 FD | TRUE_SYMLINK_REJECTED |
| lease_symlink | 真 lease symlink 指回相同原 inode/字节；独立打开 ELOOP；先获取健康 owner，再在第二个 holder 准确拒绝 lease，关闭原 owner | TRUE_SYMLINK_REJECTED |

真链接证据：owner `8e945a6d-cf3d-48e2-bae3-04baf21af649.owner` → 同目录 `.owner.original-target`，S_IFLNK，原 dev64522/inode21834/0B，SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；lease `4865ac8f-8ae0-4303-b40a-bb53cb51c999.lease` → `.lease.original-target`，S_IFLNK，原 dev64522/inode21588/36B，SHA `098452e6143a7938a10d87bf01587886d89bfa4355f2aa0307cd63ba8cca0a76`。

冻结入口实际断言 readlink、目标 regular、移动前后 dev/inode/UID/长度、跟随 stat 及原字节 SHA 一致；两个生产负例都必须准确为 E5B_EXISTING_GUARD_ROLE_LENGTH_UID，任意异常不会通过。独立 O_NOFOLLOW 探针两次均 ELOOP/actualClose=CLOSED。

全部五个原观察 guard holder 为 CLOSED/returned=true：三个已分配 RAW_AND_DUP 对关闭，两个 NONE_PREOPEN_REJECTION 没有分配 FD。CLOSED 日志由实际 raw/dup closeAttempted、两个 FileDescriptor.valid=false 及原 holder 返回检查门生成；前置拒绝未虚称关闭已分配 FD。自有读写/探针 holders 的 allClosed 和最终时限检查也通过。

每例边界前后 NOFOLLOW 快照、metadata/自有账本/payload 字节不变，R_count=0/S_count=0、liveGrant=false；最终 E5C_LOCK_BOUNDARY_PASS 与 JUnit PASS 同时成立。固定 root `files/e5c_guard_fixture_20261017_once` 保留，不删除或换名。64 节点/256KiB/单64KiB/holder128、日志4MiB/更紧64事件×4096字符、60s 三例一次门均由入口检查通过；没有另行扫描 root 来补计数。

tester 在读取完整原始回执并核对冻结源码检查门后，先落 [fixture-independent-admission.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_CONT_EVIDENCE/fixture-independent-admission.json)，才允许本批条件 QUERY。准入严格限同一已授权整批的固定只读 QUERY。

**G01 判定：PASS_ACTUAL_ANDROID_PRODUCTION_OBSERVATION_LOCK_BOUNDARY_ONLY。** 这是批准的精确反射原 lock 边界补验；metadata/death=ASSUMED_SYNTHETIC_NOT_EXECUTED，fullObserve/originalN2=NOT_RUN。没有取得完整观察 live grant，没有执行 force/sync/死亡前置或用夹具模拟原恢复成功。

## 3. 原 N2 只读 QUERY

在独立新 instrumentation 中精确调用 `E5RecoveryDeviceTests#originalN2QueryOrAbort` 一次；e5N2Action=QUERY，固定 task `86cafdb3-0fc4-447d-920b-b19c884bf494`、budget `730a73e1-50e1-4198-a515-047104f00e31`，保留 e5RecoveryBatch=`D1-E5B-N2-RECOVERY-20261017`。未传 settlement receipt，未调用整类或默认动作。

实际输出 `QUERY_ELIGIBLE`，`retainedBytes=-1 sha=NOT_READ originalCloseACK=false retainedOperations=0`；JUnit **OK (1 test)，0.026s**，ADB 客户端 1.828s。原始回执 SHA `0ac55263ad5c2f5af073cc6721274d0d8f1195cb241773007ac1cce1c6b9c115`。

| 原进程 | UID / process | queryRows / uniqueMatches | 实际退出 timestamp | reason / status | 当前 /proc |
| --- | --- | --- | --- | --- | --- |
| 24853 | 10221 / com.videokit.app | 1 / 1 | 1792208963379 | 10 / 0 | ENOENT，absent=true |
| 24873 | 10221 / com.videokit.app:e4_codec | 1 / 1 | 1792208963381 | 10 / 0 | ENOENT，absent=true |

时间均在固定原 N2 窗口内，准确 PID/UID/process 唯一匹配。reason/status 保留系统原数值，不补写旧测试中 NOT_COLLECTED 字段或推断原 codec 无帧根因。

QUERY 通过仅表示原 metadata 和两个实际退出记录前置成立；原 exclusive leases/FD settlement 仍未测试，原 closeACK=false，没有 fence、输出 hash、S 或 guard.identity 新记录。当前 QUERY host 的 retainedOperations=0 不等于旧 N2 协议原资源已按 ACK 归还，也不解除 R/pending。

## 4. 原现场前后保全

安装前、安装后、QUERY 后三份准确有界元数据核对均通过，相关 dev/inode/size/UID/mode/mtime、metadata SHA 和原身份/WRITING journal/lease 准确字节一致。dev 64522、UID10221 保持。

| 原文件 | inode | 字节 | 最终结果 |
| --- | --- | --- | --- |
| identity.anchor | 20302 | 36 | 原预算身份一致 |
| ledger.bin | 20303 | 192 | 原 R2MiB、无 S，SHA 4a8f0409aee7bf91576927b932ad390bf941c465ac303200e6f2bdcdb7d900eb |
| operation.pending | 20492 | 0 | 保持存在 |
| task.identity | 20384 | 225 | 原 task/epoch/gen/service/UID 一致 |
| task.journal | 20390 | 85 | 原 WRITING/granted=true/fence 一致 |
| task.lease | 20385 | 36 | 原 a256356e-361b-47a0-b2e9-32dce4ccea8e 一致 |
| task.owner | 20304 | 0 | 原文件属性与空字节保持 |
| task.mp4 | 20386 | 0 | 仅 stat，未读取/hash 输出内容 |

原 epoch `5131975343750146374`/gen1、service `775a5ee9-fff3-4340-a03b-97751099c0c4` 不变；恢复目录、完成文件、归档 pending 均不存在。未进行清账、补 metadata、换账户/UUID 或重复 S。

预置 `basic.mp4` 的 dev/inode/size/UID/mode/mtime `64522,20198,349102,10221,8180,1792207996`；`subtitle.avi` 为 `64522,20199,736454656,10221,8180,1792208513`；三份 stat 一致。没有读取/hash 真实媒体内容或扫描 cache。夹具只访问唯一自有根，未使用这些媒体或原预算。

## 5. 预算、所有权与后续

续行 ADB 共 11 次：7 次必要只读 metadata/连续性、2 次 install、1 次 fixture、1 次 QUERY；全部 exit0、实际客户端 wait 返回、管道关闭，当前无在途 client/handle。没有安装/fixture/QUERY 重试。原失败批 5 次保留，累计 16 次，不把续行改写成原批成功。

续行原始日志 45686B；含原失败批累计 63707B，均低于 8MiB。fixture 回执 4082B <4MiB；QUERY 回执1264B。媒体内容 hash/read、Gradle/开发模型、native fault、信号/force-stop/cancel、手机/本机一次 ID 脚本均 0。没有放大等待或修改产品期望。

夹具实际原 holders 已返回；原 N2 的旧协议 UNKNOWN/closeACKfalse 保持，不能用新 QUERY 退出记录洗成协议归还或产品成功。D1/M0/P0/历史 FAIL 不因本次局部通过而关闭。

本批已完成并停止，不自动下一批。负责人可依据本报告单独评审 G01 与原 QUERY 证据；如安排原 N2 写恢复，仍须明确准确 ABORT 范围、实际锁/结算/持久化返回与后续独立观察条件，再另行正式派发。当前没有 ABORT、OBSERVE_SETTLED_N2、正常 MP4/AVI/能力/取消的执行许可。

完整本地审证：[final-independent-review.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_CONT_EVIDENCE/final-independent-review.json)。本报告完成后主动通知负责人并保存回执。
