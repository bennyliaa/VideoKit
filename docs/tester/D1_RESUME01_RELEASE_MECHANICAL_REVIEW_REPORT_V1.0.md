# D1 RESUME01_RELEASE 独立机械核验报告 V1.0

日期：2026-10-20。结论：**PASS_INDEPENDENT_MECHANICAL_REVIEW**。本报告在现场查询及许可消费之前形成，仅解除本批机械核验门；真实 registry/claim/账本、工具来源、新鲜 M1 和部署条件仍须依次成立。

依据正式 `D1_RESUME01_RELEASE_TESTER_REQUIREMENTS_V1.0.md` 及负责人同批条件授权。新 scopeId `1f1cc608-2337-438f-a9f5-086cda29ceb2`；唯一方法 `ordinarySenderCannotBindCodec`。

独立检查结果：

- release seal SHA-256 `b7537e7dd4934c248f727064a103c1fbfc099d0e7a28cce55b28a777df7fd461`，134 个不可变文件和 ZIP 133 成员逐项大小/hash及名称集合一致。来源 ZIP 5849591 B，SHA-256 `93e0779bc6d1d1326df6536e4537ca94cc1a86013a2aef590e372f769eb52bf4`。
- 74 个生产来源和 183 个 JAR 成员与静态 PASS 候选逐字节等价。JAR、observer、三个 APK 均准确复用已审字节，零构建；没有加入 SkinKit 或 UI 变更。
- scope/release/config/permit 的 canonical 编码、实际摘要、新 scopeId、唯一方法、sourceReview 及相互引用通过。sourceReview 准确为真实独立报告 `0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743`。
- scope SHA `917d8c1dc57d267a25101355f077e4a0c3ed62b6c93c10d63ec8255def6b1bde`；release SHA `04605dcf8f1ab1b2c0d0147da255e6514f309f4669f79efa1bf0f404042f35e5`；config SHA `c988760490747e7d456311b3b4df1fdf4579bc753ac0cf0130a8115d5ad958eb`；permit SHA `37e899f0cc92ef97d8d473f96d8491050e5985210975db56337efe0b4ce6bead`。
- 原 registry 的 trust plan、授权、审查和 head 沿原身份保留，没有被新来源审查覆盖。13 项封存快照的来源沿 E11-final seal → 原 E11 seal → export 前清单及原快照逐项核对；计划中原真实 root 与每个 expectedActual 路径相符。本轮机械阶段未读真实 registry，不用复制快照代替其现场检查。
- 行政 disposition 保持610 B、原十字段与四个证据摘要，TERMINATED_WITHOUT_RETURN/false、B/H 和 K UNKNOWN 不变；没有全局 claim 豁免。
- 两条主机 observer 请求、完整 pins、准确三个 APK 参数、五条元数据请求、唯一 instrumentation argv 和部署 once 路径一致。35 子调用图不含离线 fake 路径；pm path 依赖指向同包前一操作，按原固定解析规则展开，不新增子调用或接受外部任意路径。
- 许可数值及预算一致：43 操作，原始/重复输出1949696 B +元数据控制786432 B +不可使用409600 B =3145728 B；归档4194304 B。零占用重试。actual-read 超额/UNKNOWN规则明确，不把保存上限当物理读限，不借旧余额。

许可在冻结材料中为 ISSUED_NOT_CONSUMED；本机械报告未创建部署 once、case claim、归还 marker、安装 disposition 或修改冻结材料。后续现场若具体 claim、原 registry 字节、数据/版本、采集能力或工具来源不符，即保存实际阻塞并停止；不得以本 PASS 跳过。

本报告不批准额外调用、终止、重启 server、清理、重试或其他五方法。设备阶段按已授权的同批条件继续，实际结果另出完整报告；T07 在本报告时仍 NOT_RUN，D1 NOT_PASSED/M0 NOT_STARTED。

证据：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_RELEASE_REVIEW_EVIDENCE/independent-mechanical-audit.json`。本报告由 tester 外存，未使用包内模板伪造独立 PASS。
