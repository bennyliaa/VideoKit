# RENDER02 集中独立复审及未来设备计划

2026-10-20；**当前设备运行及人工听音全部 NOT_RUN**。本文件不派发、不生成 scope 或一次性许可。先独立接收本候选 seal、精确 APK/test/hash/签名、元数据新准入及三项修复，再由负责人决定未来准确范围、预算、现场占用和 fixture。原停止的 scope 不复用，不以长期授权替代本批准入，不在禁用设备绕过原限制。

## 精确身份和共用前置

runner component 为 `com.videokit.d1present.test/com.videokit.d1present.RenderInstrumentation`；类为 `com.videokit.d1present.RenderDeviceTests`；Activity 为 `com.videokit.d1present.PresentationActivity`（exported=false、无 launcher）。instrumentation 只针对 `com.videokit.d1present:presentation`，同包 startActivitySync 可以启动该 Activity，未新增外部启动能力。

每次只选择一个准确方法，独立新进程；`class=类全名#方法`、`renderCase=方法`，`renderScopeSha256=负责人正式批准范围的64位hash`。源码只校验语法，不能签发权限。原 owner 未知时停止，不能强杀或重启以制造新进程。安装、私有 fixture、设备前置观测的次数/字节/客户端生命周期须另经准确派单；本文件不执行这些动作。

## 保留的四个静音自动方法

| 方法 | 前置及证据 |
|---|---|
| generatedMutedDualConsumers | 生成源、六个真实 bitmap/post 回执、576000B PCM API/排空、首 consumer 关闭仍未整体释放、原所有 owner/source/像素归还 |
| existingMp4RawMutedDualConsumers | 已批准私有 `files/d1_render_fixtures/basic.mp4`，349102B、SHA256 `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`；原 C14 read-only raw 路径六帧、PTS/旋转及原 CPU 归还；不是该 MP4 压缩音轨 |
| cancelRejectsLateGeneration | 预暂停、真实 raw 在途/源未释放、无 unrelated setup failure 后取消；旧代拒绝，原归还后收证；不能替代在途平台调用的实机证明 |
| pausedSeekAndSurfaceRecreation | 预暂停、真实 TextureView 重建和转交、seek、新 epoch/surface 回执、原 owner 归还；方向/画面需外部截图 |

四项均**不传 renderManual**，默认静音，任何传入 manual 参数在 @Before 拒绝。正常方法不得接受0帧/0PCM，取消只允许准确取消语义，不用 unrelated 初始化失败冒充通过。新 receipt 含 `bitmapDrawn=true postReturned=true currentAfterPost=...`；counter 不代替截图。

## 第五入口：真正闲置到完整三秒 Listen

唯一方法 `manualIdleListenThreeSeconds`。准确参数为：

```text
component = com.videokit.d1present.test/com.videokit.d1present.RenderInstrumentation
class = com.videokit.d1present.RenderDeviceTests#manualIdleListenThreeSeconds
renderCase = manualIdleListenThreeSeconds
renderManual = IDLE_LISTEN_3S_V1
renderScopeSha256 = <负责人届时正式批准范围的准确64位hash>
```

这些是未来 invocation 参数说明，没有执行命令。缺少 manual 值、class/method 不相等、进程不符均在启动媒体前拒绝。不要用整类运行、外部 am start、改 exported 或先运行静音方法来替代。

1. instrumentation 在同包启动 Activity，并设置内部 `renderManualIdle=true`。此模式隐藏自动启动按钮，Listen 初始 disabled；**此时 session=null，没有生产线程或声输出**。
2. 最多5秒等待真实 SurfaceTexture 可用；失败则不继续。随后在 UI arm 一次窗口并打印 `RENDER02_MANUAL_IDLE_READY`。从 UI arm 的单调时间起最多15秒，只接受一次真实 Listen 点击；等待及 marker 不自动开始 PCM。
3. 操作者在15秒内点击“明确听音：从闲置启动完整3秒低幅声 / Listen”。同包 UI claim 窗口并在 session.start 前设置初始 audible，启动独立生成画面+固定 PCM。若已存在任何 session，明确报 `LISTEN_REQUIRES_IDLE_NO_RUNNING_SUBSTITUTE`；不把部分已消费的静音音源转响充当完整三秒。
4. PCM 为自生成 PCM16/48k/stereo，576000B/3秒，seed1447764006，SHA256 `268d0e111f05ef5ad7ba405df6b78e5e8f6b3a43ebd926c48429d139a27da4ff`，峰值257、平台gain0.15，需实际焦点授予。听不到、焦点拒绝/失焦或用户取消如实报告；禁止自动录音/麦克风/网络或引入第二未知声源。声学环境及允许设备音量由负责人正式前置决定。
5. 未点击超时：UI 同步关闭窗口，late click 被拒绝，禁用按钮；session仍null则正常关闭闲置 Activity，并报告未完成听音，不能算PASS。点击恰逢关闭由 UI/同步窗口串行裁决，不双启动。
6. 已启动后，最多30秒观察同一 WorkSession 的原 owner/coordinator/bridge/source 归还（session自身硬窗30秒、最多6帧；不是保证30秒内 native 返回）。核576000B提交、failure、sourceReleased、pixels0和原线程。完成日志明确为 `RENDER02_MANUAL_LIFECYCLE_ONLY ... actualListening=REQUIRES_INDEPENDENT_HUMAN_EVIDENCE`；测试返回不自动登记听音PASS。
7. @After 对已有session只发取消，只有该原session真实returned才finish Activity；runner沿用E13FinishOwner，全部原线程/source未返则不finish instrumentation。API/close未知时原持有者继续保管，停止后继，不能kill、二次close、清数据、卸载、退款/换scope。闲置未启动则无 WorkSession 待返。

准备≤5秒+点击窗≤15秒+原归还观察≤30秒；UI调度/API停顿不是可保证总时限，超时绝不当归还证明。操作者另提供实际开始/点击/结束时间、是否听到连续三秒、异常/焦点变化和独立原始证据。无人参与始终 **NOT_RUN**。

## 集中报告

独立复审先核官方新来源与 pin 是否足够准入，再重放本机严格校验及受控竞态；不得将 coder 的新来源检查当独立审批。未来设备整批一次报告四自动方法、第五手动项、第一失败、逐帧旧/新代/真实post、原所有对象/客户端终态、原fixture与资源账、截图方向/听音操作者证据及所有 NOT_RUN/BLOCKED。JVM 受控端口不证明 Android Canvas/AudioTrack/RSS/隔离危险链；全 D1/P0、许可与 M0 边界维持。
