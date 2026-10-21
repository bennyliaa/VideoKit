# MEDIA3_CONTAINER02_FIX 开发要求 V1.0

2026-10-21；负责人正式派D1_MEDIA3_CONTAINER02_FIX。

依据独立完整报告docs/tester/D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md，13782B，SHA256 4d8853e56b18de0605309a6ba627b674c222d8b846a670d4cb59754bc71a4e87，结论FAIL_NEW_P2_WITH_FUNCTIONAL_SCOPE_OPEN。新使用extractor/decoder同版本有限离线来源许可/strict证据通过保持；真实容器/合格fixture/平台效果仍OPEN/NOT_RUN。旧候选与证据完全保留，D1未过M0未启。

MC-B01/P2：TemporaryOutput.inspectHostMp4Structure在原REOPEN ACK已到但同原任务线程尾段尚未返回时，先置hostInspectionAttempted，再将OUTPUT_ORIGINAL_PENDING记首错，未执行检查资格永久耗尽。准确同原任务返回后不能继续；不是实际超时、取消或解析失败。

修复须集中统一这个入口及其共享的检查准入/暂待原归还状态：准入前暂待与实际检查已开始后的真实失败区分，保留同一原REOPEN响应及授权Provider，观察原observer/worker真实返回后能够继续尚未执行的检查；不得盲目第二次reopen/RPC、重发、清真正超时/取消/失败/UNKNOWN或提前释放。实际解析失败后的重入策略保持明确，不能借修复循环重试。结构检查成功仍不能validated、READY或COMMIT。沿用8MiB累计/16MiB输出/64KiB块/总源2每源1queue0及原返回门。

有限关键顺序集中覆盖：REOPEN ACK先/原线程尾段后、原线程先/ACK后、同原observer未返、真实超时/取消/abort/权限或坏Provider/真正结构失败、合法观察后单次继续；覆盖共享入口同类路径，禁止只为单例改字符串求绿。主机缺Android类时，用明确前解析准入证据证明已继续到正确边界，不能冒容器正例。依赖/版本/许可不扩、无新平台替身或编码器/设备/ADB/占用操作，不并发Gradle/缓存写。

在新docs/coder/d1media3-container02目录集中实现、自测和必要一次集中strict构建，复用原工具与准确新入口输出根；旧01/05 seal不改。完整交付主报告/接口顺序决定/集中用例结果/源码与生产JAR来源/许可strict差异/准确NOT_RUN矩阵/hash seal与ZIP。映射原MC01–32及独立MC-B01复现和真实超时对照，不增加通用诊断框架。完整冻结主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774，由负责人核后正式交tester整包审；不逐问题交接。
