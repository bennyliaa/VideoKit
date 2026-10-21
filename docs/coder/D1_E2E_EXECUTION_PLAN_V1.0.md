# D1 E2E 一次 actual 自有全61回归执行计划 V1.0

2026-10-17。**本计划供独立tester在负责人交测后核验并执行一次；coder准备窗口没有运行此命令。** 它不授权真实媒体、mock回归、诊断补跑或重复full。

批次 `D1-E2E-201dffc63b60405da3046f21fa7ff26d`；固定机器LZF；包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2e`。唯一fixtures根名 `e2e-201dffc63b60405da3046f21fa7ff26d`，仅在本包selfcheck内。metadata状态目录execution和fixtures根均应在准备交付时不存在。

## 核验与单次命令

先按附录只读verify核完整源码/产物/原R脚本、批次授权和准备证据，并将负责人提供的外部SHA与 `evidence/e2e-freeze.json` 原字节摘要比对。生产原controller.run仍会拒绝full；不得以改src、改freeze、改profile或使用旧B预约绕过新层。

唯一正式入口形式：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2e\tools\launch-once.py' --run --batch-id 'D1-E2E-201dffc63b60405da3046f21fa7ff26d' --expected-freeze '<负责人报告中本E2E封存文件的SHA256>'
```

负责人交测报告提供上述SHA的具体值，替换整个尖括号字段；冻结文档不嵌自身封存摘要，避免自引用。不要用在未知副本上自算的摘要代替外部预期值。不给--run时仅Inspect，不产生执行目录、许可消费、资源查询或G/J/R。

## 预定门禁与实际执行

1. 严格验证batch/machine/package/runtime/code、C修后生产与D确认以及新immutableFiles；只允许SYNTHETIC/ACTUAL_OS_OBSERVER，mock或REAL_IO拒绝。
2. 正式请求以CREATE_NEW持久化唯一预约，在G之前消费。随后执行fresh≥2GiB门槛；不足时保存FAIL/拒绝且G未启动，不自动重试求低，不退款。
3. launcher只创建一次原G，绑定原父PID和G PID/creation。child再次核身份/冻结/唯一根并CREATE_NEW claim，随后才创建新自有fixtures及Engine。
4. 调用原preflight、61行原次序与原GC。R保持原LoadFrom；观察使用实际OS，原G在PF前baseline、J/R各原HELLO，不借D160/161、不重base、不调限。180秒及每行界保持。
5. 首FAIL/PENDING保留原失败并按原owner状态清理，不再完整回归、不跑mock或诊断。外层200秒仅停止等待/报告PENDING；未返回原IO/回调/进程继续保所有权，不能kill、关闭未知资源或假写零账本。
6. 原退出、Hub/IO/private cell/observer/日志关闭及结果文件hash由独立结果manifest记录；只在实际proof具备时写noInFlight。代码seal保持原样，运行输出不添加到不可变代码集合。

第5步的200秒通知不是launcher退出承诺：原launcher在同一线程继续持有并等待原Popen；driver有未排空Engine时也强留原owner，可能持续等待人工处理，不新建采集线程。首份launcher-result/result-manifest不覆盖；晚退出另写late-exit/late-result-manifest。即使G已退出，缺helper或关闭证明仍不能PASS/最终hash活动根；未知值继续保留。

原self-owned输入135168B，输出信用655360B；不是test_media素材，不创建真实runs。任何既有同名根、既有预约/claim、身份或完整性冲突均拒绝，不删除、改名复用或获得第二次许可。

## 硬界与收取

manifest/e2e-batch.json固定maxG1/maxFullAttempts1；wrapper metadata196608B，准备含seal819200B以内，原生产文件峰保守预留3178496B，总metadata/证据≤4MiB；fixture合计≤2MiB。原24/6/8、64/8 cell、452/544/101、IO/事务/32记录、180/200及G/J/R资源、日志/metric/fresh内存门槛全部保持。

静态检查只证明准备逻辑分支及不可变绑定，不证明未来机器fresh memory、进程峰、原helper退出或全61结果。tester收取实际原回执、result-manifest和原root证据后报告负责人，清楚分开PASS、FAIL、NOT_RUN与PENDING；不能把失败前partial断言或成功清理当完整PASS。

本许可来自E2E新批准，不复用E2B已消费许可；失败、低内存、启动失败或PENDING均无自动退款/重启。后续任何新批次、诊断、真实媒体或再次full须由负责人另派。本计划保持JNI/P0/C14/历史FAIL、产品namespace/READY限制；D1未通过、M0未启动。
