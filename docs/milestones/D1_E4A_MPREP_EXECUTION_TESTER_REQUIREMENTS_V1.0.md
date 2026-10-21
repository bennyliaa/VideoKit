# D1 E4A-MPREP 两源整批预置执行要求 V1.0

2026-10-17。独立静态复审支持，现正式授权tester一次整批MP4→条件AVI，按docs/coder/D1_E4A_MPREP_PRELOAD_PLAN_V1.0.md及冻结固定manifest执行，无需再次询问设备或授权媒体样本使用。仅HA1Q6WXR/UID10221/pwd原值/既有E4A安装不重装。

绑定seal96f62df6a902a8b20eab73d97de63ea82321ceffe42c15f983530a245c3b2660、ZIP5c43f62ec601971427ae66bda0fe451c563018c81679c5c07d2f425bb7c01047，执行前核准确源码导入。固定入口preload_once.py --execute --formal-batch D1-E4A-MPREP-TABLET-20261017 --evidence-dir D:/CodexProjects/VideoKit/docs/tester/D1_E4A_MPREP_EVIDENCE 一次。冻结JSON/source不改，全部收据包外新目录。

明确允许读取原授权两真实源及发送精确封装流：sample.mp4 raw349102/SHA720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9，subtitle.avi raw736454656/SHA3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f，准确绝对路径依manifest。仅这两源只读，不NAS/扫描/替代文件。

所有准入/空间/原身份/UID快照/独占tempdir/顺序probe遵守已审计划。MP4每源唯一producer→原计量/BEGIN DECODE END/原owner归还→temp独立n/SHA/前后stamp→同devinode合作式mv-n无覆盖发布→独立final n/SHA/前后stamp/temp消失→ready CREATE_NEW/fsync-close-readback与四本次原记录重验全成立后，正式允许在同一批次继续AVI，不另停等负责人。AVI前再次重验同一MP4真实receipt/owner0及剩余空间。任一失败或UNKNOWN即停后续，不自造摘要/跳过、补传/加时/换路/清理/覆盖或重新进程续作。

空间初始>=785071KiB/AVI>=784731KiB，历史used不删；原归档/26B/T6P/cache/budget保持不访问。新准确tempdir files/e4_mprep_TABLET_20261017_once、两.part及final fixtures依计划，目标已有即拒不猜已准备。

预算host raw1473607516B/编码生成1964810032B不落盘/wire982405016B，device temp+final hash总1473607516B，新媒体736803758B+probe5B，rename不额外复制。raw24576/encoded32768/carry2/工作设计256KiB非RSS；每源producer60/600s从预hash开始、每temp/final hash15/120s、普通metadata15s/共同本机2s，metadata13计划/20硬门、producer各1，日志8MiB/单artifact128KiB、ready元数据读4MiB128次，状态文件4/4KiB。原1GiB encoded界不扩。

长进程通过原exec会话handle观察，不重新启动；每次观察<=60s可继续原handle，重大阻断可报告。UNKNOWN保原解释器/Job/file/args/handle，不退出假归还或二次close。活动超时不推远端归还。成功亦仅TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS。

交docs/tester/D1_E4A_MPREP_EXECUTION_REPORT_V1.0.md两源完整原proof/ready/全部实际字节与时间/旧产物保留/归还或原handle，完整一次主动报告。无手机模拟器/安装/Gradle/Binder/产品正常取消故障/预算标记/自动下一批。D1未通过/M0未启动/P0历史FAIL保持。
