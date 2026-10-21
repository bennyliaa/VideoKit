# VideoKit

VideoKit项目源码与设计文档的私人版本库。当前D1未通过、M0未启动，项目暂停；此仓库是工程/文档快照，不是稳定产品发布。

- [当前设计基线](docs/CURRENT_DESIGN_BASELINE_V1.0.md)
- [设计评审索引](docs/DESIGN_REVIEW_V1.0.md)
- [主里程碑](docs/MILESTONES_V1.0.md)
- [GitHub同步与tester提交规则](docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md)

正式App规划为Flutter+自有Theme；当前app目录含Android技术验证工程，不能冒充已完成Flutter产品。Android播放采用Media3，原生Kit独立；ASR/翻译是单列扩展。

仓库保留自有源码/设计/报告与小型元数据。构建缓存、local.properties、用户测试媒体、第三方发行包、生成APK/JAR/大采集文件不纳入Git；本地文件仍保留，历史报告中的这些路径/hash不因同步改写。历史候选可能需要单独合法取得的固定依赖/样本才能复现，初始同步不运行构建或测试。
