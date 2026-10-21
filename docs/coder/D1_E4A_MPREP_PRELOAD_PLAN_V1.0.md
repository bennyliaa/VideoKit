# D1 E4A-MPREP 固定双样本整批预置计划 V1.0

2026-10-17。当前executionAuthorized=false、真实预置NOT_RUN。仅负责人正式派发后tester执行一次整批；无需每文件另造入口。设备HA1Q6WXR，原com.videokit.app/UID10221/pwd /data/user/0/com.videokit.app，固定ADB D:/Android/SDK/platform-tools/adb.exe。

批次D1-E4A-MPREP-TABLET-20261017，nonce E4AMPREP_TABLET_20261017_ONCE，新私有目录files/e4_mprep_TABLET_20261017_once。包外证据目录D:/CodexProjects/VideoKit/docs/tester/D1_E4A_MPREP_EVIDENCE须全新。

## 两个唯一输入

| 项目 | MP4 | AVI |
| --- | --- | --- |
| 原始B | 349102 | 736454656 |
| 无LF编码B | 465472 | 981939544 |
| temp（新目录内） | basic.mp4.part | subtitle.avi.part |
| final | files/e4_fixtures/basic.mp4 | files/e4_fixtures/subtitle.avi |
| producer时限含预hash | 60s | 600s |
| 每次temp/final独立hash时限 | 15s | 120s |

准确host源分别：

```text
D:/CodexProjects/VideoKit/test_media/imgs_and_videos/videos/sample.mp4
D:/CodexProjects/VideoKit/test_media/02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi
```

源SHA分别720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9、3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f。来自旧冻结元数据，本轮coder未重新stat/read/hash。运行时原FD长度/两遍rawSHA必须相符，无替代源、整片缓存、编码副本或重传。

## 固定准入与执行

1. features/原UID/pwd/files角色。正证files/e4_fixtures目录非链接且rwx可访问，两个final不存在，新temp目录不存在。df-k可用空间须至少两源736803758B＋64MiB余量＋5B；旧文件占用留在当前used，不删除腾空间。df格式或空间不满足即停。
2. 一次UID ps观察，疑似旧receiver停不信号；未见不清历史UNKNOWN。独占mkdir准确新目录，umask077；T6单父顺序解码探针使用其中probe.ascii/probe.raw，正常5B，额外状态cap4文件/4KiB。所有原rc/文件长度/hex及完整响应/原归还须准入。
3. MP4前再核正向父访问、准确temp/final冲突及剩余空间。唯一raw→ASCII producer，BEGIN/DECODE/END及raw/encoded事实原样齐全；原owner实际归还后，独立temp前后stat/n/rawSHA。
4. 核同device/父UID/原temp stamp，合作式mv-n发布；mv0不是成功证明。必须temp消失、final普通非链接且完整原stamp保持，再另条命令独立final前后stat/n/rawSHA、同dev/inode及temp仍消失。若mv跳过或未知，停，不hash冲突目标或删件回滚。
5. 将MP4 ready连同本批manifest、raw/encoded事实及四原记录引用CREATE_NEW写入包外，flush/fsync/实际close，读回长度SHA并逐内容重核原argv/exit/owner/receiver/temp/publish/final。AVI前再次核验同一真实回执及四原记录和owner0；没有任意receipt SHA输入、READY字符串捷径、从AVI开始或恢复旧批次入口。
6. 仅第五步成功才同批条件继续AVI，按剩余AVI＋64MiB＋5B再次df及冲突门，再执行同样唯一producer/temp证明/无覆盖rename/final证明/ready回执。任一步失败立即阻断后续，保留全部目录/部分件/已发布文件和原回执，不重试/换路/加时/覆盖或清理。
7. 两源完成集中报告TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS；不自动产品测试。普通元数据观察不是掉电持久性或恶意并发隔离；旧远端UNKNOWN保持。

原basic.mp4.E4AN_PREP01_81407_a790f44f.keep不读写/不再归档；旧26B/T6P状态/cache/budget不访问。任何目标/temp已存在都拒绝，不猜已准备。fixture父必须现成可访问，不创建或修改权限；不使用外部路径/root/manifest改动。

## 整批预算

host raw两遍1473607516B，编码两遍生成1964810032B而不落盘，wire982405016B；device temp与final各独立hash一次，每源最多2n，总1473607516B。新增payload736803758B＋probe5B，rename不额外整片copy。初始free须按KiB向上取整满足上述新增＋64MiB，AVI前剩余门重新观察；不是空间预留保证。

metadata计划13/硬20、producer每源1；普通metadata15s、producer60/600s、每次hash15/120s、共同本机归还观察2s。日志8MiB、单artifact128KiB、预留最终result；本机ready元数据重读≤4MiB/128次。raw块24576/编码块32768/carry≤2，工作设计256KiB不等RSS；不扩1GiB编码上界。

原Job/file/process/args在close未知时保留，artifact读写close未知也强持有；不下一设备I/O、不二次close/GC/退出退款，晚归还不恢复旧批次。attempt在首调用前持久CREATE_NEW消费；producer尝试和日志预留失败不退款。若ready已写但fsync或close失败，不能因此放行AVI；记录原首因，保留解释器或已写现场。

## 直接入口

默认仅计划预览，不打开真实源或执行ADB：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4amprep/tools/preload_once.py'
```

正式派发后tester只执行一次以下准确整批入口；formal-batch仅防误用，不是许可凭据：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4amprep/tools/preload_once.py' --execute --formal-batch D1-E4A-MPREP-TABLET-20261017 --evidence-dir 'D:/CodexProjects/VideoKit/docs/tester/D1_E4A_MPREP_EVIDENCE'
```

执行前按集中消息的外seal SHA只读核验，保持已安装E4A产品/testAPK身份，不重建或重装：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/CodexProjects/VideoKit/docs/coder/d1e4amprep/tools/package_tools.py' verify --expected-freeze <外部seal-SHA256>
```

当前固定产品app-debug.apk SHA e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f；testAPK SHA 1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be，包com.videokit.app。tester依既有安装记录核对其适用性，异常停止，不自动安装或拓展设备。

## 产品方法只准备

预置完的原normalMp4SixRealFrames、normalAviSixRealFrames、capabilityDenialDoesNotOpenSource、cancelRejectsWrongEpochOversizeAndLateFrame按tools/product-test-preparation.json另批逐准确方法派发；不自动跑整类/Binder/故障方法。原稳定budget身份及实际正常回执必须独立审查，cancel不能用任意非空SHA或更换budget身份清额度。无手机/模拟器、NAS、Gradle、权限/架构改动。D1未通过/M0未启动/P0和历史FAIL保持。
