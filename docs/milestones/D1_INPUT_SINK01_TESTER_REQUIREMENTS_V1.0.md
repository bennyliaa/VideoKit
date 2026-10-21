# D1_INPUT_SINK01 并行离线测试及整包复审要求

2026-10-20；正式批次D1_INPUT_SINK01，属于原D1第3/4项可行性缺口，不启动M0。目标是实际宿主readAt→既定Media3 DataSource薄适配、授权临时OutputSink能力/事务与重新打开验证接线，不是新播放器/编辑器/资源框架或最终公共API冻结。旧RENDER02产品/capture/已停止设备scope和UNKNOWN保持原字节。

按项目已定Media31.9.3及原平台接口，复用已有AsyncReadBridge/LeaseRegistry/sourceVersion/epoch和成熟muxer，禁止自造codec/容器/网络/NAS/凭据层或扩FFmpeg音频。若所需Media3 DataSource模块尚不在当前缓存，允许仅同精确版本必要官方artifact/POM/传递依赖来源、许可和校验准入；不能偷偷升级/关闭metadata校验或先用同名假接口宣称接入。新依赖身份/许可与既有差异完整交独立review，无法合法取得则对应集成BLOCKED，但继续可独立完成的真实薄适配。

有限离线数据固定生成seed/hash；最大8MiB样本，逻辑偏移用稀疏/受控provider验证2GiB以上和溢出，不分配巨大文件；单块≤64KiB、每源读在途1/队列≤4、总同时源≤2、输出≤16MiB，不把这些候选预算冻结为产品阈值。超时仅停止新准入并保管原资源，原close/worker真实返回前不发布SourceReleased，不退款UNKNOWN。

阶段A现在正式派发，可与coder并行：仅对已冻结RENDER02 AsyncReadBridge/LeaseRegistry与已审E11/E13F输出Sink来源做独立离线读源码/受控宿主边界测试，先记录准确source pins；核短读/未知长度/2GiB以上/取消迟到/双consumer归还、partial write/close失败/重新打开/READY与COMMIT分层，整理可直接用于新批的独立用例及当前真实缺口。测试代码和所有输出只在tester新目录，不改产品/冻结源、不读coder新目录浮动源码。若来源的平台依赖无法本机运行，静态审证与NOT_RUN分列，不能编假Sink成功代实际输出验证。

本阶段不运行Gradle/Android构建或共享可变缓存，允许使用已有JDK在tester独立目录编译有限检查；避免与coder构建并发冲突。严禁设备/ADB/5037/占用查询，不重复检查环境。阶段A集中提交D1_INPUT_SINK01_OFFLINE_BASELINE_REPORT_V1.0.md和独立用例/原来源pins/完整发现，主动通知负责人，不逐问题向coder打断。

阶段B等coder完整冻结及负责人交测后，独立核新DataSource实际框架接口与源/Sink适配实现、依赖许可/metadata、身份与原始构建/自测证据；运行本阶段独立边界回归和差异验证，一份整包报告所有缺陷交负责人集中修复。A报告不冒新候选已测，B本机PASS也不冒实际播放/编辑/设备危险链通过。原D1/P0及真实媒体尚未测保持分栏，不自动M0。
