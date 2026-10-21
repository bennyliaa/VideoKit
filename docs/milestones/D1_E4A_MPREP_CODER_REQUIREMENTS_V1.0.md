# D1 E4A-MPREP 真实样本预置完整入口开发需求 V1.0

2026-10-17。T6P唯一256B实机完整通过，采纳本轮单写者探针及ASCII解码/独立SHA事实，不清旧失败或归因。现集中完成MP4和AVI真实样本预置工具及执行计划，新小d1e4amprep，产品E4A冻结不改，不新增APK/Gradle。

复用T6已证流式Base64/原强close/完整响应/单父probe/receiver，按精确文件大小/原SHA参数化，不整片缓存或落主机编码副本。固定两源仅来自旧future-media-plan.json；coder不stat/read/hash真实媒体，不设备。新增可审固定manifest/准确CLI允许后续tester一次整批条件顺序执行MP4→AVI，先MP4实际独立准入/原owner归还/外部receipt落盘才允许AVI，不用任意非空摘要自证。发生任何失败/未知立即停依赖，不自动重传或换路。

MP4 raw349102/SHA720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9，无LF465472；AVI raw736454656/SHA3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f，无LF981939544。总raw736803758/wire982405016/host raw两遍1473607516，编码两遍生成1964810032不落盘；独立设备hash每源一次最大n，再发布后核可增加一次n但须明确预算总量。流式raw24576/encoded32768/carry2/工作预算256KiB非RSS。原pump1GiB encoded界不扩，AVI时限600s从预hash前开始，MP460s；独立hashMP415s/AVI120s。空间先核容纳两源+历史文件/余量，不删凑预算。

新准确私有temp目录及两文件，独立临时前后stat+有界rawSHA/原UID/非symlink/长度正确；发布到files/e4_fixtures/basic.mp4及subtitle.avi须先正证父可访问/目标不存在，原归档basic.mp4.E4AN_PREP01_81407_a790f44f.keep保持不动/不再次归档。合作式同目录无覆盖发布采用已审mv-n后独立身份/长度SHA与temp消失，不把mv返回0当已发布；若为同一文件系统跨目录rename保持devinode核对，不复制额外整片。任何目标/temp存在不覆盖/删件/猜已准备。旧26B/T6P状态/输出cache/budget不访问修改。

为减少交接，计划一次交付两文件预置/发布完整工具与未来原四媒体相关方法准备（normalMP4/normalAVI/capability/cancel），产品方法本工具不自动执行/不重跑Binder。tester后续一次正式批次可以预置完集中报告再产品测试，执行许可另由负责人。全日志<=8MiB、metadata总界/每命令/readhash预算/receipt持久一次attempt明确；所有首因/失败产物/UNKNOWN原解释器handle保留。精确使用本机环境/原sdk，无新依赖。

本机自有合成有限证据验证大于64KiB参数/发布路径、短件/错误SHA/冲突/中途失败阻断AVI/原close未知和不退款，不重复全历史。完整交D1_E4A_MPREP_DELIVERY/PRELOAD_PLAN_V1.0.md、最小工具/外seal ZIP/只读核验/真实范围证据，完整主动报告。coder不ADB/真实媒体/Gradle/模型下载。D1未通过/M0未启动/P0历史FAIL保持。
