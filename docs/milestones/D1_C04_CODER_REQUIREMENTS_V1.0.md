# D1 C04 集中修复需求

## 平板 C03 批次补充（2026-10-05 11:40）

tester 已结束平板 C03：7 PASS、5 FAIL、10 BLOCKED，详见 docs/tester/D1_TABLET_TEST_REPORT_V1.0.md。将以下内容合并本轮 C04，一次冻结交接，不另开小批次：

- TABLET-C03-01：宿主 realEncoderOutput 与 companion 实际编码都 code1001 失败；ACodec NO_INIT 仅关联现象，需完整 source/decoder/encoder/muxer 原因链、正常编码恢复和实际输出解码门禁。正常前置失败造成 T02、sample 后取消/死亡、第二槽与跨 owner 恢复阻断，必须保留整批回归入口。
- TABLET-C03-02/03：普通隔离 start WORKER_START_FAILED 和 broker NORMAL 失败，合并手机 worker 缺陷处理；正确失败阶段与释放不能由任意 IOException 替代。
- TABLET-C03-04：AVI 10秒取 scaled frame 为 null，需诊断取帧与有界能力错误、合理对照；不得用空帧绕过检测或声称跟踪质量通过。
- 平板 AVI 播放通过，用户确认平板 MKV 有声音、字幕正常；手机 AVI 挂起和 MKV 无声仍未关闭。不得把跨设备正常结果作为手机修复证明。

tester 已停止平板批次、保留包/fixture/账本；coder 继续仅本机，不操作设备。若无法完成某项修复，在交付矩阵准确列 BLOCKED 与证据，不能把未证根因或编译通过计为缺陷关闭。

日期：2026-10-05；状态：已派发。用户允许切换平板。coder 不操作手机、平板或 ADB；tester 独占平板并使用冻结 C03，不运行 Gradle。

依据：D1_PHONE_TEST_REPORT_V1.0.md、D1_DELIVERY_D1-20261005-C03.md。冻结 C01/C02/C03 不得修改。一次完成以下缺陷分析、修复、自检和新 C04 候选，再整体交接，不逐功能派测。

1. PHONE-C02-01：提供 Windows 二进制安全、流式且有界的 fixture 传输工具。可参考 tester 的本机 ADB shell-v2 工具，保持指定序列号、固定私有目录、空间与未知数据门禁、长度与 SHA-256 校验；控制字节及超过 2GiB 偏移/流式路径验证不能以小文本代替。本轮不操作设备或重复复制大文件。
2. PHONE-C02-02：检查 AVI/SRT 180 秒挂起的调用链，加入 prepare、主 Looper、Extractor、字幕读取的分阶段日志及有界取消/释放。不得根据一条 Wav sniff 日志认定根因。明确同 AVI 无侧车对照和手机复测入口；支持限制给出稳定错误，不能静默删除 AVI/字幕要求或以报错替代既定格式验收。
3. PHONE-C02-03：定位普通 worker NORMAL 的 IOException，记录 bind、source open、broker RPC、读取阶段与原始 cause；NORMAL 成功才进入故障注入，未到达目标阶段不能 PASS。结合 C03 实现作回归，不混淆 broker 与真实媒体隔离。
4. PHONE-C02-04：分析 MKV 有画面无声音、同机 MP4 有声音。补音轨格式、支持程度、选择、renderer、audio session/focus 的脱敏诊断及非静音人工观察入口。自动 setVolume(0) 不验证声音。若 AC3 路径确有缺口，提交许可证适合闭源的兼容方案及证据，未经准入不得引入 GPL 二进制；不靠 READY 或静默丢弃音轨通过。
5. 保留 C03 的 T01/T02 独立视频/音频、PTS、解码、注入阶段/命中/原因门禁，修复不能回退安全要求。补本轮受影响的有意义局部验证，必要编译集中进行。

异 UID companion 仅批准 D1 实验，未批准作为产品额外安装包。提交无需用户另装 companion、适合独立 Kit 与单 App 分发的隔离方案评估；同 UID 多进程仅是崩溃边界，不能宣称权限隔离。不能弱化原始 P0，无法同时满足的条件明确列出供负责人决策。

交付 docs/coder/D1_DELIVERY_D1-20261005-C04.md，含缺陷逐项状态、根因证据与尚待设备证明的假设、完整冻结产物/hash、源码清单、集中补测需求。未经真机证明不把四项缺陷标已关闭；D1 仍 NOT_READY，不进入 M0。
