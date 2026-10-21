# RENDER02 三项集中修复开发要求

2026-10-20；RENDER02_FIX，正式集中修复3项，依据tester报告c92a0b89b49180fac2db74524dbf7e043cfda6c7ea984074b9b90fe13ba3aed8。RENDER01完整冻结及失败证据保留，新目录新candidate，不就地改旧文件。D1未过M0未启；无SDK/ADB/5037/设备/安装/占用查询，tester不提前设备。

1. P1 META-PROV-01：以独立闭包审计为基础补齐实际消费的父POM/BOM/module/plugin完整清单，确认唯一Guava parent33.3.1-android 20632B观察SHA6e11986ea7250b51f847157e2dc937f32a306804dfce0007a5e81ddb9b95c579的正式仓库/供应方发布来源及原始来源证据。允许仅获取此固定版本所需官方描述/校验材料作为新准入证据，不下载/升级二进制或依赖，不将当前新hash称旧批准，不因本文件即视该hash已独立批准。若官方来源无法核实则集中列BLOCKED，不放宽校验求绿。新候选恢复verify-metadata=true和strict验证，保留35锁和原二进制身份，精确记录新增pin来源、最终实际消费闭包与有意义的校验失败拒绝检查；不引入未用Foojay组件。一次必要集中严格离线构建验证，首次失败/修复重建如实记录。
2. P2 R02：原lockCanvas晚返且已取消时，真实drawBitmap执行、清理unlock/post与旧代状态分开；只为本次实际执行且契约有效的绘制生成成功receipt/计数，禁止无绘制却drawn增加。原canvas/线程归还和sticky错误保管保持。复用tester受控竞态回归及受影响正常/seek/取消/销毁检查。
3. P2 R03：增加一个明确有界同包manual idle→显式Listen入口，使人能从闲置执行完整3秒听音流程；精确component/method/参数/准备等待/超时停止和原资源归还写入计划。保留原四自动入口/默认静音，不随意export Activity、不借外部启动或已有运行中静音会话替代。无人听音时仍NOT_RUN；不自动播放未知设备。

三项一次实现与自测、必要app/test集中构建；未改native/fixture/host复用，不增框架/新产品功能。完整交新源码/产物身份与签名、元数据来源/严格验证/消费闭包、三项回归及历史失败、机器完成矩阵、更新准确设备计划和ZIP/seal，主动通知负责人后冻结，等待tester集中复审。新元数据准入是否足以关闭P1由独立复审决定，coder不自签PASS。原6帧/30秒、像素/PCM/owner硬预算和现有成熟框架/许可/全P0保持。
