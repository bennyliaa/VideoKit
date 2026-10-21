# D1 E13I 固定同连接只读协议完整冻结交付 V1.0

2026-10-18；coder交VideoKit项目助理。正式E13I coder/tester需求已保存，依据E13H独立复审SHA256 `d74bb01bf02361fd8785bf1f215a793937ad756fb69f02eb7dfe4931256a953c`之H-R01–05/§6完成最小集中离线实现。结论：**READY_FOR_INDEPENDENT_E13I_REVIEW / NO_EXECUTION_DISPATCH**。新固定协议角色已实现并有限验证，生产执行仍未派，当前审批pin ABSENT；没有实际5037、SDK、设备、旧handle/历史PID查询或处置。

## 1. 冻结身份与实际只读结果

- ZIP：`D:/CodexProjects/VideoKit/docs/coder/D1-20261018-E13I-source.zip`，1120921 B，SHA256 `0cbbf6e45bb87bdc998fbb45e0b97305be09f12610f6e5341ce7ac2eb130c2cf`。
- 外seal：`D:/CodexProjects/VideoKit/docs/coder/d1e13i/evidence/e13i-freeze.json`，87451 B，SHA256 `d18b61928227bff9fb46848b5ae7d6c40a869c7a1976b23f5a72467d05a7ddf6`。
- 准确414 ZIP成员、415条唯一冻结记录（含ZIP）；默认verify、显式准确seal SHA verify、help、pack-help实际全部exit0，416份前后文件字节一致，writes0；没有校验时编译、测试、联网或SDK动作。
- 最终JAR：`D:/CodexProjects/VideoKit/docs/coder/d1e13i/artifacts/e13i-host-tools.jar`，346101 B，SHA256 `7eeffb64bb98f826de6d98004dd513170921b48c134804e0a4038b3459f1cb78`，193生产class。
- 183个既审E13F class逐字节复用、不重编；10个新增生产class全部与host-001实际测试字节逐个一致，原class另存。额外检查/fixture class不进JAR。来源/差异/旧原source pins和本批源码封包。
- 十一组旧seal及所有准确成员保持：E11/E11R1/E12/E13/E13A/B/C/D/E/F/H。旧F/H以及原任务资料不改，不把重叠manifest行相加冒唯一文件数。
- 最终回执：`D:/CodexProjects/VideoKit/docs/coder/D1_E13I_FINAL_READONLY_VERIFICATION_V1.0.json`，在ZIP外避免自引用；本报告与通知回执也在ZIP外。

## 2. 固定服务与准确官方协议来源

生产角色不启动adb.exe，**每条查询各一原Socket，固定127.0.0.1:5037，在同一Socket内先`host:transport:HA1Q6WXR`再` shell,v2,raw:<固定脚本>`（实际service无前导空格）**。第一完整合格并实际join原资源后，才严格派生第二。最多两条查询Socket，无version前置（本批选择0次）、feature探测、host:kill、server启动/重启、SDK fallback、其他serial、任意shell/PID入口。不是通用ADB客户端，不保证外部server永不变化；连接变化/不兼容成为失败或UNKNOWN，不自动重连。

准确官方源码commit `1cf2f017d312f73b3dc53bda85ef2610e35a80e9`，完整原始字节及SHA固定在`d1e13i/reference/protocol/`和`evidence/protocol-source-manifest.json`：adb_io.cpp、adb.h、sockets.cpp、shell_protocol.h、shell_service_protocol.cpp、daemon/services.cpp、daemon/shell_service.cpp、docs/dev/services.md、docs/dev/protocol.md及NOTICE共10份。另封原commit metadata与精确行段摘录SHA，Apache NOTICE保留。服务长度/status/FAIL、transport路由、raw/v2常量、五字节帧头/通道ID及单字节EXIT均有准确源码依据。所选Android arm64为LE；没有把底层ADB aproto的24字节头当作smart-socket/shell协议。

可选OVERVIEW.TXT在该commit HTTP NOT_FOUND，0B文件明确只作失败历史，不列协议权威；其余10份完整下载有真实pin。本轮公开官方文档读取不含5037/设备操作，也不建立SDK二进制源码映射；新实现不依赖SDK执行或版本不匹配处理路径。

## 3. 原owner与严格帧处理

Batch在once/force/close前强登记并启动非daemon原keeper；原FileChannel完成写/force/唯一close后才能首连。每Op在allocate/connect/write/read前强持原Socket、唯一reader、borrowed streams、archive writer/文件和非daemon keeper。流不自行close，只有E4Owned Socket唯一close，解析失败且可能仍在运行时由同一reader先自然drain，不强关/取消/替代reader。

服务4 ASCII hex长度/status只OKAY/FAIL，FAIL≤256B。shell header固定ID+LE uint32，严格只收stdout1/stderr2/EXIT3；EXIT长度必须1，发送控制仅一次close-stdin4零载荷。碎片/合并按字节读全，不按read次数当帧；先校验整数/帧/累计长度再用4096B块读，不按未审长度分配。单帧及stdout+stderr合计≤65536B、最多256帧、service≤2048B。截断、未知ID、重复/错误EXIT、EXIT后数据、EOF无EXIT都失败；stderr非空或exit非0也失败。

EXIT/EOF、原read返回、Socket唯一close、文件close、writer/reader/keeper真实结束分栏。keeper join同原reader，writer外实际终止/join并核全部原文件返后才标物理完成；caller再join keeper，才能资格成功或派第二。writer内flag/facts快照不自证自身线程/close。10秒仅资格；超时立即封依赖、保同原对象，晚返不恢复资格，不自动第二。永久close/文件UNKNOWN原keeper继续非daemon持有，不二close。

E13IArchive仅把既审archive模式最小适配Socket wire；不伪造Process PID/进程exit。E13IIdentity保留既审固定G身份门/脚本，去除SDK工厂/版本原型；其余183旧F class准确不变，无新通用生命周期框架。

## 4. 两命令及精确总账

第一完整固定脚本为dumpsys activity processes＋ps -A -w -o UID,PID,PPID,NAME,ARGS，准确begin/end/exit边界；不grep、不把截断当完整。实际全量过大、权限/格式未知或有其他instrumentation立即拒绝，不追加探针。

第二只能由第一准确raw推导：唯一原instrumentation组件、mFinished=false、原runtime SHA116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef、batch D1-E13A-SOURCE-20261018/class/method；mRunningProcesses的app/u0a221与全局ps UID10221/name/args/父相符；原am UID2000/准确完整scope argv/父相符。只选这两个角色数字PID，固定读取boot_id与stat/status/cmdline，核PID/四UID/PPID/完整argv/正start ticks。fixture/codec未匹配仍UNKNOWN，第二切片不证明两次间无复用或提供终止许可，不能外填旧14763/14765/14779或fixture示例PID。

新总账严格262144B，无余额：

| 项目 | 预留B |
| --- | ---: |
| G已采host及父console历史切片 | 8192 |
| 原exec未来一次收取 | 65536 |
| 外层Java摘要stdout/stderr | 32768 |
| observer facts console | 8192 |
| Batch once/intent元数据 | 2048 |
| 两query双向wire（各70656） | 141312 |
| 两query元数据（各2×1024） | 4096 |
| 合计 | 262144 |

每query的70656B涵盖TX服务/控制意图、实际RX握手/status/FAIL/header/两通道payload/EXIT。只留一份original.wire，不再落channel raw副本或echo raw到console；重复摘要已在相应预留中。意图在write前全额预留，部分/未知发送不退款；writesEntered/Returned与incomingWire/intendedTx/chargedWire分栏。**rawBytes为已校验帧长度预扣的payload额度，截断时不能把它冒实际完整收到字节；retainedWire也是留存尝试上界，archive offered/written/原文件长度另核。** 不以这些计数字段代替完整帧/EOF/归还证明。

wire/帧/归档超限明确失败与不完整，同一reader用固定buffer自然drain并丢弃越限部分，保全部预留，不无限留存或强关。**远端实际未留存流量可能超过留存cap**，不能冒“所有实际流量始终预算内”或把超额查询判成功/续第二。未知原额度不退款，旧余额不继承。

## 5. 实际有限测试与harness修复

`evidence/host-001`：一次必要生产javac exit0，四个生产源＋最初ICheck/IFixtures对既审F base编译。31独立有限peer模式全部自然exit0：

OK、SPLIT、INTERLEAVED、LIMIT、BAD_STATUS、FAIL、LONG_FAIL、SHELL_FAIL、TRUNC_HEADER、TRUNC_PAYLOAD、BAD_ID、LONG_FRAME、BAD_EXIT_LENGTH、FRAME_OVER、RAW_OVER、WIRE_OVER、EOF_NO_EXIT、EXIT_NO_EOF、DOUBLE_EXIT、AFTER_EXIT、STDERR、EXIT_NONZERO、CLOSE_PENDING、TAIL_PENDING、WRITE_PENDING、WRITE_FAIL、CONNECT_FAIL、CLOSE_UNKNOWN_CONTRACT、CHAIN_OK、CHAIN_BAD_SCOPE、CHAIN_PENDING。

全部运行真实本批生产parser/Socket owner/归档（明确标出的非IO契约测试除外），只用自身临时127.0.0.1 peer。100ms资格失败后扣住原EOF/close/writer/tail，仍保同原对象；释放同有限fixture后实际join/唯一close返回，首次资格仍失败。WRITE_FAIL是实际Socket＋archive组合，不只镜像门；落盘失败后不继续shell，测试peer自身1500ms读资格自然失败/关闭后原reader才获EOF，记录该fixture错误，不冒设备行为。

CONNECT_FAIL本地目标端口0产生真实connect失败，原未被接收的peer以100ms accept自然超时＋stop有限结束，真实join/close，修复H先无限join、后词法close永远不可达的缺口。Peer/keeper均非daemon，不靠kill/daemon退出。CHAIN_OK第一原reader/keeper结束后才第二，准确once FileChannel归还、262144预留；错scope和首pending都只有一条，未自动第二。

`evidence/supplement-002`：只额外编译测试probe一次，对同一host-001生产字节测试15个身份/完整性/UID/父/组件/start ticks门及额外角色未派拒绝、真实空stdout Socket（仅EXIT0+EOF+原物理返通过协议层）、准确E4Owned非IO open UNKNOWN不二分配。另有脚本完整AST、正确未派/错角色拒绝、原observer owner主体与F**实际字节**比较通过。

本批一轮生产编译后没有生产修正/重编；额外probe javac单列，不隐写成所有javac总共一次。检查/fixture class原字节保存、生产JAR严格排除。

父wait缺口用实际check_host.py run函数AST直接触发：只将有限fixture wait适配为50ms，pending时仍强持同Popen/记录文件，随后同原p.wait自然exit0/记录文件close；qualificationPreserved=false保留，函数拒绝资格由probe识别为预期，不把晚返改成原资格成功。没有raise遗失原引用或取消future，parentCustodyOutstanding=0；主套件20秒父资格未超，补充直接验证该分支，不跑长20秒全套。

永久Socket close抛错会留永久未知活owner，不能为有限测试造这种对象再杀掉冒成功。因此真实Socket链验证close在途/CLOSING未知、释放后真实返；准确E4Owned非IO有限fixture验证抛错UNKNOWN/二close拒绝，生产永久异常非daemon keeper分支静态保留。**不是永久未知活Socket动态归还证明**，此证据范围已在自检/契约单列。

## 6. 发布门、四文档与下一准确派单

生产Java与PowerShell审批pin仍ABSENT，正确角色实际在网络/Process前拒绝，actualScope/release/once/sourceReview均null。协议实现不再因SDK隐式kill/start技术路径阻断，但执行许可仍未签发。未来不得编辑现冻结常量绕行；须另出绑定独立review/准确typed release SHA的新来源策略版本及精确新JAR，再按负责人派单执行。

四文档在`D:/CodexProjects/VideoKit/docs/coder/`且入ZIP：

- `D1_E13I_FIXED_SOCKET_DELIVERY_V1.0.md`
- `D1_E13I_IMPLEMENTATION_CONTRACT_V1.0.md`
- `D1_E13I_SELF_CHECK_REPORT_V1.0.md`
- `D1_E13I_E13G_SUPPLEMENT_PLAN_V1.0.md`

正式coder/tester需求在`D:/CodexProjects/VideoKit/docs/milestones/D1_E13I_CODER_REQUIREMENTS_V1.0.md`与`D1_E13I_TESTER_REQUIREMENTS_V1.0.md`。两滚动协调文档顶部已同步E13I，历史段落保留，包内封副本。

准确补充草案固定Java/JAR/角色七项argv、typed e13iFixedReadOnlyRelease(scope/serial/review/budget262144/requests2)、准确根D:/CodexProjects/VideoKit/docs/tester/D1_E13I_G_SUPPLEMENT_EVIDENCE、一次e13i-g-readonly.once、wrapper id E13I-SUPPLEMENT-ONCE；没有签发实际release。第一fixed脚本在源中准确固定，第二必须来自第一完整原证据，不用本地fixture PID填真实命令。

原exec42537仍未来另派最多一次空输入收取、≤10秒响应资格/≤65536B文本，不循环、不Ctrl-C/非空输入、不重建session；本轮0次。工具若不能保证文本额度先BLOCKED，空输出/工具返回不是原Java/reader/pipe/Android ACK，晚证据另出补充。不偷偷新增CIM；已采19:31:58 host只作历史切片。所有外部终止、部署/T07仍另审。

无APK/Gradle/native构建、新runtime依赖/Maven/native差异；沿用F app19/fixture3，未安装，许可NOT_GRANTED保持。旧v17主PENDING、旧ps诊断LOST、新H本地30384 RETURN_UNPROVEN三栏独立，本轮只归档旧材料，不查历史PID、不补ACK/退款；H本地UNKNOWN不因本批新测试成功而抵消。实际旧根因仍NOT_UNIQUELY_DETERMINED，D1 NOT_PASSED / M0 NOT_STARTED，P0/历史FAIL/UNKNOWN保持。用户持续设备授权已有，限制来自准确范围与原任务未决。

请正式整包交tester独立离线复审；当前保持完整冻结，不实际连接5037/设备/旧handle，等待集中结果与负责人下一准确派单。
