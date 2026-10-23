# FACTS V2资格阶段A：独立oracle与静态交接

2026-10-23。状态：STATIC_PREPARATION_COMPLETE；V2实现/验收矩阵全部PLANNED_NOT_RUN。本批只读已验收PREAUTH20与ENV02事实，不读取或运行正在开发的V2源码，不启动测试进程/Gate/claim/SDK。D1未通过/M0未启。

source20=02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df；gate12=bdc8cba37c2157077ad3066709c4a4ca732f525746980521cbcc623203912192。ENV02报告309a56d23173a04327af4b80da5b21332f845436ea1f4cf10887bb44755e66cd/184项manifest fd3b676a69da58aa52d1c86ae3073e8b627bf5e3559f46242a976aeb0b230cbc为已接受9组限定离线证据，原192例+1观察、失败及辅助恢复不改。

## 字段和独立验收规则

oracle-and-matrix.json列出建议闭字段、证据映射和160条计划用例。GLOBAL_IDLE_QUALIFICATION_V2名称按工作单；其他建议字段名须与开发冻结的一套Schema/字段表对齐后才执行B，不把建议当已实现接口。

facts V2不带完整plan/run/nonce，必须沿runtimeBinding和已批准preauth原字节交叉绑定。V1的factAuthoritySha256/factApprovalSha256不伪装填入V2；V2使用明确preauth/binding原hash、capture/outer原证据hash和target context。raw必须逐字节核sha/size，并重核固定七query、status/时序/设备；不能只信解析结果。

原外层返回必须关联原H身份、creation、image、准确argv/nonce及wait/readers/streams/H关闭记录；body返回、candidate导出、controllerReturned或空custody不是资格。UNKNOWN、非零或缺原返回一律阻断，不退款重arm。

review默认未批准；批准需要额外受信启动方给出的原review字节hash，绑定事实/outer证据、窄HOME/服务和准确target。hash只校验批准字节，不证明人员身份；issuer字符串和caller自算hash不能冒来源证明。本阶段不生成任何真实批准或资格。

唯一HOME须role/resolve/system package/UID/user/firmware相符。服务必须有明确外部review的准确process、唯一package、uid/user、APP/PERS、严格整数state、firmware、factScope、证据hash及EXACT_SNAPSHOT窗口；systemFlag、核心UID、OEM名不能自动批准。服务state2/3、竞争TOP与仪器优先拒绝，不能由服务白名单盖过；记录漏解析、decimal state或own字段缺失拒绝。服务最多68、systemPackages最多128，保留旧边界。

鲜度锚定原事实采集instant，不能因导出/review/签发重置。0<=now-collected，0<expires-collected<=300且now<expires；恰在采集时可用，299.999s可用需其他门，300s临界到期拒绝。未来、负窗口、逆序、浮点/布尔/字符串数值钟拒绝；expiry不得晚于原事实+300s。读原UTC字节/明确DateKind String，避免宿主JSON日期自动本地化冒原lexeme。

保留V1原45映射与17条件正例回归；另验V1/V2错配、V2混入legacy字段、候选未外批、raw/receipt/binding/outer/source/target错配、窄服务与时间边界。矩阵所有状态NOT_RUN；已有20源通过不签新适配通过。

## 未来真实交接：仅静态，未批准/执行

| 顺序 | 固定文件建议 | 执行门与预算 |
| --- | --- | --- |
| 0 冻结新候选/target | source/gate/plan manifest、target-context.json | 负责人审完整新包后另派B；当前不得读浮动实现或以共享HEAD定源 |
| 1 批准只读facts | facts-template.json、canonical capture-policy.json、外部准确template SHA | 新scope/nonce；原90/30/15/10/SDK1、并发1/retry0与固定七只读查询；没有安装/媒体许可 |
| 2 原收集与释放 | raw.stdout、fact-capture-v2.json、runtime-binding.json、gate/outer-original-return.json | 必须原wait/readers/streams/H/claim归还；原proof10/gate30不扩，不能在持有Gate时等人工补hash |
| 3 原返回后窄review | qualification-candidate.json、narrow-review.json、外部批准review SHA | candidate始终REQUIRES_REVIEW/approved=false；review核实际HOME和服务证据与target；人工时间仍消耗原300s鲜度 |
| 4 签发V2 | qualification-v2.json | 校验全部原hash/闭字段；expires<=原collected+300s，不自签issuer，未知或无外批即拒绝 |
| 5 原target鲜度/全局门 | target-context.json、原global_idle文本/接收结果 | 再核source/scope/run/plan、now<expiry、仪器/竞争TOP优先；过期拒绝，不延长、不重放旧scope |

实际文件名是静态建议，不生成可消费LIVE输入。如果人工review无法在300s内完成，应如实拒绝，由负责人另派新批准采集；不扩窗、不自动重采。离线合成正例须清楚fixture标记；真实资格、设备和目标七角色仍NOT_RUN。

## Git检查点

本阶段材料与已验收PREAUTH20、ENV02正确driver和必要失败/开发报告按精确白名单保存新WIP分支。排除浮动V2目录和工作单（仅保留本阶段PLANNED引用）、媒体/ZIP/rawbinary/第三方运行时/缓存/凭据/保留路径。原完整manifest保持，不承诺远端全量复现。本报告先冻结；commit/草稿PR事后结果另写DELIVERY避免自引用。新PR依赖#1，base为review/d1-contract03-offline-20261023-af2619b2，不合main/PR1，不自动下一B/现场。

