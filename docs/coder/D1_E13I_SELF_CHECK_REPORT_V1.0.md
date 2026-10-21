# D1 E13I 有限离线自检 V1.0

2026-10-18。host-001一次生产javac exit0，编本批4生产源与最初ICheck/IFixtures，对准确F base JAR183 class；31个独立有限本地peer模式自然exit0，无生产源码修正或重编。supplement-002仅额外测试probe javac一次，对同host-001生产字节，不能把它隐写成所有javac只有一次。最终JAR193成员，全部新生产class保留实测原字节逐个核对；无检查/fixture类混入。

31模式：OK/SPLIT/INTERLEAVED/LIMIT/BAD_STATUS/FAIL/LONG_FAIL/SHELL_FAIL/TRUNC_HEADER/TRUNC_PAYLOAD/BAD_ID/LONG_FRAME/BAD_EXIT_LENGTH/FRAME_OVER/RAW_OVER/WIRE_OVER/EOF_NO_EXIT/EXIT_NO_EOF/DOUBLE_EXIT/AFTER_EXIT/STDERR/EXIT_NONZERO/CLOSE_PENDING/TAIL_PENDING/WRITE_PENDING/WRITE_FAIL/CONNECT_FAIL/CLOSE_UNKNOWN_CONTRACT/CHAIN_OK/CHAIN_BAD_SCOPE/CHAIN_PENDING。

实际生产解析器/Socket owner处理碎片、通道合上限、帧整数/长度/ID/过额、EXIT/EOF顺序/重复、非零/错误状态；pending在100ms资格先失败，原Socket/reader/writer keeper继续强持，释放同有限peer/hook后实际join/close一返；尾通知未返不得提前完成。实际写失败为Socket＋writer组合，record失败后不继续发shell，fixture原等待以自身1500ms读超时自然返回并close，原reader才获EOF；不能把此fixture错误写成真实设备行为。CONNECT_FAIL针对本地非法目标端口0产生实际connect失败；原fixture未接收client，100ms accept自然返回后stop/实际join/close，没有在join后才词法close的死等窗口。

CHAIN_OK两条同Socket握手分别完成，第一原reader/keeper实际结束后第二严格派生，原once FileChannel close/force返回，最终262144预留准确；CHAIN_BAD_SCOPE只一条、CHAIN_PENDING保同Batch及一条Op，最终自然归还仍不恢复资格，未自动第二。没有生产真实派单。

supplement-002额外测试同一生产字节的15身份/完整性/UID/父/组件/start ticks拒绝门、外部host/PID角色及未派执行拒绝；空stdout的真实Socket只有EXIT0+EOF+原物理返才通过协议层。非IO E4Owned open失败与永久close抛错UNKNOWN不能二分配/二close；这不是永久未知活Socket动态归还证明。实际Socket close未返/CLOSING已在链中扣住验证；永久异常分支静态保持非daemon原keeper，未造新永久未知网络对象后用kill/daemon退出冒通过。

父保管补充直接提取并执行实际check_host.py的run函数AST，仅把本地fixture wait适配为50ms：原pending文件记录同PID，父继续持有同Popen/输出句柄，再同原p.wait得到自然exit0及文件close；qualificationPreserved=false保持，函数断言失败由probe识别为预期，不改原资格。不是镜像父门、不是取消future，parentCustodyOutstanding=0。主套件20秒父等待未超资格，补充显式触发该分支，无20秒长跑。

PowerShell完整AST与准确角色未派/错产品角色拒绝实际回执，原observer owner主体与F实际字节比较相同。所有本地peer为非daemon、有限accept/read/释放路径且真实join，不靠daemon或kill结束。测试只连接自己临时端口，经工具明确本地网络权限，不访问真实5037。首H VERSION_OK缺ACK仍原样保留，本轮没有新未知地方probe。

官方协议源码固定commit完整下载，10份字节pin/NOTICE与片段可核；旧文档OVERVIEW.TXT在该commit HTTP NOT_FOUND留下0B，明确排除协议权威，没将下载失败说成成功。实际Android API31格式/权限/全局输出是否≤64KiB/服务实现均NOT_RUN；真实完整AM输出超限只拒绝不grep/追加。本轮实际5037/设备/SDK/旧handle读取/处置/安装/部署/产品重测均0。旧v17主任务最后PENDING/UNKNOWN、旧ps诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN、E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN三栏独立；本轮不查历史PID、不补ACK、不退款。用户持续测试授权已存在，原任务未决与本阶段范围继续限制执行。D1 NOT_PASSED / M0 NOT_STARTED，T07未派，P0/许可与旧候选不变。
