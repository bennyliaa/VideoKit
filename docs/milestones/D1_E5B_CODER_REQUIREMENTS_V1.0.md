# D1 E5B 观察原锁非创建打开集中修复需求 V1.0

2026-10-17。采纳E5A复审新增E5A-F01/P1，原E5-F01/F02静态修复支持保持。新完整d1e5b候选，旧冻结/设备N2现场只读，不先安装QUERY。

最终观察必须仅打开原有owner/lease，不MODE_CREATE、不先exists再create，不缺失补文件。专用existingGuard路径使用非创建/NOFOLLOW并核实际打开句柄fstat普通文件、owner0B/lease36B及准确原fence/身份，路径与句柄devinode一致/持锁前后必要复核，缺失/链接/目录/错误长度或身份变化拒绝且不得设备文件变更/原S/R/live grant。正常新任务创建接口保持分离；集中检查恢复与观察全部“只核原资源”调用是否误用创建接口，一次修齐，不仅观察owner单点。

直接生产观察路径有限本机反例missing-owner/missing-lease/各错误角色/符号链接/错误长度/替代身份及健康正例，断言无创建/补写、原文件清单/字节不变、无新R/S/live grant；实际句柄/锁绑定非仅路径布尔模拟。平台Android非创建打开代码/公共API兼容静态核，模型不当Android fd/flock实测。既有late force-close/跨host默认拒与生命周期原deadline门不回退，不无理由重跑全部历史检查。

一次完成修复/关键证据后集中offline双APK构建，保必要repair日志/输入。完整四D1_E5B文档/源码ZIP/签名双APK/final输入/SBOM差异/外freeze只读verify一次主动报告；只保必要来源不反复复制大量无关自检产物。原Media3/FFmpeg/native/许可边界不变，无新依赖/ADB/设备/媒体/QUERY/恢复/fault/下载。

下一计划保同签名保数据部署→原QUERY→独立审核→另ABORT→审结算→当前host实际最终观察→四正常方法，不清marker/换UUID/重装清数据/扩时。D1未通过/M0未启动/P0及N2历史FAIL保持。
