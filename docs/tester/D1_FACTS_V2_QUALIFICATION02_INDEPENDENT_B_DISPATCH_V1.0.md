# D1 FACTS_V2_QUALIFICATION02 正式独立整包B派发

2026-10-24；负责人核完整包后正式派发。本文件解除 D1_FACTS_V2_QUALIFICATION02_FIX_TESTER_REQUIREMENTS_V1.0.md 的“待完整冻结”条件，并与其合并作为独立整包验收要求。仅离线，不运行SDK/ADB/设备/Gradle/媒体/Git，不逐问题交接。

## 已核准确来源

候选 docs/coder/d1android02-facts-v2-qualification02；报告d9f520975d5d6fc63fe908c9268275fb1fd4814c763d4657ff2dcbe97c90b142；manifest783d4b6c280da96b03c55c06722d9855d839cfc5504cbc62b9c1f7714acd02b4；ZIPc5056a4a07acccead34b0dd68cc59a3830bceac2302b217d2a431581bc59167f。负责人实际核277项/13823627B及ZIP278唯一成员逐内容、大小、hash均bad0；tester仍独立复核。source30 93f75030768cbd32702451a806ebaa3d50287c0067ef5c7ed5c75c7942bf088c、gate22 2ad72384549c9d9e7d586848bd2a32e57d65ecb59cd983a1f143d3fa156ca819；profile504081cbb3a48049f2156916850e4c04ca181b243d5f5109f516da4ada069d28。plan原b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8。八组仅开发限定通过，不代独立验收。

## 独立整包重点

1. 按F01–F03/G01–G02和原160追踪逐项确认真实覆盖。01的43个变更接受模型不是43漏洞、no-op null合法、非受控异常和更早安全拒绝分层保留；独立核最终字段到底43而非44，不以计数文字错误推断删功能。核wire15字段与展开对象字段之间的完整映射，以及原未测12字段、完整版本路由、时钟和HOME/服务/仪器TOP规则。
2. 在精确新测试根的真正facts_entry→原collector→原Capture→FactsBundle正链执行合法最大raw139264B/128系统包，原stdout262144B不扩；核Base64唯一原raw及完整receipt/hash重建、越界前置受控拒绝。不得只引用coder当前根实测或用emitter替代完整正链。合法数据范围/原上限不因修复悄然缩小。
3. 在新根实际生成0/1/8/16/68及合法近界名称集合的资格，由原PS目标实际消费；核资格UTF8≤16384B、完整来源/窄授权不丢失。来源证据body8MiB/review2MiB是新表示独立边界，必须证明原来源预算内可承载全部既有合法范围，不能用这些数字替代原控制/管道上限。容量推导须对真正可达最大值与全局文本上限一致，字符数不代字节数。
4. 新引用协议逐字绑定review/candidate/bundle/outerReturn/preauth/policy/raw及准确source/scope/run/plan/nonce/clock。核实际PS与Python均从同一原文件句柄检查固定路径、根、非reparse、单硬链接、volume/fileId、原大小/hash、前后身份和原close。证据替换、错hash/字段删改、引用跨scope/根、陈旧/未来与不匹配批准准确拒绝，不接受只看hash字符串。不要通过真实挂死/故意close未知来注入失败；采用有界模型或可证明原归还的夹具并标清范围。
5. **合并预算**：检查 qualification_reference.ps1 的source计数如何与现有Gate/source ledger合并，真实生产调用方是否初始化baseSourceBytes/baseSourceReads、累计多次消费是否归同预算且不能调用重置/漏算；不以独立计数器局部未超额代全批上限。异常/短读/身份/hash拒绝的读取预留、实际计数及原资源保全逐项审查，不扩268435456B/64次生产门。新增Add-Type、Popen/.NET及文件句柄均纳全图，不操作旧对象。
6. 独立验证capture_origin登记的实际构造、Popen引用、启动、读/EOF/wait/原close/归还不可由__new__或pid-only模型替代；仍明确可信同进程宿主边界，不追求抵御任意内存修改。正常正链与变更反例并列，关键嵌套错误稳定受控拒绝，不能靠任何KeyError算准确门通过。
7. 原宿主持有已归还真实Capture，经独立有限reviewer进程完成未批准候选→准确回复→资格→原PS目标，在同一原300秒内；至少一条在新测试根真实执行。准确标OFFLINE合成独立夹具，不冒真人批准/设备事实。核超时/陈旧不刷新原collectedAt，原调用不重放；只使用既有最小交接，不另建服务或签名/IPC框架。
8. 原V1 346/45/17、preStart13及受影响生命周期/路径/原返回回归，最终Schema追踪和真实缺口集中记录；不为补总数要求无意义组合。旧01 132与tester209冻结保持，原FAIL/UNKNOWN不改。

## 执行与交付

仅写 docs/tester/D1_FACTS_V2_QUALIFICATION02_INDEPENDENT_B_EVIDENCE 及同名前缀报告/manifest；fixtures在其下唯一新scope，不写候选或旧允许根。先固定输入、独立驱动、完整过程图、读写预算。动态360秒/320秒停止新增，读取1GiB、产物16MiB、辅助96、并发1，SDK0/产品retry0；原生产时限/cap/once不扩。纯准备未入产品且无未知可留修订后集中修驱动，不逐错回交；遇真实UNKNOWN停止新增、不二close/kill/attach/补ACK退款。

整批报告须给各修复关闭/未关闭、容量实际生产消费、引用协议与原预算集成、实际新根/独立review正链、准确拒绝层、43/15字段及160追踪、原返回和完整manifest。完整交付后主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774(local)，通知失败保存回执不绕过；负责人收到完整结果后集中派下一批，不自动修复/重测/设备/Git。D1未通过/M0未启动；既定成熟框架精确版本许可、正式Flutter/独立Kit及全P0保持。