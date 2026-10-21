# C14 许可与构建准入 V1.0

2026-10-16。仅本地Debug实验，不是产品发行许可。继承C13冻结并复核五个FFmpeg/allocator库与quota.c不变；CPU/lease JNI相对C13只作包身份重编，解码/旋转/六帧验证、退出采集/trace算法不变。新增EncoderNegotiation/EncoderCapabilities/EncoderDiagnostics与必要Pipeline胶水为项目自有适配，调用Android公开系统编码能力，不自制codec、不新增FFmpeg encoder/muxer/protocol/hwaccel。

Media3 1.9.3锁/Apache-2.0依赖不变，实际复用fMP4 WritableByteChannel；app锁与冻结C13源ZIP逐字节核对。公开系统codec软硬件结果分列，能力/配置兼容与vendor安全、专利条件另审，未将系统服务说成完整隔离。未下载模型/媒体或增加商业库/权限/companion产品/crash handler。

官方FFmpeg8.0.3完整源archive SHA256 `6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818`，11,407,656B、9893文件，签名/公钥及C09已验证收据、配置/生成头、266对象/608依赖与安全差异证据随源ZIP及独立SHA清单保留。本批不重跑GPG、上游构建或全面漏洞扫描；原五库/配额的C09命名是来源标识，不擅改算法。

聚合LGPL-2.1-or-later与实际IJG/ISC/MIT/Zlib声明保留；GPL/NONFREE/VERSION3/NETWORK为0，H263仅MPEG4传递编译要求，运行仍仅AVI/MPEG4-part2及MP4/H264。原16MiB单次/64MiB申请累计与4096记录、读/packet/像素/VMS边界不扩，不冒充RSS证明。完整NOTICE/特别声明与c14-sbom.cdx.json按APK核对。

NDK30.0.16248370/API31 ARM64，原生符号/JNI descriptor/source-class/artifact绑定与实际APK manifest/DEX/签名/16KiB ZIP/ELF审计保留。Release要求维持历史SHA `71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e`，无C14实验组件；静态对齐不是16KiB页设备通过。原失败/首次构建及最终采用日志不覆盖历史候选。

完整对应源、接收方替换/再链接材料、EULA/商店/专利、权重/训练/人物与样本权利仍OPEN。跟踪沿用C13固定文字/LFS身份和空模板事实，不把候选许可目录当权重再分发准入。没有标签/模型实际质量新结论。内部命名按已定PROJECT_DECISIONS，正式产物兼容/多宿主Kit与Flutter仍待验；D1未通过，不进入M0。
