# D1 E2F 原封存证据只读重评 V1.0

2026-10-17。这是 **EVIDENCE_REEVALUATION**，原E2E批次结果仍为FAIL。原G exit2、调用工具exit1、160条原执行断言、一次预约已消费均保留；本报告不追认原PASS、不新增actual计数。

## 输入与完成判定

固定读取d1e2e原seal `aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a`、result-manifest `baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea`、preclose `702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032`。原90项不可变文件及原输出146文件逐hash核对；原manifest包含145项，自身另计，不把原preclose PASS单独当最终成功。

PF必须首条且有原controls/data/query/时限完成checkpoint。61场景按批准ID精确集合和唯一序列匹配，P10-D/P10-C按原批准位于末尾；缺失、重复、乱序、额外或未完成均拒绝。逐行control/data/query与批准配额相符，elapsed有限且在原seconds内，原160断言及总usage跨回执一致。原global控制/数据槽的完成、批准预期拒绝与原WAITING归档证据独立核验，不能仅接受62这个总数。

GC/n01..n31的原顺序/完成均核验。n32盘上READY_TO_CLOSE只证明意图，必须同时有原driver短回执 `logClose.id=GC/n32`、`closed=true`、`method=flush/fsync/close actually returned`、remainingResources=0等实际返回通道；缺失或资源未知时拒绝。PF、61场景和GC不是同一计数类别。

## 原资源与输出事实

资源模块交叉核预约/launch/claim、原父PID39108/creation134366511032212370、G PID40980/creation134366511035829924，以及J PID40896、R PID31648和各原owner/creation。原G实际exit2，J/R各原exit0，父原process handle已关闭；源/输出scope与hash不能被改成新身份。

| 角色 | 原线程→采样峰 | 原句柄→采样峰 | WS峰B | private峰B |
|---|---|---|---:|---:|
| G | 5→12（+7） | 159→204（+45） | 28438528 | 18780160 |
| J | 24→24（+0） | 266→266（+0） | 70881280 | 373424128 |
| R | 26→26（+0） | 503→505（+2） | 89251840 | 29491200 |

原五周期、最大已记录gap约1.672秒、各固定绝对/增量界与fresh≥2GiB均按原记录核对。private cell total64/archived64/active0/retained0/peak1；托管OS峰23、媒体5、buffer1。原Hub两worker实际entered/exited/joinReturned及THREAD_JOIN_PROVEN，原observer/IO/native/日志收尾与helper退出无在途，仍须由原回执支持，不能靠G退出单独推断。

原N351＋新query83/重放18＝452，硬544；input1,573,492B/59次、validation128B、output信用655360B/10目标、records32。metadata累计请求/写入6,431,845B是覆盖写入总量，文件峰664,677B是存量；两者分开，不能将累计覆盖写入说成零成本。原准备107814B＋执行metadata704997B＝812811B≤4MiB，fixture135244B≤2MiB。

原global最终93440B，独立分解event92902B/metric538B；原短回执event92828B取值早于最终n32 READY_TO_CLOSE，差74B按原记录保留，不能伪改为同一时点。独立核T01/T05各32B模式、T02十字节、T03/T04各零字节、T06..T10空，以及原L/C/Z的SYNTHETIC字节模式；不使用候选输出去定义其自身预期。

## 证据边界与最终状态

原Flow.finish完成checkpoint与冻结代码的固定0.1秒query guard支持“原guard未触发”；原.q没有逐query duration字段，不能重构每次实测时间。原observer锁存OBSERVED、reasons空、finished与最后duration/gap记录支持原采样guard未触发；compact metric行没有逐周期duration/PID，不能补造逐条时长或把离散采样称为连续OS峰。上述事实依赖原不可变源码及身份链成立，缺guard/完成/绑定证明时拒绝。

本次独立 `reevaluation/evidence-reevaluation.json` 的结论为 **SUPPORTED_ORIGINAL_TOOL_FACTS**，scope固定EVIDENCE_REEVALUATION，completion/resources均accepted。452条离线断言全部通过。原证据读取851746B/148文件（146输出＋两个tester回执），原源码完整性读取52989816B/91文件，均在各自硬界内；未启动新组件或采样。

原E2E最终FAIL、exit、原160断言、原输出、历史FAIL均不覆写。本次只有有界离线判定与负例，newActualAttempts/newActualPasses=0，无新许可或actual/OS采样。负责人可据独立tester复核裁定有限工具事实及下一批，D1/JNI/P0/C14/真实媒体/五产品变体仍未获通过。
