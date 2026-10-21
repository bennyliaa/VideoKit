# D1 R4 控制操作与有限IO逐行清单 V1.0

2026-10-16。仅设计、未实现/执行。依据[R4需求](D:/CodexProjects/VideoKit/docs/milestones/D1_R4_CODER_REQUIREMENTS_V1.0.md)，补齐[R3报告R3-R01](D:/CodexProjects/VideoKit/docs/tester/D1_R3_REVIEW_REPORT_V1.0.md)的操作映射。保持[R3 close/writer契约](D:/CodexProjects/VideoKit/docs/coder/D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md)与[61行manifest](D:/CodexProjects/VideoKit/docs/coder/D1_R3_BRANCH_MANIFEST_V1.0.md)；**仅覆盖R3 manifest§2/§6及R3回执§3的每行非query额度和总控制分配515的解释**，以本清单的具体操作数替代，不改其IO/分支/终态/资源/时间预算。原件不编辑。544次、101次query、180秒等硬限额不变；不新增组合finalize协议。

## 1. 计数、身份与执行者

一个下列具名token就是一个独立逻辑控制请求。控制台到权威、driver的每次提交均收费；接纳、拒绝、同ID重放各收费一次。每行按列出顺序给`row/n01`至`row/nNN` requestId，commandId默认等于requestId；重放时新传输requestId沿用原commandId，正文指明原ID。并发花括号中的请求各有ID、各收费；发起异步请求不等待完成便可发后项，但明确的检查点不可跳过。所有身份前缀含batch/task/sourceLease/version/consumer/generation或export/handle/epoch/delivery/descriptor/ticket；表内省略这些固定字段，不以字符串当授权。

四个执行者：G是外部controller和宿主权威所在父进程；S是G内source authority；O是G内Sink authority。J为预启Java helper，R为预启.NET helper，二者不同进程实例。G持guard，J持真实ReadHandle，R持独立reference；输出A/B/validator在R内，A与B是同进程真实dup，mailbox也在R内。另一个helper J只读恢复journal，不创建第三helper。恢复query仍由G中的O认证/裁定，不能把J读到字符串当权限。

读取/写入/seek是**数据面请求D**，逐个有`row/d01…`操作ID和实际delegate计数，仍需在源/Sink原子点接纳。它们不另算非query控制N，但严格占R3的I/C/V/O和行时间；这不将open、claim、close或验证授权藏进D。表中D全部展开至有限次数；一次D只有一次delegate，无自动补读/重试。每次close等控制N的实际native调用另留子operationId；N和native计数是两列事实，不能彼此代替。

query保持R3每行的Qr/Qn：`row/q1…qK`为K次新观察；Qr=1时再发送一次原`row/q1`，缓存响应不重新观察。每行计数表含明确Qr/Qn，**不会以状态回调/另一helper/失败请求再增加query**。有并发/重试时，正文指定q位置；其余行q放在该行最后检查点，重放q1在最后新观察之后，检验小seq不覆盖新seq。query只不可写元数据，≤100ms/次，全部在行deadline内。

同进程自动完成回报不是第二个客户端控制请求：每个已接纳操作至多一次可信完成事实写回其原操作槽，更新ticket/在途向量；重复完成只去重。结束D、关闭V、归还consumer使READY_ELIGIBLE/ABORTED条件满足，是既有操作的状态机后置条件，不新建API。其实际副作用/回报条数照记。需要另向helper发送释放闸门、close、授lease、提交ready/abort时，均在N列单独列出，不能改称回调省略。

固定故障/ACK丢失位置及静态能力包装随PF启动参数加载到J/R，参数含本清单有限的row/requestId映射，不改变任何任务初态或预开资源。运行时没有免费“arm故障”RPC；放闸请求`gate`明确计N。并发开始屏障、ID生成、纯CPU比较、controller本地单调计时、OS等待退出证据是本地调度/观察，不是再发控制请求；各自有事件ID并计时间/日志。任何实际增加的外部调用必须收费，禁止实现时用该约定隐藏动作。

## 2. token的单一请求语义和有限子操作

| token/权威 | 一次请求的原子点、有限实际动作及所属资源 |
|---|---|
| `res(c,v)` / S | 接纳一份future-open reservation，初次同task建立记录；不打开文件。后续consumer/版本嵌在同记录，不另增顶层记录。 |
| `g+` / G | 绑定该task/version的只读guard分配登记→一次原生open→对象身份记录；只拥有G这份ticket。 |
| `h+(x)` / S→J | S原子登记一次OPEN_ADMITTED，J一次factory/open和至多一次结果回报；得到独立x/ticket。seal先赢则拒绝、factory0。一次控制接纳请求及其单次provider调用，不额外调用另一个open API。 |
| `r+` / R | 为当前已授权版本登记并一次只读open独立reference；不得沿任意路径重开。 |
| `seal(v)` / S | 一次ACTIVE→SEALED_DRAINING；禁止新数据接纳。自身不隐含close或结束consumer。 |
| `end(c)` / S | 一次结束该consumer的future-open义务；资源未清保持QUIESCING，全部证据满足才RELEASED。不关闭descriptor。 |
| `cancel(c)` / S，`cancelO` / O | 一次围栏该任务新增数据；响应可丢，已接纳IO和各ticket保留。不会在该请求内自动发close RPC。 |
| `ch(x)` / J、`cr` / R、`cg` / G | 一个精确descriptor的一次close请求，最多一个底层close进入；注册ticket/revision在本次分配时已建立。release证明回原权威；其他descriptor不随之抹去。 |
| `retry(x,rev)` / 该close权威 | 单ticket的新attempt，限R3资格；次数/并发/revision先CAS。拒绝时native0。相同command重放不是新attempt。 |
| `gate(op)` / J或R | 一个已接纳异步操作的完成投递/执行闸门放行，不另读/另开文件，也不重新发送writer。最多1次实际放行。 |
| `retire` / S | 模型owner身份围栏，保留所有引用；不是OS死亡证明。S版本授权`version(v)`只改授权模型，原文件不修改。 |
| `notice(v)` / S | 一次旧releaseSequence通知接收，只更新匹配版本墓碑；不授新访问或物理移动权。 |
| `grant` / O | openTemporary：意图/能力/输入别名检查和唯一grant原子登记；只不可写元数据。不在此请求里create/dup/send/claim；拒绝时这些均0。 |
| `allocA` / R | 已有grant的单目标create：先登记allocation槽，再一次独占create及A/ticket回报；失败未知不再create。 |
| `dupB` / R | 已有A的一次真实DuplicateHandle，不继承、不CLOSE_SOURCE，分配B独立ticket；不是第二open。 |
| `sendB` / R | 原子耗唯一send资格后，一次同进程mailbox放入B能力单元；无额外OS dup。ACK丢也不重送。 |
| `takeB` / R | 唯一receiverInstance的一次takeOnce，将同一B放入唯一owning cell；不dup，重复取拒绝。 |
| `claim` / O | 认证receiver/delivery/claimId，单次持久认领；确认已收才准原B写。未知只query/围栏/abort，不恢复写。 |
| `flushB` / R | 一次真实flush及所声明的数据sync ACK（每项最多1）；B仍持有，不将flush当close。 |
| `ca`、`cb` / R | 分别只关A或B，一请求一ticket；最多一次native close，不组合“关所有writer”。 |
| `v+` / O→R | 封存/全writer归还后原子授一次validationLeaseId及outputRevision，R一次只读open；一个授权/打开请求及其一次provider子调用，不含读取或关闭。 |
| `cv` / R | 一次validator descriptor真实关闭并完成该lease归还；成功验证receipt只在实际读完、关闭及输入收尾后可用。 |
| `takeover` / O | 非终态原子新epoch围栏；已有READY则仅返回既有终态，不增加epoch。 |
| `ready` / O | 对同task/revision/epoch的receipt仲裁并提交READY；旧owner拒绝，native写FD0。首次T01的回复固定丢失，不重发ready。 |
| `abort` / O | 单次ABORT_PENDING仲裁，资源为0才ABORTED；READY先赢则返回同token。后续归还回报可完成本次待定abort，不发第二次终态命令。 |

S/O权威的持久元数据动作（已接纳N及D）：原command内最多两次有界journal事务，分别为副作用前接纳记录与实际结果回报；纯元数据终态可只需一次。每事务明确journal open/write/sync/close各≤1，以及所需namespace ACK≤1，最多两组、全部列native计数，再确认原状态序号；ACK未知不盲重做。命名空间/requiredDurability ACK若不足即NOT_RUN_DURABILITY_UNPROVEN/PENDING。S/O每个已接纳N或D最多两个各≤8KiB元数据事务，新query最多一个≤16KiB只读事务，每事件≤1KiB；受R3总日志4MiB和既有行日志32KiB门禁，达到字节门禁先停止。journal读写句柄在每事务实际close后才允许下一次事务/J恢复读取；controller log＋journal/恢复reader同时最多2。这里的磁盘子调用逐项记录，不当媒体验证读取；不声称它们有固定时延。query重放不新开journal。实际实现若需超过上述两事务/额外副作用必须重新映射评审，不能自行增加。

## 3. 源31行：独立控制序列与IO

未写参数的g/h/r是该行任务既有对象；每任务资源owner始终G/J/R。每行最后的q数量见表；没有借别的S任务句柄。表内`D`标数据面，不计入N。N是本行所有明确控制token的数目，行预算不再固定6。R3所有I/C/H/B/秒保持，末列再次列秒以便复核。中间行D指最终归还状态，不能据此提前close。

| 分支 | 任务/初态→按序控制token（一个token一个N） | 数据面/实际调用与正常或异常出口 | N | Qr/Qn | 秒 |
|---|---|---|---:|---|---:|
| P01-N1 | S01空→res(c1,v1); g+; h+(H); r+ | D: provider/reference各一次65536请求；g/H/r各open1，满读才窗口成功 | 4 | 0/1 | 2 |
| P01-N2 | S01沿N1→无新控制 | D: 同两对象各一次65536，保留三引用 | 0 | 0/1 | 2 |
| P01-N3 | S01沿N2→无新控制 | D: 同上，独立窗口3 | 0 | 0/1 | 2 |
| P01-N4 | S01沿N3→无新控制 | D: 同上，窗口4；仍不关S01 | 0 | 0/1 | 2 |
| P02-EOF | S01沿N4→无新控制 | D: H在L请求1，delegate EOF−1；reference不再读 | 0 | 0/1 | 1 |
| P02-ZERO | S01沿EOF→seal(v1); ch(H); cr; cg; end(c1) | D: seal前零请求在bridge返回0、delegate0；三close各1后DRAINED | 5 | 0/1 | 1 |
| P01-S1 | S02空→res(c1,v1); g+; h+(H); r+ | D: 四次真实1B、外层65536/65535/65534/65533；ref读4B，UNFILLED | 4 | 0/1 | 2 |
| P01-S2 | S02沿S1→无新控制 | D: 窗口2同四read＋ref1，额度不足拒绝下一请求（controller本地准入事件） | 0 | 0/1 | 2 |
| P01-S3 | S02沿S2→无新控制 | D: 窗口3同上，不补读 | 0 | 0/1 | 2 |
| P01-S4 | S02沿S3→seal(v1); ch(H); cr; cg; end(c1) | D: 先完成窗口4同上，再执行控制序列，实际三close后D | 5 | 0/1 | 2 |
| P03-RAW | S03空→res(c1,v1); g+; h+(H) | D: Z请求16、EOF，guard/H两引用 | 3 | 0/1 | 1 |
| P03-MEDIA | S03沿RAW→seal(v1); ch(H); cg; end(c1) | 本地空媒体preflight判定，无decoder/媒体read；两close后D | 4 | 0/1 | 1 |
| P04-SEQ | S04空→res(c1,v1); g+; h+(H); r+ | D: length=null包装，真实H32/ref32，两个read | 4 | 0/1 | 1 |
| P04-CPU | S04沿SEQ→seal(v1); ch(H); cr; cg; end(c1) | 本地CPU要求已知长度负例，无decoder；三close后D | 5 | 0/1 | 1 |
| P05-SHORT7 | S05空→res(c1,v1); g+; h+(H); r+; seal(v1); ch(H); cr; cg; end(c1) | D在seal前：外层32/25/18/11/4，delegate7/7/7/7/4；ref32，共6read；末三close→D | 9 | 0/1 | 2 |
| P06-ZERO | S06空→res(c1,v1); g+; h+(H); seal(v1); ch(H); cg; end(c1) | D在seal前一次请求32，注入0、delegate0；不重试；两close→D | 7 | 0/1 | 1 |
| P07-EARLY | S07空→res(c1,v1); g+; h+(H); seal(v1); ch(H); cg; end(c1) | D在seal前4096处请求1，真实EOF、EARLY_EOF；不报换版；两close→D | 7 | 0/1 | 1 |
| P08-LATEOPEN | S08空→res(c1,v1); g+; h+(H); seal(v1); cancel(c1); gate(open); ch(H); cg; end(c1) | open真实返回H后先扣投递，q1在cancel后见PENDING；gate后晚H不交付只close，q2在排空后 | 9 | 0/2 | 3 |
| P09-CANCEL | S09空→res(c1,v1); g+; h+(H); cancel(c1); seal(v1); gate(read); ch(H); cg; end(c1) | D在cancel前真实读32后扣完成；q1见operation1；gate后无新代数据回调，q2见D，重放q1 | 9 | 1/2 | 3 |
| P09-TIMEOUT | S10空→res(c1,v1); g+; h+(H); seal(v1); gate(read); ch(H); cg; end(c1) | D真实32后扣完成；本地1秒timer触发一次SOURCE_TIMEOUT；q1超时前/q2超时后PENDING/q3排空后，重放q1 | 8 | 1/3 | 3 |
| P10-A | S11空→res(c1,v1); g+; h+(H); seal(v1); ch(H); {retry(H,rev1),retry(H,rev1)}; cg; end(c1) | ch预delegate失败attempt1；q1得rev1；两不同command并发一接纳attempt2、一IN_FLIGHT/STALE；实际close1；q2终态后重放q1 | 9 | 1/2 | 3 |
| P10-B | S12空→res(c1,v1); g+; h+(old); ch(old); h+(new); r+; {ch(old原command重放),retry(old旧revision)}; seal(v1); ch(new); cr; cg; end(c1) | old close实际1但ACK失；q1取得CLOSED_PROVEN；之后新H真实32/ref32，旧两请求native0；q2最后D，重放q1；数字未复用也记录不同object，不伪造强制复用 | 13 | 1/2 | 3 |
| P11-FUTURE | S13空→res(A,v1); res(B,v1); g+; h+(HA,A); r+; ch(HA); end(A); h+(HB,B); seal(v1); ch(HB); cr; cg; end(B) | D: HA16、HB16、ref32，共3read；q1在end(A)后/B尚未open见reservation1，q2最终D。g1/HA1/HB1/ref1分配，HA关闭才开HB | 13 | 0/2 | 3 |
| P11-SEALED | S14空→res(A,v1); res(B,v1); g+; h+(HA,A); r+; ch(HA); end(A); seal(v1); h+(HB,B); cr; cg; end(B) | D在ch(HA)前HA16/ref16，共2read；q1在seal后B未结束，HB请求拒绝/factory0；q2排空后D | 12 | 0/2 | 3 |
| P12-OLDOPEN | S15空→res(A,v1); g+; h+(H1); r+; seal(v1); ch(H1); cr; cg; end(A); version(v2); res(B,v2); g+; h+(H2); r+; ch(H2); cr; cg; end(B); h+(old-v1拒绝) | D: v1 H16/ref16先于seal，v2 H16/ref16后于open/关闭前，共4read；v1排空才授权v2。v2读完即关三引用/end(B)，但v2尚未seal、版本仍ACTIVE，不能获物理移动许可；q1旧open拒绝且v2状态/计数不变 | 19 | 0/1 | 1 |
| P12-NOTICE | S15沿OLDOPEN→notice(v1) | 迟到v1通知只墓碑；q1只查v1再重放，同时原通知操作的状态变更证据表明v2仍ACTIVE且无seal/移动许可，v2媒体引用已在前行实际归还 | 1 | 1/1 | 1 |
| P12-CHANGED | S15沿NOTICE→version(v3可信变化事件); seal(v2) | v3只是同一记录的授权版本事件、无consumer/open；SOURCE_CHANGED通知按v2绑定处理，无原文件修改；前行已真实归还，seal使v2排空，q1核版本与资源 | 2 | 0/1 | 1 |
| P13-SEQ | S16空→res(c1,v1); g+; h+(H); r+ | D: 注入顺序能力，H8/ref8两read | 4 | 0/1 | 1 |
| P13-SEEK | S16沿SEQ→seal(v1); ch(H); cr; cg; end(c1) | D在seal前一次seek请求，能力层拒绝、delegate seek0，源read预算不增加；三close后D | 5 | 0/1 | 1 |
| P10-D | S17空、全部Q后→res(c1,v1); g+; h+(D); h+(C); seal(v1); ch(D门闸前登记); ch(C门闸前登记); gate(D首次); retry(D,rev1); retry(D,rev2); retry(D,rev3第四拒绝) | 两close均在首次故障前接纳、C尚未执行。D首次＋2次都确定预delegate失败、attempt3/native0；q1在首次失败后，q2在第二失败后，第三失败的可信返回带rev3供第四拒绝；最后重放q1。两对象保持拥有，G guard1/J对象2 | 11 | 1/2 | 2 |
| P10-C | S17沿D→gate(C首次); retry(C不同op); retire(S原owner); retry(C新owner) | C原请求实际进入最多1、结果UNKNOWN；q1在未知后、q2不同op拒绝后、q3新owner拒绝后，重放q1；不再close/open/结束consumer，转GC | 4 | 1/3 | 3 |

P12在OLDOPEN行完成v2数据访问并实际关三引用/end(B)，NOTICE及CHANGED行媒体峰值才确为R3的0。v2仍ACTIVE不等于允许移动：旧通知不能替它seal或生成物理事务许可；CHANGED才显式seal。没有在guard归还后再读或授权新的consumer，历史身份记录仍在S15内。S17的预登记ch只是独立异步close请求在delegate前受测试闸门扣住，不是新“组合关闭”API；C完成前D已耗尽也不会让C成为新close授权。票据命名S17.D/S17.C分开，原UNKNOWN不因后续退出改成功。

## 4. 输出30行：新任务不借其他任务的writer或receipt

T01的B正常claim后持续到Q01；T02/T03/T04各有独立grant/A/B，T05更是完整独立任务。普通数据payload仅复用Q01已脱离输入的不可变32B私有字节；不得跨task复用授权/lease/receipt。所有A/B/V ticket冠以其T编号。W0–W5用既有takeover独立请求建立授权的新cleanup epoch，表示旧owner身份退休；不另外假定免费恢复获权，也不声称真实OS死亡。每个真实目标只有allocA一次，dupB最多一次，send/take/claim最多一次，拒绝/重放不增加这些计数。

| 分支 | 任务/初态→按序控制token | 数据面/副作用及检查点 | N | Qr/Qn | 秒 |
|---|---|---|---:|---|---:|
| Q09-OPEN2 | T01空→{grant,grant原command重放} | 两次请求一接纳一重放、grant记录1/create0；q1两请求完成后再重放 | 2 | 1/1 | 2 |
| Q09-CLAIM | T01已有grant→allocA; dupB; sendB; takeB; claim | create/dup/send/install/take/claim各1，确认已收；A/B各ticket，native峰2，q1末尾 | 5 | 0/1 | 2 |
| Q09-SECOND | T01已CLAIMED→claim(不同receiver拒绝); claim(不同claimId拒绝) | 两个负例分别请求，dup/send/take增量0，原B仍唯一writer | 2 | 0/1 | 1 |
| Q09-REPLAY | T01沿SECOND→grant(OPEN2原command重放); claim(CLAIM原command重放) | 两次重放只元数据，owning cell不增；q1末尾再重放q1 | 2 | 1/1 | 1 |
| Q09-PLAN | T01沿REPLAY→grant(同export不同planVersion拒绝) | 意图冲突无副作用，原任务/对象保留 | 1 | 0/1 | 1 |
| Q09-SOURCE | T01沿PLAN→grant(同export不同sourceVersions拒绝) | 同上，字段单独变更一次 | 1 | 0/1 | 1 |
| Q09-PRESET | T01沿SOURCE→grant(同export不同preset拒绝) | 同上，字段单独变更一次 | 1 | 0/1 | 1 |
| Q01-SEQ | T01已有A/B→res(src,v1); g+; h+(H); r+; seal(v1); ch(H); cr; cg; flushB; cb; ca; v+; cv; end(src); ready | D在seal前H32/ref32共2；D在flush前顺序B写32一次；全部writer关闭后V只读至多65536/1read；cv后end(src)→receipt本task READY_ELIGIBLE；ready实际持久但回复按固定配置丢失。g/H/r和A/B峰5，验证不重叠 | 15 | 0/1 | 2 |
| Q05-STREAM | T01沿Q01→无新控制 | space=null但预先允许bounded；复核同次流式IO及既有READY事实，实际写/验证增量0，不另制造成功任务 | 0 | 0/1 | 1 |
| Q06-LOST | T01既有READY原回复失→recoverJournal(J) | G确认journal写句柄已关后J独立只读open/read≤16KiB/close各1，返回O校验同token/intent；q1由J认证发O并紧接同ID重放，二者完成后q2由G直接发O。无新writer；所需真实durability不证则NOT_RUN | 1 | 1/2 | 3 |
| Q08-READY | T01既有READY→cancelO(回复按固定配置丢失) | q1恢复READY、q2仍同token，再重放q1；无在途writer/validator，不能报CANCELLED | 1 | 1/2 | 2 |
| Q07-READYFIRST | T01既有READY→takeover; abort | 两请求均实际到O，返回原READY/token，不增加epoch、不重新close | 2 | 0/1 | 1 |
| Q04-DUP | T02空→grant; allocA; dupB; sendB; takeB; claim; ca | 独立目标，create/dup/send/install/take/claim各1；A实际close1后D由B小写1B一次；B仍持有，不借T01 | 7 | 0/1 | 2 |
| Q02-RANDOM | T02沿DUP仅B→flushB; cb; v+; cv | D: B三次64位seek＋三次小写（含覆盖，写共≤32B）；flush/close后V一次≤65536读回，cv归还；未markReady，留验证取消对照 | 4 | 0/1 | 3 |
| Q08-VALIDATOR | T02封存且首V归还→v+; cancelO; gate(validation完成); cv | D: 第二V一次≤65536先真实读后扣投递；q1在cancel后见lease1，q2放闸/cv后A，q3确认A，再重放q1。一次cancel仲裁在资源清后完成ABORTED，无第二abort | 4 | 1/3 | 3 |
| Q04-CLOSEACK | T03空→grant; allocA; dupB; sendB; takeB; claim; flushB; cb | D: B写1B一次；cb实际close1但ACK丢；q1见B完成证明/A仍1，q2再次确认，重放q1；不重关B，不关闭A | 8 | 1/2 | 3 |
| Q08-WRITER | T03仅A→ca(执行闸门前登记); cancelO; gate(Aclose) | q1在cancel后A仍1，gate使原close实际执行1，q2 A归还/ABORTED，q3同终态、重放q1；不新发ca | 3 | 1/3 | 3 |
| Q05-SPACEFAIL | T04空→grant; allocA; dupB; sendB; takeB; claim | D: B第一次小写1B完成，第二写请求1B注入ENOSPC、delegate0；真实写≤1B；A/B不自动close，错误置失败围栏待取消 | 6 | 0/1 | 2 |
| Q08-UNKNOWN | T04仍A/B→cancelO(回复按固定配置丢失) | 两引用保持；q1/q2/q3均查PENDING，再重放q1；没有新grant/close，当前不是资源0或已取消 | 1 | 1/3 | 2 |
| Q08-DRAIN | T04已cancel→ca; cb | 两个真实close各1，可信完成回原cancel槽使ABORTED；q1终态。不另发无必要gate或abort，不伪造此前PENDING | 2 | 0/1 | 2 |
| Q07-TAKEFIRST | T05空→grant; allocA; dupB; sendB; takeB; claim; flushB; cb; ca; v+; cv; takeover; ready(旧owner拒绝); abort(新owner) | D: claim确认后本task B写32一次，flush并逐份关；本task V一次≤65536读完/cv→同revision receipt。q1在READY_ELIGIBLE后；旧ready仅本地排队未提交，takeover先持久e2，旧ready实际到O拒绝、native0，新owner abort→A；最后重放q1不倒退状态 | 14 | 1/1 | 3 |
| Q09-W1 | T06空→grant; allocA; takeover(模型旧owner退休); ca; abort | A实际create1/close1，dup/send/take/claim0；owner退休为模型事件，非OS死亡 | 5 | 0/1 | 2 |
| Q09-W2 | T07空→grant; allocA; dupB; takeover(模型旧owner退休); ca; cb; abort | A/B各create/close1，dup1/send/take/claim0 | 7 | 0/1 | 2 |
| Q09-W3 | T08空→grant; allocA; dupB; sendB(ACK未知); takeover(模型旧owner退休); ca; cb; abort | q1在send未知后保留安装未知槽；takeover后用既有mailbox槽定位原B仅清理、nativeclose各1；q2在abort后，再重放q1；send总1/take0/claim0。定位不是再次交付 | 8 | 1/2 | 2 |
| Q09-W4 | T09空→grant; allocA; dupB; sendB; takeB; takeover(模型旧owner退休); ca; cb; abort | 安装/take1、claim0，原receiver cell的B真实close1，不漏引用 | 9 | 0/1 | 2 |
| Q09-W5 | T10空→grant; allocA; dupB; sendB; takeB; claim(提交确认丢失); takeover(模型旧owner退休); ca; cb; abort | q1在claim未知后，即便CLAIMED也不恢复写；q2在abort后再重放q1；claim1、数据write0、不重新claim/send/take | 10 | 1/2 | 2 |
| Q09-W0 | T14空→grant; takeover(模型旧owner退休); abort | grant已记录目标尚未创建，create/dup/send/take/claim0；只元数据终结 | 3 | 0/1 | 1 |
| Q03-RANDOM | T11空→grant(能力冲突拒绝) | 顺序能力要求random，writer/create/dup/媒体IO0；q1只查拒绝记录 | 1 | 0/1 | 1 |
| Q03-VERIFY | T12空→grant(无验证能力拒绝) | validationReadLease=NONE，全部媒体IO0，不暗建可读副本 | 1 | 0/1 | 1 |
| Q09-ALIAS | T13空→grant(输入别名拒绝) | 元数据身份检查绑定PF已知input身份；必要只读身份句柄最多open1/close1、同时1，均为grant检查的显式native子操作，无truncate/write/create目标 | 1 | 0/1 | 1 |

Q07-TAKEFIRST的14次独立控制请求中，grant/claim/两次writer关闭/验证授权/验证归还/takeover/旧ready/新abort均有独立ID；alloc/dup/send/take/flush也逐个收费。无组合finalize、无免费前置。cv完成并核revision后才生成T05 receipt，复用的是无源访问能力的32B字节，不是T01 receipt。正常成功路径存在，但实际阻塞、能力/持久性/版本不满足仍应停止，不能用预算表保证运行通过。

### 4.1 正常到达各检查点时的真实副作用计数向量（仍未运行）

T01–T10合计create目标10、dup9、send8、take7、claim提交6；install与take正常确认路径一致，W3安装未知在清理前单列区间，不能提前精确计0。claim拒绝/重放另有控制请求，不增加提交6。输出数据write请求9次、实际delegate最多8次（T04第二写注入失败delegate0）；另随机seek3次。flush/syncB各4次；写descriptor关闭A10＋B9＝19次，每个不同ticket最多一次。validator独立open/read/close各4次（T01一次、T02两次、T05一次），总V预算4×65536。实际短写/读不足不补delegate，按失败/UNFILLED停止，不使计数偷偷增加。T02第一次dup后1B小写和后续三次随机写分别记录，共4write，不只记三次。

每个N用一对有界接纳/完成事件：接纳≤256B，完成≤512B，后者逐字段含该N的native open/create/dup/send/install/take/claim/flush/sync/close及journal子调用计数、ticket/owner/证明状态和首错。每个D也一对总≤768B，所有query响应≤1KiB。不是每个native子步骤再堆无限文本。字段超长直接拒绝/脱敏，不能截掉UNKNOWN事实。每行32KiB包含这些所有事件；本表最大N19/D4/Q1行按19×768＋4×768＋1024＝18688B，其他行也小于32KiB；独立record快照总≤16KiB（当前槽≤8KiB＋journal临时/备用槽≤8KiB，避免落盘临时副本未计）。PF128KiB、全局512KiB及32条记录快照的总文件预算保持3,178,496B，余量仅停止证据。事件数、每项计数和实际日志字节必须落盘，达到门禁不能靠省略证据报通过。

## 5. PF16与全局清理/停止32的具体分配

PF每项独立`PF/n01…n16`，无额外query；控制请求的正常/拒绝都消耗该槽，不重启PF。

| ID | 接收者与独立请求 | 原子事实及有限子操作 |
|---|---|---|
| PF/n01 | G：建立运行头/预算与私有日志目录 | 唯一PF记录；日志/journal仅元数据不计媒体目标 |
| PF/n02 | G：启动J，携固定manifest配置 | 原进程实例、≤3条pipe；一次进程创建，不执行额外版本子进程 |
| PF/n03 | G：启动R，携固定manifest配置 | 同上；两helper在整个批次内不重启 |
| PF/n04 | J：版本/runtime hello | 既有J返回JDK身份/能力，不再启动java-version进程 |
| PF/n05 | R：版本/runtime hello | 既有R返回.NET身份/能力 |
| PF/n06 | S：res(PFconsumer,C/v) | 属PF记录的源reservation |
| PF/n07 | G：g+(C) | 一次guard open、ticket |
| PF/n08 | S→J：h+(PFH) | 一次真实ReadHandle open |
| PF/n09 | R：r+(C) | 一次独立reference open |
| PF/n10 | G：同对象/共享模式证据核查 | 核对三个open已返回的metadata（不再调用stat），核同实例/长度/无写共享条件；随后D各读16B比较，计I32/C2，不在此另open |
| PF/n11 | S：seal(PF版本) | 阻止后续PF数据接纳 |
| PF/n12 | J：ch(PFH) | 实际close1 |
| PF/n13 | R：cr | 实际close1 |
| PF/n14 | G：cg | 实际close1 |
| PF/n15 | S：end(PFconsumer) | PF源排空，运行头记录仍在 |
| PF/n16 | O：固定能力/输出目录/元数据额度预检 | 不创建媒体目标；真实dup、durability能力只能后续实际证明，不能把声明当PASS |

PF/n10请求的本地元数据子操作不是三次新的helper RPC：对象身份随PF/n07–09的真实open返回，G对收到的有界证明做核查；若实现需要追加跨进程stat请求，须另映射，不能偷偷执行。原始数据read仍各有D ID和两次实际delegate计数。

GC是**清理和停止合用的32槽**，不是正常清理32再加故障32。`GC/n01…n32`单槽最多提交1次，无需的槽记SKIPPED_ALREADY_PROVEN，不移用。没有额外query。单任务串行，停止时最多一个当前task；P11最多两个consumer；J同时最多一个可安全再关的活动H（S17两对象均无重试资格、不能用GC/n10）；R最多一reference、A/B各一或一个validator。早期失败新增helper实例禁止。

| ID | 接收者与独立请求 | 资格/实际操作及异常出口 |
|---|---|---|
| GC/n01 | S：全局源admission fence | 原子停止全部新reserve/open/read，资源不清零 |
| GC/n02 | O：全局输出admission fence | 不新grant/交付/认领/验证授权，既有清理仍可 |
| GC/n03 | S：cancel当前consumer A | 不存在/已完成则跳过，未证资源仍在 |
| GC/n04 | S：cancel当前consumer B | 仅P11第二consumer可能需要，不为每个历史task再cancel |
| GC/n05 | O：abort当前输出 | 仅当原分支尚未提交cancel/abort且非READY需要，已有pending命令则不重发 |
| GC/n06 | J：放既有晚open闸门 | 最多一个，晚H已在原open槽、只供清理 |
| GC/n07 | J：放既有read完成闸门 | 最多一个已真实返回的read；无新增read |
| GC/n08 | R：放既有输出close/写完成闸门 | 当前输出最多一个闸门，A/B关闭仍各由后槽计费 |
| GC/n09 | R：放既有validation完成闸门 | 与writer持有状态互斥，不偷偷重读 |
| GC/n10 | J：close一个已知安全持有H | 未曾close或ticket仍具安全attempt资格且未耗尽才用；已在途、CLOSED、UNKNOWN、S17.D耗尽一概跳过，native≤1 |
| GC/n11 | G：close父guard | 一份精确ticket，native≤1；UNKNOWN不盲关 |
| GC/n12 | R：close reference | 单reference/ticket，native≤1 |
| GC/n13 | R：close输出A | 精确A/ticket，安全资格同上，native≤1 |
| GC/n14 | R：close输出B | 精确B/ticket，安全资格同上，native≤1 |
| GC/n15 | R：close validator V | 只有既有lease，native≤1；在途read未结束不伪造归还 |
| GC/n16 | J：受控正常退出请求 | 不装盲重关UNKNOWN的shutdown hook；G本地等匹配启动实例实际结束，记录≤1次OS等待及退出证据；不是信号故障实验 |
| GC/n17 | R：受控正常退出请求 | 同上，R有未证资源时也只能靠真实退出证据，不声称close调用成功 |
| GC/n18 | S：J原实例death证据通知 | 单一owner事实接纳，核固定原ledger中每份J引用（S17.D/C各自列证），原close UNKNOWN/首错保留 |
| GC/n19 | S：R原实例death证据通知 | 独立核R的source reference/in-flight，不清父guard；没有R源引用也可跳过 |
| GC/n20 | O：R原实例death证据通知 | 独立核输出A/B或V的逐descriptor归属；不借S通知清输出 |
| GC/n21 | S：end当前consumer A | 只有该consumer所有操作/回调/其他owner引用实证归还才释放；否则PENDING |
| GC/n22 | S：end当前consumer B | P11第二预留，条件同上；不追加新consumer |
| GC/n23 | G：close J stdin父端 | 一个pipe端点/ticket，子端只在已证J退出后据owner exit列账 |
| GC/n24 | G：close J stdout父端 | 单端点 |
| GC/n25 | G：close J stderr父端 | 单端点 |
| GC/n26 | G：close R stdin父端 | 单端点，子端按R退出分别证明 |
| GC/n27 | G：close R stdout父端 | 单端点 |
| GC/n28 | G：close R stderr父端 | 单端点 |
| GC/n29 | G：close J process handle | G已存退出证据后关父进程句柄，不把close该句柄当J已死 |
| GC/n30 | G：close R process handle | 同上 |
| GC/n31 | G：close当前journal/恢复reader | 每事务应已关；至多一份异常残留。若残留在尚活J且未证，不能由G关同数字；保持PENDING并记录owner |
| GC/n32 | G：flush/close controller log | 单日志owner结束请求，有限flush1/close1并保存最终快照；未知保留，不开新log循环重试 |

death通知是一次单一owner生命周期事件，不批量关闭/执行子请求：最多枚举已登记6个媒体槽及该owner固定控制资源证明，仅更新对应ticket知识；S与O分别接收、分别收费。退出请求与实际死亡分开，等待是G本地OS观察（无跨窗口query），不是helper自己证明已死。未实际退出不得发送“已死”事实通知；可用同槽发送UNKNOWN观察但不释放资源。S17常规尾部：GC关闭G guard、J实际退出、S逐D/C证明、end消费者；D的实际close次数仍0，C结果仍UNKNOWN。

任一close失败未知后不追加重试；本批GC每槽最多1次，未证资源保留。若guard/log/pipe等属于G的资源也UNKNOWN，G仍活，不能借J/R死亡清除；清理决定期限内无法证明即PENDING。GC不是保证所有故障都可在32次内彻底释放的承诺。完成任务的历史资源已关且证据在记录内，不逐task再调用cleanup；最多活动资源向量由行级串行/终态门禁保证。清理20秒、停止18秒共享这些32槽；先到的deadline禁止后续等待或新提交，未用槽仍未授权补跑。

## 6. 累计预算与时间可行路径

逐行表重算：P非query176、Q非query127，合计303；PF16＋GC32后非query351≤443，query101后全控制452≤544，未分配92次。主体表为唯一计数依据。非query包含所有列出的拒绝、重放、PF16、GC32；全部query保持18重放＋83新观察＝101。总控制不得超过544，非query不得超过443，未分配差额不授权任何新动作。媒体IO、10目标/32记录、输出/验证/日志、6媒体句柄/24总OS句柄/8缓冲及180秒均沿R3；每个D的外层请求收费和真实delegate另列，EOF/失败不退预留。

时间按R3每行deadline，不把控制步骤各给100ms后再加IO。query在本行最多100ms；本清单给非query接纳/状态机处理规划每请求≤10ms的快速路径，锁外原生IO、journal sync、实际消息完成另计入剩余行时间，**不是10ms保证或功能证据**。逐行必要控制处理预留为`10ms×N＋100ms×(Qr+Qn)`，剩余全给该行有限D/native/等待/落盘；若某平台实测不满足必须停止/报具体超限，不能删步骤或扩大deadline。计时从发送前开始，不能先免费做native再开始计时。

Q07-TAKEFIRST：14×10ms＋2×100ms＝340ms，3秒行剩2660ms给本task create/dup/交付/写/flush/关闭/验证/journal，存在步骤完整的有限低延迟路径，无必然的控制额度冲突。P12-OLDOPEN：19×10ms＋100ms＝290ms，1秒剩710ms；S17-D：11×10ms＋300ms＝410ms，2秒剩1590ms；C：4×10ms＋400ms＝440ms，3秒剩2560ms。实际系统调用阻塞仍可能使这些行NOT_RUN/失败/PENDING，不能以静态余量报真实完成。

PF16的快速处理≤160ms，20秒剩19840ms含两helper启动、read及回收；GC32≤320ms，20秒清理与18秒停止保留其余实际等待/证明落盘。全分区仍20＋52＋55＋5＋20＋10＋18＝180秒。Final-accounting只纯计算/使用已开日志的有界写入，无新控制/媒体IO；最终日志close用GC/n32在记账完成后调用，仍归其32槽，时间归Final-accounting10秒，不能在log关闭后再写或额外开文件。GC/n32的close结果通过原controller调用的既有返回通道给外层调用者（有界≤8KiB、计全局回执512KiB），不另建log来记录上一份log的关闭；若返回也丢失，外层按该log关闭未证/PENDING，不能用关闭前写下的意图冒充完成证明。GC的其余31槽在清理/停止分区执行，GC/n32固定为收尾最后一步；分区预算可提前停止，不在180外补日志。

本批不批准实现/运行。公共API承载、真实版本/共享模式、DuplicateHandle绑定、实际dup/send/take/claim/close次数与ACK、必要durability和OS退出均未验证。宿主JNI仍BLOCKED、D1未通过、M0未启动；Kit/Flutter/C ABI/许可/P0及历史FAIL/C14冻结不变，F03四次仍仅encoder协商。
