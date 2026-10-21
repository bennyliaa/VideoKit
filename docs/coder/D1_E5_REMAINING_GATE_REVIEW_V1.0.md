# D1 E5 剩余门禁 V1.0

2026-10-17。仅本机实现、模型与离线 APK 构建可审；D1 NOT_PASSED、M0 NOT_STARTED、全部P0/JNI/独立Kit正式交付门和旧signal FAIL保持。

| 门禁 | 当前结论 | 下一证据 |
|---|---|---|
| N2 实际启动根因 | UNKNOWN，原日志缺flags/阶段/ACK | 一次正常MP4有限观测，保存E5原字段 |
| 同步callback标志/原ACK准入 | 生产修复+JVM通过 | 真机原UID/PID/flags/ACK/openReturned/startProven |
| 能力四提案/真实六帧 | 未执行 | 原12秒协商/60秒总门内实际6入6出 |
| 原source/native/Image/mux/FD/CONTROL收尾 | 模型与静态审，设备待证 | 原任务实际归还，失败保产物+实际消费S |
| 原N2 pending处置 | 狭义实现存在；设备准入未通过 | 原两个退出记录、原真实排他lease/fence/ABORT/S与所有恢复owner返回 |
| 恢复证据不足/重复/部分持久化 | 本机反例通过 | 设备不足时拒绝，不以人工清账绕过 |
| MP4/AVI 正常 | 原N2为1FAIL，AVI阻断 | 原pending合法处置通过后按顺序实测 |
| capability/条件cancel | 原N2均BLOCKED | 两正常先通过；0源读、无假READY；同首次cancel30秒 |
| CPU/codec隔离威胁 | :e4_codec同UID仅故障边界 | 不宣称恶意RCE/权限隔离；原CPU普通isolated边界保留 |
| native signal/JNI/全P0 | 历史FAIL/未通过 | 本批不重跑不覆盖 |
| 依赖与许可 | E4A lock/native差异0，完整对应源码保留 | 非发布许可或安全清零 |

首个正常MP4仍失败时，记录当前原身份/Bundle/host诊断、codec候选与具体阶段/首错/ACK enter-return计数、source与output实际资源、原journal/R/marker/S与文件身份，立即停止后续正常AVI/能力/cancel，不换预算或延长等待。若仍无足够根因，交一次有限观测结果给负责人再派修复；不得循环重跑或猜测设备已修好。

原N2恢复 QUERY可仅给出metadata/death已核的查询结论，不代表排他lease/关闭/结算已证；必须单独正式ABORT才能推进。记录不足、UID/PID/时间歧义、marker非0、原journal不符、原ledger已变、锁忙、native调用/close未知、fsync失败或中间恢复归档已存在均保持BLOCKED。不得删除归档/marker/输出/ledger、换UUID/目录、清数据、卸载重装洗状态。

下一整批只含原pending处置准入→正常MP4→正常AVI→能力→条件cancel。旧三个quarantine与Binder方法虽保源码历史，本批选择表不含它们。任何将旧ADB exit0、JUnit失败、进程系统结束、0B输出或本机模型通过计为真实产品PASS均无效。
