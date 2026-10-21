# D1 E2E actual 自有文件全 61 回归测试报告 V1.0

日期：2026-10-17。执行角色：VideoKit tester。批次：`D1-E2E-201dffc63b60405da3046f21fa7ff26d`。

**最终结论：FAIL，新增 P1 缺陷 1 项（E2E-F01）。** 已按授权完成唯一一次实际尝试，原始失败、已消费许可和结果均保留，无补跑。独立复核确认 PF 及全部 61 个自有文件场景完成、160 条原执行断言、输出和采样资源门槛满足；新增包装层把 PF＋61 的 62 条 checkpoint 当作“未完成61”而拒绝。不能将上述局部成功改写为本批次 PASS，完整批次通过数仍为 0。

实际资源已排空，原 J/R/G 退出、Hub worker join、GC/n32 原日志关闭返回及父 Popen 句柄实际关闭证据完整，**无在途任务**。D1 未通过，M0 未启动；真实媒体、设备及产品准入均未放行。

## 1. 执行依据与冻结核验

依据 E2E tester/coder 正式需求、负责人正式交接授权及 E2D 报告 §4。核对三份开发文档、新 launcher/admission/runtime/driver 源码和原生产编排后执行。封存与实际前置记录：

| 项目 | 结果 |
|---|---|
| 外部 expected seal | `aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a` |
| E2E-source.zip SHA256 | `2a1202f2bba27d86f20f73af6fe286d5574e0575d67880eb865eb0644bc4db34` |
| 源码/不可变集合 | 73/90，逐长度/hash、ZIP 精确成员一致，运行后仍未变 |
| 生产绑定 | E2C 修后 32 源码＋5 配置、10 原产物及原 r-helper 字节不变；未编译 |
| 开发准备检查 | 153 条纯准备检查，未作为实际功能或资源证明 |
| 启动前目录 | execution/selfcheck 均不存在 |
| 父 fresh 可用内存 | 2,597,638,144 B ≥ 2GiB |
| 子 fresh 可用内存 | 2,574,761,984 B ≥ 2GiB |
| 原采样器 fresh 可用内存 | 2,581,688,320 B ≥ 2GiB |
| 一次性门禁 | CREATE_NEW 预约先 G；父子身份/claim 先 fixtures/Engine；spawnCalls=1，无退款 |

默认生产 controller 的拒绝仍保留。本轮使用新批准的独立 wrapper，SYNTHETIC authored files＋ACTUAL_OS_OBSERVER，无 mock/REAL_IO、test_media stat/hash/读取、设备、Gradle、下载。源码封存采用已交接的 e2e-freeze.json 映射，未删除旧 seal 或修改 R 启动脚本。

前后两次已审读只读 verify 均 PASS；第二次同时核对原结果清单 146 个输出文件及预算。tester 自有检查不导入候选代码、不新增 OS 采样。见 [执行前独立核验](D:/CodexProjects/VideoKit/docs/tester/D1_E2E_EVIDENCE/pre-execution-review.json)。

## 2. 实际执行结果及新增缺陷

仅调用负责人指定命令一次。原 launcher PID39108/creation100ns=134366511032212370；原 G PID40980/creation100ns=134366511035829924。原 G exit2，命令工具返回 exit_code1，耗时约8.53秒。没有200秒 PENDING、强杀、重启或第二次尝试。

**E2E-F01 / P1：完整回归结果计数包含 PF，wrapper 恒拒绝正常完整结果。**

- 位置：[e2e_driver.py:155](D:/CodexProjects/VideoKit/docs/coder/d1e2e/tools/e2e_driver.py:155)。`witness['status']=='PASS'` 时要求 `rows==61`，否则写 `INCOMPLETE_FULL_ROW_COUNT` 并改为 FAIL。
- 原 [preflight](D:/CodexProjects/VideoKit/docs/coder/d1e2e/src/phases.py:6) 调用 PF 的 Flow.finish；原 [Flow.finish](D:/CodexProjects/VideoKit/docs/coder/d1e2e/src/gengine.py:277) 将 PF 和每个场景均加入 results。Cleanup.finish 返回 `len(report['rows'])`，正常完整结果是 PF 1＋场景61＝62；GC/n32 另由返回通道见证。
- 本次完整原行序列正好为 PF＋61 个唯一场景，P10-D/P10-C 按批准移至最后；无缺失、重复或额外场景。全部 row 的 control/query 配额和行时限符合 manifest。原 preclose status=PASS/error=null，160 条断言；wrapper 最后检查才改写最终 driver status=FAIL。
- 影响：正确跑完的完整批次也不能获得正确判定；153 条准备检查未覆盖原 PF 与真实结果计数的组合。tester 执行前静态审核亦未识别这一计数语义，缺陷由本次实际运行暴露。
- 修复建议：明确 PF、61 个场景与 GC 三类完成证据，核对场景 ID 精确集合、唯一性、批准顺序及各完成记录，并单独核 PF 与 GC/n32；不要只把硬编码61改成62就视为完整性证明。补充有界离线判定检查，覆盖完整、缺行、重复、乱序及额外行。
- 本批处理：保留原 FAIL/退出码/预约、原 preclose PASS 和全部结果，不覆写，不退款、不补跑。可由负责人另派最小判定修复与基于本次封存结果的只读复核；修复版本是否可采信原执行证据由负责人裁定。本报告不自授新 full 或自动追认 PASS。

## 3. 已执行、未执行与独立输出验证

实际完成 PF、全部61场景及 GC/n01..n32；场景范围31个源场景＋30个输出场景。场景未执行数 0，但包装层最终 FAIL，不能把160条断言或61个 checkpoint作为整批通过数。

完整逐行 control/data/query/time 结果及已执行/未执行清单见 [completed-and-not-run.json](D:/CodexProjects/VideoKit/docs/tester/D1_E2E_EVIDENCE/completed-and-not-run.json)。未执行：真实 test_media/REAL_IO、设备/C14、五项产品 namespace durability 变体、第二次 actual 尝试。五变体仍为 NOT_RUN_DURABILITY_UNPROVEN，本轮工具 READY/OS_DATA_SYNC_ACK 不代表产品 OutputToken/COMMIT 或断电持久性。

独立重新读取已关闭输出并核字节及 SHA256，未调用候选校验函数：

| 输出 | 独立预期与实际 |
|---|---|
| T01.out / T05.out | 各32字节，值0..31 |
| T02.out | 10字节：Z、0、x、y、0、0、0、a、b、c |
| T03.out / T04.out | 各1个零字节 |
| T06.out..T10.out | 均0字节 |
| L.bin / C.bin / Z.bin | 各131072/4096/0字节，独立生成预期模式逐字节一致 |

原 result-manifest 包含其自身以外145个文件；tester 核全部146文件集合、长度/hash、分类及预算一致，归档完整原始输出。result-manifest SHA256：`baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea`。preclose SHA256：`702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032`。

见 [独立结果审计](D:/CodexProjects/VideoKit/docs/tester/D1_E2E_EVIDENCE/independent-results-audit.json) 和 [原结果清单归档](D:/CodexProjects/VideoKit/docs/tester/D1_E2E_EVIDENCE/execution-archive/execution/result-manifest.json)。

## 4. 资源、IO、日志与时间门槛

原 G PF/n01 前基线固定，J/R 原 HELLO 实例基线固定，未后移或重置。5个实际采样周期，最大已记录间隔约1.672秒≤2.5秒，样本返回时限未触发；所有绝对值与增量均在原界内：

| 角色 | 原线程→采样峰 | 原句柄→采样峰 | WS采样峰 B | private采样峰 B |
|---|---|---|---:|---:|
| G | 5→12（+7） | 159→204（+45） | 28,438,528 | 18,780,160 |
| J | 24→24（+0） | 266→266（+0） | 70,881,280 | 373,424,128 |
| R | 26→26（+0） | 503→505（+2） | 89,251,840 | 29,491,200 |

G符合线程16/+12、句柄256/+64及内存256MiB/+128；J/R符合64/+32、512/+128及J768MiB/R512MiB/+256。离散采样不构成连续OS峰值或所有未来运行保证；本批未再现旧G369/+209或R519超限，但旧 FAIL 仍保留。

- private cell 累计64/archived64/active0/retained0，峰1，达到累计硬界但未超过；Hub64次通知，最终全部静默。无累计退款、强GC或历史对象删除换额度。
- 托管资源峰23≤24、媒体句柄峰5≤6、buffer峰1≤8。observer identity3（其中借用2），5周期，18开18关，同时自有峰1，最终信用0，无 close UNKNOWN、nativeQueryPending。
- 原预算：N351＋query83新/18重放＝452，低于硬544；input请求1,573,492 B/59次、validation128 B、output信用655360 B/10目标、records32，均符合原预算。源实际请求比预留1,573,522少30 B，不退款扩读。
- metadata累计请求/实际写入均6,431,845 B，UNKNOWN请求0、commit HEALTHY。该值是累计覆盖写入量；文件占用峰664,677 B，与4MiB存量/证据合计口径不同，未将覆盖写入伪装成零成本。
- 准备107,814 B＋执行metadata704,997 B＝812,811 B≤4MiB；fixture135,244 B≤2MiB；wrapper40,320 B≤196608，production占用664,677 B≤3178496。
- 最终global.log=93,440 B≤131072；独立分解event92,902 B≤104320、metrics538 B≤26752。运行回执中的event92,828/metric538在最后GC/n32 READY_TO_CLOSE前取值，实际最终event多74 B；原返回通道证明随后flush/fsync/close实际返回，不能靠盘上READY_TO_CLOSE行替代。
- 父/子wrapper完整性读取分别80,333,792/80,479,115 B，150/152次≤256MiB/8192；结果hash812,731 B≤6MiB。无父PIPE/collector worker；单次启动临时句柄6为静态预留上界，不声称OS实测峰。
- 原行时限均满足，完整唯一命令约8.53秒内返回，180秒与外200秒停止等待界均未触发。无额外诊断或采样补跑。

## 5. 退出与最终处理

原J PID40896、owner03c3668c-6a2d-4c33-b6f7-888ab4d402c0；原R PID31648、ownerf9073814f11c42389cc1108fff33b4e3。两者原退出证明均exit0并绑定原实例；GC按原顺序关闭pipe/process句柄、Hub两原worker实际entered/exited/joinReturned/THREAD_JOIN_PROVEN。原IO收尾和日志GC/n32 flush/fsync/close已返回，remainingResources=0。G原exit2实际被父观察；父原process handle关闭证明为true、spawn信用0，wrapper metadata/identity信用0，无UNKNOWN。launcher原调用亦实际结束，无被遗留的等待会话。

本轮新增缺陷E2E-F01集中交负责人安排修复。保留唯一许可消费和完整证据，等待另行正式派发，不自行下一批。冻结源码和历史证据均未修改。host JNI BLOCKED、Kit/Flutter/AAR/Android/licensing P0、产品namespace/READY限制、C14限制及历史G/R FAIL不变，C14平板功能执行仍0。**本批FAIL；D1 NOT_PASSED，M0 NOT_STARTED。**
