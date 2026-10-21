# D1 E13I 固定Socket整包独立离线复审 V1.0

2026-10-18；tester。依据正式E13I需求及E13H H-R01–05/§6。

**结论：NOT_PASSED，3项P1集中修复后重审。** 固定同连接transport＋shell-v2的协议/原owner接线、完整封包和生产硬拒绝可核；实际wire预算、生产计费事实持久化及父超时记录失败保管尚有缺口，当前不支持签发E13G补充执行release。D1 NOT_PASSED / M0 NOT_STARTED。

本轮不连接真实5037或任何本地peer网络、不执行SDK/设备/旧handle/STATUS/处置/部署/产品方法，不编候选、不机械重跑31组或长套件。仅离线审查；另对原check_host.py真实run函数AST做一次约0.65秒的受控记录失败probe，启动一个有限本机Python子进程，之后由tester用同Popen自然wait并关闭原文件，未留下新未知对象。没有新Java/候选生产JAR执行。

## 1. 封包、来源、原始证据

| 对象 | 独立核验 |
| --- | --- |
| 外seal | `d18b61928227bff9fb46848b5ae7d6c40a869c7a1976b23f5a72467d05a7ddf6` |
| ZIP | `docs/coder/D1-20261018-E13I-source.zip`，1120921B，SHA256 `0cbbf6e45bb87bdc998fbb45e0b97305be09f12610f6e5341ce7ac2eb130c2cf`；415条唯一记录/414个准确成员，集合/字节/SHA/CRC通过 |
| 最终JAR | 346101B，SHA256 `7eeffb64bb98f826de6d98004dd513170921b48c134804e0a4038b3459f1cb78`；193成员=原F183逐字节沿用＋本批10个实测生产class；检查/fixture未混入 |
| 官方协议 | 固定commit `1cf2f017d312f73b3dc53bda85ef2610e35a80e9`，10份全文/NOTICE及8份逐行摘录长度/SHA/准确来源范围一致；0B NOT_FOUND的OVERVIEW不当权威 |
| 独立审计 | tester自有9687项检查通过，读取4177份唯一冻结文件，40份原命令退出/保管回执核验；不运行候选verify替代独立审查 |
| 旧冻结 | 十一组manifest行375/65/46/367/270/118/141/9/1001/1179/181保持，不加总冒唯一文件数 |

生产host仅一轮必要javac：4生产源及初期检查源对准确F base JAR编译，31有限peer组使用其实际字节；supplement-002另一次javac只编新增测试probe，生产未重编。这一额外probe编译有原回执，不写成“所有javac仅一次”。无新APK/Gradle/native、新Maven/native依赖；原APK及签名沿既审F冻结不变，不冒新签名产物或再次签名执行。NOTICE保存不等商业许可通过，许可UNCHANGED_NOT_GRANTED。

官方主源码中smart-socket长度/status、shell协议ID/uint32长度、单字节EXIT及close-stdin和Java解析对应：`shell_protocol.h:38–63,96–108`、`shell_service_protocol.cpp:31–67`、`daemon/shell_service.cpp:784–792`等准确全文及摘录可核。长度源实现使用native uint32，Java按little-endian限制在已声明Android arm64范围；不是任意端序/设备兼容证明。本轮只读包内全文，不访问网站或实际server。

## 2. 集中缺陷

### E13I-F01 / P1：wire上限只限制留存，错误后的实际读取无上限

位置：`E13ISocket.java:13–14,20–21`；`E13IReadOnly.java:11,14`。

wire()先增加chargedWire，再在retainedWire越70656时停止归档；readSome仍读原socket并增加incomingWire。任意协议/输出/归档错误后drain()持续read直到自然EOF，wireOverflow/Batch.reservations不阻止新的实际读取。固定4096B buffer只保证内存和留存有界，不能保证实际RX或TX+RX总量有界。发送意图与实际返回虽在内存区分，Batch只收固定预留，没有接收实际超额的总账门。

**已有原证据直接确认**：host-001/WIRE_OVER/final-owner-facts.txt为retainedWire=69934、chargedWire=78126、incomingWire=77837、intendedTx=289；78126=77837+289，已越单query wire70656。测试只断言retainedWire≤cap，并不能证明实际网络预算。该有限例尚未耗尽全批256KiB，但同一drain没有更高硬门，远端更多数据可越单项乃至全批总额；不能用未发第二条的额度或“资格失败”自动授权超额。

交付已坦诚说明actual流量可能超过留存上限，这避免假称成功，却不满足本需求的实际wire/总262144预算。按失败处理、停止第二条不等于预算已经被守住。

最小修复：把应用层每次read/write的准入长度纳入同原query/Batch剩余硬额度，在实际IO前核准，不事后才截留存。额度不足时不新增消费、封住第二条，保原Socket/reader/keeper为预算未决，不强关、取消、重连或用新reader收尾；必要的边界/EOF判断也须预留计费。若选择继续drain，则需明确其实际流量不受本profile约束并另审需求，不能以现262144 profile放行。这里只限制本程序主动消费/发送，不能承诺内核缓存或远端网络总量由客户端绝对限制。新增有限证据应核实际incoming+保守TX意图而非仅retained，且不能制造永久活Socket后kill求测试退出。

### E13I-F02 / P1：精确wire/发送状态只存于内存，生产原账无法独立结算

位置：`E13ISocket.java:9,24`、`E13IArchive.java:13–14`、`E13IReadOnly.java:22`；对照`ICheck.java:46`。

incomingWire/intendedTx/chargedWire/writesEntered/Returned/retainedWire/frames/rawBytes/late等在Op内存中，facts()会格式化它们，但**生产路径没有调用并持久化facts()**。实际archive facts仅eof/protocolExit/offered/written/archive失败及提前快照说明；公开main只打印固定reservations。丰富final-owner-facts.txt是ICheck额外写的测试产物，不是生产归档接线。

因此当wire被截留、实际发送未返或JVM退出时，仅凭original.wire和现facts不能恢复未留存RX量、是否进入/返回write、原实际计费与资格。尤其F01的超额counter可能完全丢失，固定预留不能代替实际账。完整wire在正常路径可反解协议，不覆盖已丢弃/部分发送路径；测试harness保的丰富信息不能替生产记录。

最小修复：在原有限元数据预算内接入生产计费/资格事实，包含实际RX、保守TX意图、写入进入/返回、原留存尝试/offered/written及不完整范围、协议EXIT/EOF/原失败/late、各线程/Socket原返回分栏。原final facts只由同owner生成，有界、异常/记录未返仍保管；不以facts自证自身close或writer thread已返。利用现有两份≤1024B元数据额度定稿，无须新增通用日志系统或额外raw副本。新增证据须走真实生产Batch/Op，去掉测试harness额外facts也能离线审账。

### E13I-F03 / P1：父等待超时后，pending记录或console异常仍可提前抛弃保管

位置：`tools/check_host.py`的run函数TimeoutExpired分支及finally。

已修的正常超时路径会保同Popen和输出文件并继续p.wait，已有50ms实际AST证据支持。但该分支在继续wait之前先无保护地write(pending)和print(flush)。若磁盘写入或console失败，会直接进入finally；waitReturned仍false，不关闭文件、不完成原wait，随后异常逸出整个脚本。OWNERS只是该Python进程内dict，没有额外非daemon责任者或可审交接，脚本退出时可再次失去原Process与记录句柄。这是故障记录路径，不能以正常超时通过覆盖。

tester有限probe直接提取**同一run函数AST**，只将20秒资格换为20ms、在write(pending)注入OSError；启动睡眠0.6秒的本机子进程。实测函数已抛OSError时原子进程仍活、原waitReturned=false。tester外层随后用同holder Popen自然wait exit0、关闭同原文件并清除测试引用；新未知0、kill0/网络0。准确source SHA与事实见parent-record-failure-probe.json，未编候选或运行网络套件。

最小修复：pending/console记录故障只能降低资格/标记录未知，不能越过同原Process的持续wait或明确保管交接；每个诊断写入都要受保护，最终资源事实与记录成功分开。测试包括pending磁盘故障与console故障，直接执行原run分支，确认仍由同父holder等待原child自然返/同文件close；不能靠daemon、kill或换Popen补成功。

当前三项均未修复；生产审批pin ABSENT使本轮没有实际流量风险，但不支持将现候选绑定release执行。

## 3. 已成立的实现与有限证据边界

| 项目 | 已审结论 |
| --- | --- |
| 固定服务与同连接 | 默认生产127.0.0.1:5037；同一原Socket先host:transport:HA1Q6WXR，再shell,v2,raw:固定脚本；无SDK/host:kill/start/feature查询/fallback。两个角色脚本不是外部参数，第二PID仅由第一完整证据派生 |
| 服务及帧解析 | ASCII长度/OKAY/FAIL≤256、五字节header/LE uint32、只接受stdout1/stderr2/EXIT3、单字节EXIT，一次4号零载荷close-stdin；固定4096块，不按未审uint32分配大payload。坏ID/截断/重复EXIT/EXIT后数据/EOF无EXIT/非零/非空stderr均失败 |
| 数据与资格 | 单帧和stdout+stderr累计64KiB、帧256；合法EXIT0和自然EOF分别必要；10秒仅结果资格。现F01导致错误后的实际wire上限仍不成立，不能把此行外推成总账通过 |
| 第一→第二门 | 第一query.run须无失败/完整/物理返回并join原reader/keeper后才解析；唯一全局instrumentation、旧准确scope/batch/class/method、app10221/am2000及父/argv一致。其他占用/格式/权限未知拒第二，缺fixture/codec角色不推不存在 |
| 启动身份 | 第二固定boot_id和两个派生PID的stat/status/cmdline，核正start ticks、四UID/PPID/argv；两切片不证明无复用，不授终止资格 |
| 原Socket与文件 | 先登记OWNERS，流仅借用、唯一E4Owned Socket close；同reader的实际EOF/IO返回与逻辑EXIT分栏；keeper join原reader，外部观察archive writer真正停止并join/逐文件返，caller join keeper后才资格成功。文件/close UNKNOWN不二close |
| late与依赖 | 资格超时/第一失败或解析错误停止第二，晚返不恢复原资格；原keeper保同原对象。Batch once使用CREATE_NEW/force/原close，失败不绕过已有once；现三缺口仍需独立修 |
| 冻结审批门 | APPROVED_REQUEST_SHA=ABSENT，PS准确角色也在context/Process前拒绝。当前actualScope/release/once/sourceReview未签发，不能直接改冻结常量或旁路脚本 |

31个本地peer模式及额外15身份拒绝、空stdout协议层、父超时、脚本拒绝等证据与最终10生产class字节绑定。本轮不重跑这些peer。非IO的E4Owned永久close异常只证明契约保持UNKNOWN/不二close，不冒永久未知活Socket动态归还。真实Socket close未返/CLOSING与尾通知扣住有有限链证据。

CONNECT_FAIL使用本地端口0的实际连接失败；peer的有限accept/read超时及stop/join修复避免旧“join后才listener.close”的具体死等路径。该修复可接受；F03针对另一条父记录故障，不改写现31组的真实成功。测试peer的原finite释放/自然join不是Android或实际5037服务行为证明。

## 4. 总账与留存必须分栏

当前预留算术正确：base116736=host8192+原exec65536+Java32768+observer8192+batch intent2048；两query各72704=双向wire70656+两metadata2048；合262144，无余额。TX意图为保守收费并非物理全部写出，archive retained/offered/written/文件长度是不同事实，内存stdout/stderr用于解析并非额外落盘文件。

但reservations只证明预留规模，不能证明actual incoming受限；wire文件不含被丢弃流量，测试facts说明它已经不同。F01修复前实际流量可能无限，F02修复前生产原账不能持久复核。两者都不能由“不通过/不发第二条”豁免，也不能自动借未用的其他预留扩单项cap。保留全部未知预留，不退款。

父console/原exec工具返回的重复文本必须继续计相应预留；原exec≤65536B/一次≤10秒在工具接口无法保证时仍先BLOCKED，不以取消Promise丢返回。G已采host19:31:58仅历史切片，不因引用8192B变成未来fresh，也不偷偷加CIM调用。

## 5. 一次E13G补充的最小准入——当前不支持，修复后另审

必须先集中修三项并重交最终来源，确认实际wire上限、原生产账持久事实及父故障保管通过，不新增通用机制。随后才可由负责人签发准确一次read-only release，不能把本文写为已批准执行。

最小绑定条件：

- typed release精确kind=e13iFixedReadOnlyRelease、原runtime scope/serial、独立review SHA、budget262144/requests2；固定新主机来源的批准request SHA与准确release字节一致。生成新来源策略版本及最终JAR后重审，不修改已封I。
- 固定Java/最终JAR SHA/公开角色、准确release路径及SHA、PS脚本SHA/固定root/id/32768B host cap、once名称与唯一批次。原once必须由同Batch在connect前真实写/force/close；已有/未知/记录失败就停止，不换目录/id再跑。
- 两条固定脚本/服务模板源码SHA、官方协议commit与来源pin、所有IO/帧/字节/元数据限额及实际账Schema。第一真实wire/完整stdout及归还记录能够绑定第二派生的准确PID脚本；不能把IFixtures示例PID带到设备。
- 原exec42537单次空读与两query分别派发和记账，≤10秒与文本65536B可保证才调用；不循环，不Ctrl-C、不新STATUS/Binder/SDK。查询只读不解除旧主任务/旧UNKNOWN，不自动触发处置或T07。
- 任一第一调用不合格/其他instrumentation/设备输出过大/权限或身份未知，保持原对象并停止第二；实际server消失或不兼容不启动server、不fallback、不重连重试。第二切片不赋予结束历史PID的资格。

这些是修复后准确派单必须满足的条件，不是新许可或要求重做APK。若另行调整预算含义，须需求明确变更及独立复审，不能在当前固定预算里隐式执行更多实际流量。

## 6. 三个历史UNKNOWN及本轮停止

旧v17主case PENDING/UNKNOWN、旧ps诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN、E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN独立保留；本轮不查它们当前PID/端口/原session，不补ACK、不以新peer成功抵消或退款。新测试probe由tester真实收尾，不产生第四个未决对象。

原主保管按既定安排保持，无新轮询；离线协议实现不反控旧v17，D1未过/M0未启、T07未派、P0/许可/历史FAIL及renderer/audio/Kit门不变。报告和集中缺陷主动发送负责人，证据在 `D:/CodexProjects/VideoKit/docs/tester/D1_E13I_REVIEW_EVIDENCE`；4177份审查输入最终再核SHA不变，通知回执另存，不反写已发送报告。
