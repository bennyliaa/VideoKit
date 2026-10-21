# C04 单App / 独立Kit隔离与AC3条件方案

日期：2026-10-05。本文件为研究与架构评估，所有C04设备项目NOT_RUN；不是已实现产品准入。额外不同UID companion仅获D1实验授权，未批准产品额外安装包。同UID多进程只有崩溃边界，仍可访问宿主权限与私有数据，不能满足P0权限隔离。

## 单APK与Kit候选边界

Android12普通isolated进程不能通过Manifest声明获得任意codec/GPU访问。C04增加独立codec API探针，但尚未设备执行；C03普通start/broker失败不证明codec权限，companion导出1001也未证明完整硬件路径。平台特权或isolated_compute不是普通App/Kit的通用绕过手段。

可研究单APK CPU边界：普通isolated service执行经许可审查的CPU解封装、解码、检测、跟踪与遮罩，SourceBroker按task/owner/epoch供给有界字节。宿主普通UID只接收经布局、长度、步幅、尺寸及时间戳校验的有限PCM、像素/遮罩块，使用OS编码、显示与音频。不能把不可信压缩媒体交回宿主native解析，再宣称风险已隔离。共享内存须解决TOCTOU，优先有界复制或不可变封装；FD、Writer与输出仍遵守撤销、真实租约、确定死亡及独立验证后READY门禁。

Kit需约定宿主Manifest合并、service与接口版本、任务授权、签名/UID校验、最小IPC面、全局并发/队列/缓冲预算、provider断连及失败恢复。SDK无法自行授予普通isolated硬件权限。CPU decoder与模型权利、API兼容、性能/功耗、恶意native崩溃/OOM、像素验证和长时资源回收尚未实现，方案仍BLOCKED。

不同UID companion可用signature permission与精确宿主UID限制入口，但具有更多Binder/GPU能力，攻击面大于普通isolated。真实codec/GPU/FD、并行崩溃与回收还需设备证明；单App/Kit发行与额外APK签名分发需产品决策，不能弱化P0来默认采用。

## AC3条件方案与准入

先用同一手机MP4/MKV手动听音与格式、支持程度、选择、renderer/session/sink/focus证据定位。[Media3支持格式](https://developer.android.com/media/media3/exoplayer/supported-formats)区分容器与样本格式支持；容器能播放不保证每台设备AC3 decoder可用。现象不能单独确定无声根因。C04没有集成外部decoder、FFmpeg二进制或新权重。

闭源发行可评估商用decoder，必须获得Android/ABI、再分发、SDK转授权与专利条件的明确合同；具体供应商尚未准入。另一有条件路线是LGPL构建FFmpeg AC3：[FFmpeg8.0 AC3 decoder源](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavcodec/ac3dec.c)为LGPL2.1+，[FFmpeg法律说明](https://ffmpeg.org/legal.html)区分GPL/nonfree配置与义务；[Media3 FFmpeg扩展说明](https://raw.githubusercontent.com/androidx/media/1.9.3/libraries/decoder_ffmpeg/README.md)提供构建路径。

必须固定版本/构建选项，禁用GPL/nonfree依赖，避免误启用libx264等；优先动态链接。许可证/notice、对应源码与修改、替换或重新链接能力、反向工程条款、包完整性、专利/地域义务均需审查。LGPL不意味着免义务或自动专利清算，静态链接闭源尤其不能默认通过。仅启用AC3 decoder不自动完成准入。未完成法律/发行条件和二进制来源/hash/SBOM审查之前不集成。AC3许可与人脸模型权利是独立门禁。

## 诊断依据与推断限制

[Android12 AMS](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java)只允许isolated instanceName的字母、数字、下划线、点，旧UUID连字符被拒。名称修正静态明确，但旧设备错误链已丢失，不能宣称找回了真实旧cause。

[Media3 1.9.3 ExportException](https://raw.githubusercontent.com/androidx/media/1.9.3/libraries/transformer/src/main/java/androidx/media3/transformer/ExportException.java)定义1001为FAILED_RUNTIME_CHECK。旧日志中的NO_INIT接近release，可能是清理结果，不能确认根因。

[标准InAppMp4Muxer](https://raw.githubusercontent.com/androidx/media/1.9.3/libraries/transformer/src/main/java/androidx/media3/transformer/InAppMp4Muxer.java)声明负时间戳edit list支持、加入视频旋转元数据并过滤可选metadata；C04对齐adapter，但不声称1001已解决，也不放宽独立两轨、PTS及完整decoder门禁。可能负PTS被严格验证拒绝时，必须保留失败事实。

[默认Extractor列表](https://raw.githubusercontent.com/androidx/media/1.9.3/libraries/extractor/src/main/java/androidx/media3/extractor/DefaultExtractorsFactory.java)包含AVI，默认顺序可先sniff WAV。需实际阶段日志识别阻塞，不能凭WAV一条日志定根因。
