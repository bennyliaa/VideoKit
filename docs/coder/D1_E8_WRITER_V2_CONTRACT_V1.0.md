# D1 E8 writer V2 生命周期契约 V1.0

2026-10-17。设计契约，未实现/未构建/未执行。适用未来新writer，不把旧V1补成V2；独立Kit框架、原资源/预算协议不替换。

## 身份与事前采样

在任何恢复业务写、FD转交、源/CPU/encoder创建前，登记actor attempt UUID、UID/process/角色、task/epoch/generation/service instance/budget、原guard dev+inode与fence、操作序号；身份还要有同一次系统boot标识和该进程kernel starttime。候选公开可访问来源是/proc/sys/kernel/random/boot_id与/proc/self/stat字段22的starttime；解析stat不能按空格粗切，comm可能含空格或括号。starttime是boot内ticks，不拿墙钟began或PID代替，也不需要转换为墙钟进行唯一性判断。

必须在目标API31/OEM上用正式有界元数据计划验证读取权限/格式/重复一致性（本批未验证）。事前对self采两次bootID/PID/starttime并要求一致；跨进程由实际Binder caller UID/PID绑定nonce挑战、目标self采样及可信内核视图一致核对，不信任调用者自报PID，isolated UID可变需记录实际UID。不可读取/不一致时在业务资源创建之前失败关闭，不退回墙钟猜测。若boot_id不可用，可评估受支持的boot计数+同机来源作为独立适配方案，但不得未经审查将普通app可改值冒充boot身份。

具体兼容候选为Settings.Global.BOOT_COUNT（本机既有android-36 SDK通过只读javap确认公开常量存在，无编译）；用只读resolver取系统值、拒绝缺值/负值，同来源双采样。此检查只证明SDK符号存在，不证明原API31平板权限、OEM递增或数据恢复语义。identity必须固定bootSourceKind=KERNEL_BOOT_ID或SYSTEM_BOOT_COUNT，禁止运行中切换或混比；计数来源还绑定原安装/设备域，系统设置还原或域不明按不确定处理。正式适配验证选择可用来源后才启用新恢复writer，不让未实现V2采样成为已退休旧V1日常播放的永久前置步骤。

FD/共享内存传递前必须先登记接收参与者身份及具体owner/lease关联，实际ACK才算完成转交；未ACK的传输保持UNKNOWN。host、codec、isolated CPU及任何持FD后代都有独立生命周期记录，不能只证明host死就当全部远端source/slot/FD已回收。仍使用原强持有者/CONTROL in-flight/真实callbackACK/原close返回机制；无新“统一释放计数”捷径。

## 三类事实及状态

|事实|可否持久及语义|新host职责|
|---|---|---|
|不可变身份、已验证终局S、内容承诺、fence变更、已接受历史返回/死亡事实|可。严格绑定来源/任务/版本，不声称当前liveproof|核记录/绑定/合法前缀未变，不永久重问有限history|
|ACTIVE/PREPARED/COMMITTING/资源UNKNOWN|可持久为“不得自动放行”的意图或不确定状态；不是完成|重新识别原代次/参与者，活或未知则隔离；不可清pending|
|本host已持锁、当前文件及原holder真实返回、live grant|仅本次操作实际证据；不能序列化当下次许可|每次重新获得和真实返回，不用旧报告代替|

业务writer状态NEW→IDENTIFIED→ACTIVE→QUIESCING→TERMINAL_STATE→RETURNED→RETIRED；任何关键调用未知转QUARANTINED，时间资格PENDING不随迟到回返变PASS。TERMINAL_STATE只表示业务状态已持久，RETURNED需原业务FD/worker/slot/控制调用/目录屏障实际返回；RETIRED是这些既有事实已被可信协议接受，可作长期历史事实，不是一个仍需无限重证死亡的活writer。

任何数据文件都不能包含“写我自身最后close已经返回”的自证。业务close事实先由原owner实际完成并通过既有可信回执传出，再由终局记录发布者登记；发布者自身文件/目录/guard的真实返回由它自己的live操作证明。若发布者提交到一半或其最后guard close UNKNOWN，其元数据事务保持不确定，不给活任务伪ACK。新host只可在识别原发布者已实际返回或精确原代次已终止、所有参与者安全处置后，以自己fresh操作重新验证/完成已批准同一事务；不能把文件存在当旧close，也不要求永远证明所有已退休发布者的历史退出。

需要实现审查明确区分“旧业务资源仍未知”和“元数据发布最终持久性未知”。前者保持阻断直到原真实返回，或经可靠原代次终止及全参与者隔离的独立恢复；死亡是能力终止，不回填原closeACK或重新释放活进程的计数。后者可在确证无活原写入者后，对完整不可变数据进行fresh force/close/目录同步及读回，建立当前owner证明；这不是宣称旧force成功。全局合作guard获取不能独自证明旧close，因为unlock可先于close。

## 原代次识别与永久事实

同boot且/proc/PID starttime相同表示原进程仍在，不能因exit历史有相同PID就认死；不同starttime表示PID已由别的进程使用，原代次已结束，但不要杀新进程。bootID可信变化表示旧boot进程不能继续执行，仍不声称旧操作close成功。ENOENT在可靠boot视图及当前查询完整返回下是当前不存在，遇权限/格式错误均UNKNOWN。需双采样boot前后并重核task/guard绑定，防跨boot采样撕裂；death断言与关键信任来源一起归档。

只有ACTIVE/不确定操作在恢复时需要识别其精确代次及参与者。系统exit历史可作原因/状态辅助诊断，不能作为唯一永久恢复依据；已采集start/boot可以让后来PID复用与重启成为可判定事件。已实际返回并退休的业务writer无需每host重复查死，retired记录也不重新开启同任务。原因UNKNOWN不自动放行业务，只是原因证据缺失与当前代次终止分开；不能把V1旧壁钟规则偷偷套为V2。

隔离进程的/proc视图可能受限制，不假定同UID host能读取所有isolated PID。另一个可实现路径是事前绑定实际跨进程Binder实例/nonce/角色，在业务FD转交前注册并强保留linkToDeath；原框架已有真实DeathRecipient链路，可对准确对象的系统死亡回调及来源做一次接受并持久登记。普通onServiceDisconnected、ping失败、超时或新service实例不能冒充该回调。回调丢失且同boot/proc不可读时仍UNKNOWN，不退回历史查询猜测；可等待已有原owner实际收尾，或由独立可信进程生命周期来源做正式处置。完整实现必须验证这个适配路径并覆盖参与者谱系，E8没有将其算作已实现。

## 持久编码与提交约束

未来独立版本的canonical记录需固定schema/policy/attempt/task/budget/boot/start/参与者/序号/父摘要/终局语义，严格长度与字段白名单、唯一规范编码、无重复键、无隐式缺省。按每actor身份≤4096B、终局包≤16384B、单任务参与者≤16、总控制元数据≤256KiB提出初始上界，最终结合真实框架约束审定；不扩原128输出记录上限。旧V1迁移policy单独版本，不通用转型。

意图CREATE_NEW→完整payload force/close→目录同步→精确commit引用→force/close→目录同步→同锁读回，所有FD在open前登记，固定锁顺序。出现重复/不同payload/缺父/截断/部分rename/未知schema即失败关闭。单实例重入、跨host同attempt、相同已提交回放只能识别历史终局，不重执行、不发旧grant；新操作必须新attempt并明确父状态。当前账本须包含全部已接受前缀并合法追加；不得让旧checkpoint拒绝所有未来合法扩展。

hash链校验检测随机损坏/错绑定和部分修改，不等于同UID攻击防回滚。合作协议只能追加且不删除；预留与消费始终保留。用户恢复旧数据/应用回退/备份迁移需显式兼容策略，未知schema或计数倒退即隔离；sameUID恶意者回滚整套自洽已签政策之后的新消费并不总能由本地检测，记录这一限制。需要更强保证时由独立远端/硬件单调锚评估，不伪称现有文件已经实现。

## 实际结束与成本

不因JUnit结束、进程退出、future取消、slot计数归零或deadline到期造closeACK。原E7A受管任务/handle/精确归档ACK模式作为诊断控制的已证快路径参考，UNKNOWN故障分支仍需真实实现级注入/设备证据，不能直接宣称全覆盖。产品既有60秒方法/首次取消30秒/源8192readAt与64MiB/单输出2MiB/摘要成本等不在此设计扩大。

每host：一次限长政策/元数据读取、有限当前参与者/proc采样、原guard/账本锁和原当前返回门；退休writer history查询0次，不对全部旧视频重新解码，不无限轮询。不活动actor的重核可按当前事务清单有界处理；超出上界拒绝并外部审查，不能扫描全盘或清旧记录降成本。新host观察成本与媒体播放验证成本分开计账。
