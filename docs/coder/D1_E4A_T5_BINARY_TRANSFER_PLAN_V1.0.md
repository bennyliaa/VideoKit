# D1 E4A-T5P 私有目录ASCII流诊断提案 V1.0

2026-10-17。负责人审查后另派，当前executionAuthorized=false、设备NOT_RUN。仅HA1Q6WXR/com.videokit.app/UID10221/pwd /data/user/0/com.videokit.app。批次D1-E4A-T5P-TABLET-20261017，nonce E4T5P_TABLET_20261017_ONCE，新目录files/e4_diag_T5P_TABLET_20261017_once，唯一目标其中payload256.bin。

采用T5正式选定的测试专用Base64路线，覆盖旧工具实现选择；不改产品权限/manifest/架构，不再试外部base/Download/push。无root、全局暂存、媒体库发布或新依赖。

## 固定顺序及准入

1. 原features完整成功、原exit/实际归还/长度SHA门通过，精确shell_v2。metadata均shell -n -T -e none run-as，无fallback。
2. 原UID/pwd/files角色，准确新目录不存在；失败保原值，不修改期望或换目录重跑。
3. **无文件写1B解码支持探针**：printf固定AA==（4B）→toybox base64-d→toybox od-An-tx1。原三端各rc通过FD3分别记录，另记pipeline rc/fd3-close rc；都0且hex只一个00才准入。中间decoder失败即便末端exit0也拒绝。不假设pipefail，不将NUL放进shell变量。
4. 一次UID ps快照，疑似旧cat/tee/sh/mksh/head/cp/dd/base64接收或旧线索停止、不信号；未见仍UNKNOWN_NOT_CLEARED，格式异常停止，不认定旧远端资源全部归还。
5. umask077独占mkdir准确私有子目录，无mkdir-p、chmod、清理或旧路径访问；已有目录/目标或symlink即停止。
6. 唯一producer（此命令不带-n）：原同FD raw预哈希后seek0，分块无LF标准Base64 ASCII经stdin发送。目标noclobber，原BEGIN/DECODE原rc/END的UID/pwd/同PID/准确路径/decoderRc/statRc/256计数必须完整且成功；原host source/stdin/管道/wait实际归还必须齐全。
7. 独立新命令核准确私有文件普通非symlink、原UID、stat256、前后元数据及最多256B原始SHA。全部通过才记合成路线通过，不能以344B编码提交或ASCII假设代替。

原receiver非零也保留可证明的部分原标记，不能升级通过。原实际close UNKNOWN保留原Job/file/process/args，不二次close、强GC或退出解释器清零，不下一I/O；晚归还不升级已失败attempt。普通系统调用无法保证强制按时中断，15s不是远端全部归还保证。

## 精确预算

唯一固定源为冻结payload256.bin，0..255原始256B，SHA 40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880；编码恰344B/LF0。raw预哈希与流读各最多256B，编码预哈希344B、提交最多344B，原始计数/SHA与实际编码/提交计数/SHA分列。新设备目标预期256B；独立原始hash≤256B。额外兼容探针只在管道内产生1B，不写文件。

metadata计划6/硬上限20，producer1；每命令/producer15s、本机共同归还观察2s；日志1MiB、每份原收据64KiB、stdout/stderr各16KiB且各保留4KiB。编码原始块24576B/编码块32768B/carry≤2，无整片内存或编码副本；工作缓冲设计预算256KiB，不等于进程RSS。

CREATE_NEW attempt在任何变更前消费；失败留新目录/部分文件和原记录，不补传、不改文件、不重试/换路/加时。不访问或stat/hash旧26B、81407B归档、MP4/AVI，不操作手机/安装/Gradle/Binder/预算标记/产品方法/递归。旧T4失败和全部冻结保持。

## 唯一入口

默认只打印计划，无adb或payload读取：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at5/tools/diagnose_ascii_once.py'
```

负责人正式派发后，tester只运行一次以下新入口；批次标志仅防误用，不构成许可。证据目录必须全新，位于冻结包外，不复用T4/T3的attempt或目录。

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at5/tools/diagnose_ascii_once.py' --execute --formal-batch D1-E4A-T5P-TABLET-20261017 --evidence-dir 'D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T5P_EVIDENCE'
```

固定ADB D:/Android/SDK/platform-tools/adb.exe。执行前用集中交付消息外seal SHA只读核验：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at5/tools/package_tools.py' verify --expected-freeze <外部seal-SHA256>
```

保存attempt.json、每原命令argv/完整有界字节与SHA/退出和归还事实、receiver部分观察与完整proof、独立raw proof和result.json。本机假客户端或Git解码通过不证明设备base64兼容；兼容探针实际失败就停止，不能临时改命令后再试。

未来MP4/AVI准确源旧身份、4×ceil(N/3)流量/内存/时限设计见tools/future-media-plan.json及交付报告；未重查媒体、无媒体执行入口或自动下一批。待256B实际报告通过后，由负责人先审MP4恢复，再审AVI及原产品测试。D1未通过/M0未启动/P0及历史FAIL保持。
