# QUALIFICATION07 REV2 独立整包B测试报告

2026-10-24。**PASS：准确REV2的本批离线功能簇独立通过，9组通过，无本批新增资源UNKNOWN。** 不代LIVE、完整七角色、设备或D1验收；D1未过/M0未启。开发REV1原FAIL、旧05返回未证及旧tester对象均不查询、修改或收尾。

## 来源、驱动与执行

按正式独立B单SHA256 `050eab4475e74819fc96d75aa28d216e2632a2726636079f63fc301527e2569a`执行。准确产品根为docs/coder/d1android02-facts-v2-qualification07/rev2。整包manifest `e9a275eba60347706fee8ed622350368b1fb0a87f6100c361297952f5a204e7f`，567项8138358B；ZIP `bd3d716c2e8a5cd928f52ef4e90c290c0af32b8b1226ce04cbdef8d11ae78def`，568唯一成员逐内容一致。前后567项bad0；冻结的613项测试源、输入及运行时前后无变化。

source30 `0db36468464dcfb92c2da87de8d6bff678b09af173bb21b41ed9e3d4d58157de`；gate22 `ba8fbd645e4c8403525c111ba2943cb81f3fbf6fbfc11a9f6d7c7c5a49026f81`。固定runtime helper原2056B/47f9及metadata2593、14依赖准确核对。完整schema原UTF8字节与fact_preauth中的内联全文一致，required派生及必要pin保留；source_budget的完整容量shape与参考值一致，size/admit函数AST与冻结06逻辑一致，没有缩减合法raw容量来适配预算。

仅在D1_FACTS_V2_QUALIFICATION07_INDEPENDENT_B_EVIDENCE及同名前缀报告输出。新scope系列fixtures/a78e225c；一次整批、各产品scope一次、无重试。测试顺序代码按REV2实际API派生为tester自己的worker.py；没有运行开发worker、REV1或修改产品来源。独立辅助脚本来自已审05A，重新绑定准确REV2来源/字段/符号/理由；实际调用与冻结tuple共用build_budget_spec。guard在Capture/Journal工厂之前准入，错误source、program、executable、cwd、env及额外参数均纯预检拒绝，Capture/Popen0。

冻结order SHA256 `71d0525e7b38054751cf7e2fe14cfac719327c42dcdc6b896d69b2bd2f59a90e`。父侧以本次原Popen句柄核worker身份，原对象wait、readers、流及handle仅正常归还一次；无PID发现、attach、kill或二close。先保存原exit/stdout/stderr/return，再检查辅助结果，避免缺文件掩盖原原因。

## 实际结果

|组|独立结果|关键证据|
|---|---|---|
|原Capture资格正/负/PS宿主|PASS|0/7/0退出及原返回|
|最大facts实际原入口|PASS|raw139264B、128包、packet193635B|
|独立有限OFFLINE review|PASS|三目标新scope，realHumanApproval=false|
|原生产identity/global正常链|PASS|原Runner→Gate→Owner→PS顶层，两角色PASS|
|原生产错固件|PASS|identity语义拒绝，无global后继|
|原receipt同字节物理替换|PASS|文件身份读前拒绝，内容read0B|
|独立18项辅助|PASS|18/18准确ID、理由、类型及原返回|
|当前V1回归|PASS|346/346|
|容量/非法prefix/构造边界模型|PASS|8项有限模型，未造真实UNKNOWN|

独立固定文件复核39项通过，其中包括8个结果解析有限文件模型的汇总核验；另有来源闭包14项通过。缺文件、重复JSON字段、未complete、布尔类型错误、ID顺序、authority标签和汇总不一致均准确拒绝；这些是tester结果接收器模型，不冒产品攻击实测。

## 缺陷关闭与实际账表

**子raw漏事件已关闭。** 新原facts 64行/64次/**8998997B**，逐scope/path/kind/index/chargedBytes与本批固定计划一致；阶段及owner在后续行一致，私有seed原事件未带可选阶段字段的部分，准确归属从同scope固定计划派生核对，不伪称原事件本就含全部字段。父raw与子raw分别收费，child-reservation与route-child-reservation各有一行。普通原文件read/close已返回；runtime16是固定helper预留并标fixedHelperReturned，子预留不能当作独立子句柄close实测。

**显式route自读义务已接入。** route_fixture真实自读由原父Gate在原Popen前永久预留，不能拿其他hash读抵消。完整schema并入已有必要源后source30/gate22维持原64门；本批RAW实际64，COMPLETE61、LIVE58仅按最终源码静态分支核算，没有运行LIVE或native route。

**共享producer pin已关闭。** 最终GICollector、factPlan、adapter、capture、origin具名摘要均匹配；29处可准确关联来源文件的产品字面消费点全部一致。Runner SOURCE_FILES、PS srcKeys与source30集合一致，Gate22逐hash及七项policy摘要准确。11个reference/实际内联PS函数逐段一致。共享GIQualificationExpanded02的collector校验在当前V1 346项和真正V2正常生产入口均获证，不只依赖manifest自洽。

|新目标|Gate字节/读|Runner字节/读|原永久ticket字节/读|pending|
|---|---:|---:|---:|---|
|positive|9155052 /64|9757232 /76|828608 /7|无|
|wrong-firmware|8599914 /46|9023624 /47|273496 /2|无|
|receipt-replace|8599918 /46|9023391 /47|273500 /2|保留|

独立按原费用事件+永久票据+有限probe费用逐项回算Gate/Runner计数与字节一致。正常ticket版本0→1，delta实际2+5读各合并一次；未用预留不退。正例在原claim保持期间实际将Gate读满64，第65次内容open前SOURCE_READ_BUDGET拒绝，下一角色预留亦读前拒绝。Runner256/512MiB及真实256MiB字节边界没有实际到达，辅助模型分列。

## 原receipt身份链

原writer→console五字段receiptRef→原controller wait/EOF/流/H返回→Owner通过Runner自己的原读句柄核volume/fileId/大小/前后身份/hash，正例两角色均独立核对一致：identity4323B、fileId281474980561175；global_idle4334B、fileId281474980561186；volumeId均1418466484。原内容SHA、console captureReceiptSha256和原reader引用一致，源delta经恢复视图后并回原权威。

正例额外经原reader测试错path、volume、fileId和SHA分层拒绝；错身份read0，错SHA须原内容读取后拒绝，所有原close返回且费用永久保留。

替换scope先保留原identity receipt，再同路径同bytes重建：4338B、SHA256 `121378694a4a5f323bb5cae111629487bbf1317493ad53b82af81f6b71b31244`保持，fileId **281474980561264→281474980561268**。原reader返回ORIGINAL_RECEIPT_FILE_IDENTITY，**内容read0B，原close返回**。无global后继，原claim归还；未merge的永久票据pending保留。此pending是已知拒绝后的费用记录，不是资源UNKNOWN，也不是字节被篡改或原归还伪造。

## 完整控制容量与辅助范围

本批permit/policy/activation/admission/request/proof/receipt/console/native及重复功能读、转发按原容量构造机制准入，independent evidenceRoot与home均纳入。正常共享预留250886B<262144；identity实际局部48796B≤预留64897B≤65536，global_idle实际36876B≤预留60781B≤65536；功能读取分别36879/23860B，均低于对应37230/33108B预留。原8192/65536/262144/1048576等局部/共享上限未扩。

7189字符独立证据根模型由同一完整admit函数拒绝CONTROL_ENVELOPE_CONTROLLER_65536:93574>65536，未物化，OS/完整资格可达性未证，不称真实溢出。非法prefix bool、float、0/1/3及非fixture prefix2在资源前拒绝。构造前已知拒绝/真正进入后UNKNOWN只做准确有限状态模型，没有人为挂死原调用。

18辅助涵盖缺base、类型、错scope、重复初始化、同原模块重载不清零、错hash/身份已计费且close、读前cap、拒绝后不退款、零预留、完整实际wire。全部明确syntheticAuthority=true/realAuthority=false；真正生产owner票据/delta另有上述原链证据，不能混为辅助的真实权威。

## 预算、归还和限制

动态worker **44.312秒**，原外层总计44.890秒，低于320秒停新增/360秒总窗；16个宿主Popen，audit16/16一致，facts内2、.NET4、worker1，冻结受控图实际23节点（条件上限25），并发1、retry0。新108个原文件事件全部close返回；各Gate、Runner、Owner原操作、writer、线程、原controller及外层句柄归还证明齐全，新custody全0、无新增观测UNKNOWN。父侧原证据读取16804198B/617次已正常关闭，另作独立宿主域记录。

预冻结分域来源预留512MiB<1GiB，包括facts32MiB、目标Gate64MiB、Runner96MiB、驱动/模型256MiB及准备64MiB；各原Gate/Runner的实际费用如上。不能把这些保守预留冒充全系统物理I/O总测量，解释器隐式加载及OS元数据未全量计量。全部交付产物低16MiB，以最终manifest/freeze数为准。

63/21/18历史oracle已逐ID保留来源hash并映射当前有限证据；不是宣称102项逐项重跑或全部通过，不做无意义笛卡尔组合。旧05数值路径不重放；原驱动A准备与本批实际结果分开。报告后不自动进入设备、Git或下一批。SDK/ADB/设备/native route/TCP/Gradle/媒体/Git均0，test_media未触及。

未执行：LIVE、完整七角色、真实设备、真实长路径资格、真实reparse/hardlink攻击、真实构造/close永久UNKNOWN、所有字节/次数极限的动态到界。开发REV1FAIL和全部旧对象/once/预算保持。后处理脚本一次因模型目录已存在停止，改为只复用本批结果解析模型目录后完成，未新增或重跑产品scope。

完整原始证据、post-audit.json、static-closure.json、oracle-trace.json及最终manifest保存在同名前缀证据根，集中交负责人审核后再派下一整批。
