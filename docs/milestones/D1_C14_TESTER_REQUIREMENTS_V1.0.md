# D1 C14 编码能力协商与真实帧管线测试需求 V1.0

日期：2026-10-16；状态：正式整包交接，负责人独立冻结核验PASS。按冻结73可调度项执行，另2项保留NOT_RUN_UNCHANGED_PLATFORM_LIMIT；不Gradle。

基线为原始需求、D1架构评审、C13最终报告与D1_C14_CODER_REQUIREMENTS。C13实际52 PASS/3 FAIL/14 BLOCKED及手机69环境阻断保持；不得用C14成功回写旧报告。

## 正式交接后的集中核验

1. 独立校验冻结ZIP/源码/证据/APK/签名/编译方法与计划、锁定框架与完整源NOTICE/SBOM、release无实验。确认只有限公开编码能力适配，未新增自制codec、未扩FFmpeg许可或宿主压缩源解析。
2. 两设备授权已有。现场核serial/API/ABI/页大小/用途/hash签名/空间，手机→平板串行且tester独占、不Gradle。手机仍禁用有限预检后环境BLOCKED继续平板，不强启/卸载清数据/变包名绕过、不再找不存在按钮。明确用途同签名更新前备份身份及可读数据，旧fixture/capture/报告全部保留。
3. 真实MP4/AVI新管线各一次，完整保存候选能力、顺序、每次格式/诊断、关闭证明及最终选中结果；总尝试数/deadline事先冻结。能力声称不代替实际配置，首失败不能隐匿；前候选未实际释放不得新建下一。实际configure失败与CAPABILITY_UNSUPPORTED/环境区别，不改PASS。无编码能力则依赖BLOCKED。
4. 六真实源帧/输入/输出样本/隔离EOF六帧及实际PTS/画面阈值全部验证。无音频仅技术探针，host正式H264/AAC双轨与恢复独立回归；有限多snapshot不当实时性能。新配置不能以换合成帧、取消独立验证、降阈值或宿主读压缩源过关。
5. 测能力反例、configure拒绝有限下一候选、全部拒绝、关闭失败/取消/在途不重选、尝试上限与脱敏诊断；分清Debug注入和实际设备CodecException。C13十四未进入反例完整验证，特别是实际Sink写flush/截断/READY响应丢失、消费者在途取消、另一真实任务及第二encoder许可，失败先停止外调度核在途再独立项。
6. 统一保守8份RGBA1179648B+YUV55296B静态限界，实际数组/队列/引用与峰值另列，不冒充RSS。Source、逐代次death/绑定、codec/Image/callback、FD/writer/owner/队列/consumer分别审核，超时PENDING不能释放许可。单输出2MiB、pipeline累计4MiB/24journal、全部新输出8MiB/48任务、日志32MiB，写入时限额。素材只读核hash，不删旧证据凑额度。
7. 受影响CPU身份/注册/解绑/预算/取消及host/legacy回归依冻结计划。未改变退出采集时不重跑两个历史同条件SIGSEGV，明确NOT_RUN_UNCHANGED_PLATFORM_LIMIT，保留C13-T02 FAIL和trace/ordinary OPEN，绝不计新PASS或D1通过。若正式交接另列真实采集改动才依据具体审批验证；不得自行改变signal0规则或用raw回填。
8. 评审全P0/独立Kit/Flutter/完整危险链/跟踪与模型权利/真实标签/手机/16KiB和发行OPEN，内部命名沿既定决定，不因实验成功直接进M0。真显示/音频、完整双轨与模型质量不能由视频专用链外推。

整批交docs/tester/D1_C14_TEST_REPORT_V1.0.md，列所有实际PASS/FAIL/BLOCKED/UNKNOWN/NOT_RUN与集中缺陷、预算/素材和最终在途状态。不改产品源码、冻结件或自派下一批；任务完成事件供负责人收取，不反复跨窗口通知。D1未通过、不进入M0。

正式交接预算决定：新增encoder反例可能产生额外journal，为完整执行73项，将整批新task/journal记录上限由32明确为48，pipeline仍24journal/4MiB、单输出2MiB、全部新输出8MiB、日志32MiB。仅调整记录数量，无功能门槛变化；执行前核空间，不事后删记录，不突破冻结App内额度，接近任一额度时停调度报告。
