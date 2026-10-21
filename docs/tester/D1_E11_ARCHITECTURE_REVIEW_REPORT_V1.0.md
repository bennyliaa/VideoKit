# D1 E11 架构与最终整包独立静态复审报告 V1.0

日期：2026-10-18。依据：docs/milestones/D1_E11_TESTER_REQUIREMENTS_V1.0.md，以及负责人正式派发的 E11 基础候选与 R1 最终覆盖规则。角色：tester。

**结论：PASS_STATIC_LOCAL_FINAL_R1_CANDIDATE_REVIEW。** 最终 R1 候选的源码边界、真实终局来源、制品与冻结包一致性、一次离线构建及有限本机验证证据符合本次静态复审范围，未发现阻断候选准备交付的问题。可供负责人考虑另行具体设备派单；本报告不授权安装、激活或播放，不签发 release，不认定真机回归通过。D1 NOT_PASSED、M0 NOT_STARTED、长期准入 OPEN、全部 P0/许可及历史结论保持。

## 交付范围与方法

审阅基础 E11 的 DELIVERY、ARCHITECTURE_AND_THREAT_BOUNDARY、REMAINING_GATE_REVIEW、DEVICE_EXECUTION_APPENDIX 四文档，及同名 R1 最终四文档和 D1_E11_HANDOFF_REPORT_V1.0.md。基础375项与其旧JAR保持历史封存；最终部署必须使用 R1 工具及八字段配置，不能使用基础旧JAR。HANDOFF为包外汇总，已独立记录输入pin。

未执行候选的构建、自检、生产JAR、设备工具或媒体用例。独立读取并重算1351项本机输入，核两个ZIP的精确清单/字节、各层seal、源码、原测试/构建/签名日志及class/APK内容；本批仅运行测试侧文件审计脚本。

| 固定对象 | 实际字节 | SHA256 |
| --- | ---: | --- |
| 最终完整ZIP | 24845592 | 0fdc6d9439d48819608d83fd46234f27846ac852d726a614dbeec3103d22fafc |
| 最终R1外seal | 13989 | 2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3 |
| 最终 e11-host-tools-final.jar | 279793 | adb7b384ed305c925be7b2a670f33063e8d4309e085f1a6b7950f4b7125ebc27 |
| v15 app-debug.apk | 10659394 | 2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48 |
| v15 androidTest.apk | 2751249 | e644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb |

最终65项、基础375项及旧E10A463项原pin均匹配；最终ZIP包含完整基础source ZIP及其seal、R1源码/日志/最终JAR/绑定和四文档，未修改原冻结内容。实际最终JAR路径：docs/coder/d1e11/revision-r1/e11-host-tools-final.jar。

## 主要审查结果

**真实终局与授权分离：通过。** 接受的终局补审报告SHA a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff、688原输入及217项原执行manifest精确匹配。旧补审manifest实际非零文件由真实SHA绑定；其声明排除的0B self占位只作为历史占位明确排除，其余原行核验，不伪称实际manifest是0B，也未改原文件。

原registry的13文件与导出前原记录及新snapshot逐项相同；已存在的5853B catalog原字节、类型、四事件DAG、head、checkpoint/seal及原actor/reserve/return/finish均匹配。catalog SHA27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7，head6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5，准确M4f21f71a-bf66-4a44-a287-320f0ae25fde。导出调用只读原终局，NEW目录存输出，不append原release/events/head、不重SEAL；原READ_WRITE打开方式不等于追加内容，未新增访问时间或任意掉电持久性承诺。

旧trust.authorization/review仅为N2迁移历史来源；新sourceReview、deploymentDispatch、approvedRelease、当前device proof及两normal receipt均为空或模板占位。APK在构建后才以实际SHA进入独立绑定，不嵌自身hash、没有授权自指。SHA用于绑定真实输入，不能认证人类身份或实时撤销；当时有效的新部署批准仍由受信执行者独立核实。

**当前观察与grant：通过静态及本机替身范围。** E9Phase由源码固定catalog digest/head/environment产生E9Catalog.Trusted，实际APK DEX中的完整catalog Base64与原字节匹配。普通E9Record、自选digest、磁盘commit或normal receipt声明不等于实时准入。

E9Runtime/E9CurrentObservation每次先撤销旧grant，并核当前idle、准确原owner/lease/fence、13metadata、完整ledger的1011B接受前缀及合法settled后缀、无pending、精确控制目录/intent/acceptance/commit。最后原holder真实返回并退出ACTIVE后，才可在一致epoch发布grant。并发epoch先于class锁失效；重复、失败与被后续观察取代均不发布旧grant。已知失败且全返可移出ACTIVE并结束失败，UNKNOWN/在途保留原对象，不第二close、不发grant。

**入口与runner：通过明确范围。** 新runner只接收精确MP4、AVI、能力拒绝、条件cancel四方法；拒整类、旧迁移及额外死亡/隔离故障选择，每case保留原@Before真实当前观察。ACTIVATION下E9AndroidIdentity构造、事务commit首写及主机PREPARE manager均在相应首个身份/写入/配置或设备调用前拒绝；新test manifest只注册E11 runner。

runner在finish/onException先撤销grant；当前观察、原Session、encoder slot及旧操作任一未返即阻止platform finish。实际所用lifetime门及新Gradle app公开入口有本机验证，runner钩子有源码/编译证据；**实际Android runner UNKNOWN结束行为未执行**，不认定真机安全结束已证。

**normal回执：结构/次序边界通过。** AVI要求当前scope的MP4回执；能力及cancel要求两份不同report SHA和outputTask，均绑定本scope、实际pair、v15/ACTIVATION、catalog/batch/case及READY/6 received/6 input/6 output/fullEOF/PTS1000us/ownersReturned。双回执连接保留canonical尾LF再计算索引，不是第三份报告。选择器只核声明结构、绑定和次序，不认证外部报告来源，不发grant；外部tester/负责人仍须独立接受实际normal原证据。能力先于条件cancel等派单条件由受信批次流程维持，不能把选择通过当完整授权。当前两真实normal回执不存在。

## R1一次派发及未知状态

**原detached部署跨JVM重放弱点：CLOSED_STATIC_LOCAL_R1。** 不能仅依赖同进程dispatch counter。最终R1在任何安装前，原supervisor强持有E11DeploymentOnce原holder，执行固定路径CREATE_NEW→写精确意图→force→readback→原close返回，全部通过才进入原artifact/source/ABI/UID/idle/严格升版/同签名两install-r门。未知或部分安装消费原派发，不自动重试。

部署配置精确多出dispatchRecord绝对路径并由config原SHA绑定，固定文件名activation-deployment.once、父目录预存在、全路径无symlink、位于原final registry之外。复制同一config/release仍指同记录，换路径会改变配置SHA，不能作为自动恢复；未来真实派单还须明确采纳该新主机控制文件。新工具部署缺字段拒，旧基础工具不接受新八字段配置，防止混用。

原记录即使部分存在也拒，不删不覆盖。FileAlreadyExists竞态明确无FD，可已知失败安全结束；其余UNKNOWN或原close未证不派发、保留原keeper。记录状态RESERVED_OUTCOME_NOT_ASSUMED不证明批准、部署成功或资源归还；文件force/readback也不新增Windows目录项在任意掉电模型下的保证。

最终JAR163个生产class：159个与基础160类逐字节相同，替换E9HostActivationSession并新增E11DeploymentOnce/Cut/IO三类；四项与实际R1编译class匹配，无OnceCheck/E11ProductionCheck/E11PublicEntryCheck夹具类。

八次原本机合成JVM检查的原命令、结果和日志与汇总匹配，覆盖首用/新进程重放、两并发仅一份成功、force失败后重放拒绝、close UNKNOWN原custodian保留及另JVM重放拒绝。它们运行实际Once生产类，但不是实际安装器/设备运行；UNKNOWN专用夹具的控制器收尾保留originalCloseAck=false，不能算生产资源原归还。

## 测试与构建证据范围

| 既有证据 | 核验结果 | 限制 |
| --- | --- | --- |
| 12组最终映射154断言、13次调用 | 原stdout/stderr pin及断言数匹配，源码检查覆盖parser、selector、deployment、当前观察各分支、router和export往返 | Windows UID/inode/fsync/部署Port替身；未重跑旧套件/native |
| 14项SDK公开门断言 | 实际新Gradle app class及SDK输入pin、原日志匹配 | SDK stub，不是Android运行；runner钩子仅静态/编译和所用lifetime门 |
| R1八次跨JVM检查 | 实际Once class、原结果/日志匹配 | 合成本机记录，无实际安装器或ADB |
| 一次main-001离线双APK构建 | 原exit0和BUILD SUCCESSFUL、166项精确输入匹配 | 本复审没有构建或执行候选 |

166输入snapshot SHA c136acbd8730cdbb545c960e55234f66bc5d5310fcaca6cb850c669756c8de9e。后补host router/exporter/R1未改变这些Android输入或APK，未第二次Gradle构建。两APK直接解析v2签名块证书SHA均为原5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；密码签名验证依据已封apksigner原通过日志，本复审未重跑签名工具。

7个APK native库逐项与原上游字节/hash相同，35项Maven锁和严格六帧/fullEOF/1000us及框架关键源码保持。FFmpeg/Media3及原许可P0不因依赖未变而获得清除。

测试侧独立文件审计首次因过宽的类名Check过滤，误拒生产CheckedFrame；原脚本/exit1/stdout/stderr保留。仅修正明确夹具类前缀后，第二次文件审计exit0、原进程与两pipe返回。候选、旧封存内容未改，未重跑候选测试；此项不是候选缺陷，记录在tester-correction-01.json。

## 集中问题、关闭范围与后续门

- E11-RVW-01：detached跨进程重放弱点由R1持久一次记录关闭，关闭范围为源码和八次本机合成验证，实际设备部署仍NOT_RUN。
- E11-RVW-02：历史catalog与当前proof、重复/并发撤销、已知失败与UNKNOWN区分，静态/本机范围接受。
- E11-RVW-03：runner未知时禁止platform finish的实现与编译接受，Android实际钩子验证仍未运行。
- E11-RVW-04：新部署批准、撤销及两normal报告来源由外部受信执行者核实，属于明确边界，不把结构校验升级为认证。
- E11-RVW-05：旧manifest self占位显式处理，实际文件原SHA及其他行可信pin保持，不伪造零字节证据。

未来设备附录可作为待审草案：新的具体许可→fresh exact14/原UID/签名/数据目录/idle→R1固定once路径和真实批准release→单次保数据14→15→post-install精确pair/旧档保持→每host当前观察→MP4原证据独立接受→AVI原证据独立接受→两真实不同normal回执后能力→另满足条件才cancel。源不同（含已15）、未知或预算不足即停，不重装、不重放、不换path/port扩额、不重置账本。

4MiB累计、2MiB每任务全额预留、128任务、96原PC操作、128总accept、≤16受审PC查询、5秒控制/55秒一般响应、1MiB输出/日志、48holder等门保持。未来合法normal允许追加R/S并增加总消费，必须保留原107218/三R三S接受前缀，不能承诺新总消费永远仍107218；不足下一次全额预留就停止。

当前NOT_RUN：14→15安装/真机current observation、MP4/AVI/能力/cancel、两真实normal回执、Android UNKNOWN结束钩子、内核raw/dup故障、普通发送者权限负例、长期回归。未签发真实release/部署scope，未创建真实once派发记录、产品grant或normal回执；本复审不能解除用户暂不激活/不继续播放的限制。

## 证据与停止状态

自有证据目录：docs/tester/D1_E11_EVIDENCE。

- independent-review-audit.json：SHA7f50b9e7a87a2647d6e71dfecb58c12927178cded540adc309efa94e2e2ca83d。
- input-pins.json：SHA9c9074b1db060f510513258006288b61a02886a7ec7fcde2a32470974919603d。
- manual-source-review.json：SHA528221c6ba08fc31d7dd5de4bb0b1e7247771ded493449ad0d3c87da69c67ef8。
- evidence-manifest.json：SHA403046e93bff01c2cdd226aaf6b25e714460e699f09c6d68256206b47d0bd0d5，生成前固定文件集合，排除自身/后生成报告/发送回执。

完成后立即通知负责人并保存发送回执，停止等待。不设备、不安装激活、不播放、不自动后续测试；原107218、全部档案产物、oldCloseACK=false、历史FAIL/UNKNOWN、D1 NOT_PASSED/M0 NOT_STARTED及所有P0保持。
