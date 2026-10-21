# D1 E13E 有限生产边界自检 V1.0

2026-10-18。本机自检有原输入pin、精确argv、自然exit、stdout/stderr。无ADB/设备/媒体；本机fixture kernel/UID、Looper、基础runner是有限替身。实际生产Probe/Sender/BindingOwner/runner、source等待及PC路径执行；不是镜像gate替代全部接线。

## 当前有效证据

- android-005：18组，实际adapter/runner/原共同owner/fixture端点；含countDown-finally成功/原失败、完整Probe、fixture UNKNOWN/错身份重放、runner原异常/FD结果UNKNOWN、订阅前/中/假检查后/worker退出前、永久UNKNOWN、早snapshot与同原ACK、stage上限、bind/HELLO/fixture/unbind在途。实际HELLO使用生产E4CodecWire，平台只提供IBinder/Parcel等替身。HELLO扣住31秒，原调用真返后仍不能变PASS；其余平台在途扣住5.2秒。不是每一种平台调用都实测55秒。
- host-004：准确实际PC archive/HostCase/Supervisor，原子JVM进程56秒自然结束，55秒先判PENDING，早晚raw同operation逐字节落盘；原EOF/exit/pipe/所有archive文件自然归还后原custodian自然终结。open拒绝、write失败、write在途、close UNKNOWN分支；UNKNOWN不二close。原本机子进程的模拟Android token只用于主机解码门，不是Android归还证明。
- host-006：最终生产classes编译，GUARD/source原caller join/runtime真实termination/原@Before观察在途/正常archive；最终JAR从这次生产classes筛选，不重新编译自检镜像。
- public-004：两个新UUID case并发、E13部署及旧E11部署公开入口，实际Guard/入口执行，只shadow固定位置到本机夹具目录。全部在SDK及监督器分配之前准确PENDING拒绝，child/install0。实际外层observer运行同一被拒绝Java entry：已有stdout记录不覆盖，stderr继续drain、空stdout、原Process/reader/pipe自然返，记录失败与物理归还分开。

host-004的55秒case对应最终JAR原PC pipeline成员还须逐字节来源核验；若本轮最终编译仅改变其他入口/来源，不机械重跑同一长case。最终审证给准确class比较，不能只靠同名类推断。

outer-009针对最终实际observer再验：持久receipt的自身close为未证/null，console仅在实际metadata文件close后给全归还；原stdout文件不可用不覆盖，仍读完同一原进程。outer-008原Process自然结束后，console解析发现VoidTaskResult杂讯，源头[void]抑制并留原失败材料，不把它算设备或资源归还成功。

r01-lock-010直接执行最终E9观察，实际stage sink与平台边界均不持E9CurrentObservation.class monitor；原ACTIVE登记/退回与无假grant同时验证。

## 保留的开发期失败与修正

host-001已编译后GUARD命中指针误匹配*.claim，修正active.pointer；host-002/003验证修正。android-003的stage总长断言发现换行/尾标记上限未计全，收紧为48×500+尾部预留；android-004/005通过。android-004 protocol-only旧汇总错误列入未执行的11组，命令原记录仅6组，另存计数审计说明；最终汇总只认实际commands，未篡改历史输出。没有把这些开发期FAIL改成PASS。

构建main-001缓存锁权限拒绝、env-002源目录DSL错误均在APK编译前；fixed-003修正源码目录和晚ACK后首次成功；r01-004再按真实R01源码修正收窄观察锁，最终成功且旧成功版保留。保留全部输入/日志/时间。Android001/002为逐步验证，部分源后来变化，不充最终制品全部源码一致性证明；最终源码/类成员映射及最新适用组单列。

actual-after-007额外直接执行生产E13DeviceTests.@After、真实JUnit4.13.2 TestName/TestWatcher和实际runner：callback未返时原@After失败，经原TestWatcher记录，晚原返后唯一finish仍含失败。CALLBACK_PASS是直接提交成功结果的完成门分支，不能冒称实际@After在资源未返时也通过。

## 仍未验证

真实API31主Looper/Binder调度、独立UID/签名/kernel拒绝、false/SE的系统dispatcher/unbind、真实monitor平台finish、当前原task状态和T07全部NOT_RUN。本机base runner只执行与准确monitor1.8.0源码相符的非主约束替身；实际生产runner调用线程已检查，不能写成已执行真实Android monitor。固定依赖主源码摘录沿用已封存E13D来源。

未机械重跑旧绑定九组/source/历史signal/native套件；仅因新增source完成门，执行原registry/caller/runtime等待的有限直接分支。所有历史P0/FAIL/UNKNOWN及许可保持，D1 NOT_PASSED/M0 NOT_STARTED。
