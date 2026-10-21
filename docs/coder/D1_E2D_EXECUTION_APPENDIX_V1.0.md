# D1 E2D 执行与只读复核附录 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2d`。本附录记录已结束的唯一修后小范围对照，不授权再次执行。六点句柄160/164/161/193/161/161，排空归档后弱cell/closure0、外部Future1和原值保持；完整Engine准入仍未证，旧G369/+209及R519 FAIL保持。

## 唯一活动及文件

| 活动 | 原证据 | 成本/含义 |
|---|---|---|
| E2C逐字节生产绑定 | production-binding.json | 32src＋manifest/profiles共37文件、10原编译产物；先核C freeze、ZIP、source-manifest自身摘要；不改生产/重编 |
| 唯一G预约 | g-comparison-reservation.json | CREATE_NEW先于任何Hub/cell，maximumG1/samples6；未再次调用run或预约以补跑 |
| 原G六点 | g-comparison-1792174935530529100.json＋stage0..5/entered0..5 | 原PID35964/creation134366485352518462/owner不换，每点一次，无第7样本 |
| 原caller退出 | g-comparison-outer-exit.json | 绑定原report SHA/runId/identity，实际exec exit0，rerun false/newDiagnosticG0 |
| 只读审计与封存 | audit/source-manifest/freeze-summary、E2D-source.zip | 读取既有证据/hash，无OS指标/诊断/测试/编译；PASS不产生full准入 |

当前新增targeted runs0、compile0、actual full0，测试断言计0；旧C1125/旧B955/partial77等只历史分列。一次OS调用完成后没有改代码再测、没有重启择低、没有补对照或追加逻辑测试。

原probe SHA `6975917a764cde4db387c35ddd93a902ba37433e072eb092d7ace598ebcaca46`，原JSON保存同值。生产依赖源保持E2C原命名及字节：所复制32源、manifest/profiles和产物均hash相同，未将E2C.dll改名伪装成新编译。外部Python版本3.12.14/64位及DLL SHA与E2C一致；这仍不证明具体编译锁原语或每对象句柄类型。

## 调用者与观察临时引用

Probe只绑定生产private_cell/compact_cells/cell_facts。先由短创建函数登记原source操作并创建生产cell，只有首原Future被外部持有；后续Future/cell/闭包只留weakref。短消费函数实际complete→gate→result，逐cell wait_for(cell_quiescent)及源done/nativeReturned具证后返回，creator再调用compact。没有Engine/Native/Channel构造、真实IO、J/R或媒体。

采样前的引用统计在独立短函数内一次获取弱referent并仅返回标量/审计纯值，返回后才调用Win32 reader；不会让alive列表、最后循环变量、原闭包或inspect帧跨到OS观察。生产归档计数分别1/8，工具未手清活动dict。终点只清probe.audit_copy，生产cell_total9/history9/peak8/active0不变；保历史审计证据，未清历史退款。

首外部Future始终持有，排空后其cell反向边已由生产归档解绑，原Future.result与原value按is核验，Hub关闭后仍相同。合法外部Future残留不要求回ZERO；末点161较本ZERO+1不能被直接命名为特定句柄类型。只有当前小9范围的观察与引用效果，不能外推完整Engine长程峰或抵消旧209增量。

## 独立成本与返回

1G/2Hub/6sample/identity1，reader6周期＋身份捕获1合计13开13关/峰1/credit0；ledger峰3、buffer信用峰8、最终0。9source admissions/private creations/逻辑native completions/gates/Future consumptions/callback returns，normal compact2、cleanup补complete/gate/consume/compact均0。原452控制未运行，诊断额外操作单列，无新driver controls/RPC。

两Hub线程在六点结束后实际close/join；closed、workersAlive0、remainingCredits空、ownershipPending false，原G命令exit0。外部Future仍保持至closure核验，不要求所有合法外部对象立即回收。没有关闭后第7个OS样本；outer-exit来自原caller已返回的结果。

总1.125s≤60秒，最后sampleDuration约0.015s，其余0.0是时钟粒度；各返回后≤0.1秒。不可中断OS若未返须保entered/原身份/PENDING，不强杀或替换；本轮全返回。若超绝对/增量限额，脚本先保原样本再FAIL并停止计划后续采样，只清理原已分配资源，不补跑。本轮无该超限。

原report diagnosticArtifactBytesAtReport100630B只对应当时g-comparison前缀含reservation/entered/stage/report，不含随后outer与单独production-binding。audit另计最终109,229B＝100,630原快照＋635 outer＋7,964 binding，≤512KiB并纳入整批4MiB；原快照不回写。fixture0≤2MiB，整批日志/证据含seal精确量由freeze-summary给出，源码ZIP/依赖产物与诊断日志分别计费。

## 只读验证

以下命令只读本包、原E2C及更早冻结记录/源码/依赖，以及原回执保存的Python版本/DLL摘要；不重新读取当前外部runtime文件，不导入或运行compare-g/生产方法、不查OS指标，不编译、不起G/J/R、不媒体。

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2d\tools\verify.py'
```

预期integrity PASS、state E2D_FROZEN_PENDING_INDEPENDENT_REVIEW，comparison保持原六点结果，但actualFull NOT_RUN/通过0、realMedia NOT_RUN；runtimeAdmission为小probe无新actual准入，旧B G FAIL仍保留。此复核校验原运行时摘要证据，不重新证明当前外部runtime与原观察相同；环境后来更新不改写旧观察，也不由本命令证明新环境适用性。冻结文件/ZIP哈希和数量以freeze-summary及verify输出为准。

E2C freeze `bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179`、源码ZIP6,327,273B/SHA `035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934`；C103条冻结/自检记录/70源，B199/63、A326/53、E2231/43、E1E188/33及13基线逐hash保持。原C1125通过、B完整FAIL/partial77及R519均不改。

完整交付后由负责人安排独立审查和是否另授新actual自有回归。本批不自派tester/full、不开真实媒体授权，不访问test_media内容/stat/hash、真实PF/runs、NAS/Gradle/ADB/设备/下载。JNI/P0/C14/历史FAIL、五产品namespace/READY限制保持，D1未通过、M0未启动。
