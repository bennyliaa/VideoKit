# MEDIA3_CONTAINER02_FIX 测试要求 V1.0

2026-10-21；负责人正式派D1_MEDIA3_CONTAINER02_FIX。

依据独立完整报告docs/tester/D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md，13782B，SHA256 4d8853e56b18de0605309a6ba627b674c222d8b846a670d4cb59754bc71a4e87，结论FAIL_NEW_P2_WITH_FUNCTIONAL_SCOPE_OPEN。新使用extractor/decoder同版本有限离线来源许可/strict证据通过保持；真实容器/合格fixture/平台效果仍OPEN/NOT_RUN。旧候选与证据完全保留，D1未过M0未启。

MC-B01/P2：TemporaryOutput.inspectHostMp4Structure在原REOPEN ACK已到但同原任务线程尾段尚未返回时，先置hostInspectionAttempted，再将OUTPUT_ORIGINAL_PENDING记首错，未执行检查资格永久耗尽。准确同原任务返回后不能继续；不是实际超时、取消或解析失败。

修复须集中统一这个入口及其共享的检查准入/暂待原归还状态：准入前暂待与实际检查已开始后的真实失败区分，保留同一原REOPEN响应及授权Provider，观察原observer/worker真实返回后能够继续尚未执行的检查；不得盲目第二次reopen/RPC、重发、清真正超时/取消/失败/UNKNOWN或提前释放。实际解析失败后的重入策略保持明确，不能借修复循环重试。结构检查成功仍不能validated、READY或COMMIT。沿用8MiB累计/16MiB输出/64KiB块/总源2每源1queue0及原返回门。

有限关键顺序集中覆盖：REOPEN ACK先/原线程尾段后、原线程先/ACK后、同原observer未返、真实超时/取消/abort/权限或坏Provider/真正结构失败、合法观察后单次继续；覆盖共享入口同类路径，禁止只为单例改字符串求绿。主机缺Android类时，用明确前解析准入证据证明已继续到正确边界，不能冒容器正例。依赖/版本/许可不扩、无新平台替身或编码器/设备/ADB/占用操作，不并发Gradle/缓存写。

当前等待完整新候选，尚未正式交测，不读浮动源码、不重跑无变化旧套件。负责人核完整冻结后另派：独立核seal/ZIP/旧来源保全/来源许可strict，实际文档入口及生产JAR优先/源码双路径；自行复现MC-B01无cancel/abort干扰，保留真实超时sticky不重发对照，验证合法观察后复用同原Provider仅一次继续、所有原observer/worker返回和keeper归还。集中审同类先后矩阵及原05/01回归，真实容器目标不因有限修复通过关闭。整包报告集中通知负责人，由负责人统一回交修复；无设备/Gradle/共享缓存修改。

## 2026-10-21 完整冻结正式交测

负责人核主报告cfe817dd8d966f4cebdc8710a243d47b217f1ff16139f6099de91b29029efbc6、seal0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d全部676项含ZIP与ZIP675唯一成员计数一致，正式启动独立整包复审。准确候选docs/coder/d1media3-container02，顺序决定D1_MEDIA3_CONTAINER02_FIX_ADMISSION_ORDER_V1.0.md。

实际新输出目录执行冻结review_all.py，源码和生产JAR757e53a49d92a9b2148417e0b37ed9680162a7709b1493029759e58ce08dfd8f优先双路径。自行复现无cancel/abort干扰MC-B01、ACK先/原线程先/同observer尾段及共享两个入口交叉继续；确认同原Provider而非恰好同配额、REOPEN只一次。真正超时/取消/权限/坏值/UNKNOWN不清，实际检查开始失败后不得无界重试。核首错、准入资格、原registry/observer/worker归还和既有05/01边界。

不以coder22/8或60进程退出0代独立结果。完整审产物/签名/继承许可strict/旧封存差异。真实容器/合规fixture/结构成功缓存/解析过程权限变化、恶意atom内部内存、SeekMap/NAL/时基/EOS与平台仍OPEN/NOT_RUN，不加替身求绿、不凭受控4B validator回归签隔离验证或READY/COMMIT。无设备/ADB/占用/Gradle/共享缓存。整包结果集中报告负责人，之后再统一派发。
