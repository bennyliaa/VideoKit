# D1 E13I 固定同连接只读协议交付 V1.0

2026-10-18。依据E13H独立复审SHA d74bb01bf02361fd8785bf1f215a793937ad756fb69f02eb7dfe4931256a953c及负责人E13I正式派单，完成固定角色最小离线实现并冻结交独立复审，不自批执行许可。

每条查询在自己的同一原Socket上先固定host:transport:HA1Q6WXR，再固定shell,v2,raw:既定脚本。两条串行、无SDK/no host:kill/no server启动重启/no feature探测/无任意host服务或PID CLI；可选version前置本批不使用（0次、最多两Socket）。新公开入口只接受准确角色及未来固定release pin，APPROVED_REQUEST_SHA仍ABSENT，当前Java/脚本均在Process/网络前拒绝。与H的技术阻断不同，协议角色已离线实现，执行派单仍未签发。

准确官方协议commit 1cf2f017d312f73b3dc53bda85ef2610e35a80e9的10份全文及NOTICE、原始字节SHA/行段摘录封包；实际处理smart-socket长度/status/FAIL、shell-v2五字节头、1/2通道、3号单字节EXIT、一次4号零载荷close-stdin。借用流不独立close，唯一原Socket close/EOF/EXIT/原reader及archive writer实际join分栏。

一轮必要生产host编译成功、31组有限原peer测试通过；之后仅增加一个测试probe编译，生产不重编，对最终生产class执行身份/空输出/父保管/脚本验证。最终JAR共193class：183原F逐字节不变＋10本批实测class逐字节绑定，检查类不混入。JAR 346101B SHA7eeffb64bb98f826de6d98004dd513170921b48c134804e0a4038b3459f1cb78。无APK/Gradle/native构建、新依赖或Maven/native差异，FFmpeg等既有许可门NOT_GRANTED保持。

精确256KiB新预算覆盖wire/握手/帧/错误/元数据/原exec预留和重复console：8192+65536+32768+8192+2048+2×(70656+2048)=262144B，无未分配余额；stdout+stderr合65536B/查询、最多256帧、服务2048B、FAIL256B，10秒只是资格。单一original.wire保留请求意图与接收wire，不另写channel raw副本或echo到console；发送失败的全部意图预留不退款。超额同reader有界留存/明确丢弃，actual未留存remote traffic可越留存上限，不能冒完整raw/预算内查询成功。

本地harness connect失败路径原accept自然超时后stop并实际join；父wait超资格继续强持同Popen及记录句柄，50ms适配探针真实验证原Process随后自然exit0/文件关闭，但资格仍false，不靠raise丢owner、kill或daemon求通过。close永久异常使用准确E4Owned非IO有限fixture验证UNKNOWN不二close，真实Socket链验证close未返/CLOSING及尾通知扣住；未制造一只永久未知活Socket再强行结束以冒有限证据。

完整包/外seal/最终只读回执和四文档交审，十一个旧seal及准确成员不改；两滚动文档仅顶部新增安排、包内封副本。本轮实际5037/设备/SDK/旧handle读取/处置/安装/部署/产品重测均0。旧v17主任务最后PENDING/UNKNOWN、旧ps诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN、E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN三栏独立；本轮不查历史PID、不补ACK、不退款。用户持续测试授权已存在，原任务未决与本阶段范围继续限制执行。D1 NOT_PASSED / M0 NOT_STARTED，T07未派，P0/许可与旧候选不变。
