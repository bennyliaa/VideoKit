# D1 R1 负责人处置与R2契约决定 V1.0

日期：2026-10-16；输入：coder R1三份材料、tester D1_R1_REVIEW_REPORT_V1.0.md（14 SUPPORTED/1 CONTRADICTED/4 MISSING）。本文件为负责人在既有授权内的设计决定，不宣称功能通过、整体API冻结、D1通过或M0开始。原始全P0不变；C14及历史报告只读。

## 1. R1-R05引用勘误

原R1矩阵W14链接是可变batch-status.json，却描述12:38:18。该固定快照应为docs/tester/D1_C14_EVIDENCE/batch-status-20261016T123818.json，SHA256 1f8fa4c6ca11c271d19fab16da06a3e490723c50251837219f6b0e3d49ca3d7a。当前batch-status另有12:41状态，环境中间报告描述各时点。保留R1已评审文件hash，以此附加勘误承接，不回写冻结记录；两时点均不表示C14执行通过。

## 2. 故障功能与精确原因的分栏原则

原始§27故障后果P0不变：会话原生故障不得拖垮宿主、错误释放其他会话或生成成功部分输出；真实死亡/Source/其他消费者/输出租约/Surface/codec等必须分别有证据，未证继续PENDING/quarantine。Java catch或系统服务存在不替代原生故障隔离。

采纳R1将功能隔离与平台精确原因可观测性分别制定用例的原则，R2需提交新旧用例映射与判据，独立评审后才能用于新实验。App在确认worker死亡但系统不提供精确signal/trace时，可报告WORKER_DIED并保留cause UNKNOWN及原始字段；不能补造signal11/权限原因、读取测试期望当事实或外部raw写回App。精确原因能力为独立OPEN项，不以UNKNOWN伪装精确诊断成功。原C13严格方法仍FAIL、C14两项NOT_RUN，历史trace/ordinary UNKNOWN不关闭，也不追认D1或任何候选通过。现无新平台/采集条件，不重跑同条件崩溃。

这一区分不降低任何原始P0，不批准把仍在宿主的致命调用仅作泛化风险接受。R1-R04须建立真实危险调用/进程机制/可控故障/存活及回收证据矩阵；无法证明满足P0时仍BLOCKED。单APK ordinary isolated现约束保持；同UID分进程/新增组件若作为替代须另列明确决定，不能在R2自行采纳。

## 3. R1-R01源租约决定

物理源归并、版本及移动事务权威在宿主。宿主注入不透明sourceLeaseId和sourceVersion，多个mediaToken可归并同租约版本；Kit不扫描路径、不猜文件等价、不见Browser数据库。consumerId/bindingGeneration和“整个可能再次open的任务预留”均计入租约，不能仅数当前文件句柄。

宿主移动意图先原子seal当前租约版本，停止新消费者与future open授权，再取消/排空对应预留、open/read/close/相关数据回调、实际worker/消费者引用。会话SourceReleased只说明该消费者已清空；全源可移动必须宿主聚合seal成功和全部消费者/在途/失败close实际归零。通知携带lease/version/generation/releaseSequence，可按同身份查询；SourceReleased终态通知本身不是妨碍通知产生的待排空数据回调。旧代迟到资源只清理不复活，旧状态不得给新版本移动许可。新打开要宿主重新授权版本/代次，不沿旧路径重开。

R2须明确seal/reserve/open竞态的线性化、源换版/别名映射/通知丢失/进程死亡恢复及最大有限重试，给不同token同物理源、未来open、移动后旧open的可判定例子。此为宿主通用资源契约，不实现Browser业务或SDK文件移动API。

## 4. R1-R02输出决定

能力必须显式：sequentialWrite、seek/randomWrite、maxOffset/knownLength、flush/close意义、durability与只读验证租约可用性；未知空间不等无限空间。容器/验证能力不足在写前稳定拒绝，无暗建未授权暂存。FD借用/dup/转移三者由adapter明确其一种及关闭权，stream.close、dup.close和fsync不合并成“已安全”。

exportId为稳定幂等任务键，绑定planVersion与sourceVersions；handleId标一次授权临时目标，ownerEpoch区分恢复owner，attemptGeneration区分实际尝试，不能通过换id规避同任务未知结果。公共Host协议须提供query(exportId)和幂等markReady/abort仲裁：READY持久且回包丢失仍同token，合法新owner可终止WRITING，旧owner不可成功，READY不可由迟到abort撤销。writer实际停止/close及授权验证lease读取/归还、必要校验通过后才READY；业务COMMIT仍宿主独立操作。R2需明确writer/验证身份/租约状态、恢复未知与返回错误码/阶段映射。

## 5. R1-R03/R04下一步边界

先以本机现有授权真实文件ReadHandle作为可离线E2候选，源样本只读，实际2GiB边界小块对照可采用已有大MKV但不解码它。包装器可控延迟/失败须标注注入，不能称真实SMB网络故障。Android/SAF/真实NAS未测均NOT_RUN；不要求用户NAS凭据，不偷偷扩SDK文件源业务。

R2先形成判据与最小实验设计，不编产品/新APK、不中断C14。UNKNOWN长度不同空源；正请求短读合法，非零请求0进展有界失败；已知长度提前EOF为损坏/不一致，只有可靠宿主版本证据才宣称SOURCE_CHANGED。保留稳定code＋stage＋可重试/资源状态，具体公开码表在R2评审，不把第三方异常直接公开。

R1-R04列危险调用的实际进程/UID/owner/输入可信度/触发阶段/观察者/资源证明/缺证替代；普通异常、native crash、OOM/全局压力、系统终止分开，不能给抵抗失电/系统强杀绝对保证。R2不得通过文字接受尚未隔离的宿主致命调用。

## 6. 执行

R2只完成契约决定细化、事件序列、有限实验计划与原P0追踪，整包交tester评审后再派有限实现。C14 73项及2历史信号未运行保持，等待用户可用环境通知后负责人再安排，不轮询设备。模型/标签后续先团队盘点再提真实用途缺口，不下载未准入权重。Media3/FFmpeg当前许可和正式Flutter/独立Kit方向不变，Android先行；D1未通过，M0不启动。
