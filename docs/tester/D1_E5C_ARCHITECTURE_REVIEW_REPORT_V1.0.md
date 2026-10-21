# D1 E5C 隔离 Android 补验入口整包复审报告 V1.0

2026-10-17；tester。依据 `docs/milestones/D1_E5C_TESTER_REQUIREMENTS_V1.0.md` 及负责人批准的 Debug-only 精确反射锁边界补充，对完整冻结包、四文档、最终构建/APK、既有证据及执行计划集中静态复审。

**结论：SUPPORTED_FOR_FORMAL_DEVICE_BATCH。新增静态阻断 0 项。** 支持负责人另行正式派发：同签名保数据更新最终双 APK → 单次隔离夹具 → 夹具完全 PASS 且实际资源全部返回后，独立新 instrumentation 执行固定原 N2 只读 QUERY。计划可执行性获支持，不等于已授权或已执行设备操作。

**E5B-G01 仍为 AWAITING_ANDROID_EVIDENCE_AND_REVIEW。** 本次仅审查补验入口；Android 真 symlink、flock、FD 关闭、原 QUERY 均未运行。本入口只覆盖原观察的 private lock 边界，不覆盖完整 observe、死亡/metadata 前置、force/sync、live admission 或 N2 恢复。写恢复、最终观察和正常产品回归仍需后续证据及单独派发。

本轮 tester ADB、安装、设备/QUERY、真实媒体 stat/read/hash、Java/Gradle/模型重跑均为 0。D1 NOT_PASSED、M0 NOT_STARTED、全 P0/JNI、N2 FAIL/PENDING、旧 signal FAIL、C14 待测与 Windows 真文件链接 NOT_RUN 保持。

## 1. 冻结、来源及最终产物身份

| 项目 | 独立核验 |
| --- | --- |
| 候选根 | docs/coder/d1e5c；D1-20261017-E5C |
| 外 seal SHA256 | 75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c |
| ZIP | 18345999B；ac7d5bc2901ab66bb16299cf8c2052e6e7bd3344276b1c3d2a0b50b38a291743 |
| 成员 | 138 源文件、144 不可变文件，大小/SHA、ZIP 精确成员与字节 PASS |
| 最终 build snapshot | 6af5f97db1f2e74ac35627fc3a46bc6b2b74037f495b422d3af522987827bd36 |
| 最终 app APK | 10527871B；5b7992f1ec01f8782b59dd1508c6a47e3af4f2602ba428e1b65892724f73f464 |
| 最终 test APK | 2743033B；5101c8efa43fd4ab5944479c8bafa8934ab9c4a1a1318fd9c6eae4c5d3f0e36c |

两包既有签名日志与封存字节身份核验通过，证书均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；本轮没有重跑签名器。版本 5 / D1-E5C，appId com.videokit.app / com.videokit.app.test，两个原非导出服务、单产品 APK 布局和 ACCESS_NETWORK_STATE 权限保持，无新增 INTERNET/companion。

main-001、repair-001 均离线编译 exit 0，但首轮 APK 清单审计失败：overlay 缺少原 Debug 服务清单。最终 repair-001 补回与 E5B 字节一致的清单，绑定最终输入和最终双 APK；首轮 app APK SHA `4eb0506e953ffe86a3e70ac9335f227efbde749f414c1c31497225a41ae67590`、原输入/日志/失败说明另封存，不作为最终部署对象。首轮 test APK 与最终 test APK 同字节，不能用这一点省略最终 app 身份校验。

E5C 直接引用冻结 E5B 的生产 src/android、原测试及 C14 目录，新增仅为 Debug 测试入口/边界策略与交付工具。独立重核 E5B seal 和 1561 个不可变文件，并按冻结 upstream-copy-map 补充核对应源辅助文件；原生产 Guard/Observation/Recovery/Admission/Lifecycle 无字节修改，main/debug 复制清单与原字节相同。源码 ZIP 包含必要相对布局与完整 C14 对应源容器，未复制旧自检树。

独立比较最终 APK 七个 native 条目与 E5B APK 及对应 upstream 字节相同；依赖锁相同，35 Maven 坐标差异 0。Media3 1.9.3 / FFmpeg 8.0.3 保持，不表示漏洞、许可、发布 P0 或同 UID 安全沙箱问题关闭。

## 2. 精确生产边界与隔离路径

审查入口：[E5CGuardFixtureTests.java](/D:/CodexProjects/VideoKit/docs/coder/d1e5c/app/src/androidTest/java/com/videokit/spike/e4/E5CGuardFixtureTests.java)。仅 Debug、com.videokit.app 主进程、UID10221，精确方法/三参数匹配且无原 session/encoder slot/恢复或观察 retained 才进入。consume 是当前进程一次门，固定 `files/e5c_guard_fixture_20261017_once` 必须独占创建成功并 chmod 0700；既有 root 直接失败，不扫描、不删除、不换名重跑。

反射精确指定未改 `E5AFinalObservation.private lock(Path,E5BGuard.Role,String,E5BFileId)`，核声明类、private 修饰和返回 E4Owned 签名。调用进入原 `E5N2RecoveryAndroid.existingGuard → E5BGuard → E5BAndroidGuardIO`，实际使用 Android lstat/open/fstat/dup/JNI flock/unlock/close，没有 Guard 或 IO 模型替身。

夹具 Platform 仅放行当前 case 两条精确自有路径及正确 role/epoch/expected 实例，然后委托原适配器。death、writer death、recoveryOwner、sync、metadata force/close 接口直接拒绝。没有执行完整 observe()/recovery.execute()；未改观察对象只是为精确 private lock 提供 holder 注册和同一调用链。构造派生的未使用 N2 子路径没有被访问，不读写原 N2 路径。

每例使用自有随机 task/epoch/账本 ID，own-identity/own-ledger/own-payload 均为合成字节，R_count/S_count 为 0，不包含原真实 N2 ledger。日志明确 metadata/death=ASSUMED_SYNTHETIC_NOT_EXECUTED、fullObserve/originalN2=NOT_RUN。实际 live grant 进入前要求 null，前后对象相同，所有局部观察 actualReturnProven 必须仍 false。此处“无 R/S”证明限于自有合成账本不变和未执行生产 reserve/settlement；不通过读取原预算作证明。

## 3. 健康及两真文件链接负例

健康例通过原边界取得 owner、lease 两把实际原锁，然后由原 holder 关闭。原 Android Guard 在打开前后和锁前后核实际句柄/路径类型、长度、UID、dev/inode/fence；本补验不改这些生产条件。

owner/lease 负例分别先移动自有原 guard 至相邻 `.original-target`，再建立相对文件 symlink 指回该目标。要求 lstat S_IFLNK、readlink 精确目标、目标是 regular、dev/inode/UID/长度与移动前相同、跟随 stat 指向同一 inode，原目标 SHA 相同。因此错误跟随链接仍可能看到原身份和字节，不能只靠“替代 inode”误打误撞拒绝。

独立 O_NOFOLLOW 探针直接调用同一 Android IO，必须得到 ErrnoException/ELOOP；其他异常不接受。该探针的 holder 预登记并要求实际 close 返回。它证明系统打开行为，不能代替生产观察锁边界本身的拒绝。

随后实际反射锁边界的负例必须准确抛 `E5B_EXISTING_GUARD_ROLE_LENGTH_UID`：owner 链接在第一个 holder 拒绝；lease 链接先成功取得健康 owner，再在第二个 holder 拒绝并关闭原 owner。任意异常、缺 native 库或反射失败不能算预期 PASS。

每例链接设置后、边界前后的 NOFOLLOW 有限快照比较路径、类型、dev/inode/UID/mode、普通文件长度/SHA、link target；没有新节点或自有 metadata/ledger/payload 修改，不遍历链接。用于构造链接的 move/symlink 是负例准备动作，不能被误写成整个方法全程只读。

## 4. 所有权、实际 FD 关闭与时限

Run 在 worker 启动前保存在静态 RETAINED；原观察对象在任何反射 lock 前强引用登记，原类 holder 在 factory 前登记。自有读写/探针同样预登记 E4Owned。失败保留 Run、原 holder、root；UNKNOWN/CLOSING 不重试，不派替代 closer，不删除现场。

closeOriginal 从原 Guard 读取实际 Descriptor，保留 dup 的 FileDescriptor 引用。对健康已分配资源，只有 raw/dup 均 closeAttempted 且两个实际 FileDescriptor.valid=false，原 holder CLOSED/returned 才标 CLOSED。生产 lstat 前置拒绝未分配 FD 明确记 NONE_PREOPEN_REJECTION，不冒充关闭了已打开 FD；部分分配或关闭不明均 UNKNOWN、不能通过。

方法从开始计 60 秒，host 仅等待剩余时间；worker 在各阶段和读写检查同一截止。超时记录 PENDING/actualReturn UNKNOWN，不 cancel/shutdownNow/force-stop 或清 root；hostTimedOut 和 worker 截止阻止迟到结果改为本轮通过。系统调用不返回时，60 秒只表示验收截止，不能保证内核调用被终止；Run 的强引用只在进程存活期间有效，系统结束 instrumentation 不构成资源真实关闭证明。执行方必须据此将 QUERY 留 NOT_RUN。

[E5CFixtureBounds](/D:/CodexProjects/VideoKit/docs/coder/d1e5c/app/src/androidTest/java/com/videokit/spike/e4/E5CFixtureBounds.java) 与调用路径限制 64 节点（含目录/链接）、256KiB 普通文件及链接数据、单文件 64KiB、128 IO holders、3 case/1 attempt；写入内容为固定小夹具，每次有限快照核边界且最终核 root 总量。日志上限 4MiB，同时实施更紧的 64 事件、每条 ≤4096 字符。到达限制即失败，不截断拼成功。快照最大深度 4，唯一新 root 下没有可接收的外部路径。

## 5. 已有证据的适用范围

封存 local-check-results 仅为 **10 项纯 JVM bounds/deadline 检查 + 9 项源码约束**，输入与日志身份已核验；不写成 19 项 Android 用例。10 项包括节点/总量/单文件上下界、60 秒前/临界以及 nanoTime 差值溢出边界。9 项静态约束包括精确生产边界、真实链接构造、独占 root、不取消、ELOOP/FD 检查、有限快照及 grant/账本不变。

这些证据不证明 Android 真链接创建/读取、flock、实际 FD 关闭，也不证明原 N2 writer 死亡或完整观察。旧 E5A 270 / E5B 82 只引用既有审查，不重跑、不相加、不升级历史结果。G01 须看到本次实机完整原始证据并独立评审后才能登记新范围的结果；Windows 1314 NOT_RUN 历史保持。

独立审计最初只使用 E5B immutable 索引，遗漏 upstream-copy-map 绑定的辅助来源，因索引缺项停止；补充该已冻结映射后全部核验通过。此为 tester 审计工具映射修正，没有修改候选文件或重跑开发模型。

## 6. 整批计划准入与停止门

`docs/coder/d1e5c/tools/device_plan.json` 绑定最终双 APK/证书、精确逐步参数，顺序为 app install -r → test install -r → 单个 E5C 方法 → 条件满足后原 N2 只读 QUERY。正式派发必须绑定原平板 HA1Q6WXR，不自动选设备或回退手机；核原 appId/同签名/UID10221/版本5，不能卸载、clear、降级或取得新 UID。

隔离方法为 `E5CGuardFixtureTests#isolatedOriginalInodeSymlinks`；参数必须是 e5cCase=isolatedOriginalInodeSymlinks、e5cBatch=D1-E5C-GUARD-LINK-TABLET-20261017、e5cRun=FORMAL_DEBUG_FIXTURE_ONLY。只有健康两锁、两个真链接/同原 inode/SHA、ELOOP、准确生产拒绝、无修改/grant、所有原 holder/实际 FD 返回、最终 E5C_LOCK_BOUNDARY_PASS 及 instrumentation 单方法 PASS 全部成立，才可在正式整批任务内进入下一步。单看 exit 0、系统结束或某条 PASS 字符串不足。

QUERY 在独立新 instrumentation 精确选择 `E5RecoveryDeviceTests#originalN2QueryOrAbort`，明确 e5N2Action=QUERY、固定原 task/budget、**保留原 e5RecoveryBatch=D1-E5B-N2-RECOVERY-20261017**。源码直接引用 E5B，故不改为猜测的 E5C batch。该路径只读原 metadata/退出证明，不取锁/fence/输出 hash/写 S/创建 guard.identity；要求 QUERY_ELIGIBLE、originalCloseACK=false、retainedOperations=0 及系统证据独立归档。

任一部署失败、既有 root、夹具 FAIL/BLOCKED/PENDING/UNKNOWN、超时、FD 未归还或 runner/传输不明确，整批停止，QUERY=NOT_RUN；不自动重试、换 root、换 batch、取消或杀 owner。部署、夹具、QUERY 分别报告；QUERY 失败不抹去已有夹具证据，也不自动触发 ABORT/observe/产品方法。夹具完全 PASS 是进入狭义 QUERY 的条件，不等于 G01 正式审查关闭或后续写恢复许可。

原预算 `730a73e1-50e1-4198-a515-047104f00e31`、task `86cafdb3-0fc4-447d-920b-b19c884bf494`、epoch `5131975343750146374`/gen1、原 service/host/codec、R2MiB 无 S/pending、失败输出及预置 MP4/AVI 保持。不触真实媒体/缓存，不补原 metadata，不用自有夹具 UUID 代替原预算，不运行本机一次 ID 符号链接脚本。

当前仅完成静态复审，E5C 未由 tester 部署。独立证据：[identity-and-recorded-static-audit.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_EVIDENCE/identity-and-recorded-static-audit.json)。报告完成主动发送负责人并保存回执。
