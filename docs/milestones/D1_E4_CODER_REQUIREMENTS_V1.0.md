# D1 E4 单APK媒体执行进程边界集中开发需求 V1.0

2026-10-17。E3有限真实IO已验收，转原§27会话故障安全及R2 J01–J11危险链。Android先行/Flutter App/独立Kit/Media3 1.9.3与受限FFmpeg Debug边界不变；本批是D1可行性原型，不是M0产品编码。

负责人明确批准有限原型路线：不可信压缩输入demux/decode继续同APK ordinary isolated UID；系统codec枚举/编码/图像平面/封装及相关JNI放同APK独立受控执行service进程，由它持owner线程/资源，host仅控制/授权broker。该service若同UID只能称崩溃边界，不能称权限/RCE隔离；exported=false、调用者原Binder UID/实例/task/epoch/generation核验，禁止任意文件路径/凭据从host穿透，不增加companion安装包。此批准仅评估可行性，不解除原所有危险链P0。

新docs/coder/d1e4集中实现最小可编译Android Debug实验：参考C14已定六真实帧→AVC/fMP4及四提案有限能力协商，不改C14冻结，Media3薄适配/Android原生公开API复用，复制依赖源码需完整hash关系；不引新第三方包/扩大FFmpeg codec网络/下载模型。拆出codec执行service及broker/typed bounded RGBA帧队列2/encoder1/原资源lease，帧/任务/epoch真实所有权账本与源/Sink关闭验证接口，不经Flutter/Dart运帧。压缩输出验证仍ordinary isolated，不能把host旧MediaExtractor当隔离通过。

至少完整代码路径：正常六帧接续、进程未准备/能力拒绝、取消及迟到帧、service原实例死亡时host/另一真实任务继续、未证资源PENDING不复用、不假READY、重连新代拒旧结果、output只临时授权Sink且不写源。故障注入仅编译到Debug受控自身service，不在本批设备/本机native crash执行；后续将新机制一次设备验证，不能复用旧companion成功或反复同条件求signal。App原因可WORKER_DIED+UNKNOWN并保原系统值，历史signal0严格FAIL不改。

交D1_E4_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md：更新J01–J11逐调用进程/UID/owner/输入信任/完整权限与故障边界/实际资源证明及残留具体缺口，Surface/AudioTrack/图片字幕/跟踪GL不得被编码service覆盖。Android 12手机/平板适配与未来iOS/macOS/Windows adapter只设计不实现。独立Kit/AAR服务命名与宿主权限不绑定Browser；公开API未冻结不擅更全契约。

本批coder只本机开发，尽量集中多小功能后一次主Gradle构建+必要修复重编、有意义JVM/合成IPC规则自检；不ADB/设备/真实PF/播放/native crash/大文件复制。使用已有SDK/cache，缺依赖不联网绕过，给具体阻断。禁止把编译或fake owner tests当实际codec/硬件/隔离通过。

原C14冻结/73待设备与两信号NOT_RUN保持；不轮询设备或催连接。交D1_E4_DELIVERY/DEVICE_EXECUTION_APPENDIX/REMAINING_GATE_REVIEW_V1.0.md与上述架构文档、完整源码ZIP/测试APK与签名/SBOM差异/产物SHA/只读verify/代码与本机自检/设备整批计划（正常前置→独立反例→host/他任务→资源）。一次全部冻结无在途主动报告负责人，等独立审查和正式设备批次，不自行派测。全部P0/历史FAIL/JNI残留按事实追踪，D1未通过/M0未启动。
