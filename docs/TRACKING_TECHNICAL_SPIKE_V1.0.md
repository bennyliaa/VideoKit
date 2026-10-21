# 自动人脸与物体跟踪技术 Spike 设计

版本：V1.0；日期：2026-10-05；状态：设计计划；是否运行及有限结论由对应冻结报告证明，本文件不作全局未运行断言。

## 1. P0 目标

首版包含人脸检测后用户选定目标跟踪、框选/点选移动物体跟踪、多目标、短时遮挡/出画后的重关联尝试、纠正关键帧、丢失提示和漏码检查。模型不可用或跟踪失败不破坏播放及手动编辑；手动回退不能替代自动跟踪 P0 验收。

## 2. 开源候选与权利边界

| 能力 | 首轮候选 | 已查到的代码/目录许可 | 尚需核实 |
| --- | --- | --- | --- |
| 图像处理/传统跟踪 | OpenCV 精简模块 | 4.5+ Apache-2.0 | 实际版本、contrib/第三方模块逐项许可 |
| 人脸检测 | OpenCV Zoo YuNet | 对应目录说明为 MIT | 固定模型 hash、训练数据来源及商用/再分发权利 |
| 用户指定物体跟踪 | OpenCV Zoo ViTTrack | 对应目录说明为 Apache-2.0 | 模型具体权利、训练来源、纠正与重关联质量 |
| 推理运行时 | OpenCV DNN 或 ONNX Runtime | OpenCV Apache-2.0；ORT MIT | 固定版本、执行 provider 依赖、遥测/离线验证 |

来源：[OpenCV](https://opencv.org/license/)、[YuNet 目录](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)、[ViTTrack 目录](https://github.com/opencv/opencv_zoo/tree/main/models/object_tracking_vittrack)、[ORT 许可证](https://github.com/microsoft/onnxruntime/blob/main/LICENSE)。目录许可是候选证据，不代替模型来源与训练数据审查。许可证不清的权重不打包进入产品。

不默认采用 Ultralytics/YOLO 等名称对应的任意模型，也不默认采用许可受限的人脸权重。没有必要做人脸身份识别；身份 token 仅在当前工程内用于目标关联，不建立永久人脸库。

## 3. 处理流程

只读源 → 平台帧提取 → 方向/色彩归一 → 检测候选 → 用户选择 targetId → 追踪/周期性重检测 → 关联与置信估计 → 轨迹、丢失区间和覆盖报告。

多目标按预算建立独立跟踪状态；低分辨率分析可减少成本，但需正确映射原图。自适应取样只能用于预分析，不能跨越未观测帧就断言完整覆盖。最终导出覆盖检查根据输出实际帧 PTS 对遮罩位置和可信区间复核；不能把“每帧有矩形”等同于目标被准确覆盖。

遮挡/相似目标时标 AMBIGUOUS/LOST，不盲目换身份。重新入画可尝试短期特征关联，保留不确定性；自动恢复后也需记录。人工纠正关键帧使后续片段失效并重新计算，结果用 projectRevision/requestId 去重。

## 4. 实验矩阵与指标

建立有许可和人工标注的单人/多人、侧脸、低光、遮挡、快速运动、相似目标、出画重入、横竖屏、4K 输入与多目标样本。训练与验收数据分开，不把厂商 README 指标当作本产品验收值。

测 detection precision/recall、ID switch、LOST 区间、边界 IoU、真实目标未覆盖帧、错误恢复、交互纠正成本、处理 FPS、首结果耗时、峰值 CPU/GPU 内存、热降级和电量。CPU 基线先行，再测平台加速 provider；不承诺所有设备实时处理。

每个视频保留人工标注与脱敏质量报告，Release 不永久记录用户轨迹与人脸资料。模型在安装包内或明确用户授权的本地导入，默认不联网下载、不上传。禁用运行时遥测并以网络阻断实测验证。

## 5. 必须解决的风险

单目标 ViTTrack 不天然具备长期重识别或多目标身份管理；光流等传统跟踪也不能自动补足。需复用许可合适的关联方法并自行实现需求所需编排，比较至少两条路线，未过质量门禁不宣称自动跟踪完成。

自动打码属于效果验收；选定目标未覆盖却未警告是发布阻断。允许保守扩大遮罩或全帧处理的替代保护必须展示给用户并验证，而非静默修改。

## 6. Spike 退出材料

固定版本/hash/模型权利清单；CPU/加速兼容与资源报告；覆盖标注报告；纠正/丢失/重入可交互原型；取消与内存压力测试；阈值建议及其误报/漏报权衡。质量、耗时、温度和取消数值由用户评审后冻结；本设计新验收计划待测，历史局部结果不覆盖也不重置。

## 7. 数据与指标冻结

[工程跟踪模型](EDIT_TRACKING_EXPORT_DATA_MODEL_V1.0.md)统一task/projectRevision/configRevision、TrackingSample/Result、CoverageReport和LOST/AMBIGUOUS、纠正后的旧结果拒绝。MET-TRACK按[指标冻结表](METRIC_FREEZE_REGISTER_V1.0.md)由coder提案/独立tester核标注/负责人批准，保留原D1可行性及M5质量门，不为本次文档整理新开实验。资源/原生隔离按[设计](RESOURCE_AND_ISOLATION_DESIGN_V1.0.md)。
