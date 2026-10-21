# D1 E4A-T6P 单写者探针及256B诊断提案 V1.0

2026-10-17。当前executionAuthorized=false，设备NOT_RUN，负责人审查后另派。仅HA1Q6WXR/com.videokit.app/UID10221/pwd /data/user/0/com.videokit.app。

批次D1-E4A-T6P-TABLET-20261017，nonce E4T6P_TABLET_20261017_ONCE，唯一新私有目录files/e4_diag_T6P_TABLET_20261017_once。该目录内准确文件仅：

```text
probe.ascii       固定AA==，正常4B
probe.raw         解码结果，正常一个00字节
payload256.bin    唯一256B实际诊断目标
```

负责人允许的额外诊断状态文件预算最多4个/4KiB；本协议只创建前两个，正常5B。连payload正常三文件261B。全部由原app身份umask077/noclobber创建，失败保留，不清理、不改名、不覆盖、不复用。旧T5P已消费且producer0/目录未创建保持，不据此使用旧nonce或路径。

## 固定顺序

1. features完整成功原响应及原归还门，精确shell_v2。原UID/pwd/files角色、新目录不存在。metadata统一shell-n-T-e none run-as，不换身份/期望或fallback。
2. 一次UID进程观察，疑似旧receiver停不信号；未见仍UNKNOWN_NOT_CLEARED，格式异常停。
3. 原UID独占mkdir准确新目录，umask077；这里开始可能留下产物，不再声称探针无文件。
4. 父shell顺序printf到probe.ascii、取得原rc；条件满足才以前者重定向给base64-d，输出probe.raw并取得原rc；核两文件普通非链接及stat4/1后，od-N1读取至父命令替换并取得原rc。后续未运行就记SKIPPED。所有操作/捕获返回后，**唯一父shell**依次输出三个rc与PROBE。没有管道、后台端点、共享FD3或printf原子假设。
5. 必须严格四行、固定printf/decoder/od顺序，三端rc0、原UID/pwd/parentPid、SEQUENTIAL_FILES、两stat rc0/长度4与1、hex00。原客户端成功和完整长度/SHA/归还也须通过；非零、缺失、截断、重复、乱序或交织全部拒绝，不重拼。失败留目录和原状态文件，payload源未打开、producer0。
6. 只有probe通过，唯一producer才去掉-n，以同原只读FD预哈希后seek并分块标准无LF Base64发送。原BEGIN/DECODE原rc/END须同UID/pwd/PID/准确目标及decoderRc0/statRc0/raw计数256；noclobber直接解码到payload，不经过外部路径。
7. 独立新命令核payload普通非symlink、原UID、stat256、前后元数据和head-c256有界原始SHA。全部证据齐全才记ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE；任何ASCII提交量/exit0/单独后续观察不能替代。

原raw256B/SHA40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880，编码344B/LF0。host raw两遍各256B，编码预哈希344及提交≤344B；额外probe写4B编码/1B解码、od读≤1B，独立device payload hash≤256B。

metadata计划6/硬20、producer1；每metadata/producer15s，共同本机归还观察2s，日志1MiB/单收据64KiB；stdout/stderr各16KiB、保留各4KiB。文件预算不扩为任意写权限。原T1 close强owner/原Job对象保留，未知时不下一I/O、不二次close/GC/退出洗清；超时不证明远端归还，晚归还不升级旧失败attempt。

## 入口与交接

默认只预览，不读源、不启动ADB：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at6/tools/diagnose_ascii_once.py'
```

仅正式派发后tester一次执行，formal-batch是防误用字段而非许可；包外证据目录须全新。

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at6/tools/diagnose_ascii_once.py' --execute --formal-batch D1-E4A-T6P-TABLET-20261017 --evidence-dir 'D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T6P_EVIDENCE'
```

固定ADB D:/Android/SDK/platform-tools/adb.exe。运行前核验集中交付的外seal SHA：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4at6/tools/package_tools.py' verify --expected-freeze <外部seal-SHA256>
```

原attempt、各命令argv/输出/长度SHA/退出/归还状态、probe各端及文件原值、rawSource/encoding/receiver观察与proof/独立raw proof/result全部保留。设备od-N1/解码与新协议实际支持仍UNKNOWN，失败就停，不临时改命令重跑。无外部stage/push、旧残件/媒体stat-read-hash、手机、安装、权限、Gradle、Binder、预算标记、产品方法或自动下一批。

未来媒体设计仅继承tools/future-media-plan.json，当前没有媒体执行入口；256B实证通过后由负责人先恢复MP4批次，再审AVI与原产品测试。D1未通过/M0未启动/P0和历史FAIL保持。
