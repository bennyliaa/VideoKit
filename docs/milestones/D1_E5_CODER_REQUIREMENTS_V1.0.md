# D1 E5 远端就绪与原任务收尾集中开发需求 V1.0

2026-10-17。基于D1_E4A_N2_DEVICE_TEST_REPORT，0PASS/1FAIL/3BLOCKED，E4AN2-F01/P1。真实fixture已合法，正常MP4在BEGIN后约15s远端STARTED未证，0帧/PENDING/E4_REMOTE_PENDING。根因未证，不延长等待或清账求通过。新完整候选d1e5，保E4A/工具/所有旧报告和设备现场。

## 集中修复范围

1. 从N2原源码/原logcat/identity/journal/ledger定位BEGIN接纳→owner启动→能力枚举/四提案→实际codec/Image/mux创建→同步callback ACK→STARTED接收的完整链。检查同步Binder锁/线程/owner执行、STARTED前异常被吞、ready状态/QUERY快照、超时清理接续。明确已证/推断，修真实生产路径，不用Fake或跳编码/删隔离验证获得READY。仍Media3 1.9.3/原受限FFmpeg、同APK codec进程/独立Kit/Flutter边界，不新依赖。
2. 补最小完整阶段诊断：task/epoch/gen/原instance、host/codec PID UID、阶段时间、原codec候选/创建配置开始错误、callback实际在途/ACK、最后原remote Bundle字段有界可审；首错/cleanup/系统reason分列，不泄源凭据。测试摘要需显示实际远端未就绪原因，PENDING不可只通用字符串。若无源码证据足够定位，提交明确一次有限观测计划而非猜修；批内仍先完成可独立自检诊断/资源修复再集中构建。
3. 正常失败/超时后同原任务取消/收尾须主动推进但不提前扣在途，原native调用不返仍PENDING，原source/codec/Image/mux/FD/callback/CONTROL和输出owner真正返回后才ABORTED/S结算保失败产物，不等测试结束系统杀进程代关闭。独立正常/取消用例原60s/12s/30s门不放宽。
4. 一并设计并实现可审的原持久pending合法恢复/查询/abort机制，仅可针对原N2 task86cafdb3-0fc4-447d-920b-b19c884bf494、epoch5131975343750146374/gen1/service775a5ee9-fff3-4340-a03b-97751099c0c4、host24853/codec24873/UID10221/稳定budget730a73e1-50e1-4198-a515-047104f00e31。不是通用reset。原R/marker/WRITING保留直至独立证据证明相关原进程/句柄/在途不再能写、真实lease可排他fence、原FD/owner关闭和持久ABORT/产物身份已核，才能合法结算实际已保留输出消费并解除未用预留。系统finished inst可作死亡证据的一部分，不补造原closeACK或自动按空文件退款。证据不足仍UNKNOWN/BLOCKED，不自动删除marker或换UUID/目录/清数据/重装洗状态。恢复动作须另派tester，coder仅实现/本机自有故障证据和精确准入方案。保原journal/ledger历史可追溯，不回写原FAIL。

## 开发与验证

一次完成以上有关小功能/诊断/收尾/恢复计划，再集中JVM/有意义假故障与offline Android构建，必要修复保原日志，减少编译交接。至少STARTED前能力异常/原callback未返/owner异常/取消迟到/旧代/close未知、完全已证abort和证据不足拒绝/不重复结算/预算不退款关键路径。自有小数据与模型，不能当真实codec/Binder验证。

coder不ADB/设备/真实媒体stat-read-hash/新fault执行/下载。现有两fixture和所有失败产物/旧cache/budget不动。完整E5交付/架构边界/剩余门禁/设备附录、精确源码ZIP/双APK/签名/最终build输入/SBOM差异/外freeze只读核验/有界自检证据一次冻结主动报告。下一计划分原pending合法处置准入→正常MP4→正常AVI→能力→条件cancel整批，禁止含三个quarantine或重跑Binder。不要部分包交tester，D1未通过/M0未启动/全P0/JNI与旧signal FAIL保持。
