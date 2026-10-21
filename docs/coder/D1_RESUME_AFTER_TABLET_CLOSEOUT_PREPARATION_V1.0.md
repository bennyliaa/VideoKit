# D1 恢复批次离线准备报告

日期：2026-10-20；结果：PREPARATION_COMPLETE / DEVELOPMENT_NOT_DISPATCHED。

已完成正式 coder 需求及 tester 草案，路径分别为 `docs/milestones/D1_RESUME_AFTER_TABLET_CLOSEOUT_CODER_REQUIREMENTS_V1.0.md` 与 `docs/milestones/D1_RESUME_AFTER_TABLET_CLOSEOUT_TESTER_REQUIREMENTS_V1.0.md`；两份协调文档顶部同步当前顺序。没有编码、构建、设备/旧任务查询、终止、部署、测试或许可消费。

## 冻结身份复核

2026-10-20 本地读取工件并计算 SHA256，以下与冻结 candidate-binding 一致；只证明本地文件身份，不证明安装或设备通过。

| E13F delivery-final 文件 | 字节 | SHA256 |
|---|---:|---|
| app-debug.apk | 10708622 | 938d70fbc70fd9bfdbef4ac37d2d83a66d7260e88e8c3c62bb2d022ea427908e |
| app-debug-androidTest.apk | 2774237 | 4227751bf659fca9efc8a8d2d32d5ce754bcbef9033e15a0c92ab7537dca9dd7 |
| fixture-debug.apk | 80041 | a8c86650ae756f682fb2cbaaa896424974893282026525266e7b1912a8dd1867 |
| e13f-host-tools.jar | 323116 | 97eadcd0cf7beaf1fd0bb7986e012ced69f6e09866f4af7e060338a2d0afabc4 |

位置：`docs/coder/d1e13f/artifacts/D1-20261018-E13F/delivery-final/`。app/test signer=5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；fixture signer=45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9，签名信息引用冻结 binding，未新跑签名工具。

独立来源审查 `docs/tester/D1_E13F_LIFECYCLE_REVIEW_REPORT_V1.0.md` 实核 SHA256=74469cb11aa7ec198daa4539570b1ed436c5851f1e8503f0e78af6a182826d72。此审查不扩展为未来改策略后的 PASS。旧 candidate-binding 的 DRAFT_NO_DISPATCH、null release/scope/once/sourceReview 与 ABSENT pin 保持历史原样。

## 决策与尚缺输入

既有 guard 已接受 TERMINATED_WITHOUT_RETURN/false，因此优先复用十字段 typed disposition，仅新增真实证据聚合、新来源 pin 及对应主机材料；不改生命周期设计。预计正式批次集中一次主机构建、零 Android 构建，继续复用 app19/fixture3。未结 claim 仍是独立硬门；全局行政记录不能自动覆盖，不清理/伪造归还。

等待负责人接受 TABLET_CLOSEOUT_CONT 最终报告及行政记录后，确定其摘要、review/authorization 证据、新来源候选与准确单方法预算，再正式启动开发。当前最终平板结果、行政记录 pin、新 release/scope/once、M1/M2 和逐项操作预算均未绑定；不生成可执行许可、不把它们填为成功。

下一真实产品项建议只派 `ordinarySenderCannotBindCodec` 一次。历史六方法 51/53 操作与 2MiB 不是本单项预算，必须重新逐项核算并独立审查。失败/占用/UNKNOWN 首次停止并保留原 owner，不追加其余五项。

原 A/K 外部终止、B/H UNKNOWN、原 Android 缺失 ACK、原 FAIL 及账目继续保留。D1 NOT_PASSED、M0 NOT_STARTED。Flutter/独立 Kit、全部 P0 与既定开源许可范围保持；输入/格式/渲染音频/Sink/跟踪/资源隔离及 API 阈值余门已列入 coder 需求，不能由此次准备或单 T07 宣称完成。
