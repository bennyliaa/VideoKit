# D1 E8A 直接切点测试设计 V1.0

2026-10-18。全部为设计，当前产品/Android/迁移/部署执行0、构建0。已有生产源码直接静态审查、旧部署脚本和原记录引用与实现级执行分开；不以设计状态表自测来冒充真实owner测试。

## F01 实现阶段必须调用的对象

未来测试必须直接调用实际managed migration runner的身份phase/命令接收/队列预留/Job/holder/finish门、实际registry writer/读取/终局接收器、原E5BGuard/E4OutputBudget和实际new-host observation分支。只替换平台IO/时钟/传输/进程观测，禁止复制状态模型或只重跑E7纯gate27项。每次assert实际调用顺序、原FD raw/dup/dir状态、真实返回计数、是否platform.finish、是否生成activation接收资格和产品资源创建，不能仅assert文本状态。

|ID|场景与必须断言|
|---|---|
|A01|没有registry reserve、actor身份采样或初始FD close UNKNOWN时，mkdir/CREATE_NEW/业务写调用0；prepare产品资源创建0|
|A02|错UID/PID/bootSource/start/nonce/handle/attempt/ordinal/policy/descriptor/prepare pair SHA，不得BIND；当前权限不可验证不降级V1|
|A03|外部reserve落盘/close/校验失败或管理head不连续，写许可0；不能根据device完整commit重建成功authority|
|A04|EXECUTE接受后尚在队列/allocate窗口，原operation已预留，不得因FD EMPTY提前finish；重复seq命令不执行第二次|
|A05|mkdir、intent open/write/force/close/dirsync每一真实切点卡住/Exception/Error，registry不越级，原holder和handle保留|
|A06|payload每切点及commit每切点失败/原actor退出，区分从未创建/完整/截断，不把缺返回当未发请求而重试|
|A07|完全相同有效acceptance+commit，最后guard unlock成功后raw或dup close在途/UNKNOWN；另一host可取锁仍不得激活、platform.finish0|
|A08|metadata/dir/ledger原close均返回但最后guard未返，RETURN_VERIFIED0；allCallsReturned不能由调用者传bool|
|A09|10秒资格到界/迟到原返回，原PENDING不可变；原owner真实归还后允许按非合格收尾，不自动变可激活|
|A10|同commit下缺/旧/错actor returned回执、错误seq、管理失联、活UNKNOWN，new-host grant0；正确scope缺任一actor清单也拒绝|
|A11|收到精确原RETURNED快照、外部实际存储/关闭、归档seq、原normal finish后才FINAL审查；仅finishClaimed或进程不存在不当close证据|
|A12|外部returned.json/checkpoint/final seal各写入/flush/close/独立验证失败，没有可发布H_actor；不同记录不同步不挑最高文件名|
|A13|管理器丢失/重启、有已发控制但未知回复，消耗额度，不重发EXECUTE/ACK；同handle有限STATUS无新写；无authority则阻断|
|A14|同payload完整commit只读COMMITTED_IDENTIFIED不等于可新host观察；prepare代码即便所有files齐全仍产品grant0|
|A15|活原actor无论能否取锁都不能另启恢复actor；旧代次确证终止/全参与者归属齐全才允许actor2；陌生PID不能被杀|
|A16|原actor终止但未返回，终局记TERMINATED_WITHOUT_RETURN不CLOSED；新actor2逐一真实原返回，catalog保留两者和独立恢复接受|
|A17|旧actor实际晚返但非合格，actor2新身份/新资格重验证；不得把actor2的close当actor1的原返回|
|A18|终局资格齐全后当前payload/commit全缺席可专门CREATE_NEW同scope；完整payload+当前commit缺席只建commit。ENOENT不回填旧CREATE未执行；完整commit只重验。截断intent/其他对象、旧intent缺失却已提交、错内容/缺外部identity隔离，不覆盖删档|
|A19|actor2也UNKNOWN则停止，无actor3自动继任；原107218/三R三S/所有产物/原fence与oldCloseACKfalse完全不变|
|A20|H_actor先封存不含未来APK SHA；activation asset精确同head/catalog，外部activation-release绑定实际APK，不出现自指或修改已封存events|
|A21|activation asset错误head/旧scope/漏actor/错intent或commit、未知schema，产品创建0；受信完整包但当前guard/fence/ledger/pending/返回失败亦0|
|A22|正确最终catalog跨新host不查退休4869历史、不复用旧livegrant；每host真正持原guards、核全部合法ledger后缀及实际返回，结果只授本host|
|A23|身份phase返回后、EXECUTE未接受且无排队动作，互斥关闭写命令入口才可失败结束；晚到EXECUTE拒绝，无关资源取消0|

## F02 真实旧reader与实际部署门

已有冻结E5AFinalObservation源码在WRITER_DEATH调用旧history，metadata()检查旧档/ledger/fence，不读取legacy-acceptance、policy schema或revocation；E5AAdmission.require只识别旧恢复痕迹与进程内proof。新marker的存在不会被这段代码自动检测。此为真实源码直接审查，不是已在设备降级。原E6B MP4旧reader成功也不与当前history0矛盾。

后续基线测试必须加载冻结真实旧reader实现，以原有Platform替身提供合格旧死亡/guards/实际返回，在纯本机有界旧metadata夹具旁放入新policy/未知schema/撤销标志；记录它确实不消费这些新字段以及原路径的结果。此负面能力测试用于证明“不支持旧reader”是必要限制，绝不能为了测试让其结果伪称拒绝。禁止用一个认识新schema的新模拟器来替代旧类；不得读真实视频体，旧0B synthetic输出足够，所有写限本机测试夹具。

实际部署门实现后直接调用同一入口的文件核验、已安装身份核验与install dispatch wrapper，替身只代替平台查询/安装调用。至少覆盖：

|ID|实际边界断言|
|---|---|
|D01|旧E7A或更早真实reader忽略新marker的能力有真实旧类证据，报告限制；部署门在任何install前拒绝此旧SHA，不依赖history|
|D02|原签名但提高versionCode的旧代码、复制manifest gateABI、改文件名均因完整SHA不在批准集合拒绝；install计数0|
|D03|approved app配错test、角色PREPARE配ACTIVATION、签名/UID/package/descriptor/head错、源审核缺失，install0|
|D04|正确本机候选但已安装base.apk不同/版本不符/存在原actorUNKNOWN，install0；不能用install-r杀未知任务|
|D05|-d/卸载clear/data restore/换budget或手动绕过入口明确不支持；实际wrapper不会发这些命令，不冒称Android能挡住有权管理员|
|D06|正确阶段安装后核actual base.apk/组件/phase，不符不激活；versionCode或Success文本单独不足|
|D07|prepare产品入口及所有旧恢复/debug/public资源入口直接走phase gate；activation不含可写迁移路由，旧prepare test在新app下首写前拒绝|
|D08|撤销需新compatible release实现，旧程序不因外部新json自动变安全；升级前原业务真实返回，旧版本被移出allowlist|
|D09|受信后续compatible release携带同一H_actor但新部署记录合法；不能因不变历史事实日期旧而重新查4869，也不能接受当前已被替代scope|

已有E7A execute_managed.py中的包内SHA核验、版本/UID与安装后base.apk SHA检查是实际部署流程先例；新E8A full allowlist/phase gate尚未实现，不能把先例升级为新门已通过。

## 设计边界、成本与通过条件

已有E8账本六条hash事件/三R三S/107218reserved0及来源只读复核可继承不重读媒体；F01当前无运行actor，所有新身份/回执均占位。A01-A23共23组、D01-D09共9组是32组后续直接测试设计，不是执行PASS。旧V2重启/PID复用/全参与者/部分提交、同UID主动篡改保证限制等22组E8设计继续作为上层需求，不累计成已执行54组。

另需真实实现级核成本：device最多4文件8448B/3目录；外部20文件内容上界155648B、metadata192KiB+日志1MiB；2actor、各2个10s资格phase/最多8请求/STATUS3/holder48；两个未来双APK发布阶段。超限拒绝并留痕，不能静默加holder、权限、文件或恢复次数。所有数字是设计界，须真实调用计数和故障切点核定，不宣称实测。

设计独立通过后负责人另派集中实现；真正实现先自检/整包审查，prepare实机迁移与activation构建分别正式派发，不因设计支持自动执行。最终scope由可审实现/实际风险和既有授权决定，不现在请用户批准。E6B-OBS-F01仍OPEN、D1未过/M0未启，全P0/许可/原Kit框架保持。
