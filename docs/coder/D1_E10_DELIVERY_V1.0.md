# D1 E10 精确执行包交付 V1.0

本包是唯一原N2终局验收迁移的准备交付，状态 PREPARATION_ONLY_NOT_EXECUTABLE。未产生实际新registry/migration/attempt/handle、签发scope、现场预检、H_actor/catalog、设备写或activation。复用E9B原双APK/JAR，不构建、不编译、不运行旧通过套件。发现一个生产收尾缺口，列于static-blockers.json；执行准备结论为 **BLOCKED_PENDING_INDEPENDENT_REVIEW_AND_COORDINATOR_DISPOSITION**，不能由本包直接启动迁移。

## 四文档映射及机器输入

本DELIVERY负责范围/授权/来源/成本；EXECUTION_RUNBOOK负责可实际落到原CLI的条件流程、现场采集和统一账；FAILURE_AND_FINAL_REVIEW负责失败/UNKNOWN/actor2及独立final；ACTIVATION_INPUT_DAG负责后续独立发布输入，无预建包。

plan/descriptor.json是已冻结生产proposal的精确725B，SHA256 4a1877713ba2b6763d777e73e9b956914a3b5fefa8c8c35c340f81531e6c2adb；plan/expected-commit.json是同一算法的244B固定期望字节，二者不是设备提交或授权。execution-plan.json列固定旧事实/新增白名单/额度/不生成身份状态；templates列实际managerTrust/preparePlan字段与逐条命令的未实例化模板，带templateOnly外壳，**不可直接交生产CLI**。外壳不是新协议或执行器。

## 授权来源与生效

用户原有全权项目推进、恢复开发、永久平板授权属于项目/设备层权限；具体新旧N2终局策略、指定三文件及一次写actor须由负责人在E10独立审查后正式采纳并派发。来源分别见reference/E10_COORDINATOR_DISPATCH_SOURCE.md、正式需求、已接受真机报告；对于其他窗口用户原话，本包仅引用负责人/报告的记录，不伪造签字或逐字用户批准。E10准备派单本身明确禁止设备/写迁移。

scope.template.json保持DRAFT_NOT_EFFECTIVE且实际身份、签发时间、正式派单和接受的E10审查SHA均null。正式派发时负责人签发具体scope，受托tester可按派单记录其精确文件及来源，由实际负责人派单承担策略采纳；身份只生成一次并存原字节。scope的SHA256是这些真实字节的绑定，直接供生产Trust.authorization引用，不是随机64hex token、密码、资源返回证据或产品准入。原只读scope的授权SHA不可挪用，E3已耗许可不能重用。不得因为模板尚未填充而循环询用户或另建token框架；当前缺的是集中发现的代码出口缺口处置和独立执行派单。

## 精确新增与旧事实

设备路径均在files/e4a_output_budget/legacy-acceptance/<新M>/：actors/0001.intent ≤2048B；n2-v2.acceptance精确725B；n2-v2.commit精确244B。本actor仅3文件，已知内容+intent上界3017B（各生产单文件上界2048/4096/256，总分配上界6400B）；最多3新目录legacy-acceptance、<M>、actors。目录项/块/文件系统journal开销另计，不能把3017B当总磁盘成本。新intent实际长度仅在真实actor与BOUND hash已得时由canonical actor.intent计算，当前不填造PID/boot/start/H_actor。

全部O_CREAT|O_EXCL/CREATE_NEW，0600文件/0700目录；payload/commit/intent写后force/readback，父目录sync。代码会打开/排他验证原guard、13项档案/metadata、原0B输出及ledger，force旧metadata/ledger和原目录，但不改旧字节、不追加R/S、不新媒体输出。原ledger完整≤131072B，接受固定1011B前缀及合法已settled后缀，不能锁死整文件1011B。

原task86cafdb3-0fc4-447d-920b-b19c884bf494、attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f、budget730a73e1-50e1-4198-a515-047104f00e31、fence662e9ecd-bede-42e6-bb58-ce81d668ff44、owner64522:20304:10221/0B、lease64522:20385:10221/36B及oldCloseACK=false保留。S0 ABORTED0B，后续53651+53567=107218，三R三S/无reserved为历史接受基线；现场须重新核，合法settled后缀需归入本次审查，不删除还原历史。旧writer缺boot/start根因UNKNOWN不能回填成Java close。

## 复用制品与证明范围

app version13/D1-E9B-PREPARE，SHA ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020；test SHA 2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b；host JAR SHA 4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707。精确路径/大小/签名/35坐标7库/E9B seal源均列external-input-pins.json。计划安装0次；现场pair不同则阻断另审，不盲目再次install-r。

已接受真机只读report与127项证据manifest本地逐项重算，用作历史能力证明：SYSTEM_BOOT_COUNT正常分支、原身份39.3ms与FD返回、非等待/五秒完整广播、归档精确ACK/normalfinish、PC26操作自然返。旧actor PID17434/boot2/start16410590，registry b1d2b533-2461-4a85-ad05-d64509a6b1f9、migration eed3bd1d-7f52-47a4-bd66-992f5b8937f1、attempt fa4e3689-90dc-4bef-b565-fb602863d97f、handle8419402b-16a0-45a0-92fe-d1ec7019848c均**已结束不可复用**。这些不是当前设备值，写COMMIT、guard raw/dup故障、DUMP普通发送者负例等不因该报告而通过。

## 只读校验与封存

tools/validate_package.py只读取本地文件并输出JSON；无subprocess/socket/ADB/UUID生成/文件写。默认严格检查模板状态、字节成本、47外部输入、E9B402 immutable及真机127旧证据；PASS仅PREPARATION_ONLY，不是执行通过。--bound-dir在正式派发后读取新inputs、scope/新UUID/原scope隔离、canonical plan/config/命令/index与现场receipt绑定，仍不证明其采集真实性或替代原生产guard/返回门。校验器拒绝重复key、非canonical wire、越界路径/错误hash/旧actor复用。无正向伪造现场fixture；有限负例仅校验器输入拒绝测试，不重跑生产套件。

本包保留D1 NOT_PASSED、M0 NOT_STARTED、长期准入OPEN。Framework、独立Kit/Flutter、48资源/严格6帧/full EOF/1000us、FFmpeg许可P0均不变。下一步先独立审查本包及P1出口缺口，不能自动开始设备或activation。
