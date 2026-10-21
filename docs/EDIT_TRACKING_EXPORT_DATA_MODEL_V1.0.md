# VideoKit 工程、跟踪与导出数据模型

V1.0；2026-10-21；当前设计基线，非实现/性能/许可验收证明。项目PAUSED_WAITING_USER，D1未过/M0未启；仅文档更新，不派开发、补测、设备或恢复自动跟进。

## 1. 共通规则

字段命名按[统一接口](API_DATA_CONTRACT_V1.0.md)，时间int64微秒、区间半开[inUs,outUs)、坐标以方向元数据应用后的媒体M归一化，有限数/非负范围/溢出检查，帧率为有理数。view变换不改导出空间O，方向只应用一次。对象不序列化路径/凭据/原句柄/模型context。

## 2. 模型字典

| 对象 | 必需字段 | 校验与归属 |
| --- | --- | --- |
| EditProject | schemaVersion,projectId,projectRevision,sources,clips,masks,trackingRefs,exportPreset | 所有实体ID唯一、引用存在；宿主repository持久化 |
| ProjectSource | sourceId,mediaToken,technicalFingerprint,mediaInfoRef,leasePurpose | fingerprint含技术/内容核验政策，未知不可冒相同源；恢复由宿主重新授权 |
| Clip | clipId,sourceId,sourceInUs,sourceOutUs,outputOrder,transform | out>in；源长未知需范围实际验证；重复同源片段仍有不同clipId |
| EditPlan | planId,projectId,projectRevision,planRevision,clipMappings,effectOrder,sourceFingerprints | 不可变；export捕获此revision，编辑新revision不更改在途输出 |
| ClipTimeMapping | clipId,sourceInterval,outputInterval,rateNumerator,rateDenominator | 有理映射、溢出检查；若首期不支持速率编辑只能1/1，不静默加功能 |
| Mask | maskId,targetId,sourceId,sourceRange,shape,normalizedGeometry,effectType,effectParams,keyframes | 参数范围按已冻结preset；图形不可逆变换/NaN/越界拒绝 |
| MaskKeyframe | keyframeId,sourcePtsUs,geometry,interpolation,origin:MANUAL/TRACKED | 同位置冲突显式仲裁；手工纠正优先且使下游计算失效 |
| TrackingTask | taskId,projectId,projectRevision,targetId,sourceRange,modelRef,configRevision,state | 结果仅写相同revision/config，用户纠正后旧task不可覆盖 |
| TrackingSample | targetId,sourcePtsUs,geometry?,confidence?,status:TRACKED/LOST/AMBIGUOUS/MANUAL | LOST/歧义不能填假确定框；confidence无校准则null |
| TrackingResult | resultId,taskId,projectRevision,modelHash,samples,lostIntervals,ambiguousIntervals,coverageRef | 原采样不冒每输出帧覆盖；用户选定目标只工程内关联，不建人脸身份库 |
| CoverageReport | reportId,planRevision,sourceFingerprints,outputPtsCoverage,unprotectedIntervals,policy,verifierVersion | 任何未确认区间阻止“完整保护”成功，保守全帧策略需显式批准并实测 |
| ExportPreset | presetId,version,container,video/audioCodec,dimensions,frameRate,colorPolicy,rotationPolicy,audioPolicy | 能力/许可/设备范围先验；preset未冻结不得标正式输出支持 |
| ExportTask | exportId,requestId,projectId,planRevision,presetId,sourceFingerprints,outputHandleId,logicalState,returnReport | 取消与READY单一仲裁；逻辑终态与原返回双层 |
| OutputToken | tokenId,exportId,handleId,outputGeneration,validationRef,metadataRef | 不透明临时输出引用；无源覆盖/删除权，不是COMMITTED |
| OutputValidation | validationId,exportId,planRevision,checks,validatorVersion,input/outputHashes?,warnings | 结构/可读/时长/音画/覆盖按适用项核；未知/仅壳成功不能冒validated |

输出metadata含原需求11.2全部技术字段（来源、容器编码、尺寸时长/音轨等）并补planRevision/验证摘要；此表不是删减原返回字段。对原需求未定义的字段保持可选/UNPROVEN，不能用null代必需验证。

## 3. 时间与变换

输出有序clip映射必须连续或按显式gap策略，不因重排沿用输出时间的旧轨迹。轨迹绑定源PTS，映射后逐输出实际帧评估。VFR用实际PTS，不用frameIndex/fps估计盖掉间隙。全景旋转/裁剪仅显式编辑改变O；UI观看矩阵不写Mask源坐标。多mask重叠按EditPlan.effectOrder确定，预览与导出共用评估数据，平台shader用黄金图验证。

## 4. 版本、恢复与并发

EditProject未知major拒绝，只做已登记迁移；旧文件先只读校验，迁移写新副本并保留原件。源指纹变化使原TrackingResult/CoverageReport失效，宿主重新解析并由用户确认工程，不自动沿旧路径找相似媒体。重启恢复不恢复原指针/半个编码任务；初期重新授权后从头导出，新exportId/临时目标，旧UNKNOWN仍独立保管/查询。

Tracked→LOST/AMBIGUOUS不伪恢复为成功；重关联只新sample显式记录不确定历史。projectRevision、planRevision、model/config版本都进缓存键，不能以同targetId覆盖用户新纠正。数据最小化，默认无持久人脸特征；宿主显式存工程也不得上传。

## 5. 示例与测试

设计JSON样例见[样例](schemas/design_model_examples_v1.json)，字段结构约束见[Schema](schemas/design_contracts_v1.schema.json)；样例是设计数据，不是真输出或质量结果。ET-01非法范围/引用/重复/未来schema；ET-02重排/VFR/重复源/变换黄金样本；ET-03纠正旧结果拒绝；ET-04源变更恢复/不可保护区间；ET-05导出固定plan/取消READY竞态。M4/M5/M6分别验收，M0只Fake。
