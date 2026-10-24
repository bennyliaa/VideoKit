# QUALIFICATION06 封存05完整事实调用图静态A报告

2026-10-24；结论：静态A完成，发现资源前完整准入及状态边界缺口；不签运行通过，D1未过/M0未启。仅审封存05固定字节，06候选及独立B均未测试。

## 范围与证据

依据 D1_FACTS_V2_QUALIFICATION06_TESTER_REQUIREMENTS_V1.0.md。ZIP SHA256 `32aadc2e6021d03f5fe780e3f2f8d0fe99a15c6cb1370223375ab8ace575e458`；内部manifest `2b102c6dc962d7a6b1d4742b38171b871132097703db8fdd004ad40802bef3a7`。独立逐内容核106唯一成员、105项1062255B，提取49项固定代码/契约元数据至本批证据根；未提取work目录。originalCallsFinal=false，原排他lock明确排除，快照不包含全部原件，不证明原调用归还。

证据目录：D1_FACTS_V2_QUALIFICATION06_PHASE_A_EVIDENCE。extraction-audit.json保存逐项核验；source-budget-table.json/CSV保存准确逐阶段字节、25pin明细与16项runtime预留；state-and-source-anchors.json保存源码行证据。只运行tester文件读取、哈希、AST解析和算术脚本；未import产品、调用产品函数、构造Capture/Gate或执行产品进程。SDK/设备/Gradle/Git均0。未读活动输出、旧lock、session或PID。

## F01：完整调用图超出64读，准入过晚

以下是全部前置成功返回条件下的静态计划，绝非05原计数器或异常日志。普通Gate.source_read永久预留文件长度+1及1读，检查在开文件前；PreparedFacts原读取按实际长度计，合并只记一次。RAW长度139264B取封存manifest中q05-4e42cf95条目，未读取原活动raw。

|路径节点|累计计划读|累计计划字节|
|---|---:|---:|
|Gate manifest及25pin|26|详见逐项CSV|
|固定runtime helper及metadata重读|28|详见逐项CSV|
|runtime原子预留14文件+metadata两次|44|本段7952341|
|合并PreparedFacts六次及CLI raw归属一次|51|详见逐项CSV|
|route construct seal/script额外两读，原Popen之前|53|8495709|
|route返回后script及contract校验|55|8501483|
|receive seal/binder/collector/CLI/plan五读|60|8540624|
|父raw检查及子raw预留|62|8819153|
|fixture metadata及解释器原文件检查|64|8931914|
|fact construct seal请求|65|将被拒绝，实际不得累加|
|fact construct script计划请求|66|若全部允许则8936575；65拒绝后不可达|

runtime为原子28→44预扣，并非观测到16次逐步返回。metadata5447B、14声明文件合计7941447B；仅依据封存声明核算，不读取当前运行时。Gate.receive的proof/receipt两读在控制通道及carry，不能加进source次数。父raw为R+1，子raw预留为R，子raw预留当前先累加再检查，尚不代表子进程实际读过。

当前RAW_FILE账面完整路径需要66读；第65个请求在64+1>64时应先拒绝，计数仍64，不能报告实际已收费66。全路径假设字节8936575远小于268435456B，字节充足不能抵消次数超限。COMPLETE无raw分支去掉CLI归属、父raw、子raw三项，当前账面63读8518782B；不把RAW结论推广到不同LIVE路径。

此外，route_fixture.py:13显式Path(__file__).read_bytes()做子进程自身哈希，未找到相应父侧source预留。此前pin、construct及返回后校验读取同文件不覆盖这次独立读取。此项另列1读和该脚本实际长度，详JSON；若纳入完整显式来源义务则67读。不是把旧账本改写成67，也不把解释器隐式导入或OS元数据伪装成已测I/O。fact子raw已有独立预留，不重复计费。

PreparedFacts的USED已经在六次初读后消耗；原Gate先完成自身runtime检查才合并私有成本。完整费用未在once、claim及原route构造之前一次纳入，拒绝可能已晚于资源占用。原64/256MiB门应保留；不能扩cap、退款或重放旧once解决。

## F02：entered与真实原构造边界混淆

facts_entry.py:17–25的construct先做参数/环境等校验，再读seal/script，然后才调用保存的original(a,**kw)。calls.append只在original返回后发生，因此空calls/无PID无法证明原构造没进入。

fact_collector.py:155在调用subprocess.Popen包装器前设置entered=True并加入CUSTODY；156–158将包装器任何异常概括成FACT_START_UNKNOWN。故确定发生于包装器内、真实original之前的预算拒绝也可能落入unknown保留路径。entry_gates的checker-start同样以原调用是否返回决定UNKNOWN，尚未区分包装器已知拒绝与真正原构造未知。

这是源码边界缺口。05原异常没有落盘，不能认定其实际就是第65读异常，更不能据此解除05保留、二close、kill、补ACK或退款。真实原构造进入后抛错、挂起或返回未证仍须保守保留；所有源I/O/关闭返回情况也必须独立判断。

## 最小改进及后续验收

在现有Gate/PreparedFacts与construct机制中先形成固定完整调用费用，再在资源进入前拒绝；覆盖初读携入、runtime原子预留、两角色guard、子raw及显式子自读。可复用准确scope内已验证且不可变的seal映射，保留必要脚本字节及全部pin校验；或消除同一固定helper/metadata的冗余读取。必须按06最终固定字节重新核完整图，不能仅减两读就签通过。无需新增诊断、IPC或账本服务。

在实际original(a,**kw)调用点区分admitted、native-constructor-entered与returned；具类型的已知前置拒绝只有在相关原调用和I/O均已证返回时才能分类无新进程。不得用外层entered或返回后calls记录代替真实边界，也不得放松进入后未知保留。

新增oracle.json所有条目为PLANNED_NOT_RUN，覆盖完整预算、字节/次数边界、分支、真实构造前后与控制通道。此前05驱动A28项及108规划保持原件，仅作准备引用，本次未执行旧helper。后续完整06冻结经负责人核包正式派B，才独立验证原receipt身份、控制容量、生产正负链、辅助18、预算、新状态分类及尾项V1。维持360/320、1GiB/16MiB/96、并发1/retry0。当前不自动B或设备测试。

工具记录：初始系统python别名不可运行；随后tester算术脚本发现两个快照raw条目，修正为准确q05-4e42cf95元数据选择后运行成功。两次准备失败均在纯文件核算阶段，没有产品资源调用或预算消费。
