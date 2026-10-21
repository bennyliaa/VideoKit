# D1 E5A 恢复完成与失败终局集中修复需求 V1.0

2026-10-17。E5复审REQUEST_CHANGES，采纳E5-F01/P1与F02/P1，详D1_E5_ARCHITECTURE_REVIEW_REPORT。新d1e5a完整候选，旧E5/E4A/报告/设备现场只读；本批不先部署或QUERY，避免无必要安装交接。

F01：修完成内容已可见但force/实际close/最终目录sync或目录FDclose未证的跨host窗口，不能仅completion字节+archive存在判恢复完。原ACTIVE/poison进程内状态不能保护新host。设计明确持久阻断和完成准入线性化点，任何晚期失败重建host不得追加新R。不能递归增加最后自证文件再遗漏其close；选择可实现协议/独立最终观察或明确需要后续确认的状态，但不能假造原closeACK/绝对掉电保证。若需独立观察证明原恢复进程实际死亡/相关FD不再存在与当前持久状态一致，则按明确身份/证据核，不能按任意重启洗许可；原未证sync不回填成功。保原before/R/S/产物和唯一实际消费，不删marker/换UUID/清数据。实现与设备计划一并解释边界。

补真正晚期反例：completion完整内容已写而force抛错、close异常/未返回、最后dirsync/dirFDclose异常或未返；原资源强引用和重建host reserve拒绝。正常全返可准入、部分完成不可自动续写/重复S。直接生产路径和自有文件，不镜像布尔测试。旧早期sync反例不等覆盖。

F02：正常失败Future/仪器结束必须绑定原owner实际cleanup归还或原首次cancel30s绝对截止；初轮后同Session迟到仍在原窗口内，仪器不能先assert结束杀原host。保原首错和FAIL，不将cleanup完成改READY；原native/CONTROL/callback未返不提前扣数。所有正常/negative/cancel/await异常路径统一检查，禁止只改positive等待另一条提前终结。原产品60s/协商12s/STARTED15s/首次取消30s不扩，不因每轮query/新await重新给时限。

补有界生产生命周期证据：初轮PENDING→原窗口内迟到实际返回→ABORTED/结算完成后才允许测试结束，以及原绝对截止仍UNKNOWN→保留/诊断明确终结而不伪资源归还。覆盖同owner continuation实际排队/唯一finish，不仅CallbackGate模型。Android真实行为仍后测，不以JVM外推。

一次完成两修复及集中本机关键证据后offline构建双APK，必要repair日志保留；保持flags/STARTED ACK/阶段trace/六真实帧/isolated EOF/源不变和既定框架许可。四E5A文档/完整源ZIP/APK签名/最终build输入/SBOM差异/外seal只读核验一次冻结主动报告。无ADB/设备/真实媒体/新fault/下载/Gradle并发。实际部署QUERY→独立审阅→另派原ABORT→独立结算→正常四方法顺序不变，D1未通过/M0未启动/P0历史FAIL保留。
