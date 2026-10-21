# D1 E4 单 APK Android 媒体执行进程原型交付 V1.0

2026-10-17。交付范围是本机集中实现、离线编译、纯 JVM 规则自检和下一批设备计划。当前 Android 编码、安装、ADB、播放、native fault、真实进程死亡及硬件验证全部 NOT_RUN。D1 未通过，M0 未启动；全部原 P0、C14 的73项待设备及两项信号 NOT_RUN、历史 signal0 FAIL 均保持。

完整工程位于 `D:/CodexProjects/VideoKit/docs/coder/d1e4`，独立 Gradle 只含一个 app 模块，applicationId 仍为 `com.videokit.app`。没有改根 app/settings/manifest、旧 C14 冻结源码/产物或测试结论。交付一个 Debug app APK 和它的 instrumentation APK；后者只用于测试，不是 companion 媒体安装包。E4服务、故障代码、CPU原生库和 NOTICE 只进入 Debug source set，未建立新的产品 release 或 AAR 交付。

host `E4Session` 只控制与授权 broker，有限原始帧走 Android Binder，不经 Flutter/Dart。压缩输入及压缩输出验证复用 C14 ordinary isolated `CpuIsolatedService`；最小23个原 Java 依赖和7个原 native 库逐字节复制并记录来源，完整C14源码 ZIP 一并保留。源只读 Provider 的实际 read/close、CPU 原注册 Binder/UID/task/epoch、actual death/source release/slot归还沿原协议。没有扩大 FFmpeg 8.0.3 编解码或网络功能，也没有新下载依赖或模型。

`E4CodecService` 在同 APK 的 `:e4_codec` 单独进程、`exported=false`，与host同UID。它持单一owner线程，运行有限codec枚举/四提案协商、六帧RGBA→AVC、Image/Plane和Media3 1.9.3 FragmentedMp4Muxer。只收固定裸帧与获授临时 Sink/lease FD，不收源FD、任意路径、URI或凭据。它提供崩溃边界，不能称权限/RCE隔离；sameUID自身对宿主私有文件/权限的能力仍是残余风险。

`E4Protocol` 与 `E4Broker` 提供完整task/epoch/generation/原service实例及UID匹配，帧队列2、单consumer、encoder/output1、六帧顺序/PTS/布局/alpha、实际owner关闭返回账本。ResourceLease跨线程关闭拒绝；CLOSING不计归还，异常UNKNOWN保留原对象且不重试。host ledger只记录已ACK的转发及远端证据，不能假造host encoder资源或把转发当实际编码。

新CPU桥接获得六个真实snapshot，保留原时间基/实际PTS并逐帧等待消费返回。codec只能到 `ENCODED_AWAITING_ISOLATED_VALIDATION`；host还须核原service关闭/回调ACK归还、Source/Sink/worker lease，取得 isolated 完整EOF/六帧/PTS≤1ms/画面内容验证，随后才请求原FencedTask临时输出READY并实际关闭owner。工具READY仍非产品业务COMMIT。

Binder入口为同步有界协议，核原调用UID及任务/代际/实例。callback也采用同步metadata ACK：magic、原hostUID和原service实例必须一致，实际返回前保持callbackInFlight；失败或挂起保原callback/event与UNKNOWN。host在后续原Binder QUERY确认callback归零，不把callback自己声称的结束当原返回。PID只作原实例一致性观测，不作为独立安全身份；这一选择依据[Android Binder API](https://developer.android.com/reference/android/os/Binder#getCallingPid())，其oneway回调不提供PID。

取消仅撤销新工作并排原owner清理，迟到或旧代帧不能复活。原service Binder death产生App `WORKER_DIED`，保留系统原reason/status；status0仍UNKNOWN_FAIL，不从故障名称、ARMED或清理补成signal证明。该代未证资源/编码许可继续PENDING，另一CPU真实任务按自身两槽/源继续；重连仅先做新实例metadata及旧身份拒绝验证，不借新代绕过原未知编码许可。

Debug白名单含能力拒绝、首次配置拒绝、实际release后未证ACK、owner有限暂停，以及自身service的两阶段self-kill/native-segv。fault需原hostUID/PID/task/epoch/gen/实例和一次arm token，延迟执行前再核原Session，native hook还核Debug和自身`:e4_codec`进程。代码本批只编译，绝未执行这些故障。旧CPU信号链没有借E4重跑或改判。

本机纯Java集中自检已PASS：89项，javac/java各一次、零修复；证据 `evidence/local-check-results.json` 与原日志/源码hash绑定。覆盖六帧顺序、队列2/consumer1、UID/旧代、实际close未返回、UNKNOWN不复用、取消迟到、原实例死亡只影响自身记录、host与远端资源证据分离。它不证明真实Binder/codec/硬件或进程故障。主Android构建的原记录及必要修复全部保存在 `evidence/build-attempts` 和最终 `build-results.json`，不删除失败或将编译算作设备通过。

最终离线构建 `repair-004` 已PASS并核源码快照一致。共保留1个MAIN及4个必要REPAIR：MAIN缓存锁权限失败；repair-001公开SDK目录标志不兼容；repair-002缺已缓存的coroutines1.8.1实体，保持offline并对齐原C14已锁定/完整缓存的1.9.0及Kotlin2.2.10；repair-003为取消幂等修复前成功版本，原记录另存；repair-004重编最终源码。没有重复相同源码求PASS，JVM自检未重复。APK审计曾仅因aapt2布尔文本表示不同而解析失败，失败记录保留，修正元数据解析后复用已成功的签名检查，不重新构建或替换APK。

最终app Debug APK为10529808B，SHA256 `7368e7d9cdef6ad810014dc71f04cf22f6aefbc60c51019588f09df363bdeca9`；instrumentation APK为2711421B，SHA256 `427383e302708e1a0f6003d209fabed94ac969450f9fe3bbcc3f6e680ce1b171`。两APK v2签名校验通过，证书SHA256均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，未打包私钥。实际manifest两service均未导出、CPU isolated=true、codec isolated=false；合并权限仅ACCESS_NETWORK_STATE，未声明INTERNET或companion查询。该normal权限允许同UID host/codec查询网络状态，不等于已运行联网；ordinary isolated不继承应用权限。

资源限额：固定256×144、stride1024、RGBA147456B、六帧、queue2/consumer1、CPU2、encoder1；保守16份可达RGBA2359296B+YUV55296B，主帧Parcel196608B、callback16384B。它不覆盖未回收ART垃圾、Binder/系统codec/驱动内部缓存或整个RSS，设备仍须实测。协商≤4创建/12s，总正常管线60s；原生或Binder调用超时只报PENDING并保owner，不强行中断。HELLO同原Binder至多51次、名义5s窗口；正常末尾关闭至多21 QUERY，取消至多101 QUERY，间隔50ms、名义约1/5s。单次同步调用若不返回，这些窗口不构成硬中断或归还证明；仅等待原控制metadata，不新建实例或重设基线。

host仍运行原 `AndroidLease.exclusive` 的受控FD flock/unlock JNI以及文件/同步/Binder平台native调用，这是明确保留的J06风险，不声称host零JNI。旧host MediaExtractor等未编入本批最小APK，但正式产品的J01/J07以及字幕、图片、Surface/AudioTrack、跟踪GL等J08–J11未因本编码service关闭。逐调用位置、权限/故障边界、实际待证明和Apple/Windows仅设计见同目录架构及剩余门禁两文档。

`upstream-copy-map.json` 对原C14字节复制，`derived-source-map.json` 对协商/编码/平面转换/fMP4改包适配给出原hash；完整source ZIP、APK/签名证书、实际7 native库与SBOM差异均由本批source manifest/seal及只读verify约束。APK不包含机器配置或签名私钥。外部完整交付报告提供最终freeze与源码ZIP/APK hash，避免被自身绑定的文档循环嵌入seal hash。

SBOM记录35个实际锁定Maven坐标，新增package family为0；减少后的工程有14个package family所选版本集合与原C14不同，完整差异在 `evidence/sbom-difference.json`。原Media3固定1.9.3、7个native库逐字节保持；没有把整个依赖图称为不变，也没有新增SCA/漏洞或生产分发许可通过结论。缓存artifact读取11796560B，未发起依赖下载。

下一步由负责人一次交tester做独立静态审查，再正式派新的有限设备批次；本窗口不自行派测试、不轮询设备、不请求连接。手机/平板原App禁用/缓存/安装状态须现场只读核，不能借换包名、删除数据、companion或旧成功绕过。具体方法/前置/故障隔离调度/停止规则见 `D1_E4_DEVICE_EXECUTION_APPENDIX_V1.0.md` 和包内 `tools/device_plan.json`。
