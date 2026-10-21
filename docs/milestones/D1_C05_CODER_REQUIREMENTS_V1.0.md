# D1 C05 集中修复技术需求

日期：2026-10-05；依据 docs/tester/D1_C04_TABLET_TEST_REPORT_V1.0.md。平板 C04 已结束，23 方法20通过3失败；正式 D1 尚未通过。一次完成以下修复、自检和候选冻结再交 tester，不逐项编译或交接。

1. TABLET-C04-01：普通 broker SIGSEGV 模式在 RPC_DONE 后返回普通结果，HANG因此未执行。查实际信号触发、处理、回传与 Binder death 竞态。故障必须证明指定任务/模式实际死亡或超时及源/租约最终状态，不能只凭进入 mode 或任意 IOException 通过。与已经通过的 companion sample 后 SIGSEGV 区分。使 HANG 可独立有界执行，避免一个失败遮蔽所有后续覆盖。
2. TABLET-C04-02：ordinary codec 探针 WORKER_DIED 不能认作已证权限拒绝。收集实际 codec 调用阶段、Java cause/native abort、UID/PID及死亡/协议日志；若平台合法表现为 native death，测试只能在有具体原因证据和正确释放门禁时描述该事实，不将无原因死亡重命名为拒绝通过。保留源、FD、lease释放未知为 quarantine。
3. TABLET-C04-03：AVI10秒 scaled/unscaled 均为空，MP4对照正常。评估从现有许可已准入的播放/解码管线取得指定时间帧的方案，平台支持缺口及适合闭源的替代依赖须单列准入。不能换0秒、空Bitmap、删除AVI或改用仅MP4通过；实际帧时间未知如实记录，不宣布检测质量通过。
4. 保留 C04 已通过的正常导出、T01/T02、真实sample后取消/死亡、第二槽与跨owner恢复门禁。不为修复普通探针回退实际管线安全要求。手机问题仍需后续真机补测，不能据平板通过关闭。

仅本机修复与集中自检，不操作手机/平板/ADB，不修改 C01至C04 冻结件或测试媒体。额外 companion 仍仅D1实验，产品单App独立Kit隔离方案及模型许可未决继续列出，不弱化P0、不进入M0。

交付 docs/coder/D1_DELIVERY_D1-20261005-C05.md，含三项缺陷逐项根因/状态、实际证据与假设、准确冻结源码/产物/hash、必要自检、完整设备追加批次。无法修复明确 BLOCKED，不能把新增日志或编译成功作设备缺陷关闭。
