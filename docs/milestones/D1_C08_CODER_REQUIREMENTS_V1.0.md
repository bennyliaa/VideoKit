# D1 C08 单APK CPU解码有限实验需求

日期：2026-10-05；负责人已读C07交付及独立CPU审核。选择方案A作有限可撤销D1实验，不是最终产品/商店许可准入。授权获取官方FFmpeg n8.0源码并核验来源/hash/完整LICENSE，按已提白名单构建LGPL-only动态库；禁止GPL/nonfree/version3、网络/外部未审库及权重。保留全部源/配置/patch/ELF依赖/许可证/NOTICE/SBOM及已知漏洞记录，仅实验debug引入，不进入release或向外分发。构建发现许可组合不符停止引入并报告。

一次完成最小单APK普通isolated CPU AVI/MPEG4-part2与MP4/H264解封装/解码：自定义opaque token AVIO，broker有界只读/seek，至少取得真实PTS的有效视频帧；宿主不得解析压缩媒体或任意worker返回对象。尺寸/stride/offset/长度/时间戳/task/epoch/UID/PID、在途帧/缓冲/队列预算校验后仅有界复制受控帧。实验不必同时实现完整编辑/模型/全部格式。

单APK/AAR形态包含nonexported isolated服务，不额外安装companion。明确系统显示/编码及宿主JNI仍未证风险，不凭裸帧或单解码成功关闭整个P0。准备正常源、损坏源、worker自身SIGSEGV、挂起有界终止/实际death与SourceReleased、第二任务和宿主存活及无源修改集中测试。任务退出历史signal与原始匹配崩溃事实分别记录；C07历史SIGSEGV自动FAIL不回写，不无限同条件重跑。若公开历史记录signal0仅记录unknown，不把cleanup死亡冒充目标信号证明；真实故障事实须精确匹配独立证据。

同时分析TABLET-C07-01记录差异与证据API的时序/身份选择，能据事实修正则补局部反例，不能凭重试偶然成功或放宽cause门禁。ordinary历史UNKNOWN FAIL保持，不重新派测。

仅本机获取、构建、实现与集中自检，禁止ADB/设备、付费/发布或改C01-C07冻结件及素材。新依赖源码取得/构建不可行或许可未闭合准确BLOCKED，给可执行下一步，不盲目扩大范围。交docs/coder/D1_DELIVERY_D1-20261005-C08.md、许可构建证据与完整冻结候选/hash、集中设备验证说明。正式导出/T01T02及旧恢复门禁不得回退，不进入M0。手机补测另安排。
