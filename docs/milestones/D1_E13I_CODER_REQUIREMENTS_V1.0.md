# D1 E13I 固定同连接只读协议实现需求 V1.0

2026-10-18；负责人正式派单。依据E13H复审报告SHA d74bb01bf02361fd8785bf1f215a793937ad756fb69f02eb7dfe4931256a953c，先读§5 H-R01–05及§6。仅集中离线实现、有限peer自检和必要一次host编译，保持E13H及所有历史冻结。无真实5037/SDK/设备/旧handle/处置执行，不编APK/Gradle/native，不作小功能交接。

允许替代SDK执行方向：仅既有127.0.0.1:5037、固定HA1Q6WXR的transport及两条既定只读shell-v2命令。每条同一原socket完成transport+该shell，不启动SDK、不发送host:kill/server start/restart，不作通用ADB客户端，不开放任意host服务/serial/shell/PID。准确官方协议commit/文件字节pin和服务白名单先保存。

先登记原owner/intent/pins/总预算，唯一reader、E4Owned与有界归档，Socket借用流关闭责任唯一；原线程外实际join后才能认定归还。严格status/FAIL/header/ID/长度/EXIT/EOF分栏；stdout+stderr合64KiB，规定帧数/wire上限/10秒资格。未返保同原对象，错误/超限不重试、不强关在途shell，不以EXIT或EOF伪造另一事实。第一完整合格且原资源真实归还才严格派生第二，不用示例PID。

总256KiB不能增加。重新核246784B草案+15360B余量，包含握手/帧/错误/归档副本/重复输出及未知预留；超则减少输出或明确拒绝，不能漏wire账。可不使用可选version前置；若使用，仍固定一次host:version≤1KiB/2秒，只信息前置、不当server稳定证明。

有限本地peer覆盖真实生产解析/owner链：碎片/交错、截断/错ID/过长/超额/重复EXIT/EXIT无EOF/EOF无EXIT/迟到/close未知、记录失败及派生门。修本地harness connect失败peer.accept无限join与父wait超资格丢原Process两个缺口，fixture有限失败释放并真实join，父明确强持交接，不以kill求通过，不将keeper改daemon冒归还。

E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN仅独立归档，不查历史PID、不补ACK；旧v17主PENDING、旧诊断LOST和该本地UNKNOWN三栏独立。最终JAR/脚本/来源/diff/有限原始证据/外seal/ZIP及实际只读verify完整冻结交审；另列E13G一次补充准确命令/预算草案，不实际执行。同步两份滚动文档顶部，主动完整报告。D1未过/M0未启、T07未派、用户持续授权和P0/许可门保持。
