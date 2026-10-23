# D1 PREAUTH01 独立整包 B 报告 V1.0

2026-10-23；tester完整集中回交。正式派发来源为负责人01a107c3-2bf9-7fa0-94a0-234258ca6774本轮消息及 `D1_PREAUTH01_INDEPENDENT_B_TESTER_REQUIREMENTS_V1.0.md`（SHA `ee13878755ca379545d9ad7db76486910730d1db8cd44b704899c17edc3daef7`）。原Git检查点等待条件已正式解除；本报告仅覆盖新PREAUTH01离线复审。

## 结论

**BLOCKED_TEST_DRIVER_HOST_CONTEXT_BEFORE_QUALIFICATION**。唯一实际批次在worker第一次实际宿主上下文复核时抛出 `PROFILE_HOST_ENV_CWD`，尚未进入辅助资格、产品PreparedFacts构造、Gate、claim或capture。独立整包B未完成，不能以开发7/7、旧A400或本次纯模型替代。没有新增确认产品源码缺陷或资源UNKNOWN，不自动重启或进入后续范围。

准备阶段当前20源上的193条模板对照全部匹配预定结果：191条准确拒绝、一个规范OFFLINE正例、一个已批准raw hash下非紧凑JSON的行为观察。验收口径为**192条有明确判据的纯检查 + 1条观察**，不能把最后一项写为“强制canonical模板拒绝已通过”。动态worker中的重复纯检查轮和所有产品原对象测试均NOT_RUN，不重复累计为386条。

## 准确冻结来源

| 输入 | SHA256 / 状态 |
| --- | --- |
| source20 | `02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df` |
| gate12 | `bdc8cba37c2157077ad3066709c4a4ca732f525746980521cbcc623203912192` |
| 原七角色plan | `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8` |
| 原BLOCKED报告 | `d170d1bffb784d78624bb753ed5fa341d17f503541f5b680ab6dbc9308bdd413`，原56项manifest `3ce81441d75e8a47368078197fcc43a20ace8eef916f1f3dcbd6f08c3cd8059c` |
| 开发SELFCHECK02报告 | `0a49494fc88b55050229c51e7bf918cac4fc79868c67ec1f02bcc401f3fc70d9`，原108项manifest `2c8c69d8ecec03d7bc339ae8bdb2349bdb942258f0c050b183197f1aa960fe61` |

前后原56项/472652B、开发108项/3707218B均bad0，两原ZIP SHA与57/109唯一成员和逐项内容匹配。20源/12gate及本次订单所有源、profile、输入hash均未变化。原候选 `evidence/result.json` 仍为 `d11659b55f31aa5bed06fbd76aff611da4b8588334f97d425dad2d052ce1fc10`。

开发期间误写旧result再从原ZIP恢复的历史及进程图漏计1保留；本次前后匹配不改写为开发期间从未变化。未运行其错误worker main，没有再次覆盖或恢复任何旧原件。

## 本批准备与覆盖

独立驱动位于 `D1_PREAUTH01_INDEPENDENT_B_EVIDENCE`。只抽取旧driver四个有限检查函数的惰性定义，全部写入改走本批save；产品原对象/CLI测试另写独立调用与收尾。没有执行旧worker顶层或finally。命名空间静态递归检查列出全部依赖，missing=[]，未再漏BACKEND类全局。

22组完整argv/executable/cwd/env/streams源pin纯正例通过，88个错误程序/多参/cwd/env模型准确拒绝，22个Windows原始四元组审计模型匹配。它们在纯预检中显式使用未来宿主上下文；**该建模漏掉Windows环境键归一化，不能代实际宿主上下文检查**。实际检查在任何内部Popen之前保守停止，audit没有回调抛错或I/O。

完整预图包含20个worker内Popen、CLI内部2个Popen、PS.NET固定Python Start1个以及外层worker1个，共24个；先前开发漏计的.NET子进程已列出程序、完整参数、来源pin和原返回判据。346语义输入（98原矩阵/175独立含17条件正例/73新集合）按当前20源重建并固定为四份，单份最大897505B，未因单文件限制扩大预算。语义宿主尚未运行，不能继承旧17源A为新20源已验收。

| 范围 | 实际结果 |
| --- | --- |
| 封闭模板、外部固定hash与内部合成hash分层 | 准备阶段纯验证192条明确判据通过、1条观察；下文限定 |
| Namespace/启动tuple/完整预图 | 静态PASS；真实宿主检查FAIL，资格未开始 |
| 三次成熟驱动资格 | NOT_RUN |
| 开发138模板重放 | NOT_RUN |
| 当前346语义、原45矩阵与17条件正例 | 输入已冻结；执行NOT_RUN |
| 原preStart13及PS.NET实际子进程 | NOT_RUN |
| 同原PreparedFacts/Gate/holder/file-id/route/proof/receipt/ticks/binding/once | NOT_RUN |
| wrong receiver消费后重入/原release | NOT_RUN |
| V2原capture/旧V1兼容/外层原返回 | NOT_RUN |
| CLI正确/默认/缺hash/额外动作/policy规范字节/错误hash/同home跨进程重放 | NOT_RUN |
| 旧56/108/两ZIP/20源/12gate前后核验 | PASS，原历史状态不回填 |

纯模板语料分别记录25条固定原批准hash的caller篡改拒绝、167条内部合成OFFLINE hash输入（含规范正例）及1条raw序列化观察。逐例expected/actual/reason、批准hash与输入hash在 `independent-template-model-evidence.json`。内部覆盖字段缺失、重复/大小写碰撞、非有限数、源pin、严格整数预算、固定SDK/设备/query、UTC/90秒和policy/scope/身份绑定；没有用外部hash拒绝冒每个内部细项。

**观察O1：模板raw字节规范化边界。** 沿用原外部hash改变成pretty JSON会在PREAUTH_EXTERNAL_HASH准确拒绝；明确合成批准pretty字节的hash后，当前validate接受同义非紧凑JSON。实现未强制模板只有一个canonical序列化。CONTRACT显式要求CLI policy字节规范化，该实际CLI路径本次NOT_RUN。若“canonical JSON”的需求也要求模板必须唯一规范字节，当前接受行为构成需负责人裁定的实现差距；本报告不把它作为canonical拒绝PASS，也不由此证明真实人员批准。所有输入均为OFFLINE合成，不运行正确LIVE模板或签名/来源鉴别。

## T-B01：独立driver实际宿主绑定失败

订单SHA `9565c9d10cd7848d1913b1bc48e345208bd09197949cad60dfee72135ad7de6c`；batch `3cc284cc4a1044cc811153b616553450`。预定fixture根为候选既定允许的 `selfchecks/work/indb-3cc284cc4a10`，最终从未创建，未改白名单。订单、原once、实际失败脚本和profile全部保留，没有修改后重跑。

worker在第123行预检所有计划调用时，driver_guard第43行实际cwd/env guard拒绝，尚未进入第一个group。外层传入环境键为SystemRoot/WINDIR/TEMP/TMP，profile以该混合大小写原字典计算 `inheritedEnvSha256`。本地CPython3.12的Lib/os.py明确在Windows将环境键upper()，因而SystemRoot在子进程os.environ中按SYSTEMROOT表示，原字典hash与此模型hash不相等。

这是足以导致失败的静态不兼容。失败时未保存子进程实际cwd/env键集/hash快照，不能补造完整实际环境或声称已逐项观察所有差异。原Popen构造参数和audit已保存；后验分析保留两种hash与本地os.py来源hash。

后续建议仅为**静态方案，未安装/未执行**：维持原Popen/audit原始四元组准确比较；另计算Windows键归一后的子进程上下文预期，检查大小写碰撞，并在新worker-self中先记录实际cwd、键集和hash供准入核验，再进入资格。不能把audit原字典和child os.environ混作同一序列化。新scope/新订单及实际资格仍需负责人另派，本批不自动续跑。

## 原返回、写入与预算

实际仅外层启动worker一次：PID31664，creation FILETIME `134372367886402614`；自身命令行/nonce和原H身份一致。worker exit1/0.438s，外层exit1/0.469s，stdout0B/stderr1014B。原wait、两reader join、流和原HANDLE唯一close均返回。没有创建任何qualification/PS/CLI内部子进程、产品Gate/claim/lease或产品once；释放N/A，不伪造产品abort-release。该结论由原回执、准确异常前缀、空collect产物及fixture根不存在共同支持，不只依靠工具退出或空custody。

所有启动/group/finally/异常目的已先列在write-destinations.json；独立driver对builtins.open/io.open/os.open/os.mkdir在操作前核R或新fixture根，只有已准入Popen的固定DEVNULL例外，process audit只观察。五个纯写根模型接受新根、拒绝旧evidence/开发根及保留名；因失败发生在group前，完整实际写入路由和子进程产物整合仍未验证。CLI/PS写点通过固定源码与输入根预检，未声称跨进程全局IO拦截已实测。新产物未使用aux等保留目录。

预算outer360/worker300/240停新增、并发1/retry0、最多64含PS.NET、读取2GiB/8192次、归档32MiB/2048项/单1MiB、单辅助观察≤90s均预存。静态读预留2080374784B（1984MiB）在2GiB内，含四套Gate原source cap、解释器/PS导入、模型和驱动归档；不是完整物理IO测量。原90/30/15/10、SDK1和各source/control字节门未扩。

实际外层记录读取3102717B/38次；worker因异常无最终账本，已达确定性self_io前缀重建3157919B/40次，另有解释器/产品模块只读导入，不冒称总物理IO。后验早期盘点53文件/3202207B、最大897505B；最终数和全部字节在独立冻结回执。实际图1/计划24，没有预算重arm、退款或重复ACK。

后验逐例证据生成曾因纯模型模块导入覆盖datetime绑定而触发断言；未写入错误逐例结果，原脚本及部分静态分析保留。单独post_audit_v2在函数定义导入后恢复显式模型时刻，通过validate的now输入生成193条证据。它不改系统时钟/产品guard/已冻结worker，不创建Gate/capture/once，不是功能场景重跑，记录在post-file-replay-error.json。

## 边界与集中交付

真实SDK/ADB/Native route/TCP/help/设备/Gradle/媒体/新依赖/Git/index均0；没有资格V2适配、真实HOME/服务政策、目标七角色或完整D1证明。旧运行态查询0，不kill/二close/补ACK退款，不改原FAIL/UNKNOWN/once/N2。test_media只读且未使用。

完整本批报告、准确源/输入/驱动/profile/预图、原返回、失败、193模型、前后核验和写根分析一并manifest冻结后发负责人。缺口集中回交，不逐问题联系coder。**D1未通过、M0未启动；tester停在本批，不自动测试新scope或进入现场。**

主要证据：[后验裁定](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_INDEPENDENT_B_EVIDENCE/post-audit.json)、[实际宿主分析](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_INDEPENDENT_B_EVIDENCE/host-context-case-analysis-v2.json)、[193条纯证据](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_INDEPENDENT_B_EVIDENCE/independent-template-model-evidence.json)、[验收口径](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_INDEPENDENT_B_EVIDENCE/scope-adjudication.json)、[原外层返回](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_INDEPENDENT_B_EVIDENCE/outer-final.json)。

