# D1 E2E 新 actual 自有回归批次准备交付 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2e`。依据 [正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2E_CODER_REQUIREMENTS_V1.0.md)，本批仅准备一个新的自有文件 actual OS observer 全61回归入口、机器/批次授权与静态门禁，交独立tester核验后一次执行。**本窗口没有启动driver G、J/R、完整回归、OS诊断或fresh内存检查；没有消费新许可、创建执行目录或fixtures。**

批次 `D1-E2E-201dffc63b60405da3046f21fa7ff26d`，机器 `LZF`，唯一自有根名 `e2e-201dffc63b60405da3046f21fa7ff26d`。状态 **PREPARED_NOT_RUN_PENDING_TESTER**，只允许 `SYNTHETIC + ACTUAL_OS_OBSERVER`；REAL_IO/mock关闭。准备完成不表示实际回归通过，旧G369/+209与R519 FAIL、E2B已消费许可保持；D1 NOT_PASSED、M0 NOT_STARTED。

## 原生产身份与最小适配

32份生产源码、原branches manifest/profiles共37文件及E2C.dll/9 class共10产物绑定E2C修后版本，并承接E2D确认；没有改生产或重编。原 `tools/r-helper.ps1` 从E2C逐字节复制，保绝对Assembly.LoadFrom、E2C_KEY和原协议/owner/FFM/compact链。

E2C freeze `bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179`、source ZIP `035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934`；E2D freeze `f0a3e8fc9ae7e6e8c3def52d0002d23af77212ad35cb016a612e34e45f42de1b`、source ZIP `6c6eef8c0d9541aefe1eb807a312d1fce7ba968038c127e565af9becd7ccf9d8`。

必要适配全部位于新增tools：独立launcher/准入/driver，不调用或修改原controller.run的范围拒绝，不恢复其不可达full入口。新driver在新claim后直接调用原Engine/Scenarios/preflight/Cleanup/stop_failure，保持原61顺序、GC、首失败和UNKNOWN收尾语义，不猴子补丁生产函数。

原R启动脚本会拒绝活动包下 `evidence/freeze-summary.json`，故本批使用独立不可变封存文件 **`evidence/e2e-freeze.json`**，不生成旧名、不删除任何旧seal，也不改原R脚本。这是本新授权批次的封存身份映射。正式tester须从负责人报告取得该文件的外部预期SHA并传给launcher；封存自身不能包含自己的摘要。原生产真实入口仍关闭，新层也不能读test_media。

## 一次性门禁与停止合同

`manifest/e2e-batch.json` 固定机器名、包根、运行时身份、批次/唯一根、C/D生产身份及硬界。默认Inspect不创建execution/selfcheck、不采资源、不启动或预约。mock/REAL_IO、错误批次/机器/代码完整性等拒绝不得自动重试。

只有tester明确正式启动才持久CREATE_NEW预约，发生在任何driver G之前；本批采用更保守的预约即消费、不退款。fresh≥2GiB检查只在正式预约后执行，低内存也停止且不自动重启求低值。最多一次Popen G/full，创建失败、FAIL或PENDING均不恢复许可。

launcher原PID、原G PID/creation及批次/封存/唯一根绑定；child核原父身份与自身原实例并CREATE_NEW claim，先于fixtures、Engine和Native。唯一根仅在本包selfcheck下，原CREATE_NEW创建，不能删除重用；不会创建真实runs或取真实输入。执行结果目录与代码集合分离，结果manifest另收路径/字节/hash和原退出/剩余所有权，不修改冻结准备证据。

首FAIL/PENDING保原回执及有界原owner清理，不追加回归/诊断、强GC、强杀或替换owner。200秒只停止等待/报告PENDING，不推断native已返回，不撤销原process/pipe/worker信用；原owner未排空时不能写noInFlight。所有运行时读数和退出事实均须由未来tester实际执行产生，本窗口的合成假对象不作此证明。

200秒通知写出后，原launcher仍在原线程持有同一个Popen；driver若尚有未知Engine/Channel/cell所有权，也持有原Engine并保留首PENDING，不靠函数返回或进程析构释放。只做等待/保留，不增加采样、RPC或第二次GC；可能持续等候人工处理。G退出而helper/关闭证明不足时，结果清单保持不完整，不读取仍可能变化的root冒充最终账本。

## 原门槛、准备验证与预算

保持fresh≥2GiB；G PF前固定baseline，线程16/+12、句柄256/+64、WS/private256MiB/+128；J/R各原HELLO线程64/+32、句柄512/+128、J768MiB/R512MiB及+256。24/6/8、总cell64/活8、452/硬544/101query、输入/输出/validation/事务/32记录、原180秒/外200停止等待、1s/201/gap2.5/返回后0.1、event104320/metrics26752均不改。

本次153条静态/纯合成内存backend检查全部通过，仅加载纯门禁和编排函数，未导入生产模块或真实runtime backend；默认Inspect另用import硬守卫验证。没有启动Engine/Native/Channel/Hub/Thread/Popen/Win32或fresh资源查询。覆盖Inspect、授权/身份/完整性、唯一预约竞争、低内存不启动且不退款、claim先fixture、原父子实例、超时不kill/关闭/退款、独立输出与总账。证据见本包audit，不加旧C1125、D六点或B partial77到本批通过数。源码集合73文件，原生产/配置37、原r-helper及10编译产物均逐hash绑定通过。

准备fixture≤2MiB/证据≤4MiB，并为一次未来执行保守留足空间：准备日志含seal≤819200B；原生产文件峰预留3178496B＋wrapper metadata196608B合计仍≤4MiB。3178496是原文件峰的保守预留，不声称它全是日志。fixture另预留原135168B输入＋655360B输出信用；不扩原IO预算。wrapper身份验证、原pipe/metadata和结果哈希IO独立有界计账，不藏入452。

完整性读取每个原父/子进程分别上限256MiB、8192文件次，逐64KiB块hash；结果收取由原launcher另限6MiB/512文件。wrapper不建PIPE/采集worker；按本地CPython启动实现，父层DEVNULL临时句柄上界4（共享NUL句柄＋三个可继承副本）、原process handle1、临时primary-thread handle1，启动阶段父层合计上界6；另序列身份查询临时handle峰1。此为独立成本预留，未测OS峰，未知关闭信用不释放。launch以独占临时文件完成write/fsync/close后一次无覆盖发布；暂存与两个结果manifest均占wrapper预算。

封存的immutableFiles含源码、原依赖产物、配置、准备证据和三文档，排除未来execution/和唯一selfcheck根；运行后代码hash集合不变，结果manifest单独记录实际产出与预算。准备与执行的fixture/证据合计不能超2MiB/4MiB，不能用删失败证据换预算。

源码ZIP、C/D至更早只读依赖、source manifest、只读verify及三文档齐备。后续先由负责人交tester核验，再使用报告中的具体一次启动命令；本窗口不代执行。没有test_media字节/stat/hash、真实PF/runs、设备/Gradle/ADB/NAS/下载。JNI/P0/C14、五产品namespace/READY及历史FAIL限制保持。

执行与身份映射详见 [EXECUTION_PLAN](D:/CodexProjects/VideoKit/docs/coder/D1_E2E_EXECUTION_PLAN_V1.0.md) 和 [EXECUTION_APPENDIX](D:/CodexProjects/VideoKit/docs/coder/D1_E2E_EXECUTION_APPENDIX_V1.0.md)。
