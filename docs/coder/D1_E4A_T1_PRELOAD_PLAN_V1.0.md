# D1 E4A-T1 一次预置计划调整 V1.0

2026-10-17。提案D1-E4A-T1P-TABLET-20261017，**executionAuthorized=false、实际预置NOT_RUN**。须负责人先集中独立审查T1冻结，再另派准确一次平板批次；不得用本计划补传。产品E4A不重建/重装，旧工具/产品冻结和81407B设备残件保持，D1未通过/M0未启动。

## T1新增收尾门

- 实际分配过的原stdin必须正常close返回；只要抛错/未返回，即便原客户端exit0、writer/source/其他pipe结束，也保UNKNOWN_RETAINED及原Job/process/stdin/source/参数。后续collect/transfer_file拒绝，不二次close/补传/换路线。
- 确认尚未调用allocator的可执行文件预检拒绝，不虚构process/stdin或成功close；仍需原source确实关闭。要求绝对普通非symlink可执行文件，无PATH隐式搜索。已进入构造但返回不明保守UNKNOWN，不从异常文本推断无分配。
- 原关闭在迟后实际返回，只允许观察原close/source/drains/wait/线程事实释放本机资源占用；原超时attempt仍NOT_ADMITTED，不续期、不发布、不自动下一步。UNKNOWN期间不得重启工具解释器洗全局owner；保原进程状态和包外收据报告负责人。
- 本机故意UNKNOWN case各在独立解释器退出，不是正式流程的恢复方法，OS退出清理不计归还。

## 唯一目标与准备

仅平板HA1Q6WXR、com.videokit.app、user0；手机不查询/催启用，模拟器不操作。原Binder PASS不重跑，不运行正常/取消/三quarantine。正式tester必要只读确认一次实际设备/包/签名/enabled/空间及run-as id/pwd、父目录普通非symlink、toybox工具支持，不能从旧scope错误输出猜目录为空。预检失败即停，不安装、清数据、删cache/marker或换包名。

使用冻结tools/fixture_transfer.py的provision_once与其同目录T1 exact_process.py；防止sys.path误导入旧T版本。执行前按外seal验证整包及输入源码，不测浮动文件。--plan只构造字符串/sourceOpened=false，不打开source或调用ADB；只有另行正式派发后才允许AdbBackend(execution_authorized=True)。布尔护栏不是授权凭据。

## MP4先保留残件，再一次新临时传输

| 项 | 精确值 |
|---|---|
| 原残件路径/身份 | files/e4_fixtures/basic.mp4，81407B，SHA a790f44fc3c6ff4579c83f57b42a4b31cd95278cca28fd4aa6b97fd295fd9695 |
| 不覆盖归档名 | files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep |
| T1全新临时名 | files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part |
| 最终fixture | files/e4_fixtures/basic.mp4 |
| 唯一attempt | E4AT1P_TABLET_20261017_basic_once |
| 历史授权源声明 | D:/CodexProjects/VideoKit/test_media/imgs_and_videos/videos/sample.mp4，349102B，SHA720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 |

本窗口未stat/读取上述媒体或设备。正式批次先在新tester证据目录CREATE_NEW attempt并flush/fsync，再核原残件长度与完整SHA（超81407先拒绝不hash），归档名不存在才同目录无覆盖改名，独立核归档前后同字节及原名消失。缺失/不符/归档冲突即停，不猜已归档，不删除。

新temp必须不存在，旧目标碰撞只查metadata不全hash。源同一只读FD先完整长度/SHA，再归零进行唯一二进制producer；64KiB块，实际write计数/SHA、并发stdout/stderr、flush/close/wait/原owner证明齐备后只得PROCESS_IO_COMPLETE_ONLY。任一失败保原文件和UNKNOWN，不重开临时名。

独立进程先stat限本文件349102B、再sha256sum；准确长度/hash匹配后，固定路径再次确认空，同目录mv -n发布，再独立核最终长度/hash与temp消失才FIXTURE_ADMITTED。多层引用、Android cat/mv/sha行为仍未实际验证；不支持或回执未知即停，不改命令路线补跑。rename可能完成但证明失败时不自动rollback/再次rename。

## AVI仅在MP4完全准入后首次一次

历史授权源D:/CodexProjects/VideoKit/test_media/02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi，736454656B，SHA3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f。本窗口未访问。最终files/e4_fixtures/subtitle.avi必须不存在；temp为files/e4_fixtures/.subtitle.E4AT1P_TABLET_20261017_once.part，attempt E4AT1P_TABLET_20261017_avi_once。

沿相同生产pump/独立校验/同目录发布，producer只有一次。MP4任何失败都不读AVI。失败保临时文件，不续传、删除、覆盖或更换渠道；原fixture/源/cache/预算和marker不改。

## 接入、预算与归档

精确JSON仍在tools/tablet-preload-plan.json。正式tester可按旧T已审接入形态逐文件调用provision_once，source/expected/final/temp/attempt/residual/archive从**本T1**计划读取；先外部准入再显式构造AdbBackend，失败即break。包外保存原backend.logs及attempt/events/result，不能向冻结d1e4at1目录追加收据。不得在UNKNOWN时启动新Python绕过registry，或复用旧T pump。

| 全两文件成功的计划量，非已发生用量 | B |
|---|---:|
| 唯一producer payload | 736803758 |
| host完整prehash+同FD流式读取 | 1473607516 |
| 新临时及发布后两次完整hash | 1473607516 |
| 原残件归档前后hash | 162814 |
| 设备计划总hash内容读取 | 1473770330 |
| 新增数据峰值 | 736803758 |
| 新件及仍保留残件合计 | 736885165 |

同目录rename不增第二份payload；历史APK/cache/其他文件及安全余量单列，不清理凑空间。源只读，无shell文本编码/base64变换。每进程stdout/stderr各1MiB、额外至多16KiB块后拒绝，各留64KiB前缀；64KiB源块。整体证据8MiB由正式tester包外累计核门并保存首因/原返回，超额停不丢证据。

MP4过程60s、AVI300s、metadata/hash每命令≤120s、cleanup共同2s。普通OS open/read或不返回调用没有可强制中断硬界；本机客户端结束不证明远端owner结束。stat后hash的内容字节界依赖合作式稳定普通文件，不宣称抵御恶意并发增长。父目录/UID/权限和空间未知即停，不加时/重跑求通过。

完成或受阻都交负责人集中报告，不自动继续产品测试。具体截断层次UNKNOWN，E4A-N PASS1/BLOCKED9、旧P0/历史FAIL保持；实际预置须独立审查后另行派发。
