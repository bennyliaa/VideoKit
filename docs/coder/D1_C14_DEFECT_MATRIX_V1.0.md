# C14 集中缺陷与覆盖矩阵 V1.0

2026-10-16。C13平板52 PASS/3 FAIL/14 BLOCKED、手机69环境阻断是正式输入，不回写。C14本机实现/检查完成不等于设备修复通过，全部设备执行NOT_RUN；D1未通过，不进入M0。

| 输入 | C14实际变化 | 本机证据/设备验收与状态 |
|---|---|---|
| C13-T01 两configure FAIL | 不再首个codec＋固定可选key直接配置；新增公开能力限界、实际isFormatSupported、≤4确定提案、默认/声明Baseline与标准颜色组合 | 共享EncoderNegotiation规则反例＋Android编译；MP4/AVI六帧正例设备NOT_RUN，不能说已唯一查明或修复vendor原因 |
| C13-T01 诊断合并 | ENUMERATE/CAPABILITY/CREATE/CONFIGURE/START/INPUT/OUTPUT/MUX/VALIDATION/CLOSE；保存公开CodecException事实、初次尝试错误与每次关闭 | 日志不输出任意message/路径；元数据与diagnostic限额纯检查。实际vendor错误诊断须设备保存 |
| 候选释放/重选 | 创建中/owner calls/Image/codec引用、关闭未证分别记账；仅真实释放后下一，配置中无Source producer/输出writer；运行期失败不回退 | configure-first/all、cancel gate、实际release后保守ACK丢失的Android方法编译；不把ACK模拟说成硬件release故障实测 |
| C13-COV01 14项前置BLOCKED | 17 pipeline方法全部保留，含两正例、owner恢复及原14负例；新增6 encoder方法 | 实际PTS≤1ms、六帧EOF、luma≤24及源差异≥4/输出≥2均不改；须正例后再调度依赖，不用fake生成视频补通过 |
| C13-LIM01 数组/质量/EOF | 全文统一8份RGBA1179648B＋YUV55296B；新增queue/offers与codec/Image/转换数组逻辑持有字段 | 静态可达引用预算与实际逻辑账本；设备峰值/整堆RSS/持续多轨与质量仍OPEN |
| C13-T02 系统signal0 | ExitEvidence/TraceCapture/CPU采集/native解码算法未变，仅身份重命名 | 严格FAIL保持；两项CPU SIGSEGV列NOT_RUN_UNCHANGED_PLATFORM_LIMIT，不为换包名重跑/外部raw回填，不计本批PASS |
| 手机禁用 | 原硬环境门禁保持 | 本批无ADB。仍阻断时记ENVIRONMENT_BLOCKED，不要求找不存在按钮、不卸载清数据/换包绕过 |
| 内部命名文字 | 按PROJECT_DECISIONS：com.videokit、com.videokit.<module>、com.videokit.app既定 | 只将正式artifact/version兼容待验OPEN，不撤销已定内部命名 |
| 跟踪/全危险链/全P0 | 原十二项和M0–M8保留，无模型/媒体/新依赖 | 真实标签0帧/权利未闭合，宿主JNI与显示/音频/字幕/图片/跟踪危险链OPEN；不因局部通过进入M0 |

35 CPU受影响回归＋7 host双轨/故障/恢复＋8 legacy＋17 pipeline＋6 encoder＝73可调度方法；另2个编译保留的CPU信号方法明确不重跑，合计75个已编译指定方法记录。原host/legacy故障路径仍用于编码/Sink与恢复共享边界回归，不增加新native crash campaign，不把legacy raw11用于CPU App信号判定。方法依赖、预期和来源见设备附录/device_plan。
