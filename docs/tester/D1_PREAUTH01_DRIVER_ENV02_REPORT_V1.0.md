# PREAUTH01 DRIVER_ENV02 独立整包B复审报告 V1.0

2026-10-23；tester依据 `D1_PREAUTH01_DRIVER_ENV02_TESTER_REQUIREMENTS_V1.0.md` 正式执行。**PASS_IN_SCOPE_COMPLETE_OFFLINE_B：环境驱动资格和原定9组离线复审全部通过。** 未发现本批新增产品源码缺陷或资源UNKNOWN。此结论仅为准确冻结候选的限定离线B，不代表真实设备/资格V2/D1通过；D1未通过、M0未启动，后续不自动执行。

## 准确来源与保全

source20 `02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df`；gate12 `bdc8cba37c2157077ad3066709c4a4ca732f525746980521cbcc623203912192`；plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`。原56/472652B、开发108/3707218B及两原ZIP57/109成员、内容和hash前后全部匹配。旧失败报告和57项manifest `992c684578af2da658b7f1f3e179b7e5d6b79c0f8b36891c5788118e6ea37562` 仍bad0，不倒改其资格/runtime未执行结论。

开发曾误写旧result再恢复、旧进程图漏计1的历史保持。未运行开发错误worker main，未覆盖或再次恢复旧原件；此次独立driver只抽取明确惰性定义，独立新namespace与输出根。新证据 `D1_PREAUTH01_DRIVER_ENV02_EVIDENCE/v1`；实际fixture为原候选允许根下全新 `selfchecks/work/indb-17a969f7063e`，原失败scope未复用，未改产品白名单。

## ENV02资格与实际快照

本批允许最多两版资格修正，实际只用v1一版、一次资格阶段、三个程序，未使用第二版或资格重试。产品事务retry0；资格尝试次数独立记录，不将授权的迭代混作SDK重试。

raw Popen/audit保留creator的精确字典与四元组；child环境仅将键按Windows规则大写，值不变，大小写碰撞/重复键纯拒绝。env=None继承父实际环境与显式env分开；raw cwd=None与实际继承cwd也分开。7个环境/cwd模型、完整namespace缺项0、22准确tuple正例/88反例及22个原始Windows四元组模型通过；实际构造仍验证真实宿主上下文，没有放宽raw守卫。

worker在实际context检查前先保存原身份/nonce、actualCwd、键集、规范环境SHA及四个受控值hash，没有输出秘密值。实际cwd为新v1目录，键集恰为SYSTEMROOT/TEMP/TMP/WINDIR，规范SHA `4820d78af0910f70dae96e307a570bf7e35c4223d85078f079646f58e9ee69a5`，与预期及值hash逐项相同。creator的SystemRoot原大小写保留在Popen模型，审计也准确匹配。

| 真实资格 | exit | 原观察秒 | 原wait/readers/streams/H |
| --- | --- | --- | --- |
| Python0 | 0 | 0.063 | 全部返回 |
| Python7 | 7 | 0.063 | 全部返回，语义为已知非零 |
| PowerShell0 | 0 | 1.969 | 全部返回 |

三项自然小于5s且无stderr；资格完成后立即继续同一批原定B，没有中途停报或追加SDK/设备动作。所有资格共用同一个360/300/240预算起点。

## 九组实际结果

| 组 | 结果 | 秒 |
| --- | --- | --- |
| driver-qualification | PASS | 2.141 |
| developer-template-replay | PASS：138反例、1正例 | 0.047 |
| independent-two-layer-template | PASS：193条当前源语料 | 0.047 |
| current-source-346-semantics | PASS：98+175+73，含原45/17 | 7.484 |
| original-preStart13 | PASS | 1.500 |
| actual-original-V2-binding | PASS | 1.406 |
| actual-wrong-receiver-once | PASS | 0.938 |
| legacy-V1 | PASS | 1.000 |
| explicit-CLI-and-replay | PASS：7个实际入口 | 2.391 |

模板193条在本次worker中实际执行，191准确拒绝/2正例。固定旧批准hash的caller字段/pretty字节修改在PREAUTH_EXTERNAL_HASH拒绝；明确合成OFFLINE外批hash下的坏Schema/重复与大小写字段/源pin/严格预算类型/SDK设备/query/UTC和90s/policy身份则到各自准确内部原因，没有以hash统拒冒细项覆盖。根据负责人JSON契约澄清，批准pretty原字节的新hash可以接受，O1符合当前契约；旧192条与1观察按原记录保留，不累成386或重写历史。所有外批均合成OFFLINE，hash不证明批准人身份。

当前20源的346语义分四个≤1MiB输入实际交给原PS检查，全部expected/status/reason匹配，42条件正例，175独立集合中的17条件正例通过，原45映射包含在98集合中；这次是当前源实际验证，不继承旧17源A400。preStart13含真实创建未Start的唯一原收尾、纯未知状态模型和一个固定.NET Python真实Start及原wait/readers/dispose；没有制造真实未知。

同原PreparedFacts→原Gate→binding→原capture→finish/release实际通过。binding与原owner/thread/generation/claim file-id/route/proof/receipt/ticks对应；47个绑定/once边界包含prepare前、prepare重复、另一无资源Gate对象、真实错误线程、20字段删/null在原binding字节门拒绝、绑定重复、消费后及release重复。字段篡改明确到PREAUTH_BINDING_ONCE_BYTES，没有假称绕过该门测到更深守卫。另有4个当前事实wire坏头/尾/query输入，分别准确FACT_BEGIN/FACT_END_OR_DURATION/FACT_ORDER_OR_FRAME拒绝。

wrong-receiver独立新scope实际到PREAUTH_ORIGINAL_CAPTURE，receiveEntered已消耗；再次接收准确PREAUTH_BINDING_ONCE_BYTES，原claim唯一归还、sdkChildrenEntered0，没有退款/rearm。旧V1保持authority/approval字段，错误双hash链分别FACT_PRIOR_APPROVAL_HASH和FACT_EXTERNAL_APPROVAL_CHAIN，原capture重入FACT_ONCE；新V2只含authorizationKind/externalPreauthSha256/runtimeBindingSha256，不伪造legacy批准字段。

| 实际CLI | 结果 |
| --- | --- |
| 准确template/hash/canonical policy | exit0，V2事实、原释放合格，qualificationIssued=false |
| 跨进程同home重放 | exit2，PREAUTH_FRESH_OUTPUT_REQUIRED，未删除home |
| 默认/缺外部hash/额外动作 | 各exit2，准确argparse拒绝 |
| 非规范policy字节 | exit2，FACT_ENTRY_POLICY_CANONICAL_BYTES |
| 错误外部hash | exit2，PREAUTH_EXTERNAL_HASH |

正确CLI的内部2个构造及2个audit匹配，原collector/claim释放合格；本进程本身的真实退出由外层原Observer wait/readers/streams/H证明，未让CLI自证外层返回。七个CLI程序均有原返回回执。

## 完整原返回、写入与账本

原worker PID24944，creation FILETIME `134372383877788846`；自身argv/nonce与原H相符，worker/外层exit0。15份外层收集回执（资格3、语义4、preStart1、CLI7）全部原返回；原Gate/Fact内层按原对象回执与关闭标记核验，pending/custody均0。外层stdout85B/stderr0；worker17.484s、外层17.531s。无新增UNKNOWN，无kill/二close/补ACK。

实际完整图24，与预图24一致：worker内Popen20/audit20全匹配、CLI内部Popen2/audit2全匹配、PS.NET固定Python1、外层worker1。没有把只数Python hook当全图，没有漏.NET。额外动作/错误程序只做构造前模型或准确拒绝入口，不实际SDK。

| 原Gate范围 | source字节/读次 | control字节 |
| --- | --- | --- |
| 新V2原对象 | 8303441 / 45 | 20454 |
| wrong receiver | 8190682 / 43 | 17546 |
| legacy V1 | 8248145 / 36 | 11627 |
| 正确CLI | 8310239 / 49 | 20454 |

各自小于原256MiB/64读和262144局部control门；模板/policy、binding创建和receiver载荷沿原账计入。四个新claim都原unlock/close并无pending；同home重放在fresh-output门提前拒绝，未进入新的claim/capture。

全部启动/group/finally/异常写点预先固定，新driver在文件操作前检查新ENV02证据根或准确新fixture根；250项实际写操作记录均在允许根，固定DEVNULL例外仅位于准入Popen内部。CLI/PS子进程按固定源与预检输入写新根，其实际产物也在最终盘点内；未声称对所有原生子进程作全局IO hook。没有使用aux新目录，旧原件未改写。

预算outer360/worker300/240停新增、≤64完整图、2GiB/8192读、32MiB/2048项/单1MiB、单辅助≤90s保持；原产品90/30/15/10/SDK1、source/control与并发1/retry0未扩。静态总读预留2080374784B（1984MiB）；四Gate已知source合33052507B/173读，外层自有读取3105577B/40次，写根检查额外读保守上界11375592B仍在原driver预留内。读取有明示预留，完整解释器/PS物理IO未全局测量，不将source逻辑量称物理总量，不因未用额度退款。

## 验收边界与集中交付

qualification V2适配仍NOT_IMPLEMENTED/NOT_RUN；真实外部往返批准、HOME/服务政策、真实SDK/ADB/Native route/TCP/help/设备/Gradle/媒体/新依赖/Git/index均0。合成facts和语义条件通过不代真实平台/目标七角色或D1验收。原生产保守标记、旧FAIL/NOT_RUN/UNKNOWN/once/N2和所有账目保持，旧运行态查询0。test_media未使用或写入。

订单SHA `4b1e5fcb83086c7d0432708c6024d2492c83e52c38ae01f3dd44578e11789c38`。本批报告、v1实际snapshot/profile/input/全部原返回、来源前后核验、完整写图及新fixture原产物统一manifest冻结后一次发负责人；没有新建v2或第二次产品执行。后续准确范围由负责人另定，tester不自动现场或追加测试。**D1未通过、M0未启动。**

证据：[后验总核验](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_DRIVER_ENV02_EVIDENCE/post-audit.json)、[实际宿主快照](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_DRIVER_ENV02_EVIDENCE/v1/worker-self.json)、[九组原结果](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_DRIVER_ENV02_EVIDENCE/v1/worker-final.json)、[原外层返回](D:/CodexProjects/VideoKit/docs/tester/D1_PREAUTH01_DRIVER_ENV02_EVIDENCE/v1/outer-final.json)。

