# D1 C03 M0 冻结边界

日期：2026-10-05；建议清单，未执行 M0 冻结，D1 仍 BLOCKED / NOT_READY。

## 可以提交负责人评审的语义

| 语义 | 已有证据 | 限制 |
| --- | --- | --- |
| 不透明 Source token、只读、64 位偏移、未知长度、短读与 EOF | 47 条桌面契约；实际 broker/DataSource 编译 | 具体外部 provider、NAS 与断线尚未实测 |
| read 缓冲区归桥接层、迟到结果只排空、generation 隔离 | 桌面实际 operation/consumer 账本与非协作队列耗尽 | timeout 只结束等待，不宣布实际释放 |
| close 失败保留、每个实际 handle 的有限重试和查询 | 新 24 条中的双 handle 恢复、永久失败不释放及队列测试 | 三次上限是原型限制；正式 provider 恢复能力须另验 |
| SourceReleased 要求 retired、零 consumer、零 operation、零 failed close | 桌面账本测试；Android broker 编译 | 只描述源，不能代表输出 FD、Surface 或全局设备清理 |
| 同 task 查询未知 READY、READY 与 COMMITTED 区分、abort 不删除已 READY | 原契约与新跨 owner 桌面进程实验 | Android journal/fsync/Binder/FD 锁运行尚 NOT_RUN；正式宿主 ABI 未定 |
| 输出预设必须独立核验视频与音频样本、实际解码才 READY | 12 条反例通过；实际 Android 解码入口编译 | 设备实际 decoder 门禁 NOT_RUN；当前仅 256×144 H264/AAC 短片原型 |

以上可评审的是语义，不是宣布跨平台、Android 真实 IPC 或最终接口已经通过。

## 不得冻结的关键架构与能力

普通 `isolatedProcess=true` 不是已证明可执行硬件编码/GPU 的 worker。[AOSP main SELinux 策略](https://android.googlesource.com/platform/system/sepolicy/+/refs/heads/main/private/isolated_app_all.te)的 blob 为 `43f1ac656f118688bb780ab434b82d13179911ab`，普通 isolated domain 的 service-manager allowlist 不含 codec 服务，并禁止 GPU 驱动访问；isolated_compute_app 的例外不能擅自当作普通第三方 Service 权限。Android 12 tag 的网页读取失败已披露，不能声称逐设备策略已检查。设备拒绝路径探针准备但未运行。

替代实现为**同签名、另一 APK/普通应用 UID 的 companion**，非宿主同 UID 进程回退。它无网络/存储/相机/麦克风权限，signature permission 加精确宿主 package UID 验证；host broker 是唯一输入授权，输出和只读 lease FD 由宿主逐 task 显式授予，worker 只获自身写目标。公开 codec/GPU 的攻击面仍大于 ordinary isolated domain，extra APK、签名/升级/安装和 Kit 分发方案必须由负责人作产品决定。实际 Binder FD 访问、编码、Surface 和并发 crash 行为仍 NOT_RUN。因此 companion 编译成功不关闭 D1 关键可行性阻断。

两个固定 worker 进程槽只实现每进程一个任务、UID/PID/task/epoch 校验和有界 quarantine；两个进程共享 companion app UID。Android 对同 UID 进程组的 native crash/内存回收是否影响另一任务，已准备并行真实编码实验，未通过前不承诺槽存活。不是 12 槽生产调度器；flock 为协作 crash 恢复，不是撤销恶意持有者 FD 的内核能力。不得冻结生产防 RCE/OOM 保障、硬时间 SLA、最大并发与容量。

仍不得冻结：NAS/SourceDisconnected 真实回收、非 seekable Sink、授权发布与 COMMITTED、宿主/系统失电 durability、共享预览 Surface 生命周期、完整媒体/人脸管线迁移、动态隐私无网络观察、Apple/Windows 实现、正式签名/R8/AAR、权重许可准入和最终 NOTICE、工具漏洞已消除、真实样本跟踪质量与最终保护覆盖。

设备数值与兼容矩阵在 M1/M2/M3 等相应正式阶段验收，跟踪质量在 M5/M6、保护与导出在相应后续门禁验收。D1 不提前完成所有 M1–M8 产品功能，但隔离替代方案的实际可行性和产品选择仍是 D1 待处置关键问题；没有降低 P0。
