# D1 E2A 真实IO必要适配集中开发需求 V1.0

2026-10-17。负责人全文审阅D1_E2_ADMISSION_REVIEW_REPORT，采纳配置输入及具体E2-C01意见，正式裁定下列工具实验策略。本批批准必要适配/编译及自有非媒体文件验证，不批准test_media字节读取、真实PF/61运行。

## 负责人裁定

- 实验目的仅本机原始字节/协议/OS_DATA_SYNC_ACK probe。五项产品namespace/READY变体继续NOT_RUN_DURABILITY_UNPROVEN，不生成产品OutputToken/业务COMMIT，不声称掉电或真实G崩溃重启。
- G全程delta锚定原进程PF前基线，保持绝对线程16，将提案增量+8明确替换为+12，覆盖规划+10与有限余量；不能HELLO后重置基线。J/R各原实例HELLO后基线，线程64/+32。其余E2阈值批准为有限实验停止条件：句柄G256/+64、J/R512/+128；WS及private G256MiB/+128、J768MiB/+256、R512MiB/+256。不是产品指标或成功保证。现场availablePhysical≥2GiB保持，新鲜检查，不沿用旧快照/自动降门槛。
- 1秒/最多201周期/gap≤2.5秒/返回后0.1秒作为采样停止合同批准，不能宣称绝对峰或中断OS；耗时占原行/180秒，不增线程/RPC。原受管24/媒体6/8槽保持，observer最多1临时信用，满额拒绝。
- 原global.log131072B批准分events104320+metrics26752（头≤1024+201条≤128），实现强制门禁/exact_write，不能容纳则BLOCKED_OBSERVER_LOG_CREDIT，不加日志/峰/时间。
- A05选择固定Windows x64/JBR21.0.10、仅J helper的FFM opened-FD桥首选路线：原RandomAccessFile.getFD对象借用实际FileDescriptor.handle，GetFileInformationByHandle返回opaque身份/长度/mtime及原owner/object/ticket。不另open/dup/close借用HANDLE、不读字节、不改位置/raw不出J不入journal，原h+/OPEN回执带元数据，不增identity RPC。允许该工具编译/运行所必需的JDK21 preview、native-access=ALL-UNNAMED及只java.base/java.io向该工具开放；不全模块开放、不下载。实际字段/ABI/flags/符号先本地验证，失败保持BLOCKED_VERSION_NOT_PROVEN，不回退path/hash/另开文件。此批准仅有限J工具，不解除宿主JNI/P0或产品路线阻断。

## 一次整批实现

新docs/coder/d1e2a保留完整上游身份，集中实现A02只读L/C/Z别名与CREATE_NEW独立输出命名空间/祖先reparse及输入目标物理身份拒绝；A05强引用/close互斥/失败仍计原open已分配并清理；observer实接G PF前至n32前的原实例基线/等待点采样、既有IO pool pending、日志容量/计时/句柄账本，不同worker同步等自身造成死锁。首媒体字节前比较G/J/已分配R实际opened对象，不在未配R分支加reference。原操作内有限身份查询副作用逐项列明；变化影响预算时交具体差异，不藏调用。

验证用自建非媒体文件：opened对象/路径属性分离、flags/字段/符号失败、close竞争/查询失败、安全清理、输入目标别名拒绝；observer实际原实例/缺指标/超阈值/gap/容量不足/close未知等有界验证。真实命名空间/身份检查只可对自有文件执行，test_media仅既授权精确stat允许，不读/复制/修改。fixture累计≤2MiB/日志证据≤4MiB，集中编译/必要修复重编与相关合成回归允许，不频繁小项交接。

保持61分支452/544、101query、IO/事务/32记录/180秒与200秒仅停止等待等原硬界。真实执行入口仍默认关闭且本批不生成可自行解锁授权，后续冻结审查后负责人另派唯一批次/root现场准入。真实JBR桥不支持或资源门槛不满足如实阻断，不能换路径证明或降产品P0。

交D1_E2A_DELIVERY/REAL_IO_ADMISSION/EXECUTION_APPENDIX_V1.0.md及源码ZIP/产物/profile/manifest/只读verify/证据hash，裁定→实现→负例→限制映射。全部完成冻结无在途后主动报告负责人，不自行派测/实验。无Gradle/ADB/设备/下载/M0；JNI/C14/P0/历史FAIL保持，D1未通过。
