# D1 E2 检查入口、停止与冻结说明 V1.0

2026-10-16。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2`。默认只读Inspect，真实入口永久关闭于本配置候选；后续批准不能仅改JSON自放行。合成/编译入口冻结后拒绝原地重跑，另建授权批次并保留旧证据。

## 只读入口

已有Python `C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`；PowerShell7.6.5/.NET10.0.11位于同runtime的`dependencies\native\powershell\pwsh.exe`；JBR21.0.10位于 `D:\Android\Android Studio\jbr\bin`。无dotnet SDK、新下载或设备依赖。

完整性核验不访问媒体路径：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2/tools/verify.py'
```

默认配置Inspect读取本包4个JSON和manifest，不stat/open媒体、不创建run目录：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2/src/admission.py' --inspect
```

也可 `tools/launch.ps1 -Mode Inspect`。输出61项条件probe配置、独立审批/Java版本桥/真实绑定/指标与日志信用等blockers，executionAllowed恒false。`tools/audit.py --audit`只读核已有证据，`tools/profile_audit.py`只读取配置及docs历史来源，不解析真实输入文件；媒体路径只做词法比较。

下列是**拒绝检查**，应返回2，不能当执行命令：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2/src/admission.py' --request-real E2-CONFIGURATION-DENIED
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'D:/CodexProjects/VideoKit/docs/coder/d1e2/src/controller.py' --synthetic-selfcheck --profile REAL_IO
```

两者本批实际均返回2并保存entry-denials；REAL_IO分派位于fixtures/Engine前，Engine第一句require_synthetic也在Native初始化前拒绝真实绑定。e2_checks另用fatal open/mkdir/media/helper哨兵核request函数零副作用。无全局扫描、NAS、复制素材进SelfCheck或重算hash。

## 本批执行及证据

tools/build.ps1 -Compile一次，现有Roslyn/javac成功生成E2.dll/JavaHelper两个class，协议key E2_KEY；无需repair重编。原native/Java身份绑定语义保持，未加JNI/FFM。

tools/run-selfcheck.py --run一轮，仅显式SYNTHETIC profile：L131072/C4096/Z0/B65536；PF16＋61行＋GC32，159项PASS，回执 `evidence/selfcheck-1792165512531930500.json`。去掉路径名猜B后完整流程保持，绝不将此缩小边界当真实2GiB证明。

tools/check-targeted.py --run两轮：早期712保留；补未计费IO反例后最终716，回执 `evidence/targeted-1792165801504473800.json`。最终合成总875；不会累加早期、旧E1E或配置元数据检查冒充媒体结果。

tools/check-observer-self.py --run-self只执行一次，作用于该配置Python进程自己的PID/创建时间，6项PASS，回执 `evidence/observer-self-1792165801337125700.json`。实际snapshot先关闭，再打开/关闭自身query句柄；同时峰1，ledger信用0，无worker/RPC/media。仅证明本机x64结构/API绑定这一自检，不是G/J/R基线、真实PF或阈值批准。普通运行该工具默认INSPECT_ONLY，冻结后拒绝--run-self。

metrics组件不在import时调用native；MetricObserver仅认可明确mock专用marker/模式，真实批准不在本包产生。候选Win32 reader获取只读OS counter，不读进程内存内容；线程快照只保目标计数。所有query/close有原owner事实；未知close保句柄及observer信用，不重试。0.1秒检查仅在OS调用返回后成立，后续接线须复用既有IO池和原pending事实，不能增加线程或强杀。

## 停止与记账

所有观察/编码/写日志耗时属于原行和全局180秒，不另加时间；外层200秒只停止等待。指标提案1秒/201周期/gap2.5秒、绝对/基线增量和2GiB可用内存均PROPOSED，未替代24/6/8、452/544或IO硬限。缺指标、身份变化、当前行余时不足、无法预留observer信用/日志容量都停止新接纳，保PENDING，不静默跳过后称已测绝对峰。

日志提案为既有131072B global.log分events104320＋metrics26752，201×128＋1024头；必须获批且证明组合能装下。现E2合成事件92901B只是参考，不保证未来实耗。每次metadata write仍exact_write且累计字节单独记，不加journal事务/媒体read/RPC。runtime-policy注明缓存名义计数与真实语言堆开销的差异，不能将受管23当全部线程/句柄/内存。

正常合成n32前完成receipt/PF意图和IO排空；真实flush/fsync/close返回后G不再写盘，原stdout见证关联关闭前SHA `3ff2bf65c61b5c6bc49740d981089a20a518735deced45942d2748ca0ac3e2c4`。恢复仍将磁盘GC/n32意图留待外部见证，不能独立当close成功。所有原helper实际wait code0，受控测试线程均join，无本批已知在途。

## 冻结及后续准入

全部返回后一次freeze：源ZIP包括src/tools/manifest/profiles/upstream-e1e完整源码关系；产物、三文档、全部证据和自检文件由source-manifest/freeze-summary逐项字节/SHA关联。旧E1E188冻结/自检＋33源码核验不变，13项基线保留。只读verify不构建、不启动helper、不访问真实媒体。

当前默认batch/outputRoot为null，规划真实runs根从未创建。后续只能由负责人根据独立审查明确安排：真实命名空间及Java opened-FD桥的必要适配/验证，指标与日志信用审批，冻结SHA绑定的新批次授权，再做现场版本/资源准入；本窗口不自行派tester/真实执行。未读真实媒体字节、未真实PF/媒体/Gradle/ADB/设备/下载，JNI/P0/历史FAIL/C14保持，D1未通过、M0未启动。
