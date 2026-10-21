# D1 E13 设备部署与六方法执行附录 V1.0

日期：2026-10-18。REVIEW_ONLY，当前设备执行NOT_RUN。人类已给常规项目真机长期授权，未来按负责人具体正式设备批次执行，无需再问；先有限核其他项目占用，在用则稍后，不抢占。不因本附录存在派发ADB或真实scope/once。

## 身份与顺序

唯一设备候选HA1Q6WXR/TB138FC/API31/user0，现场不符停止。接受v15 ACTIVATION app SHA2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48、test SHAe644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb、signer5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f、UID10221/10222、原data inode6972/4741为源。目标v16与三APK实际pins见本包evidence/apk-delivery/apk-audit.json；早期/修正前APK仅历史，不得派发。

独立tester/sourceReview通过后，负责人另给同一scope的准确配置/release、原registry/head、目标/fixture实际hash、六方法与预算；新once必须e13-activation-deployment.once且在原registry外，CREATE_NEW。新E13HostActivationSession安装主app/test各install-r一次，再新装已证不存在的ordinary fixture一次；不降级、不回v14、不clear、不重装或复用旧once。任何失败/部分安装/未知停止，没有自动重试。

每方法独立host，E13 runner只接受精确class#method、e13Case、固定batch D1-E13-SOURCE-20261018、e13ScopeSha256四字段。每host保留@Before真实E9当前观察与原keeper归还门。一次按表顺序执行六项，不整类、不旧normal/迁移，不让多方法串在一个JUnit host内掩盖owner。

## F04：逐方法原对象与payload预算

| 精确方法 | 原Provider open上限 | 原read payload上限 | 原close实际调用上限 | 证据/原规则 |
|---|---:|---:|---:|---|
| ordinarySenderCannotBindCodec | 0 | 0 | 0 | 授权host HELLO、独立普通UID kernel bind拒绝；两原本地控制binding与fixture原target binding真实归还，非source close |
| authorizedHostSourceReadAndClose | 1 | 4096B | 1 | 原bridge open/read内容准确、排空/退役后runtime实际终止 |
| oldGenerationNeverOpensSource | 1 | 32B | 1 | 当前代真读；旧task/epoch/instance各拒，增量opens/reads/bytes=0 |
| twoConsumersHoldSourceUntilLastReturn | 2 | 48B | 2 | 同generation，先退一个不retire；另一个继续读取，最后才SourceReleased |
| cancelLateOpenRetainsOriginalOwner | 1 | 0 | 1 | 原open在途取消先响应，runner门false；原open迟到及其原handle close返回后才归还 |
| lateReadAndCloseFailureDoNotReleaseEarly | 1 | 48B | 2 | 16B先读+32B迟到原private buffer；一次明确close失败+一次原ticket重试；不发布迟到结果 |
| 合计 | 6≤8 | 4224B≤64KiB | 7≤16 | 每原ticket仍initial+最多2次明确失败后重试，pending不重叠；余量不授权新增动作 |

非媒体夹具是同一固定4096B字节定义，由每source host在本地内存生成，不传真实媒体、不扫test_media。五个source host各准备4096B（累计20KiB内存初始化）与4224B实际provider读取分栏；4096是单份fixture大小，不冒称全批只写内存4096B。每消费者独立原handle，双consumer共享generation；不是用重复对象/晚到结果代替原归还。每次bridge await原5000ms，fixture协调latch/Future观测也≤5000ms；方法30秒仅资格。记录cancelAtNs、responseAtNs、allOriginalsReturnedAtNs及原身份，取消响应不等完成。未返停止后继并保持原group/runtime/callback/ticket/许可。

## 48次PC操作及2MiB文本的整体分配

| 阶段 | 原操作数上限 | 具体构成与文本分配 |
|---|---:|---|
| 单次部署Java entry | 1 | 原supervisor entry；top日志≤32768B |
| 部署内部原process | 32 | 主pair制品检查5＋安装前当前检查7＋install2＋安装后检查7=21；原app/test数据身份前后各2=4；fixture badging/cert/原不存在/install/path/hash/UID=7。固定总32，wrapper提前拒第33次；合计原text≤524288B，每命令仍取原上限与剩余额较小值 |
| 六个E13HostCase原Java entry | 6 | 每entry top原输出≤81920B，含其原child转存/PC结束metadata；总491520B |
| 六个原am instrument child | 6 | 每项原supervisor GENERAL55秒/65536B上限，不是外部timeout杀任务；总393216B |
| 独立只读现场与收尾metadata | 3 | 占用/源身份/旧账档基线、部署后pair/data/fixture身份、全批后原账档/无在途；每份≤65536B，总196608B。正式tester将固定必要字段合并成三个精确只读客户端，禁止加全量日志/媒体扫描 |
| 总计 | 48 | 已分配1638400B；余458752B仅现有scope/index/原控制metadata记录，仍受2MiB整体门，不得追加process/方法/重跑 |

六case的top与child即使保存相同raw也分别算实际文本预算，不按阶段清零。PC scope/index/原客户端/原exit/两reader/唯一物理pcClosed全部留证。单操作原上限不因全批2MiB扩大。原supervisor96操作/128accept只是原机制硬上限，不授权超过本批48；本批计划socket STATUS/OP/CLEANUP连接查询0，意外未知没有“免费查询”额度。

三个独立metadata必须由tester在派单前写明精确字段和原输出上限。若原接口使三份不足、无法独立证明现场/保管/收尾，交预算缺口BLOCKED并由负责人修改正式范围，不能执行中补次数或省略关键证据。没有实际器件占用判断证据时不得开始。

## 终态与停止

成功必须六方法各原JUnit PASS、同scope/case的实际runner all-owner finish门、原PC/pipe自然归还、所有source/callback/控制binding原对象返回；将HALLO对照与source正对照分开。JUnit FAIL但原资源实际已返只记功能FAIL并停止，可正常PC收尾；PENDING/UNKNOWN不发finish证明、不让runner退出、不kill/force-stop、第二close、换UUID或新进程清理，不强行结束JUnit。

只注入可返回close错误与可控延迟，不主动永久UNKNOWN/真实OOM/重启/自杀/native信号。实际未知保原host、原Java/ADB Process和custodian，按同scope/task/epoch/instance/generation日志集中交负责人决定；本批不新建强制cleanup控制框架，不声称未知自动恢复成功。

全批媒体输出/READY/新R/S=0；接受账本214483B/7R7S/reserved0、旧107218B/1011B前缀、全部旧产物/fence/oldCloseACK=false保持。不得清账/重ABORT/迁移/读真实媒体来填证据。当前只是离线计划，不宣称现场账本刚重读。
