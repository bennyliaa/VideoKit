# D1 RENDER01 整批验证入口与证据边界

2026-10-20；仅供负责人制定后续正式派单。**当前所有Android运行/效果均NOT_RUN，没有现场查询、安装、启动或音频输出。** 不复用RESUME/ENV03已停止scope，不以长期真机授权代替本候选精确身份/预算和设备占用门，不操作其他项目。ENV03只是最后接受报告的占用事实，本批没有查当前现场。

## 接收与停止

先独立核完整freeze/源码、最终APK/test hash、签名、构建来源、自检与已知差距、硬预算和本批后端/许可决定。独立空沙箱包是 `com.videokit.d1present`，不是旧包更新；负责人尚须明确接受此身份及fixture准备/测试范围。不得在禁用手机安装新包绕过原限制，也不修改旧VideoKit数据、once、registry或UNKNOWN。

正式派发后才按新鲜占用/环境、精确APK身份和原资源前置执行。四方法为同一冻结候选的完整功能簇，**每个方法独立准确invocation/新进程**，每次先确认无本候选未知原owner；不能在单一instrumentation中整class重复以重置预算。`renderCase`须与唯一`class`方法相等，`renderScopeSha256`为负责人届时批准范围的准确hash；源码只验证选择语法，不自行构造执行权限。custom runner复用原E13FinishOwner，原WorkSession/线程/source未返时不finish。

设备包/fixture准备、观测次数/字节/客户端生命周期等须由负责人另给完整实际预算；本文件不生成claim、release、once、SDK命令或新执行框架。任何错误先保留真实第一失败与资源状态；未知停后继并保管，禁止清数据/卸载/kill/二次close或换scope求绿。若权限/危险链评审不能接受，只报告具体BLOCKED，不为测得效果绕过。

## 已实现的Android入口

runner `com.videokit.d1present.RenderInstrumentation`；唯一测试类 `com.videokit.d1present.RenderDeviceTests`。test manifest限制 `android:targetProcesses="com.videokit.d1present:presentation"`；@Before实际校验同进程，否则在媒体操作前失败。

| ID/精确方法 | 前置与实际预期 | 独立证据及不能扩大的结论 |
|---|---|---|
| RA-01 generatedMutedDualConsumers | 无外部媒体；默认静音。真实六次Canvas提交、576000B PCM提交/播放头排空，原render/audio/bridge/coordinator归还，pixel held0，raw queue≤2/PCM queue≤4 | 保存D1_RENDER_FRAME逐帧PTS/producer/play epoch/surface代次和D1_RENDER_CONSUMER真实registry快照；首consumer关闭必须sourceReleased=false。生成画面不是解码，静音API不是听音PASS |
| RA-02 existingMp4RawMutedDualConsumers | 此新包私有fixture basic.mp4长349102、SHA720957c9…0a6a1f9，来源与只读准备已接受。六个原C14 CPU任务依次真返，原PTS/rotation传递，呈现与PCM正常收尾 | 保存C14原出生/UID/PID/代次/STOP/death/source账目及逐帧呈现回执；独立截图核画面。该PCM仍是生成测试声，不是该MP4音轨；不代替NAS/持续播放器 |
| RA-03 cancelRejectsLateGeneration | 使用预暂停生成源，必须先等已打开的实际raw工作在途、无其他setup失败且source未释放，再取消；旧epoch/surface拒绝，只接受无错误或准确SESSION_CANCELLED | 这是平台调用前的队列/源取消，不冒充Canvas/native write在途取消。原JVM受控blocked-port用例另覆盖逻辑保管；实际永久UNKNOWN仍NOT_RUN |
| RA-04 pausedSeekAndSurfaceRecreation | 在start前暂停，走真实TextureView移除/重建、旧SurfaceTexture转交、seek代次变化；UI意图时ACK=false，恢复后至少1且≤6个新epoch/new surface提交，原owner/source归还 | 全程默认静音；保存新旧epoch/generation和回执。检查方向及画面需外部截图，不以counter代替。此控制是有限snapshot，不是任意连续Seek |

RA-01/02正常入口不允许0帧/0PCM绿灯；RA-03不接受与取消无关的初始化错误；RA-04不接受只有metadata没有真实提交。所有结果仍须独立原始资源审证，不能仅采信返回字符串。

## 同包人工/效果项目

| ID | 具体操作/预期 | 结果记录要求 |
|---|---|---|
| RA-VIS | 在同一次已批准RA-01/02/04流程按实际窗口采集本Activity截图；对应FrameReceipt最后实际PTS/rotation与画面 | 生成图：原左半红、原上半绿，各帧蓝值变化，alpha255；90°为平台顺时针，目标视口只等比适配。真实MP4用已授权帧作对照。不存在截图/看不清则NOT_RUN，不假造画面 |
| RA-SOUND | 单独准确派发技术Activity的一次明确“Listen”动作：从未启动状态点击后才生成并播放3秒低幅PCM；再核Mute、pause/epoch/stop与原归还 | 需真实操作者/时间/听到的实际现象，或已批准回环。仅AudioTrack/write/播放头/focus返回不能登记听音通过；不自动开启麦克风/录音/网络 |
| RA-FOCUS | 在批准且不影响其他项目的条件下核焦点授予、全静音、取消与唯一owner；实际失焦情形须有合法明确前置 | 不为制造失焦操作其他项目或任意App，不用本机AudioFocusPolicy PASS替代AudioManager。条件缺失则NOT_RUN，不能新增不明第二发声源 |
| RA-LIFE | 区分借用的View texture和转交后的原texture；检查原Surface/Bitmap/texture释放、原输入/owner及focus回调线程归还 | API不返回就保管原对象并停止；外部进程消失/窗口消失不是原Java/pipe/holder ACK。UI原生分配/BufferQueue/AudioServer峰值另测，64MiB ledger不代RSS |

技术Activity没有launcher且exported=false，不因这个计划擅自启动。一次有限session最多6帧/30秒，声音最多3秒；一进程不重复start。截图/听音可与准确已派单场景同次收证，不能为理想结果不断重启。

## 本机与设备证据的分栏

最终本机自检直接调用实际core/bridge/registry和真实Java线程，只在Canvas/AudioTrack端使用明确有界port。它能证明队列/owner/epoch/焦点策略/双consumer和late-return逻辑，不能证明Surface、音频服务、真实画面/听音、温度或故障隔离。Android集中构建只验证API/打包，不能把任何本文件用例登记PASS。

完整一次报告应列四方法及人工项的实际前置、执行/未执行、第一失败、每个原对象和原客户端终态、帧与原来源身份、输入/输出/资源量、阈值、截图/操作者证据及不能关闭的门。发现缺陷整批回负责人集中派修复，不单按钮反复交测。本候选不关闭压缩音轨、跟踪、全危险链、独立Kit、M0或D1整体。
