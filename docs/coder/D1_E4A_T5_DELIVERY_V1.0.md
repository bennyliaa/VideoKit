# D1 E4A-T5 开发交付 V1.0

2026-10-17。候选D1-20261017-E4A-T5。已完成测试专用流式Base64 ASCII→run-as私有文件解码路线，本机有限检查完成，设备诊断NOT_RUN。路径相对D:\CodexProjects\VideoKit。

## 路线与范围

T4L已证原app外部base/Download不满足双身份访问，原结果保持；不再试外部路径或创建框架目录。依据D1_E4A_T5_CODER_REQUIREMENTS_V1.0.md，本批明确以Base64覆盖旧工具“不做base64”的实现选择；这不是产品需求或许可证变更，不新增权限/root/manifest/架构/依赖。

新增stream_base64.py复用原T1 process强owner，以同一个原只读源FD完成预哈希、seek和流式发送。原始块24576B，短读另保留0..2B carry，标准Base64无LF、末尾padding正确；输出只含字母数字+/=，不含NUL或0x1A。编码数据不落盘，不整片缓存。预哈希与实际流式读取分别记录原始bytes/SHA；实际编码量与提交bytes/SHA另列，不能把编码提交344B说成原始文件落盘256B。

为复用已审强owner，薄适配器调用精确版本exact_process.py的Job/_reserve/_run等内部接口；包内字节锁定该版本，未宣称兼容任意未来版本。top-level expected/sourcePrehash/submitted字段对应编码字节，rawSource对象对应原始数据，encoding对象明确对应关系。原始读取每遍最多声明n字节，结束依据声明计数、原FD元数据和原SHA核验，不追加超界探读；streamReachedDeclaredEnd不是额外EOF观察。元数据相同不构成恶意并发源的快照保证。

exact_process.py仍13077B，SHA f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d；command_response.py与T4字节相同。原stdin实际close、源close、writer/drain/wait/线程返回与UNKNOWN强持有均保留。预哈希/源打开失败也按原Job保留关闭事实；未知归还不允许下一个I/O，迟到返回不升级旧attempt。

## 设备协议与独立证据

固定shell_v2、shell -T -e none；仅producer允许编码ASCII stdin，metadata使用-n。先检查原UID10221/pwd与files角色，准确新目录不存在。设备base64 -d支持尚UNKNOWN，先执行**无文件写**的AA==→base64-d→od：原printf/decoder/od各返回值经FD3分别写标记，另记pipeline rc和FD3实际关闭rc，最终hex须为一个00字节。不能仅以管道末端exit0认定解码成功；没有假定pipefail支持。只有全部原rc0/输出完整/原本机owner返回才准入。

随后一次原UID ps观察，疑似旧receiver即停不信号，未见也维持UNKNOWN_NOT_CLEARED。新私有目录files/e4_diag_T5P_TABLET_20261017_once独占mkdir/umask077，原目标不存在且非symlink。原producer输出BEGIN，再noclobber直接执行toybox base64-d到新文件；明确捕获并输出DECODE原rc，成功后另记录stat原rc/数量及END。同UID/pwd/PID/准确路径、decoderRc0/statRc0/256B齐全才继续独立proof。

非零原producer也保留完整原输出中的部分BEGIN/DECODE/END观察，例如decoder rc7；该观察不绕过原成功/归还门。最后独立新命令核目标普通非symlink、原app UID、stat256、前后元数据一致及head-c256有界原始SHA。编码SHA、exit0、ASCII假设或后续单独观察都不能替代这些条件。此处是文件字节证明，不是fsync/durability、播放、产品COMMIT或全局资源归还。

新批次D1-E4A-T5P-TABLET-20261017，nonce E4T5P_TABLET_20261017_ONCE；唯一目标上述目录/payload256.bin；旧26B及归档/媒体路径完全不访问。实际设备解码语法、工具支持与接收结果仍NOT_RUN，不从本机工具推断Android兼容。

## 有限本机证据

唯一main-001：**51项断言PASS**，33条顶层原调用记录＋关闭异常隔离用例内1条producer原记录。顶层原进程/管道均返回、topLevelRetainedOwners0；隔离用例内原Job仍UNKNOWN_RETAINED/1直到该用例解释器结束，下一I/O被拒绝，**没有以OS退出把它改为RETURNED**。实际本批没有生产诊断在途。证据evidence/local-check-results.json及check-attempt/result/checks.log绑定最终源码与原记录，原外层检查exit0/60s限时未触发，无补跑、无旧整套重跑。

编码直接使用生产EncodedSource与write_all，覆盖0/1/2/3/256/65535/65536/65537B、全字节、短原始块3字节carry、padding、正短写与信用；最大自有测试源65537B。另对0/1/65537B运行真实本机原pump→Python解码子进程，核原始/编码量与摘要。小测试的预期bytes和结果保存在内存，不能类比整片媒体缓存。

实际Git shell对全部6脚本集中sh-n通过；另用真实本机printf/base64/od执行1B探针及中间decoder强制exit7场景。后者原外层exit0但decoder原rc7仍被保存且拒绝，证明没有被管道末端吞错。两次探针的UID/pwd通过本机函数模拟，仅管道与实际工具返回为本机事实。

4个生产诊断本机模型场景：正常完整decode落盘及独立SHA；decoder非零；短件26B但exit0；完整长度错误SHA。真实本机文件由Python标准解码器以xb写入，故可验证字节及控制流；Android权限/UID/mode和设备命令回执为模型字段，不模拟SELinux。失败产物保留，原自有26B占位不变，同attempt拒绝复用。

关闭异常在独立解释器中注入原源close调用后抛错：即使底层原rawFD已关闭，包装close没有正常返回，原Job sourceCloseReturned仍false、强owner1，拒下一I/O，无第二次close/GC/信用退款。该异常历史独立保留，不计正常场景通过或进程退出清除。

实际ADB/device/真实媒体stat-read-hash/Gradle/依赖下载均0。Git所需Windows同步对象访问经自动审核允许，范围仅本机已有工具和自有小数据。

## 流量、内存与后续媒体设计

当前诊断raw256B→encoded344B、LF0；host原始prehash256＋stream256，编码prehash344＋实际提交344，设备独立原始SHA≤256B；额外前置探针为固定ASCII4B解码1B，只到od不落文件。metadata计划6/硬20、producer1、每命令15s/共同归还观察2s/日志1MiB。失败留产物，无重传/换路。

未来源身份仅抄自旧冻结元数据，**未重新stat/read/hash**。详细源绝对路径及旧SHA见tools/future-media-plan.json：

| 未来源 | 原始B | 无LF编码B | 原始预哈希＋流读B | 时限设计（未授权） |
| --- | ---: | ---: | ---: | --- |
| basic.mp4，原sample.mp4 | 349102 | 465472 | 698204 | transfer60s，独立hash15s |
| subtitle.avi | 736454656 | 981939544 | 1472909312 | transfer600s，独立hash120s |

两源合计raw736803758B、wire982405016B，编码两遍生成1964810032B但不落盘；host raw两遍1473607516B；设备独立hash总cap736803758B。padding导致不能简单四舍五入用N×4/3，实际为4×ceil(N/3)。AVI编码量低于原pump1GiB硬界；600s需要至少约1.56075MiB/s编码有效速率且尚未计预哈希/协议开销，不是实测速率或成功承诺。总transfer时限从预哈希前开始，无自动加时或重试。

编码块最多32768B，raw块24576B/carry≤2；工作缓冲设计预算256KiB，独立于文件长度，不含Python/ADB进程基线、OS缓冲与日志。测试记录peakTrackedBuffer仅被追踪对象长度，不能冒充总RSS峰。完整媒体没有编码副本或内存整片，源稳定性与原FD元数据限制仍需在正式批次披露。

未来只计划先MP4小文件、独立原SHA审查后另派AVI；复用transfer_base64即可。receiver/proof的目标、期望计数和有界hash参数须按新正式媒体批次实例化，当前CLI固定256B，**没有可运行的媒体入口**。私有临时件到原产品fixture槽的无覆盖发布及原正常产品方法另批审查，不自动复用旧attempt、不碰残件、也不把传输通过算播放通过。

## 交接

下一诊断直接入口见D1_E4A_T5_BINARY_TRANSFER_PLAN_V1.0.md，executionAuthorized=false，负责人审查后另派tester。小包仅必要原报告/收据/seal/两个继承模块与新源码/证据，不嵌套历史大包。旧T4路线失败、旧26B、T1/T3/T4及产品冻结保持。

新seal d1e4at5/evidence/ascii-freeze.json；精确清单evidence/source-manifest.json；完整包artifacts/D1-20261017-E4A-T5-source.zip。外seal SHA、ZIP身份/数量和只读verify实际结果集中交负责人，封存后只读。D1 NOT_PASSED/M0 NOT_STARTED/P0及历史FAIL保持。
