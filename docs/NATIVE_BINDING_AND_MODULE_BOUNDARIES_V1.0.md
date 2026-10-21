# VideoKit 原生绑定与模块边界

V1.0；2026-10-21；当前设计基线，非实现/性能/许可验收证明。项目PAUSED_WAITING_USER，D1未过/M0未启；仅文档更新，不派开发、补测、设备或恢复自动跟进。

## 1. 唯一职责分配

| 产物/层 | 实现/依赖 | 持有内容 / 禁止依赖 |
| --- | --- | --- |
| videokit-api | 平台无关语义；Android语言封装 | DTO/接口；不含Media3/Context/UI/模型/宿主数据库 |
| videokit-core/playback | Android Kotlin串行会话+公共策略 | 唯一会话状态/源租约/任务；不在C++或Dart复制同权状态机 |
| videokit-media3 | Kotlin/Java→固定Media3 | Android数据源/解码/Surface/音频薄适配；不经C++重造解码链 |
| shared/domain+schema | 可移植编辑计划/变换/轨迹数据，C++边界设计 | 不持Activity、凭据、平台播放器；Android复用范围实施前明确，不因此强制一切播放过JNI |
| bindings/c | 仅共享原生能力的稳定C ABI | opaque handles/固定宽整数/structSize/version；不传STL/异常 |
| bindings/flutter | Dart typed facade+Android Kotlin平台通道 | 命令/事件/快照；独立于Flutter页面，不为每次UI重编模型 |
| image/timeline/effects/tracking/export | 原模块边界的可选功能artifact | 纯播放不强制模型/编码器；编辑接口引用通用源/计划 |
| speech-recognition/translation | 独立可选adapter/模型manifest | whisper/llama代码与模型隔离，ggml符号/版本处理须显式验证 |
| videokit-ui | 可选Compose/View原生UI | Flutter不强嵌此UI；原生宿主可不安装Flutter |
| apps/videokit-app | Flutter页面/Theme/国际化/宿主源输出 | 不包含Browser业务；SkinKit当前不接 |

上述为设计产物表，不新增构建任务或声称已有所有artifact。Apple/Windows仍M9，各平台binding遵同一语义，不将Android平台类塞C ABI。

## 2. 数据与调用路径

AndroidFlutter命令→平台通道→会话executor→Media3；回调→有界事件聚合→Dart主isolate。帧走平台纹理/Surface，PCM走原生有界buffer lease，禁止按帧/音频块经Dart消息往返。其他原生宿主直接调平台SDK；共享C++编辑计划走JNI/C ABI，控制事件与媒体数据通道分离。具体Flutter插件/引擎版本实施前冻结。

异步readAt只由媒体工作线程申请，不同步FFI等待UI执行器。若C ABI消费异步句柄，提交request并回completion，buffer由lease明确retain/release；不能把Dart对象指针交后台长期持有。每次回调带bindingGeneration/timelineEpoch，线程归属/可重入性/取消以及原返query是binding合同组成。

## 3. 生命周期责任

平台backend持Surface/codec；Flutter adapter只持纹理注册ID及显示lease。detach先通知backend停止引用，再注销纹理，离屏策略由宿主决定；UI树销毁不等媒体资源已返。原生handle通过registry按owner验证，整数handle不可跨进程照搬；IPC使用broker token。request取消后不能释放仍被原生读写的buffer。

错误在原生映射稳定code+typedArgs，Flutter只渲染本地化；Locale切换不重置插件或backend。依赖锁、SBOM/NOTICE随各artifact，不把跨平台语义一致当实现/许可证/图像一致。

## 4. 验收

BIND-01纯播放与原生宿主无Flutter/AI/编码强依赖；BIND-02通道过期/重复/错线程和buffer原返；BIND-03纹理重建/后台/旋转与codec释放；BIND-04版本拒绝与独立构建；BIND-05源码包/最终产物依赖和许可证。按M0/M1/M7/M8/M9分层待测，不增加D1临时框架。
