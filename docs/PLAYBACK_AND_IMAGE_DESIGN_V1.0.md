# 视频播放与图片查看设计

## 2026-10-21 国际化详细设计补充（当前有效）

依据[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)及[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，首轮界面支持en/zh-Hans，SYSTEM/EXPLICIT切换与确定性script回退，资源离线完整；界面、字幕、识别、翻译四类语言分别设置，不隐式互改。UI localeGeneration不改变媒体generation/epoch，不重建播放或取消模型任务。

界面RTL不镜像媒体/遮罩，时间轴保留LTR；字幕文本方向依内容语言。

仅文档更新，主阶段/原P0/冻结证据保持，项目PAUSED_WAITING_USER，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

2026-10-21 用户确认：播放复用 Media3/平台播放器，保留统一 PlaybackBackend 隔离平台实现，libmpv不再列正式选型/对照或计划内验证。识别独立模块优先验证whisper.cpp，翻译独立模块评估llama.cpp+适用模型并可替换，平台适配位于各能力底层。自有开发集中统一API/宿主输入/生命周期/预算/字幕时间轴/取消/Flutter UI与编排，不重造解码/音画同步/推理引擎。

播放细节由[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)补齐：Session/Source/Probe/Backend/Transport/Clock/Video/Audio/Track/Subtitle/Snapshot职责、统一接口与取消原返。本文原图片、坐标、格式和多实例P0继续有效；模型字幕为独立扩展，不因新增设计删格式或将当前未证能力标通过。

本节为当前设计；被撤销指令已从执行正文移出，修改前原文见history/design/2026-10-21-consolidation/。历史证据保持，项目继续暂停。

版本：V1.0；日期：2026-10-05；状态：方案草案，格式与性能未经实测。

## 1. 开源与平台后端

Android 首选 Media3 ExoPlayer、轨道选择与其数据源扩展；图片候选 Coil/系统 ImageDecoder，按动画暂停、长图分块和格式实测结果组合，不认为一个图片库涵盖全部 P0。Apple 使用 AVFoundation/ImageIO，图片缓存和动画可评估 SDWebImage；Windows 评估 Media Foundation/WIC。Flutter 控件可依法复用 media_kit 的 MIT 交互组件，但须改成调用 VideoKit binding，不引入未经审批的原生依赖。

平台支持不足时列出具体 container+codec 组合和适配候选，交由设计评审；必需格式不得无记录地移出测试矩阵。播放/图片/编辑导出分别报告 capability。

## 2. 读取与探测

Android 自定义 DataSource 以 DataSpec.position 映射 readAt。同步读取只在媒体工作线程，使用独立可取消 I/O 执行器与有界缓冲，不在 Looper/UI 线程等待宿主回调。probe 和 playback 分别打开句柄；失败释放后再返回稳定错误。

Apple resource loader 适配随机读请求与取消；Windows IMFByteStream 适配 offset/异步完成。是否每种容器能通过该路径读取必须实测，尤其 seekability=SEQUENTIAL_ONLY 时不能伪装可 Seek。

参考：[Media3 DataSource](https://developer.android.com/reference/androidx/media3/datasource/DataSource)、[Apple 资源加载](https://developer.apple.com/documentation/avfoundation/avassetresourceloaderdelegate)、[Windows 字节流](https://learn.microsoft.com/en-us/windows/win32/api/mfobjects/nn-mfobjects-imfbytestream)。

## 3. 会话和控制

一个会话当前只绑定一个媒体。bind 取消旧请求并隔离 generation。连续 Seek latest-wins，报告被替代请求；用户滑动期间 UI 预览位置和实际解码位置区分。音轨/字幕选择按技术身份恢复，失效返回 warning。

保留所有原文控件：播放暂停、快进退、Seek、速度、音量/静音、轨道、全屏方向锁、自由缩放/平移、编辑及 HostAction。无固定上一/下一按钮；图片导航交给宿主。错误/编辑模式的必要控件不自动隐藏。

控件可见性由当前会话输出；编辑工程可请求保持显示。观看量使用实际播放时钟和可见/后台策略，排除缓冲与跳转。全屏不是重建媒体身份；旋转与窗口变化保留会话或明确快照恢复。

## 4. 通用变换与遮罩坐标

定义编码像素空间 E、应用方向元数据后的媒体空间 M、用户观看变换后的显示空间 V、导出空间 O。用户缩放和平移仅作用于 V，默认不改变导出；只有显式编辑裁剪/旋转改变 O。

触摸遮罩通过逆变换 V→M 保存为归一化坐标；预览与导出分别 M→V/M→O。EXIF/视频方向元数据只应用一次；坐标边界、矩阵不可逆及异常尺寸均拒绝。跨平台矩阵顺序、插值与舍入写入 shared schema 黄金测试。

## 5. 图片路径

同一 session 根据媒体类型切换静态/动态解码适配，不创建第二套宿主 API。静态图隐藏全部视频控件；动态图提供播放/暂停/循环，能力报告真实支持。帧延时、循环次数和暂停恢复需测试，不能用首帧截图代替 GIF/WebP 播放。

按屏幕尺寸采样；长图/超大图分块缓存并限制像素、帧数、CPU/GPU 内存。窗口放大时按需提高分辨率。HEIC/HEIF/AVIF 能力随系统和编码变化探测，不只凭后缀。

## 6. 多实例与资源

显示目标独立 attach/detach；离屏可降低刷新/暂停/释放并返回状态。图片不计硬件视频额度，动态图仍计解码工作与内存。所有共享纹理/缓存按引用计数；会话 release 不清空其他会话的活跃资源。

测试覆盖原文全部后缀、大小写、真实容器编码组合、大图、损坏文件、0 字节、2GiB+、旋转、字幕、快速 Seek、1/4/9/12 混排、热压力和句柄归零。缺少样本标 NOT_RUN，禁止用扩展名作为 PASS 证据。

## 集中整理后的执行依据（2026-10-21）

[IMAGE_SUBSYSTEM_DETAILED_DESIGN](IMAGE_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)；[RESOURCE_AND_ISOLATION_DESIGN](RESOURCE_AND_ISOLATION_DESIGN_V1.0.md)。

以上补充现有职责、接口和验收追踪，不新增主阶段或删除原P0。历史设计原文已归档，不再作为并行指令；当前项目暂停，不能以本文触发开发测试。
