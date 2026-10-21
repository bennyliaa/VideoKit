# D1 C01 冻结证据独立审核

日期：2026-10-05；候选：D1-20261005-C01；审核人：VideoKit tester。

结论：冻结材料完整性和限定范围的实验/构建记录核查通过；C01 仍为 NOT_READY，D1 仍未正式验收，不进入 M0。本报告的 PASS 仅限证据审核，不代表 Android 功能、性能、跟踪、安全导出或阶段全量通过。

## 1. 对象、方法和边界

依据 [审核需求](../milestones/D1_C01_EVIDENCE_AUDIT_TESTER_REQUIREMENTS_V1.0.md) 和 [C01交付](../coder/D1_DELIVERY_D1-20261005-C01.md)。以 d1/evidence/freeze-summary.json 的 C01 长度/hash 为基准，逐项复算复制产物和证据文件 SHA-256。源码只从已验证的 C01 ZIP 读取，不使用变化工作树；交付文本同时与 ZIP 内冻结版本核对。冻结时间声明为 2026-10-05T02:50:34.899961+08:00。

独立检查采用 PowerShell/.NET ZIP 与 SHA-256 API；读取日志、JSON、冻结源码、APK ZIP/DEX 字符串。未运行 Gradle、javac/实验程序、媒体解码、APK安装、adb或任何设备操作，未改产品源码、coder输出、test_media。没有重跑28项实验；审核其日志与冻结实现是否对应，不把日志当独立实测。模型/许可资料只核查冻结记录，未作联网权利调查或法律合规结论。

hash仅证明审核时内容与交接清单一致，不证明构建过程的外部真实性或密码学签名来源。独立 hash 记录：[freeze-hash-check.json](D1_C01_AUDIT_EVIDENCE/freeze-hash-check.json)。

## 2. 冻结身份与产物

四个产物与26个证据文件共30项，长度/hash全部匹配，无缺失或差异。source-manifest.json hash为 8b02a24aa83ce83762685eeb69499c948c5a413cc077ea51be220b202677487a；ZIP共94条，manifest中94个source_files逐项长度/hash全部匹配，无额外条目。git_commit为null。证据虽不在源码ZIP内，freeze-summary已单独列hash，现已全部核对，不能误判为未冻结。

| 对象（位于 docs/coder/d1/artifacts/D1-20261005-C01） | 字节 | 独立SHA-256 | 结果 |
| --- | ---: | --- | --- |
| app-debug.apk | 39664163 | 01208e1634ea1c3c54c133766d6d7e659f47153e6422a17e0deb8dc86967c4fd | PASS |
| app-debug-androidTest.apk | 2252788 | 513aefcb2a41ec5cd8a280d855059c6c4198e2f53572f0be066db99b2c57cf7e | PASS |
| app-release-unsigned.apk | 22066538 | e874aab072dd54a58ef09e618fc43b20cde6dd8edd61d87b978f2639517f6f17 | PASS |
| D1-20261005-C01-source.zip | 307791 | b06874cbedfb1d06dd858723f722e1dda892e1cdc5c94cc955156fabe920a027 | PASS |

独立DEX字符串检查：Debug/Test均在classes4.dex包含Spike描述符；Release没有该描述符。Debug/Release仅列四ABI的libandroidx.graphics.path.so，Test无原生库。未发现test_media/sample媒体/大MKV/新增AVI命名条目；这只核实特定命名和描述符，不能排除任意改名资源或证明全部隐私要求。

aapt冻结日志显示Debug/Release minSdk31、targetSdk36；冻结build.gradle.kts相同。Test APK SDK未提供单独aapt日志，本轮未重新执行aapt，Test SDK独立核查为NOT_RUN。静态日志无INTERNET权限，不代替网络实测。

## 3. 构建、依赖和媒体审核

| 项目 | 证据/实际观察 | 结果及界限 |
| --- | --- | --- |
| 集中构建关联 | 冻结构建配置引用d1 Debug与androidTest源；final-build.log含assembleDebug/Release/DebugAndroidTest和testDebugUnitTest，BUILD SUCCESSFUL 21s；strict-verification.log为20s成功 | PASS：记录与配置相符；未独立重建 |
| 基线失败与SDK警告 | baseline失败记录保留；compileSdk37.2配置与日志吻合，AGP9.3.3声明测试至37.1 | PASS：警告已披露；37.2平台兼容实测NOT_RUN，不能因warning即判构建失败 |
| 单元测试范围 | JUnit XML仅addition_isCorrect，1条，0失败/错误 | PASS：限该记录，不验证D1业务 |
| Release | 冻结配置release optimization.enable=false；unsigned APK，无AAR | PASS：基线描述准确；R8/正式Kit发布验收NOT_RUN |
| 依赖分类 | dependency-inventory：344项；107 Release runtime，147 Debug runtime（配置有重叠）；61项无直接POM许可声明 | PASS：统计复算一致；完整NOTICE/漏洞审查BLOCKED |
| 工具/产品区分 | JNA5.6.0与javax.annotation-api1.3.2列在lint/UTP工具，非runtime；Guava listenablefuture1.0位于Release runtime，POM许可空 | PASS：分类相符；缺声明需补证，不据此断言违法或全面许可通过 |
| 锁与校验范围 | ZIP含app/gradle.lockfile及verification-metadata.xml，严格验证日志已hash核对；依赖清单有缓存artifact hash | PASS：资料存在；未复算全局缓存artifact，首次hash信任不等于签名/安全/权利证明 |
| 模型 | 固定Zoo commit、YuNet/ViTTrack LICENSE/README/LFS指针均hash匹配 | PASS：文本证据；实际权重未下载/hash验证、训练/预训练权利不足，集成BLOCKED；推理质量NOT_RUN |
| 媒体 | 冻结inventory含45个文件，17个manifest样本及桌面局部探测；大MKV有H264/AC3/ASS轨；新增AVI/SRT有记录 | PASS：记录核查；未重读源媒体hash/解码，Android渲染NOT_RUN |

字幕缺口更新：新增AVI记录为XVID、624×352、MP3，不能按文件名推断H264/720p。外部SRT记录GB18030严格解码、1445条、相邻重叠1；大MKV内嵌ASS记录已存在。因此不再笼统列“没有字幕样本”。待验证的是侧挂多source/token路由、GB系中文渲染、ASS支持、选择/关闭/Seek与对白同步。清单解析不证明设备解码和字幕效果。

动态GIF/WebP均为1帧，不能作动态图通过。双音轨与跟踪人工标注集仍未证实。HEIC/HEIF桌面无解码器是NOT_RUN，非坏图FAIL；TS/M2TS编码仍主要依提供者声明。样本授权仅限本地测试，不自动允许产品打包/分发。未重复读取约GB级源文件，源前后完整性结论仍是coder冻结证据声明。

## 4. 28条断言与冻结实现映射

contract-probe.log实际有28条PASS和RESULT passed=28 failed=0。冻结ContractProbe实现可以对应这些断言，未发现日志把复制或模拟步骤伪称真实编码。下表每条审核结果均为PASS，仅指对应关系；执行层面的独立复测为NOT_RUN。

| 日志序号 | 断言 / 冻结实现 | 证据限制 |
| --- | --- | --- |
| 1 | known length：MemoryHandle 5字节 | 合成数据 |
| 2 | short read and target offset：每次最多2字节 | 合成短读 |
| 3 | short reads reach EOF | EOF与短读在同一断言 |
| 4 | INVALID_RANGE：负offset | 未覆盖全部整数溢出 |
| 5 | INVALID_RANGE：offset超过已知长度 | 非真实远程源 |
| 6 | idempotent release and drained | 无在途I/O场景 |
| 7 | SESSION_RELEASED | 关闭后读取拒绝 |
| 8 | unknown length | MemoryHandle length=null |
| 9 | unknown-length EOF | 循环结束后check(true)，返回流内容未完整断言 |
| 10 | SOURCE_DISCONNECTED | 人工抛IOException，不是NAS断线 |
| 11 | INVALID_READ_RESULT | 人工返回0 |
| 12 | actual file offset above 2GiB | RandomAccessFile读取offset=2^31+12345的64字节 |
| 13 | large-offset bytes match independent seek | 同一本地文件、独立RAF基准；不是播放解码 |
| 14 | worker I/O starts | CountDownLatch等待工作线程进入 |
| 15 | cancel drains cooperative transport | close释放latch；没有非协作provider |
| 16 | stale result cannot mutate caller buffer | 私有缓冲、关闭结果丢弃；未验证跨bindingGeneration所有访问 |
| 17 | copy sample becomes ready | Files.readAllBytes＋字节复制/重开比较，不是编码/封装 |
| 18 | open fault aborts | 打开真实文件后人工抛错 |
| 19 | write fault aborts | 实际写成功后人工抛空间不足，不是真实满盘 |
| 20 | flush fault aborts | 人工抛错，未fsync验证耐久性 |
| 21 | close fault aborts | 实际close后人工抛错，非未关闭句柄失败 |
| 22 | validate fault aborts | 重开验证返回false |
| 23 | OUTPUT_CAPABILITY_UNSUPPORTED | random=false拒绝 |
| 24 | preflight before open | 检查open计数0 |
| 25 | CANCELLED | write完成时同步cancel |
| 26 | cancel never ready | 检查ready=0/abort=1，未独立完整竞态 |
| 27 | OUTPUT_READY_UNKNOWN | ready++后人工丢响应 |
| 28 | unknown response not blindly aborted | 仅ready=1/abort=0；未实现状态查询和幂等恢复 |

协作取消1.0861ms是日志单次Windows测量，不能成为Android/NAS取消阈值。resource-budget.log与冻结实现对应12槽硬上限、预留、内存拒绝、幂等释放及跨槽保留，审核PASS；没有真实codec容量、峰值内存、热、唯一声音、原生崩溃隔离证据。

## 5. D1七项覆盖与集中阻断清单

| D1项 | 证据审核结果 | 正式能力结论 |
| --- | --- | --- |
| 1 基线/样本 | PASS（限定记录核查） | 真机格式和特殊覆盖NOT_RUN，部分完成 |
| 2 依赖/许可 | PASS（记录/分类） | 完整供应链及模型权利BLOCKED |
| 3 readAt/Seek | PASS（局部桌面断言/编译） | 真机Seek和非协作取消NOT_RUN，异步生命周期BLOCKED |
| 4 编辑/Sink | PASS（复制/故障模拟记录） | 真实编码NOT_RUN，未知ready恢复BLOCKED |
| 5 跟踪 | PASS（文本身份） | 权利BLOCKED，质量/纠正/离线隐私NOT_RUN |
| 6 预算/隔离 | PASS（策略记录） | worker实现/原生故障隔离BLOCKED，硬件与热NOT_RUN |
| 7 跨平台分析 | PASS（已提交分析） | Apple/Windows实现NOT_RUN，不阻断Android |

以下为交给负责人的一个集中补齐批次；静态缺口不是已在产品真机复现的缺陷。

| ID / 严重度 | 复现或缺项、影响 | C02必要补齐与回归 |
| --- | --- | --- |
| B1 / 阶段阻断 | AndroidReadSeekProbe未运行，仅当前位置/STATE_READY与句柄计数，未断言正确视频帧、连续播放、快速Seek和跨generation | 负责人安排授权手机/平板；产物对应格式/字幕/2GiB+Seek/取消/Surface与codec资源证据；覆盖真实帧与生命周期 |
| B2 / 阶段阻断 | 权重只有LFS指针，无有效训练/预训练权利链与标注质量集；没有模型加载/纠正/LOST/AMBIGUOUS | 提供有效权利或合法替代及实际权重hash；人工标注覆盖、纠正revision、未覆盖导出门禁和离线网络/落盘实测；缺数据不宣称可靠 |
| B3 / 安全阻断 | 冻结实现为App进程，无worker/broker；预算策略不能隔离SIGSEGV/OOM | 按任务隔离原型、授权broker、原生crash/kill/OOM/取消失效注入；验证宿主/其他槽存活、资源和输出回收 |
| B4 / 安全阻断 | Sink未知ready只有READY_UNKNOWN；markReady在terminal锁内同步调用，响应挂起时cancel等待该锁；没有任务查询、deadline/幂等恢复；真实编码未执行 | 补同exportId/handleId查询、异步仲裁/有界取消；真实Transformer编码与重开结构/PTS/音画验证；测未知响应、并发取消、kill及失败abort |
| B5 / 阶段阻断 | NOTICE/POM缺项/漏洞未关闭；动态GIF/WebP、双音轨、特殊图与标注缺口；字幕有样本但未验证路由/渲染 | 产品runtime与工具分表；补必要许可与漏洞资料、有效样本及hash；真机动画/音轨/中文SRT/ASS测试；不扩大授权为再分发 |
| A1 / 高，归B1 | ReadBridge.close先closed=true，再handle.close；若close抛错，重复close直接返回，无法重试失败释放；与交付披露一致 | 补失败关闭重试/状态查询、在途drain完成与资源归零，不能以已标closed作为已释放；注入先失败后成功close |
| A2 / 高，归B1 | 同步桥依provider协作close；HostDataSource.close不awaitDrained，factory/open与close无完整仲裁；没有SourceReleased聚合事件 | 异步工作执行器/deadline、非协作读取试验、open/close竞态、generation和多消费者租约归零；验证源释放顺序 |
| A3 / 中，证据补齐 | Test APK无单独minSdk badging；工具校验日志未记录完整调用命令/退出码为结构化运行清单；快照hash不能证明从该快照构建 | C02附三APK badging及命令/工具版本/开始结束/退出码、候选源hash与构建关联；无必要不重编C01 |
| A4 / 中，兼容风险 | compileSdk37.2超过AGP声明测试上限37.1；unsigned、未优化Release是基线，不是发布Kit | 记录采用方案和兼容验证；发布阶段另做签名/R8/独立AAR，不为D1随意要求提前实现M0 |

输入零长度、target越界/溢出、提前EOF与已知长度冲突、非协作取消、open/close并发、完整ready/取消竞态并未由28条全覆盖，需增加有意义证据。Sink abort幂等仅使用deleteIfExists实现，现有日志未重复调用验证；不能将源码表面幂等视为实测PASS。

## 6. C02接收建议与停止条件

C02先提交唯一candidateId、整包完成矩阵、复制产物/源码ZIP/证据hash、完整构建自检记录、样本/依赖/权重身份、设备和未决项。C01现有匹配证据无需为本轮审核重复构建；任何修复必须归C02，不静默替换C01。

若B1–B5仍有关键缺项，负责人先处理接收条件，不把半成品当正式完整候选。真实测试需要设备操作时由负责人通知用户并完成授权。合法样本/模型权利与阈值未就绪时保留NOT_RUN/BLOCKED。不得以本报告的证据PASS冻结异步输入、Sink恢复、worker隔离或跟踪质量。

本轮完成证据审核后停止，等待负责人派发C02完整候选正式验收；D1仍未正式验收，不进入M0。
