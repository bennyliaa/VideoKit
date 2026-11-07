# VideoKit 项目工作规则

- 用户已于2026-10-23明确恢复开发测试，当前按负责人最新正式整批派单推进；D1未通过/M0未启。历史暂停/停止仅按原时间和范围保留，用户后续明确暂停停止优先；文档更新/版本同步本身不构成恢复或新的设备执行许可。
- 2026-11-06用户决定：技术路线以docs/requirement/15_MEDIA_TECHNOLOGY_DECISIONS.md为准；原D1离线验证工具链不再作为门禁（原证据与状态不改写），D1改为聚焦验证S1–S6并与M0并行。
- 工作前读docs/requirement/00_DEV_DOCS_INDEX.md、12_MILESTONES.md与15_MEDIA_TECHNOLOGY_DECISIONS.md；历史停止/继续指令按准确来源和范围，不复用旧批次。
- 历史资料在项目外：D1证据 `D:\CodexProjects\VideoKit test-workspace\D1`；旧Android原型与交接文档 `D:\CodexProjects\VideoKit test-workspace\archive`；只作参考，不改写。
- 代码、文档和测试按整批开发自测冻结→独立整包测试→集中缺陷回交，禁止逐问题交接，不测试浮动源码。
- 提交代码/文档：仅提交准确本批、保留验证状态、检查diff及许可/密钥/大文件，默认整批分支/PR审阅，不force push/发布或以提交代验收；用户要求时才提交。
- test_media（`D:\CodexProjects\VideoKit test-workspace\test_media`）只读且不入库，原证据/预算/once/FAIL/UNKNOWN不改写。原调用未知不得擅自二close/杀进程/补ACK退款。
