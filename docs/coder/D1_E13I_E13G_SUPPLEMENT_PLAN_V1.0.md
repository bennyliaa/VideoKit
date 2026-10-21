# D1 E13I E13G一次补充准确待派方案 V1.0

2026-10-18。协议实现已完成有限离线核验，仍需完整独立复审和负责人准确派单；目前APPROVED_REQUEST_SHA=ABSENT，实际scope/release/once/sourceReview null。不能编辑已冻结常量或绕过脚本直接执行；未来应另出绑定独立review/准确release SHA的来源策略版本并重审，不将本文当许可。

固定端点127.0.0.1:5037、serial HA1Q6WXR，无SDK/no server start/restart/host:kill。可选version请求本批省略（0）；两条设备query各一Socket，同一Socket串行请求transport再shell-v2，最多两Socket。服务白名单及wire格式见准确官方commit 1cf2f017d312f73b3dc53bda85ef2610e35a80e9。

第一实际服务字符串在E13IIdentity.INVENTORY固定：shell,v2,raw:printf边界；dumpsys activity processes（完整global instrumentation/进程资料）；ps -A -w -o UID,PID,PPID,NAME,ARGS（完整global行）；分别准确成功结束标记。无外部script/serial参数。raw stdout与stderr分通道，只有exit0、EOF、原Socket/reader/archive/keeper实际归还、无不允许stderr/截断/落盘失败才解析，其他instrumentation/权限/格式未知或超过64KiB则停止。真实dump太大不能扩大cap或改grep。

第二实际服务必须据第一完整raw及其原归档字节绑定，严格核唯一原instrumentation组件、原runtime SHA 116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef、batch D1-E13A-SOURCE-20261018/class/method，app UID10221与原am UID2000及父/argv。只由这两个当前匹配PID生成固定boot_id、/proc/PID/stat/status/cmdline读取；无示例PID外填，第一未返不第二。第二UID/PPID/argv/正start ticks变化即UNKNOWN，未匹配fixture/codec等仍未知，不凭两切片提供终止资格。

未来wrapper固定argv为：D:/Android/Android Studio/jbr/bin/java.exe、-cp、D:/CodexProjects/VideoKit/docs/coder/d1e13i/artifacts/e13i-host-tools.jar、com.videokit.spike.e4.E13IReadOnly、--g-readonly、准确release文件路径、该文件SHA。实际文件必须是经独立review绑定的typed e13iFixedReadOnlyRelease(kind/scope/serial/review/budget262144/requests2)，SHA固定进新来源策略；本文没有生成可执行release。固定root D:/CodexProjects/VideoKit/docs/tester/D1_E13I_G_SUPPLEMENT_EVIDENCE，only once e13i-g-readonly.once，wrapper id E13I-SUPPLEMENT-ONCE，cap32768；路径/角色/原scope/输入pins都必须一致，不能复用旧UUID或once。

总预算不扩大：已采host/父console8192＋原exec待收取65536＋外层Java摘要32768＋observer facts8192＋batch intent2048＋两query各(wire70656＋metadata2048)=262144B，余额0。wire含TX意图/实际RX握手/帧头/EXIT/FAIL/通道payload，只有一份wire文件，不重复channel文件/echo raw；两个metadata均≤1024、batch intent≤2048。stdout+stderr合65536、帧≤256、service≤2048、FAIL≤256，每query10秒资格。send失败全部意图额度未知不退款，重复摘要计相应预留。异常remote过量同reader固定buffer drain并丢弃标不完整，留存cap不是远端强制截止，过量不能通过/续第二。

原exec42537仍仅未来另派最多一次空输入收取、响应资格≤10秒、文本≤65536B，不循环/非空/Ctrl-C/重建session；本轮0次。若工具不能保证输出额度则不启动记BLOCKED，不用取消或丢返回。空输出/工具返回不是原owner ACK，晚证据另出补充，不回写旧切片。已采host切片19:31:58只作历史，不另偷偷新增CIM预算。

先独立审完整E13I，再由负责人签准确一次补充批次；读取结果仅用于最小收尾方案，所有行政终止仍另审，不能因服务连接成功放行产品/部署/T07。本轮实际5037/设备/SDK/旧handle读取/处置/安装/部署/产品重测均0。旧v17主任务最后PENDING/UNKNOWN、旧ps诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN、E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN三栏独立；本轮不查历史PID、不补ACK、不退款。用户持续测试授权已存在，原任务未决与本阶段范围继续限制执行。D1 NOT_PASSED / M0 NOT_STARTED，T07未派，P0/许可与旧候选不变。
