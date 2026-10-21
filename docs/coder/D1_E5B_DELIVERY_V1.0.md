# D1 E5B 完整候选交付 V1.0

2026-10-17。D1-20261017-E5B，新根docs/coder/d1e5b。实现与本机支持场景、离线构建已完成，提交整包静态复审；**真正文件符号链接反例仍为OS权限阻断、NOT_RUN，不将本包说成全部要求已验证。** Android fstat/flock/设备/QUERY/ABORT/观察/真实媒体均未运行。D1未通过、M0未启动、全部P0/JNI与N2/旧signal FAIL保持。

## 修复范围

依据 [E5B需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E5B_CODER_REQUIREMENTS_V1.0.md) 和 [E5A复审](D:/CodexProjects/VideoKit/docs/tester/D1_E5A_ARCHITECTURE_REVIEW_REPORT_V1.0.md) 修E5A-F01/P1。观察与恢复只能调用existingGuard；现存owner/lease使用非创建、NOFOLLOW打开，核实际FD普通文件/UID、owner0B/lease36B与准确fence，path与FD的dev/inode在锁前后及使用/关闭前复核。恢复前像增加82B guard.identity，观察须与实际打开句柄匹配，拒绝事前同字节替代文件。

同时修当前输出任务的原lease重开：初始化owner与首次issue lease仅走独立createNew/O_EXCL接口；workerLeaseClear、READY与abort走openExisting，沿用已捕获身份/epoch。abort先取得既有正确原锁，再写journal，缺失不补或改journal。移除没有调用者的MODE_CREATE旧锁工厂；WorkerLease继续只接已授权PFD，不按路径创建。

相关核账也改为既有READ/WRITE/NOFOLLOW FileChannel；只有全新预算初始化可CREATE_NEW，不再使用可能创建缺失ledger的RandomAccessFile("rw")。旧R/S字节格式、累计实际消费、未知关闭、跨host默认拒与原绝对截止规则保持；没有借缺失或链接清账、换UUID或补元数据。

## 定点证据与明确缺口

最终JVM repair-003通过82项父检查，子进程内部断言另保日志不叠加。16种观察夹具包含健康、missing-owner/lease、两个目录角色、owner1B、lease0/35/37B、错误36B fence、两个同字节替代inode、两个Junction重解析点、缺guard.identity与替代身份记录。直接走生产观察，拒绝项逐原路径/角色/volume-fileID/字节清单不变、无新R/S/live grant，创建接口调用数0；替代身份用实际打开FileChannel的Windows内核句柄属性核验，非仅路径布尔值。

另有直接生产恢复missing-owner/missing-lease两项、正常新任务的两次合法创建/后续非创建重开、缺lease时worker-clear/READY/abort不补写、一个completion-close UNKNOWN及新host明确观察对照、原首次30秒/计时回调迟到定点回归。不重跑旧270项；E5A的Admission/Lifecycle/CallbackGate/DirectoryBarrier逐字节保持，原证据仅引用。

Windows真实句柄核验使用本机JBR的GetFileInformationByHandle包装及volume/fileIndex，模块反射开关仅用于本机工具；UID映射与目录FD替身是模型，不能当Android UID/fstat/flock或目录fsync实测。两个Junction是实际重解析节点，**不是实际文件SymbolicLink**。

普通及提升执行创建真正文件符号链接均失败WinError1314；当前token无该权限，WSL亦不可用，未安装环境或改系统设置。Junction普通沙箱受限，获准在新自有目录运行后通过。[环境门](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/environment-gate.json)。所有前次失败日志保留：main为拒绝前未获锁的fence校验重复导致过度保留，修正后repair-001遇Junction沙箱权限；repair-002支持场景通过；补相关路径后repair-003为最终82项。

已备 [固定源码单次真正符号链接补验脚本](D:/CodexProjects/VideoKit/docs/coder/d1e5b/tools/invoke_true_symlink_once.ps1)，默认INSPECT，只有明确Run、一次ExecutionId和精确freeze SHA才运行；仅在docs/coder/E5B_SYMBOLICLINK_ONCE的新目录编译/生成自有夹具，将原guard移到本夹具旁再建真正文件符号链接，确保目标仍为原inode，执行同一生产观察并核不创建/不改原字节/无R/S/grant。它不提升权限、不改系统设置、不接设备或媒体；现有权限环境才可由负责人准确派发。该脚本本批未执行，缺口不自动关闭。

## 构建、签名与来源

offline Gradle main-001一次通过，公共Android Os.open/lstat/fstat/pread/pwrite/fcntlInt API编译通过；没有Gradle并发、下载、安装或新fault。最终build输入SHA256 `8d9004bfd016ca1aed4340b67e2d020b03bebc4c58a3f93b99ac17d0cb4a091e`。

| 角色 | 字节 | SHA-256 | 文件 |
|---|---:|---|---|
| app-debug | 10527157 | `324247d61e0c6bab7e218cd859cd7b857572ce17a87e67e0cf941d5d3b60694a` | [APK](D:/CodexProjects/VideoKit/docs/coder/d1e5b/artifacts/D1-20261017-E5B/final/app-debug.apk) |
| androidTest | 2718585 | `63b5d31f74190d8be2e32870bce24ea0e88a3f665f4bb901a04e2e4fa6942708` | [APK](D:/CodexProjects/VideoKit/docs/coder/d1e5b/artifacts/D1-20261017-E5B/final/app-debug-androidTest.apk) |

两包证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f` 与E5A/E5/E4A一致；appIdcom.videokit.app / test、versionCode4/D1-E5B、原两非导出服务/权限，无INTERNET/companion。35 Maven坐标、七native字节差异0，Media3 1.9.3/FFmpeg8.0.3及完整C14对应源码/NOTICE许可映射保留，不宣称许可、安全或发布放行。

[定点JVM结果](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/local-check-results.json)；[构建](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/build-results.json)；[最终输入](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/final-build-inputs.json)；[签名/Manifest/native审计](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/apk-audit.json)；[所有相关原打开调用审计](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/original-open-audit.json)；[未回退组件](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/preserved-invariants.json)；[SBOM差异](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/sbom-difference.json)。

完整 [源码ZIP](D:/CodexProjects/VideoKit/docs/coder/d1e5b/artifacts/D1-20261017-E5B/D1-20261017-E5B-source.zip) 包含最终源/工具、必要旧来源摘要、新定点日志/自有夹具、四文档与完整C14对应源；没有重复复制E5A的2243项自检产物，无密钥/local.properties/build/classes/缓存/真实媒体。双APK独立immutable。[外freeze](D:/CodexProjects/VideoKit/docs/coder/d1e5b/evidence/e5b-freeze.json)绑定精确成员；ZIP和freeze自身SHA在集中交接外列，避免循环。只读复核：Python -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1e5b/tools/e5_package.py verify。

直接基线E5A2247项与native来源E4A207项共2454 immutable只读核验，旧seal一致。旧候选/工具/报告/设备fixture/缓存/预算/失败现场未改。本次仅提交审查，符号链接实测缺口须单列；不自动派发部署、QUERY、恢复或产品回归。
