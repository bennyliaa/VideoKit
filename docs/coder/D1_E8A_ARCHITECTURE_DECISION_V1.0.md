# D1 E8A 架构决策 V1.0

2026-10-18。PROPOSED_DESIGN_REVISION；E8-F01/P1、E8-F02/P2仅提交修订，不自称已获独立关闭。旧E8/E7A不改。本批实现/构建/设备/媒体/迁移执行均0。

## 决策：外部登记，准备与激活分离

保留E8“精确一次性旧V1终局验收＋每host当前整链路”，但拒绝以device commit直接激活。新增迁移actor的authority放在现有负责人/tester可信管理流程的本机registry，不在它自己可写的device commit里。采用两阶段受信发布：准备版本只允许受管迁移、不允许产品例外；新actor全部实际返回并由外部独立归档正常结束后，才冻结最终验收包；后续激活版本将这个精确终局验收包及registry head摘要嵌入已审核的同签名APK。未来新host读取受信包内事实，核device绑定和自己的当前资源，再授本host liveproof。

这是一次旧V1例外的有限两阶段发布，不是永久在线管理服务，也不要求新的远端/硬件防回滚根。代价是后续至少两个独立构建交付阶段：prepare双APK一批，实证及独立审查后activation双APK一批；每批按一次主构建原则，不在同一已通过输入上凑重建。E8A本批不构建。此前仅两device文件的scope已废弃，完整新增清单见迁移计划。

## E8-F01 的封闭边界

首次应用目录mkdir/CREATE_NEW之前，新actor必须在外部registry预留并完成身份绑定：migrationID、actor ordinal/attempt UUID、受管handle、command sequence、旧task/policy/descriptor、prepare app/test精确SHA、actual UID/PID/process、已验证bootSource/starttime或独立审定具体内核/Binder绑定、参与者清单。没有可靠绑定/registry可用状态，不发写入命令；旧V1缺birth不适用于新actor。

actor自身日志或device intent只声称“谁计划做什么”，不是谁已归还。外部authority以准确handle+操作sequence实际响应及冻结代码/平台状态取得所有原holder返回，再核准确ACK和系统正常finish。commit正确但最后guard unlock后close UNKNOWN，registry必须保持QUARANTINED；另一个host能取锁也不能使它变成RETURN_VERIFIED。activation版本尚未产生，prepare版本硬阻断产品例外，因此这两种状态不能被同一commit混淆。

若原actor可靠终止而原Java返回未取到，不造closeACK。只有已登记单进程/无FD转交的原代次终止及全部参与者处置证据成立，外部才能批准一个不同的恢复actor对同一精确事务做有限完成或重验证；最终receipt必须显式保留旧actor TERMINATED_WITHOUT_RETURN，不能把它标RETURNED。新恢复actor自己的全部实际返回和正常finish仍必需。缺失identity/registry/可信终止、活UNKNOWN或不明FD谱系均阻断，不依赖任意删档/重启。

跨host“可激活”需要受信activation包固定的精确最终catalog：原actor明确终局（真实返回，或明确死亡后由合格继任者完成的独立接受）、无未处置actor、最后成功执行者实际归还/正常finish、descriptor/approval/commit/外部head一一绑定。只有COMMITTED_IDENTIFIED不是可激活；同payload幂等只读识别也不是资源证明。

## 无自身close证明回归

原应用迁移操作先实际完成/返回，外部管理器随后在应用UID之外保存返回证据并独立审定；它不让原actor再开文件来“证明自己的close”。最终receipt由受信发布构建固定进入activation APK，安装只能在外部确认所有旧actor已终局且无未知资源后执行。不存在要求写入一个新的device receipt后再证明它自己的close的循环。

管理器自身registry落盘也会失败：若write/flush/close/校验/独立封存不确定，则没有可发布的FINAL head，不能生成激活版本。它不把自己文件内的completed=true当唯一证据；本机可信管理者和独立来源绑定审证是既定合作信任边界。编译/签名/包身份核验是受信发布流程，不重新成为Android迁移actor。最终包一经审定，退休事实不因管理器后来离线而失效；未最终封存、未得到完整受信receipt时的失联必须阻断。

## E8-F02：只支持受管的兼容版本集合

不再声称旧E5AFinalObservation会因新文件自动拒绝。其生产源码未读取legacy-acceptance/new schema/revocation，只读旧history和旧档；当旧条件满足时它仍可能通过。当前history0不能充当版本门。

选择“受管部署禁用不兼容版本＋仅支持显式compat gate的后续版本”。实际部署入口必须验证独立批准的完整app/test SHA对、原签名、真实package/UID、单调版本、角色PREPARE或ACTIVATION、源审计过的gateABI及精确批准descriptor/final head；安装前检本机文件，安装后检实际base.apk和组件，不只看versionCode。相同签名的高version旧代码、伪gate声明、复制manifest标志、非批准APK对都不在SHA允许集合中。不得通过-d、卸载/clear、restore数据或换包身份绕过。

Android并不会自动禁止有签名/adb权限的管理员手动重打高version旧代码。若绕开受管入口这样安装，即超出本方案支持范围，不能宣称应用旧reader一定安全拒绝；要重新隔离并恢复已批准兼容包且核数据连续性。已有本机部署脚本确实核APK SHA和安装后base.apk，可作为可行流程先例，不等于E8A部署门已实现。后续测试必须针对实际旧reader和实际部署gate，而非另写认识新policy的模型。

## 保留的模型与事实

仍是可信签名代码/合作故障恢复；同UID主动篡改、root、自洽全套回滚不承诺被本地hash彻底抵抗。原跨UID/Binder角色、隔离参与者、原资源门不删。预算730a73e1-50e1-4198-a515-047104f00e31及三R三S：N2 ABORTED0、后续ABORTED53651、READY53567，共107218/reserved0；全部原档案/输出、oldCloseACK=false不变，旧birth不补。E7A实机只支持快完成/保留到ACK，UNKNOWN分支没有升级成实机通过。

长期准入E6B-OBS-F01仍OPEN；D1未过/M0未启，原P0与独立Kit框架不变。新host依然必须证明当前policy/精确档案/guard与fence/完整合法账本前缀及后缀/无pending及活UNKNOWN/本host所有原资源返回，受信历史receipt不能成为livegrant。
