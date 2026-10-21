# D1 E4A-T6P 私有 ASCII 流唯一实机诊断报告 V1.0

日期：2026-10-17，约11:10；tester。设备HA1Q6WXR；批次D1-E4A-T6P-TABLET-20261017；nonce E4T6P_TABLET_20261017_ONCE。依据 `docs/milestones/D1_E4A_T6P_TESTER_REQUIREMENTS_V1.0.md` 执行已审固定CLI一次。

**结论：PASS_DIAGNOSTIC_ONLY。** 原结果 `ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE`：顺序探针完整通过，一次原始256B→编码344B接收成功，独立新命令确认私有目标原始长度/前后stat/SHA全部一致。E4AT5P-F01在本轮唯一单写者实机回归中通过，未再出现交织；这不是压力稳定性或全设备结论。新增问题0。未执行媒体/产品，D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL保持。

## 1. 冻结及一次性执行

执行前新证据目录不存在，准确入口 `docs/coder/d1e4at6/tools/diagnose_ascii_once.py --execute --formal-batch D1-E4A-T6P-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_T6P_EVIDENCE`。主CLI正常退出0，未改冻结源码/JSON、无重试。

只读verify PASS：52源/54不可变；外seal SHA `861d2e179c66801f80353d79c6c2420a10f5748dfdd090db991a95e3ac0d6f37`；ZIP86977B/SHA `73bef2bc282e4474e53f9d867bc317d8ee5f6928c64ed7418a706b557b8be681`。固定准确导入T6及原T1强owner机制。仅主机权限提升连接既有ADB，设备未root/改权限。

## 2. 全部实际原调用

所有调用原exit0、stderr0B、PROCESS_IO_COMPLETE_ONLY、RETURNED，原stdout完整未截断。metadata使用固定shell -n -T -e none及run-as原app；唯一producer去掉-n。

| 顺序/原JSON | 阶段 | elapsed | stdout B | stdin B |
| --- | --- | ---: | ---: | ---: |
| 00-features.json | 精确shell_v2完整features | 0.078s | 220 | 0 |
| 01-original-context.json | 原身份/files/新目录不存在 | 0.157s | 83 | 0 |
| 02-uid-snapshot.json | 一次原UID快照 | 0.156s | 417 | 0 |
| 03-new-private-directory.json | 独占新准确私有目录 | 0.156s | 85 | 0 |
| 04-one-byte-sequential-file-probe.json | 两文件顺序probe | 0.281s | 348 | 0 |
| 05-one-base64-receiver.json | 唯一编码流接收 | 0.219s | 372 | 344 |
| 06-independent-raw-proof.json | 独立原始文件校验 | 0.219s | 308 | 0 |

context确认UID10221、pwd `/data/user/0/com.videokit.app`、files目录非链接、新目录当时不存在。UID快照仅见self23005及toybox ps23009，未见本协议识别的旧receiver线索；这只是一帧原UID观察，不证明全部历史远端资源归还，priorRemoteOwnership仍UNKNOWN_NOT_CLEARED。

## 3. 单父写者探针实际回归

准确新目录 `files/e4_diag_T6P_TABLET_20261017_once` 创建后，顺序写probe.ascii/解码probe.raw，唯一父shell输出四行，原字节CRLF。完整stdout SHA `26088f2c9dec50c52000173e747fe76f461cdbf6b3e0e6ce45fbb69741a621ba`：

```text
T6_PROBE_RC|E4T6P_TABLET_20261017_ONCE|stage=printf|rc=0
T6_PROBE_RC|E4T6P_TABLET_20261017_ONCE|stage=decoder|rc=0
T6_PROBE_RC|E4T6P_TABLET_20261017_ONCE|stage=od|rc=0
T6_PROBE|E4T6P_TABLET_20261017_ONCE|uid=10221|pwd=/data/user/0/com.videokit.app|parentPid=23019|mode=SEQUENTIAL_FILES|asciiStatRc=0|rawStatRc=0|asciiBytes=4|rawBytes=1|hex= 00
```

准确顺序、三端原rc、两stat、parentPid和原身份均通过，hex为单字节00；本机实际返回完整，严格解析通过。设备toybox base64-d及od-N1的本轮用法已实际通过，未放宽解析/重拼标记/忽略异常。

额外状态文件正常两件4B＋1B，在负责人最多4文件/4KiB范围；程序对普通非symlink角色和长度的原门已走通。没有额外pull/hash状态内容、全目录枚举或状态文件独立UID/mode审计，因此不伪造这些附加观察。状态文件保留，不按旧T5“无文件探针”假设处理。

## 4. raw/encoded计量和原receiver证明

同原只读源FD raw预哈希256B、raw流读256B，摘要均 `40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`；达到声明终点、actualRawCloseReturned=true。编码预哈希344B，实际提交344B，摘要均 `ab7727e21f4bbba6508dd72804d97435a78eb44a1e277af1c0f65a8522de382e`，无LF/无编码磁盘副本。原始512B读取与编码688B生成分列，不能把344B提交说成原始落盘计数。peakTrackedBufferBytes853只代表被追踪对象，不是RSS。

唯一准确payload目标 `files/e4_diag_T6P_TABLET_20261017_once/payload256.bin`。完整原stdout SHA `edf92388638e1024774d5fa0213cb63b9532e2d3372c0ff55ab907abd15dec10`：

```text
T6_BEGIN|E4T6P_TABLET_20261017_ONCE|uid=10221|pwd=/data/user/0/com.videokit.app|pid=23033|path=files/e4_diag_T6P_TABLET_20261017_once/payload256.bin
T6_DECODE|E4T6P_TABLET_20261017_ONCE|rc=0
T6_END|E4T6P_TABLET_20261017_ONCE|uid=10221|pwd=/data/user/0/com.videokit.app|pid=23033|path=files/e4_diag_T6P_TABLET_20261017_once/payload256.bin|decoderRc=0|statRc=0|bytes=256
```

BEGIN/END同PID23033、UID/pwd/nonce/准确目标一致，原DECODE0、stat0、raw256。receiverObservation与receiverProof一致。原host source/stdin/管道/wait实际返回门通过，未仅凭编码提交或exit0判成功。

## 5. 独立raw proof

另条新run-as命令确认普通非symlink目标、原UID、长度256、前后stat一致，最多head-c256原始SHA符合：

| 字段 | 原实际值 |
| --- | --- |
| uid / pwd | 10221 / /data/user/0/com.videokit.app |
| path | files/e4_diag_T6P_TABLET_20261017_once/payload256.bin |
| before / after | 64522,19424,256,10221,8180,1792206618（完全相同） |
| stat解释 | dev64522、inode19424、256B、UID10221、普通文件0600、mtime1792206618 |
| 原始SHA | 40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880 |
| 完整原stdout SHA | c5fef9011d416df6fa1107e8f51d5575ccc74c4262c8edf6b3bc31c424142e86 |

该命令独立于producer的END计数；没有把后续观察回填旧失败attempt。证明范围是本轮合成文件字节，不是fsync/durability、播放、产品COMMIT或旧二进制截断原因定位。T3旧26B、81407B及旧T5P失败仍保持原事实。

## 6. 实际预算、归还与范围

metadata6≤20，producer1；各原elapsed0.078—0.281s≤15s，原共同本机归还观察2s未出现UNKNOWN。raw源读取512B、编码预哈希＋提交688B（仅提交344B）；设备额外probe写4＋1B、od最多读1B，独立payload hash256B。新增准确目录一处；按固定写路径和原stat共正常状态2件5B＋payload1件256B=3件261B，未列目录推断其他文件总数。

原记录1828/1968/2572/2145/4318/4314/3152B，均≤64KiB；attempt+7原JSON+result共24814B<1MiB，后续tester报告/审计另计。最大单流417B<4KiB保留/16KiB硬界，均完整；stderr全0。全部原stdin/source实际close、writer/flush、stdout/stderr close和原exit观察均通过，errors空、creationUnknown=false、stdinCloseError=null，无owned-child强制终止。本机retainedLocalOwners0、无在途；历史远端UNKNOWN_NOT_CLEARED未清零。

未访问外部路径/push、旧残件、MP4/AVI或媒体，未操作手机/安装/Gradle/Binder/预算/产品方法/权限/manifest/root/signal；无补传、改令、换路、加时、重试、清理或自动下一批。所有新诊断产物保留，attempt已消费。

## 7. 证据与交付

原证据 `docs/tester/D1_E4A_T6P_EVIDENCE`：attempt.json、result.json、7原调用JSON及对应stdout原字节文本。receipt-audit.json逐原完整字节/SHA、归还、raw/encoded计数及proof核验PASS；audit.py只读本机现有回执，不再调用设备或重新hash设备内容。每份原JSON SHA见receipt-audit.json，足够定位全部准确原调用。

本报告主动发送负责人。E4AT5P-F01的本轮实机回归通过；设备ASCII合成传输路线获得256B证据，后续MP4/AVI、fixture无覆盖发布和原产品测试仍须负责人另派。成功不自动媒体预置，D1未通过、M0未启动、历史问题不关闭。
