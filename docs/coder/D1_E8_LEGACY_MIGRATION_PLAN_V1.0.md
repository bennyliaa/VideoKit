# D1 E8 旧V1迁移计划 V1.0

2026-10-17。DESIGN_ONLY/NOT_EXECUTED/NOT_PERMISSION。实施前必须独立设计评审、实现与静态/有限故障测试、准确设备派发；用户要求E8交付后暂停。本批没有可直接执行的迁移工具。

## 精确对象与保全

设备HA1Q6WXR/user0，原App UID10221，同原签名；budget730a73e1-50e1-4198-a515-047104f00e31，cap4194304/single2097152/records128不变。原files/e4a_output_budget及files/e4a_outputs不移动、不复制成新账户、不删除、不重新初始化。

旧task86cafdb3-0fc4-447d-920b-b19c884bf494/epoch5131975343750146374/gen1/service775a5ee9-fff3-4340-a03b-97751099c0c4；recovery目录N2-e5-recovery；旧lease a256356e-361b-47a0-b2e9-32dce4ccea8e，新ABORTED fence662e9ecd-bede-42e6-bb58-ce81d668ff44。原owner guard dev64522/inode20304/UID10221/0B、lease dev64522/inode20385/UID10221/36B，archive guard.identity82B；旧输出inode20386/0B。dev/inode均为既有证据，不是E8实时值；实施时不符即停，不更新预期来凑通过。

保留全部identity.before/journal.before/lease.before/ledger.before、recovery.owner、guard.identity、proof.txt、N2-e5-recovery.complete96B、operation.pending.N2-e5-aborted原dev64522/inode20492/0B以及现存task metadata。S0的chain1747c406b45987a8f4a3e8194bb170dfac92eb938d94ad2950bbb1f303ad4055、原R链6660cfb1b19dee6ced8fb9427d6605eb394ba9ecd9ab5931905a9a8727ffd026，原originalCloseACK=false不变。

也保留失败task0ee15550-8952-4639-91ac-83ab9d14d36c的53651B/生产SHA20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd与READY taskfbe4330b-111b-4b05-a93c-467413eb8d34的53567B/SHA6877567a65c7811131fe38d17bb642fa906bcb0c10fa38c3ba636c70dcaafb5e及全部元数据。三条R/三条S必须唯一且有序，消费107218不减，reserved0。迁移控制记录不作为新输出R/S、不扣除/抵消原消费；新增控制元数据须另计小额磁盘预算，不能借此无限扩张。

## 批准包与不可逆语义

建议policyID=D1-E8-LEGACY-N2-TERMINAL-ACCEPTANCE-V1，作用范围仅上述budget/task/attempt。实施版本应将独立审定的规范验收payload SHA和原ledger1011B完整前缀SHA、原archive清单摘要及批准ID固定在受信代码中，不能由设备文件自己挑选任意“已批准”的hash。将本批evidence矩阵中的真实来源作为审批依据；批准ID/人员/时刻在最终批准后填写，E8没有生成批准token。

拟新增文件仅files/e4a_output_budget/legacy-acceptance/n2-v1.acceptance（规范payload，≤4096B）及n2-v1.commit（固定≤256B，引用payloadSHA/policyID）。目录CREATE_NEW；已有一致已提交记录仅做只读识别，不改写；已有部分/不同记录一律阻断。禁新增绕过通用allow/ignoreWriterDeath标志。文件记录的语义是“终局验收策略已选定并提交”，绝不声称写该文件的最后一次close/fsync已返回。

不可逆变化是批准将旧任务身份永久标为终局退休，新的兼容代码不再通过反复旧writer历史查询决定它能否被再次结算。原数据本身不变。以后回退不认识该记录的旧版本只能安全阻断；不能删除迁移文件后当全新现场或重新跑原ABORT。若要撤销管理验收，需要新显式policy/revocation阻断而非恢复WRITING；不得逆向消费。审批应明确这项语义、仍未证明旧kernel birth、合作模型假设、实际写入两小文件及目录、保留范围、失败隔离和升级/回退行为。负责人如判断需人类一次性不可逆批准，提交这个具体包后再处理，不先执行。

批准摘要绑定不得循环：先冻结不含批准回执自身hash的proposal descriptor，取得descriptorSHA；批准回执引用该SHA及精确scope，得到approvalSHA；最终受信实现固定descriptorSHA+approvalSHA的有序manifest摘要，设备payload引用这两者。批准回执不再反指最终manifest摘要，任何后改proposal都使批准失配。E8只交未批准proposal，不填写批准者或生成许可；device commit也不能自签成为批准来源。

## 实施阶段与返回证明

1. 实现前审查：取得完整已有历史回执、冻结代码和外部批准来源，独立确认原ABORTED_SETTLED确实在所有原holder/目录返回之后产生；旧V1 birth标NOT_RECORDED，终局验收不是补造死亡证明。证据不充分时停在DESIGN/ISOLATED，不进入下面阶段。
2. 正式设备派发才允许预检。确认无未归档instrumentation、当前原任务/旧holder/worker仍在途，无未知live source/slot/FD；当前相关进程识别采用精确任务绑定和可访问的现有进程事实，不能“所有同UID进程都死”或仅PID不存在。任何活UNKNOWN必须等待其真实返回或取得独立实际死亡及所有远端参与者处置证据，批准不能代替。E7A已结束仅作既有快路径事实，实施前仍须新预检。
3. 在原holder登记前置下打开既有owner/lease guard，不CREATE/TRUNC/替换；lstat/fstat/noFollow/角色UID/精确dev+inode/fence并实际flock。再打开既有ledger的实际排他锁；固定顺序owner→lease→ledger，不能与生产反向持锁。匹配原归档、完整ledger及107218下界，活动pending不存在；不读真实视频体作为本批设计论证。正式实施若输出hash属必要验证，须在新设备计划中另列精确字节/权限，不暗中扩大。
4. 当前快照与历史验收payload一致后，CREATE_NEW写acceptance，原文件force/实际close、同步目录并读回；写commit、force/close/目录同步、读回。全过程受原guard排他保护，无新媒体reservation/无R/S/fence变化。所有metadata/lock/directory原holder保留到真实返回；不能只因commit存在就宣称整个迁移任务完成。
5. 当前迁移owner所有实际操作返回才可限内出成功live receipt；采用E7A验证过的受管finish原则，不用JUnit失败结束未知操作。10秒等既定资格若沿用须独立制定预算，不默认扩到本设计；超时永久PENDING不变成功。最后guard unlock/close失败仍UNKNOWN，即使锁可再获取也不能伪ACK；活未知owner阻断。
6. 下个独立新host只验证此精确已提交policy及不可变档案，执行所有当前guard/fence/ledger/无pending/实际资源返回门，给本host live grant；不查询已退休4869的历史，不消费旧liveproof。随后正常AVI/能力/cancel仍按新的完整正式计划分别派发，迁移成功不自动运行它们。

## 部分提交、幂等与隔离

同已批准payload的COMMITTED识别是只读幂等，不再次写、不重结算、不重发grant。相同payload但prepare-only/commit损坏/不同payload/多份commit/未知版本均STOP；不能先清目录再重试。进程在commit前后死亡，旧原closeACK仍不能补成true；原进程及远端参与者已被可信证明死亡后，可由新恢复owner在原guard下对相同已批准payload进行专门“完成政策提交”操作，完整重验账本、fresh force/close/readback，发新owner自己的实际返回证明。它不是重跑ABORT，也不新增S；需单独一次性派发，不自动恢复。

活owner的allocate/close UNKNOWN不得以重启/force-stop清理换资格。若历史回执或当前绑定不符，则只登记外部ISOLATED_LEGACY_N2及原账户阻断，保留目录/产物/107218消费；不搬走档案骗代码“不存在”，不换budget继续。可能的独立外证是原可信报告的完整调用/退出/资源返回来源、受管原操作自然收尾、精确进程代次死亡及参与者归属；不是再强求已未采集的旧boot字段。若提出人工终止活未知进程或其他破坏性隔离，必须另列准确PID/代次/FD与输出、不可逆影响和批准，不包含在推荐的无删除迁移中。
