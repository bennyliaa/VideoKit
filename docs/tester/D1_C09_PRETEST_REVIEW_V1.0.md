# D1 C09 PRETEST REVIEW V1.0

日期：2026-10-16。审查员：tester。依据 D1_C09_TESTER_REQUIREMENTS_V1.0.md（含最新设备授权）与 D1_C09_CODER_REQUIREMENTS_V1.0.md。本轮只审冻结 C08 与 C09 验收计划，不审正在实现的 C09 工作源码为候选，不运行 Gradle、编译、APK 安装或任何设备命令。

**结论：PRETEST_REVIEW_COMPLETE / WAITING_FOR_FROZEN_C09。C08 冻结完整性与静态构建证据核验通过；C08 仍不是可安装 CPU 候选。H263 是上游 MPEG4 的实际传递依赖，且存在独立注册入口；当前事实是未完成准入，不是已证 GPL 违规。C09 需先闭合所选版本的漏洞、实际编译来源/许可与完整冻结，再统一真机测试。D1 未通过，不进入 M0。**

## 1. 审核对象和证据等级

| 对象 | 本次独立结果 | 不能据此推断 |
| --- | --- | --- |
| C08 冻结链 | 2 个产物、24 个证据文件及 source-manifest 的 hash 一致；源码 ZIP 10012 个条目逐项长度/hash 匹配 | 不是 C09 身份，也不是 CPU 设备通过 |
| FFmpeg 8.0 来源 | 压缩包 SHA256 与冻结记录一致；tar 内 9888 个普通文件逐一匹配源码身份清单，源码 ZIP 对应内容一致 | 不是所选 C09 维护版本的来源证明 |
| 实际对象 | 267 个 object 的长度/hash 核验通过，267 份依赖记录存在 | 依赖记录不等于逐对象许可、漏洞可达性或最终链接来源审核完成 |
| 四个动态库 | 独立解析实际 ELF：AArch64 / ET_DYN，所有 LOAD 对齐 16384，NEEDED/SONAME 与构建记录一致 | 不是 Android/isolated 加载、16KiB 页面设备运行或 APK 内 ZIP 对齐通过 |
| 签名回执 | 已审冻结 GOODSIG/VALIDSIG 及指纹 FCF986EA15E6E293A5644F10B4322F04D67658D8；保留 TRUST_UNDEFINED 的原始限制 | 本轮没有重新运行 GPG，不把冻结签名回执称为新的独立密码学验证或完全信任 |
| 构建/规则日志 | 冻结 make 成功、Android Java 编译成功、14 项纯退出规则反例 PASS | 本轮未重跑；没有 C08 APK、CPU JNI/service 或 CPU 设备通过数 |

本次核验针对 ZIP 内冻结源与列举的 C08 证据/对象，没有把浮动根 App/Gradle 文件是否等于 C08 当准入判断。原 verify_freeze 工具还会比较当前根工作树，因此未采用其未完成结果；独立归档核验结果见 [核验记录](D1_C09_PRETEST_EVIDENCE/c08-freeze-check.json) 与 [过程记录](D1_C09_PRETEST_EVIDENCE/audit-console.log)。没有改写冻结文件或历史测试结果。

冻结摘要 SHA256：`c086f5a21a6fcfa616d244c4762e6d1c7bd8abcf336079879de02d9e038ba520`。源码 ZIP：`08e37cf7a2c13d27d8357e5d6fa48cc471a0879157bca9d9b575f237766d56bb`。未准入 native ZIP：`a1b3b9c5c43d92ed4a98cb03ea8115f1c1a0f69f8e0e1e27dfecf0123a4fe91b`。FFmpeg 原压缩包：`b2751fccb6cc4c77708113cd78b561059b6fa904b24162fa0be2d60273d27b8e`。

## 2. H263 必要依赖、注册和许可事实

已核对冻结上游 `configure`：`mpeg4_decoder_select="h263_decoder"`，`h263_decoder_select` 包含 `h263_parser`。生成配置实际 decoder 为 H263/H264/MPEG4，parser 为 H263/H264/MPEG4VIDEO；AVI/MOV demuxer；encoder/muxer/protocol/hwaccel 为空。实际 `codec_list.c` 和 `parser_list.c` 含 `ff_h263_decoder`、`ff_h263_parser`，因此不只是无对外入口的共享帮助代码。相同选择关系可从[官方 n8.0 configure](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/configure)复核。

`h263dec.c`、`h263_parser.c` 的文件头均写明 LGPL 2.1 or later；生成配置 GPL/NONFREE/VERSION3/NETWORK 均为 0。上游全源码保留 GPL 许可证或可选 GPL 文件，不等于这些文件已进入实际库。FFmpeg 的组合许可取决于具体组件及配置，见[精确版本许可](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/LICENSE.md)。以上支持“不能仅凭 H263 名称判断 GPL 混入”，但不证明整个 267 对象及其头文件、生成代码、JNI 和最终分发已合规。

C08 的 STRICT_WHITELIST 阻断作为历史交付事实保留。C09 要求已明确允许审查必要传递依赖，不应仅为保留名义两项名单而拆坏 MPEG4；本次不再要求先拆除 H263。C09 应提交“请求组件→上游选择关系→实际对象/注册入口→许可及漏洞结论”闭合表；如保留 H263 入口，也要说明实际允许的媒体格式/codec 检查如何限制入口。接受或拒绝实际输入须符合冻结实验契约，不能把“已编入”与“已批准对外提供”混为一谈。

## 3. 源身份、构建、ELF 和漏洞集中发现

| 编号 / 优先级 | 已确认事实 | C09 正式交测前所需闭合 |
| --- | --- | --- |
| PRE-01 / 高 | C08 固定 8.0，无已应用安全补丁；已知漏洞记录对实际构建标 NOT_ASSESSED | 选定精确维护版本或补丁集，逐 CVE 映射到源/对象/启用入口及输入条件；已修复、不可达或待解决均给可核查依据，不能因裁剪/isolated 而推定安全 |
| PRE-02 / 高 | source-level 聚合 SBOM 自述 object-level license incomplete；H263 注册存在，全部编译对象许可尚未闭合 | 完整源/patch/config/对象与依赖/注册清单、各许可及 NOTICE、实际 JNI 包装和所有 ELF 来源；无 GPL/nonfree/version3 或未审外部库扩入；Debug 准入与产品发行分开 |
| PRE-03 / 高 | C08 没有可安装 CPU APK，也没有 token AVIO/真实帧/单 APK isolated 实现 | C09 提交完整可安装冻结候选及测试包；库/源码/APK/配置身份闭合，不能从旧 app/build 取包或把继承 companion 方法当 CPU 实现 |
| PRE-04 / 高 | C08 改善退出记录等待和匹配规则，但只有 14 条纯规则回执；未证厂商系统会补齐 signal | 真机分别保存 App 历史退出结果和匹配的原始 crash；status0、trace absent、记录歧义/超时保持未知，不把 cleanup kill 当目标 SIGSEGV，不回写 C07 FAIL |
| PRE-05 / 中 | 四 ELF 静态 AArch64/16KiB LOAD 对齐及依赖已核验；没有运行或 APK 布局证据 | C09 新库重新检查 NEEDED/SONAME/符号、API/ABI、APK 内打包/对齐、普通 isolated 实际加载；设备页面大小和兼容事实分开，4KiB 设备成功不证明 16KiB 页面设备运行 |

官方 8.0 后续修复列表包含 C08 已列的 CVE-2025-69693、CVE-2025-63757、CVE-2025-67306、CVE-2026-8461、CVE-2026-30999，当前可见 8.0.1/8.0.2/8.0.3 的对应条目；这不是穷尽漏洞列表或实际可利用性结论。[官方安全列表](https://ffmpeg.org/security.html)。

本次进一步抽查 CVE-2025-63757 对应的[官方修复提交](https://github.com/FFmpeg/FFmpeg/commit/716cf25eb8616e8e068a7c2a5d23ae107bd117b4)：修改 `libswscale/output.c` 的 `yuv2ya16_X_c_template` 整数运算。C08 确有 `libswscale/output.o`，冻结源码该函数仍保留修复前的乘法转换写法。这说明“涉及已编译源文件”已有具体证据；函数是否留在最终库、实际目标像素格式与输入是否到达该路径、C09 是否修复仍需记录，不直接宣称当前实验已可利用。另两项补丁详情本轮未成功获取，不据此推定安全；完整漏洞矩阵仍由冻结 C09 提供。

四 ELF 的独立检查：libavcodec→libavutil/libc；libavformat→libavcodec/libavutil/libm/libc；libavutil→libm/libc；libswscale→libavutil/libm/libc。C08 目标编译参数是 API31，启用 shared、关闭硬件加速/网络/外部自动探测；这些是该次构建事实。16KiB 链接参数和成功链接不能替代实际加载、帧解码或发行许可结论。

## 4. C09 冻结后统一验收清单

**本批交付优先闭合四组：必要依赖/许可与实际库；8.0.3补丁覆盖；帧协议和真实PTS；目标故障与最终释放。下表是有限Debug CPU实验及受影响回归，不是全部产品验收。**

若本批采用8.0.3，应随冻结材料提供下列累积覆盖表，不能只列版本号或只检查8.0.3小节。本轮没有审核浮动C09源码，也没有认定这些补丁已经进入新库。

| 官方8.0维护线修复 | 覆盖核查依据 |
| --- | --- |
| CVE-2025-69693（8.0.1） | 5a6e2b0ab1bbc5a85a9575af8e4d67b4f0ed3d14 |
| CVE-2025-63757（8.0.1） | 716cf25eb8616e8e068a7c2a5d23ae107bd117b4；重点关联已编译swscale/output路径 |
| CVE-2025-67306（8.0.2） | b5996929df27276db37e075600988ebb17890eb4 与 fe72a8781b22912ec7125de1509d83fc2b1ad802 |
| CVE-2026-8461（8.0.3） | 24b452cd9f6664dcee63f1d597ba052b34f8efd2、31c9c550ef5a2aea5606c319b6299108c359f21f、3e8f3537f957da011d7360acacc9941f3ce5c306 |
| CVE-2026-30999（8.0.3） | 5c8a8750de5239136da3e2cdb2ede8122864b252 |

来源为前述官方安全列表。提交所选精确源码包含修复或等价修复的证据、全部本地patch及构建对应hash；逐项列是否编译/运行可达，未知不能写“不受影响”。这五项不是未来C09全部漏洞扫描结果；版本更新也需核查引入的差异。

下面是一个整批清单，当前均待 C09 完整冻结，不逐小功能交测。每项保留 candidate/APK/library/source hash、设备、方法、实际阶段、开始结束时间、断言与最终资源状态；前置失败只阻断相关依赖，其他独立项继续。

| 门禁 | 应提交或执行的控制/反例 | 明确通过依据与失败处理 |
| --- | --- | --- |
| G01 候选和准入 | 完整源码/签名/hash/patch/config/SBOM/许可和漏洞矩阵；精确 APK/测试入口/必要 native 库；历史库与新库区分 | 冻结清单及所有产物相互匹配，必要依赖已审；新候选身份或准入未闭合则不安装，不把 C08 native ZIP 当 APK |
| G02 设备与数据 | 正式交接后有界核验手机/平板 serial、型号、API/ABI、调试状态；实际旧包/用途/签名、空间、cache/恢复备份 | 用户已授权直接连接测试，不重复询问；仍只操作识别明确的设备。按手机→平板串行，未知包/设备或签名不符停止相关动作；未知数据不覆盖，不卸载/清数据 |
| G03 单 APK 进程边界 | CPU 库在同 APK 的非 exported 普通 isolated Service 运行；记录宿主/worker 实际 UID/PID、授权 token 及组件/权限 | worker 确为异 UID/PID；CPU 测试不启动/依赖额外 companion，不把 :process 名称当 isolated；宿主没有压缩源解析回退，非法调用被拒 |
| G04 正常 CPU 解码 | 已验证 AVI/MPEG4-part2、MP4/H264；正常 prepare/seek/EOF/drain；记录真正使用的库/decoder、实际输出帧 | 实际 CPU source/read/decoder/frame 证据，宿主活着、源 hash 不变；无帧、只回 metadata 或静态 Bitmap 不算通过。当前视频实验不顺便声称音轨解码/正式导出能力 |
| G05 自定义 AVIO | opaque token，只读短读、EOF、取消、未知长度、64 位偏移/seek-size/起止位置、>2GiB、越界/溢出及 provider 失败 | 真实 read/seek 与稳定 code，有界等待及实际账本；不传路径/文件URL/凭据，不回落 file/network protocol，不因一次空读忙循环；实际允许的 seek 契约以冻结说明为准 |
| G06 真实 PTS | 输出实际 decoded frame 的 PTS/time_base/必要的 best-effort 标记、seek 后新 epoch、B帧重排/EOS | 可与源帧/可信解码对照，时间基换算与溢出安全；请求10秒/片段内1秒不是实际源PTS。缺失/推算值需标明，不能伪装精确PTS或质量通过 |
| G07 帧协议和 TOCTOU | task/epoch、实际 Binder caller UID/PID、陈旧/跨任务/伪造身份；宽高/plane/stride/offset/长度/溢出、格式、消息数量；共享区修改竞态 | 未认证或越界数据在宿主使用/分配前拒绝；采用校验后不可变的宿主副本或证明写权限撤销，无校验后仍被 worker 修改的窗口；FFmpeg 原始布局归一化与宿主协议限制分开 |
| G08 资源上限 | 冻结明确的分辨率/像素/packet/frame/在途数量/队列/总字节、内部 decoder 峰值、超大声明与队列背压 | 压力反例可观察预算拒绝，不是只限制IPC输出后在worker先无界分配；不扩大预算掩盖失败。实际阈值由交付冻结，不把旧方案提案数值当现行实现 |
| G09 源格式与损坏 | 有效格式、错路由、空/短头/匹配头但截断body、坏尺寸、损坏packet/EOF，正常控制先行 | 真实 parser/decoder 进入和稳定失败阶段，无输出帧冒充成功、不全面声称恶意媒体fuzz通过；原媒体只读，受控反例不写共享目录 |
| G10 取消与 HANG | 实际读取/解码或帧输出后取消；独立 HANG 带正常前置、超时与经认证任务终止 | 合作式取消、等待超时和真实 worker 死亡分别记录；不能因 Future 超时宣布停工。超时后仍活跃的 I/O/帧/FD 计入 quarantine、预算不回收，不靠任意 PID kill |
| G11 SIGSEGV/第二槽 | 正常 CPU 控制后实际 native SIGSEGV；另一 CPU task 同时有真实帧；故障后宿主和第二槽继续 | 对应 PID/isolated UID/时间、目标故障与 Binder death、第二任务继续处理的证据；App 退出signal和外部原始崩溃分栏，未知不PASS。旧普通broker/companion结果不能替代此 CPU 路径 |
| G12 最终资源 | 每个成功/失败/取消路径 finally 查询 death、source operations/consumers/failedClose、帧/共享区/FD；按路径检查 lease/输出状态 | 实际归零/关闭才 SourceReleased；worker死不自动等于provider/FD全部释放。输出不存在或 force-stop 不是释放证明；失败诊断与已证明的最终释放分开 |
| G13 受影响安全回归 | 按新库/JNI/协议/ExitEvidence变更矩阵选择既有锁、输出验证、精确注入、sample后死亡/并行/跨owner恢复 | 正式 H264/AAC 双轨独立非零样本、PTS/full decode及 T02 stage/hits/cause 不放宽；采帧1视频0音频、CPU实验、旧companion分别汇总，不能用一个替代另一个 |
| G14 报告和未覆盖 | 单APK CPU、继承host、companion、纯规则、外部crash、人工效果各列证据；手机/平板分开 | 新候选只报告实际运行结果，历史ordinary UNKNOWN和C07 signal差异不重写；CPU成功不关闭产品Kit/AAR/多宿主、显示编码、模型/图片/字幕、NAS、全P0或发行准入 |

出现可安装前置阻断则先留明确证据；独立可运行项继续，不反复换候选或重跑同一不确定信号获取偶然 PASS。新素材/capture/临时输出须在交付中明确预算和保留方案，保留原有两份 C06 及 C07 capture，不按新前缀默认无限新增，也不主动清理。

## 5. 集中交接条件与下一步

- 当前无需用户再次批准手机/平板测试；最新授权已明确。C09 完整冻结并由负责人统一交接后，直接按 G02 核验，再手机、平板串行集中测试。若 RSA/物理连接需要人工操作，只告知实际必要动作。
- coder 一次交付自洽 CPU 实现、许可/漏洞/构建闭合、完整 APK/hash、入口及预期原因/预算和受影响回归矩阵；本报告不审核其浮动源码或提前给出设备 PASS。
- 本次只形成这一份集中 PRETEST_REVIEW 和支持证据，没有派新设备批次、下载新CPU二进制、Gradle或设备操作。完整 C09 实测报告仍待正式交测，不能拿此文替代。
- 产品发行/专利与宿主分发义务、模型权利/质量、完整高风险流水线和全部P0继续未决。D1保持未通过，不进入M0。
