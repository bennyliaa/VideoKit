# M0 测试补充：完整 Flutter UI 框架、SkinKit 与演示数据 V1.0

## 国际化详细设计对接（2026-10-21）

按[国际化详细设计](../INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)与[数据模型](../INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，按I18N-01–15当前阶段范围独立核资源完整/ICU/类型、resolver真值、快速切换/持久化失败/迁移、四域隔离与完整UI矩阵。未接真实媒体/模型标NOT_RUN，不用Fake补绿。

这是未来阶段测试要求，不是当前派发；主里程碑不变，集中整包开发测试规则保持，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


日期：2026-10-20；未来M0要求，当前无新增产品/设备测试。与 [原M0测试](M0_TESTER_REQUIREMENTS_V1.0.md) 合并验收，主规范 [UI0-01–16](../M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。

| 用例 | 必须核实 |
| --- | --- |
| TC-M0-UI01 | PPT页04–16对应路由/返回/底侧导航全部可达，不是静态图/空白页；手机平板主要操作有反馈。 |
| TC-M0-UI02 | 播放/轨道/图片、多槽/声音切换、片段编辑/撤销重做、跟踪LOST纠正、导出阶段/取消/失败成功演示可重置。 |
| TC-M0-UI03 | 真实SkinKit二进制/Provider/Flutter Adapter；已有主题预览/应用/恢复、系统明暗/持久化/四级回退，Fake颜色不算PASS。 |
| TC-M0-UI04 | 主题代次/订阅/read view/lease释放；快切/旋转/导航无过时覆盖；核心依赖无SkinKit/Flutter。 |
| TC-M0-UI05 | 固定seed及manifest/hash/合法资产；Demo标识清晰，模拟导出说明未生成真实媒体，真实模式不静默使用Fake。 |
| TC-M0-UI06 | 真实手机/平板窗口/分屏/安全区，中英/RTL长文/100/130/200%字体、48dp、焦点键鼠及基础读屏；PPT差异有记录。 |
| TC-M0-UI07 | 开发flavor/故障入口与Release隔离，不打包用户test_media/私有图/凭据，不默认联网或写原件。 |
| TC-M0-UI08 | API/Fake/TestKit原用例继续执行；UI Controller相同端口可替换Fake/Real，来源标记和各后续页面接回矩阵完整。 |

结果采用PASS/FAIL/NOT_RUN/BLOCKED，另列evidenceKind=UI_DEMO/CONTRACT/REAL_THEME/REAL_MEDIA和环境。UI演示PASS不升级为真实媒体/AI/输出PASS，截图不替实际主题桥接与资源验收。只接收完整冻结candidate，集中缺陷后统一回交；不机械重复不变构建，不并发占用设备/Gradle。
