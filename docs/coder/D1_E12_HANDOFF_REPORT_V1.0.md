E12完整交付，请安排tester独立只读审查；下一实现批次尚未启动。

正式需求已保存：
docs/milestones/D1_E12_CODER_REQUIREMENTS_V1.0.md
docs/milestones/D1_E12_TESTER_REQUIREMENTS_V1.0.md

主件（均在D:/CodexProjects/VideoKit/docs/coder）：
D1_E12_DELIVERY_V1.0.md
D1_E12_REQUIREMENT_EVIDENCE_MATRIX_V1.0.md
D1_E12_REMAINING_GATE_DECISION_V1.0.md
D1_E12_NEXT_BATCH_CODER_REQUIREMENTS_PROPOSAL_V1.0.md
D1_E12_NEXT_BATCH_TESTER_REQUIREMENTS_PROPOSAL_V1.0.md

已逐条映射原文§26–31的99条具体要求，另列§28里程碑/§30十份设计交付、§4全部13项P0和J01–J11；31个原始文件精确pins、原字节reference副本、SOURCE_INDEX/SOURCE_LOCATIONS及结构化requirement-rows随包。当前源码与历史R2位置分开，J03–J05已迁到同UID codec进程，不能仍写全在宿主，也不能将同UID当权限/RCE隔离。

接受的E11报告SHA60eb18e88e346e49ec34491083f2b67da21670d7cd5fde40ce3b72ba8246b635支持唯一保数据部署、四独立host当前观察、两6帧READY、能力零开源与条件取消、全部原资源和五PC自然归还。E6B-OBS-F01只记CLOSED_LIMITED_E11_CROSS_HOST，不外推长期/重启/UNKNOWN。历史E6B AVI Before失败、2026-10-16 C13 self系统signal0严格FAIL、外部raw11及另一方法系统11分别保留，C14两项NOT_RUN_UNCHANGED_PLATFORM_LIMIT与ordinary UNKNOWN不变。当前接受账本214483B/7R7S/reserved0，原107218B/1011B前缀、fence/历史产物/oldCloseACK=false保持；这里只引用报告时点，未在线重读。

剩余门：
1. 普通发送者：exported=false/内核UID/实例代码存在，缺实际第三方普通UID拒绝及授权正对照。
2. UNKNOWN：原owner/permit/callback/runner不结束门存在；四正常方法不证明真实永久未知收尾。旧close-unproven为quarantine，用E11 runner硬选它不合法。
3. source聚合：一个CPU结束不等所有consumer归还；迟到open/read、双消费者与SourceReleased语义仍关键D1缺口。
4. renderer/audio：当前六帧不含Surface/AudioTrack/Flutter，无已准入PCM解码路线；先定source→raw→render/audio owner/代次/真实归还，禁止扩FFmpeg音频。
5. 独立Kit：当前SET只app、BUILD application，不是AAR；D1先定无Browser/宿主硬编码/另装产品依赖和接口可提取性，M0模块API/Fake、M7独立构建/双宿主/可移除回退，未把全部M7塞入D1。
6. host lease/file JNI、字幕图片GL与全危险链、模型/样本权利/最低质量路线、手机差异、发行许可/长期等继续OPEN/BLOCKED。
7. OSS初估仅Flutter确定。当前实际Media3 muxer+系统MediaCodec/受限FFmpeg，不是ExoPlayer/Transformer/Coil/OpenCV/ONNX/Flutter已全部接入；保留成熟组件薄适配方向，不自造媒体/跟踪框架。7native/35Maven与原版本不扩，受限Debug准入不等闭源发行准入。

下一完整实现提案暂称E13、PROPOSAL_ONLY：普通发送者与授权source资源生命周期簇，六精确入口为ordinarySenderCannotBindCodec、authorizedHostSourceReadAndClose、oldGenerationNeverOpensSource、twoConsumersHoldSourceUntilLastReturn、cancelLateOpenRetainsOriginalOwner、lateReadAndCloseFailureDoNotReleaseEarly。跨UID绑定拒绝与内部Binder校验分栏，未取得endpoint不冒称内部onTransact实测；同UID旧代拒绝不当RCE防护。一次集中构建app/test及Debug负例fixture，不另立安全/取消/诊断框架。建议实验source4096B非媒体、累计读≤64KiB/open≤8/close≤16且不超原实现允许次数；6入口各一次、每项观察≤30秒、全批process≤48/文本≤2MiB、新媒体输出/READY/R/S=0。正式版本/身份/具体派单仍须你采纳锁定。这些数值不是新执行许可。

永久UNKNOWN/故障/真实OOM/重启/长期方法数量0；先做原接口可返回错误与强保留证据，没有既有可审持续保管/观察/停止出口就提交BLOCKED，禁止为JUnit结束强杀、第二close、换UUID或拿替身归还覆盖原资源。renderer/audio与Kit交具体边界/依赖差距材料，实际显示声音另整簇提议。常规真机授权已给，未来按正式范围执行且其他项目占用则等待，不重复询问用户。

封装与只读验证：
docs/coder/D1-20261018-E12-audit.zip
244399B，SHA256 678f9029dc34435d60f68ae0ee708f0c02474a88986852acf2de4c4f8c2395ca
docs/coder/d1e12/e12-freeze.json
10565B，SHA256 6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640
docs/coder/D1_E12_FINAL_READONLY_VERIFICATION_V1.0.json
PASS_E12_READONLY_DOCUMENTARY_VERIFICATION；ZIP45项、外置封印46行，31输入及副本一致。基础E11的375项和R1的65项及两原seal全部未变（各层行数不相加冒充唯一文件数）。未运行候选构建、自检、旧测试、设备或媒体，只有新文档和本地字节哈希审计；文档标题解析首次出错已修复，交付如实记录，不算产品FAIL。后生成handoff/通知回执明确在封印之外，seal不自哈希。

请独立tester核原文逐条映射、证据范围/历史FAIL、下一整批提案的可实施性与预算，必要修改集中反馈；由你审查后正式派发实现。我未实现下一批，不宣布D1通过，D1 NOT_PASSED / M0 NOT_STARTED。
