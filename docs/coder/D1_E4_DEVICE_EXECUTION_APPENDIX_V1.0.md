# D1 E4 整批设备执行附录 V1.0

2026-10-17。当前仅计划和可编译测试代码，所有设备项 NOT_RUN。先独立静态审查，再由负责人明确设备/批次/现场条件及安装动作；coder没有运行ADB、设备、真实fault、播放或媒体读取。

## 准入与证据

使用本批冻结app Debug APK和instrumentation APK，applicationId仍com.videokit.app，不另装companion。原C14 APK/源码/73项调度/两信号NOT_RUN及历史FAIL只读保留。若正式批次需替换现有Debug安装，tester先归档原安装身份、可读缓存和旧输出，确认App/component/service当前enabled及手机既有阻断状态；不以换applicationId、卸载清数据、强启或反复安装绕过。Android12手机与平板分别记录，平板通过不能覆盖手机阻断或未知。

设备原始记录包括本批APK SHA、签名证书、设备/系统/API/ABI、原安装身份、app及两service实际enabled/exported/isolated/process，host/service/CPU原PID和内核UID、task/epoch/generation/service实例、原Binder death及系统原reason/status。CPU ordinary isolated UID与sameUID codec必须分列；同UID codec只能验崩溃边界。

输入由正式tester预置到目标app私有 `files/e4_fixtures/basic.mp4` 与 `subtitle.avi`，不从本测试自动下载或复制原媒体。本机只引用历史声明：basic349102B，AVI736454656B；精确SHA由测试源码/冻结计划绑定并由设备现场核，不以声明替代当前文件。源前后完整hash、只读源授权及旧capture保护要有原记录。两fixture约736.8MB的只读占用不计新输出，磁盘须有足够空间；验hash读取成本应纳入正式批次，不能暗中增加全文件复制。

测试类是 `com.videokit.spike.e4.E4DeviceTests`。设备方法必须通过精确选择参数运行，不调度整个class自动跑全部fault；确切方法名及顺序由 `tools/device_plan.json` 列出。故障/资源quarantine方法须引用本批、同设备的正常前置receipt SHA；任意非空字符串不能替代负责人核准的真实receipt。源码内参数只是拒绝误调度，不是独立授权系统。未明确准入时没有执行命令可自行运行。

8个编译用例依次为 `normalMp4SixRealFrames`、`normalAviSixRealFrames`、`capabilityDenialDoesNotOpenSource`、`binderRefusesBeforeBeginAndOversizeParcel`、`cancelRejectsWrongEpochOversizeAndLateFrame`、`selfKillOtherCpuContinuesAndOldGenerationRejected`、`nativeSegvOtherCpuContinuesAndOldGenerationRejected`、`closeUnprovenRetainsPermitAndNeverReady`。后三个各为独立最后方法，不自动连续运行。公共参数为精确 `e4Case`、负责人正式批次 `e4Batch`；依赖方法另需 `e4NormalReceiptSha256`，quarantine方法还需 `e4Quarantine=LAST_SINGLE_CASE`。

## 整批顺序

1. 现场只读准入与两APK身份/签名/manifest/fixture核对。环境阻断保持ENVIRONMENT_BLOCKED，未知保持UNKNOWN；不改变系统状态求通过。
2. 先MP4和AVI正常六帧各一次：六真实源snapshot、原PTS/时间基、六编码输入/六样本、实际codec/Image/Sink/worker lease关闭、isolated完整EOF及六帧内容/时间线验证、同task唯一临时token、host原owner关闭。任一正例不成立，依赖codec反例BLOCKED，不以合成图案或旧companion成功替代。
3. 独立有限反例：未BEGIN/未准备帧请求、wrong task/epoch/instance/声明UID、超长/错布局、能力拒绝、取消迟到。区分实际Binder拒绝与纯Java规则，不将改消息里的UID冒称从别App实际发起。能力拒绝可已授空临时目标FD，须实际close；Source0、muxer0、输出样本0、无READY。
4. 原实例死亡边界：codec真正ACTIVE后，另开一个真实isolated CPU任务，使其第一readAt在原5s上限内受控等待；完成两阶段自身service fault，先即时观察原Binder death，再放行原读取并获得真实RGBA。核主Handler及时响应、host原PID存活、另一CPU任务原task/UID/源/实际归还不受损。不能只跑心跳或空闲线程称另一任务成功。
5. 新代metadata重连：原death/旧绑定实际结束后取得新实例及更高generation，实际向新service提交旧身份QUERY被拒，host旧代更新也被拒。明确没有因此创建新encoder或释放旧PENDING许可。
6. close未证等quarantine反例放独立最后方法；保留原对象和许可，不接着跑依赖新encoder的方法。必要的新批次/原进程结束与真实资源核验由负责人另行决定，不能让测试cleanup把未知改成已释放。

每个fault方法独立instrumentation选择，不能一次JUnit自动顺序把未知状态传给下一项。self-kill与native-segv是新的codec执行进程机制，两者各自受正式批次限额约束，不复用或重跑原C14 CPU两信号项。若新机制未抵达预定阶段、arm/commit失效、fault未及时发生或样本不满足，保留实际FAIL/BLOCKED/UNKNOWN，不扩大等待、换注入方法或重跑求理想signal。

## 故障与资源判据

callback同步ACK必须核magic/原hostUID/原实例；发回事件时callbackInFlight=1是事实，只有原ACK返回后QUERY0且callbackUnknown=false才可认回调结束。被卡原生或Binder调用保PENDING/原strong owner；超时和unbind不是系统线程/FD已全部死亡证明。原生close与原参数中所有者的真实返回要独立保存。

App可以报告WORKER_DIED+UNKNOWN，系统reason/status按原值保存。status0为UNKNOWN_FAIL，不能用Debug函数名、ARMED、自报signal、外部raw或最后ps空补成SIGSEGV已证明。新边界的host/另任务存活证据与signal证据分栏；旧signal0严格FAIL、trace缺失及ordinary限制不改判。

固定六帧256×144/5fps提示/600000bps/rotation0，无音频；实际PTS严格递增、相对PTS≤2s，输出解码时间差≤1ms，luma误差≤24、源可区分≥4、输出≥2及映射门槛沿原C14，完整EOF必须六帧。软件encoder可作为有限候选但不能称硬件保证；四提案、12秒协商、60秒总界保持，运行期不重选。

CPU2、encoder1、queue2/consumer1、frame147456B；保守可达RGBA16份2359296B+YUV55296B。Parcel主帧≤196608B/callback≤16384B，service ingress1，有限metadata回调与控制次数见交付文档。这不是RSS/ART/驱动池峰值证明，设备须独立记录内存/FD/线程、已接纳Source/codec/Image/FD/lease/帧/原owner/回调归还。host lease JNI残余须在报告保留。

单输出含头≤2MiB；E4输出私有目录最多128条文件记录、累计4MiB，创建前预留2MiB。每方法输出/日志限额和整批累积量在执行前核算，原输出保留，不删除凑预算。源码当前未提供自动清历史动作。每选定方法日志≤4MiB，整批≤32MiB，接近任一上限即停止依赖调度交负责人。保留所有失败输出、原错误、系统原值与未证账本；实际资源未证则不继续复用编码许可。

结束按每方法实际事实交完整报告：正常前置、独立反例、host/另一真实任务、所有资源/源hash/旧输出、预算、未跑/阻断原因。该批仍不能关闭Surface/AudioTrack/字幕图片/跟踪GL、完整Kit/AAR/Flutter/跨平台/多宿主、权限/RCE或全P0。D1未通过，M0未启动。
