# C13 跟踪模型、样本与权利证据 V1.0

调查日期2026-10-16；未下载或集成模型/新媒体。文本基线及SHA见d1c13/evidence/model-baseline与tracking-evidence-review.json。候选调查不等于产品准入或法律保证。

| 候选 | 固定身份与已有文字证据 | 尚缺 |
|---|---|---|
| YuNet face_detection_yunet_2023mar.onnx | OpenCV Zoo commit `47534e27c9851bb1128ccc0102f1145e27f23f98`；LFS SHA256 `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`，232589B；目录MIT许可 | 权重实际字节未取、未验证；训练数据/人物授权与SDK离线再分发用途审查、检测/遮挡/旋转质量未完成 |
| ViTTrack object_tracking_vittrack_2023sep.onnx | 同commit；LFS SHA256 `2990f0b7cd44d92afa48cd97db6de7be113fc1d9594fddb74e2725c10478e91d`，714726B；目录Apache-2.0 | 权重实际字节未取；推理框架/ABI/最低设备、lost阈值及遮挡恢复/修正传播未实测；目录许可不能代替完整来源权利链 |

官方固定版本许可：[YuNet](https://raw.githubusercontent.com/opencv/opencv_zoo/47534e27c9851bb1128ccc0102f1145e27f23f98/models/face_detection_yunet/LICENSE)、[ViTTrack](https://raw.githubusercontent.com/opencv/opencv_zoo/47534e27c9851bb1128ccc0102f1145e27f23f98/models/object_tracking_vittrack/LICENSE)。C02留存的README含较新dynamic形状候选介绍，不能把2026may权重当成本表固定2023mar字节。

ML Kit官方[条款](https://developers.google.com/ml-kit/terms)页面版本2025-05-14：输入/结果在设备处理，但另有API指标上传和服务器联系说明；目前无满足本项目无遥测、离线独立Kit再分发约束的证据，因此不准入。[Android人脸文档](https://developers.google.com/ml-kit/vision/face-detection/android)正文要求API23；候选bundled16.1.7/unbundled17.1.0，仅文字调查。建议图像480×360、脸100×100（轮廓200×200）；C13的256×144输出不是跟踪质量输入证据。

## 真实样本/标签检查

沿用C03 F01–F05/O01–O04/N01十类、每段15–30秒、每段至少100个实际PTS标签，合计≥1000帧；clip hash、显示坐标/旋转、局部targetId/revision、visibility、人工框、annotator与独立reviewer必须完整。现有annotation-template.json仍是EMPTY_TEMPLATE_NOT_ACTUAL_ANNOTATIONS，frames=[]、rights空：本次可核验真实标注0帧，符合整套要求且权利审查闭合的clip为0；不是现有45个媒体都不可技术测试。

用户提供媒体只读用于技术验证，不能推导拍摄者/人物/发行授权。AVI/SRT存在只证明文件存在，不是字幕时序、跟踪或授权通过。没有伪造框、人物许可、独立复核人或检测质量结论；平台FaceDetector候选数不能代替人脸/物体自动跟踪P0。

下一项有限实验：先获得十类样本及权利凭证、按实际PTS完成人工标注/双人复核，再在明确准入的固定权重/CPU推理候选下测试检测召回/框IoU、ID切换、遮挡lost与恢复、人工修正revision传播、旋转/重叠遮罩及导出一致性；固定帧数、内存/时间上限和最低设备。模型/推理框架准入与样本权利未闭合前不运行或下载替代品。本批只交可核查缺口和下一实验，M5保持OPEN。
