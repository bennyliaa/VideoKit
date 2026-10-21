# D1 E13A 精确设备计划附录 V1.0

日期：2026-10-18。REVIEW_ONLY_NOT_DISPATCHED。当前不执行设备/媒体/实际scope或once；项目常规真机授权已给，后续具体派单内无需再问，他项目占用稍后试、不抢占。

候选v17/ACTIVATION/ABI1，实际升级源仍是E11接受v15精确pair/原signer/UID10221/10222/data inode6972/4741，原E13 v16未安装。新pair/fixture实际hash见evidence/apk-delivery/apk-audit.json和release/candidate-binding.json；scope须独立sourceReview、目标三APK、真实源接受报告、六方法、预算、三个metadata argv/script pins后才能派发。新once固定e13a-activation-deployment.once，在原registry外，不改名重用E11或E13旧once。

六方法顺序、源码生产source正对照、4096B非媒体定义、4224B实际read/6open/7close及上限64KiB/8/16继承E13，fixture只新装一次且确认原不存在。P1现在false/SE也对同原target connection一次unbind，三份binding状态随原ordinary方法结果输出；绑拒绝与unbind ACK不同。没有endpoint仍不测内部onTransact。

## 三个直接metadata客户端

仅使用release/metadata/下三份JSON中的**完整argv**，由既有tester原Process/pipe custodian直接启动adb.exe。脚本已嵌入argv的单个remote sh -c参数，同时保存.sh供审查；不在PC先起Python/Java执行脚本，不push新脚本，不额外ADB探路或查询。

| 客户端 | 脚本/argv前缀 | 字段 | 记录cap推导总量（含标记） |
|---|---|---|---:|
| M1 部署前 | M1_PRE_DEPLOY | 设备/用户/解锁字段、原controller占用证据、相关ps/全部active instrumentation/目标服务、v15pair/UID/data、fixture不存在、34stat/18control/完整ledger/固定inventory | ≤53512B |
| M2 部署后首方法前 | M2_POST_DEPLOY_PRE_CASE | 当前v17pair/fixture hash/version/实际普通UID、原data、设备用户及相关进程/instrumentation/service；签名由已审本地SDK结果与精确APK字节连接 | ≤27588B |
| M3 六方法后 | M3_AFTER_SIX | M1同固定stat/control/inventory/ledger、当前pair/fixture/data、相关进程/instrumentation/service，并连接六份原finish和七PC自然返回 | ≤56360B |

每份仍是1原直接客户端、原GENERAL≤55秒、stdout+stderr总≤65536B，三份保留196608B；其余原预算：部署entry1+内部32、六Java entry6+六instrument child6+metadata3=48。文本分配32768+524288+491520+393216+196608=1638400B，余458752B只给既有scope/index/metadata；总2MiB不按阶段清零，重复保存top/child raw分别算。socket STATUS/OP/CLEANUP额外连接查询0。

来源字段计划和最后接受raw均精确pin，34条stat没有造缺失inode；新四产物stat取tester既有acceptedStat。18控制文件只读完整base64/校验，ledger2271B/SHA e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649。非零.mp4/.avi/.mkv等媒体只stat，不读取或重hash；静态APK hash用于身份，不是媒体payload。旧operation.pending.N2-e5-aborted是已结算并被pin的历史标记，按原精确inventory保留，不将其误删；不得有新增在途pending或条目。

脚本输出BEGIN/END完整记录，每条明确cap，超限/命令失败退出，不tail、不静默截尾为成功。记录上界按所有cap及标签计算，不能把输出变小当完整证据。tester还必须按expected-baseline.json逐条审：精确源/目标pair、版本/UID/原data、fixture不存在或实际新普通UID、固定stat及18个完整字节pins、inventory/ledger、用户可用、无活动instrumentation/service；缺字段/未知命令输出或不满足原调用语义必须BLOCKED，不能只凭脚本exit0。

M1之前必须已有controller独占/其他项目占用证据；其不明就停，不增免费ADB客户端。每个原客户端PID/exit/原双reader/pipe及scope留证；不能把三份改为另起三Java wrapper后排除计数。M3缓存PID不等任务仍在途，也不能以PID消失代真实原资源归还。当前仅本机Git Bash -n语法核对，未执行任何remote脚本，不宣称API31各字段现场已可用。

原bridge每await5000ms、方法30秒仅资格；PENDING/UNKNOWN拒绝runner及PC结束，保原connection/source/runtime/host/ADB/custodian，不重bind/重复unbind、kill、force-stop、换UUID或填ACK。本批无永久UNKNOWN/OOM/重启/自杀/native注入。若三客户端/64KiB/48次不足，执行前集中报负责人修订，不能临时扩预算。

全批媒体输出/READY/新R/S=0，原接受214483B/7R7S/0reserved和107218B前缀/全部产物/fence/oldCloseACK=false保持，仅报告时点引用，未在线重新确认。全部六方法Android仍NOT_RUN，静态复审后由负责人另派；D1 NOT_PASSED/M0 NOT_STARTED。
