# D1 E13H 最小只读入口整包独立离线复审 V1.0

2026-10-18；tester。依据正式E13H需求、四文档及负责人补充。

**结论：PASS_PREPARE_ONLY / EXECUTION_BLOCKED。** 接受本包作为固定角色原型、生产硬拒绝及待审替代方案交付；不是可执行的E13G入口。没有设备、5037、旧handle、SDK执行、处置、部署、候选编译或长套件。本轮仅本地冻结资料/源码/制品字节核验，未运行候选或新probe。实际SDK协议映射和预检后重连竞态仍UNPROVEN；原v17 PENDING、旧诊断LOST及本批新本地probe UNKNOWN分别保留。D1 NOT_PASSED / M0 NOT_STARTED。

## 1. 整包与最终class来源

| 对象 | 独立核验结果 |
| --- | --- |
| 外seal | `befdcfcc5c04722cb138f845a27fe6d434d63fd204c211b39028914cdce2fc9e` |
| ZIP | `docs/coder/D1-20261018-E13H-source.zip`，928716B，SHA256 `38ba1472783cf540cea451ea811af83ea1dfd8e9d60f1a4f08c3aa4bcf35af76`；181条唯一记录/180个准确成员，集合/字节/SHA/CRC通过 |
| host JAR | 334906B，SHA256 `b610227fb564d8fb0d0085dcd12dd398e042ead38b28d36d9d9a3bc1babced35`；准确188成员 |
| 来源 | 原E13F全部183 class逐字节沿用；5新增生产class与host-001保存的实测class逐字节一致，各自source pin核实；HCheck替身class不进入生产JAR |
| 旧冻结 | 十组旧manifest行375/65/46/367/270/118/141/9/1001/1179逐条保持，不加总冒唯一文件数 |
| 独立审计 | tester自有8506项检查通过，读取3762份唯一冻结文件；不调用候选verify/selfcheck作为独立结果 |

单次host-001 javac原exit0，只编新增生产源和HCheck，对准确E13F base JAR编译；旧源未重编，无APK/Gradle/native构建，无新增Maven/native依赖。14份原命令回执按预期退出核验，其中包含该一次编译、初期四功能组和后续九组版本/描述/拒绝/脚本解析记录；首次VERSION_OK未决不被纳入成功回执。final-002使用同一编译字节，无第二次编译。

本包没有新APK或新签名产物。沿用E13F的19/3 APK身份及签名结论，原F seal和全部成员本轮重核不变，不冒称对未变化APK重新执行签名工具。SDK仅静态读取准确文件pin：8273560B，SHA256 `b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f`，执行0。本轮也不访问引用的网站；官方链接及coder web读取陈述不充准确SDK编译映射或完整下载源码证明。

## 2. 硬拒绝门与原型范围

`E13GReadOnly.java:59–63`仅describe或正确--g-readonly角色；正确角色仍因常量DIRECT_ADB_NO_RESTART_PROVEN=false直接抛错，没有创建Chain/Version/supervisor、Process或Socket的分支。describe只输出常量/固定模板，不作网络/SDK调用。final-002原public-reject回执的准确拒绝原因与最终5 class来源一致。

`observe_g_only.ps1`固定Java/JAR/角色、唯一id、原runtime SHA、准确证据根与32768B host cap；准确角色同样在原context分配前throw。其throw之前仅读取需求/pins，不是新的Process或网络创建。错误exe、旧case/deploy角色拒绝。原Process/readers/文件归档/异常custody主体与既审E13F脚本**实际字节**相同，脚本完整AST及三拒绝组回执可核；未删门绕行。

因此接受硬拒绝本身的安全边界；禁止通过删除throw或把布尔常量改true来“启用”本包。未来同连接socket方向是另一受审实现，当前没有实现或执行授权。

| 原型 | 已审范围 | 资格及限制 |
| --- | --- | --- |
| 固定第一argv | 固定SDK路径、127.0.0.1:5037、HA1Q6WXR、shell -T；完整dumpsys activity processes及ps -A -w -o UID,PID,PPID,NAME,ARGS，准确begin/end/exit | 64KiB/10秒；全量超限、格式/权限未知、其他instrumentation即拒绝，不能grep/截断冒完整 |
| 严格推导 | 唯一原active组件/mFinished=false/准确scope batch class method；mRunningProcesses的app与全局ps的UID10221/name/args/parent相符；原am客户端UID2000/完整argv/父UID相符 | 只选app和am两个角色；未匹配fixture/codec仍UNKNOWN，不因未选择推不存在 |
| 第二argv | 正整数PID只能从第一完整证据产生，固定boot_id和两PID的stat/status/cmdline | 核正start ticks、PPID、四UID及完整argv；是第二切片，不证明两次间无复用或具备终止资格 |
| 包内Chain | 同supervisor先retainAuthority，原Process/唯一reader/archive/actual thread join；第一未返或失败/解析不合格不启动第二 | 测试Runtime只替有限本机JVM，公开CLI没有放行路径，不是设备执行证据 |
| 版本Socket原型 | 固定host:version，默认5037；E4Owned Socket/原reader/non-daemon keeper先登记，caller资格失败不关闭在途调用 | 1KiB/2秒候选；测试只用临时本机端口；0029仅候选协议值，非准确SDK证明 |

stdout/stderr/exit与原Process归还在现有Process/archive类中有接线，保持超资格不kill、不二reader/二close。WRITE_FAILURE是直接原archive IO故障，不是完整公开入口的磁盘故障组合；本轮不扩大其证据范围。真实API31格式、/proc权限、UID/kernel/Looper/Binder及设备只读均NOT_RUN。

## 3. 新本地VERSION_OK UNKNOWN独立评估

新增记录标识建议：**E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN**。它属于host-001 HCheck VERSION_OK临时loopback测试，不能混同旧主case或旧ps诊断。

冻结事实：pending.json记pid30384/killed=false/originalPending=true；check_host.py在Popen.wait(15s) TimeoutExpired后保存pending并向外抛，不保存原exit回执或持续交接原Popen句柄。该组stdout/stderr在封存时均0B，不能据此推整个执行期没输出或补exit=0。后续三个新VERSION测试自然exit0只证明新测试，不修复首例。

“一次jcmd Thread.print为no such process”仅见交接文档及local-probe-environment-history.json的陈述；冻结的version-env-check目录没有该次独立原stdout/stderr/exit。无论该陈述是否准确，都不是原Process/reader/close ACK，也不能作为当前无存活对象证明。本轮没有重新jcmd、CIM、PID或端口查询来补它。

可能涉及的本地对象包括：原测试JVM/原启动者Process与输出文件句柄、临时ServerSocket、peer线程、Version原Socket/reader/keeper及其OWNERS引用。若原JVM已退出，相关原内存对象不可恢复；若仍存活，可能仍由自身线程/静态引用持有。当前两种情况均未证，不根据历史PID30384执行任何操作。

静态发现一个具体条件性harness窗口：`HCheck.java:18`先起非daemon peer阻塞accept；若Version连接在peer接受前失败，finally仍依次无限peer.join/worker.join/keeper.join，ServerSocket的词法close在这些join之后，可能永远到不了；`check_host.py:17`的15秒只停止父等待，不结束或可靠交接原对象。这能构造本地挂起路径，但**不是本次已唯一定位根因**。环境权限后同字节成功也不能排除其他原因。

最小当前记录已单独保存：原模式/完整argv与source/class digest、pid30384仅历史提示、15秒等待、无原exit/reader ACK、封存的两个0B文件、创建时间/临时端口/当前存活UNKNOWN，以及jcmd仅二手陈述的来源。保持原资格失败、未知不退款；不创建空stderr冒新收取、不合成原返回。

后续实现前要求收紧本地测试harness：自己临时listener/peer也必须先登记并在连接失败路径能有限、实际地结束测试fixture，逐个保留原join/close结果；平台调用UNKNOWN继续原保管，父wait超资格须明确交接原Process/记录者，不单靠raise丢局部引用。不能用把peer/keeper改daemon或全局kill让测试exit0充资源归还。现UNKNOWN若需进一步核查/行政隔离，须负责人另派准确范围；本轮只登记，不查询、不处置。

## 4. 现有server预检不能开启SDK路径

官方源码线索中的ADB_SERVER_VERSION=41、0029并不等于当前SDK二进制的准确构建映射；来源JSON明确UNPROVEN。一次host:version信息预检与后续SDK新连接之间仍可发生server替换，不能据预检成功保证SDK不进入版本不匹配处理路径。固定-H也不是充分证明。当前确实硬拒绝，未用文字风险说明替代实码门。

执行准入继续BLOCKED；原型中的TOTAL常量和预算文档只是准备，没有可执行聚合账本或原intent派单，不能称本包已运行或已实现整个256KiB执行预算。下面替代方向可有条件进入最小实现设计，不能据此移除拒绝门。

## 5. 同原socket固定transport＋shell-v2：集中实施条件

**设计方向有条件接受；实现/设备执行均未批准。** 目标是每条固定只读命令在其一条原socket上完成准确serial transport和shell-v2，完全不启动adb.exe，从源头避开SDK客户端自动kill/start路径。不是保证外部server永不更换；外部更换/连接失败必须成为UNKNOWN或拒绝，不重连重试。

### H-R01 准确协议资料与固定服务白名单

实现前保存准确官方smart-socket及shell-v2协议源码版本/文件/段落字节与SHA，至少覆盖服务长度/status/FAIL、固定serial transport选择、shell-v2 header/ID/长度端序/EXIT载荷。当前交付没有完整对应源码pin，不能凭0029或本报告常识补协议事实。无需为新路径伪造SDK源码对应；SDK继续只作历史pin、执行0。

只允许固定127.0.0.1:5037。允许的请求序列在源码写死：最多一次host:version信息请求；每个查询socket固定选择HA1Q6WXR transport，随后仅固定shell-v2服务和两个既定脚本。拒host:kill、start-server、host任意服务/任意serial、exec/pty/fallback和外部shell/PID参数。无feature探测命令、无第三条设备查询、无自动SDK退路。准确service字符串/标志依冻结协议定稿并审，不先发试探包。

version连接若使用，只是信息前置，不把其server身份当后两连接的稳定证明；不能承诺同一个version socket反复执行所有服务。**同连接**指每一条设备查询的transport选择与该条shell-v2使用同一原socket，最多两条设备命令各一socket；不得在transport成功后换连接/改serial。

### H-R02 单一原owner、先登记及真实归还

复用既有E4Owned/归档与custody模型，新增最小Socket角色：在allocate/connect/write/read前登记原批次、operation、serial、命令模板、原socket/reader/writer/keeper；准确intent/pins/总预算先落盘，关键记录未可用不连server。每原socket只有一个reader，不能为解析或补日志另起reader。

Socket及借用InputStream/OutputStream的关闭责任须唯一、明确，不能流close隐式关socket后又把第二次close称原ACK。协议EXIT、TCP EOF、原read返回、原socket唯一close、archive文件返及各原线程join分栏；不能用线程内flag或facts文件自证自身close。未知原对象由强keeper保留，caller抛错或10秒响应资格不能丢owner。

两条命令串行，第一原socket/reader/archive实际归还且证据完整合格后，才从第一完整raw推导第二准确PID脚本。不得用第二socket成功替第一ACK或扩大到未确认fixture/codec角色。原主任务及两个历史UNKNOWN均不被这些新只读对象接管。

### H-R03 严格服务与shell-v2帧解析

smartsocket请求长度/status/FAIL按冻结格式逐字节读全，拒非ASCII长度、溢出、截断、不支持或额外服务；FAIL原因也有固定上限，不按FAIL改跑其他命令。transport确认只证明所选路由，不替设备启动身份。

shell-v2 header、ID、长度端序和EXIT载荷严格依准确协议，固定小buffer逐块读，先检查整数/单帧/累计长度再分配；禁止按未审长度申请大数组。分离stdout/stderr原字节和通道/序号、帧边界、原exit。未知ID、不完整header/payload、重复EXIT、EXIT后额外数据、非法退出载荷均拒；TCP EOF不能当exit=0。无stdin输入需求；若协议需要关闭stdin，仅允许协议规定的零载荷控制帧一次，不发送其他控制数据。

帧头可能被TCP任意拆分/合并，不能把一次read当一帧；stderr不能拼入stdout后由字符串grep推完整结果。必须合法exit=0、准确全stdout范围、无不允许的stderr/诊断及原物理归还，才判该查询成功。设备完整输出超cap只记不完整/失败，不部分解析成完整active instrumentation，也不由EOF/进程不在补ACK。

### H-R04 有界归档、资格与失败保管

每设备查询stdout+stderr累计≤65536B，不能两个通道各享一次64KiB。增加固定wire/帧数/控制/FAIL原因上限，零长度/碎片帧不能无限消耗CPU或原始留存预算；每帧限额及总wire开销须从总账内明确预留。原reader只用固定buffer，原writer沿已有有界队列；原wire与stdout/stderr副本及console重复均计账。不得把协议头/控制帧默默排除总预算。

10秒是caller结果资格，不能用Socket超时、interrupt、取消future或外部close伪造原工作归还。超资格立即封依赖，保同一原socket/read/write/归档对象等待自然结果，不启动第二命令。解析/落盘失败也先停止依赖并保管；若原shell仍可能运行，不为满足cap强关在途socket或重新连接。超限后可由同一reader固定buffer有界留存/明确丢弃标记，不增加内存或假称完整raw；原EOF/IO实际返回、失败和close状态继续分别记录。永久未知明确保留，不承诺强制结束。

### H-R05 总账及最小发布门

现草案预算算术成立：8192（已采host/父console）+131072（两查询）+1024（version）+65536（原exec收取）+32768（外层Java摘要）+8192（facts console）=246784B，余15360B，总262144B。**新协议帧/握手/错误/归档副本必须纳入这余量或重排既有分配后再审，不能直接沿用算术而漏wire开销。** 固定帧数/握手上限、最多三条socket连接、实际派发次数、记录失败预留和重复console都要入同一原账，未知不退款、旧余额不继承。

接收G已采host8192B只代表其19:31:58切片，不当未来新鲜在线事实；若需再核host须另派次数。原exec42537的未来一次空读≤10秒且文本≤65536B仍另行正式派单，本轮0；工具若不能保证输出资格先BLOCKED，不以取消读取隐藏超限。

新入口仅准确版本/固定角色，禁用普通直SDK，保持旧候选冻结和原pending封锁。提供集中新源码/协议pin/差异/最终class及真实有限回执，先离线独立复审，再由负责人另派两命令与一次原exec的准确批次/预算。不能随本设计准许设备执行或结束旧任务。

## 6. 最小有限验证与不扩框架

下一实现只验证新固定角色，不重跑长套件：

- 现有server无连接/错误status/FAIL/错transport/不支持shell-v2/连接中断，全部无重试、无SDK子进程、无kill/start服务。
- 准确两命令与第一→第二派生门；错scope/UID/组件/其他instrumentation、完整性/退出码、PID/start/parent变化都拒第二，不能从fixture示例PID填真实值。
- 真实生产帧解析器的header/payload碎片、通道交错、边界长度、未知ID、截断、重复/错误EXIT、EOF无EXIT、超限帧数与输出，不用镜像parser。
- 实际Socket owner/唯一reader/有界archive中connect/read/write/close及尾通知有限扣住；10秒资格先失败，释放同一有限peer后才实际归还，未返时无第二命令、无二close/替代reader。
- 日志/归档open/write/close故障和空stdout/stderr，不丢同原owner；本地peer/listener自身也要有有限错误释放和原回执，不能再次依父wait超时遗失对象。
- 最终JAR准确生产class与测试字节绑定、原SDK执行0和所有出站服务白名单；本机临时server是明确替身，不冒实际5037/设备证明。当前不跑这些测试。

## 7. 停止与提交

证据目录 `D:/CodexProjects/VideoKit/docs/tester/D1_E13H_REVIEW_EVIDENCE` 保存独立审计/输入切片、本地新UNKNOWN记录、设计条件、最终不变核验和manifest。3762份冻结输入在出报告前再核不变。新UNKNOWN只作记录，不新增进程/端口/原句柄查询；无控制/清理动作。

集中结论交负责人：当前PREPARE_ONLY硬拒绝可接受，生产执行仍阻断；同现有server socket的替代方向须满足H-R01–R05及实际有限证据后整包再审。旧主PENDING/旧诊断LOST/新本地VERSION probe UNKNOWN三栏独立，不补ACK、不退款。D1未过/M0未启、P0/许可及历史FAIL保持。
