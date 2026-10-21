# D1 E4A-OWNER3 精确旧receiver收尾报告 V1.0

日期：2026-10-17 09:54。依据D1_E4A_OWNER3_TESTER_REQUIREMENTS_V1.0.md，仅HA1Q6WXR及原PID7722/startTicks7571831。

**结论：PASS_SCOPED_ORIGINAL_OWNER_ENDED。全部固定身份及FD3/归档dev-inode门成立后，仅一次run-as TERM7722返回0；同一原控制命令在有界观察中确认原/proc身份消失。该结论仅针对原7722/ticks7571831的地址空间与该进程FD持有关系，不表示全部历史owner清零、父资源归还、媒体字节通过或产品验收。其他旧远端未知保持UNKNOWN_NOT_CLEARED。**

## 1. 一次本机集中核对

新的包外目录 `docs/tester/D1_E4A_OWNER3_EVIDENCE` 保留字段函数、完整控制脚本及本机证据。UID/status改为while IFS= read -r、case、set --等shell内建，无设备awk/python/perl或新依赖。

本机一次有限批次：现有Git shell对完整控制脚本作-n语法检查，另一自有shell运行19项合成字段断言；两原退出0、stderr0，不执行控制脚本的设备/信号操作。覆盖有效stat、PID/comm/PPID/ticks及短stat拒绝；四UID、错误/缺失/重复UID行；dev-inode/owner错配及格式拒绝；同原身份、僵尸、PID复用和不可解析观察分支。这些只是解析证据，不冒充设备身份。

完整控制脚本SHA `b62900c46bb1887c4508e25c63959b92c744069a9a230a3b20c8dbe79cc2f9d1`，字段函数SHA `5ed6e4c5a026971e6aef217ff7ab43d6b10b35d45036605b28e08cee402adced`。执行前重核文件SHA，原实发argv中的整体脚本解引用后与此控制文本相同，没有逐条遇错修改重跑。

## 2. 一次无害设备兼容门

首个指定平板metadata命令核run-as UID/pwd，检查已知cat、readlink/od/tr/ps接口，实际验证stat -L格式、date纳秒数字与64位deadline计算、sleep小数参数，并仅列出kill信号名称。`kill -l`不接收PID、不发送信号；没有kill0或向其他进程试发信号。

该命令原exit0、完整兼容完成标记、stderr0；兼容不符本会停止，不执行定向控制。本批通过后只派发一次完整控制，不循环换工具或重设身份。未读取父/proc或媒体内容。

## 3. 同一控制命令的原身份与FD证明

09:52:06前后完成本批三条设备metadata命令。定向控制先逐项核对并保留原值，TERM前再次核原stat/ticks：

| 固定门 | 本次原实证 |
|---|---|
| PID / comm / PPID | 7722 / tee / 7718；PPID仅来自子stat |
| startTicks | 7571831，与合同固定身份相同 |
| 四UID | 10221 / 10221 / 10221 / 10221 |
| 完整NUL argv | tee、files/e4_fixtures/basic.mp4，原hex完全相符 |
| cwd | /data/user/0/com.videokit.app |
| exe | /system/bin/toybox |
| FD3链接 | /data/user/0/com.videokit.app/files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep |
| 准确归档角色 | 普通文件、非symlink |
| FD3目标stat -L | dev64522 / inode21416 / uid10221 |
| 归档stat | dev64522 / inode21416 / uid10221；与FD3目标完全一致 |

仅对已证FD3跟随stat取得元数据，没有读FD对象内容、媒体hash或传输。全部门成立后才输出原再核完成标记：

```text
OWNER3_RECHECK_COMPLETE|pid=7722|ticks=7571831|uid=10221|ppid=7718|fd=3
OWNER3_TERM_ATTEMPT|pid=7722
OWNER3_TERM_RETURN|rc=0
OWNER3_OBSERVATION|GONE|pid=7722|ticks=7571831
```

只有一次TERM调用，目标为正PID7722，经相同run-as UID执行；未向父、组、app/server或其他PID发信号，没有KILL升级、force-stop或重复TERM。信号0返回仅表示该调用成功；本报告结束依据是随后同原控制命令的/proc消失观察。

## 4. 原身份结束、观察边界及资源

控制命令整体耗时0.484秒，包含完整再核、TERM及原身份消失观察，未达到合同2秒观察窗口或15秒命令上限。观察同时受原2秒deadline与最多20轮限制，无续期或升级；未进入僵尸或PID复用分支。本批不据此确定历史截断根因或父进程资源结算。

之后唯一UID10221快照只见本次检查shell PID16482与toybox ps PID16485，未见7722项；没有因此扩大处理其他PID。一次UID快照不是全部历史资源归还证明，父7718未被查询、控制或强制结束。

原7722身份消失支持该原进程的地址空间与其FD3持有关系已经结束；归档inode可能仍有其他引用，其他进程/终端/父资源未完成全局证明。归档残件保持路径保留，没有直接内容读写/删除/重命名；本批未核当前长度或SHA，不将dev-inode证明扩展成字节完整性验收。

三原本机客户端均exit0、PROCESS_IO_COMPLETE_ONLY且ownership RETURNED，实际stdin close、source关闭、writer、stdout/stderr drain、原wait与线程归还均成立。retainedLocalOwners=0，无本机在途Job或保留handle。原T1强关闭pump保持，不因TERM返回清零其他旧远端未知。

## 5. 实际预算和证据

metadata3/上限4：兼容门、唯一控制、唯一结束UID快照。各原记录耗时0.328/0.484/0.156秒；stdout1025/869/270B，stderr均0，完整未截留。所有包外证据低于1MiB，实际总量见review-summary.json。

媒体内容/hash/传输、父/proc、其他真实信号、256B诊断、预置、手机/模拟器、安装/Gradle/Binder/产品方法全部0。没有新诊断目录、cache或预算清理，不自动下一批。

证据包括local-review及19项原日志、源码/控制脚本、兼容/控制/快照三原收据、result、原stdout/stderr、audit-summary与manifest。审计只解析保存字节；旧OWNER2报告SHA保持，不改历史失败。

## 6. 交接

本批完成该准确自建receiver的定向收尾，主动报告负责人。是否另派合成诊断或媒体恢复仍由负责人按新准确合同决定，本批成功不授权继续。D1未通过、M0未启动，P0/历史FAIL、旧T2P/T3P结果和T1P/PREP-01未知保持。
