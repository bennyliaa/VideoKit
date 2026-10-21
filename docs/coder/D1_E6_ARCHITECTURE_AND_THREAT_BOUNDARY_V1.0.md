# D1 E6 架构及威胁边界 V1.0

2026-10-17。本批修复输出时间封装，并提供精确诊断；隔离解析与真实画面验证不降级。

## 根因证据链

已授权导出件唯一固定53651B/SHA，经只读容器解析：首moof5样本duration均18750/90000s，次moof1样本duration0，无tfdt/ctts。对照原FFmpeg8.0.3 MOV代码的无tfdt/sidx→track_end回退、原JNI逐帧PTS谓词及旧实机前5日志。真实输入六PTS为0/208333/416667/625000/833333/1000000；旧容器末PTS1041667。原JNI输出验证在verified=5时仍按expected[5]比较；不把未写第六callback当仅解码五帧。

实际Media3旧配置复现相同两段错误；新生产E6Muxer与同版本真实库回放修正为一段六样本、末间隔15000和结束duration18000，所有PTS无偏移。封装3000ms阈值覆盖原2s合法输入窗和0.2s空EOS；仍2MiB最终文件、6samples、原压缩单sample256KiB。这里只改变分段策略和结束元数据，不改编码输入或时间、容差、解码计数、内容检查。旧native实际哪条branch当时未记录；目前证据证明容器缺陷可触发原拒绝，实际Android仍待复核。

## 生产native变化与精确诊断

原codec send/receive/drain循环没有为了PASS改写；AVERROR(EAGAIN)/EOF严格原规则保持。新e6_verify.h抽出等价严格维度/六帧/1000µs/完整demux+decoder EOF谓词，依旧在像素/PTS合格后才发frame callback、逐帧accept后才计数。源码原索引短路保持，第七帧不能读expected[6]。EOF不够6或decoder未EOF继续拒绝；无fake EOF或content pass。

在原cleanup真实释放FFmpeg对象后，若无原JNI pending Java异常，发一次onNativeDiagnostic（10个int+3个long）。site0表示本次成功；reason1…9表示DIMENSIONS/EXTRA_FRAME/PTS/MISSING_PTS/DEMUX/SEND/RECEIVE/DRAIN/INCOMPLETE_EOF；其余失败reason0/nonzero site精确映射到冻结cpu.c原行谓词。evidence/native-diagnostic-sites.json绑定源码SHA及每处条件。FFmpeg返回失败处保留原AVERROR，不把业务谓词0当系统错误；早期JNI返回或pending callback原异常若无snapshot，明确NOT_COLLECTED，不补零。

pkt计数为选中视频packet发送尝试数，decoded是receive实际帧数，accepted是完成原frame ACK后的数量；native readAt是JNI实际调用次数/返回字节，host另记录broker requests/returned bytes，不能以缺日志为0。诊断只含固定数值和本地映射的安全码，无native任意字符串、源路径、句柄或凭据。

CpuProtocol新增NATIVE_DIAGNOSTIC=17，保持单APK同版本host/isolated部署。原真实caller PID/UID/task/epoch/revoked检查及1024B metadata限额先于分发；一次snapshot、阶段/accept计数和字段边界校验，拒绝重复/错阶段/越界/尾数据。DONE仍需原6帧+orientation，另需本次native site0/accepted6/demuxEOF1/decoderEOF1。错误对象保留结构及代码，经原Future传播、E6FailureCodes最多8层first cause，cleanup suppressed单列。主报告validatorNativeDiagnostic完整字段与仪器HOST_DIAGNOSTICS显式名单贯通，trace只记短code；原160字行不会裁掉EOF/read计量。

## 保持的隔离、所有权及原现场

主进程不解析不可信原压缩媒体。真实六源解码和输出验证仍在无FD/path的isolated CPU，原broker只授予来源readAt；编码仍私有codec进程/真实MediaCodec，thumb/content/mapping完整校验仍生产PipelineRules，未用桌面回放代替。绝对60s、首次cancel30s、原session/CPU/slot/FD/Native call真实返回、callback ACK及原budget/R/S/无pending门不变。代码所有权/lease/current-host观察未新建替代路径。

原E5C/E5B冻结、实际G01范围、原N2结算R/S0/原closeACKfalse、旧N2 FAIL、53651消费/失败输出保持。新candidate不带一次性已消费的E5C夹具入口，不重跑旧根；Guard等相关生产源码字节不变。原本机/旧设备UNKNOWN不补证或清理。

## 本机证据边界

17项C测试直接编译并运行同生产header（Windows普通进程返回，无信号故障），17项Java执行生产诊断/cause/cleanup及未改PipelineRules正负例。真实Media3回放仅有独立SparseArray/TextUtils API shim，不替换封装算法；尚未桌面解码、Android JNI/Binder/MediaCodec/真源回归。静态传输/schema核验与编译不能代替远端实际调用。新的native诊断本身亦待Android实证。

原有限FFmpeg版本/配置/算法源码/六库不变，仅本项目cpu JNI wrapper重编；NOTICE-E6、完整原C14对应源容器、所需header/config及exact SHA/diff/build保留。静态16KiB ELF/ZIP检查不等于16KiB设备通过，SBOM/来源不是合规或安全放行。
