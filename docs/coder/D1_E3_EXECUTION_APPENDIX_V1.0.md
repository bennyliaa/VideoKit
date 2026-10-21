# D1 E3 执行与证据附录 V1.0

2026-10-17。以下命令以项目根 `D:/CodexProjects/VideoKit` 为工作目录。默认入口均不启动真实 IO；实际执行需负责人后续正式交接。

准备包目录为 `D:/CodexProjects/VideoKit/docs/coder/d1e3`。`src` 保存本批完整32源文件；`tools` 保存授权、原父子运行、通用完成判据、纯数据检查、自有小文件探针、编译、审计/冻结/只读 verify。四份 profile 和完整61分支 manifest、固定 e3-batch.json 一并冻结。新 E3.dll/java-e3 为运行产物，旧 E2C.dll/java 仅为10项历史基线。当前运行时子集与所有不可变文件逐项列在 e3-freeze.json；execution/runs/selfcheck 分集，selfcheck 另有 hash 清单。

只读核验命令如下；`$ExpectedFreezeSha256` 必须取自独立完整交付报告，不通过读取待核验 seal 的 hash 自行填充信任值：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e3\tools\verify.py' --expected-freeze $ExpectedFreezeSha256
```

默认 Inspect 命令如下，许可无需提供：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e3\tools\launch-once.py' --inspect
```

唯一正式执行命令如下。只有负责人正式交接后，才将独立报告中的 freeze 与负责人单独释放的许可分别放入 `$ExpectedFreezeSha256`、`$CoordinatorGrantToken`；包内没有后者。此处仅记录合同，本批未执行：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e3\tools\launch-once.py' --run --expected-freeze $ExpectedFreezeSha256 --batch-id 'D1-E3-11a896d3c2c34483ba2dff60fa63f5c8' --grant-token $CoordinatorGrantToken
```

不得直接运行 controller full、以任意 approved JSON 绕开入口、替换为 mock、复用已消费的 execution/root 或调整本批限制。RuntimePermit 必须在原 child 的 durable claim 后签发，constructor 及 binds 共同核固定 commitment 和进程内 secret/HMAC；仅导入私有 issuer 或伪造字典无效。父 CLI 接收许可后仅通过 child 临时环境传递，child 先 pop 再导入生产 helper 代码，receipt 不记录许可。

准备验证不等同执行：check-preparation.py `--check` 只读取固定代码/JSON、已冻结上游三份小元数据并运行纯内存判据，没有 Engine/原生对象/OS采样/媒体 stat/真实 claim。两个未来 batch/不同 root、不同 freeze、173/181个断言的模型证明判据不固定旧160。语义负例会重新绑定模型 preclose/trace hash，避免所有负例只因未更新 hash 而被拒；另有独立错 hash 负例。

build.ps1 的唯一 `-Compile` 预约已消费，仅用于一次集中工具编译，不是正式 IO 预约。C#/Java 各1次、零 repair；封包后不再编译。check-native-input.py 的本地探针预约也已消费，仅两个新建4KiB自有文件，25项 Java 原 HANDLE 检查，两进程原 exit0，无 R/生产G/真实PF。该脚本默认Inspect，禁止覆盖或再次生成原探针证据。正式 E3 预约仍未消费。

| 准备证据 | 含义 |
|---|---|
| evidence/build-reservation.json、build.json | 单次编译预约、原源码及新二进制 hash |
| evidence/native-probes-reservation.json、native-probes.json | 两项自有文件探针及原退出/25断言 |
| selfcheck/java-bridge-strict-*/L.bin、stdout.json、stderr.log | 自建fixture及原始探针回执；不是媒体副本 |
| evidence/preparation-checks.json | 本批纯数据/静态检查、负例、未来参数化模型 |
| evidence/audit.json | 上游、原分配/profile、编译、两类验证及未消费状态审计 |
| evidence/source-manifest.json、artifacts/E3-source.zip | 当前完整源码与一个完整E2F依赖容器 |
| evidence/e3-freeze.json | 外部hash绑定的seal、不可变/运行时/自检集合、准备总账 |

seal 采用 e3-freeze.json，避开原 r-helper.ps1 对活动 evidence/freeze-summary.json 的明确拒绝；旧 helper 策略没有删除历史 seal 或重写旧冻结包。新 r-helper 保持绝对 Assembly.LoadFrom，目标改为本批 E3.dll。

运行时每个源文件/工具/四profile/manifest/新二进制均在 parent 和 original child 入口按 seal 校验，精确文件集校验拒绝增删；完整离线 verify 另核所有不可变/上游/源码 ZIP/自检。外部 Python DLL 和 CPython subprocess.py 为正式入口另列有界完整 hash，准备阶段没有重 hash 系统运行时。CPython DLL固定SHA256 `2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1`；原 subprocess.py固定88747 B/SHA256 `85d29b2bf0249f5436838298c9a60ee93508b1102e9ac43b001f8a7e7ae8f375`。

源码读取每次命令的实体文件 bytes 与 ZIP 成员 logical bytes 全额记账，包含完整压缩容器和成员解压内容，合计≤268435456 B/8192次；以已验证 fingerprint 缓存避免同命令再次打开同一文件。ZIP解析从已计费原始压缩 bytes 的内存 BytesIO 进行；该账衡量实体读取及逻辑解压，不宣称覆盖所有内部CPU/内存拷贝。只核当前 E3 外层与完整 E2F 容器一层，内部更旧ZIP作为hash绑定成员而非递归展开全部历史副本。核验结果逐项报告 physicalFileBytes、zipLogicalBytes、physicalFileReads、zipEntryReads。

准备元数据上限819200 B，fixture上限1441792 B。前者加生产3178496 B及wrapper196608 B恰为4194304 B；后者加输出655360 B恰为2097152 B。本批8192 B fixture无需复制真实 L/C/Z。全量结果仅在原 G exit已观察且全部 original noInFlight 后 hash，限6MiB/512次，输出fixture限655360 B，wrapper限196608 B，manifest自身大小也入账；UNKNOWN/PENDING不扫描为假完整。原preclose最多131072 B，断言trace最多1024项、label最多160字；同一trace只在preclose完整保存，return witness保存count/hash。独立wrapper元数据句柄峰1、identity句柄峰1、spawn峰6，均不冒充生产24账内零开销。

原E2E 61行完成后因旧wrapper计数而FAIL的结果和E2F有限证据重评均不可修改；新通用门禁仍未接收真实结果。只读verify能校验将来的既有结果完整性，但不改判、不启动、不消费、不自动收集或修复。封包与测试通过只表示启动层准备交付，不表示D1/P0/产品媒体或持久性通过。
