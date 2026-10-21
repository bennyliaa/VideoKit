# VideoKit 项目工作规则

- 当前项目PAUSED_WAITING_USER，D1未通过/M0未启；只有用户明确恢复才启动开发或测试。文档更新/版本同步不自动恢复项目。
- 工作前读docs/CURRENT_DESIGN_BASELINE_V1.0.md与docs/MILESTONE_COORDINATION_V1.0.md；历史停止/继续指令按准确来源和范围，不复用旧批次。
- 代码、文档和测试按整批开发自测冻结→独立整包测试→集中缺陷回交，禁止逐问题交接，不测试浮动源码。
- 用户已要求tester在后续开发测试中按需提交代码/文档。遵守docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md：仅提交准确本批、保留验证状态、检查diff及许可/密钥/大文件，后续默认整批分支/PR审阅，不force push/发布或以提交代验收。
- test_media只读且不入库，原证据/预算/once/FAIL/UNKNOWN不改写。原调用未知不得擅自二close/杀进程/补ACK退款。
