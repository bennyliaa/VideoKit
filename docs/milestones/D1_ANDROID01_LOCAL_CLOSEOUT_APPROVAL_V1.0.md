# ANDROID01 本机测试收尾审批方案 V1.0

2026-10-21。负责人核独立B报告845cd5920251c44beed2497d66d6843e5e6531e209d503cc93eb598f45fe2829，材料审查完成，真实运行与本机UNKNOWN仍未关闭。不是执行令。

负责人一次获准只读CIM核得三原进程：
- Python35988，创建2026-10-21T06:22:14.773659+08:00，父25036，固定bundled python.exe，命令-X utf8 -B docs/coder/d1media3-android01/tools/run_suites.py 001 002 source。
- Java39256，创建2026-10-21T06:22:37.954274+08:00，父35988，D:/Android/Android Studio/jbr/bin/java.exe，-Xmx256m，准确candidate/evidence/local-002/classes及candidate/deps原11库classpath，main com.videokit.d1input.ContainerPendingOrderCheck，与原报告完整argv一致。
- jcmd19728，创建2026-10-21T06:34:01.601696+08:00，父22608，D:/Android/Android Studio/jbr/bin/jcmd.exe，命令39256 Thread.print -l。19728才是诊断自身PID。

用户可审的最小强制收尾范围仅上述三准确原进程。实际执行前再次一次性核创建时间、image、完整argv、亲子关系，绑定同一原OS进程句柄。缺失/不符/PID复用/访问拒绝立即停，不按名称或整树扩大处置。先保全原29回执/现有输出与冻结hash。

若用户批准：先终止准确父Python并在同一原句柄确认退出，最多等待5秒；父未证退出即停，不动子Java/jcmd。父退出确认后核是否出现新子派发；如发现新子立即停、单列新资源，不擅自扩大终止范围。再逐个处理绑定的原Java及原jcmd，各一次终止及同一原句柄最多5秒确认；自然已退出按真实事实记录，不重复终止。全程无设备/ADB/新attach/新测试/文件删除或旧账修改。操作前与父退出后有限快照用于准确范围校验，不持续轮询。

重要代价：强制退出可能丢失未落盘测试输出/线程栈、父进程未写回执、JVM finally/原worker/observer/FD自然返回证明；父退出会改变管道读取，可能影响子执行。没有可证原子暂停设施，因此决定到父退出之间仍有窄窗口可能新派发；本方案只能保证已证父退出之后不再由该父派发，不能保证窗口内零派发。用户需接受上述损失与窗口风险。若不接受，保留UNKNOWN且不执行。

执行后结果只能记录原测试UNKNOWN/被干预及准确OS进程终态，不记原测试PASS/自然归还，不补ACK退款；不据此宣称host全空闲或设备fresh通过。保留原活动目录、全部历史证据、740及旧6232封存；外置保存完整操作/后确认与缺口报告。当前候选冻结和tester材料审查完成事实不改变，fixture/Android/mux/D1/P0保持OPEN/NOT_RUN。
