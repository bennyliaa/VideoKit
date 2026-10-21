# D1 C02 集中真机验证请求

版本 V1.0；2026-10-05；candidateId `D1-20261005-C02`。状态：**准备完成，设备操作 NOT_RUN**。本请求交负责人统一安排；coder未检查adb连接、安装APK、复制设备文件或执行故障注入。不能把USB授权或测试包可构建当作D1通过。

## 1. 用户需准备的设备和操作

手机、平板分别准备一台 Android12/API31+ 的 ARM64 设备；记录型号、系统版本、ABI、RAM、屏幕/窗口尺寸、刷新率、剩余空间、电量、温度。平台型号与厂家编码器差异必须分栏报告，两台设备不能用一台结果替代。

由负责人通知用户开启开发者选项、USB调试，USB连接电脑，在设备确认本电脑RSA授权并保持解锁；确认允许安装本项目的两个Debug APK，以及复制下述本地测试fixture到App私有目录。请勿启用无线ADB或上传视频。故障批次只退出/发送SIGSEGV给本测试包创建的隔离worker，不终止其它应用；8MiB资源压力不是真实OOM。

基础集合约737MB，含APK与测试输出建议设备至少有1.5GB可用空间；含大MKV集合约3.95GB，建议至少5GB可用空间。时间估算为每台45–90分钟（USB速率、编解码器和人工检查会影响）；遇到失败保留日志、按批次停止，不反复重跑掩盖失败。两个设备顺序测试，不并发占用ADB/Gradle。

## 2. 冻结安装包

目录 `D:\CodexProjects\VideoKit\docs\coder\d1c02\artifacts\D1-20261005-C02`。只安装以下两个复制APK；不使用可变化的app/build产物。未签名Release不安装。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| app-debug.apk | 40623190 | f06b368f9ccf0b173080da6919e353577a84fdf498413fd0206b20c4499ebe88 |
| app-debug-androidTest.apk | 2297041 | 427d4285625843c7868c01d997a9522a43bf41a89da9d7968fa0fd56f8381d05 |

最终以 `d1c02/evidence/freeze-summary.json` 核验，辅助脚本安装前再次核对APK hash。目标包 `com.videokit.app`，测试包 `com.videokit.app.test`，runner `androidx.test.runner.AndroidJUnitRunner`。

## 3. Fixture复制范围

电脑test_media只读，不改变源文件编码、名字或字节；设备副本放在目标App私有目录 `files/d1_c02_fixtures`。API只接收固定不透明URI，真实路径仅由宿主fixture层持有。SRT在读取时内存转UTF8，设备/电脑原副本仍保留原字节。

| 设备别名 | 电脑test_media内相对来源 | 字节 | SHA-256 |
| --- | --- | ---: | --- |
| basic.mp4 | imgs_and_videos/videos/sample.mp4 | 349102 | 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 |
| subtitle.avi | 02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi | 736454656 | 3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f |
| subtitle.srt | 02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.chs.srt | 93550 | d3a44be0636d9ec4d5a2782d1a5d6ceb7141d7bf4f8df2f693d9850f867144bd |
| large.mkv（含大文件批次） | 03_large_files/large_video_over_2GiB.mkv | 3212959911 | 28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26 |

获用户授权后，负责人/指定执行者使用PowerShell；替换真实序列号，所有ADB命令都指定序列号：

```powershell
$d1Adb='D:\Android\SDK\platform-tools\adb.exe'
$d1Python='C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$d1Serial='<手机或平板的真实序列号>'
& $d1Adb devices -l
& $d1Adb -s $d1Serial shell getprop ro.build.version.sdk
& $d1Adb -s $d1Serial shell getprop ro.product.cpu.abilist
& $d1Python 'D:\CodexProjects\VideoKit\docs\coder\d1c02\tools\device_setup.py' --serial $d1Serial --authorized --large
```

`--large`复制全部四项；省略时只复制前三项，此时不能运行MKV测试/全类测试。脚本以流复制，不在共享存储二次落盘；逐副本sha256验证。把准备命令输出保存到对应设备证据目录；本轮无需重新构建。`--authorized`仅记录已获授权的前提，不代替负责人取得授权。

## 4. 测试批次及入口

每台设备记录各批次开始/结束、PASS/FAIL/NOT_RUN、异常代码/超时和宿主是否存活。建议按下面方法名分批执行，测试类统一为 `com.videokit.spike.c02.C02DeviceTests`。

| 批次 | 方法名 | 自动断言/人工补充 |
| --- | --- | --- |
| A 本地与字幕 | playbackMp4、playbackAviSrt、playbackMkvAss | READY、0/25/50/90/99% Seek、字幕轨选择/关闭/开启、资源排空；人工核查正确帧、中文字符、ASS样式、对白同步，编码不支持应作为真实失败报告 |
| B 实际导出 | realEncoderOutput、exportReadyResponseLoss | 500–3500ms剪辑、144高缩放强制重编码、H264/AAC、真实descriptor写入/fsync、重开轨道/样本/时长、同任务ready恢复、源hash不变；人工核查输出画面/音频 |
| C Sink失败/取消 | exportWriteFault、exportFlushFault、exportValidationFault、realPipelineImmediateCancel、writingJournalRecovery | 故障无错误READY、源不变、授权临时输出回收；即刻取消和日志重开已备入口，不代表编码中取消/真实宿主进程kill通过 |
| D 隔离worker | isolatedWorkerDeathAndTimeout | NORMAL、8MiB压力、自身退出、自身SIGSEGV、HANG超时；不同PID/UID、实际Binder death、lease排空、宿主另一路随后可读。记录系统tombstone权限限制；不执行系统全局OOM |
| E 离线可行性 | offlinePlatformFaceFeasibility | 授权AVI帧离线缩小后平台FaceDetector执行；仅输出候选数，不证明检测/跟踪质量或隐私目标完整覆盖 |
| F 手机/平板人工 | ProbeActivity | 旋转/前后台/连续播放、拖动Seek、字幕开关、中文/英文系统和大字体/RTL观察。技术验证UI并非Flutter产品，布局/字幕效果单列，不能据此验收产品国际化 |

单方法模板（按列表替换方法名；日志写在对应设备单独目录，不覆盖冻结候选证据）：

```powershell
$d1Method='playbackMp4'
& $d1Adb -s $d1Serial shell am instrument -w -e class "com.videokit.spike.c02.C02DeviceTests#$d1Method" com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner
& $d1Adb -s $d1Serial shell am start -n com.videokit.app/com.videokit.spike.c02.ProbeActivity --es kind avi
```

全部fixture存在时可运行整个测试类（12个方法），但分批更便于定位；不要把一种设备不支持的AVI/AC3绕过后仍写全通过。ProbeActivity提供MP4/MKV/AVI固定按钮、字幕开关和Media3 Seek；人工需确认字幕关闭确实无残留、Seek后字幕匹配对应对白。

成功导出保存在App缓存 `d1_c02_<taskId>.mp4` 与 `.task`日志；测试stdout打印taskId。验证者在得到用户对测试结果保留的安排后，只通过run-as读取该特定App私有测试输出进行容器/画面核验，不批量读取其它App或用户文件。平台文件观察/权限不可用记NOT_RUN。

尚无编译入口或证据的专项：真实NAS断线/非协作provider、编码中取消、实际宿主kill恢复、真实OOM与同时其它槽存活、12路解码压力、完整图像格式/动画、双音轨、标注质量/长遮挡/出画重入。设备接上不会自动补齐这些；需负责人在后续D1修复批次补齐，禁止本次代标PASS。

## 5. 数据保留与清理

失败/取消输出仅删除宿主为本task授权的临时MP4，状态日志保留供查询。成功输出与日志先保留到负责人完成审查。收集测试日志限本测试范围，不清空设备全局logcat、不抓取无关应用内容。

完成留证后，脚本 `--serial <序列号> --authorized --cleanup` 只移除四个固定fixture别名，不修改电脑源。若用户同意移除本测试安装，依次卸载 `com.videokit.app.test` 和 `com.videokit.app` 可清理该测试App所有私有fixture/缓存/日志；卸载会删除该App数据，应由负责人依据安装前设备状态安排，不能覆盖已有同包名真实数据。不得删除共享存储、使用全目录rm或卸载无关应用。手机、平板分别记录清理状态。

与本请求配套：[C02交付](D1_DELIVERY_D1-20261005-C02.md)、`d1c02/evidence/apk-audit.json`、`d1c02/evidence/freeze-summary.json`。仅负责人统一交tester和通知用户，本窗口不直接派发。
