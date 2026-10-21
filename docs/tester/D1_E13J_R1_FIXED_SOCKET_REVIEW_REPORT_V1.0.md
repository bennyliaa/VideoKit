# D1 E13J-R1 固定Socket最终整包独立复审 V1.0

2026-10-18；tester。依据R1正式需求、基本J需求及E13I三项P1。只选择最终d1e13j-r1；初版J保留历史，不作为另一执行候选。

**结论：PASS_LIMITED_OFFLINE_REVIEW。E13I-F01/F02/F03在最终R1的生产静态接线及有限本机原证据范围关闭，未发现新的阻断缺陷。支持负责人据本报告准备一次E13G只读补充的准确release绑定。** 当前审批仍ABSENT，未签发执行许可；本报告不执行query、原exec收取或处置，不代表设备/产品通过。D1 NOT_PASSED / M0 NOT_STARTED。

本轮只读冻结文件/制品及已有原证据，无真实5037/本地peer网络、SDK、设备、旧handle/PID、STATUS、处置、部署、候选编译或套件重跑。没有新probe，不制造新UNKNOWN。

## 1. 最终封包及来源

| 对象 | 独立核验 |
| --- | --- |
| 外seal | `b6251eaf359ef3bf64233735b248568282c56aa470f7790c9e070a28ea8c86d3` |
| ZIP | `docs/coder/D1-20261018-E13J-R1-source.zip`，1063432B，SHA256 `a51f35fa437d8b1da40d9a69571b5750ea12941d49c9a85086624a567f03b495`；262条唯一记录/261个准确成员，集合/字节/SHA/CRC通过 |
| 最终JAR | 347659B，SHA256 `715496d5d997c48c61b669316943341cd4a4fc320ee0c2805d459b99f60d142f`；193成员=F183原字节＋R1实测10生产class；检查/fixture类未混入 |
| 独立审计 | tester自有10561项检查通过，读取4690份唯一冻结文件、18份原命令/保管回执；不运行候选verify替代独立结果 |
| 旧冻结 | 十三组manifest行375/65/46/367/270/118/141/9/1001/1179/181/415/249全部保持，不把重叠行加总冒唯一文件数 |

四份最终R1交付/契约/自检/补充计划、最终源码diff、原class、固定协议10份全文/NOTICE及8份准确摘录均可核。协议沿I固定commit `1cf2f017d312f73b3dc53bda85ef2610e35a80e9`，本轮没有网络抓取或准确SDK编译映射的新宣称。

初版J seal `fb3966af1514094eecc937ff34562a7dc3b311586279d7526f1eda98cc00a6d0`、ZIP SHA `920252c0eb42db9eedefecc8ddb57ab05046735bc9df5608d7798998cd152477`及249行冻结成员保持。J阶段生产编译确为两次：初版一次、R1因raw故障后的审账时序源码修正另一次；不是同源机械重建，R1自身一次。初版成功不冒最终字节证明，R1全部10新class与保存的实际测试class逐字节对应。F183未重编，无APK/Gradle/native或新增Maven/native依赖、签名产物；旧F APK19/fixture3及既审签名原样保留。许可UNCHANGED_NOT_GRANTED。

## 2. 三项P1关闭判定

### E13I-F01：实际IO前预算——CLOSED_LIMITED

`E13JSocket.java:13–17,21–24`统一allowance：单一原reader下，每次底层read只传min(wanted,remaining)，返回n才计实际RX；完整TX意图在write前核准/收费，写入进入与返回分栏。remaining=0时新read/write/drain乃至EOF探读都被拒绝，不借第二条/其他预留，不事后截留存求合规。

到限设budgetUnknown，同原Socket不关闭、无重连/取消/替代reader；原reader可结束有限归档，但原non-daemon keeper继续强持未知Socket，不认physicalReturned、不启第二条。10秒是结果资格，晚返不能补成通过。该设计允许预算UNKNOWN长期保管，profile不负责强行清理。

BUDGET_BOUNDARY直接调用最终生产readSome/drain，底层计数InputStream实际读70656，末次长度1024，到限后read/EOF/drain调用次数增量均0；holder仍UNKNOWN。BUDGET_TX预置已收费前缀后实际只write剩2字节，额外write0；剩1字节只read1，之后底层调用0。前缀是明确单位夹具，不冒已发送70654网络字节；夹具未allocate活Socket/启动keeper，不靠kill结束永久未知网络对象。

保证范围准确限定为**应用层实际读取＋保守发送意图**，不是网卡、TCP/IP头、OS缓存或远端总流量。实际Socket链与该门使用同一最终class字节，未用镜像预算器。

### E13I-F02：生产持久审账——CLOSED_LIMITED

`E13JArchive.java:11–17`连接前建立原intent/facts；有界intent≤1024B，facts最多P/T各≤512B、合≤1024B。`E13JSocket.audit()`实际接入原writer，记录cw/in/tx/we/wr/rt/off/disk/rawQuota/frames、EOF/EXIT、failed/late/qualification/budgetUnknown、reader/Socket/writer/physical及有限why，auditOwnClose=UNPROVEN。元数据写入意图先计费，未知/失败不退款不二写。原审账文件open/write/close未知时原Op/keeper保管，不缺账放行。

R1真实修正已核：raw.write异常在writer循环内处理，仅停raw写及后续raw入队，writer仍等待同reader done，原计费继续受硬门控制，之后再写终止审账；没有重开writer或重试raw。与初版的实际源码SHA不同，revision-history/diff准确。

PRODUCTION_AUDIT直接核真实Batch/Op/Archive生成的文件，无ICheck final-owner-facts：第一query T为cw1525=in1236+tx289，第二cw1442=in806+tx636，与正常original.wire长度一致，we/wr和metadata上限正确。R1新增AUDIT_AFTER_RAW_FAILURE原raw故障点cw302，后续获准RX后终止T为**cw820=in531+tx289**，failed/FAILED、readerBody=true；原wire只写成297B、off303、rt820，清楚保留计费/尝试/成功写入的差异，不把缺raw当完整。

P是执行中首次可写切片，字段可能处在不同并发更新时点，不用P单独结算精确恒等式；终止T在reader done后核稳定计费。P/T都不自证facts自身close、writer join或最终caller资格：正常T的SNAPSHOT_NOT_FINAL、writerAlive=true/physical=false与实际写入时点一致。caller晚资格和真实归还由生产Batch的有界J_PRODUCTION_RETURN_SNAPSHOT补充，使用既有Java摘要预留；不能回填已关闭的T冒当时迟到或把文件当最终PASS。

rawQuota是帧长度预扣，不能当已读完整payload；rt是留存尝试、off是queue接受、disk是成功write，不承诺掉电耐久性。TX意图不是全部物理发送ACK。这些限制不影响终止计费可审，但必须在后续报告继续分栏。

### E13I-F03：父诊断失败保管——CLOSED_LIMITED

`check_host.py:8–49`父holder先登记，diagnostic统一捕获BaseException，只降低资格/保存有界错误；pending write/console失败不跳过finally内同Popen wait。原wait未知由同holder继续等待，不换Process。stdout/stderr分别唯一close，任一close未知则父仍持有，不二close。只有原wait及两文件close真实返回才退活动OWNERS；最后诊断失败不改这些事实，也不补资格。

parent-faults-002直接导入最终真实run，仅将本地wait资格适配20ms，child睡350ms。PENDING_WRITE/CONSOLE/BOTH三组分别故障，均同PID自然exit0、parentOriginalWaitReturned及两记录文件close=true，qualificationPreserved=false，保存准确diagnosticFailures。没有早逸出原日志异常、kill/daemon/替代Popen；新未知0。与I只测正常pending路径不同，原缺陷故障分支已直接覆盖。

## 3. 实证范围及保持的协议门

最终10组为OK、EXIT_NO_EOF、WRITE_FAIL、CHAIN_OK、CLOSE_PENDING、TAIL_PENDING、BUDGET_BOUNDARY、BUDGET_TX、PRODUCTION_AUDIT、AUDIT_AFTER_RAW_FAILURE；另有describe/生产未派拒绝、脚本AST/准确角色拒绝及3父故障组原回执。未选的I旧模式不列作R1重新实测，未跑长套件或永久未知活Socket故障后强关。

固定127.0.0.1:5037、HA1Q6WXR，每query同一原Socket先transport后shell-v2，借用流不独立close；无SDK/kill/start/version/feature/fallback。严格header/长度/ID/通道合64KiB/256帧/EXIT1byte/EOF门继承并按准确源码核；真实API31格式/权限/服务行为仍NOT_RUN。本机peer与计数流是明确有限替身，不冒设备/旧owner归还。

第一query实际成功且原reader/keeper归还后，才完整核全局instrumentation、原scope/batch/class/method、app10221/am2000和父/argv，再派生第二boot_id/stat/status/cmdline。其他instrumentation、权限/格式/全量超限或第一UNKNOWN即停止；不grep/扩大限额/补第三条。两次切片不证明无PID复用，不授终止资格；未匹配fixture/codec继续UNKNOWN。

Socket/read/write/close与archive文件、writer、keeper实际返分栏；预算耗尽或审账UNKNOWN可能使keeper长驻，这是规定的保管结果，不是可自动清理的临时错误。P/T及生产摘要不能替原Java/Android closeACK。

## 4. 总262144B与准确一次发布条件

总预留不变：base116736=host8192+原exec65536+Java32768+observer8192+batch intent2048；两query各72704=wire70656+metadata2048；合262144，余0。每query实际RX＋完整TX意图由IO前门守住，未知不退款；无额外raw副本/原文echo。

**支持现在准备准确发布绑定，不需再扩工具框架或重跑长套件。** 当前R1/初版J保持冻结；以下为发布前必须核实的最小清单，不是本报告已经执行或签发的许可：

| 绑定项 | 准确条件 |
| --- | --- |
| 审查基线 | 使用本报告最终SHA及R1 seal/JAR/source pins，选最终R1，排除初版J及I/H旧入口 |
| typed release | 精确kind=e13jFixedReadOnlyRelease、scope=`116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef`、serial=HA1Q6WXR、review=本报告SHA、budget=262144、requests=2，按生产E9Record准确序列化、≤2048B并计算SHA |
| 来源策略 | 新发布来源仅绑定该准确request SHA及对应脚本审批常量/准确新JAR路径；不改Socket/archive/identity/限额/脚本模板，不覆盖当前R1。用同reviewed F183与当前实现来源制作最终发布制品，记录实际必要host编译；逐成员比对及精确常量/路径差异验核即可，不新增框架、APK或全套测试 |
| 避免自引用 | release.review指本次完整功能复审SHA；新策略验核回执另存并绑定release及最终JAR/脚本SHA，不要求release自含未来验核文件SHA，从而不形成循环 |
| 精确入口 | Java固定exe，-cp最终发布JAR、com.videokit.spike.e4.E13JReadOnly、--g-readonly、准确release路径/SHA；新PS精确JAR/role/release SHA相符，禁止包内helper旁路 |
| 原once及root | 固定root D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE；once=e13j-r1-g-readonly.once；wrapper id=E13J-R1-SUPPLEMENT-ONCE。首次真实create/force/close后才connect；已有/未知/失败不换id/目录重发 |
| 原始证据与派生 | 第一实际wire/生产审账/完整stdout能够绑定第二派生脚本；不得外填旧/示例PID，两个脚本/服务模板及协议来源pin固定 |
| 外层文本额度 | Java stdout+stderr合32768B；observer自身intent/PID/pending/receipt/console及重复副本须在准确request定稿时离线核其合并分配，使用既有8192份额及已定总账，不能只分别看单文件cap或让任意长pins数组扩大总量。固定最小输入和有界错误摘要，装不入现分配则不执行，不临时提额 |
| 正式派单 | 负责人验核上述最终准确字节并另发一次G补充范围/预算/保管交接；当前sourceReview/release/once未签发、APPROVED_REQUEST_SHA=ABSENT且角色网络前拒绝，不能先改常量就运行 |

发布策略仅做上述机械绑定，若出现任何功能/预算/协议或保管变更，须集中说明并重审受影响部分。可以直接依此准备具体release和最终来源，无需再次提出通用工具建设。

## 5. 一次G补充的执行停止门

正式派单后最多两query，各10秒资格/64KiB通道合上限及70656实际应用IO；无真实server可用、不兼容或中途变化，不start/restart、重连或SDK退路。第一失败/其他占用/UNKNOWN不第二，到限不为探EOF偷读。保同原owner和审账对象；可能常驻预算UNKNOWN，不能在此只读profile中强关收尾。

原exec42537空输入收取作为独立子项：未来另派最多一次、≤10秒响应资格/≤65536B文本；工具无法保证则该项先BLOCKED，不能循环、取消Promise丢返回、Ctrl-C、非空输入或重建session。两query是否继续须按正式派单关系处理，不将未用65536B借给网络。空输出/工具返回不是原Java/reader/pipe/Android ACK。

G已采host19:31:58仍历史切片，不偷偷增加CIM调用预算。两个只读结果用于当前状态/收尾方案，不执行行政终止，不安装部署或续产品方法/T07；需要的动作另审。

## 6. 历史未决及报告保全

旧v17主case PENDING/UNKNOWN、旧ps诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN、E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN三栏独立；本轮不查其当前对象、不补ACK、不退款。R1修复只属于新bytecode，不反控旧v17或补其marker/内存事实。

原主保管保持，无新轮询。D1未过/M0未启、T07未派，P0/历史FAIL/UNKNOWN、renderer/audio/Kit及许可门不变。独立证据位于 `D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_REVIEW_EVIDENCE`，4690份审查输入出报告前再核不变；集中通知负责人，报告SHA与通知回执另存，不反写已发送报告。
