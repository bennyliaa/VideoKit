# D1 E9 剩余门与有限自检映射 V1.0

2026-10-18。下面PASS仅指表内已执行的有限本地范围，不代表每个设计子排列、Android实测、D1通过或正式准入。32设计组按实际生产对象映射，36最终映射JVM调用、D05针对性修复另2次，共2027个最终映射断言。A21四个当前状态失败追加子例使用独立JVM，未清空生产静态保留集合来制造恢复。

完整日志入口：evidence/local-check-results.json、selfcheck-attempts/final-production-009、replacement-cut-011；test-mapping.csv含断言计数。001至008所有失败/诊断/扩展尝试保留。主修复原因为Windows锁读取适配和实际资源检查；失败返回归档与host端dispatch检查也有明确测试。旧reader由冻结E7A源码新鲜编译、独立classloader加载，平台替身仅提供其允许继续的条件，未复制旧判断模型。

|组|实际对象|已执行有限范围|未执行或平台边界|
|---|---|---|---|
|A01|E9MigrationRun/E9MigrationTransaction/E9Phase|实际身份读取异常、未BIND、execute无许可，业务open/write为0|身份FD close UNKNOWN专门注入未做；Android身份所有失败切点NOT_RUN|
|A02|E9Actor/E9ProcessIdentity/E9Registry|UID/PID/start/descriptor/bootKind/task拒绝、错误reserve、含括号proc解析|全部字段笛卡尔组合及Android权限失败NOT_RUN|
|A03|E9Registry.Store/reserve|初始外部授权引用force失败；reserve WRITE/FORCE/CLOSE_AFTER/READ失败无写许可|磁盘掉电及进程崩溃NOT_RUN|
|A04|E9MigrationRun/E9Registry|已预留但尚未执行时FD计数0仍不safe；早ACK令PENDING；失败返回可归档收尾不可final/actor2|真实Android线程调度NOT_RUN|
|A05|E9MigrationTransaction/E9OwnedFiles/E4Owned|intent open前/后、write/force/read/close前/后Exception和Error；mkdir/dirsync异常|mkdir/dirsync每个Error/永久阻塞排列NOT_RUN|
|A06|E9MigrationTransaction/E9Registry|payload和commit七个切点各Exception/Error，不能final|任意中间字节截断组合NOT_RUN|
|A07|E9MigrationRun/E5BGuard/E9Registry|同一完整commit，lease unlock后close等待；另一真实JVM锁可取得，finish仍0；10秒后真实晚返仅PENDING|Android raw/dup close及真正10秒墙钟NOT_RUN；本地时钟受控|
|A08|E9OwnedFiles/E4Owned/E9MigrationRun|所有数据close后最后owner guard native close已发生但抛UNKNOWN，原holder不归还、不产return proof/finish|Android内核close UNKNOWN NOT_RUN|
|A09|E9MigrationRun|队列到界执行前不写；身份到界前不打开资源；永久PENDING|真设备超时与调度NOT_RUN|
|A10|E9Evidence/E9Registry|伪造/错actor/非0未返原回执拒绝|真实管理链路断连NOT_RUN|
|A11|E9MigrationRun/E9Registry.captureNormalFinish|finishClaimed及假的系统finish证据不足以final|真实ActivityManager日志和原PID缺席NOT_RUN|
|A12|E9Registry.Store/sealFinal|returned/checkpoint/seal各WRITE/FORCE/CLOSE_AFTER/READ失败，不发布final authority|真实PC崩溃/掉电NOT_RUN|
|A13|E9Registry.openKnownHead/commandIntent|错head/活actor重开拒绝；重复控制seq消耗后不得重复写|真实管理进程失联NOT_RUN|
|A14|E9Phase/E9Registry/E9Catalog|完整device commit及合格synthetic catalog仍无法使PREPARE产品/观察激活|实际activation包尚未构建|
|A15|E9Registry/E9ProcessIdentity|旧actor活着、无终局证据时actor2拒绝；同代proc仍活拒绝|真实boot/PID复用NOT_RUN|
|A16|E9Registry/E9MigrationTransaction/E9Catalog|旧close UNKNOWN后以合成OS确切终止处分启actor2；actor2实际各holder返回，catalog旧return保持ABSENT|终止证据平台来源为替身；Android死亡NOT_RUN|
|A17|E9MigrationRun/E9Registry/E9Catalog|旧actor10秒晚返+正常finish，actor2新身份新资格，保留旧PENDING|Android正常finish来源替身|
|A18|E9MigrationTransaction/E9Catalog|payload完整commit缺席时actor2只补建缺失项；0B torn commit隔离、不覆盖|全缺席、torn intent、所有部分长度组合未逐一执行|
|A19|E9Registry/E9OwnedFiles/E9LegacyState|actor2 close UNKNOWN后无actor3；原3R/3S、107218、档案和fence不变|原设备全部导出件当前hash未重读|
|A20|E9Registry/E9Catalog/E9ActivationPolicyExport|事件head固定不含未来APK/catalog自指；另存release不改head；错auth/未知外部文件拒绝；合成catalog禁止导出发布policy|实际DEVICE catalog/H_actor/activation均NOT_CREATED|
|A21|E9Catalog/E9CurrentObservation/E5AAdmission|错误信任pin/environment/registry/actor清单/schema/device commit；当前payload/pending/guard/ledger/close失败分别无grant|4个当前失败子例分独立JVM；真实activation/设备NOT_RUN|
|A22|E9CurrentObservation/E9LegacyState|合法完整追加R/S消费7B被接受；真实本地新观察持guard/账本并实际close，仅本进程grant；prepare仍拒绝产品|UID/inode/目录fsync替身；不同真实Android host NOT_RUN|
|A23|E9MigrationRun|身份真实返回、无execute预留，关闭写入口后精确ACK可结束；晚到EXEC拒绝|实际Android广播竞争NOT_RUN|
|D01|真实旧E5AFinalObservation/E9DeploymentGate|新鲜编译冻结E7A真实旧reader，未知marker仍FRESH；旧字节在新dispatch gate install前拒绝|旧Platform的死亡/guard/目录fsync为替身；不是设备旧码重装|
|D02|E9DeploymentGate|高version/相同证书/伪ABI的未知完整字节，inspect及install均0|未实际重签/安装旧APK|
|D03|E9DeploymentGate|候选phase不符拒绝|所有错签名/UID/package组合未逐一枚举|
|D04|E9DeploymentGate/E9Registry|已安装有相关进程时拒绝|实际base.apk/进程观察NOT_RUN|
|D05|E9HostDeployment/E9DeploymentGate|实际PC端port解析、候选再hash、固定install-r双命令；任意uninstall拒绝；检查后替换成已知旧字节也install0|Commands为OS替身，无adb.exe或真实安装调用|
|D06|E9DeploymentGate|安装后实际Port返回SHA不符，结果拒绝|实际安装和组件验证NOT_RUN|
|D07|E9Phase/E4FencedTask/E4OutputBudget/6 Android entry methods|prepare共享phase/预算/初始化/旧reader/旧恢复直接拒绝；另6个实际新编译Android公共入口先于平台拒绝|SDK桩非Android设备；Binder/服务事务仅源码/DEX核查|
|D08|E9Registry/E9DeploymentGate|外部revoked json/未登记activation release不构成代码撤销或激活|实际撤销release未派发|
|D09|E9Registry/E9DeploymentGate|同历史head的后续合成compatible release可以精确deploy gate；prepare仍拒绝产品|部署OS替身；真实activation未构建/安装|

## 仍开放的验收门

1. tester整包独立静态代码/证据审查尚未完成。当前包不自动获得设备、迁移、activation或正式交付许可。
2. Android真实boot/proc/UID权限、目录stream/fsync、FileChannel锁、原raw/dup close、广播seq竞争、真正10秒资格及正常instrumentation finish证据均NOT_RUN。本地替身不替代这些事实。
3. 负责人另派最终device scope、registryID/migrationID、精确prepare plan SHA/授权引用/独立最终review后，才可能运行真实actor。当前没有真实H_actor、catalog、approval token或新执行许可。
4. 实际actor最多2；未知对象/管理断链/恢复资格不足/部分torn内容均隔离，不能用第三actor、补旧ACK、删目录或新ABORT解决。未覆盖子例须由tester决定是否补充本地验证，不能预填PASS。
5. 真实final事实到齐、独立封存接受后才可另派activation发布。须固定精确同catalog/head、同原证书、必要role/入口差异及更高版本；本批没有构建它。
6. E6B-OBS-F01只有实际新host核当前原guards/完整账本/无pending并真实返回后才能关闭；静态代码和合成catalog不能关闭。D1未过，M0未启，长期准入OPEN。

原N2旧V1没有boot/start，不能补造；原close ACK=false保持。原消费107218、reserved0、三R三S和输出/档案hash来自冻结证据，当前没有重新读取真实媒体作新声明。稳定性、独立Kit/Flutter、许可与全部其他P0继承未变。
