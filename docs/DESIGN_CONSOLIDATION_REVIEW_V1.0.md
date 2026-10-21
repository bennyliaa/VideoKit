# VideoKit 设计一致性集中整理与变更记录

2026-10-21；用户授权仅文档更新。项目PAUSED_WAITING_USER，D1未过/M0未启；没有派发开发、产品测试、构建、依赖安装、设备操作或自动跟进。

## 1. 清单处理（设计层）

| 项 | 原问题 | 本次文档处理 | 依据 |
| --- | --- | --- | --- |
| 01 | SkinKit旧要求清理 | 当前主文档/M0-M8工作单已改为Flutter自有Theme；SkinKit工作单改未启用历史入口 | [FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md) |
| 02 | 主里程碑摘要 | 保留13主阶段和原目标，M0一行仅整合先前批准UI/国际化退出条件 | [MILESTONES_V1.0.md](MILESTONES_V1.0.md) |
| 03 | 任务配置版本 | 识别/翻译任务及结果显式配置revision，统一媒体字段和兼容别名 | [PLAYBACK_DATA_MODEL_V1.0.md](PLAYBACK_DATA_MODEL_V1.0.md) |
| 04 | 本地化错误 | StructuredError typedArgs/resourceContractVersion贯通API/模型；HostTextRef宿主resolver与语言刷新明确 | [API_DATA_CONTRACT_V1.0.md](API_DATA_CONTRACT_V1.0.md) |
| 05 | 幂等/取消/未知 | 逻辑重复请求与物理只一次分开，UNKNOWN不归零，输出query与READY-cancel仲裁明确 | [OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md](OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md) |
| 06 | 当前/历史状态 | 协调与评审入口整理为暂停状态，旧时间序列移入原字节归档；不改结果 | [CURRENT_DESIGN_BASELINE_V1.0.md](CURRENT_DESIGN_BASELINE_V1.0.md) |
| 07 | 工程跟踪导出模型 | 实体/PTS/引用/revision/源变更/覆盖与恢复补齐，并提供设计Schema片段与样例 | [EDIT_TRACKING_EXPORT_DATA_MODEL_V1.0.md](EDIT_TRACKING_EXPORT_DATA_MODEL_V1.0.md) |
| 08 | 安全输出验证恢复 | 验证只读租约、验证结果、状态查询、进程死亡隔离与宿主COMMIT边界 | [OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md](OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md) |
| 09 | 原生/共享/Flutter边界 | 模块产物/语言/平台通道/FFI/纹理/PCM/buffer回调所有权与验收明确 | [NATIVE_BINDING_AND_MODULE_BOUNDARIES_V1.0.md](NATIVE_BINDING_AND_MODULE_BOUNDARIES_V1.0.md) |
| 10 | 图片详细设计 | 统一会话/后端、ImageInfo/TileLease/动画时钟、长图缓存/取消与验收 | [IMAGE_SUBSYSTEM_DETAILED_DESIGN_V1.0.md](IMAGE_SUBSYSTEM_DETAILED_DESIGN_V1.0.md) |
| 11 | 资源与隔离 | 资源树/排序、声音切换未知门、单元worker/IPC/broker与原返 | [RESOURCE_AND_ISOLATION_DESIGN_V1.0.md](RESOURCE_AND_ISOLATION_DESIGN_V1.0.md) |
| 12 | 验收追踪与冻结安排 | 31节及461章节/条款入口，分别关联开发/测试工作单与TC-ID；15指标组有责任/期限/方法 | [REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md](REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md) |
| 13 | 扩展/来源缺口 | ASR翻译依赖模型、归属阶段/指标准入与SkinKit来源缺失明确；不自动新增原门 | [OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md](OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md) |

以上为设计层处理完成，不代表模型权利/平台效果/数值或API ABI已经验收冻结。原编号不变；M0主表改动仅汇总已有批准范围，不新增主门或提前ASR/翻译。开发测试要求仍分别保存，集中整包规则保持。

## 2. 历史与原证据

修改前60份文档原字节已复制到history/design/2026-10-21-consolidation，逐份长度/SHA复核，manifest有原主阶段行。原用户需求全文与历史SDK来源JSON未改；docs/coder、docs/tester及旧产物/账本/once/FAIL/UNKNOWN无写操作。旧派单原文在归档，不继续混作当前任务。供应方目录缺失不补造文件或改历史hash。

## 3. 文档校验结果与边界

- 当前设计及关联工作单本地链接检查无断链（归档仅验证目标存在/原字节，不把其过期外部资料当当前依赖）。
- 原31节及461个章节/条款入口有唯一requirementId/TC-ID、设计和开发/测试文件；代码示例/正文仍须阶段派发前人工逐项确认，不谎称自动提取完成所有语义验收。每行result保持NOT_RUN且evidence为空，不覆盖旧局部报告。
- 主阶段13项顺序保持；仅M0行把原已批准完整UI/Theme/国际化门写入摘要，其余阶段行不变。
- JSON与Schema/样例均可解析，内部引用/必需字段/示例基本类型及样例时间范围做文档结构校验。环境没有jsonschema库，未安装，未声称已完成JSON Schema标准验证或产品契约测试；Schema明确为设计片段而非完整产物ABI。
- 原子用例详细步骤/设备和样本、具体数值、模型/依赖版本及正式ABI依照指标冻结与准入表在相应阶段前批准；未冻结/未证保留，不编造PASS。

## 4. 恢复后的剩余审批/验证（本次不执行）

仅在用户明确恢复后，负责人审D1剩余门及本次新基线；每阶段派单前人工细化TC、冻结所需字段/数值，原D1已消费范围不重放。EXT-ASR/EXT-TR先确认所属主阶段/版本、模型权利/语言与设备指标。后续是实现与真实独立验证，不再以“文档写完”当退出依据。
