# D1 C08 单APK有限实验测试需求

日期：2026-10-05；计划，待完整候选负责人交接。当前不设备/Gradle、不重复C07。

先独立核查FFmpeg源码/版本/hash/完整许可、实际configure/ELF/SBOM及debug-only分发范围，不用LGPL-only参数替代最终产物审查。真实单APK普通isolated CPU解码检查UID/PID、源只读、opaque AVIO、真实帧PTS与有效内容、有界帧协议及拒绝恶意尺寸/stride/溢出/伪task。实际SIGSEGV/挂起终止、死亡/source实际释放、宿主与另一槽存活分别验证；App历史记录与匹配原始crash独立分类，未证故障不得PASS。AAR/多宿主与完整产品管线未实现仍单列未决。

旧C07 signal差异/ordinary历史FAIL保留，不回写，不重复无改变探针。形成候选后按变更影响整体回归已有源格式和输出安全门禁；设备仅正式安排的目标。交docs/tester/D1_C08_TEST_REPORT_V1.0.md，结果不等于最终商店许可、全P0或D1通过。
