# D1 E8 测试设计 V1.0

2026-10-17。本批仅设计与已有元数据离线论证，没有迁移/V2实现测试、Android/构建/媒体读取。需求证据矩阵与本机ledger解码校验见docs/coder/d1e8/evidence，不能将设计场景数记成生产通过数。交付后暂停。

## 证据基线和离线边界

重用且按SHA绑定：E5C_N2_ABORT_V1.1、原ABORT回执/归档元数据、E5C观察回执与报告、E6B_NORMAL完整报告/MP4原Before及账本HEX、E7A_MANAGED报告/seq9 snapshot/结束事件；每条关键主张标SUPPORTED/INFERRED_WITH_COOPERATIVE_ASSUMPTION/UNKNOWN/PROPOSED。本机只从已有1011B ledger HEX解码，独立重算每条hash链、三唯一R/S、0/53651/53567、消费107218/预留0，比较元数据SHA。不是新读设备或真实视频，不实现迁移接收器，也不拿一个复制模型冒充生产测试。

E7A实测只覆盖快完成、实际DUMP路由、保持到归档ACK和正常finish；28/338有限替身证据与实机范围分列。V1原birth/旧AVI匹配谓词及确切历史淘汰原因UNKNOWN不补证。设计静态约束只检查证据引用、必需场景/审批字段与对象清单完整，不证明任意实现安全。

## 后续必须直接验证的实际边界

实施阶段测试应直接调用实际迁移接收器/当前观察/原guard/账本与V2 owner，不复制其判断函数；仅替换平台调用以穷举故障。每场景核实际调用计数、原holder状态/实际返回、未改旧账本字节、无新增R/S/消费倒退、未发grant、结束未早于原返回。Android平台行为、读取boot/start权限、PID/参与者关联、持锁与跨进程确认必须另做精确有限设备计划，不能仅靠替身。

|组|场景与必须断言|
|---|---|
|L01 正确终局接受|确切原task/attempt/批准/header加六条ledger事件/三R三S及全部档案匹配，只新增两控制文件，原消费107218/产物/guard/fence不变；当前资源归还后本host可grant|
|L02 错或缺验收|错设备/UID/task/attempt/policy/批准摘要或任一archive SHA，拒绝且不写、不改预期|
|L03 正常历史淘汰|已退休旧4869 history0，不再查询；未退休/活未知actor不能藉此放行；API淘汰不是原因已证|
|L04 原host与跨host|原used实例不可重入；新host只取当前锁/核账/真实返回，不复用旧liveproof；重放同提交只读识别，不再S|
|L05 当前占用|原holder OPEN/ALLOCATING/CLOSING/UNKNOWN、任一CONTROL/slot/服务回调在途，拒绝；不得因锁可得而放过先unlock后close UNKNOWN|
|L06 文件身份|guard被替换/硬链接别名/符号链接/错误UID/角色/长度/dev-inode/fence，拒绝；在open/lock/读回间竞态不更新pin凑通过|
|L07 账本|截断/错链/重复R/S/错task/缺S/额外reserved/pending/旧前缀丢失/消费低于107218拒绝；完整合法后续追加允许，不固定永远1011B|
|L08 所有提交切点|目录建立/写payload/force/close/dirsync/写commit/force/close/最终guard归还各切点失败或进程死亡；无自证close，保留部分文件，禁自动清重试|
|L09 幂等并发|两迁移进程争同原锁；同payload已提交识别不重写，不同payload拒绝；同attempt不可新执行；未知close保持隔离|
|L10 生命周期|10秒资格在途/PENDING、迟到返回、工作线程中断、receiver失联、退出ACK重复/过期与平台finish异常；结束须所有实际原操作返回，迟到仍非PASS|
|L11 回退兼容|旧app不认识新policy安全阻断；未知schema/撤销policy/数据恢复不重新打开WRITING；无删记录回退或新budget|
|V01 身份采样|stat comm带空格/括号/长串，PID/start格式溢出、boot采样变化、权限拒绝，创建业务资源前失败；无壁钟替代|
|V02 原进程仍活|同boot+同start，无论history0或旧reason10均不可判原actor死；无权限或不可解析UNKNOWN|
|V03 PID复用|同boot不同start证明旧代次已结束，不杀新进程，不把旧closeACK改true；需全参与者安全处理和新owner真实返回|
|V04 重启|可信bootID变化且双采样一致，旧boot actor不能继续执行；重新核完整档案、账本、pending及当前资源；重启不是原操作限内成功|
|V05 跨进程FD|host死而codec/CPU持FD或转交未ACK，保持UNKNOWN；全部角色生存代次/FD谱系及真实返回分别核，不只看host|
|V06 终局/发布者|业务TERMINAL_STATE但原close未返不可RETURNED；发布记录不自证自身最后close；发布者在途/死亡恢复与旧业务完成事实分开|
|V07 部分终局与重放|canonical长度/重复键/schema/父摘要/重复commit/过期receipt/错nonce/从旧S套新task，拒绝；正常已退休事实不永远重问exit历史|
|S01 非恶意回滚损坏|原批准前缀缺失、header计数倒退和局部篡改可检出；保留证据隔离不修账|
|S02 同UID主动篡改|负面展示攻击者重算未外锚定后缀/回滚整套自洽快照的本地保证限制；不写成检测PASS，不为主模型强加新根|
|C01 有界成本|一次性迁移≤2小记录+目录，原输出R/S新增0；退休writer历史API0；每actor/参与者/总metadata界、holder上限、日志/时限与原媒体成本不扩|
|C02 停止范围|任何FAIL/PENDING/UNKNOWN停依赖不启动AVI/能力/cancel/M0，不自动迁移重试、清账或下批；交付后遵用户暂停|

## 通过标准与执行顺序

先独立设计评审，冻结准确合同和风险接受；再单独派实现并直接测试真实生产边界；其后静态整包审查，必要一次新APK构建，再由负责人审具体一次性迁移及不可逆语义，最后新host限定验证与正常功能批次。E8没有跳过这些步骤，也不安排下一批。任何关键实际返回UNKNOWN不得仅以设计论证消去；记录历史终局与新的当前liveproof同时成立才可能准入。

默认只保留合作故障恢复范围；如果要求主动对抗同UID，则需要新的安全目标和外部/硬件锚测试，不把同UID篡改反例藏掉。若当前已完成旧V1的来源/状态不符，结论应为ISOLATED，不以无穷诊断或不可能补造birth来拖延，也不以放宽资源门求通过。
