# D1 E4A-MPREP 双源整批预置执行报告 V1.0

日期：2026-10-17，约11:32—11:41；tester。设备HA1Q6WXR；原app com.videokit.app/UID10221/pwd `/data/user/0/com.videokit.app`。批次D1-E4A-MPREP-TABLET-20261017，nonce E4AMPREP_TABLET_20261017_ONCE。

**结论：PASS_PRELOAD_ONLY / TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS。** MP4完整接收、temp/final双独立raw证明及ready持久重验通过，原owner0后同批条件继续AVI；AVI同样完成。两源各唯一producer，无覆盖发布保持原dev/inode，两个最终fixture已准备。新增问题0。没有产品方法调用，D1 NOT_PASSED、M0 NOT_STARTED、P0及历史FAIL保持；不自动下一批。

## 1. 授权、冻结及原执行会话

依据 `docs/milestones/D1_E4A_MPREP_EXECUTION_TESTER_REQUIREMENTS_V1.0.md`，明确允许读取两固定媒体并整批预置。执行前包外新证据目录不存在；只读verify PASS：163源/165不可变，seal SHA `96f62df6a902a8b20eab73d97de63ea82321ceffe42c15f983530a245c3b2660`，ZIP236592B/SHA `5c43f62ec601971427ae66bda0fe451c563018c81679c5c07d2f425bb7c01047`。准确源码/继承模块未改。

一次准确入口 `docs/coder/d1e4amprep/tools/preload_once.py --execute --formal-batch D1-E4A-MPREP-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_MPREP_EVIDENCE`。原exec session91743持续观察至正常exit0，未重启或改令。主机权限提升仅用于既有ADB连接；设备无root/权限更改。沿用既有E4A安装记录，无重建重装或新安装身份。

固定manifest SHA `b0502d14f94da71b6f3a96fa2a5ddc30bd3643ca2f2da7fd79aa3d90564360fb`，attempt与两个ready均绑定该身份。attempt已消费，不复用执行。

## 2. 全部实际原调用

下列15调用均原exit0、PROCESS_IO_COMPLETE_ONLY、RETURNED，stderr0B，输出完整未截断。13 metadata、每源producer1；只有producer带编码stdin，其他stdin0B。

| 原JSON编号/阶段 | elapsed | stdout B | stdin B |
| --- | ---: | ---: | ---: |
| 00 features | 0.063s | 220 | 0 |
| 01 initial-admission-space | 0.187s | 241 | 0 |
| 02 uid-snapshot | 0.188s | 423 | 0 |
| 03 exclusive-temp-directory | 0.156s | 85 | 0 |
| 04 serial-decoder-probe | 0.266s | 360 | 0 |
| 05 basic.mp4-guard-space | 0.140s | 323 | 0 |
| 06 basic.mp4-producer | 0.422s | 378 | 465472 |
| 07 basic.mp4-temp-proof | 0.172s | 317 | 0 |
| 08 basic.mp4-publish | 0.204s | 327 | 0 |
| 09 basic.mp4-published-proof | 0.234s | 294 | 0 |
| 10 subtitle.avi-guard-space | 0.172s | 332 | 0 |
| 11 subtitle.avi-producer | 516.562s | 387 | 981939544 |
| 12 subtitle.avi-temp-proof | 1.797s | 329 | 0 |
| 13 subtitle.avi-publish | 0.234s | 342 | 0 |
| 14 subtitle.avi-published-proof | 1.828s | 306 | 0 |

全部准确argv、原字节/长度/SHA、计量/exit/close及失败字段保存于对应原JSON。每份原JSON文件SHA和stdout SHA列在receipt-audit.json；stdout另按原字节保存文本，未把控制台显示截断当成原证据缺失。

## 3. 准入、空间和顺序探针

features精确shell_v2通过；原UID/pwd/files及现成fixture父目录非链接/rwx、新temp目录不存在、两个final不存在的门全部走通。仅创建准确新目录 `files/e4_mprep_TABLET_20261017_once`，未补建fixture父或改权限。

初始可用86080584KiB≥785071KiB；MP4前86080564KiB≥785071KiB；AVI前86080216KiB≥784731KiB。均满足剩余raw＋64MiB＋5B并向上取整的原空间门。未删除历史used腾空间、未重复退款；这些是各时点df观察，不是后续空间锁定。

UID快照仅self24001及ps24005，未见本协议识别的旧receiver线索；只说明这帧原UID观察，历史远端仍UNKNOWN_NOT_CLEARED，不追查或清理历史进程。

单父probe parentPid24016，三端printf/decoder/od原rc均0，两stat均0、ASCII4B/raw1B、SEQUENTIAL_FILES、hex00；四行准确有序，UID10221/pwd原值一致。两个状态文件正常5B在cap4文件/4KiB内，保留于新目录。无共享FD3交织，未重复探针或宽松修复回执。

## 4. 两源真实读取与接收证明

host准确源仅：

- basic.mp4：`D:/CodexProjects/VideoKit/test_media/imgs_and_videos/videos/sample.mp4`
- subtitle.avi：`D:/CodexProjects/VideoKit/test_media/02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi`

| 原实际事实 | MP4 | AVI |
| --- | --- | --- |
| raw预哈希 / raw流读 | 349102 / 349102B | 736454656 / 736454656B |
| encoded预哈希 / 实际提交 | 465472 / 465472B | 981939544 / 981939544B |
| raw SHA（预哈希/流读/预期一致） | 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 | 3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f |
| encoded SHA（预哈希/提交一致） | 77a447cee5e5c5111920f4c4d1808a669b8eabd88861c987d2dbca076d1939e6 | 65034ae95f7bf3083eb7cf5e220b7a83dd3f7e8a02d24543cca129f446350520 |
| receiver BEGIN/END PID | 24037 | 24088 |
| DECODE原rc / END decoderRc/statRc | 0 / 0/0 | 0 / 0/0 |
| END原计数 | 349102 | 736454656 |

每源完整BEGIN/DECODE/END准确nonce、同PID、原UID/pwd及准确temp路径一致；raw/encoded原pump计量和摘要绑定通过。source同FD两遍，streamReachedDeclaredEnd/actualRawCloseReturned均true，无编码磁盘副本。达到声明终点不冒充额外EOF探读或恶意并发快照。

raw块24576B/encoded块32768B/carry≤2，两个producer peakTrackedBufferBytes均81920；只是追踪对象，不是进程RSS。AVI516.562s包含预哈希/传输及原返回观察，未超过600s；MP4未超60s。没有加时或重传。

## 5. temp/final独立双证明及无覆盖发布

temp准确路径分别为新目录下basic.mp4.part、subtitle.avi.part；最终路径仅 `files/e4_fixtures/basic.mp4` 与 `files/e4_fixtures/subtitle.avi`。

| 事实 | MP4 | AVI |
| --- | --- | --- |
| temp before/after、PUBLISHED stamp、final before/after | 64522,20198,349102,10221,8180,1792207996 | 64522,20199,736454656,10221,8180,1792208513 |
| 原文件角色/UID/mode | 普通非链接/10221/0600 | 普通非链接/10221/0600 |
| temp独立rawSHA | 与固定原始SHA一致 | 与固定原始SHA一致 |
| 原mvRc / tempAbsent | 0 / 1 | 0 / 1 |
| final独立rawSHA | 与固定原始SHA一致 | 与固定原始SHA一致 |

每源四处stamp完全一致，含dev/inode/size/uid/mode/mtime；fixture父原UID与同device门成立。合作式mv-n没有把跳过返回0当作成功，原temp消失和final完整身份均明确证明，之后另条final hash再次确认temp消失及原n/SHA。无整片copy重复发布、无覆盖或回滚清理。

这是本批两个文件的字节和跨目录rename证据，不是Android fsync/durability、播放或产品COMMIT；没有将新成功回填T3/T4/T5历史失败或旧截断根因。

## 6. ready持久门及MP4→AVI条件

ready均CREATE_NEW、完整正短写/flush/fsync/实际close后读回长度/SHA；立即重核本批receiver/temp/publish/final四份原记录。AVI入口再次读取同一MP4 ready及四记录，重验原argv/exit/owner、raw/encoded计量、完整标记、双独立SHA及同stamp/temp消失；原owner0才进入AVI。不是任意外部receipt SHA或READY字符串。

| ready | 原B | SHA256 |
| --- | ---: | --- |
| basic.mp4-ready.json | 10645 | d5dfbab9201e66a0e95c1f163f4a788c5e1d9cb58e4cffecb4f6f6437388afd8 |
| subtitle.avi-ready.json | 10924 | b1860298fbe076a3ca8ffd8b7402a7a36586333428754a3f79f1ef4294defc4b |

result.mp4Dependency为verifiedOriginalStages4/verifiedContent=true/originalOwnersReturned=true；两源readyVerified均同样通过。本机ready元数据重读15次/77432B，低于128次/4MiB。tester后续只读原回执审计另列，不追加媒体读取或设备命令。ready持久门不等于Windows目录项掉电保证或跨进程恢复授权。

## 7. 实际累计预算、归还与保留

| 项目 | 实际 |
| --- | ---: |
| host raw预哈希＋流读 | 1473607516B |
| encoded两遍生成 / 实际wire | 1964810032B / 982405016B |
| device temp＋final raw hash | 1473607516B，各源各两次n |
| 新媒体占用 | 736803758B，rename不重复copy |
| 探针额外状态/读取 | 2文件5B，od最多1B |
| 调用数 | metadata13≤20，producer每源1 |
| 单原record最大 | 4638B≤128KiB |
| 原artifact总量（attempt/15原记录/两ready/result） | 86126B<8MiB |
| result前累计预留 | 72412B，原预算不退款 |
| 最大单流 | 423B<8KiB完整前缀/16KiB硬界 |
| 本机保留owner / 在途 | 0 / 无 |

15原调用均原exit已观察、stdin/source实际close、writer/flush、stdout/stderr close返回，errors空、creationUnknown=false、stdinCloseError=null，无owned-child强制终止。原session91743已正常结束；没有保留的生产UNKNOWN本机handle。历史远端UNKNOWN_NOT_CLEARED保持，不将本批归还推广为历史全清。

旧81407B归档、旧26B、T6P状态、cache/budget均未访问或再hash，没有再次归档/删件/改名它们。新probe状态文件和新temp目录保留，两个.part的消失来自已证明的无覆盖rename，两个final保留。未列整个目录或额外核旧件，不伪造旧件内容独立复验。

无外部路径/push、NAS/替代源、手机/模拟器、安装/Gradle、权限/manifest/root、Binder、预算标记/产品方法或signal；无重试、换路、加时、清理或自动下一批。仅读取已授权两固定真实源；后续审计额外真实媒体读取0、额外设备调用0。

## 8. 证据和后续

`docs/tester/D1_E4A_MPREP_EVIDENCE` 保留attempt/result、15原调用JSON、两ready及各stdout原字节文本。receipt-audit.json核验原文件长度/SHA、所有原返回、两source/encoded计量、receiver、双proof/同stamp、ready四引用和MP4依赖PASS；audit.py不导入runner、不重新读媒体或调用设备。控制台截断不影响已持久完整JSON。

报告主动发送负责人。本批只完成两fixture准备，normalMp4SixRealFrames/normalAviSixRealFrames及独立negative/cancel等产品验证另行派发；不自动调用。D1未通过、M0未启动、P0与历史FAIL保持。
