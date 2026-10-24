# D1 FACTS_V2_QUALIFICATION02 集中修复开发要求

2026-10-24；负责人审完独立整包B后正式派发。只在新目录 docs/coder/d1android02-facts-v2-qualification02 集中开发、自测、冻结，不修改01冻结或测试历史。D1未通过/M0未启动；不SDK/ADB/设备/Gradle/媒体/Git，不处理任何旧运行对象。

## 准确依据与裁定

独立报告 docs/tester/D1_FACTS_V2_QUALIFICATION01_INDEPENDENT_B_REPORT_V1.0.md，SHA256 3eebbe89d530fae48a183f3db229d2c59adab7989df58e2b6c1f01aad714d7e7。负责人实际核有效delivery-manifest-v2.json（f958f9b6cbf5f1efb790897bc191f1b06c0762ee8e1d2e36b3598ff134490dde）209项/8532587B，bad0。初版汇总bytes0错误已更正留史，不要求重跑原场景。

01源26 dfcd0add7bf89b9363b7efe23b45bed0145ee977fddd48fd45725546350e74d0、gate18 e404f32bccb9aac960b001b7e529d7aed06a501d93aca2eca255c12b8a264a61、manifest07a7572ce553f4ad7cd85ca98a97e6fe7b643275d228deb6a9e05cb4c111a0c4保持冻结。新02需自身准确源/gate/plan/profile及差异，不沿用旧hash冒新通过。

F01实际原Capture接收435446B输出触发PIPE_BOUND已证，另FactsBundle借用preauth16384B解码上限不匹配。F02实际Python生成8/16服务资格17127/27407B而PS目标GLOBAL_QUAL_BYTE_BOUND已证；32/68服务仅静态投影，原qualify已拒绝。F03是可信同进程对象模型来源/嵌套校验反例，不是43独立漏洞或真实外部攻击成功；failure=null no-op为tester判据错误。32非受控异常与6项更早安全拒绝分别记录，不能据此冒准确深层校验。

## 必须整批完成

1. F01统一既有事实生产、传输、解析容量契约。保留合法raw总139264B等原功能范围，原Capture262144B/生产原cap不提高，不以减少合法包/服务、静默截断/丢证或把最大输入改非法来取得通过。优先最小有界表示、消除重复；如确需hash绑定原证据引用，须固定读取路径/身份/大小/原字节、无链接/越界、计入原读取预算并在接收端核验，不另建通用存储或诊断框架。不同消息使用明确各自有界解码，不能随处借preauth小上限或整体取消cap。实际原入口/原Capture应能承载接近边界的合法数据，超界准确受控拒绝。
2. F02统一资格生成和原PS消费的实际UTF8字节契约。完整窄政策/来源/外批/原返回/目标/鲜度证据不可删减；允许最小去重或明确有界证据引用，禁止只保留reviewSha字符串后不核内容。对既有模型合法服务集合给出完整可达大小证明；实际8/16及有依据的最大合法集合均测试。生产成功的每份资格必须符合原接收限制；生成前拒绝超限只能解决已明确超出既有合法范围的输入，不能默默缩小需求。若数学上确实无法同时满足，给出具体必要设计决定和证据，不擅自提高cap或冒通过。
3. F03在可信Python宿主边界内补齐原构造/启动/完成链的最小内部来源记录，FactsBundle不能仅信type和可填布尔字段、pid-only对象；真实原Popen实例、同原Capture、实际wait/readers/流/H与原writer完成、准确identity/argv绑定。不要声称防御同进程任意内存修改。关键嵌套schema/ownerThread/claimFileId/proof tick/receipt与gate来源等逐项确认字段义务，必需字段缺失/null/异型/额外字段受控拒绝；合法可选元数据/no-op不误拒。补足最终44字段中未测12字段删除/null/异型及完整V1→V2/V2→V1路由，区分更早拒绝与准确深层覆盖。
4. G01新候选精确支持本批开发根和未来独立测试根 docs/tester/D1_FACTS_V2_QUALIFICATION02_INDEPENDENT_B_EVIDENCE/fixtures 下新scope。不得写旧允许根、改BASE、junction或开放任意路径；保留绝对路径/非链接/非旧scope门。使用真正原facts_entry→原Capture→FactsBundle正链路离线验证，不能仅用emitter或伪造Capture替代。合法大raw可通过已有固定离线fixture的数据输入薄扩展进入实际collector，不加SDK调用或伪造真实设备。
5. G02演示可操作的最小外部review交接：原Capture所有资源已归还后，可信宿主保留真实对象，导出未批准候选，另一个明确独立的离线reviewer夹具接收并返回准确绑定的合成review，原宿主在同一原300秒鲜度内消费、原PS核验。可复用有界固定文件/现有宿主机制，不建常驻服务、签名/密钥/IPC框架，不从文件重建Capture。全过程明确OFFLINE合成，不称真人批准/现场资格，超时不刷新时间、不自动重试原产品scope。若现有架构不能支持，在本批给具体最小接口决定，不以同调用者自批代替。
6. 保持原V1 346/45/17、V2 HOME/窄服务正例、仪器与TOP优先、0/299.999/300/未来时钟、原preStart与原返回、全部异常写入保护。按最终Schema对应阶段A160追踪，记录实际覆盖/静态/未执行，避免扩无意义全组合或为数量堆测试。

## 执行与完整交付

新02独立输出；固定所有来源、输入、调用图与预算后有限集中自测。实际动态预算360秒、320秒停止新增；读取1GiB、产物16MiB、辅助96、并发1，SDK0/产品retry0，原生产上限不扩。无需Android构建，新Python/PS必要验证集中执行。纯准备错误在未进入产品且无新未知时留修订后修驱动，不逐错交接；任何原返回UNKNOWN停止新增，不二close/kill/attach/重放/补ACK退款。原FAIL/UNKNOWN、01冻结/ZIP和tester209证据前后保持。

交付完整功能差异、F01–F03/G01–G02逐项关闭或具体未完成原因、大小上界计算、真实离线正链路与独立review夹具证据、原返回/读写/预算审计、精确源/gate/plan/profile、最终Schema、manifest和冻结包。六组自测等必须分清模型/实际函数/原进程；不以自测代独立通过。完成后主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774(local)，负责人完整审核后才正式交tester整包B。通知失败保存回执，不绕过。项目指定成熟框架/精确许可、Flutter/独立Kit及全P0不变，不扩ASR/翻译或提前M0。