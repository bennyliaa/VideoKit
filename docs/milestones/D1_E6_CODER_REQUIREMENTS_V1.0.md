# D1 E6 隔离输出验证集中修复开发需求 V1.0

2026-10-17。依据D1_E5C_OBSERVE_REGRESSION_REPORT，原最终观察PASS，产品0PASS/1FAIL/3BLOCKED，E5C-REG-F01/P1。新d1e6完整候选；保E5C/E5B/全部旧报告/fixture/53651B失败输出及53651累计消费，不清账。

真实进展保留：同步flags18/8ACK/STARTED就绪实证成立，6独立源→硬OMX.qcom AVC color21→6inputs/6samples，remote已ENCODED_AWAITING_ISOLATED_VALIDATION。verifier第7isolated CPU kind2/mode11在sequence1..5日志后CPU_NATIVE_REJECTED/NATIVE_STAGE5，host泛化E4_HOST_OPERATION_FAILED。具体失败条件未证，不能凭5日志认只5解码帧、不能抹第6/EOF/PTS/thumb门。本次真实资源ACTUAL_OWNERS_RETURNED/owner1 finish1/CONTROL0/全部CPU源slot deathclose且预算S53651/无pending已证，不再处理原N2恢复。

## 集中实现

1. 核E4CpuAdapter.validate与native输出验证mode11完整链、encoder6样本/EOS/fMP4/实际PTS(0,208333,416667,625000,833333,1000000us)、验证数量/PTS/EOF/thumbnail/帧映射。必要时区分6帧后EOF drain流程、send/receive EAGAIN/EOF顺序、frame索引边界及原PTS归一化。先有据定位，不猜降阈值或将ABORT当预期。真实完整6帧+EOF/PTS<=原界/画面条件全部保持。
2. 新有界native诊断码/阶段/AVERROR原值/packet帧计数/最后PTS/EOF/drain/拒绝具体谓词，Java/跨进程/host保留精确安全结构码而非泛化丢cause；首错/cleanup分开，无原凭据路径泄漏。实际CPU readAt请求数/压缩字节可加原计数，不能日志缺失记0。
3. 修实际生产验证或编码输出根因（若为输出缺陷应修编码/mux而非宽验证）。原隔离不可信压缩解析/真实源/输出验证、媒体白名单/无网络/既定Media3与FFmpeg不变。允许必要本项目JNI/native wrapper修正与集中原有限CPU库重建，底层第三方版本/编解码/网络白名单不扩；若更改原native产物精确报告diff/SBOM/对应源码/NOTICE/构建参数与Android16KiB布局静态情况，不沿用旧7库相同结论。无需下载新依赖/源码/模型。
4. 自有有限小媒体或已授权53651B失败产物离线取证验证：tester另精确导出一次到docs/tester/D1_E6_OUTPUT_EVIDENCE/failed-output-53651.mp4后由负责人转交或路径就绪，coder可只读该导出件并计具体hash/读取/工具，不能自行ADB或读原test_media。先用源码/现有原日志分析不依赖等待；仅授权这个新失败产物本机有限读取，禁止整目录扫描/其他媒体。可使用已有工具/本项目native验证有限合成fixture，不下载ffmpeg或安装环境。不把桌面独立解码通过当Android通过。

## 验证/交付

一次集中六帧边界/末帧合法与真正多/少帧/EOF缺失/PTS异常/内容错的关键验证证据，负例不得因修复变宽；验证真实生产路径不镜像测试。原native/Java失败诊断贯通关键用例。原协议/owner/观察/预算/绝对deadline不回退，目标真正常链READY。先完成相关小修/诊断/证据后集中offline native(必要)+双APK构建，必要repair原日志保留，不频繁小项交测。

四D1_E6交付/架构边界/剩余门/设备附录、完整源码ZIP/双APK签名/final build/精确native与Maven差异/许可来源/外freeze verify一次主动交付。coder无ADB/设备/真实源stat-read-hash/新fault/下载，原失败产物导出件仅只读。下一准确正常MP4→AVI→能力→条件cancel同稳定账号/每新host原结算观察，现无pending不新ABORT。D1未通过/M0未启动/P0/旧FAIL保持。
