# D1 E5C 架构及威胁边界 V1.0

2026-10-17。仅验证生产观察的锁获取边界，不验证完整observe、真实writer死亡、N2恢复或产品编码。

## 同一生产路径

负责人批准Debug-only精确反射 `E5AFinalObservation.private lock(Path,E5BGuard.Role,String,E5BFileId)`。声明类/参数/返回类型/private必须匹配，不能替代方法或吞异常；source-provenance固定其原文件SHA `a98375bb2d67c2e54576a3c7f739ce3bc19dd90ab9b7b64c33109f4e8bb89434`。进入同E5N2RecoveryAndroid.existingGuard→同E5BGuard→同E5BAndroidGuardIO（Os.lstat/O_NOFOLLOW open/fstat、ParcelFD.dup、真实flock、unlock及两个原FD close）。E5B生产Guard、恢复、观察、Admission、Lifecycle没有新接口或字节修改。

夹具平台只放行本case两条精确路径/role/epoch/expected实例，实际existingGuard完全委托原Android适配器。死亡、recoveryOwner、sync、metadata force/close接口直接拒绝，不能假冒成功。适配器构造不做磁盘恢复动作。完整observe从未调用，actualReturnProven必须仍false，原静态live grant先null且后相同；原恢复及观察retained计数进入前必须0，产品session/slot必须0。

## 隔离及负例

仅既有com.videokit.app主进程、UID10221、Debug可运行；固定新root创建必须CREATE_DIRECTORY成功，0700。既有root阻断，不扫描它、不重置、不换名。三子目录healthy/owner_symlink/lease_symlink；每例自有随机任务、epoch、账本ID，own-identity.txt/own-ledger.txt/own-payload.bin仅合成自有字节（R/S计数0），不含真实原N2 task/budget/ledger。死亡及metadata前提明确ASSUMED_SYNTHETIC_NOT_EXECUTED。

健康通过两次原锁获取并实际关闭。负例先无覆盖move原guard到同目录相邻.original-target，再Os.symlink用相对文件名指回原inode；lstat S_IFLNK、readlink精确目标、目标regular且原dev/inode/UID/length、跟随stat同dev/inode、目标原SHA证实真链接。owner负例仅登记第1holder后拒绝，lease负例先获取健康owner再第2holder拒绝，随后关闭原owner。错误必须是原生产E5B_EXISTING_GUARD_ROLE_LENGTH_UID，不能把任意异常作预期PASS。

附加原AndroidIO O_NOFOLLOW探针要求真实ELOOP且预登记holder的close返回；它支持系统语义，不替代观察边界拒绝。生产负例lstat先拒绝，FD未分配会明确NONE_PREOPEN_REJECTION，不能虚称其关闭了某个打开的FD。健康已分配guard反射读原descriptor，实际raw/dup closeAttempted及原FileDescriptor.valid=false后才标CLOSED；UNKNOWN单列且不PASS。

每例链接设置后、边界前后的有限NOFOLLOW清单对比路径/类型/dev/inode/UID/mode/regular length/SHA/link target，忽略访问时间。无新节点、metadata/ledger/payload字节变化、R/S计数变化、live grant。只扫自有root子树，不扫app、缓存、媒体、原预算/输出。最终自有root总限额另查。

## 所有权及时限

注册Run后才调用worker，原observer在任何反射lock前强引用登记；原类holder在factory前登记。自有write/read/原探针也先注册E4Owned，最多128个IO holder；实际物理节点最多64（含目录/链接）、regular及link target数据合计256KiB、单regular64KiB。日志总限4MiB，实际更紧64事件/每事件4096字符。限定3例1次，不能重用root。所有路径受root限制，链接不遍历。

单方法从开始算60s，host只等待剩余时间，worker各阶段/读写检查原deadline。超时不cancel、不shutdownNow、不替代close或删root；报告PENDING/actualReturn UNKNOWN并保持原Run/worker/observer/holder强引用。晚返回不升级已超时结果，worker不再开始后续case；原close可能继续真实返回。该截止不是强杀不可返回系统调用的承诺，系统调用不返回时资源仍PENDING。close仅原worker在OPEN/READY时尝试，UNKNOWN/CLOSING不重试。失败保留整个root及Run（成功也保留root及已闭合Run，进程consume门不可重跑）。仪器系统结束不是协议close证据。

## 明确未覆盖

本机仅逻辑边界与编译，Android实际链接/FD/flock均NOT_RUN。原N2死亡证据、metadata验证、force/sync、全observe/live admission、ABORT/settlement及正常媒体编码均未执行。G01是否补齐取决于将来的真实证据和独立审查，不继承WindowsJunction为真文件链接证据；原Windows1314 NOT_RUN保留。
