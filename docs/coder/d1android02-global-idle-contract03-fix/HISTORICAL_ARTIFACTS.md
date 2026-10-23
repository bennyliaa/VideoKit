# 历史材料与当前材料

原 revision02 整包仍为独立B FAIL；不修改其1140项、ZIP或报告。

- reference/HISTORICAL-revision02-misbound-facts-proposal.json：原错误提案字节，历史原案，不是当前提案。
- reference/HISTORICAL-revision02-criteria-map.json：原开发映射的历史通过范围，不是本批结果。当前 criteria-map.json 全部语义标 NOT_RUN。
- reference/HISTORICAL-revision02-synthetic-qualification.json：旧source的合成示例，不是当前许可或资格。
- tools/historical-prepare_delivery.py、historical-finalize_delivery.py：旧批拼装工具的历史副本，当前不调用、不作为交付入口。
- reference/isolated-prior-scope.json：既有001a/55065隔离记录；无新增查询或收尾。

当前提案是 reference/next-readonly-facts-execution-proposal.json，所有路径/source/gate/collector/plan均绑定本批，approvedForExecution=false。当前完整结论以 DELIVERY.md 和独立冻结回执为准，不能根据文件名里的旧 PASS 宣布本批通过。
